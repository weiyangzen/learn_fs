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
