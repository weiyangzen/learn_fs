# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/pci.h

## Purpose
`pci.h` is the PCIe transport contract for rtw89. It defines Realtek PCIe/MDIO/DBI register offsets and bit fields, AX and BE descriptor/index/interrupt register maps, PCI configuration-space constants, PCIe configuration enums, DMA descriptor formats, runtime ring structures, generation dispatch tables, chip `rtw89_pci_info`, exported symbols, and inline wrappers used by the generic PCI implementation and chip-specific modules. The header is the primary source of the PCI HCI ABI between common rtw89 code, AX-generation support in `pci.c`, BE-generation support in `pci_be.c`, and individual chip descriptors.

## Important APIs, types, and definitions
- Register and bit macros cover MDIO pages, RAC analog registers, DBI access, ASPM/L1/CLKREQ/L1SS controls, AX and BE interrupt mask/status registers, TX/RX BD index/number/base registers, DMA stop/busy registers, mitigation registers, LTR registers, SER PL1 controls, and BE group-BD encodings.
- Size constants `RTW89_PCI_TXBD_NUM_MAX`, `RTW89_PCI_RXBD_NUM_MAX`, `RTW89_PCI_TXWD_NUM_MAX`, `RTW89_PCI_TXWD_PAGE_SIZE`, and `RTW89_PCI_RX_BUF_SIZE` define fixed ring and buffer geometry.
- Enums describe PCIe PHY generation/delay (`rtw89_pcie_phy`, `rtw89_pcie_l0sdly`, `rtw89_pcie_l1dly`, `rtw89_pcie_clkdly_hw*`), descriptor modes (`mac_ax_bd_trunc_mode`, `mac_ax_rxbd_mode`), tag/burst/watchdog/LBC/IO-recovery settings, functional enable states, and interrupt-mask modes.
- `struct rtw89_pci_gen_def` is the generation operations table for MAC pre/post init, DMA stop/start recovery, TX DMA control, ASPM/CLKREQ/L1SS, EQ disable, BDRAM reset, and power-wake hooks.
- `struct rtw89_pci_info` is the chip-specific PCI configuration table. It selects generation/ISR definitions, descriptor modes, burst/tag/LTR settings, IO recovery, register addresses, DMA masks, BD RAM tables, low-power index addresses, address-info/RPP parsers, interrupt functions, and SSID quirks.
- Ring/runtime structures include `rtw89_pci_dma_ring`, `rtw89_pci_dma_pool`, `rtw89_pci_tx_wd_ring`, `rtw89_pci_tx_ring`, `rtw89_pci_rx_ring`, `rtw89_pci`, and `rtw89_pci_isrs`.
- Descriptor wire formats include `rtw89_pci_tx_bd_32`, `rtw89_pci_tx_wp_info`, `rtw89_pci_tx_addr_info_32`, `rtw89_pci_tx_addr_info_32_v1`, `rtw89_pci_rpp_fmt`, `rtw89_pci_rpp_fmt_v1`, `rtw89_pci_rx_bd_32`, and `rtw89_pci_rxbd_info`.
- Inline helpers map SKB control blocks to PCI private metadata, locate RX/TX descriptors, advance RX write pointers, dequeue/enqueue TXWD pages, detect invalid LTR read values, and dispatch through chip/generation operation tables.

## Control flow and state behavior
The header encodes a table-driven design. Chip modules fill `struct rtw89_pci_info`; common code uses inline dispatchers to call the selected generation and interrupt methods. `rtw89_chip_config_intr_mask()` is the most stateful inline: it updates `rtwpci->low_power` and `rtwpci->under_recovery` according to `RTW89_PCI_INTR_MASK_*`, emits an HCI debug line, then calls the chip-provided mask builder. Other wrappers keep common code generation-neutral by dispatching MAC pre/post init, BDRAM reset, TX DMA control, interrupt recognition, and PCIe power operations through `info->gen_def` or function pointers.

Runtime TX state is represented by a descriptor ring plus optional TXWD pages. `rtw89_pci_tx_wd_ring` owns a coherent page pool and `free_pages`; `rtw89_pci_tx_ring` tracks `busy_pages`, channel number, DMA enabled flag, a 13-bit tag field, and TX result counters. `rtw89_pci_dequeue_txwd()` removes a page from the free list, resets length, and decrements `curr_num`; `rtw89_pci_enqueue_txwd()` clears the page memory, returns it to the free list, and increments `curr_num`. RX state is a descriptor ring plus fixed SKB array, a currently assembled segmented SKB (`diliver_skb`), saved RX descriptor info, and a target RX tag.

Descriptor formats preserve hardware endianness and bit layouts. TXBDs carry length, LS and DMA-high option bits, and low DMA address. TX address-info v1 splits large buffers into up to ten 11-bit length chunks with high-address selectors. RXBD info stores FS/LS, write size, and RX tag in a leading dword in the received buffer. RPP formats expose old and v1 release-report layouts so parser callbacks can normalize them into `rtw89_pci_rpp_info`.

The top-level `struct rtw89_pci` persists PCI device pointer, MMIO mapping, IRQ/TRX locks, `running`, `low_power`, `under_recovery`, `enable_dac`, TX/RX rings, H2C queues, deferred kick bitmap, and currently programmed interrupt masks. None of this is on-disk persistence; it is runtime kernel driver state rebuilt on probe/resume/reset and freed on remove.

## Dependencies and integration points
`pci.h` includes `txrx.h` and relies on rtw89 core types such as `struct rtw89_dev`, `struct rtw89_hal`, `struct rtw89_chip_info`, channel enums, `struct rtw89_rx_desc_info`, and SKB/mac80211 metadata. It also depends on Linux bitfield/endian/list/SKB/DMA/pci types through transitive kernel includes. The exported declarations are consumed by chip-specific PCI modules and by `pci_be.c`: PM ops, PCI error handlers, generation definitions, ISR definitions, DMA address sets, BD RAM tables, probe/remove, basic config, LTR setters, RPP parsers, TX address-info fillers, DMA controls, interrupt operations, and recognition functions.

The header connects three layers: chip descriptors populate `rtw89_pci_info`, `pci.c` and `pci_be.c` implement the declared functions/tables, and rtw89 core calls the HCI operations installed during probe. Register constants also integrate with `reg.h` and `mac.h` hardware controls, especially where PCI recovery calls MAC DMA reset helpers.

## Risks and edge cases
- This file is hardware ABI dense. A wrong register offset or bit mask can break DMA, interrupts, link power, or recovery across an entire chip family.
- Several macros have overlapping names for AX and BE layouts, and some fields have v1/v2 meanings. Consumers must use the matching `rtw89_pci_info` table and interrupt functions.
- Descriptor structs are `__packed` and endian annotated; size/layout drift would corrupt hardware descriptors or release reports.
- `rtw89_pci_info` mixes configuration policy and hardware register addresses. Missing callbacks or inconsistent masks can cause null calls, disabled channels being allocated, or interrupts being acked at the wrong registers.
- Inline wrappers do no locking except state changes in callers; interrupt and TRX locking discipline must be maintained in implementation code.
- `RTW89_PCI_RX_BUF_SIZE` includes assumptions about maximum payload, long RX descriptor v2, and RXBD info overhead; future descriptor growth can overflow unless this constant changes.
- `rtw89_pci_ltr_is_err_reg_val()` treats `0xffffffff` and `0xeaeaeaea` as invalid register reads, which protects against dead hardware but means LTR setup can fail early on transient bus faults.

## Test signals
Compile-time signals include struct-size/`BUILD_BUG_ON` checks, clean module builds for all chip modules, and no duplicate/missing exported symbols. Runtime validation should cover all selected `rtw89_pci_info` variants: correct TX/RX channel register programming, disabled channel masks respected, BD/RXBD ring lengths accepted by hardware, interrupt masks matching observed ISR bits, RPP parsing releasing the right TXWD sequence/channel, and low-power mode switching index addresses correctly. Power-management tests should verify CLKREQ/ASPM/L1SS bits and LTR functions for AX, AX v1, and BE v2 tables. DMA stress should show stable RX tags, no descriptor unavailability under normal load, and no TXWD leaks across recovery/reset/remove.
