# Group Research: group_579_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__c4f3eae20a57

Scope confirmed against `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_dump.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_dump.h

Purpose: Defines the Emulex driver dump-file vocabulary: in-memory file buffers, dump event context, dump file sizes, dump types, segment identifiers, human-readable legends, dump regions, and dump table entry layouts.

Key definitions:
- `emlxs_file_t`: simple buffered file abstraction with `buffer`, current `ptr`, and `size`.
- `dump_temp_event_t`: links an HBA, temperature event type, and temperature value.
- File sizes: `EMLXS_TXT_FILE_SIZE`, `EMLXS_DMP_FILE_SIZE`, `EMLXS_CEE_FILE_SIZE`.
- Dump initiators: `DUMP_TYPE_USER`, `DUMP_TYPE_DRIVER`, `DUMP_TYPE_TEMP`.
- Dump output IDs: `DUMP_TXT_FILE`, `DUMP_DMP_FILE`, `DUMP_CEE_FILE`.
- Segment IDs cover firmware/HBA dump sections, SLI structures, PCI config, mailboxes, rings, buffer lists, revision info, HBA info, driver parameters, Solaris internal structures, config regions, CEE log, and non-volatile log.
- Legend strings map those segment IDs and subregions to printable labels.
- `DUMP_WAKE_UP_PARAMS` gives a display-oriented simplified wakeup parameter structure.
- `DUMP_TABLE_ENTRY_PORT_STRUCT`, `DUMP_TABLE_ENTRY_PORT_BLK`, and `DUMP_TABLE_ENTRY` model firmware dump-table entries with endian-sensitive bitfields.

Dependencies and interactions:
- Uses `struct emlxs_hba`, `DRIVER_NAME`, and `EMLXS_LITTLE_ENDIAN`.
- Extern prototypes for the dump implementation are in `emlxs_extern.h` under `DUMP_SUPPORT`.
- Dump state and per-HBA dump files are embedded in `emlxs_hba_t` in `emlxs_fc.h`.

Implementation notes:
- This is declarative only; it has no executable functions.
- The endian-sensitive table-entry bitfields are ABI-sensitive and must match firmware dump-table encoding.
- `CC_DUMP_USE_ALL_TABLES`, `CC_DUMP_FW_BUG_1`, and `CC_DUMP_ENABLE_PAD` are compile-time diagnostic/workaround switches.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_dump.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_events.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_events.h

Purpose: Declares the driver event types, event descriptors, and queue/list structures used for DFC/HBA/SAN diagnostic event delivery.

Key definitions:
- `emlxs_event_t`: event descriptor containing mask bit, label, timeout, and destroy callback.
- `DEFINE_EVT(...)`: dual-use macro that either defines or declares event globals depending on `DEF_EVENT_STRUCT`.
- Event masks include link, RSCN, CT, multipulse, dump, temperature, virtual-port RSCN, async, FCoE, and optional SAN diagnostic classes.
- Predefined event descriptors include `emlxs_link_event`, `emlxs_rscn_event`, `emlxs_ct_event`, `emlxs_dump_event`, `emlxs_temp_event`, `emlxs_fcoe_event`, and `emlxs_async_event`.
- `emlxs_event_entry_t`: doubly linked event queue element with ID, timestamp, timer, event type, port pointer, context buffer, size, and completion flags.
- `emlxs_event_queue_t`: protected queue with mutex, condition variable, per-event `last_id`, global `next_id`, count, and first/last pointers.

Dependencies and interactions:
- Requires `kmutex_t`, `kcondvar_t`, and the driver event implementation.
- `emlxs_extern.h` declares event queue creation/destruction, event logging, DFC event retrieval, and SAN diagnostic event routines.
- `emlxs_hba_t` owns `event_queue`, event masks, timers, and DFC/HBA event state.

Implementation notes:
- `EVT_TIMEOUT_DEFAULT` is 60, `EVT_TIMEOUT_NEVER` is 0, and the default destroy callback is `emlxs_null_func`.
- CT events have a custom destroy hook, `emlxs_ct_event_destroy`, reflecting payload ownership needs.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_events.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_extern.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_extern.h

Purpose: Central external declaration hub for the `emlxs` driver. It exposes global driver state, device/DMA attributes, configuration tables, firmware/model tables, SLI APIs, and cross-module function prototypes.

Key declarations:
- Driver globals: `emlxs_soft_state`, `emlxs_instance`, `emlxs_instance_count`, revision/version/name/label strings, and `emlxs_device`.
- DDI/DMA globals: access attributes and DMA attribute variants.
- Message/logging APIs: message formatting, log create/destroy/reinit/get.
- Event APIs: event queue lifecycle, link/RSCN/CT/dump/temp/FCoE/async logging, DFC event retrieval, optional SAN diagnostic event logging.
- Solaris FCA integration: link up/down callbacks, ULP callbacks, packet init/uninit/transport/abort, unsolicited buffer handling, reset and port management.
- Utility APIs: WWN formatting/compare, command translators, byte swapping, mode translation, power-management helpers, VPD/FCode parsing.
- Optional feature sections: `DHCHAP_SUPPORT`, `MENLO_SUPPORT`, `FMA_SUPPORT`, `MODFW_SUPPORT`, `MSI_SUPPORT`, `SFCT_SUPPORT`, `DUMP_SUPPORT`.
- Mailbox APIs: SLI2/3/4 mailbox construction, queue create commands, FCF/VFI registration, FCF table reads, async event handling, completion and retry helpers.
- Memory APIs: pool creation/destruction/get/put, buffer allocation, HBQ allocation, virtual-address lookup.
- HBA and SLI APIs: adapter init, firmware decode/show/load/unload, interrupt setup, SLI3/SLI4 object mapping and reset helpers.
- FCP path APIs: packet registration, abort/close IOCB creation, chip/transmit queue operations, link/online/offline transitions, buffer posting.
- Thread/task APIs: taskq lifecycle, worker thread lifecycle, thread triggers, spawn thread management.
- DFC, dump, FCT, FCF, VPI, and RPI notification APIs.

Dependencies and interactions:
- This file assumes all core driver types have already been declared: `emlxs_hba_t`, `emlxs_port_t`, `MAILBOXQ`, `IOCBQ`, `CHANNEL`, `NODELIST`, `MATCHMAP`, `FCFIobj_t`, `VFIobj_t`, `XRIobj_t`, `RPIobj_t`, and others.
- It is the cross-module compile contract for implementation files such as `emlxs_msg.c`, `emlxs_event.c`, `emlxs_solaris.c`, `emlxs_pkt.c`, `emlxs_mbox.c`, `emlxs_mem.c`, `emlxs_hba.c`, `emlxs_sli3.c`, `emlxs_sli4.c`, `emlxs_diag.c`, `emlxs_download.c`, `emlxs_fcp.c`, `emlxs_thread.c`, `emlxs_dfc.c`, `emlxs_dump.c`, and `emlxs_fcf.c`.

Implementation notes:
- This header is declarations only, but it strongly documents driver modular boundaries.
- Several feature areas are compile-time optional, so call sites must honor matching feature guards.
- It includes duplicate declarations for `emlxs_instance` and `emlxs_instance_count`; changing that would be cleanup, not behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_fc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_fc.h

Purpose: Defines the core in-kernel driver data model for Emulex Fibre Channel adapters: packets, nodes, ports, channels, rings, memory pools, SLI3/SLI4 runtime state, HBA state, locking aliases, register access helpers, interrupt dispatch selection, and endian swap helpers.

Key definitions:
- `emlxs_buf_t`: per-I/O packet wrapper linking `fc_packet_t`, port, node, channel, IOCB, XRI, timeouts, abort state, LUN, DID, packet flags, and optional FCT/SAN diagnostic state.
- Packet flags model queue residency, completion state, timeout/flush/abort, swapped payloads, response validity, allocation, and stale/valid state.
- `emlxs_vpd_t`: persistent adapter/VPD identity and firmware version data.
- `emlxs_queue_t`: generic first/last/count/max queue structure.
- `emlxs_buf_info_t` / `MBUF_INFO`: allocation/DMA mapping descriptor.
- `emlxs_channel_t`: abstraction for SLI3 rings or SLI4 WQ/CQ I/O paths with response deferral, locks, timeout, and counters.
- `emlxs_ring_t`: SLI2/3 command/response ring state.
- `emlxs_node_t` / `NODELIST`: discovered remote node state, WWNs, DID, RPI/XRI, service parameters, per-channel transmit queues, optional DH-CHAP/SAN diagnostic/throttle state.
- `emlxs_memseg_t`: memory pool segment descriptor with high/low-water and dynamic growth metadata.
- `emlxs_stats_t`: broad HBA statistics for link, mailbox, IOCB, FCP, ELS, CT, IP, unsolicited buffers, resets, and optional FCT.
- Optional target-mode support defines FCT states, counters, and efficient power-of-two bucket macros for target I/O size statistics.
- `emlxs_port_t`: per-physical/virtual port state, VPI object, mode flags, WWNs, service parameters, D_IDs, ALPA data, node table, packet polling locks, ULP callbacks, unsolicited buffers, optional FCT and SAN diagnostic state.
- SLI access macros map SLI3 CSR/SLIM and SLI4 BAR registers through DDI accessors.
- `emlxs_sli3_t`: SLI3 SLIM/HBQ/register/ring/BPL state.
- `emlxs_sli4_t`: SLI4 BARs, doorbells, extents, FCF/VFI/RPI/XRI tables, queues, dump region, SLI parameters, and port identity.
- `emlxs_sli_api_t`: function-pointer table abstracting SLI3 vs SLI4 operations.
- `emlxs_hba_t`: top-level adapter object covering PCI identity, DMA attributes, VPD, link state, memory pools, service parameters, adapter state/flags, SLI union, I/O completion, channels, iotags, mailbox, interrupts, timers, GPIO, power management, ioctl, events, config, kstats, logging, ports, optional DH-CHAP/firmware/dump state, and reset state.

Dependencies and interactions:
- Includes `emlxs_fcf.h`, so FCF/VFI/VPI/RPI/XRI state is embedded into the port/HBA model.
- Uses illumos kernel primitives, Leadville FCA types, COMSTAR FCT types under `SFCT_SUPPORT`, and many hardware protocol types from `emlxs_hw.h`.
- Extern function prototypes that operate on these structures are in `emlxs_extern.h`.

Implementation notes:
- Lock alias macros such as `EMLXS_PORT_LOCK`, `EMLXS_MBOX_LOCK`, `EMLXS_TX_CHANNEL_LOCK`, and `EMLXS_FCF_LOCK` encode locking conventions for implementation files.
- `EMLXS_STATE_CHANGE` and `_LOCKED` update adapter state and set hardware-error flags on `FC_ERROR`.
- `MODSYM_SUPPORT` optionally routes Leadville/COMSTAR calls through dynamically resolved function pointers.
- Endian macros provide unconditional swaps and conditional LE/BE swaps; note the `LE_SWAP24_*` definitions reference `X` before being overridden for one modrev case.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_fc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_fcf.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_fcf.h

Purpose: Defines the SLI4/FCoE fabric-control object model and state machines for FCF tables, FCFI, VFI, VPI, RPI, and XRI resources.

Key definitions:
- Limits: `FCFTAB_MAX_FCFI_COUNT` and `FCFI_MAX_VFI_COUNT` are both 1 in this driver.
- Event IDs distinguish internal state entry, external fabric events, table online/offline, and FCFI/VFI/VPI/RPI online/offline/pause/resume events.
- Reason codes record why state transitions happen, including event/requested/no mailbox/no buffer/send failure/mailbox failure/no resource/not allowed/invalid.
- `XRIobj_t`: exchange resource with free-list links, XRI, state, SGL, segment, RPI bindings, owning packet, RX ID, flags, and exchange type.
- `emlxs_deferred_cmpl_t`: stores deferred completion context for port/node and three opaque args.
- `RPIobj_t`: remote port identifier state machine with index/RPI, previous/current reason and state, flags, attempts, XRI count, idle timer, owning VPI, node DID/service parameters, and deferred completion.
- `VPIobj_t`: virtual port identifier state machine, fabric/p2p RPIs, bound port, parent VFI, counts of online/paused RPIs, and port-bind flags.
- `VFIobj_t`: virtual fabric instance state machine, service parameters, parent FCFI, online VPI/logi counts, and FLOGI VPI pointer.
- `FCFIobj_t`: FCF instance state with FCF index, VLAN, generation, event tag, validity/availability/configuration/selection flags, `FCF_RECORD_t`, priority, and VFI count.
- `VFTable_t`: VFI table state and active/count/table pointer.
- `FCFTable_t`: top-level fabric table state, with separate FCoE and FC state values, request flags, online FCFIs, table pointers/counts, and timers.

Dependencies and interactions:
- Used directly inside `emlxs_sli4_t` and `emlxs_port_t` from `emlxs_fc.h`.
- `emlxs_extern.h` declares the notification and helper functions that drive these state machines.
- Depends on `MATCHMAP`, `SERV_PARM`, `emlxs_buf_t`, `emlxs_port`, `emlxs_node`, and `FCF_RECORD_t`.

Implementation notes:
- The file is declarative and state-machine oriented.
- Object flags encode both request state and derived state; implementation must keep counters and flags synchronized across nested FCFI/VFI/VPI/RPI/XRI ownership.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_fcf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_fcio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_fcio.h

Purpose: Defines Emulex-specific FCIO diagnostic ioctl command IDs, driver-specific error codes, parameter/VPD/PHY/throttle/log structures, and queue-stat reporting structures.

Key definitions:
- `FCIO_REV` is 2.
- Diagnostic ioctl namespace starts at `EMLXS_DIAG` and includes BIU/POST/ECHO diagnostics, parameter get/set/list, boot revision/download/state, CFL download, VPD, DFC command, DFC revision, PHY get, throttle get/set, and VPD v2.
- Special debug/test ioctls include BAR I/O, test code, hardware error test, and mailbox timeout test.
- Dump file IDs: TXT, DMP, CEE, FAT.
- Error codes range from `EMLXS_TEST_FAILED` through `EMLXS_REBOOT_REQUIRED`.
- `emlxs_parm_t`: user-visible driver parameter descriptor with label, min/max/default/current, flags, and help text.
- Parameter flags include dynamic, boolean, hex, dynamic reset-required, and dynamic link-reset-required.
- `emlxs_vpd_desc_t` and `_v2_t`: fixed-size VPD description formats; v2 expands fields to 256 bytes.
- `emlxs_phy_desc_t`, `emlxs_throttle_desc_t`, `emlxs_log_req_t`, `emlxs_log_resp_t`.
- FCIO queue descriptors model EQ/CQ/WQ/RQ host index, max index, queue IDs, linkage, physical/virtual addresses, interrupt vector, and statistics.
- `FCIO_Q_STAT_t`: aggregate queue statistics for all supported EQ/CQ/WQ/RQ objects plus timer and interrupt counts.

Dependencies and interactions:
- Used by ioctl/DFC paths and log retrieval declarations in `emlxs_extern.h`.
- Queue limits mirror SLI4 queue limits: 8 EQs, 4 WQs per EQ, 2 RQs, and CQs derived from WQ/RQ/MQ requirements.

Implementation notes:
- This header is a user/kernel ABI surface; structure sizes and command values are compatibility-sensitive.
- Virtual addresses are split into 32-bit `virt` and `virt_hi` fields for reporting.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_fcio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_fct.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_fct.h

Purpose: Provides conditional COMSTAR/FCT target-mode integration declarations and compatibility definitions for the Emulex driver.

Key definitions:
- Entire functional content is gated by `SFCT_SUPPORT`.
- Includes illumos kernel headers and COMSTAR headers `<sys/stmf.h>` and `<sys/fct.h>`.
- Undefines `FC_WELL_KNOWN_ADDR` before including FCT to avoid macro conflicts.
- Provides fallback definitions for newer link/port speeds if not already present: 8G, 10G, 16G, 32G.
- `EMLXS_FCT_NUM_ELS_ONLY` is 8, for ports that only send ELS commands and do not need valid command handles.
- Without `MODSYM_SUPPORT`, declares weak references for FCT/STMF entry points and `stmf_alloc`/`fct_alloc`.

Dependencies and interactions:
- `emlxs_fc.h` embeds extensive FCT state in `emlxs_buf_t`, `emlxs_port_t`, and target statistics under `SFCT_SUPPORT`.
- `emlxs_extern.h` declares target-mode implementation hooks under `SFCT_SUPPORT`.

Implementation notes:
- This header lets the same driver build with or without target-mode support.
- Weak symbols support optional linkage when dynamic symbol loading is not used.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_fct.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_fw.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_fw.h

Purpose: Defines firmware image identifiers, firmware descriptors, firmware module path, and optional static firmware table construction.

Key definitions:
- `EMLXS_FW_MODULE` resolves to `misc/<driver>/<driver>_fw`.
- `emlxs_fwid_t`: firmware IDs for LP10000, LP11000, LP11002, LPe11000, LPe11002, and LPe12000; `FW_NOT_PROVIDED` is zero.
- `emlxs_firmware_t`: firmware descriptor with ID, size, image pointer, label, kernel/stub/SLI1/SLI2/SLI3/SLI4 revision fields.
- `EMLXS_FW_TABLE_DEF` causes firmware-table definition in local memory.
- `EMLXS_FW_IMAGE_DEF` causes firmware images to be defined in the firmware table; it is forced when `MODFW_SUPPORT` is absent.
- Optional table includes adapter-specific firmware headers and builds `EMLXS_FW_TABLE`.

Dependencies and interactions:
- `emlxs_extern.h` declares firmware table globals and optional module firmware load/unload routines.
- `emlxs_fc.h` stores firmware module handle when `MODFW_SUPPORT` is enabled.
- Firmware download/parsing support is further described by firmware image structures in `emlxs_hw.h`.

Implementation notes:
- The table macro is compile-time data assembly, not executable logic.
- One LP11000 table initializer has a trailing comma after `sli4`, which is valid C initializer syntax.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_fw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_hbaapi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_hbaapi.h

Purpose: Carries the SNIA HBA API public header used by clients and libraries, with Emulex/RackTop-local copy adjustments for kernel/user builds.

Key definitions:
- `HBA_LIBVERSION` is 2.
- `HBA_API` handles Windows DLL import/export and is empty elsewhere.
- Platform typedefs define fixed HBA integer/pointer types for Windows and Unix/kernel use.
- `HBA_HANDLE`, `HBA_STATUS`, status constants, port type/state/speed constants, class-of-service type, FC-4 type bitmap, WWN, IP address, and boolean types.
- Adapter/port attribute structures: `HBA_ADAPTERATTRIBUTES`, `HBA_PORTATTRIBUTES`, `HBA_PORTSTATISTICS`.
- FCP mapping/binding structures: `HBA_SCSIID`, `HBA_FCPID`, `HBA_LUID`, `HBA_FCPSCSIENTRY`, V2 variants, target mapping, binding entries, and persistent binding structures.
- Management/event structures: WWN type, `HBA_MGMTINFO`, link/RSCN/proprietary event info, `HBA_EVENTINFO`, and optional userland `HBA_LIBRARYATTRIBUTES`.
- Binding capability/status/effective constants and FC-4 statistics.
- Event classes cover adapter, port, port-statistics, target, and fabric-link events.
- Function prototypes cover library load/free, adapter enumeration/open/close, adapter/port attributes, port statistics, discovered ports, CT passthrough, event buffers, RNID/RLS/RPL/RPS/SRL/LIRR, FC4/FCP statistics, refresh/reset, target mapping, persistent binding, SCSI inquiry/report LUNs/read capacity, callback registration/removal, and library attribute queries.

Dependencies and interactions:
- Used by driver/userland HBA management paths and DFC event structures referenced in `emlxs_events.h` and `emlxs_extern.h`.
- Guards `struct tm` and library attributes out of kernel builds with `_KERNEL`.

Implementation notes:
- This is an ABI/API header, so field widths and constants are compatibility-sensitive.
- Several comments preserve original SNIA naming and misspellings such as “Depricated” and “Persistant”.
- `HBA_ScsiInquiryV2` lacks `HBA_API` while adjacent exported prototypes include it; that may be intentional or legacy.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_hbaapi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_hw.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_hw.h

Purpose: Defines low-level Emulex adapter hardware, SLI, Fibre Channel, FCP/SCSI, ELS, CT, FDMI, buffer descriptor, DMA map, and firmware-image constants and structures.

Key definitions:
- Adapter capacity and ring constants: max vports, max transfer, ring counts, PCB size, SLI2/SLI3 IOCB sizes, SLIM sizes, command/ring assignments for FCP/FCT/IP/ELS/CT, retry and timeout defaults.
- Well-known D_ID values: FDMI, name server, SCR, fabric, broadcast, Menlo, and masks.
- FC frame R_CTL/type constants and command/response direction flags.
- CT structures: `CtRevisionId_t`, `CtCommandResponse_t`, `SliCtRequest_t`; CT service types, name-server subtype, accept/reject codes, reason/explanation codes, management-server and name-server command IDs, port types, and last-entry flag.
- PCI/SBUS register offsets and bit masks: BARs, command/status, capabilities, extended capabilities, configuration access, SBUS control/status/update, host/chip attention/status/control, BIU config.
- MSI maps/masks and interrupt mode definitions under `MSI_SUPPORT`.
- SLI4 register offsets and bit definitions: UE status/mask registers, EQ interrupt CSR registers, SLI status/control, physical-device control, POST/semaphore fields, BAR doorbells, MQ/CQ/EQ/WQ doorbell bit layouts, bootstrap mailbox constants.
- FCP/SCSI payloads: `FCP_RSP`, `FCP_CMND`, inquiry data, read capacity, SCSI status/response codes, CDB opcodes, and vendor-specific CDB values.
- Fibre Channel service parameter structures: rings, ring definitions, `NAME_TYPE`, common service parameters, class parameters, `SERV_PARM`, vendor version format, and endian-sensitive bitfields.
- ELS constants and payloads: command codes for LS_RJT, ACC, PLOGI/FLOGI/LOGO/PRLI/PRLO/ADISC/FARP/FAN/RSCN/SCR/RNID/AUTH and more; payload structs for LS_RJT, LOGO, PRLI, PRLO, ADISC, FARP, FAN, SCR, RNID, RRQ, D_ID, and aggregate `ELS_PKT`.
- Buffer/DMA descriptors: `ULP_BDE`, `ULP_BDE64`, `ULP_BPL64`, `ULP_BDL`, `ULP_SGE64`, `BE_PHYS_ADDR`, and `MATCHMAP`.
- FDMI/HBA management definitions: operation codes, subtype, reject code, HBA/port attribute types, attribute entries/blocks, port/HBA identifiers, registration payloads, and accept payloads.
- Firmware/download definitions: SRAM config constants, SLI firmware adapter type encodings, program type enum, firmware image/file descriptors, checksum/AIF/flash/load-list constants, object max transfer, BE2/BE3 UFI/flash directory structures, flash entry types, driver-level BE firmware file/image structures, and object firmware header.

Dependencies and interactions:
- Provides foundational hardware/protocol types consumed by `emlxs_fc.h`, `emlxs_fcf.h`, firmware download code, mailbox code, ELS/CT/FCP paths, and dump code.
- Requires endian macros (`EMLXS_BIG_ENDIAN`, `EMLXS_LITTLE_ENDIAN`) to choose protocol bitfield layout.
- References constants defined elsewhere, such as `MBOX_SIZE`, `MBOX_EXTENSION_SIZE`, `MBOX_EXTENSION_OFFSET`, and `RQ_DEPTH`.

Implementation notes:
- This file is declarative and ABI/protocol-layout heavy; bitfield ordering and structure sizes are hardware/protocol sensitive.
- Several variable-length payload structures are represented with single-element trailing arrays, a pre-C99 idiom used throughout this driver.
- It includes both older FireFly/SLI2/SLI3 register definitions and newer SLI4/BladeEngine firmware formats, showing support across adapter generations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_hw.h -->