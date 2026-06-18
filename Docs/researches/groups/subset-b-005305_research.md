# subset-b-005305 grouped research

Grouped research for Broadcom MPI3 `mpi3mr` protocol headers, private driver state, application BSG/ioctl handling, diagnostic-buffer support, and debug helpers. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_ioc.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_ioc.h

Purpose: defines the MPI 3.x IOC-management wire ABI used by the `mpi3mr` driver for controller bring-up, facts discovery, operational queue creation/deletion, event notification/acknowledgment, persistent event log access, component image download/upload, and IO Unit control operations. It is a layout contract between host memory and Broadcom MPI3 firmware, not executable logic.

Important APIs/types/functions: central request/reply layouts include `struct mpi3_ioc_init_request`, `struct mpi3_ioc_facts_request`, `struct mpi3_ioc_facts_data`, `struct mpi3_mgmt_passthrough_request`, request/reply queue management structs, `struct mpi3_port_enable_request`, `struct mpi3_event_notification_request`, `struct mpi3_event_notification_reply`, `struct mpi3_event_ack_request`, the many `struct mpi3_event_data_*` payloads, PEL structs such as `struct mpi3_pel_seq`, `struct mpi3_pel_entry`, `struct mpi3_pel_request`, action-specific PEL request structs, `struct mpi3_pel_reply`, component image `struct mpi3_ci_download_request`/reply and upload request, and `struct mpi3_iounit_control_request`/reply. The defines encode IOC init message flags, who-initialized values, driver capabilities, IOC facts capability/exception/protocol/personality bits, event IDs, event reason/status values, PEL classes/locales/actions/status, component-image flags/actions, and IO Unit control opcodes plus parameter index conventions.

Control flow: this header describes messages consumed by code in the firmware and driver modules. Typical flow is IOC facts request to populate driver capabilities, IOC init to provide reply-free and sense-buffer queues plus driver information, queue create/delete messages for operational queues, port enable, event notification subscription, event replies followed by ack when requested, and optional PEL/component-image/IO Unit control commands through admin request posting. Variable-length SAS and PCIe topology event payloads use `__counted_by(num_entries)` arrays so event handlers must size-copy by firmware-provided entry counts.

State and persistence behavior: no state is stored here. The structures map persistent-in-controller state such as firmware version, facts, queue depths, device handles, topology status, PEL sequence numbers, component image activation status, and IO Unit control results into DMA-visible request/reply buffers. Host code must convert little-endian fields and copy selected facts into `struct mpi3mr_ioc_facts` and related driver state.

Dependencies and integration points: depends on common MPI transport definitions from `mpi30_transport.h` for version unions, SGEs, function codes, and default reply fields; image/version structs from `mpi30_image.h`; configuration structures such as driver pages from `mpi30_cnfg.h`; and the admin queue implementation in `mpi3mr_fw.c`/`mpi3mr_app.c`. Event IDs feed `mpi3mr_os_handle_events()`, `mpi3mr_app_save_logdata_th()`, HDB status changes, SAS/PCIe transport refresh, device add/remove, and reset paths. PEL structs are used by app BSG PEL enable/abort and sequence-number helpers.

Risks and test signals: layout, endian, and size drift are high risk because firmware consumes exact offsets. Event variable-length arrays need bounds validation by callers. IOC facts capability bits drive DMA mask, queue sizing, segmented diagnostic support, IO throttling, and protocol exposure, so bad interpretation can break initialization or device presentation. Test signals include compile-time structure size/offset coverage, IOC facts parsing across controllers with and without optional capabilities, event notification replay/ack flows, SAS and PCIe topology events with zero/multiple entries, PEL wait/abort/status paths, component image activation statuses, IO Unit control lookup/remove/timestamp operations, and error paths for non-success `ioc_status`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_ioc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_pci.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_pci.h

Purpose: supplies small MPI3 PCIe/NVMe constants used by NVMe encapsulated passthrough commands.

Important APIs/types/functions: defines `MPI3_NVME_ENCAP_CMD_MAX` when not already supplied and bit masks/values for `MPI3_NVME_FLAGS_FORCE_ADMIN_ERR_REPLY_*` and `MPI3_NVME_FLAGS_SUBMISSIONQ_*`. These distinguish IO versus Admin submission queue behavior and whether admin error replies are forced for fail-only or all cases.

Control flow: there is no executable flow. The flags are consumed when constructing or interpreting MPI3 NVMe encapsulated command messages, particularly BSG passthrough code that inspects NVMe command data format and builds PRP or SGL lists.

State and persistence behavior: no state or persistence. The constants are ABI values placed in request flags passed to firmware.

Dependencies and integration points: included by `mpi3mr.h` with the other MPI headers. It complements NVMe encapsulated request structures from `mpi30_init.h`/transport definitions and the PRP/SGL construction paths in `mpi3mr_app.c`.

Risks and test signals: risk is mostly semantic drift against firmware specifications. Tests should cover NVMe BSG passthrough for admin and IO queue commands, forced admin error reply behavior, and compile coverage where `MPI3_NVME_ENCAP_CMD_MAX` may already be defined by another included header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_sas.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_sas.h

Purpose: defines SAS device-information bit fields and the MPI3 SMP passthrough request/reply ABI.

Important APIs/types/functions: `MPI3_SAS_DEVICE_INFO_*` marks SSP/STP/SMP target and initiator capabilities plus the masked device type values for no device, end device, and expander. `struct mpi3_smp_passthrough_request` carries host tag, function, change count, IO unit port, destination SAS address, request SGE, and response SGE. `struct mpi3_smp_passthrough_reply` returns IOC status/log info and response data length.

Control flow: no direct code runs here. Transport and BSG paths populate the passthrough request, attach request/response buffers, post it through the admin queue, and interpret the reply. The app SGL builder has a special SMP passthrough branch that allows at most two SGEs and requires each SMP data buffer to fit within one ioctl SGE.

State and persistence behavior: no persistent state. SAS capability bits are copied from firmware config pages or event payloads into `mpi3mr` target/SAS transport objects; SMP request state lives only for the duration of a posted admin command.

Dependencies and integration points: relies on `struct mpi3_sge_common` from `mpi30_transport.h`. Used by `mpi3mr_transport.c` for SAS expander/phy management and by `mpi3mr_app.c` for user-space SMP passthrough via BSG. SAS device-info constants are also used when classifying target devices and expanders.

Risks and test signals: incorrect device-info interpretation can misclassify expanders, SATA/STP targets, or initiators and break transport topology. SMP passthrough risks include wrong SAS address, oversized buffers, or response truncation. Tests should cover SMP passthrough success/failure IOC statuses, max-size boundary checks, SAS topology refresh with end devices and expanders, and device-info bit combinations seen in firmware pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_sas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_tool.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_tool.h

Purpose: declares the MPI3 diagnostic buffer post/manage protocol used to hand host diagnostic buffers to firmware and later release, pause, resume, or clear them.

Important APIs/types/functions: defines diagnostic buffer types `MPI3_DIAG_BUFFER_TYPE_TRACE` and `MPI3_DIAG_BUFFER_TYPE_FW`, management actions `MPI3_DIAG_BUFFER_ACTION_RELEASE`, `PAUSE`, `RESUME`, and `CLEAR`, the segmented-post message flag, `struct mpi3_diag_buffer_post_request`, and `struct mpi3_diag_buffer_manage_request`.

Control flow: `mpi3mr_app.c` allocates trace/FW host diagnostic buffers, fills a post request with buffer type, DMA address, length, and segmented flag, then waits for admin completion. Release uses the manage request with release action and updates local HDB status based on completion or diagnostic-buffer status-change events.

State and persistence behavior: this header stores no state. The protocol mutates firmware ownership of host diagnostic buffers; local status is tracked in `struct diag_buffer_desc` as not allocated, posted/unpaused, posted/paused, or released. Buffer contents persist in host memory until uploaded by BSG or freed during cleanup.

Dependencies and integration points: included by `mpi3mr.h`; uses MPI transport function IDs `MPI3_FUNCTION_DIAG_BUFFER_POST` and `MPI3_FUNCTION_DIAG_BUFFER_MANAGE` from `mpi30_transport.h`. Tied to IOC facts diagnostic size/capability fields, Driver Page 1 sizing, Driver Page 2 trigger policy, HDB BSG commands, and firmware event `MPI3_EVENT_DIAGNOSTIC_BUFFER_STATUS_CHANGE`.

Risks and test signals: main risks are DMA address/length endian mistakes, segmented trace buffer list handling, posting buffers larger than controller limits, and stale local status after firmware releases/pauses a buffer. Tests should cover contiguous and segmented trace posting, FW buffer posting, release timeout/reset handling, BSG query/upload/repost, and status-change event reasons released/paused/resumed/cleared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_tool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_transport.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_transport.h

Purpose: defines the base MPI3 transport ABI: version, system interface register layout, register offsets/masks, reply descriptors, SGE formats, request/reply headers, function codes, IOC statuses, and IOC log-info encodings.

Important APIs/types/functions: `struct mpi3_sysif_registers` models the MMIO system interface including IOC information/config/status, admin queue addresses/indexes, operational queue indexes, write-sequence, host diagnostic, fault, HCB, reply/sense free indexes, diagnostic read/write, scratchpad, and device-assigned registers. Reply descriptor types include default, address, success, target command buffer, and status descriptors plus `union mpi3_reply_descriptors_union`. SGE layouts include simple/chain/last-chain/bit-bucket and extended EEDP entries. `struct mpi3_request_header` and `struct mpi3_default_reply` are the common message prefix/reply. Function and status defines cover initialization, config, SCSI, task management, SMP, NVMe, target-mode, queue management, toolbox, diagnostic buffer functions, product-specific functions, and detailed IOC status codes.

Control flow: firmware bring-up uses register writes for write-sequence unlock, IOC config enable/shutdown, host diagnostic reset actions, admin queue setup, and producer/consumer index updates. Runtime completion flow polls or interrupts on reply descriptors, uses descriptor phase/type bits to decide whether to fetch a reply frame or synthesize success/status, then advances consumer indexes. Request builders attach SGEs and use function codes/status values from this header for admin and operational queue messages.

State and persistence behavior: the header itself is stateless, but it describes mutable hardware-visible state in BAR registers and DMA rings. Queue producer/consumer indexes, phase bits, fault status/info, diagnostic read/write state, HCB configuration, reply-free/sense-free host indexes, and device-assigned registers all reflect controller runtime state. Host memory structures using these layouts persist until driver cleanup or reset.

Dependencies and integration points: foundational for all `mpi3mr` sources. `mpi3mr_fw.c` uses sysif registers, queue indexes, reply descriptors, and statuses; `mpi3mr_os.c` uses function/status values for SCSI IO; `mpi3mr_app.c` uses SGEs, headers, function codes, status reply descriptors, and EEDP/NVMe SGE modifier data; `mpi3mr.h` embeds the sysif pointer and cached facts derived from this ABI.

Risks and test signals: MMIO offset or mask errors can prevent initialization, reset, or interrupt processing. Reply descriptor phase handling and queue index updates are race-sensitive. SGE flags must correctly mark end-of-buffer/list and chain entries, especially in BSG passthrough. Tests should include controller initialization, admin and operational queue wraparound, interrupt coalescing, fault/reset paths, diagnostic read/write, reply descriptor type handling, SGE chain construction, EEDP protection information, and all relevant IOC status-to-error mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_transport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi3mr.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi3mr.h

Purpose: is the private driver-wide contract for the Linux Broadcom MPI3 storage controller driver. It collects kernel/SCSI/PCI includes, MPI protocol headers, version and resource constants, driver-private state structures, inline lifetime helpers, and cross-file function prototypes.

Important APIs/types/functions: major types include `struct mpi3mr_ioc_facts`, `struct op_req_qinfo`, `struct op_reply_qinfo`, `struct mpi3mr_intr_info`, `struct mpi3mr_throttle_group_info`, SAS transport objects (`mpi3mr_hba_port`, `mpi3mr_sas_port`, `mpi3mr_sas_phy`, `mpi3mr_sas_node`, `mpi3mr_enclosure_node`), target objects (`mpi3mr_tgt_dev`, `mpi3mr_stgt_priv_data`, `mpi3mr_sdev_priv_data`), `struct mpi3mr_drv_cmd`, diagnostic/trigger structs, DMA/chain descriptors, `struct scmd_priv`, the central `struct mpi3mr_ioc`, firmware event and delayed command nodes. Inline helpers manage target-device krefs. Prototypes expose initialization, resource management, queue posting, reply handling, reset/watchdog, event ack, SCSI task management, BSG registration, PEL helpers, config page reads/writes, SAS transport updates, diagnostic buffer operations, and HDB triggers.

Control flow: all modules share `struct mpi3mr_ioc` as the per-controller anchor stored in `Scsi_Host` private data. Probe/setup code fills PCI, sysif, DMA, queue, interrupt, facts, and command-tracker fields; runtime IO posts operational requests and consumes reply queues; admin commands use `mpi3mr_drv_cmd` trackers with mutex/completion/callback state; firmware events are queued as `mpi3mr_fwevt`; reset and watchdog paths coordinate through flags, mutexes, wait queues, and command flushing; app/BSG paths use ioctl DMA SGEs, BSG command trackers, PEL state, and diagnostic buffers; SAS transport paths maintain target, expander, HBA port, enclosure, and rphy lists.

State and persistence behavior: state is in memory per controller and per target. Persistent runtime state includes queue producer/consumer indexes, DMA pools/buffers, target device lists and reference counts, bitmaps for chain buffers/device removals/event acks, event queues, reset flags, cached IOC facts, topology change count, PEL sequence memory, logdata ring buffer, diagnostic buffer descriptors and trigger config, SAS transport lists, and IO throttling counters. Hardware/firmware state is mirrored in cached facts, device handles, diagnostic buffer posting state, and transport topology; no disk persistence is owned by this header.

Dependencies and integration points: integrates Linux block-mq, SCSI midlayer, PCI/AER, DMA pools, workqueues, SAS transport, BSG UAPI, and all MPI protocol headers. It is consumed by `mpi3mr_fw.c`, `mpi3mr_os.c`, `mpi3mr_app.c`, and `mpi3mr_transport.c`. External integration points are SCSI host/device attributes, BSG control nodes, SAS transport templates, PCI probe/error recovery, and firmware admin/operational queues.

Risks and test signals: high risk areas are shared mutable `mpi3mr_ioc` fields touched by ISR, workqueue, reset, BSG, sysfs, and SCSI IO paths; command tracker state bits; target-device kref/list lifetime; queue-full prevention; reset/unrecoverable/block flags; PRP/SGE DMA buffers; and diagnostic trigger flags. Tests should cover probe/remove/reinit, reset races with BSG and IO, target add/remove, SAS refresh, queue wraparound, command timeouts, PEL enable/abort, HDB trigger/repost/upload, sysfs reads/writes, PCI error recovery, and lockdep/KASAN/KCSAN coverage for list and kref lifetimes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi3mr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi3mr_app.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi3mr_app.c

Purpose: implements the driver application/control surface: host diagnostic buffer allocation/post/release/trigger handling, BSG driver commands, MPI passthrough commands, NVMe PRP/SGL construction, user buffer DMA staging, logdata caching, BSG device registration, and host/SCSI-device sysfs attributes.

Important APIs/types/functions: exported functions include `mpi3mr_alloc_diag_bufs()`, `mpi3mr_issue_diag_buf_post()`, `mpi3mr_post_diag_bufs()`, `mpi3mr_issue_diag_buf_release()`, `mpi3mr_release_diag_bufs()`, `mpi3mr_set_trigger_data_in_hdb()`, `mpi3mr_set_trigger_data_in_all_hdb()`, `mpi3mr_hdbstatuschg_evt_th()`, `mpi3mr_diag_buffer_for_type()`, trigger handlers `mpi3mr_global_trigger()`, `mpi3mr_scsisense_trigger()`, `mpi3mr_event_trigger()`, `mpi3mr_reply_trigger()`, `mpi3mr_refresh_trigger()`, `mpi3mr_app_save_logdata_th()`, and BSG lifecycle `mpi3mr_bsg_init()`/`mpi3mr_bsg_exit()`. Important internal functions include `mpi3mr_alloc_trace_buffer()`, `mpi3mr_process_trigger()`, `mpi3mr_bsg_pel_abort()`, `mpi3mr_bsg_process_drv_cmds()`, `mpi3mr_bsg_build_sgl()`, `mpi3mr_build_nvme_sgl()`, `mpi3mr_build_nvme_prp()`, `mpi3mr_map_data_buffer_dma()`, `mpi3mr_bsg_process_mpt_cmds()`, and sysfs show/store handlers.

Control flow: diagnostic setup reads Driver Page 1 for preferred HDB sizes, falls back to defaults, allocates trace/FW buffers with decrement retries, and posts them through admin commands. Trigger refresh reads Driver Page 2, caches trigger elements, and sets quick-present booleans. Reply/event/SCSI-sense/global trigger paths take `trigger_lock`, match configured trigger conditions, set release-active flags, and queue HDB trigger events. Driver BSG commands verify adapter IDs, serialize on `bsg_cmds.mutex`, and dispatch adapter info/reset, all-target info, change count, logdata enable/get, PEL enable, HDB query/repost/upload/refresh. MPI passthrough BSG validates buffer-entry ordering and sizes, stages request/reply/data buffers, maps data into preallocated ioctl DMA SGEs, builds MPI SGEs or NVMe PRP/SGLs, posts an admin request, waits for completion, copies replies/sense/data back, and issues target or controller reset on timeout.

State and persistence behavior: mutable state is in `mrioc`: diagnostic descriptors and trace segment pools, Driver Page 2 trigger cache, HDB trigger active flags, PEL enable/class/locale/abort state, BSG command tracker, preallocated ioctl SGEs/chain/response buffers, temporary PRP list allocation, target block counters for task-management passthrough, circular logdata buffer and index, sysfs `logging_level`, and SATA NCQ priority enable in per-device private data. Buffer contents and logdata remain in host memory until uploaded, overwritten, freed, or reposted; there is no disk persistence.

Dependencies and integration points: depends on the Linux BSG library, SCSI BSG UAPI `scsi_bsg_mpi3mr.h`, admin queue posting, config page helpers for driver pages, reset handling, target lookup/refcount helpers, task management, SAS ATA NCQ helpers, sysfs attribute groups, MPI diagnostic/PEL/NVMe/SMP/SGL protocols, event counter signaling, and firmware event worker trigger queuing.

Risks and test signals: highest risks are user-controlled BSG buffer parsing, size/offset arithmetic, DMA descriptor exhaustion, PRP page alignment, SGE modifier collisions, command timeout/reset races, lock ordering around `bsg_cmds.mutex` and trigger spinlock, target kref lifetime, and HDB status transitions. Test signals include invalid BSG layouts, boundary transfer sizes, SMP single-SGE constraints, NVMe PRP and SGL formats, admin command timeout paths, reset during BSG, unrecoverable/block-on-PCI cases, PEL enable escalation/abort, HDB upload offset bounds, segmented trace allocation rollback, sysfs `logging_level` and NCQ priority writes, and sanitizers for DMA/list/lifetime errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi3mr_app.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi3mr_debug.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi3mr_debug.h

Purpose: provides driver logging level bits, unconditional controller-prefixed log macros, conditional debug-category macros, and inline helpers to dump message frames or arbitrary buffers as little-endian dwords.

Important APIs/types/functions: debug masks include event top/bottom half, init, exit, task management, reset, SCSI error/info, reply, config error/info, transport error/info, BSG error/info, generic debug, and SGE debug. Logging macros include `ioc_err`, `ioc_notice`, `ioc_warn`, `ioc_info`, category-specific `dprint_*` macros, `dprint_scsi_command()`, `dprint_dump()`, and `dprint_dump_req()`.

Control flow: normal macros format through `pr_*` with `ioc->name`. Conditional macros check `ioc->logging_level` bitmasks before printing. Dump helpers iterate over 32-bit little-endian words and print eight words per line.

State and persistence behavior: no persistent state is defined here. Runtime behavior depends on each controller's `mrioc->logging_level`, which is exposed through a writable sysfs attribute in `mpi3mr_app.c`. Log output goes to the kernel log.

Dependencies and integration points: included by `mpi3mr.h` and used throughout firmware, OS, app, config, transport, reset, and SCSI paths. `dprint_dump()` is used by BSG timeout/debug paths to show admin frames and management payloads.

Risks and test signals: risks include log flooding when verbose bits are enabled, leaking command payload contents into kernel logs, and dereferencing an invalid `ioc` in macros. Dump helpers assume dword-sized buffers and do not validate alignment beyond casting. Tests should cover compile-time macro use across modules, sysfs logging-level changes, dynamic debug scenarios for BSG timeouts, and avoiding dumps of uninitialized memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi3mr_debug.h -->
