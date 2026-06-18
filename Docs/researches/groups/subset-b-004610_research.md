# Research: subset-b-004610

Grouped research for QLogic Ethernet driver files under `sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qla3xxx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qla3xxx.h

## Purpose

`qla3xxx.h` is the hardware contract header for the legacy QLogic QLA3xxx NIC HBA driver. It defines the packed on-wire/on-DMA IOCB formats, memory-mapped register page layouts, EEPROM/NVRAM structure, queue sizing constants, DMA buffer control blocks, and the main `struct ql3_adapter` state container consumed by the qla3xxx implementation.

The file contains no executable functions. Its behavior is expressed through fixed binary layouts, register bit definitions, and driver state fields that other qla3xxx source files use to program the ASIC, post transmit and receive buffers, interpret completions, manage link state, and recover from resets.

## Important APIs, Types, And Constants

Core DMA/firmware command structures:

- `struct ob_mac_iocb_req`, `struct ob_mac_iocb_rsp`: outbound MAC transmit request/response descriptors. Important fields are `opcode`, flag bits for interrupt/checksum/continuation semantics, `transaction_id`, `data_len`, IP header offsets, and up to three DMA buffer address/length entries.
- `struct ib_mac_iocb_rsp`: inbound MAC receive response with packet length and inbound address list pointer.
- `struct ob_ip_iocb_req`, `struct ob_ip_iocb_rsp`, `struct ib_ip_iocb_rsp`: IP-oriented command/response formats, including checksum result bits for 3032 hardware.
- `struct net_rsp_iocb`: generic response descriptor used in the response queue.
- IOCB opcodes such as `OPCODE_OB_MAC_IOCB_FN0`, `OPCODE_OB_MAC_IOCB_FN2`, `OPCODE_IB_MAC_IOCB`, and `OPCODE_IB_IP_IOCB`.
- Buffer length flags such as `OB_MAC_IOCB_REQ_E`, `OB_MAC_IOCB_REQ_C`, `OB_IP_IOCB_REQ_E`, and `OB_IP_IOCB_REQ_C` indicate list termination and continuation/OAL chaining.

Register and hardware layout types:

- `struct ql3xxx_common_registers`: mailbox registers, flash/NVRAM access registers, control/status, interrupt mask, queue producer/consumer indexes, and MADI access.
- `struct ql3xxx_port_registers`: page 0 port-control page, including MAC/PHY management registers, IP registers, statistics selectors, fatal error status, local RAM access, and port status.
- `struct ql3xxx_host_memory_registers`: page 1 queue DMA configuration for request, completion, large RX, and small RX queues.
- `struct ql3xxx_local_ram_registers`: page 2 memory allocator and table sizing state for buflets, IP/TCP hash tables, NCB, and DRB tables.
- Bit-field enums define `ispControlStatus`, interrupt mask, semaphore ownership, external/internal hardware config, port control/status, MII management, MAC config, statistics selector indexes, and fatal error bits.

Persistent device configuration:

- `struct eeprom_port_cfg`, `struct eeprom_bios_cfg`, `struct eeprom_function_cfg`, and `struct eeprom_data` model the EEPROM/NVRAM contents, including MAC addresses, subsystem IDs, port configuration, buffer/table sizing, serial/board strings, and checksum.
- EEPROM command constants cover FM93C56/66/86 style serial EEPROM opcodes, address/data bit widths, and bit-banged Auburn serial interface signals.

Queue and DMA state:

- Queue sizing constants: `NUM_REQ_Q_ENTRIES`, `NUM_RSP_Q_ENTRIES`, `NUM_LBUFQ_ENTRIES`, `JUMBO_NUM_LBUFQ_ENTRIES`, `NUM_SBUFQ_ENTRIES`, and `NUM_SMALL_BUFFERS`.
- `struct lrg_buf_q_entry` and `struct bufq_addr_element` define receive buffer queue entries and DMA address elements.
- `struct ql_rcv_buf_cb` tracks one RX skb, DMA mapping, physical address split, and free-list link.
- `struct oal_entry`, `struct oal`, and `MAX_OAL_CNT` implement outbound address list chaining for fragmented TX skbs beyond the three inline IOCB SG slots.
- `struct ql_tx_buf_cb` keeps the skb, IOCB entry, OAL pointer, segment count, and DMA unmap metadata for a transmit request.
- `struct ql3_adapter` is the central runtime state: PCI/netdev/NAPI references, spinlocks, MMIO base and current register page, shadow registers, request/response queues, TX/RX software rings, EEPROM copy, link state, MAC/PHY parameters, workqueue and delayed reset/link/timeout work, frame sizing, and feature flags.

## Control Flow And State Behavior

This header shapes driver control flow through state fields and register contracts rather than code:

1. Probe/setup code maps BAR space into `mmap_virt_base`, assigns `mem_map_registers`, selects pages through `current_page`, reads `nvram_data`, and programs queue base addresses in `ql3xxx_host_memory_registers`.
2. TX code allocates a request queue entry, fills `struct ob_mac_iocb_req`, uses inline DMA slots and optional `struct oal` continuation entries, advances `req_producer_index`, and later uses `struct ql_tx_buf_cb` plus completion `transaction_id` to unmap and free the skb.
3. RX setup posts large and small buffer queues using `struct lrg_buf_q_entry`, `bufq_addr_element`, and `ql_rcv_buf_cb` pools. Completion processing interprets inbound IOCBs, returns buffers, and maintains producer indexes and release counters.
4. Link and reset work is coordinated by `qdev->flags` bits such as `QL_RESET_ACTIVE`, `QL_RESET_START`, `QL_LINK_MASTER`, `QL_ADAPTER_UP`, `QL_LINK_UP`, and allocation-done flags.
5. EEPROM, flash, PHY, DDR, and driver-global operations are serialized through hardware semaphore bit definitions in `semaphoreReg`.

Persistent state lives in EEPROM/NVRAM (`struct eeprom_data`) and in hardware register state. Runtime state in `struct ql3_adapter` is volatile and rebuilt during probe, reset, MTU changes, and queue reallocation.

## Dependencies And Integration Points

The header depends on Linux kernel networking and PCI types through users of this header: `struct pci_dev`, `struct net_device`, `struct napi_struct`, `struct sk_buff`, `struct timer_list`, `struct workqueue_struct`, `struct delayed_work`, DMA mapping metadata macros, spinlocks, and endian-tagged integer types.

Integration points include:

- Linux netdev TX/RX paths via skb-backed `ql_tx_buf_cb` and `ql_rcv_buf_cb`.
- PCI/MMIO accessors through register layout structs stored as `__iomem` pointers.
- DMA APIs through `dma_addr_t` and `DEFINE_DMA_UNMAP_ADDR/LEN`.
- NAPI receive polling via the `napi` member.
- Workqueue/timer reset and link maintenance through `reset_work`, `tx_timeout_work`, `link_state_work`, and `adapter_timer`.
- MII/PHY and EEPROM code via register constants and bit-banged serial interface definitions.

## Risks And Edge Cases

- Binary layout risk is high. The IOCB structs are `#pragma pack(1)` and EEPROM/descriptor structures use exact endian and bit-field assumptions. Any field movement changes hardware ABI.
- `MS_64BITS(x)` and `LS_64BITS(x)` split DMA addresses; misuse or truncation would corrupt queue/buffer programming.
- Queue sizes are power-of-two and page-size motivated. Changing constants can break ring wrapping or hardware expectations.
- EEPROM structures use C bit-fields and comments note endianness sensitivity. Cross-endian behavior must be validated carefully.
- OAL chaining depends on `MAX_SKB_FRAGS` and flags in length words. Incorrect last/continuation bits can produce DMA past the intended scatterlist.
- Reset and allocation flags in `qdev->flags` are positional enum values intended for bit operations. Renumbering or mixing with masks would corrupt state checks.
- Register-page structures assume MMIO layout and 32-bit register width. Adding padding or compiling with unexpected packing would be unsafe.

## Test Signals

Good validation signals for changes touching this header include:

- Successful build of the qla3xxx driver with sparse/endian warnings enabled.
- TX/RX traffic over normal MTU and jumbo MTU, including fragmented skb TX that exercises OAL chaining.
- RX buffer recycling under memory pressure and DMA mapping error injection if available.
- Link up/down and PHY auto-negotiation tests for both port/MAC indexes.
- EEPROM read/checksum and MAC address extraction tests.
- Reset, TX timeout, and adapter down/up cycles that confirm flags and queue allocation state transitions.
- Runtime DMA API debug and KASAN/KMSAN checks for descriptor or buffer lifetime mistakes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qla3xxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/Makefile

## Purpose

This Makefile declares how the Linux kernel Kbuild system composes the `qlcnic` QLogic 1G/10G CNA Ethernet driver. It maps `CONFIG_QLCNIC` to the `qlcnic.o` module/built-in object and lists the source objects that form the driver, with optional SR-IOV PF and DCB objects controlled by separate Kconfig options.

## Important Build Rules

- `obj-$(CONFIG_QLCNIC) := qlcnic.o` builds the driver when `CONFIG_QLCNIC` is enabled.
- `qlcnic-y := ...` links the common driver body from hardware, main netdev, initialization, ethtool, context, I/O, sysfs, minidump, 83xx hardware/init/vNIC, and SR-IOV common objects.
- `qlcnic-$(CONFIG_QLCNIC_SRIOV) += qlcnic_sriov_pf.o` conditionally adds physical-function SR-IOV support.
- `qlcnic-$(CONFIG_QLCNIC_DCB) += qlcnic_dcb.o` conditionally adds Data Center Bridging support.

The always-built list includes:

- `qlcnic_hw.o`, `qlcnic_main.o`, `qlcnic_init.o`
- `qlcnic_ethtool.o`, `qlcnic_ctx.o`, `qlcnic_io.o`
- `qlcnic_sysfs.o`, `qlcnic_minidump.o`
- `qlcnic_83xx_hw.o`, `qlcnic_83xx_init.o`, `qlcnic_83xx_vnic.o`
- `qlcnic_sriov_common.o`

## Control Flow And Integration Behavior

Build-time control flow is Kbuild driven:

1. If `CONFIG_QLCNIC` is disabled, none of these objects are linked as the `qlcnic` driver.
2. If enabled, all `qlcnic-y` objects are linked into one composite `qlcnic.o`.
3. If `CONFIG_QLCNIC_SRIOV` is enabled, PF-specific SR-IOV code is linked in addition to common SR-IOV code.
4. If `CONFIG_QLCNIC_DCB` is enabled, DCB implementation code is linked; otherwise call sites must be guarded or provided by stubs/conditionals in headers.

## Dependencies And Integration Points

This file integrates with the kernel top-level driver build and Kconfig system. It assumes corresponding `.c` files exist in the same directory and that shared headers expose valid stubs or conditional declarations for optional features.

The Makefile makes `qlcnic_83xx_hw.c` part of the normal driver, so the 83xx operation tables and mailbox/flash/link support are compiled whenever the driver is enabled, not only for a separate 83xx config.

## Risks And Edge Cases

- Optional feature mismatches can produce unresolved symbols if common code calls PF SR-IOV or DCB functions without matching `#ifdef` protection or static stubs.
- Moving an object out of `qlcnic-y` can silently remove registration paths or operation tables needed for supported hardware.
- Adding new source files without updating this Makefile leaves code unbuilt in kernel builds.
- `qlcnic_sriov_common.o` is always linked; it must remain valid even when PF SR-IOV is disabled.

## Test Signals

- Kernel build with `CONFIG_QLCNIC=m` and `=y`.
- Build matrix with `CONFIG_QLCNIC_SRIOV` and `CONFIG_QLCNIC_DCB` both enabled and disabled.
- `modinfo qlcnic` and module load smoke tests on systems without optional hardware.
- Link-time checks for unresolved symbols after changing object membership.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic.h

## Purpose

`qlcnic.h` is the central internal interface for the QLogic qlcnic NIC driver. It defines driver versioning, descriptor formats, firmware/flash metadata, queue and ring state, mailbox command containers, adapter state, NPAR/eSwitch/SR-IOV data models, operation tables, inline dispatch wrappers, device-ID helpers, and exported prototypes shared across the driver.

The header bridges Linux networking, PCI, firmware mailbox protocols, ethtool, sysfs/minidump, 82xx/83xx hardware variants, and VF/PF behavior. Most qlcnic implementation files include this header and operate through `struct qlcnic_adapter`, `struct qlcnic_hardware_context`, `struct qlcnic_hardware_ops`, and `struct qlcnic_nic_template`.

## Important APIs, Types, And Constants

Driver and firmware versioning:

- `QLCNIC_LINUX_VERSIONID`, `QLCNIC_DRIVER_VERSION`, `QLCNIC_VERSION_CODE`, `_major`, `_minor`, `_build`, and `QLCNIC_DECODE_VERSION`.
- Minimum and flash image constants such as `QLCNIC_MIN_FW_VERSION`, `QLCNIC_FLASH_TOTAL_SIZE`, unified image names, and firmware offsets.

Descriptor and queue ABI:

- `struct cmd_desc_type0`: 64-byte aligned TX command descriptor with LSO offsets, opcode/flags, fragment count/length, DMA buffer addresses, MSS, context/port, encapsulation fields, VLAN TCI, and outer header metadata.
- `struct rcv_desc`: packed RX descriptor containing buffer handle, length, and DMA address.
- `struct status_desc`: 16-byte aligned status/completion descriptor.
- Ring size macros: `RCV_DESC_RINGSIZE`, `RCV_BUFF_RINGSIZE`, `STATUS_DESC_RINGSIZE`, `TX_BUFF_RINGSIZE`, `TX_DESC_RINGSIZE`.
- Queue bounds/defaults for command, normal RX, jumbo RX, SDS, TX, RSS/TSS, and hardware limits.

Runtime state containers:

- `struct qlcnic_hardware_context`: MMIO bases, locks, PCI/function identity, link state, firmware capabilities, NPAR/eSwitch/SR-IOV data, mailbox, interrupt table, minidump state, 83xx reset/IDC state, register tables, coalescing settings, and hardware operation pointers.
- `struct qlcnic_adapter`: the main netdev/PCI adapter object with netdev, pdev, state bits, ring counts, firmware wait/fail counters, reset state, MAC address, stats, VLAN bitmap, work items, DCB, filter hashes, firmware image pointer, and `nic_ops`.
- `struct qlcnic_host_rds_ring`, `struct qlcnic_host_sds_ring`, and `struct qlcnic_host_tx_ring`: software state and DMA metadata for receive descriptor rings, status descriptor rings, and transmit rings.
- `struct qlcnic_recv_context`: receive context grouping RDS/SDS rings and firmware context IDs.
- `struct qlcnic_adapter_stats` and per-TX queue stats track software counters.

Firmware and mailbox protocol:

- CDRP command/response macros: `QLCNIC_CDRP_CMD_BIT`, `QLCNIC_CDRP_FORM_CMD`, `QLCNIC_CDRP_IS_RSP`, response codes, and firmware return codes.
- Host/card request and response structs for RX/TX contexts: `qlcnic_hostrq_rx_ctx`, `qlcnic_cardrsp_rx_ctx`, `qlcnic_hostrq_tx_ctx`, and `qlcnic_cardrsp_tx_ctx`.
- `struct qlcnic_fw_msg`, `struct qlcnic_nic_req`, `struct qlcnic_mac_req`, `struct qlcnic_vlan_req`, and `struct qlcnic_ipaddr`.
- `struct qlcnic_mailbox`, `struct qlcnic_cmd_args`, `_cdrp_cmd`, and `struct qlcnic_mbx_ops`.
- H2C/C2H opcodes for RSS, coalescing, LED, LRO, MAC receive mode, IP address, link events, bridging, hardware LRO, loopback, and DCB AENs.

Flash, firmware dump, and persistent metadata:

- Flash layout constants and structs `qlcnic_flt_header`, `qlcnic_flt_entry`, and `qlcnic_fdt`.
- Board type and board info constants.
- Minidump template headers for 82xx/83xx and `struct qlcnic_fw_dump`.
- Force dump/reset magic keys such as `QLCNIC_FORCE_FW_DUMP_KEY`, `QLCNIC_FORCE_FW_RESET`, `QLCNIC_SET_QUIESCENT`, and dump enable/disable keys.

Virtualization and switch management:

- `struct qlcnic_info`, `qlcnic_info_le`, `qlcnic_pci_info`, `qlcnic_pci_info_le`.
- `struct qlcnic_npar_info`, `struct qlcnic_eswitch`, and function config structs for PCI, NPAR, port mirroring, and eSwitch.
- MAC filter structures `qlcnic_mac_vlan_list`, `qlcnic_filter`, `qlcnic_filter_hash`.
- SR-IOV/VF helper prototypes and checks.

Operation tables and dispatch:

- `struct qlcnic_nic_template` abstracts higher-level NIC lifecycle and netdev operations: firmware start, driver init, reset request, IDC work cancellation, NAPI add/del, IP config, legacy interrupt clear, shutdown, and resume.
- `struct qlcnic_hardware_ops` abstracts register access, mailbox commands, context creation/destruction, link events, PCI/NIC info, MAC/VLAN changes, NAPI enable/disable, coalescing/RSS/LRO/loopback/promisc, filters, board info, AER callbacks, interrupts, firmware dump helpers, and encapsulation offload checks.
- Static inline wrappers such as `qlcnic_issue_cmd`, `qlcnic_fw_cmd_create_rx_ctx`, `qlcnic_fw_cmd_create_tx_ctx`, `qlcnic_linkevent_request`, `qlcnic_config_intr_coalesce`, `qlcnic_config_rss`, `qlcnic_nic_set_promisc`, and interrupt enable/disable helpers call through the operation tables.

## Control Flow And State Behavior

The header defines the common control-flow shape for the driver:

1. Probe code allocates a `struct qlcnic_adapter`, fills the hardware context, determines hardware family and op mode, installs `hw_ops` and `nic_ops`, reads firmware/NIC/PCI info, sets ring counts and features, then sets up netdev registration.
2. Device open/attach allocates software/hardware resources, configures interrupts, creates RX and TX firmware contexts through operation-table callbacks, posts RX buffers, enables NAPI and interrupts, and sets state bits such as `__QLCNIC_DEV_UP`.
3. TX uses `struct qlcnic_host_tx_ring`, `struct cmd_desc_type0`, `qlcnic_cmd_buffer`, and hardware consumer indexes to map skbs, submit descriptors, stop/wake queues, and clean completions.
4. RX/NAPI uses SDS completions to replenish `qlcnic_host_rds_ring` descriptors, account stats, and pass skbs to the stack.
5. Firmware and management operations are funneled through `qlcnic_cmd_args` and the configured `mbx_cmd` implementation, allowing 82xx, 83xx, PF, and VF variants to encode commands differently.
6. Reset, AER, firmware hang, diagnostics, and maintenance mode are coordinated with `adapter->state` bits including `__QLCNIC_RESETTING`, `__QLCNIC_AER`, `__QLCNIC_DIAG_MODE`, `__QLCNIC_MAINTENANCE_MODE`, and firmware ownership flags in `adapter->flags`.
7. Link, DCB, LRO, RSS, loopback, LED, promisc, VLAN, and MAC filter changes are implemented through either `nic_ops` or `hw_ops`, so callers use one common API while hardware-specific files provide the concrete behavior.

Persistent state includes flash/firmware metadata (`fdt`, FLT/FDT offsets), firmware images loaded through `struct firmware`, and NPAR/eSwitch configuration read from or written to firmware. Runtime state includes queue memory, state bits, coalescing values, link status, filter hashes, workqueues, and mailbox queues.

## Dependencies And Integration Points

`qlcnic.h` depends heavily on Linux kernel subsystems:

- PCI, DMA, and MMIO: `struct pci_dev`, `dma_addr_t`, `void __iomem`, PCI error recovery callbacks, MSI/MSI-X entries.
- Networking: `struct net_device`, `struct netdev_queue`, `netdev_features_t`, skb fragments, VLAN bitmap, ethtool, MII, NAPI, link modes, and netdev TX return types.
- Firmware loading: `struct firmware` and firmware image metadata.
- Concurrency: spinlocks, mutexes, completions, workqueues, delayed work, timers, atomic variables, bit operations, and rwlocks.
- Optional features: SR-IOV, DCB, HWMON, minidump, sysfs, ethtool.

Important local integration points are `qlcnic_hdr.h`, `qlcnic_hw.h`, `qlcnic_83xx_hw.h`, `qlcnic_dcb.h`, and implementation files listed in the Makefile. The header also declares many cross-file functions from `qlcnic_init.c`, `qlcnic_main.c`, `qlcnic_ethtool.c`, context code, sysfs, minidump, SR-IOV, and 83xx modules.

## Risks And Edge Cases

- Descriptor, mailbox, and firmware context structs are ABI-bound. Alignment, packing, endian conversions, or field width changes can break hardware communication.
- Operation-table pointers are trusted by many inline wrappers. A missing callback can cause NULL dereferences unless the wrapper explicitly guards it.
- Many state bits are shared between reset, diagnostics, AER, open/close, mailbox, and workqueue paths. Races can leave contexts active while queues are detached or interrupts enabled.
- `qlcnic_tx_avail()` assumes power-of-two ring lengths and producer/consumer discipline.
- Capability flags from firmware determine offload behavior. Incorrect interpretation can advertise unsupported TSO/LRO/VXLAN/encapsulation features to the stack.
- VF/PF and non-privileged modes gate operations differently. Management-only functions such as setting NIC info or LED/loopback must reject non-privileged callers.
- Mailbox commands use allocations with atomic context in some paths; error handling must free both request and response arrays.
- Endian-sensitive structures have separate `_le` and host-native forms; copying between them must convert fields explicitly.

## Test Signals

- Build matrix for 82xx, 83xx, VF, SR-IOV PF, DCB, and HWMON configs.
- Probe/open/close/remove tests with MSI-X, MSI, and legacy INTx fallback.
- TX/RX traffic tests across normal MTU, jumbo MTU, TSO, checksum offload, VLAN, RSS/TSS, LRO, and encapsulation offloads when supported.
- Firmware mailbox command success/failure/timeouts for context create/destroy, MAC/VLAN, NIC/PCI info, link events, RSS, LRO, coalescing, and statistics.
- Reset, firmware hang, AER, suspend/resume, diagnostics, and maintenance-mode transitions.
- SR-IOV PF/VF tests for op-mode detection, mailbox routing, VF multicast/promisc behavior, and PF-only management operations.
- Static analysis for sparse endian annotations, lockdep, DMA API debug, KASAN, and NULL callback paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_83xx_hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_83xx_hw.c

## Purpose

`qlcnic_83xx_hw.c` implements the 83xx/84xx hardware-specific side of the qlcnic driver. It installs the 83xx hardware and NIC operation tables, handles indirect register access, interrupt setup, mailbox command processing, asynchronous firmware events, RX/TX context creation, diagnostics, LED/link/pause/RSS/LRO/MAC/IP configuration, PCI/NIC information queries, flash read/write/erase helpers, driver lock recovery, memory writes, statistics, firmware minidump capability extension, shutdown/resume, mailbox workqueue lifecycle, and PCI AER callbacks.

The file is the concrete implementation behind many `struct qlcnic_hardware_ops` and `struct qlcnic_nic_template` callbacks declared in `qlcnic.h` and `qlcnic_83xx_hw.h`.

## Important APIs, Functions, And Data

Operation tables and register maps:

- `qlcnic_83xx_mbx_tbl[]`: mailbox command metadata mapping opcodes to input/output register counts.
- `qlcnic_83xx_ext_reg_tbl[]` and `qlcnic_83xx_reg_tbl[]`: indexed register tables used by shared register access and ethtool register dumps.
- `qlcnic_83xx_hw_ops`: supplies 83xx implementations for register access, mailbox commands, context create/destroy, link events, NIC/PCI info, MAC/VLAN changes, NAPI control, coalescing/RSS/LRO/promisc, PCI error callbacks, interrupt mask helpers, minidump helpers, and encapsulation offload checks.
- `qlcnic_83xx_ops`: higher-level NIC template for reset requests, IDC cancellation, NAPI add/del, IP address config, legacy interrupt clear, shutdown, and resume.
- `qlcnic_83xx_register_map()`: installs operation table and register table pointers in the hardware context.

Register and interrupt handling:

- `qlcnic_83xx_rd_reg_indirect()` and `qlcnic_83xx_wrt_reg_indirect()` program the per-function CRB window and read/write the wildcard register.
- `qlcnic_83xx_setup_intr()` chooses MSI-X/TSS-RSS/legacy INTx, allocates `intr_tbl`, rejects legacy INTx for function numbers above the supported range, and initializes interrupt descriptors.
- `qlcnic_83xx_clear_legacy_intr()`, `qlcnic_83xx_intr()`, `qlcnic_83xx_tmp_intr()`, `qlcnic_83xx_setup_mbx_intr()`, `qlcnic_83xx_free_mbx_intr()`, `qlcnic_83xx_enable_mbx_interrupt()`, and `qlcnic_83xx_disable_mbx_intr()` manage legacy/MSI-X interrupt acknowledgement, mailbox/AEN interrupt source routing, diagnostic interrupts, and NAPI scheduling.

Mailbox and AEN handling:

- `qlcnic_83xx_alloc_mbx_args()` allocates request/response arrays based on `qlcnic_83xx_mbx_tbl` and encodes HAL version in the command header.
- `qlcnic_83xx_issue_cmd()` queues mailbox commands and waits by completion, no-wait return, or busy polling depending on `cmd->type`.
- `qlcnic_83xx_init_mailbox_work()`, `qlcnic_83xx_detach_mailbox_work()`, `qlcnic_83xx_free_mailbox()`, `qlcnic_83xx_mailbox_worker()`, and `qlcnic_83xx_mbx_ops` implement the asynchronous mailbox queue.
- `__qlcnic_83xx_process_aen()`, `qlcnic_83xx_process_aen()`, `qlcnic_83xx_poll_process_aen()`, `qlcnic_83xx_handle_aen()`, and `qlcnic_83xx_mbx_poll_work()` parse firmware mailbox ownership, route link/IDC/request/time-extend/broadcast/SFP/DCB events, and notify mailbox completions.
- `qlcnic_dump_mbx()` and `qlcnic_dump_mailbox_registers()` provide failure diagnostics.

Context and queue programming:

- `qlcnic_83xx_create_rx_ctx()` builds `QLCNIC_CMD_CREATE_RX_CTX` with SDS/RDS mailbox payloads, programs status and receive ring DMA addresses, receives firmware context IDs and producer/consumer MMIO offsets, and optionally adds extra SDS rings through `qlcnic_83xx_add_rings()`.
- `qlcnic_83xx_del_rx_ctx()` destroys the RX context and marks it freed.
- `qlcnic_83xx_create_tx_ctx()` resets TX producer/consumer state, builds `struct qlcnic_tx_mbx`, selects interrupt IDs, sends `QLCNIC_CMD_CREATE_TX_CTX`, and stores firmware producer CRB and context ID.
- `qlcnic_83xx_del_tx_ctx()` destroys a TX context.

Configuration and management:

- `qlcnic_83xx_check_vf()` determines PCI function number, SR-IOV VF status, non-privileged function mode, and selects VF or 83xx NIC ops.
- `qlcnic_83xx_get_fw_version()`, `qlcnic_83xx_get_port_info()`, `qlcnic_83xx_get_port_config()`, `qlcnic_83xx_set_port_config()`.
- `qlcnic_83xx_initialize_nic()` registers or unregisters the NIC function with firmware and requests firmware resources plus loopback IDC/DCB AEN registration.
- `qlcnic_83xx_setup_link_event()`, `qlcnic_83xx_handle_link_aen()`, `qlcnic_83xx_test_link()`, `qlcnic_83xx_get_link_ksettings()`, and `qlcnic_83xx_set_link_ksettings()`.
- `qlcnic_83xx_get_pauseparam()` and `qlcnic_83xx_set_pauseparam()`.
- `qlcnic_83xx_config_led()`, `qlcnic_83xx_set_led()`, and `qlcnic_83xx_get_beacon_state()`.
- `qlcnic_83xx_nic_set_promisc()`, `qlcnic_83xx_sre_macaddr_change()`, `qlcnic_83xx_change_l2_filter()`, `qlcnic_83xx_get_mac_address()`, and `qlcnic_83xx_config_ipaddr()`.
- `qlcnic_83xx_config_hw_lro()`, `qlcnic_83xx_config_rss()`, `qlcnic_83xx_config_intr_coal()`, `qlcnic_83xx_set_rx_tx_intr_coal()`.
- `qlcnic_83xx_get_nic_info()`, `qlcnic_83xx_set_nic_info()`, `qlcnic_83xx_get_pci_info()`, and `qlcnic_get_pci_func_type()`.
- `qlcnic_83xx_config_intrpt()` adds/removes firmware interrupt registrations and stores firmware-provided source offsets.

Diagnostics and statistics:

- `qlcnic_83xx_diag_alloc_res()` and `qlcnic_83xx_diag_free_res()` temporarily detach normal netdev resources, create diagnostic contexts, post RX buffers, and restore prior ring counts/state.
- `qlcnic_83xx_loopback_test()`, `qlcnic_83xx_set_lb_mode()`, `qlcnic_83xx_clear_lb_mode()`, and `qlcnic_extend_lb_idc_cmpltn_wait()` run internal/external loopback with IDC completion AEN synchronization.
- `qlcnic_83xx_interrupt_test()` triggers a firmware interrupt test and checks `diag_cnt`.
- `qlcnic_83xx_reg_test()`, `qlcnic_83xx_get_regs_len()`, `qlcnic_83xx_get_registers()`.
- `qlcnic_83xx_get_stats()`, `qlcnic_83xx_fill_stats()`, and `qlcnic_83xx_copy_stats()` gather TX, MAC/eSwitch, and RX statistics through mailbox responses.

Flash, driver lock, and memory helpers:

- `qlcnic_83xx_lock_flash()` and `qlcnic_83xx_unlock_flash()` serialize flash operations with firmware/shared registers.
- `qlcnic_83xx_lockless_flash_read32()`, `qlcnic_83xx_flash_read32()`, `qlcnic_83xx_read_flash_descriptor_table()`, and `qlcnic_83xx_read_flash_mfg_id()`.
- `qlcnic_83xx_enable_flash_write()`, `qlcnic_83xx_disable_flash_write()`, `qlcnic_83xx_erase_flash_sector()`, `qlcnic_83xx_flash_write32()`, `qlcnic_83xx_flash_bulk_write()`, `qlcnic_83xx_flash_test()`, and `qlcnic_83xx_read_flash_status_reg()`.
- `qlcnic_83xx_lock_driver()`, `qlcnic_83xx_unlock_driver()`, and `qlcnic_83xx_recover_driver_lock()` coordinate multi-function driver locking and forced stale-lock recovery.
- `qlcnic_ms_mem_write128()` writes 128-bit chunks to QDR/DDR memory through indirect memory-space registers with alignment/range checks.

Power/error recovery:

- `qlcnic_83xx_shutdown()` detaches the netdev, cancels IDC work, brings the device down if running, disables mailbox interrupts, and saves PCI state.
- `qlcnic_83xx_resume()` reinitializes IDC, handles vNIC mode, reattaches the driver, and schedules IDC polling.
- `qlcnic_83xx_io_error_detected()`, `qlcnic_83xx_io_slot_reset()`, and `qlcnic_83xx_io_resume()` implement PCI AER handling.

## Control Flow And State Behavior

Probe/hardware selection flow:

1. `qlcnic_83xx_register_map()` installs 83xx operation tables and register maps.
2. `qlcnic_83xx_check_vf()` reads the function number and op mode, selects VF ops for SR-IOV VFs or non-privileged functions, and marks SR-IOV capability for privileged PFs.
3. Firmware version, PCI info, NIC info, port config, and capabilities are read through shared registers and mailbox commands.

Open/context flow:

1. Interrupt setup allocates `ahw->intr_tbl`, chooses MSI-X or legacy fallback, and assigns type/id/source placeholders.
2. Firmware interrupt registration through `qlcnic_83xx_config_intrpt()` fills source offsets.
3. `qlcnic_83xx_create_rx_ctx()` and `qlcnic_83xx_create_tx_ctx()` create firmware contexts and bind hardware CRB producer/consumer pointers to ring structures.
4. NAPI and interrupt enable callbacks then drive RX/TX completion processing elsewhere in the driver.

Mailbox flow:

1. Callers allocate `qlcnic_cmd_args` using metadata-derived register counts.
2. `qlcnic_83xx_issue_cmd()` enqueues the command and selects wait/no-wait/busy-wait semantics.
3. The mailbox worker serializes commands, writes host mailbox registers, sets host ownership, waits for completion signaled by an interrupt or poll path, decodes firmware status, clears ownership, and dequeues.
4. A timeout marks the mailbox not ready, dumps registers, captures mailbox data, requests a firmware dump/reset, and returns timeout status.
5. AEN paths share the same firmware mailbox space and are protected by `aen_lock`.

Configuration flow:

- Link, pause, LED, loopback, RSS, LRO, coalescing, promisc, MAC/VLAN, IP, and NIC info changes generally build one mailbox command, encode context/function identity in `arg[1]`, issue it, and update local `ahw`/adapter state only on success or restore old state on failure.
- Loopback is special: it tears down normal resources, creates diagnostic resources, sets port loopback mode, waits for IDC completion and link-up AENs, sends loopback traffic, clears loopback mode, and restores normal resources.

Flash and persistent state flow:

- Flash operations lock the flash semaphore, program flash direct-window/control/data registers, poll `QLC_83XX_FLASH_STATUS_READY`, and unlock.
- Flash descriptor table and manufacturer ID are cached in `adapter->ahw->fdt` and `adapter->flash_mfg_id`.
- Writes and erases may enable/disable flash write based on FDT manufacturer matching.

Stateful fields include `adapter->flags`, `adapter->state`, `recv_ctx->state`, ring producer/consumer indexes, `ahw->intr_tbl`, `ahw->mailbox`, `ahw->mbox_aen`, `ahw->idc.status`, `ahw->port_config`, `ahw->link_*`, `ahw->beacon_state`, `ahw->fdt`, `adapter->flash_mfg_id`, `ahw->diag_test`, `ahw->diag_cnt`, and temporary LED mailbox register snapshots.

## Dependencies And Integration Points

This file integrates with:

- `qlcnic.h` for adapter/hardware context types, operation-table definitions, common wrappers, and shared constants.
- `qlcnic_83xx_hw.h` for 83xx register offsets, mailbox structs, IDC state, flash constants, and prototypes.
- `qlcnic_sriov.h` for PF/VF interface IDs and broadcast event handling.
- Common qlcnic modules for attach/detach, up/down, context orchestration, RX buffer posting, loopback traffic, firmware dump/reset, IDC state machine, vNIC operation, sysfs, minidump, ethtool, DCB, and SR-IOV.
- Linux PCI error recovery, IRQ registration, MSI-X, workqueues, completions, spinlocks, netdev, ethtool link settings, firmware, and MMIO accessors.

## Risks And Edge Cases

- Mailbox/AEN concurrency is delicate because command completions and async events share firmware mailbox registers. Incorrect ownership clearing or locking can lose events or hang commands.
- `qlcnic_83xx_nic_set_promisc()` and `qlcnic_83xx_sre_macaddr_change()` intentionally return before freeing no-wait command memory on successful queueing; completion cleanup happens later in `qlcnic_83xx_notify_cmd_completion()`. Changing this pattern can double-free or leak.
- Interrupt setup allocates `intr_tbl`; the legacy path returns `-EOPNOTSUPP` for unsupported functions after allocation without freeing in this function, so callers must clean up on failure.
- RX/TX context creation relies on hard-coded mailbox argument offsets and packed structs. Off-by-one register counts corrupt firmware payloads.
- `qlcnic_83xx_create_rx_ctx()` computes `num_sds = adapter->drv_sds_rings - QLCNIC_MAX_SDS_RINGS` in `qlcnic_83xx_add_rings()`; callers must only enter this path when more than the base number of SDS rings exists.
- Diagnostic paths detach/re-attach resources and manipulate ring counts. Failures must restore `drv_sds_rings`, `drv_tx_rings`, `diag_test`, and netdev attachment state.
- Loopback waits depend on AEN delivery and may extend wait time from firmware events. Missing AENs yield timeouts and must clear mode safely.
- Flash functions cast byte pointers to `u32 *` and require 4-byte aligned addresses/counts. Unaligned buffers or counts can fault or corrupt reads.
- Flash erase address byte reversal and OEM/FDT command selection are hardware-specific and easy to break.
- Driver lock recovery force-unlocks stale owners across functions. Incorrect owner detection could break another live function.
- Link setting code maps legacy supported/advertising bits into modern ethtool structures; unsupported half-duplex and autoneg behavior differs by port type.
- AER paths disable PCI and stop polling; reattach failures must leave reset/AER bits consistent.

## Test Signals

High-value validation includes:

- 83xx probe/open/close/remove with MSI-X, MSI, and legacy INTx fallback.
- Mailbox command tests for every metadata entry touched by changes, including timeout injection and AEN interleaving.
- RX/TX context creation/destruction with single ring, multiple SDS/TX rings, RSS/TSS, and loopback diagnostic contexts.
- Link up/down, SFP insert/remove, DCB config-change AEN, IDC request/completion, and broadcast event tests.
- Etthtool coverage: LED identify, link settings get/set, pauseparam get/set, coalescing, register dump, interrupt test, loopback test, flash test, and statistics.
- SR-IOV PF/VF and non-privileged function testing for operation gating and interface ID encoding.
- Flash read/FDT/mfg-id paths on supported hardware, plus write/erase tests only under controlled conditions.
- Suspend/resume and PCI AER recovery with firmware reset/dump paths enabled.
- Lockdep, KASAN, DMA API debug, sparse endian checks, and fault injection for allocation failures and mailbox timeouts.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_83xx_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_83xx_hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_83xx_hw.h

## Purpose

`qlcnic_83xx_hw.h` declares the 83xx/84xx hardware interface for qlcnic. It provides BAR/register offsets, mailbox payload layouts, firmware image constants, reset/IDC data structures, mailbox/AEN state definitions, link/LED/pause/statistics/flash constants, operation prototypes, and helper macros used by `qlcnic_83xx_hw.c`, 83xx initialization, vNIC, minidump, ethtool, and common qlcnic code.

It is the hardware-specific ABI boundary between the common qlcnic driver and 83xx firmware/register semantics.

## Important APIs, Types, And Constants

Register and hardware constants:

- BAR and CRB window definitions: `QLCNIC_83XX_BAR0_LENGTH`, `QLC_83XX_CRB_WIN_BASE`, `QLC_83XX_CRB_WIN_FUNC()`.
- Semaphore/lock registers: `QLC_83XX_SEM_LOCK_FUNC()`, `QLC_83XX_SEM_UNLOCK_FUNC()`, driver lock recovery constants.
- Link and legacy interrupt registers: `QLC_83XX_LINK_STATE()`, `QLC_83XX_LINK_SPEED()`, `QLC_83XX_INTX_PTR`, `QLC_83XX_INTX_TRGR`, `QLC_83XX_INTX_MASK`.
- PEG status, pause registers, PEG PC status registers, and firmware image constants such as `QLC_83XX_FW_FILE_NAME`, `QLC_84XX_FW_FILE_NAME`, and boot-from-file/flash markers.

Mailbox payload structs:

- `struct qlcnic_sds_mbx`: status descriptor ring DMA address, ring size, interrupt ID/value.
- `struct qlcnic_rds_mbx`: regular and jumbo receive descriptor ring DMA addresses, buffer sizes, and ring lengths.
- `struct __host_producer_mbx`: firmware-returned host producer offsets for regular and jumbo rings.
- `struct qlcnic_rcv_mbx_out` and `struct qlcnic_add_rings_mbx_out`: receive context creation/add-rings response fields, including context ID, state, vport, physical port, host consumer offsets, and producer offsets.
- `struct qlcnic_tx_mbx` and `struct qlcnic_tx_mbx_out`: transmit context request and response layouts.
- `struct qlcnic_intrpt_config`: interrupt type/enabled/id/source metadata.
- `struct qlcnic_macvlan_mbx`: endian-specific MAC/VLAN mailbox payload.

Firmware/reset/IDC state:

- `struct qlc_83xx_fw_info`: firmware pointer plus selected firmware file name.
- `struct qlc_83xx_reset`: reset sequence template state, offsets, array scratch, and completion markers.
- `struct qlc_83xx_idc`: inter-driver communication state machine callback, timers, status bits, error/dump flags, current/previous/vNIC states, wait limits, quiesce/delay flags, and state names.
- `enum qlcnic_83xx_states`: firmware/device IDC states from unknown/cold/init/ready through reset/quiescent/failed.
- IDC timing and capability constants such as `QLC_83XX_IDC_INIT_TIMEOUT_SECS`, `QLC_83XX_IDC_RESET_ACK_TIMEOUT_SECS`, `QLC_83XX_IDC_MAX_CNA_FUNCTIONS`, and `QLC_83XX_IDC_FLASH_PARAM_ADDR`.

Mailbox and AEN macros:

- `QLCNIC_MBX_RSP()`, `QLCNIC_MBX_NUM_REGS()`, `QLCNIC_MBX_STATUS()`, `QLCNIC_MBX_HOST()`, and `QLCNIC_MBX_FW()`.
- `QLC_83XX_MBX_AEN_CNT`, `QLC_83XX_MBX_READY`, response states, and command types `QLC_83XX_MBX_CMD_WAIT`, `NO_WAIT`, and `BUSY_WAIT`.
- SFP/link decoding macros: `QLC_83XX_SFP_MODULE_TYPE()`, `QLC_83XX_CURRENT_LINK_SPEED()`, `QLC_83XX_LINK_PAUSE()`, `QLC_83XX_AUTONEG()`, and DCB/FEC/EEE bits.

Feature and configuration constants:

- LED constants `QLC_83XX_ENABLE_BEACON`, `QLC_83XX_LED_CONFIG`, and beacon on/off values.
- Link speed encodings and statistics register counts.
- Function privilege/op-mode macros `QLC_83XX_GET_FUNC_PRIVILEGE()`, `QLC_83XX_DEFAULT_OPMODE`, `QLC_83XX_PRIVLEGED_FUNC`, and `QLC_83XX_VIRTUAL_FUNC`.
- 83xx filter, multicast, unicast, SR-IOV, eSwitch, PVID strip, LRO/LSO/HW-LRO capability bits.

Flash constants:

- Flash register offsets, direct-window helpers, command signatures, read/write/erase modes, read retry counts, status-ready value, write-size bounds, polling delay, OEM command signatures, address temp values, and lock timeout.

Declared functions:

- Hardware ops: register access, mailbox commands, interrupt setup, function number, CAM/API locks, sysfs hooks, NAPI hooks, RX/TX context create/delete, NIC/PCI info, link events, promisc/RSS/LRO/coalescing, MAC/VLAN, MAC address, interrupts, flash access, IDC, vNIC, minidump helpers, ethtool diagnostics, AER, and memory write.
- Notable prototypes include `qlcnic_83xx_issue_cmd()`, `qlcnic_83xx_create_rx_ctx()`, `qlcnic_83xx_create_tx_ctx()`, `qlcnic_83xx_config_intrpt()`, `qlcnic_83xx_lock_flash()`, `qlcnic_83xx_idc_init()`, `qlcnic_83xx_aer_reset()`, and `qlcnic_ms_mem_write128()`.

## Control Flow And State Behavior

The header enables several hardware flows:

1. Initialization code maps BAR0, assigns register tables, detects function/op mode, loads firmware or boots from flash, initializes IDC state, and creates mailbox work state.
2. Context creation packs `qlcnic_sds_mbx`, `qlcnic_rds_mbx`, and `qlcnic_tx_mbx` into mailbox register arrays at fixed offsets. Firmware responds with context IDs and CRB offsets through the corresponding out structs.
3. Interrupt setup stores each interrupt in `qlcnic_intrpt_config`; firmware later fills the source register offset.
4. Mailbox commands use response-state enums, host/FW register macros, and command type to select blocking, nonblocking, or busy-wait behavior.
5. Link, LED, pause, loopback, statistics, SFP, DCB, and autoneg state are encoded in mailbox response words decoded by macros in this header.
6. Flash operations use the flash register constants and status polling values to serialize direct-window reads, writes, sector erase, and descriptor-table reads.
7. IDC state persists across polling work and firmware reset transitions in `struct qlc_83xx_idc`, while `struct qlc_83xx_reset` holds reset template progress.

Persistent state represented by this header includes firmware images in flash, flash descriptor table contents cached elsewhere, IDC control parameters in flash, and device/driver presence registers. Runtime state includes mailbox command queues, interrupt config, reset sequence progress, IDC state, and port/link configuration values.

## Dependencies And Integration Points

This header includes Linux types and Ethernet helpers, plus `qlcnic_hw.h`. It forward-declares `struct qlcnic_adapter` and `struct qlcnic_fw_dump` while relying on full definitions from `qlcnic.h` in implementation files.

Integration points:

- `qlcnic_83xx_hw.c` implements most prototypes and uses all mailbox/register constants.
- `qlcnic_83xx_init.c` and `qlcnic_83xx_vnic.c` use IDC, reset, firmware, and vNIC declarations.
- Common qlcnic code calls these functions through `struct qlcnic_hardware_ops` and `struct qlcnic_nic_template`.
- Etthtool code uses link, pause, LED, register, flash, interrupt, and loopback prototypes.
- Minidump code uses saved-state and template helper prototypes.
- SR-IOV code depends on 83xx PF/VF mode and mailbox behavior.

## Risks And Edge Cases

- Many structs use explicit endian-specific field ordering. Any change must preserve firmware mailbox register layout on both little- and big-endian builds.
- Mailbox register count and fixed offsets such as `QLC_83XX_HOST_SDS_MBX_IDX` and `QLCNIC_HOST_RDS_MBX_IDX` must match firmware expectations and metadata in the implementation.
- Function privilege macros assume two bits per function in the op-mode register; extending function counts or changing register format requires coordinated updates.
- Flash command signatures and polling values are hardware-specific. Incorrect constants can hang flash operations or corrupt persistent firmware/config data.
- Driver-lock recovery constants control force-unlock behavior across PCI functions. Aggressive recovery can break another active function.
- Link/SFP decoding macros pack several concepts into mailbox words; wrong shifts advertise incorrect speed, port type, pause, or module state to ethtool.
- Header prototypes expose many functions across files; changing signatures requires coordinated updates across common, 83xx init, vNIC, SR-IOV, ethtool, and minidump code.

## Test Signals

- Compile tests on little- and big-endian configurations to catch mailbox struct layout issues.
- 83xx/84xx probe, firmware boot-from-flash and boot-from-file, IDC init/reset/quiesce paths.
- Mailbox context create/destroy tests validating register counts and response offsets.
- MSI-X/legacy interrupt registration and firmware interrupt add/delete.
- Etthtool link, pause, LED, stats, register dump, flash, loopback, and interrupt tests.
- Flash descriptor-table read, mfg-id read, and controlled write/erase validation on supported hardware.
- SR-IOV PF/VF and non-privileged function tests for op-mode decoding and mailbox interface ID routing.
- Firmware reset/AER/minidump paths using reset and saved-state helpers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_83xx_hw.h -->
