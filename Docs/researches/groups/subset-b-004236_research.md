# subset-b-004236 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/mptsas.c -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/mptsas.c

## Purpose
`mptsas.c` is the SAS protocol driver for the legacy LSI Fusion MPT stack. It binds supported LSI SAS PCI devices, attaches a SCSI host with SAS transport support, discovers the SAS topology from MPT config pages, registers local phys/ports/rphys with the kernel SAS transport, and handles hotplug, integrated RAID, expander, link, queue-full, reset, and broadcast primitive firmware events.

This file is the SAS-specific layer above the generic `mptscsih.c` SCSI service layer. Normal I/O is delegated to `mptscsih_qcmd()` and `mptscsih_io_done()`, while this file owns SAS topology, target allocation, hotplug decisions, and SAS management passthrough commands.

## Important APIs, types, and functions
- Module parameters: `mpt_pt_clear`, `max_lun`, and `mpt_loadtime_max_sectors` tune persistent table clearing, reported LUN capacity, and block size limits.
- MPT callback contexts: `mptsasDoneCtx`, `mptsasTaskCtx`, `mptsasInternalCtx`, `mptsasMgmtCtx`, and `mptsasDeviceResetCtx` separate normal I/O, SCSI task management, internal scan/DV commands, SAS management commands, and SAS device-removal target resets.
- `mptsas_driver_template` is the SCSI host template. It wires queueing to `mptsas_qcmd`, target/device setup to `mptsas_target_alloc`, `mptsas_sdev_init`, `mptsas_sdev_configure`, and teardown to `mptsas_target_destroy` plus `mptscsih_sdev_destroy`.
- `mptsas_transport_functions` exports SAS transport operations: link error reads, enclosure/bay identifiers, local phy reset, and SMP passthrough.
- Config-page readers include `mptsas_sas_io_unit_pg0/pg1`, `mptsas_sas_phy_pg0`, `mptsas_sas_device_pg0`, `mptsas_sas_expander_pg0/pg1`, and `mptsas_sas_enclosure_pg0`.
- Topology helpers include `mptsas_probe_hba_phys`, `mptsas_probe_expanders`, `mptsas_probe_devices`, `mptsas_scan_sas_topology`, `mptsas_setup_wide_ports`, `mptsas_probe_one_phy`, `mptsas_add_end_device`, `mptsas_del_end_device`, and expander add/delete/refresh helpers.
- Event handling is split between interrupt-context routing in `mptsas_event_process()` and process-context work in `mptsas_firmware_event_work()`, which dispatches to SAS device, RAID, IR2, broadcast primitive, expander, link status, persistent-table, and queue-full handlers.
- Reset paths include `mptsas_target_reset_queue()`, `mptsas_target_reset()`, `mptsas_taskmgmt_complete()`, `mptsas_schedule_target_reset()`, and `mptsas_ioc_reset()`.

## Control flow
Module initialization calls `sas_attach_transport()`, registers MPT callbacks with `mpt_register()`, registers event/reset callbacks, then registers the PCI driver. Probe calls `mpt_attach()`, validates adapter readiness and initiator capability, allocates a `Scsi_Host`, initializes SAS topology/device-info lists and mutexes, allocates the `ScsiLookup` table, optionally clears persistent SAS mappings, calls `scsi_add_host()`, scans the SAS topology, and enables firmware event processing.

Initial topology discovery reads HBA IO Unit pages for local phys, reads phy and device pages for each local phy, forms narrow/wide ports by grouping phys with the same attached SAS address, creates SAS phy/port/rphy objects, walks expander pages by handle, refreshes expander phys, adds end devices, and finally reports active integrated RAID volumes on reserved channel `MPTSAS_RAID_CHANNEL`.

The normal I/O path is intentionally short: `mptsas_qcmd()` rejects deleted targets or discovery-quiesced hosts, optionally prints debug CDBs, and calls `mptscsih_qcmd()`. Completion and result translation are handled by `mptscsih.c`.

Firmware events are copied into `fw_event_work` objects and queued on `ioc->fw_event_q`. `mptsas_firmware_event_work()` handles rescan sentinel events (`event == -1`), ignores most events while `fw_events_off` is set, and otherwise dispatches to specialized handlers. Device and RAID events are normalized into `struct mptsas_hotplug_event` and processed by `mptsas_hotplug_work()`.

For `NOT_RESPONDING` device events, the driver does not immediately delete the target. It blocks I/O, marks the virtual target deleted, queues a target reset, and only queues the device-delete work after the target reset completion path decides the removal can proceed.

## State and persistence behavior
Persistent runtime state lives mostly in `MPT_ADAPTER` and `MPT_SCSI_HOST`: `sas_topology`, `hba_port_info`, `sas_device_info_list`, `fw_event_list`, `target_reset_list`, `sas_mgmt`, `taskmgmt_cmds`, discovery flags, missing-delay values, RAID page caches, and per-target `VirtTarget`/`VirtDevice` hostdata. The source file does not persist data to disk; persistence refers to adapter firmware SAS persistent mapping tables, which can be cleared through `mptbase_sas_persist_operation()`.

`sas_device_info_list` caches firmware mapping, OS mapping, SAS address, enclosure/slot metadata, logical-volume status, hidden RAID component status, and a cached-removed flag. This list is used to translate firmware events such as queue-full or RAID component changes into OS SCSI targets.

SAS topology objects are mirrored into kernel transport objects. `mptsas_portinfo` and `mptsas_phyinfo` are driver-owned, while `sas_phy`, `sas_port`, `sas_rphy`, and `scsi_target` are transport/midlayer-owned objects referenced from driver topology structs.

## Dependencies and integration points
The file depends on `mptbase.h` for adapter state, frame allocation, config-page access, reset/event registration, RAID page helpers, firmware persistent operations, and diagnostic/debug macros. It depends on `mptscsih.h` for generic SCSI command queueing, completion, task management, queue depth, host attributes, and lifecycle helpers.

Kernel integration points include PCI driver binding, SCSI host registration, SCSI target/device callbacks, SAS transport class registration, BSG SMP passthrough, DMA coherent allocation, workqueues, completions, spinlocks, mutexes, and kernel list APIs.

## Risks and edge cases
- Topology locking is subtle. Some helpers document that the SAS topology mutex must already be held, while others take it internally; nested calls during expander deletion and sibling walking need careful review for deadlock and list mutation safety.
- Several event paths mutate topology and SCSI transport objects from workqueue context while scans or resets can also manipulate the same state. Correctness depends on `fw_events_off`, `sas_topology_mutex`, `sas_device_info_mutex`, and target reset serialization all being used consistently.
- Some allocation failures are handled gracefully, but `BUG_ON()` is used in expander event allocation paths, which can panic the kernel on memory pressure.
- `mptsas_add_end_device()` can return nonfatal failure codes if rphy allocation/add fails; later refresh paths must be able to recover.
- The code supports old firmware discovery behavior, integrated RAID hidden component exposure, dual-port physical disk paths, and missing-device delay state. These branches are hard to cover without hardware or emulation.
- Queue-full handling depends on stale-but-cached firmware-to-OS mapping. Incorrect `sas_device_info_list` updates can reduce the wrong SCSI device queue depth.
- Timeout paths in SAS management and task-management commands may free message frames and trigger hard/soft resets; races with completion paths are high-risk.

## Test signals
- Build with `CONFIG_SCSI`, `CONFIG_SCSI_SAS_ATTRS`, Fusion MPT options, and optional `CONFIG_PM`/`CONFIG_FUSION_LOGGING` combinations.
- Probe/remove tests should verify `scsi_add_host()`, topology scan, SAS transport object creation, `sas_remove_host()`, event queue cleanup, and no leaked `mptsas_portinfo`/`mptsas_device_info` entries.
- Hardware or simulator tests should cover HBA-only devices, expanders, wide ports, link up/down, target removal with missing-delay, SAS discovery events, persistent table full, queue full, broadcast primitive, and IOC reset/rescan.
- Integrated RAID tests should cover volume create/delete/status changes, hidden physical disk add/delete/reprobe, inactive/foreign volume events, and dual-port physical disk mapping.
- Management-path tests should exercise SMP passthrough, local phy reset, link error reads, enclosure/bay lookup, and timeouts with reset recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/mptsas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/mptsas.h -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/mptsas.h

## Purpose
`mptsas.h` defines the private SAS topology, event, and mapping structures shared by the Fusion MPT SAS driver implementation. It is not a broad public API header; its types model firmware events, SAS physical topology, OS/firmware target mapping, and enclosure information used by `mptsas.c`.

## Important APIs, types, and functions
- `struct mptsas_target_reset_event` stores queued target-reset work for SAS device removal, including firmware event data, whether a reset was issued, and timing.
- `enum mptsas_hotplug_action` is the normalized action set used by `mptsas_hotplug_work()`: add/delete end device, add/delete RAID volume, add/delete/reprobe hidden physical disks, add inactive volumes, or ignore.
- `struct mptsas_mapping` records an `(id, channel)` pair for either OS-visible mapping or firmware mapping.
- `struct mptsas_device_info` tracks a discovered SAS device across OS and firmware mappings, SAS address, device flags, enclosure/slot metadata, logical volume state, hidden RAID component state, volume ownership, and cached-removal state.
- `struct mptsas_hotplug_event` is the work item payload used after raw firmware event decoding. It carries adapter, normalized event type, SAS address, bus/target IDs, device information, handle, phy ID, physical disk number, and optional `scsi_device`.
- `struct fw_event_work` embeds delayed work and flexible event payload storage for process-context firmware event handling.
- `struct mptsas_discovery_event` is a small work item for discovery/rescan style operations.
- `struct mptsas_devinfo` mirrors SAS Device Page 0 fields in CPU-endian driver form.
- `struct mptsas_portinfo_details`, `struct mptsas_phyinfo`, and `struct mptsas_portinfo` model wide/narrow SAS port groupings and link firmware data, plus kernel transport objects (`sas_phy`, `sas_port`, `sas_rphy`, `scsi_target`).
- `struct mptsas_enclosure` mirrors SAS Enclosure Page 0 fields.

## Control flow
The header supports a control flow where firmware config pages are read into `mptsas_devinfo`, `mptsas_phyinfo`, `mptsas_portinfo`, and `mptsas_enclosure`, then converted into SAS transport `identify`, phy, port, rphy, and SCSI target objects. Firmware notifications are copied into `fw_event_work`, normalized into `mptsas_hotplug_event`, and then consumed by SAS hotplug logic.

## State and persistence behavior
These structures are in-memory state only. They preserve the relationship between firmware identifiers and OS-visible SCSI topology during a driver lifetime. `mptsas_device_info::is_cached` lets the driver remember removed OS devices long enough to translate later firmware events safely. Logical volume and hidden RAID fields let the SAS driver hide or expose physical disks depending on integrated RAID state.

## Dependencies and integration points
The header assumes surrounding Fusion MPT and kernel SCSI/SAS definitions are already available: `MPT_ADAPTER`, `MPT_SCSI_HOST`, `EVENT_DATA_SAS_DEVICE_STATUS_CHANGE`, `list_head`, `delayed_work`, `work_struct`, `scsi_device`, `scsi_target`, `sas_phy`, `sas_port`, and `sas_rphy`.

## Risks and edge cases
- The structures contain raw pointers to transport and SCSI midlayer objects; lifetime rules are enforced in `mptsas.c`, not encoded in the types.
- `mptsas_portinfo_details::phy_bitmask` is a 64-bit mask with a comment noting limited support for larger phy counts.
- OS and firmware mappings can diverge during hotplug, RAID reconfiguration, and target deletion. Consumers must know whether they need `os` or `fw` mapping.
- Flexible event payloads in `fw_event_work` require callers to allocate the exact event-data size.

## Test signals
- Compile coverage should catch type drift against kernel SCSI/SAS and Fusion MPT headers.
- Runtime tests should validate that target reset queue entries, hotplug payloads, device mapping entries, and topology structs are allocated, linked, unlinked, and freed without leaks during add/remove/reset flows.
- RAID tests should verify `is_logical_volume`, `is_hidden_raid_component`, `volume_id`, and `is_cached` transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/mptsas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/mptscsih.c -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/mptscsih.c

## Purpose
`mptscsih.c` is the generic SCSI host service layer for Fusion MPT protocol drivers. It builds MPT SCSI I/O request frames from Linux `scsi_cmnd` objects, maps scatter-gather DMA including MPT chain buffers, completes SCSI commands from firmware replies, issues task-management requests, flushes commands across resets/removal, provides internal scan/domain-validation commands, adjusts queue depth, exposes host sysfs attributes, and exports these services for SAS/SPI/FC-specific drivers.

In this source set, `mptsas.c` consumes this file heavily: SAS queuecommand delegates to `mptscsih_qcmd()`, completion contexts use `mptscsih_io_done()`, reset handlers use `mptscsih_*reset()`, and SAS host attributes/lifecycle callbacks reuse this implementation.

## Important APIs, types, and functions
- I/O construction and completion: `mptscsih_qcmd()`, `mptscsih_AddSGE()`, `mptscsih_getFreeChainBuffer()`, `mptscsih_freeChainBuffers()`, and `mptscsih_io_done()`.
- Command lookup: `mptscsih_get_scsi_lookup()`, `mptscsih_getclear_scsi_lookup()`, `mptscsih_set_scsi_lookup()`, and `SCPNT_TO_LOOKUP_IDX()` manage the `ioc->ScsiLookup[]` table indexed by MPT request frame number.
- Reset/error handling: `mptscsih_IssueTaskMgmt()`, `mptscsih_abort()`, `mptscsih_dev_reset()`, `mptscsih_bus_reset()`, `mptscsih_host_reset()`, `mptscsih_taskmgmt_complete()`, `mptscsih_taskmgmt_reply()`, `mptscsih_taskmgmt_response_code()`, and `mptscsih_get_tm_timeout()`.
- Reset cleanup: `mptscsih_flush_running_cmds()`, `mptscsih_search_running_cmds()`, and `mptscsih_ioc_reset()`.
- Internal commands: `mptscsih_scandv_complete()`, `mptscsih_get_completion_code()`, `mptscsih_do_cmd()`, and `mptscsih_synchronize_cache()`.
- Device configuration: `mptscsih_sdev_configure()`, `mptscsih_sdev_destroy()`, `mptscsih_change_queue_depth()`, and `mptscsih_bios_param()`.
- RAID helpers: `mptscsih_is_phys_disk()` and `mptscsih_raid_id_to_num()` translate firmware RAID physical disk state, including SAS dual-path and inactive-list cases.
- Lifecycle and observability: `mptscsih_remove()`, `mptscsih_shutdown()`, optional `mptscsih_suspend()/resume()`, `mptscsih_info()`, `mptscsih_show_info()`, and sysfs host attributes for firmware, BIOS, MPI, product, NVDATA, board, delays, and debug level.

## Control flow
For normal I/O, the SCSI midlayer calls `mptscsih_qcmd()`. The function checks task-management quiesce state, obtains a message frame, chooses data direction and tag control, maps the Linux CDB and LUN into `SCSIIORequest_t`, selects normal SCSI I/O or RAID physical-disk passthrough, writes sense-buffer DMA address, builds either a null SGE or a full SGL with optional chain buffers, stores the command in `ScsiLookup[]`, records the frame in `host_scribble`, and posts the frame to firmware.

Firmware completion calls `mptscsih_io_done()`. The function validates request indices, retrieves and clears the lookup entry, rejects already-freed or mismatched frames, handles deleted SAS targets, translates IOC/SCSI status into Linux `sc->result`, copies sense data, logs selected errors, adjusts residual bytes, reports queue-full events, unmaps DMA, calls `scsi_done()`, and releases chain buffers.

Task management serializes on `ioc->taskmgmt_cmds.mutex` and the MPT task-management-in-progress flag. `mptscsih_IssueTaskMgmt()` checks IOC operational and doorbell state, allocates a task frame, fills target/bus/LUN/type/context fields, posts through high-priority queue or handshake path, waits for completion, parses the reply, and triggers a hard or soft-hard reset on timeout. Abort, LUN reset, bus reset, and host reset wrappers adapt this generic operation to the SCSI error-handler API.

Reset callbacks flush outstanding commands before or after IOC reset phases. Internal scan/domain-validation commands use a separate `internal_cmds` completion object and callback so they can issue INQUIRY, TUR, REQUEST SENSE, READ/WRITE BUFFER, reserve/release, and SYNCHRONIZE CACHE without going through a normal `scsi_cmnd`.

## State and persistence behavior
The key runtime state is `ioc->ScsiLookup[]`, `scsi_cmnd::host_scribble`, `ioc->ReqToChain[]`, `ioc->ChainToChain[]`, `ioc->FreeChainQ`, sense buffer pool offsets, `ioc->taskmgmt_cmds`, `ioc->internal_cmds`, target/device hostdata, and adapter RAID data. Nothing is persisted to disk.

The lookup table and chain-buffer trackers form the ownership model for in-flight I/O. Successful or failed completion must clear the lookup entry, unmap DMA, return chain buffers, and complete the SCSI command exactly once. Internal and task-management commands use completion/status fields instead of `ScsiLookup[]`.

`mptscsih_sdev_destroy()` sends SYNCHRONIZE CACHE for configured disk LUNs during teardown, except hidden RAID components. SMART sense data can be copied into the adapter event log and may trigger SEP slot predicted-fault status for IBM vendor devices.

## Dependencies and integration points
The file depends on `mptbase.h` for adapter structs, request/reply frame layout, frame allocation/posting/freeing, SGE construction, reset helpers, RAID page helpers, debug macros, and MPT management status bits. It depends on Linux SCSI midlayer APIs for `scsi_cmnd`, DMA mapping, queue depth, command completion, device/target hostdata, error handlers, and sysfs host attributes.

It is intentionally exported with many `EXPORT_SYMBOL()` entries so protocol drivers can reuse one SCSI implementation while providing transport-specific probing and topology.

## Risks and edge cases
- The `ScsiLookup[]` and `host_scribble` checks are critical double-completion guards. Any mismatch can leak frames, lose completions, or complete stale commands.
- `mptscsih_AddSGE()` handles chained SGEs manually. Off-by-one errors in chain offsets, `RequestNB`, or zero-length SGE handling would corrupt firmware requests.
- Timeout handling in task management and internal commands may free message frames and reset the IOC while a late completion is possible.
- Result translation contains adapter- and bus-specific behavior, including SPI errata, FC retry semantics, SAS nexus loss, queue-full handling, and autosense precedence. Regression risk is high if simplifying status mapping.
- Several paths depend on `VirtDevice`/`VirtTarget` hostdata being valid. Device removal and SAS hotplug must coordinate with command search/flush logic.
- The RAID helpers assume cached IOC RAID pages are current enough for hidden physical disk detection; stale pages can misclassify devices.

## Test signals
- Compile tests should cover the exported symbols with all protocol drivers that include `mptscsih.h`.
- I/O tests should verify no-data, read, write, large SG lists requiring chain buffers, zero-length SG entries, and DMA unmap on all completion/error paths.
- Error injection should cover every major IOC status class, autosense valid/failed, queue-full, device-not-there, task terminated, data underrun/overrun, residual mismatch, SAS nexus loss, and FC/SPI-specific branches.
- Reset tests should cover abort, LUN reset, bus reset, host reset, IOC reset phases, internal command timeouts, and late completion behavior.
- Device teardown tests should cover in-flight command cleanup and SYNCHRONIZE CACHE behavior.
- Sysfs tests should read all host attributes and write valid/invalid debug levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/mptscsih.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/mptscsih.h -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/mptscsih.h

## Purpose
`mptscsih.h` is the shared interface for the Fusion MPT generic SCSI host layer. It defines scan/domain-validation completion flags, internal command flags, queue-depth defaults, setup defaults, the `INTERNAL_CMD` request descriptor, and exported function prototypes used by transport-specific Fusion drivers such as `mptsas.c`.

## Important APIs, types, and functions
- Scan/DV result flags: `MPT_SCANDV_GOOD`, `MPT_SCANDV_DID_RESET`, `MPT_SCANDV_SENSE`, `MPT_SCANDV_SOME_ERROR`, `MPT_SCANDV_SELECTION_TIMEOUT`, `MPT_SCANDV_ISSUE_SENSE`, `MPT_SCANDV_FALLBACK`, and `MPT_SCANDV_BUSY`.
- Internal command flags: `MPT_ICFLAG_BUF_CAP`, `MPT_ICFLAG_ECHO`, `MPT_ICFLAG_EBOS`, `MPT_ICFLAG_PHYS_DISK`, `MPT_ICFLAG_TAGGED_CMD`, `MPT_ICFLAG_DID_RESET`, and `MPT_ICFLAG_RESERVED`.
- Queue constants: `MPT_SCSI_CMD_PER_DEV_HIGH`, `MPT_SCSI_CMD_PER_DEV_LOW`, `MPT_SCSI_CMD_PER_LUN`, and `MPT_SCSI_MAX_SECTORS`.
- Setup defaults: `MPTSCSIH_DOMAIN_VALIDATION`, `MPTSCSIH_MAX_WIDTH`, `MPTSCSIH_MIN_SYNC`, `MPTSCSIH_SAF_TE`, and `MPTSCSIH_PT_CLEAR`.
- `INTERNAL_CMD` describes internally generated SCSI CDBs: data pointer/DMA address, transfer size, opcode, firmware channel/id, LUN, flags, physical disk number, and reserved bytes.
- Exported lifecycle hooks: remove, shutdown, optional suspend/resume, info/show-info, host attribute groups.
- Exported I/O and SCSI midlayer hooks: `mptscsih_qcmd`, `mptscsih_sdev_configure`, `mptscsih_sdev_destroy`, `mptscsih_change_queue_depth`, `mptscsih_bios_param`, and completion callbacks.
- Exported error/reset hooks: task management issue/complete, abort, device reset, bus reset, host reset, IOC reset, and response-code logging.
- Exported RAID/lookup helpers: physical disk detection, RAID id-to-number mapping, SCSI lookup access, and running command flush.

## Control flow
Protocol drivers include this header to wire their `scsi_host_template` and MPT callback registration to the generic SCSI implementation. Normal queuecommand calls enter `mptscsih_qcmd()`, completions enter `mptscsih_io_done()`, error handlers call the exported reset routines, and scan/domain-validation/internal command flows use `INTERNAL_CMD` plus `mptscsih_scandv_complete()`.

## State and persistence behavior
The header does not define persistent storage. It describes transient command and status state consumed by `mptscsih.c`: internal command payloads, scan/DV status flags, command flags, and exported hooks that operate on adapter and SCSI host state. The setup constants are compile-time/default policy values rather than persisted configuration.

## Dependencies and integration points
The prototypes rely on Fusion MPT types (`MPT_ADAPTER`, `MPT_SCSI_HOST`, `MPT_FRAME_HDR`), Linux PCI power-management types, SCSI host/device/command types, block geometry types, and sysfs attribute group definitions. The header is the integration contract between generic Fusion SCSI services and specific Fusion transport modules.

## Risks and edge cases
- `#endif` for the include guard appears before the `INTERNAL_CMD` typedef and extern declarations, so repeated inclusion protection only covers the constants. This reflects the local source but is unusual and could cause duplicate declarations if included multiple times in one translation unit.
- Many exported APIs assume valid `VirtDevice`/`VirtTarget` hostdata and initialized adapter fields; the header cannot express those preconditions.
- Queue and sector constants are shared policy knobs. Changing them can alter midlayer queueing, chain-buffer pressure, and device behavior across all transport drivers.
- `INTERNAL_CMD::physDiskNum` is `u8` while comments and code use `-1` sentinel assignments; consumers rely on unsigned wraparound semantics.

## Test signals
- Compile all Fusion protocol drivers that include this header to catch prototype or include-guard regressions.
- Exercise normal I/O, exported completion callbacks, error handlers, queue-depth changes, RAID helper paths, and internal command paths from at least one transport driver.
- Static analysis should flag the unusual include-guard layout, unsigned sentinel use, and assumptions around external type availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/mptscsih.h -->
