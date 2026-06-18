# subset-b-004929 research

This grouped report covers the Realtek rtw89 PCI transport files assigned to subset-b-004929. Each section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/pci.c

## Purpose
`pci.c` is the main PCIe host-controller implementation for the rtw89 wireless driver. It binds the generic rtw89 core/mac80211-facing HCI operations to Linux PCI services and Realtek PCIe hardware: device claiming, BAR mapping, DMA mask/DAC selection, TX/RX descriptor ring allocation, interrupt handling, NAPI polling, TX submission, RX delivery, release-report processing, power-management link setup, AX-generation PCIe initialization, level-1 recovery, and PCI error callbacks. The file also exports shared helper/data symbols used by chip modules and BE-specific code, including DMA register-address sets, BD RAM tables, interrupt variants, LTR setup functions, RPP parsing, and the `rtw89_pci_gen_ax` generation table.

## Important APIs, types, and functions
- Module parameters `disable_clkreq`, `disable_aspm_l1`, and `disable_aspm_l1ss` gate PCIe power-link features at runtime.
- `rtw89_pci_probe()` and `rtw89_pci_remove()` are the exported PCI bus lifecycle entry points used by chip-specific PCI ID modules.
- `rtw89_pci_ops` is the `struct rtw89_hci_ops` implementation. It provides TX write/kick/flush, start/stop/pause/switch-mode, register read/write, DMA control, NAPI poll, recovery, resource clear, interrupt enable/disable, and BD reset callbacks to the rtw89 core.
- `rtw89_pci_setup_resource()` chains BAR mapping, DMA ring allocation, H2C queue setup, and lock initialization. `rtw89_pci_clear_resource()` reverses those resources and drains firmware-command SKBs.
- TX path functions include `rtw89_pci_check_and_reclaim_tx_resource()`, `rtw89_pci_tx_write()`, `rtw89_pci_txbd_submit()`, `rtw89_pci_txwd_submit()`, `rtw89_pci_fwcmd_submit()`, and `rtw89_pci_ops_tx_kick_off()`.
- RX and release-report processing is handled by `rtw89_pci_poll_rxq_dma()`, `rtw89_pci_rxbd_deliver_skbs()`, `rtw89_pci_poll_rpq_dma()`, `rtw89_pci_release_tx_skbs()`, `rtw89_pci_release_rpp()`, and the exported parsers `rtw89_pci_parse_rpp()` / `rtw89_pci_parse_rpp_v1()`.
- Interrupt variants `rtw89_pci_config_intr_mask*()`, `rtw89_pci_enable_intr*()`, `rtw89_pci_disable_intr*()`, and `rtw89_pci_recognize_intrs*()` cover legacy AX layouts, AX v1 indirection, and BE register layouts.
- AX-generation hardware setup is in `rtw89_pci_ops_mac_pre_init_ax()`, `rtw89_pci_ops_mac_post_init_ax()`, `rtw89_pci_ops_deinit()`, and many chip-condition helper patches for BER, deglitch, autok/refclk, LDO, L1/L2 behavior, IO recovery, debug, and keep-register settings.
- PCIe link/power helpers `rtw89_pci_basic_cfg()`, `rtw89_pci_link_cfg()`, `rtw89_pci_l1ss_cfg()`, `rtw89_pci_aspm_set_ax()`, `rtw89_pci_clkreq_set_ax()`, and `rtw89_pci_ltr_set*()` program ASPM, CLKREQ, L1SS, completion timeout, and latency tolerance reporting.
- Recovery and PM hooks include `rtw89_pci_ops_mac_lv1_recovery()`, `rtw89_pci_io_error_detected()`, `rtw89_pci_io_slot_reset()`, `rtw89_pci_io_resume()`, `rtw89_pci_suspend()`, and `rtw89_pci_resume()`.

## Control flow and state behavior
Probe allocates an `ieee80211_hw` with private `struct rtw89_pci`, installs PCI HCI metadata into `rtwdev->hci`, applies global and subsystem-ID quirks, initializes core state, enables the PCI device, maps BAR2, allocates coherent TX/RX descriptor pools plus per-channel TXWD pages and RX SKBs, sets up chip information, applies basic PCIe link configuration, initializes NAPI, requests a threaded IRQ, and finally registers with the rtw89 core. Remove frees IRQ/NAPI/core registration first, then tears down DMA resources, disables the PCI device, deinitializes core, and frees the hw object.

TX state is split between descriptor rings (`bd_ring.wp/rp`), per-channel TXWD page lists, queued SKBs, and the hardware host index register. Normal data frames map the SKB for DMA, fill a TXWD page with descriptor body, PCI write-pointer metadata, and address-info records, enqueue the SKB under that TXWD sequence, write a TXBD pointing at the TXWD page, then advance the host write pointer. Firmware commands are special-cased to CH12: the H2C descriptor is pushed directly into the SKB, a TXBD points at the mapped command buffer, and SKBs are tracked in `h2c_queue` / `h2c_release_queue` instead of TXWD pages. Doorbells are deferred in `kick_map` while HCI is paused and replayed on resume.

TX completion can arrive through RPQ release reports before the TXBD ring hardware pointer has advanced, especially in low-power mode. RPP handlers parse the sequence, queue selector/status, and DMA channel, locate the corresponding TXWD page, unmap SKBs, report mac80211 status via `ieee80211_tx_status_ni()`, update per-ring counters, and return TXWD pages to the free list when both descriptor reclaim and SKB release are complete. Resource-check paths opportunistically drain RPQ and reclaim TXBDs before returning available descriptors/pages.

RX state is a preallocated circular RXBD ring backed by mapped SKBs. NAPI clears RPQ/RXQ interrupt bits, drains RPQ release reports, then drains RXQ data while respecting `rtwdev->napi_budget_countdown`. RXBD info is synchronized from device to CPU, parsed from the leading `rtw89_pci_rxbd_info`, optionally validated against an incrementing RX tag, and then synchronized back for device reuse. Segmented packets are reassembled into `rx_ring->diliver_skb` using FS/LS flags, RX descriptor length/offset, and `rtw89_chip_query_rxdesc()`. Complete packets are handed to `rtw89_core_rx()`, and the host index is written back after processed descriptors.

Interrupt state is guarded by `irq_lock`; TRX ring state is guarded by `trx_lock`. The top-half disables device interrupts and wakes the threaded handler unless `running` is already false. The thread recognizes/acks generation-specific ISR registers, reports RDU, halt-C2H, WDT, and SPS OCP conditions, schedules NAPI in normal mode, directly polls RX/RPQ in low-power mode, and only re-enables interrupts immediately when recovery/low-power handling bypasses NAPI. `low_power` and `under_recovery` are durable runtime flags in `struct rtw89_pci` and are changed only through `rtw89_chip_config_intr_mask()`.

AX MAC pre-init is a hardware patch sequence: apply chip quirks, configure PHY/PCIe analog controls via MDIO/direct registers, wake PCI power, stop WPDMA/TRX DMA, poll DMA idle, clear indexes, program BD/truncation/tag/burst modes, reset software rings into hardware registers, reset BDRAM, leave firmware-command DMA enabled for firmware download, and restart global DMA. Post-init enables LTR, enables all TX DMA queues, and releases WPDMA/PCIe IO. Deinit disables wake/LTR/DMA and clears indexes. Basic link configuration is rerun on resume and after BE resume, and it enables CLKREQ/ASPM/L1SS only if the upstream PCIe configuration indicates host support.

## Dependencies and integration points
This file depends on Linux PCI, DMA mapping, NAPI, IRQ, SKB, mac80211 TX status, and PCI error-recovery APIs. It integrates with rtw89 core structures and helpers from `mac.h`, `reg.h`, `ser.h`, `txrx.h`, and chip-provided `struct rtw89_pci_info`. Chip-specific modules supply `rtw89_driver_info` and `rtw89_pci_info` tables through PCI ID `driver_data`; those tables choose generation callbacks, interrupt register variants, descriptor formats, DMA channel masks, register-address sets, BD RAM tables, RPP format size, LTR callback, and optional SSID quirks.

Exported symbols are part of the internal rtw89 module ABI: chip modules call `rtw89_pci_probe/remove`, use `rtw89_pm_ops`, `rtw89_pci_err_handler`, generation definitions, ISR definitions, DMA address sets, BD RAM tables, LTR setters, interrupt helpers, RPP parsers, and TX address-info fillers. Runtime integration points include `rtw89_core_init/register/unregister`, `rtw89_core_napi_*`, `rtw89_chip_fill_txdesc*`, `rtw89_chip_query_rxdesc`, `rtw89_mac_ctrl_hci_dma_*`, `rtw89_ser_notify`, and mac80211 TX/RX delivery.

## Risks and edge cases
- Descriptor-ring accounting is hardware ABI sensitive. Off-by-one differences between `rx_ring_eq_is_full` chips and normal rings affect both RX availability and host-index writes.
- `rtw89_pci_rxbd_deliver_skbs()` tolerates unexpected FS/LS patterns but must not leak `diliver_skb` or leave stale `diliver_desc.ready`; error paths free and reset state deliberately.
- TX completion ordering is nontrivial: RPP can release SKBs before TXBD reclaim, so `rtw89_pci_release_txwd_skb()` conditionally reclaims and warns only outside low power.
- DMA cleanup paths must match allocation paths for disabled channel masks and CH12 no-TXWD behavior. A failed partial allocation has to free only initialized rings.
- DAC/36-bit DMA enablement is limited for chips requiring manual DAC and depends on upstream bridge vendor/device. Wrong 64-bit enablement can cause device loss or DMA faults.
- PCI config access can fall back to DBI only on selected chips. Link-power changes, autok, and MDIO sequences can fail or time out and often leave only warning/error logs.
- Interrupt mask variants must match silicon generation. Mixing v1/v2/v3 ISR layouts would miss acks, storm interrupts, or fail to schedule NAPI.
- `rtw89_pci_io_error_detected()` treats `pci_get_drvdata()` as `net_device *` even normal probe stores `rtwdev->hw`; this mirrors upstream-like PCI ERS hooks but is a point to verify if error recovery is exercised.
- Several hardware workarounds are gated by chip ID/CV/CID. Adding new chips without a precise `rtw89_pci_info` and generation table can silently use the wrong register semantics.

## Test signals
Build/modpost should verify exported symbols and chip modules link. Runtime probe should show successful PCI enable, BAR2 mapping, DMA mask selection, ring allocation, NAPI init, IRQ request, and core registration. TX/RX validation signals include no `no available TXBD/TXWD`, no DMA mapping errors, increasing TX counters and TX status reports, RPQ release completion without invalid sequence/channel warnings, RX packets delivered through NAPI, and no repeated RX tag mismatch. Interrupt tests should cover normal, low-power, and recovery masks and confirm interrupts are reenabled only after NAPI completion or low-power polling. Power/link tests should exercise ASPM/CLKREQ/L1SS module parameters, suspend/resume, DAC restoration on resume, LTR enable/disable, and absence of device-loss after link-power transitions. Fault/recovery tests should trigger RDU, WDT/halt-C2H SER notification, level-1 stop/start DMA, and PCI AER reset callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/pci.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/pci_be.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/pci_be.c

## Purpose
`pci_be.c` implements BE-generation PCIe behavior that differs from the AX path in `pci.c`. It supplies BE-specific ASPM/L1SS/CLKREQ programming, IO-recovery watchdog setup, DMA stop/start and idle polling, descriptor index clearing, BE mode configuration, BDRAM reset, debounce/LDO/link/SER hardware setup, LTR v2, interrupt mitigation, level-1 recovery DMA reset, EQ/OOBS calibration workaround, suspend/resume hooks, BE ISR definitions, and the exported `rtw89_pci_gen_be` generation dispatch table.

## Important APIs, types, and functions
- `rtw89_pci_aspm_set_be()`, `rtw89_pci_l1ss_set_be()`, and `rtw89_pci_clkreq_set_be()` are the BE generation callbacks for PCIe link power features.
- `_patch_pcie_power_wake_be()` toggles BE wake control in `R_BE_HCI_OPT_CTRL` and is used both locally and as the generation `power_wake` callback.
- `rtw89_pci_set_io_rcy_be()` programs or disables the BE watchdog/IO recovery timers across AON, MDIO, LA mode, WLAN, AXIDMA, local, and AXI read/write channels.
- `rtw89_pci_ctrl_wpdma_pcie_be()` and `rtw89_pci_ctrl_trxdma_pcie_be()` control BE WPDMA, TXDMA, RXDMA, and AXI master stop bits.
- `rtw89_pci_clr_idx_all_be()`, `rtw89_pci_poll_txdma_ch_idle_be()`, `rtw89_pci_poll_rxdma_ch_idle_be()`, and `rtw89_pci_poll_dma_all_idle_be()` reset and validate BE descriptor/DMA state.
- `rtw89_pci_mode_op_be()` maps `rtw89_pci_info` descriptor/burst/tag/watchdog settings into BE HAXI init, RX append, and expansion-control registers.
- `rtw89_pci_ops_mac_pre_init_be()`, `rtw89_pci_ops_mac_pre_deinit_be()`, and `rtw89_pci_ops_mac_post_init_be()` are the BE MAC init/deinit phases used through `rtw89_pci_gen_be`.
- `rtw89_pci_ltr_set_v2()` exports the BE LTR programming sequence with chip-specific latency values for RTL8922A versus later BE chips.
- `rtw89_pci_lv1rst_stop_dma_be()` and `rtw89_pci_lv1rst_start_dma_be()` implement BE level-1 recovery DMA stop/start.
- `rtw89_pci_disable_eq_be()` is a RTL8922A EQ/OOBS/offset calibration workaround.
- `rtw89_pci_suspend_be()` and `rtw89_pci_resume_be()` define `rtw89_pm_ops_be`.
- Exported `rtw89_pci_isr_be`, `rtw89_pci_isr_be_v1`, and `rtw89_pci_gen_be` are consumed by BE chip `rtw89_pci_info` tables.

## Control flow and state behavior
BE pre-init starts by configuring IO recovery from `rtwdev->pci_info`, forcing PCI wake on, stopping WPDMA and all TRX/IO DMA, clearing descriptor indexes, and polling until TX/RX DMA are idle. It then programs descriptor/burst/tag/watchdog mode, resets common software/hardware PCI rings through `rtw89_pci_ops_reset()`, resets BDRAM, applies debounce and LDO low-power policy, sets BE PCIe link/autoload/aux-clock behavior, configures PCIe SER PL1 behavior, disables normal TXDMA queues while enabling the firmware-command channel, and finally reenables TRX/IO DMA for firmware download. This mirrors the AX pre-init contract but uses BE HAXI and BE power/reset registers.

BE post-init enables LTR through the selected `info->ltr_set` callback, releases IO stop while leaving TX/RX state alone, enables WPDMA, enables normal TXDMA and firmware TXDMA channels, and configures interrupt mitigation. MIT setup chooses a 1 ms RX timer unit and a RX count threshold of half the maximum RXBD count. BE pre-deinit turns wake off, checks WLAN MAC power state, and only disables TRX/IO DMA plus clears indexes if the MAC is still powered.

DMA recovery uses the common `rtw89_pci_ctrl_dma_all()` wrapper but BE-specific idle status. If stopping DMA fails because `B_BE_HAXI_MST_BUSY` remains set, it toggles MAC HCI DMA TRX off/on and polls again. Restart toggles MAC HCI DMA, clears indexes, resets BDRAM, and reenables DMA. These generation callbacks are plugged into `rtw89_pci_ops_mac_lv1_recovery()` in `pci.c`.

Link-power state is set directly in BE registers. ASPM first programs PCI config ASPM delay to 16 us and then toggles `B_BE_ASPM_CTRL_L1`. L1SS has an extra RTL8922D CID7090 branch enabling ASPM/PCIPM L1.1/L1.2 bits before toggling `B_BE_L1SUB_ENABLE`. CLKREQ programs BE latency and toggles `B_BE_CLK_PM_EN`; the disable path clears through `R_AX_L1_CLK_CTRL`, which is an alias-like constant reused with a BE bit and should be verified against register definitions when porting.

SER setup is chip/CV dependent. RTL8922A CAV/CBV leave PL1 SER disabled with selected masks; CCV/default clears ISR, enables PL1 SER, and masks/unmasks PM/LTSSM sources. RTL8922D uses BE2 flow: toggle SER flush reset, manipulate RAC PHY error mask/flag registers on both G1/G2 lanes, clear PL1 ISR, program masks and timer unit, enable PL1 SER, and optionally enable SER detect for CID7090. Suspend/resume temporarily changes PL1 timer units for WoW, freezes/unfreezes PCIe register reset, manipulates PRST gating, clears SER/PHY ISR state, and calls `rtw89_pci_basic_cfg()` on resume.

## Dependencies and integration points
The file includes Linux PCI plus rtw89 `mac.h`, `pci.h`, and `reg.h`. It relies on common PCI helpers from `pci.c`: `rtw89_pci_ops_reset()`, `rtw89_pci_ltr_is_err_reg_val()`, `rtw89_pci_ctrl_dma_all()`, `rtw89_pci_clr_idx_all()`, `rtw89_pci_basic_cfg()`, and the generation dispatch contract declared in `pci.h`. It calls MAC-level DMA reset helpers `rtw89_mac_ctrl_hci_dma_trx()` and uses chip metadata (`chip_id`, `hal.cv`, `hal.cid`, and `rtw89_pci_info`) to select RTL8922A/RTL8922D behavior. Its exported symbols are selected by BE chip bus-info tables and by PM wiring in BE PCI modules.

## Risks and edge cases
- BE hardware setup is highly chip-revision specific. RTL8922A CV branches and RTL8922D CID7090 branches must match the actual silicon, or SER/L1SS/LDO settings can be wrong.
- IO recovery timer defaults use different analog/MAC/AUX timer values; a wrong `io_rcy_tmr` or scale can either miss stuck IO or trigger false recovery.
- `rtw89_pci_mode_op_be()` only touches `R_BE_RX_APPEND_MODE` for RTL8922A; future BE chips with different append behavior need explicit handling.
- Grouped descriptor-address mode and unsupported channel masks are handled elsewhere through `pci.c` and `pci.h`; BE stop masks must remain consistent with those tables.
- SER and EQ workaround code directly manipulates RAC analog registers and temporarily disables ASPM/EQ state. Restore ordering is important to avoid link instability.
- Resume clears PHY ISR flags by toggling `PHY_ERR_FLAG_EN` only on RTL8922D; missing this can leave stale PHY error state after system sleep.
- LTR v2 rejects dead register reads before programming. This prevents writing through invalid bus state but can abort MAC post-init and prevent the device from starting.

## Test signals
BE probe should complete pre-init through DMA idle polling, BDRAM reset, debounce/LDO/link/SER setup, firmware-command DMA enablement, post-init LTR, WPDMA enable, TXDMA enable, and MIT configuration. RTL8922A and RTL8922D should be tested separately, including RTL8922D CID7090 L1SS/SER paths. Suspend/resume tests should confirm PRST gating is restored, PL1 timer unit returns to the normal value, SER/PHY ISR clear polling does not warn, and `rtw89_pci_basic_cfg()` reestablishes ASPM/CLKREQ/L1SS. Recovery tests should force HAXI busy, exercise the fallback HCI DMA TRX toggle, and verify BDRAM/index reset plus DMA restart. Link-power tests should verify ASPM/L1SS/CLKREQ module parameters still gate the BE callbacks through the common wrappers in `pci.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/pci_be.c -->
