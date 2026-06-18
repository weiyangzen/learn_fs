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

`sas_device_info_list` caches firmware mapping, OS mapping, SAS address, device flags, enclosure/slot metadata, logical-volume status, hidden RAID component status, and a cached-removed flag. This list is used to translate firmware events such as queue-full or RAID component changes into OS SCSI targets.

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
