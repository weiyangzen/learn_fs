# Group Research: group_582_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__fdc4fe934487

Scope verified against `Docs/research_subset_a.md`. The subset includes `sources/os/illumos/illumos-gate`, and all eleven requested source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_iocb.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_iocb.h

## Role

`ql_iocb.h` defines the hardware IOCB contract for the illumos `qlc` QLogic ISP2xxx Fibre Channel adapter driver. It is a protocol/header file rather than executable logic: it names queue entry opcodes, fixed DMA descriptor layouts, status values, and the prototypes used by `ql_iocb.c` to build request queue entries.

## Major Definitions

The file starts with generic 32-bit and 64-bit DMA data segment layouts, then defines many IOCB formats used by different hardware generations and modes.

Initiator command formats include:
- Type 2 32-bit SCSI command IOCBs with extended LUN support.
- Type 3 64-bit command IOCBs.
- Type 6 and Type 7 ISP24xx command IOCBs.
- FCP command DMA layout for Type 6 commands.
- Command chaining and continuation entries for scatter/gather lists.

Completion and synchronization formats include:
- Classic and ISP24xx status entries.
- Status continuation entries for extra sense data.
- Marker entries and ISP24xx marker entries.
- Completion status constants such as complete, incomplete, DMA error, reset, aborted, timeout, underrun, queue full, port unavailable/logged out/busy, and driver-defined status values.

Management and fabric/control IOCBs include:
- Management Server and CT passthrough entries.
- ELS passthrough request and response entries.
- Task management entries.
- Abort command entries.
- Login/logout/log entry structures.
- Virtual port control, virtual port modify, and report-ID acquisition entries.
- Menlo firmware verification and Menlo data access entries.

Target-mode and IP-over-FC layouts include:
- Enable/modify LUN entries.
- Immediate notify and notify acknowledge entries, with ISP24xx variants.
- ATIO and CTIO request/response structures.
- IP transmit, receive, receive-continuation, 24xx receive, and buffer pool entries.

The `ql_mbx_iocb_t` union collects the major mailbox-executed IOCB variants into one command container.

## Interfaces

The prototypes exported for `ql_iocb.c` cover:
- Starting IOCBs and issuing markers.
- Loading receive buffers.
- Building command, management-server, and IP IOCBs.
- Separate 24xx builders for command, management-server, and IP IOCBs.

## Integration Notes

This header is layout-sensitive. Most structures mirror firmware queue entries and DMA-visible hardware formats, so field order, width, and padding are part of the driver/firmware ABI. It depends on driver-private types such as `ql_adapter_state_t`, `ql_srb_t`, `ql_request_q_t`, `ql_tgt_t`, and `ql_lun_t` from the broader `qlc` driver.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_iocb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_ioctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_ioctl.h

## Role

`ql_ioctl.h` declares the public internal entry points implemented by `ql_ioctl.c` for the `qlc` Fibre Channel adapter driver. It is a small prototype header with no data structure definitions.

## Interfaces

The file declares:
- Character-device entry points: `ql_ioctl`, `ql_open`, and `ql_close`.
- NVRAM utility load/dump helpers.
- VPD load/dump and VPD lookup helpers.
- Flash read/modify/write access through `ql_r_m_w_flash`.
- NVRAM read access through `ql_get_nvram`.

## Integration Notes

The header depends on illumos DDI types such as `dev_t`, `cred_t`, `intptr_t`, and `caddr_t`, plus `ql_adapter_state_t` from the `qlc` driver. It sits between the driver’s device-node control plane and lower flash/NVRAM/VPD management routines.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_isr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_isr.h

## Role

`ql_isr.h` declares interrupt-handling interfaces and interrupt tuning globals for the `qlc` Fibre Channel adapter driver.

## Major Definitions

The file defines `MAX_SPURIOUS_INTR` as `4` and declares two global counters/tuning values:
- `ql_spurious_cnt`
- `ql_max_intr_loop`

## Interfaces

The interrupt entry points are:
- `ql_isr`, the main ISR callback.
- `ql_isr_aif`, an alternate interrupt function handler.
- `ql_isr_default`, the default interrupt handler.
- `ql_disable_intr` and `ql_enable_intr` for adapter interrupt masking.

## Integration Notes

The declarations depend on illumos interrupt callback types (`uint_t`, `caddr_t`) and the driver state type `ql_adapter_state_t`. The header does not define interrupt status bits; those are supplied by hardware and mailbox/register headers.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_isr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_mbx.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_mbx.h

## Role

`ql_mbx.h` defines the mailbox command/status interface for the illumos `qlc` QLogic ISP2xxx Fibre Channel adapter driver. Mailbox commands are the driver’s control path into firmware for initialization, link management, diagnostics, flash access, fabric login/logout, resets, resource queries, and extended 8xxx/82xx features.

## Major Definitions

The file groups firmware status and event constants:
- ROM/self-test states, firmware running/config errors, and command completion statuses.
- Sub-error codes for mailbox command errors.
- Asynchronous event codes for reset, system errors, request/response transfer errors, LIP/link changes, port database updates, RSCN, SCSI/IP/CTIO completions, DCBX/FCF updates, temperature events, D_Port diagnostics, IDC events, SFP insertion/removal, NIC firmware state, and autoload firmware events.
- Event-specific reason fields for port database updates, RSCN scope, thermal alerts, D_Port diagnostics, and Menlo alerts.

Mailbox command opcodes include:
- Firmware load/execute/dump/read/write/checksum commands.
- Abort, target reset, LUN reset, clear/abort task set commands.
- Loop, fabric, port database, login/logout, SNS, RNID, link status, and FC_AL commands.
- IP initialization/unload and XGMAC/statistics commands.
- Flash access, SFP, SERDES, LED, DCBX, FCF, IDC, port reset/config, mini-dump template, and 82xx interrupt toggling commands.

The header defines command option masks and data structures:
- `mbx_cmd_t` for mailbox command descriptors.
- Diagnostic `echo_t`.
- Loop Fabric Address command payloads.
- 23xx and 24xx port database layouts.
- Port database state values and helper macro `PD_PORT_LOGIN`.
- Link configuration fields for pause, DCBX, loopback, backplane training, autonegotiation, and jumbo frames.
- FCF list descriptor `ql_fcf_list_desc_t`.

## Interfaces

The prototypes cover the complete mailbox-control surface:
- IP bring-up/shutdown, online self-test, loopback, ELS echo, and LFA/change requests.
- SCSI task management and target/LUN resets.
- Loop/fabric login, logout, port database fetches, loop maps, RNID, link status/statistics, LIP, and ID list operations.
- RISC RAM word/block read/write, mailbox IOCB execution, mailbox wrap test, firmware execution/init/state/version/options.
- Diagnostics for loopback, echo, beacon, SERDES, SFP, firmware tracing, Menlo reset, MPI restart, IDC, port config, flash access, XGMAC stats, DCBX, FCF, resource counts, mini-dump template, flash image load, LED config, remote register access, temperature, and SERDES read/write.
- `MBOX_CMD_TABLE()` maps mailbox opcodes to printable command names for logging/debugging.

## Integration Notes

This is one of the central firmware ABI headers for `qlc`. Constants are shared by ISR, initialization, firmware, flash, diagnostic, and ioctl paths. Many numeric values are reused by different hardware generations, so callers must interpret command/event values in adapter-generation context.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_mbx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_nx.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_nx.h

## Role

`ql_nx.h` defines NetXen/82xx-style hardware support used by the `qlc` driver. It describes chip revisions, firmware/device state handshakes, CRB/register address maps, PCI/windowing rules, ROM/flash access constants, interrupt register mappings, and minidump template formats.

## Major Definitions

The file includes:
- P3/P3-plus revision constants and revision test macros.
- Phantom firmware initialization states and host acknowledgement values.
- Device state values such as poll, cold, initializing, ready, need reset, need quiescent, failed, and quiescent.
- CRB/NIC register offsets for command producer/consumer indexes, pause buffers, firmware command/argument registers, command and receive PEG state, interrupt coalescing, RX/TX packet timers, XG state, DMA shift, link speed, software interrupt masks, capabilities, MSI mode, and virtual-port mappings.
- Extensive CRB hub/agent address mapping tables and macros for transforming hardware address spaces.
- ROMUSB/ROM controller registers and SPI ROM instruction opcodes.
- PCI/PCIe memory windows, 128 MB and 2 MB address ranges, CRB windows, direct and indirect addressing helpers, MSI-X table constants, PCI IDs, and interrupt target/mask registers.
- `NX_LEGACY_INTR_CONFIG`, a static initializer for legacy interrupt vector and target-mask/status register mappings across functions.
- Flash and firmware offsets, board info magic, bootloader/image start offsets, and firmware size offset.
- CRB lock, ROM lock, IDC lock, and firmware reset acknowledgement timeout constants.

## Minidump Support

The latter part defines NetXen mini-dump metadata:
- Template command options for size-only versus full-template retrieval.
- Entry type constants for CRB, MUX, queue, board, SRE, OCM, processor registers, caches, stacks, ROM, memory, control entries, and end markers.
- `md_template_hdr_t`, `md_entry_hdr_t`, generic `md_entry_t`, and specialized read/control entry structures for CRB, cache, OCM, memory, ROM, MUX, queue, and control operations.
- Driver flag bits for skipped entries and size errors.
- Control opcodes for write, read/write, AND, OR, poll, read state, write state, and modify state.
- MIU test-agent registers used by minidump memory reads.

## Interfaces

The exported `ql_nx.c` prototypes cover:
- 82xx 32-bit register read/write.
- Chip reset and firmware reload/check/reset.
- Hardware and firmware interrupt clear/enable/disable.
- CRB interrupt pointer updates.
- ROM read/write/erase/status-register write.
- Driver-active state set/clear.
- IDC event handling and polling.
- Request-in register writes.
- Mini-dump template retrieval.

## Integration Notes

This header is highly hardware-specific and depends on macros/types defined elsewhere in the `qlc` driver, including `UNM_PCI_CRBSPACE`, `ql_adapter_state_t`, and bit constants. It is the low-level map that lets the Fibre Channel driver manage converged NetXen/QLogic hardware resources shared with NIC functions.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_nx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_open.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_open.h

## Role

`ql_open.h` provides build-time default identity/version settings for the illumos `qlc` Fibre Channel adapter driver.

## Definitions

The file conditionally defines:
- `QL_VERSION` as `151216-3.07`.
- `QL_NAME` as `qlc`.
- `QL_DEBUG` as `0x0`.
- `OS_MAJ` as `11`.

## Integration Notes

The values are guarded with `#ifndef`, allowing the build system or including source to override them. The header has no function prototypes or data structures.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_open.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_xioctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_xioctl.h

## Role

`ql_xioctl.h` defines extended ioctl support structures and helper interfaces for the `qlc` Fibre Channel adapter driver. It bridges management utilities to mailbox, flash, VPD, firmware image, LED, link-statistics, AEN, and fabric management operations.

## Major Definitions

The file includes:
- Management server loop IDs for older and 24xx adapters.
- `ql_mbx_ret_t`, a mailbox return-register container.
- Name-match flags for node name, port name, port ID, and loop ID.
- CT information unit preamble layout and directory-server type.
- Big-endian link statistics counters.
- REPORT LUN header/list structures.
- Flash chip information and flash description table structures.
- Flash manufacturer IDs, device IDs, and flash type flags.
- LED/beacon state flags for older and 24xx adapters.
- PCI option ROM header/data structures and code-type constants.
- Firmware cache entry `ql_fcache_t` and firmware image type flags.
- Flash layout table pointer/header/region structures.
- Function/port configuration map structures, with function types for NIC, FC, iSCSI, and vNIC.
- Flash region identifiers for firmware, boot code, VPD, NVRAM, flash description, error logs, golden firmware, bootloader, and 8021-specific regions.
- `ql_xioctl_t`, the per-adapter extended ioctl context containing flash description, adapter I/O statistics, SNIA counters, AEN tracking queue state, and flags.

## Interfaces

The prototypes include resource allocation/free for xioctl state, the `ql_xioctl` dispatcher, AEN enqueueing, firmware-cache setup/release/search, LED blinking, FCode/PCI dump and load helpers, and loop-point configuration.

## Integration Notes

This header is coupled to external FC HBA ioctl definitions via `<exioct.h>` and to QLogic driver state through `ql_adapter_state_t`. It also duplicates some flash-description concepts found in hardware headers because ioctl utilities need stable payload definitions for firmware and flash operations.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_xioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlge/qlge.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlge/qlge.h

## Role

`qlge.h` is the main private driver header for the illumos `qlge` QLogic Ethernet driver. It connects illumos DDI/MAC/GLD facilities with QLogic hardware definitions from `qlge_hw.h`, debug macros from `qlge_dbg.h`, and version defaults from `qlge_open.h`.

## Major Definitions

The file defines:
- Driver identity (`ADAPTER_NAME`), boolean compatibility values, endian conversion macros, helper word/byte extraction macros, carrier update macros, and common return codes.
- Solaris compatibility/timer/DMA constants.
- DMA descriptor wrapper `struct dma_info` and helper macros for sync, virtual address access, and zeroing.
- Initialization step flags used during attach/setup/teardown.
- TX/RX limits for scatter/gather, LSO, copy thresholds, VLAN fallback constants, checksum offsets, and timeout thresholds.
- MAC driver states such as init, attached, started, bringdown, stopped, detach, and suspended.
- Soft reset request flags.
- Ioctl reply enum values used by STREAMS/ioctl handlers.
- Link speeds, multicast and unicast address containers, kstat index values, loopback modes, and flash-image search states.

Queue and ring structures include:
- `bq_desc` for receive buffer descriptors and recycle callbacks.
- `tx_ring_desc` for TX queue entries, DMA handles, copy buffers, OALs, and packet metadata.
- `tx_ring` for work queue state, locks, producer/consumer indexes, doorbell registers, statistics, and queue-stop state.
- `rx_ring` for completion queue state, interrupt routing, receive statistics, large/small buffer queues, producer/consumer indexes, free/in-use descriptor rings, and polling/copy counters.
- `intr_ctx` for interrupt handler association, masks, and in-flight handler counts.
- `tx_buf_desc` for transmit buffer address/length descriptors.

The central `qlge_t` soft-state structure contains:
- DDI device, PCI, access-handle, register, and fault-management state.
- Interrupt handles and priorities.
- MAC registration handles, kstats, and GLD statistics.
- Adapter mutexes, timers, power state, function identifiers, link state, MTU, duplex, pause, loopback, DCBX, and LSO state.
- Multicast/unicast address state.
- Soft interrupt handles for MPI events and resets.
- Extended ioctl staging buffers and MPI core-dump storage.
- Mailbox synchronization fields, firmware/version/port config data, and ioctl DMA buffers.
- Flash layout, VPD, NIC configuration, and flash description state.
- TX/RX rings, coalescing settings, copy thresholds, RSS/ring counts, polling counters, and optional buffer-usage tracking.

## Interfaces

The header declares functions from multiple `qlge` source files:
- Register access, waits, PCI dumps, descriptor dumps, firmware dumps, GLD setup, chip/loop ioctls, and binary core dumps.
- Delay, semaphore locking, initialization, start/stop, multicast/promiscuous updates, hardware stats, TX/RX paths, doorbell access, MAC address register programming, XGMAC reads, interrupt control, polling, hashing, atomics, timers, and route initialization.
- Flash locking, flash load/dump/VPD/parameter helpers.
- MPI interrupt handling, MPI reset, firmware state/version, link status, mailbox tests, port config, loopback/pause, LED config, SFP dump, IDC request, flash tests, processor data access, RISC RAM access, and system error triggers.
- Core dump and debug printing helpers.
- Unicast MAC setup and fault-management helpers.

## Integration Notes

`qlge.h` is the driver’s coordination point. It is not a hardware ABI by itself; it composes illumos networking, DMA, interrupt, kstat, fault-management, mailbox, flash, and ring state around the fixed layouts in `qlge_hw.h`.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlge/qlge.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlge/qlge_dbg.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlge/qlge_dbg.h

## Role

`qlge_dbg.h` defines debug-level flags and conditional debug/core-dump macros for the `qlge` Ethernet driver.

## Major Definitions

Debug levels include flags for:
- NVRAM/register/PCI operations.
- Initialization.
- GLD.
- Mailbox and flash.
- RX, RX rings, TX, statistics, and interrupts.

If `QL_DUMPFW` is defined, `QLA_CORE_DUMP` and `QLA_DUMP_CRASH_RECORD` call the corresponding dump functions; otherwise they compile away.

If `QL_DEBUG` is enabled, macros route debug printing and buffer/descriptor dumps through `ql_printf`, `ql_dump_buf`, `ql_dump_req_pkt`, `ql_dump_cqicb`, and `ql_dump_wqicb` when the adapter’s `ql_dbgprnt` mask includes the requested level. If `QL_DEBUG` is disabled, these macros compile to no-ops.

The file also defines logging severity marker strings:
- `QL_BANG`
- `QL_QUESTION`
- `QL_CAROT`

## Integration Notes

This header depends on `qlge_t` fields and debug helper functions declared elsewhere, especially in `qlge.h`. It is deliberately macro-heavy so debug code can be compiled out when not enabled.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlge/qlge_dbg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlge/qlge_hw.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlge/qlge_hw.h

## Role

`qlge_hw.h` is the fixed hardware/register/firmware ABI header for the illumos `qlge` QLogic Ethernet driver. It defines bit constants, register offsets, mailbox structures, flash layouts, ioctl payloads, core-dump formats, queue initialization blocks, and network IOCB formats.

## Major Definitions

The file starts with general constants:
- Schultz adapter/device identification.
- Mailbox register counts.
- `BIT_0` through `BIT_31`.
- `ql_stats_t`, the driver-visible statistics bundle for interrupts, speed, duplex, TX/RX counters, multicast/broadcast counters, CRC/errors, and hardware stats.
- Ethernet CRC size and processor/mailbox address register constants.

Hardware register sections define bit fields for:
- System, reset/failover, function-specific control, host command/status, configuration, status, revision ID, forced ECC error, error status, semaphores, completion queue stop, MAC address index, split-header, NIC receive config, routing index, CAM output routing, completion queue interrupt status, processor address, host command, XGMAC access, MAC protocol address control, TX/RX config, pause frames, and XGMAC statistics.

Networking and queue definitions include:
- Interrupt enable/disable macros.
- Completion queue, RX ring, and TX ring limits.
- Large-buffer queue and buffer queue address elements.
- Link state enum.
- Work queue initialization block `wqicb_t`.
- Completion queue initialization block `cqicb_t`.
- RSS initialization block `ricb`.
- Host command IOCB opcodes.
- OAL entries and outbound MAC request/response IOCBs.
- Inbound MAC response IOCB with checksum, VLAN, RSS, split-header, buffer-selection, and receive error flags.
- System event IOCB with link, CAM, ECC, management fatal, MAC interrupt, and PCI buffer-read error events.
- Generic network response IOCB and request/response entry-size macros.

Control-plane and diagnostic definitions include:
- ioctl command base `QLA_IOC` and commands for PCI/register access, debug level get/set, flash read/write, VPD read, properties, adapter listing, firmware image read/write, staged copy in/out, core dump, system error trigger, and soft reset.
- ioctl payload structures for header metadata, PCI/device registers, flash I/O, MPI version, link status, adapter properties, adapter info, dump headers/image headers/footer, and crash records.
- Mailbox timeout, IDC destination function enums, firmware/PHY version structures, port config structures, mailbox command/data structures, and NIC mailbox register locations.
- MPI core dump global/segment headers and segment numbering for mailbox/control/XGMAC/MAC protocol regions.

Flash and firmware layout support includes:
- Flash register flags and SPI commands.
- Flash chip info and flash description table.
- Manufacturer/device IDs and flash type flags.
- PCI option ROM header/data structures.
- Flash layout table data structure (`QFLT`) and image layout table (`QFIM`) structures.
- Image entry, timestamp, description header, flash layout table header/entry/container, and NIC configuration table with factory/CLP MAC and VLAN data.

## Endianness and ABI Notes

The file provides conditional endian-conversion macros for little-endian and big-endian builds, backed by `ql_change_endian`. It also uses packed hardware structures and restores packing after IOCB definitions. The structure layouts are consumed directly by firmware, DMA rings, ioctl clients, and flash parsers, so sizes and field ordering are part of the hardware/driver ABI.

## Integration Notes

`qlge_hw.h` is included by `qlge.h` and provides most of the constants referenced by initialization, interrupt, flash, MPI, ioctl, TX/RX, and GLD code. It intentionally mixes register maps, firmware mailbox data, ioctl payloads, and flash metadata because those surfaces all describe the same adapter hardware contract.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlge/qlge_hw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlge/qlge_open.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlge/qlge_open.h

## Role

`qlge_open.h` provides build-time defaults for the illumos `qlge` Ethernet driver.

## Definitions

The file conditionally defines:
- `VERSIONSTR` as `100721-v1.07`.
- `QL_DEBUG` as `0x0`.
- `__func__` as `"qlge"` if the compiler/environment has not defined `__func__`.

## Integration Notes

The values are guarded with `#ifndef`, allowing build-time overrides. The file has no structs or function prototypes and is included by `qlge.h`.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlge/qlge_open.h -->