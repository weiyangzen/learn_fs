# Group Research: group_581_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__1919b8c2294f

Scope checked against `Docs/research_subset_a.md`: all files are under included source tree `sources/os/illumos/illumos-gate`. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_buf.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_buf.h

This header defines the Emulex OneConnect Ethernet driver's buffer-management layer: DMA buffer descriptors, queue ring helpers, receive-buffer descriptors, transmit-buffer descriptors, and cache-management prototypes.

Key contents:
- Queue index helper `GET_Q_NEXT()` and ring-state macros for pending/free/full/empty state, producer/consumer pointer movement, and virtual/physical item lookup.
- TX mapping limits: `OCE_MAX_TX_HDL`, `OCE_MAX_TXDMA_COOKIES`, `OCE_TX_MAX_FRAGS`.
- `oce_addr64_t`, an endian-aware 64-bit physical address accessor split into high/low 32-bit fields.
- `oce_dma_buf_t`, the common DMA allocation descriptor carrying kernel VA, device PA, access handle, DMA handle, size/offset/length, and page count.
- DMA buffer access/sync macros, including `DBUF_PA`, `DBUF_VA`, `DBUF_DHDL`, and `DBUF_SYNC`.
- `oce_ring_buffer_t`, the generic DMA-backed ring descriptor shared by hardware queues.
- Receive buffer descriptor `oce_rq_bdesc_t`, including DMA buffer, receive queue backpointer, fragment address, STREAMS `mblk_t`, free routine, and reference count.
- Transmit copy/mapped buffer descriptors and WQE descriptor structures: `oce_wq_bdesc_t`, `oce_wq_mdesc_t`, `oce_handle_t`, and `oce_wqe_desc_t`.
- WQE entry type enum for header, mapped, copy, and dummy WQEs.
- Packed receive-buffer headroom header `oce_rq_buf_hdr_t` and `OCE_RQE_BUF_HEADROOM`.
- Prototypes for RQ/WQ cache creation/destruction, WQE descriptor constructors/destructors, mapped-DMA-handle caches, and DMA page-list extraction.

Dependencies:
- Includes `sys/ddidmareq.h`, `oce_io.h`, and `oce_utils.h`.
- Uses `struct oce_rq`, `struct oce_wq`, `struct oce_nic_frag_wqe`, `struct phys_addr`, STREAMS `mblk_t`, DDI DMA/access handles, and the driver's `OCE_LIST_NODE_T`.

Research notes:
- This is a low-level memory contract for the OCE transmit/receive paths. Correctness depends on DMA handle lifetime, ring index accounting, and physical-address packing.
- The file is tightly coupled to `oce_io.h` queue definitions and `oce_hw_eth.h` NIC WQE/RQE formats.
- The packed RX buffer header and 18-byte headroom are part of receive packet layout assumptions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_buf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_hw.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_hw.h

This packed hardware-interface header defines the Emulex OneConnect common register, doorbell, event, mailbox, and common-subsystem command formats used by the OCE driver.

Key contents:
- Device generation and device IDs for CNA Gen2/Gen3, TigerShark, and Tomcat.
- PCI/CSR register offsets for semaphores, soft reset, online status, interrupt control, POST state, and image transfer sizing.
- Doorbell offsets and bitfield unions for RX, TX, CQ, EQ, bootstrap mailbox, and MQ doorbells.
- Link-status, network-port, MAC-address-type, interface-capability, mailbox-ring-context, async-event, and RX-filter constants.
- Endian-aware bitfield unions for PCI config interrupt control, semaphores, soft reset, online status, MPU semaphore/control, and hardware doorbells.
- Event queue entry `oce_eqe`, mailbox scatter/gather entry `oce_mq_sge`, mailbox payload `oce_mbx_payload`, mailbox envelope `oce_mbx`, MQ CQE `oce_mq_cqe`, async link-state CQE, and bootstrap mailbox `oce_bmbx`.
- Mailbox subsystem and common-opcode enumerations for interface MAC operations, link status, flash access, queue creation/destruction, flow control, firmware config, VLAN config, RX filter config, MSI message changes, function reset, and function link config.
- Common mailbox request/response header `mbx_hdr` plus status helper macros.
- Mailbox payload structures for link query/set, MAC query/set/add/delete, multicast table, VLAN tags, interface create/destroy, EQ/CQ/MQ context creation/destruction, firmware version, flow control, flash read/write, firmware configuration, VLAN configuration, RX filters, EQ delay modification, maximum mailbox buffer query, function reset, and link enable/disable.

Dependencies:
- Includes `sys/types.h`.
- Uses packed structs and extensive `_BIG_ENDIAN` conditional bitfields.

Research notes:
- This is an ABI-sensitive device wire-format header. Structure layout, packing, endian fields, page-array limits, and opcode values must match firmware.
- Queue creation commands expose hardware context formats for EQ, CQ, and MQ rings, while `oce_io.h` wraps them in driver queue objects.
- Filesystem relevance is indirect through storage/network driver infrastructure: this is a high-speed NIC/FCoE-era hardware contract in the illumos kernel tree.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_hw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_hw_eth.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_hw_eth.h

This header defines the OCE NIC-subsystem hardware descriptors, mailbox commands, statistics layouts, and RSS configuration used for Ethernet transmit and receive operation.

Key contents:
- NIC WQE size, packet type constants, header/data split modes, and WQ type constants.
- NIC mailbox opcodes for RSS, ACPI, promiscuous mode, stats, WQ/RQ create/delete, RSS CQ, RSS MSI, HDS RQ, and advanced RSS.
- RSS enable flags for IPv4, TCP/IPv4, IPv6, and TCP/IPv6 hashing.
- Packed transmit descriptor formats:
  - `oce_nic_hdr_wqe` for header WQEs with checksum, LSO, VLAN, event, completion, total length, and MSS fields.
  - `oce_nic_frag_wqe` for fragment physical address and length.
  - `oce_nic_tx_cqe` for TX completion status, WQE index, packet count, WQ ID, LSO/cast encoding, and valid bit.
- Receive descriptor formats:
  - `oce_nic_rqe` for RX fragment address.
  - `oce_nic_rx_cqe` for packet size, VLAN tag, fragment index/count, checksum pass flags, packet type, RSS data, HDS metadata, and valid bit.
- Valid/invalidate macros for TX and RX CQEs.
- Mailbox payloads for promiscuous mode, NIC WQ create/delete, NIC RQ create/delete, NIC stats retrieval, and RSS configuration.
- Hardware statistics structs:
  - `rx_port_stats`
  - `rx_stats`
  - `tx_counter`
  - `tx_stats`
  - `rx_err_stats`
  - `mem_stats`
  - `mbx_get_nic_stats`

Dependencies:
- Includes `oce_hw.h`.
- Shares packed and endian-sensitive wire formats with firmware and hardware queues.

Research notes:
- This is the Ethernet-specific half of the OCE hardware contract, complementing the common mailbox/register definitions in `oce_hw.h`.
- The stat layout feeds `oce_stat.h` and the driver's kstats.
- RX/TX CQE valid-bit handling and descriptor invalidation are central to queue-drain correctness.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_hw_eth.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_impl.h

This is the main private OCE driver implementation header. It gathers illumos DDI/MAC/FMA dependencies, driver defaults, hardware access macros, adapter state, GLDv3 entry points, hardware lifecycle routines, interrupt routines, and fault-management helpers.

Key contents:
- Size constants, device/queue limits, MTU/frame limits, jumbo-frame limits, multicast limit, queue defaults, buffer sizes, interrupt vector defaults, RSS table/key sizes, and DMA alignment.
- Default OCE capability and enable flags for broadcast, untagged, promiscuous, multicast-promiscuous, and L3/L4 pass-through modes.
- FMA capability flags and default RSS/flow-control settings.
- PCI BAR identifiers for device config, CSR, and doorbell regions.
- Register read/write macros over DDI access handles for CSR, doorbell, and device-config mappings.
- PCI function extraction macro using `PCICFG_INTR_CTRL`.
- Driver lock macros and enums for ring size and driver state.
- `struct oce_dev`, the central adapter state:
  - bootstrap mailbox and locks;
  - WQ/RQ/CQ/EQ/MQ arrays;
  - state/suspend/attach progress;
  - TX/RX copy and reclaim thresholds;
  - PCI BAR mappings and MAC handle;
  - kstats and hardware statistics buffer;
  - link status/speed;
  - interrupt handles/capabilities;
  - queue counts and ring sizes;
  - MTU, MAC address, multicast table, RSS/LSO/promisc/flow-control settings;
  - firmware config, interface ID, function/capability fields, firmware version;
  - PCI IDs and logging controls.
- GLDv3/MAC callbacks for start, stop, send, promiscuous, multicast, unicast, capabilities, ioctl, properties, and stats.
- Hardware lifecycle prototypes for start/stop, hardware identification, BDF lookup, hardware init/fini, adapter setup/unsetup.
- FMA prototypes for init/fini, DMA/register flag setup, ereport emission, and handle checking.
- Interrupt setup/teardown/handler registration and enable/disable prototypes.

Dependencies:
- Includes many illumos kernel headers for DDI, MAC, GLDv3, STREAMS, PCI, FMA, and module support.
- Includes `oce_hw.h`, `oce_hw_eth.h`, `oce_io.h`, `oce_buf.h`, `oce_utils.h`, and `oce_version.h`.

Research notes:
- `struct oce_dev` is the shared state object tying together hardware queues, MAC-layer registration, PCI resources, DMA memory, firmware state, statistics, interrupts, and driver configuration.
- The header is private to the OCE driver and forms the integration layer between illumos MAC/DDI/FMA APIs and the hardware/mailbox definitions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_io.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_io.h

This header defines the OCE driver's queue object model and hardware I/O operation prototypes. It bridges generic ring buffers and hardware mailbox formats into event, completion, mailbox, transmit, receive, and RSS queue management.

Key contents:
- Mailbox and statistics timeouts.
- Queue length/type/state enums for EQs, CQ callbacks, mailbox queues, WQs, RQs, CQs, and RSS.
- `eq_config` and `oce_eq` for event queues with lock, hardware ID, parent/callback context, ring, refcount, state, and delay/vector configuration.
- `cq_config` and `oce_cq` for completion queues with eventability, DMA coalescing, associated EQ, handler, ring, state, and refcount.
- `mq_config`, `oce_mq`, and `oce_mbx_ctx` for mailbox queue state and asynchronous callback context.
- `wq_config` and `oce_wq` for transmit queues, including TX locks, CQ, ring, descriptor caches, free-list structures, preallocated copy buffers/DMA handles, queue state, WQ ID, and scheduling counters.
- `rq_config`, `rq_shadow_entry`, and `oce_rq` for receive queues, including CQ association, receive buffer descriptor arrays, shadow ring, freelist/recycling indexes, pending/buffer-available counts, queue state, and RX/recycle locks.
- `link_status` structure mirroring relevant common mailbox link-status response fields.
- DMA allocation/free and ring-buffer create/destroy prototypes.
- Queue management prototypes for EQ delay, EQ/CQ arming, EQ draining, and RSS readiness.
- Bootstrap and mailbox posting/waiting/dispatch prototypes.
- Hardware and PCI lifecycle prototypes, network interface create/delete, reset, and TX/RX setup/teardown.
- TX/RX operations for queue selection, WQ/RQ CQ draining, start/clean, packet send, receive discharge, and RX pending wait.
- Mailbox helper prototypes for header initialization and firmware/hardware operations: firmware version, MAC address, interface create/delete, interrupt vectors, link status, RX filters, multicast table, firmware config, stats, flow control, promiscuous mode, MAC add/delete, VLAN config, link config, RSS config, and private mailbox ioctl dispatch.

Dependencies:
- Includes DDI types, mutex, STREAMS, debug, byteorder, `oce_hw.h`, and `oce_buf.h`.
- Depends on descriptor and mailbox structures from `oce_hw.h` and `oce_hw_eth.h`.

Research notes:
- This is the operational API used by the OCE implementation files to create/destroy queues, post mailbox commands, and drive TX/RX.
- Queue state is explicit but simple (`QDELETED`, `QCREATED`); higher-level state is in `oce_impl.h`.
- Receive queue management contains separate locks for RX processing and buffer recycling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_ioctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_ioctl.h

This small header defines private OCE ioctl command values and the driver-query payload.

Key contents:
- OCE ioctl base value `OCE_IOC`.
- Private ioctl commands:
  - `OCE_ISSUE_MBOX`
  - `OCE_QUERY_DRIVER_DATA`
- Supported query version `OCN_VERSION_SUPPORTED`.
- `MAX_SMAC` limit for secondary MAC addresses.
- `struct oce_driver_query`, carrying version, secondary MAC address table, primary MAC address, driver name/version strings, and secondary-MAC count.

Dependencies:
- Uses `ETHERADDRL` but does not include the defining Ethernet header itself, relying on including context.

Research notes:
- `OCE_ISSUE_MBOX` exposes a mailbox-issue path, so callers and implementation must validate payload size and firmware-visible structures carefully.
- `OCE_QUERY_DRIVER_DATA` is a small management/introspection ABI for driver identity and MAC addresses.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_stat.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_stat.h

This header defines the OCE driver's kstat-facing statistics structure and stat lifecycle functions.

Key contents:
- `struct oce_stat`, a collection of `kstat_named_t` counters for:
  - RX/TX bytes and frames;
  - RX/TX errors and drops;
  - unicast/multicast/broadcast frame counts;
  - CRC, alignment, range, frame-too-long, address-match, checksum, FIFO, and control/pause frame counters;
  - hardware drop reasons such as no packet buffers, missing descriptors, too many fragments, invalid ring, MTU drops, runt/short/header/tcp-length drops, and no-fragment drops.
- `oce_stat_init()` and `oce_stat_fini()` prototypes.

Dependencies:
- Includes `oce_hw_eth.h` and `oce_impl.h`.
- Uses `kstat_named_t` through `oce_impl.h`.

Research notes:
- The fields correspond closely to `mbx_get_nic_stats` and nested RX/TX stats in `oce_hw_eth.h`.
- This is the public driver-observability surface for OCE hardware counters inside illumos kstats.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_stat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_utils.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_utils.h

This header defines OCE utility macros, logging controls, endian/dword swapping, address helpers, simple list structures, list APIs, atomic reservation, and RSS hash-key generation.

Key contents:
- Logging module masks for config, TX, RX, and ISR.
- Default and maximum log-setting masks.
- `oce_log()` macro, routing messages through `cmn_err()` based on per-device module mask and severity.
- Delay macros `OCE_USDELAY` and `OCE_MSDELAY`.
- Utility macros for log2, address low/high extraction, 64-bit address construction, pointer casts, 4K page offset, and page-count calculation.
- Debug-only `OCE_DUMP()` word dump macro.
- `OCE_DW_SWAP()` and endian-selective `DW_SWAP()` for big-endian conversion of dword buffers.
- Intrusive doubly linked list node `OCE_LIST_NODE_T` and locked list header `OCE_LIST_T`.
- List API prototypes and convenience macros for create/destroy/insert/remove/empty/size/link-init.
- `oce_atomic_reserve()` prototype.
- `oce_gen_hkey()` prototype for generating an RSS hash key.

Dependencies:
- Includes `sys/types.h` and `sys/list.h`.
- Uses `kmutex_t`, `cmn_err`, `CE_*`, `drv_usecwait`, `highbit`, `howmany`, `BMASK_32`, and byteorder macros via including context.

Research notes:
- The list type is driver-local rather than illumos `list_t`; it carries its own mutex and item count.
- The logging macro depends on `OCE_MOD_NAME` and `struct oce_dev` fields from `oce_version.h`/`oce_impl.h`, so include order matters.
- `OCE_DW_SWAP()` is used for firmware/hardware command buffers on big-endian platforms.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_utils.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_version.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_version.h

This header defines the OCE driver version strings, module name, description, and identification string.

Key contents:
- Version components:
  - `OCE_MAJOR_VERSION` = `"1"`
  - `OCE_MINOR_VERSION` = `"2"`
  - `OCE_RELEASE_NUM` = `"0"`
  - `OCE_PROTO_LEVEL` = `"e"`
- Combined `OCE_VERSION` string.
- `OCE_REVISION`, `OCE_MOD_NAME`, `OCE_DESC_STRING`, and `OCE_IDENT_STRING`.

Dependencies:
- No external includes.
- Uses C++ guards.

Research notes:
- The version string is consumed by driver identity/reporting paths, including `oce_ioctl.h` query payloads and logging via `OCE_MOD_NAME`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/oce/oce_version.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/exioct.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/exioct.h

This large header defines QLogic SAN/device-management external ioctl ABI structures and command namespaces used by management tools for the `qlc` Fibre Channel adapter driver.

Key contents:
- External ABI version `EXT_VERSION`.
- Generic constants for signature, WWN, serial, port ID, string, SCSI CDB, MAC address, and address-mode sizes.
- OS-dependent limits imported from `exioctso.h`.
- Main ioctl envelope `EXT_IOCTL`, including signature, request/response addresses, vendor data, status/detail status, request/response lengths, address mode, version, subcode, instance, HBA selector, and vendor-specific status.
- Status and detail-status codes for success, busy, pending, invalid parameters, overruns/underruns, device/HBA readiness, mailbox/SCSI status, unsupported subcodes/versions, queue full, and VP index errors.
- DeviceControl/ioctl command aliases for query, FCCT/ELS/SCSI passthrough, AEN registration/retrieval, RNID, host/RISC/NVRAM/option ROM/VPD/flash operations, fcache, SFP, PCI data, firmware traces, vports, reset, I2C, dump, SerDes, VF state, flash update capabilities, and BB_CR data.
- Extensive subcode definitions for query/get/set operations, SCSI passthrough, NVRAM scope, vport commands, flash access, firmware reset, I2C temperature, dump, SerDes, and flash-update capabilities.
- Query/result structures for HBA node, HBA port, FC4 statistics, loopback request/response, discovered ports/targets/LUNs, SCSI/FC/destination addresses, port statistics, driver properties, firmware properties, chip properties, CNA port properties, adapter region versions, RNID requests/responses, SCSI and FC-SCSI passthrough, AEN registration/events, beacon control, LUN bitmasks, device database entries/lists, target swap data, IIDMA port parameters, PCI option-ROM header/data, Menlo/Mercury firmware management, virtual port IDs/params/info, board temperature, SerDes registers, VF state, FCF list, resource counts, firmware FCE trace, ELS passthrough request, flash update capabilities, and BB_CR data.
- Macros for LUN bitmask manipulation and many FC/FCoE/port-speed/device-type constants.

Dependencies:
- Includes `exioctso.h`.
- Uses fixed QLogic typedef aliases such as `UINT8`, `UINT16`, `UINT32`, `UINT64`, `INT32`, and `INT64`.

Research notes:
- This is a management ABI, not just an internal header. Structure sizes and fields are annotated and must remain compatible with user tools.
- Several structures use embedded addresses as integer fields because ioctl callers may be 32-bit or 64-bit, controlled by `AddrMode`.
- The file spans classic Fibre Channel, FCoE/CNA, Menlo/Mercury management, virtual ports, flash/NVRAM, diagnostics, firmware traces, and physical-layer controls.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/exioct.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/exioctso.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/exioctso.h

This OS-dependent companion header supplies illumos/Solaris type aliases, platform limits, address-mode selection, and ioctl command numbers for the QLogic external ioctl ABI in `exioct.h`.

Key contents:
- Includes `sys/int_types.h`.
- Defines `INT8`, `INT16`, `INT32`, `INT64`, `UINT8`, `UINT16`, `UINT32`, and `UINT64`.
- Selects `EXT_ADDR_MODE_OS` as 64-bit under `LP64`, otherwise 32-bit.
- Defines OS limits for maximum HBAs, buses, targets, LUNs, non-SCSI3 LUNs, and AEN queue entries.
- Assigns OS ioctl command numbers from `EXT_CC_QUERY_OS` through `EXT_CC_GET_BBCR_DATA_OS`.
- Defines `EXT_CC_HBA_NODE_SBUS`.

Dependencies:
- Consumed directly by `exioct.h`.

Research notes:
- This file isolates OS-specific command-number and sizing decisions from the otherwise broad QLogic management ABI.
- Address mode selection is important for mixed 32-bit userland and 64-bit kernel ioctl handling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/exioctso.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_api.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_api.h

This is the central private API/state header for the QLogic `qlc` Solaris Fibre Channel adapter driver. It defines driver-wide constants, register access macros, queue state, DMA descriptors, target/LUN state, adapter state, flags, locking macros, return codes, and exported private function prototypes.

Key contents:
- Includes illumos SCSI, byteorder, PCI, DDI/FMA, QLogic open header, Fibre Channel public headers, and FCA interface definitions.
- Compatibility definitions and weak declarations for DDI interrupt APIs.
- PCIe/MSI/MSI-X/SR-IOV register constants and NPIV status fallback constants.
- Fibre Channel speed constants through 32Gbit.
- Bit constants `BIT_0` through `BIT_63`.
- DDI register access macros for normal registers, IO-mapped registers, and memory BAR registers.
- Fibre Channel constants for LUN limits, QLogic FCA brand, local ELS codes, loop IDs, fabric IDs, N-port handles, topology flags, timers, queue sizes, DMA attributes, and SG list limits.
- Register offset table `reg_off_t`, flash/NVRAM/VPD address maps for multiple adapter generations, flash error log constants, VPD tags, RISC-to-host status values, and HCCR commands.
- Initialization control blocks for older ISP adapters and 24xx+ adapters, including virtual-port configuration and extended initialization block support.
- IP initialization control blocks.
- DMA memory descriptor `dma_mem_t`, memory allocation/alignment enums, and 24-bit `port_id_t`.
- Intrusive link/list headers `ql_link_t` and `ql_head_t`.
- Request/response queue contexts `ql_request_q_t` and `ql_response_q_t`.
- Per-command state `ql_srb_t`, with transport packet, watchdog, unsolicited buffer, FCP, request sense, queue, IOCB, token, retry, and DMA SG context.
- SRB state flags for ISP started/completed, retry, poll, watchdog, ELS, unsolicited-buffer ownership/callbacks, FCP/IP/generic services, timeout, abort, device queue, token array, and management service.
- LUN and target queue structures:
  - `ql_lun_t` for per-LUN command queue, throttle, SCSI3 LUN address, and link.
  - `ql_tgt_t` for per-target locking, port ID, loop ID, outstanding count, IIDMA rate, watchdog, unsolicited-buffer state, retry counters, login state, port database data, PRLI data, and LUN queues.
- Target flags, IIDMA rates, kstat device/adapter stat structures, firmware code segment structure, dump state flags, extended logging trace structures, NVRAM cache descriptor, and PLOGI retry descriptor.
- Attach-progress flags and legacy interrupt-set structure.
- Mailbox data and LED state structures.
- `ql_adapter_state_t`, the central adapter object with:
  - global HBA linkage, locks, state flags, topology, timers, BB_CR state;
  - task daemon and completion taskq state;
  - interrupt handles and capabilities;
  - outstanding command tokens;
  - request/response queues;
  - receive buffer queue;
  - mailbox synchronization;
  - unsolicited buffer tracking;
  - device queues and kstats;
  - PCI and device mappings;
  - Solaris FCA registration data;
  - firmware, RISC, NVRAM, power-management, SBus, ioctl, cache, dump, trace, virtual-port, FCoE, NetXen, DMA attribute, and FMA state.
- Adapter state flags, task daemon flags, mailbox flags, configuration flags, interrupt flags, endian helpers, loop/device validity macros, daemon/loop readiness macros, interrupt-pending macro, and locking macros.
- Local return/status codes, SBus FPGA definitions, port ID/name extraction macros, ELS command table initializer, ELS descriptor structures, PRLI response structures, globals, and many private function prototypes for flash, firmware dump, DMA, queues, ELS, device lookup, loop state, unsolicited buffers, NVRAM cache, PLOGI params, interrupts, and module dump templates.

Dependencies:
- Depends on many qlc-specific types from other headers, including `ql_adapter_revlvl_t` from `ql_apps.h` and firmware/NVRAM types from `ql_init.h`.
- Uses illumos Fibre Channel types such as `fc_packet_t`, `fc_unsol_buf_t`, `fc_fca_tran_t`, `fca_port_attrs_t`, `la_els_logi_t`, `fcp_cmd_t`, and `la_wwn_t`.

Research notes:
- `ql_adapter_state_t` is the main driver architecture map; most qlc source files operate on it.
- The header preserves compatibility across many QLogic adapter generations: 22xx/23xx/24xx/25xx/27xx/80xx/81xx/82xx/83xx, FC and FCoE.
- Filesystem relevance is through storage I/O: this is a Fibre Channel HBA driver surface used by SCSI/FCP storage paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_api.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_apps.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_apps.h

This header defines QLogic application/utility-facing structures and ioctl command constants used by tools such as `qladm` and `qlctest`.

Key contents:
- Firmware trace buffer sizes `FWEXTSIZE` and `FWFCESIZE`.
- ISP8100 extended initialization control block `ql_ext_icb_8100_t`, including FCF matching, VLAN ID, fabric name, and proposed MAC address.
- Adapter revision-level structure `ql_adapter_revlvl_t`.
- Application mailbox command structure `app_mbx_cmd_t`.
- Diagnostic loopback parameter structure `lbp_t`, with different pointer widths under `apps_64bit`.
- Diagnostic operation IDs for command queue check, firmware checksum, self-test, revision level, mailbox/data loopback, firmware execution, adapter feature bits, NVRAM defaults, and ECHO.
- Utility ioctl command values for load/dump, FOAPI reserved range, and admin operations.
- Admin command enum `ql_adm_cmd_t` for extended logging, adapter info, device list, loop reset, firmware dump/trigger, beacon, NVRAM, flash, property updates, VPD, and firmware module update.
- Admin operation envelope `ql_adm_op_t`.
- Adapter info payload `ql_adapter_info_t`.
- Port-type enum and device-info payload for admin device listing.

Dependencies:
- Includes `sys/scsi/scsi_types.h`.
- Shares types with `ql_api.h` and `ql_init.h`.

Research notes:
- This file is a smaller, utility-facing ABI separate from the broader SAN/device-management ABI in `exioct.h`.
- The `apps_64bit` conditional in `lbp_t` is a direct user/kernel compatibility concern for diagnostic loopback buffers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_apps.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_debug.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_debug.h

This header defines QLogic qlc debug and extended logging prototypes/macros.

Key contents:
- Debug function prototypes:
  - `ql_dump_buffer`
  - `ql_el_msg`
  - `ql_dbg_msg`
  - `ql_flash_errlog`
  - `ql_dump_el_trace_buffer`
- Conditional `QL_DEBUG_ROUTINES` and message prefix macros based on `QL_DEBUG`.
- Global extended-log and trace-buffer locking macros.
- Extended log macro `EL()` and direct `cmn_err()` error macros `ER()`/`ERV()`.
- Trace buffer reservation and debug stack-depth constants.
- Debug levels 1 through 16, each conditionally mapping `QL_PRINT_N` and `QL_DUMP_N` to debug routines when the relevant `QL_DEBUG` bit is enabled, or to no-ops otherwise.
- Level 2 is enabled for any nonzero lower 16 bits of `QL_DEBUG` through `QL_DEBUG_ROUTINES`; level 9 is enabled for `QL_DEBUG & 0x104`.

Dependencies:
- Uses `ql_adapter_state_t`, `ql_global_el_mutex`, `cmn_err`, `CE_CONT`, and mutex primitives from including context.

Research notes:
- This is compile-time controlled instrumentation; when debug bits are disabled most macros compile away.
- The file provides both per-adapter debug logging and global extended logging trace-buffer support.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_debug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_fm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_fm.h

This header defines qlc-specific FMA ereport classes, fault IDs, report metadata, external DMA/access attributes, and FMA helper prototypes.

Key contents:
- QLogic device class string `QL_FM_DEVICE`.
- qlc-specific ereport class strings for DMA error, bad payload, command failure, chip hang, unknown errors, asynchronous mailbox request/response transfer errors, access-handle errors, and DMA-handle errors.
- Maximum ereport class length `QL_FM_MAX_CLASS`.
- `qlc_fm_ereport_t`, mapping fault ID, description, qlc eclass, generic eclass, and impact code.
- `qlc_fm_ereport_fid_t` enum for qlc fault IDs.
- External DDI access and DMA attribute declarations.
- FMA prototypes for access-handle checking, DMA-handle checking, DDI error callback, init/fini, impact reporting, service impact, and per-packet DMA-handle checking.

Dependencies:
- Uses `ql_adapter_state_t`, `ql_srb_t`, DDI FMA types, and DDI DMA/access types from including context.

Research notes:
- This is the qlc driver's FMA integration boundary.
- The ereport IDs align driver-detected hardware/DMA/command failures with illumos fault-management reporting.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_fm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_init.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_init.h

This header defines QLogic adapter initialization, NVRAM, firmware dump, dump-template, NVRAM access, device-list, and initialization lifecycle interfaces.

Key contents:
- External task callback delay `ql_task_cb_dly`.
- Classic ISP2200-style `nvram_t` layout, including firmware options, frame/IOCB/execution settings, WWPN/WWNN, connection options, host parameters, boot target data, adapter features, subsystem IDs, and checksum.
- 24xx+ `nvram_24xx_t` layout with initialization control data, firmware options, serial link controls for multiple adapter families, FCoE/MAC fields, host/BIOS/boot parameters, CLP flags, default names, enhanced features, firmware table pointers, model fields, feature masks, subsystem IDs, and checksum.
- Firmware dump sizes for 2200, 2300, 6322, 24xx, 25xx, 81xx, 27xx, and 83xx adapters.
- VPD and SFP sizes.
- Firmware dump structures:
  - `ql_fw_dump_t` for 2200/2300-era devices.
  - `ql_24xx_fw_dump_t`
  - `ql_25xx_fw_dump_t`
  - `ql_81xx_fw_dump_t`
  - `ql_83xx_fw_dump_t`
- Kernel-only dump-template entry type constants and structures for template headers, entry headers, I/O register reads/writes, PCI reads/writes, RAM reads, queue/FCE capture, RISC pause/resume, interrupt disable, host-buffer dumps, scratch capture, register reads/writes, and raw dump data.
- NVRAM lock flags for NVRAM and VPD data.
- Product ID constants after reset.
- NVRAM command bit definitions for start, read, write, erase, mask, and delay.
- Device ID list structures for old, extended, and 24xx formats, plus union `ql_dev_id_list_t`.
- Device-list entry count `DEVICE_LIST_ENTRIES`.
- Kernel prototypes for adapter initialization, PCI/SBus config, NVRAM config/read/write/lock/release, property handling, firmware load/start, cache-line setup, ring init, firmware readiness, device-list parsing, chip reset, ISP abort, command requeue, and virtual-port control/create/destroy.

Dependencies:
- Uses constants/types from `ql_api.h` and `ql_apps.h`, including queue sizes, `ql_ext_icb_8100_t`, and `ql_adapter_state_t`.
- Kernel-only section depends on many `BIT_*` constants and qlc core types.

Research notes:
- This file is adapter-generation compatibility-heavy. NVRAM and dump layouts are hardware/firmware contracts and should not be casually refactored.
- Firmware dump structures include variable/extensible tails for trace buffers and extended memory.
- The kernel-only dump-template structures describe a firmware-provided or module-provided recipe for capturing hardware state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_init.h -->