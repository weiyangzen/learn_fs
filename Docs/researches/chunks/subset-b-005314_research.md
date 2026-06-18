# sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_scsih.c lines 1-8936

## Scope

This chunk covers the front half of the `mpt3sas_scsih.c` SCSI host layer for MPT Fusion SAS/SATA/PCIe controllers. It includes module parameters, adapter/device bookkeeping helpers, SCSI mid-layer callbacks, task-management and reset paths, firmware-event queueing, normal SCSI I/O submission/completion, SAS host/port refresh, SAS expander creation, internal discovery commands, and SAS topology add/remove handling through the beginning of SAS device-status debug decoding.

## Purpose

The code in this range is the SCSI-facing control plane for `mpt3sas` adapters. It translates Linux SCSI mid-layer requests into MPI SCSI_IO and task-management frames, maintains in-memory representations of SAS end devices, PCIe/NVMe devices, RAID volumes, expanders, enclosures, HBA ports, and virtual PHYs, and reacts to firmware topology/status events by adding, blocking, unblocking, or removing SCSI-visible devices.

The major responsibilities are:

- Register module parameters controlling queueing, discovery, logging, protection information, HBA enumeration, diag buffers, multipath, host tagsets, and discovery command retries.
- Keep per-adapter global state discoverable via `mpt3sas_ioc_list` and `gioc_lock`.
- Map firmware handles, SAS addresses, WWIDs, rphys, target IDs, channels, and HBA ports to driver-private `_sas_device`, `_pcie_device`, `_raid_device`, `_sas_node`, and `_enclosure_node` objects.
- Allocate and refcount asynchronous firmware work items.
- Bind SCSI targets/devices to `MPT3SAS_TARGET` and `MPT3SAS_DEVICE` private data.
- Build MPI request frames for normal SCSI I/O and internal discovery commands.
- Convert firmware completions into SCSI result codes, sense data, queue state, SMART/PFA behavior, and debug logging.
- Handle SCSI error recovery through abort, logical-unit reset, target reset, and host reset.
- Perform removal handshakes: target reset first, then SAS IO unit remove-device control.
- Maintain SAS transport topology after port enable, host reset, expander events, and link changes.

## Important Types And State

- `enum device_responsive_state` is the local state machine for discovery probes: `DEVICE_READY`, `DEVICE_RETRY`, `DEVICE_RETRY_UA`, `DEVICE_START_UNIT`, `DEVICE_STOP_UNIT`, and `DEVICE_ERROR`.
- `struct sense_info` is a normalized tuple of SCSI sense key, ASC, and ASCQ, used for both fixed and descriptor sense data.
- `struct fw_event_work` wraps firmware event payloads for process-context handling. It carries retry counters, delayed-work state, list membership, the adapter pointer, device handle, VF/VP IDs, ignore flag, event code, a `kref`, and inline event data.
- `struct _scsi_io_transfer` is an internal SCSI command descriptor used for discovery/TUR/START/ATA pass-through flows. It stores target handle, RAID-pass-through flag, DMA direction and address, CDB, LUN, timeout, reply validity, sense, IOC status, SCSI status/state, log info, and transferred length.
- Driver-private state is anchored in `struct MPT3SAS_ADAPTER`: device lists, locks, callback indexes, command tracking slots (`tm_cmds`, `scsih_cmds`), firmware-event queue, HBA SAS topology, pending-bitmaps, and recovery flags. This file assumes most definitions come from `mpt3sas_base.h`.
- SCSI private objects are attached by `scsih_target_alloc()` and `scsih_sdev_init()`: `struct MPT3SAS_TARGET` is stored on `scsi_target->hostdata`, and `struct MPT3SAS_DEVICE` is stored on `scsi_device->hostdata`.

## Module Parameters And Global Integration

The file registers kernel module metadata and many tunables:

- `logging_level` updates every adapter in `mpt3sas_ioc_list` under `gioc_lock`.
- `max_sectors`, `max_lun`, `missing_delay`, `disable_discovery`, `diag_buffer_enable`, `prot_mask`, `enable_sdev_max_qd`, `issue_scsi_cmd_to_bringup_drive`, `multipath_on_hba`, `host_tagset_enable`, and `command_retry_count` alter queue limits, discovery behavior, retries, multipath behavior, and diagnostics.
- RAID transport integration is carried by `mpt2sas_raid_template` and `mpt3sas_raid_template`, selected by MPI generation.

The chunk depends heavily on Linux SCSI mid-layer APIs (`scsi_add_device`, `scsi_done`, `scsi_change_queue_depth`, `scsi_host_find_tag`, `shost_for_each_device`, error-handler return values), SAS transport APIs (`sas_enable_tlr`, `sas_read_port_mode_page`, transport add/remove/update helpers), block queue limits, DMA coherent memory, kernel workqueues, spinlocks, mutexes, completions, and MPI configuration/message definitions.

## Device Lookup, Lists, And Reference Behavior

SAS, PCIe, RAID, expander, and enclosure objects are stored in adapter-owned lists protected by specific spinlocks:

- SAS devices use `ioc->sas_device_lock` and are searched by target private data, rphy, SAS address plus HBA port, or firmware handle. Both live and init-time lists are consulted. Successful SAS lookups increment the object kref through `sas_device_get()`.
- PCIe devices use `ioc->pcie_device_lock` and are searched by target private data, WWID, channel/id, or handle. Successful lookups call `pcie_device_get()`.
- RAID volumes use `ioc->raid_device_lock` and are searched by channel/id, handle, or WWID, but the helper returns raw list pointers rather than kref-managed references in this chunk.
- Expanders are tracked as `_sas_node` objects on `ioc->sas_expander_list` under `ioc->sas_node_lock`, by handle or SAS address plus HBA port.
- Enclosures are found by enclosure handle from `ioc->enclosure_list`.

Add/remove helpers follow a consistent ownership model: add functions take an extra reference before list insertion; remove functions delete from the list under lock, drop the list reference, and then perform SCSI/transport teardown outside the lock. This pattern is visible in `_scsih_sas_device_add()`, `_scsih_sas_device_remove()`, `_scsih_device_remove_by_handle()`, `_scsih_pcie_device_add()`, `_scsih_pcie_device_remove()`, and `_scsih_pcie_device_remove_by_handle()`.

The code must preserve user-visible boot ordering during initial load. `_scsih_determine_boot_device()` matches discovered RAID, SAS, or PCIe devices against BIOS page 2 requested, alternate, and current boot-device forms. It stores pointers and channels for later boot-device probing, but only while `ioc->is_driver_loading` is true and BIOS page 3 reports a BIOS version.

## SCSI Target And Device Lifecycle

`scsih_target_alloc()` allocates `MPT3SAS_TARGET`, attaches it to `starget->hostdata`, and binds it to one of three backend object classes:

- RAID channel (`RAID_CHANNEL`): maps target ID/channel to `_raid_device`, records the firmware handle, WWID as SAS address, volume flag, and WarpDrive direct-I/O pointer when applicable.
- PCIe channel (`PCIE_CHANNEL`): maps target ID/channel to `_pcie_device`, records handle/WWID, sets PCIe-device flags and fast-path flags, and stores the back pointer.
- SAS/SATA devices: resolves the target parent rphy to `_sas_device`, records handle/SAS address/port, sets RAID-component and fast-path flags, and stores the target ID/channel into the device object.

`scsih_target_destroy()` reverses those bindings, clearing `starget`/`sdev` back pointers and dropping references taken during allocation. `scsih_sdev_init()` allocates `MPT3SAS_DEVICE`, tracks the LUN, links to target private data, hides RAID components from upper-level drivers, and fills RAID/PCIe/SAS back pointers if they were missing. `scsih_sdev_destroy()` decrements target LUN count, clears target pointers when the last LUN disappears, and frees device-private data.

`scsih_sdev_configure()` performs device-specific setup:

- RAID volumes read volume capabilities, initialize WarpDrive properties, select queue depth by RAID level/backing media, cap RAID `max_hw_sectors`, set RAID transport level, and return.
- Hidden RAID physical disks resolve volume handle/WWID for later logging and reset handling.
- PCIe/NVMe devices select `ioc->max_nvme_qd`, log WWID/port/enclosure info, cap transfer size to the smaller of firmware-reported MDTS and the driver’s 2 MiB PRP-list limit, set `virt_boundary_mask`, and return.
- SAS/SATA devices choose queue depth by protocol and port width, mark SES devices with `ignore_delay_remove`, log enclosure and location metadata, display SATA capabilities, optionally issue ATA IDENTIFY DEVICE to mark SSDs, and enable TLR for SSP tape devices.

Queue depth changes route through `scsih_change_queue_depth()` and `mpt3sas_scsih_change_queue_depth()`. SATA devices are limited to `MPT3SAS_SATA_QUEUE_DEPTH` unless `enable_sdev_max_qd` or Gen3.5 behavior allows broader queueing; non-tagged devices are forced to depth 1.

## Normal SCSI I/O Path

`scsih_qcmd()` is the main request entry point from the SCSI mid-layer. Its control flow is:

1. Validate device and target private data; complete with `DID_NO_CONNECT` if absent.
2. Gate commands through `_scsih_allow_scmd_to_device()`, which rejects most I/O during PCI error recovery or host removal, with newer MPI generations still allowing shutdown-oriented `SYNCHRONIZE_CACHE` and `START_STOP`.
3. Reject invalid handles, deleted targets, and blocked devices; return host/device busy for recovery, link-reset, task-management, or blocked states.
4. Serialize ATA pass-through commands with `ata_command_pending` to work around firmware SATL behavior.
5. Build MPI control flags from DMA direction, simple queueing, NCQ priority, and TLR enablement.
6. Obtain an SCSI I/O SMID, clear the request frame, configure EEDP/T10 PI if required, fill function, handle, data length, CDB, LUN, sense buffer, and SGL.
7. Optionally apply WarpDrive direct I/O, then post through fast-path, normal SCSI I/O, or default queues depending on target flags and function.

`_scsih_io_done()` is the completion path. It finds the original `scsi_cmnd` by SMID and block-mq tag, clears SATL pending state, handles direct-I/O fallback to the RAID volume, copies autosense data, triggers SMART/PFA handling for ASC `0x5d`, sets residuals, and maps IOC status plus SCSI state/status into Linux SCSI result codes. It handles special cases including SATA NCQ collateral abort retry (`DID_IMM_RETRY`), virtual I/O retry, RAID task termination, underrun/overrun handling, EEDP guard/app/ref-tag sense construction, and TLR disablement when invalid-frame response info is observed. It finally unmaps DMA, frees the SMID, and calls `scsi_done()`.

Debug helpers `_scsih_scsi_ioc_info()`, `_scsih_response_code()`, and `_scsih_normalize_sense()` convert firmware status into readable kernel logs and normalized sense tuples.

## Task Management And Error Recovery

SCSI EH callbacks are implemented by:

- `scsih_abort()`: checks whether the command is still tracked, rejects RAID volumes/components, chooses NVMe-specific timeout if needed, sends `ABORT_TASK`, and verifies the command really disappeared from the tracker.
- `scsih_dev_reset()`: sends logical unit reset, using volume handle for hidden RAID components and PCIe protocol-level reset for NVMe where appropriate, then checks `scsi_device_busy()`.
- `scsih_target_reset()`: similar to device reset but target scoped and checks `target_busy`.
- `scsih_host_reset()`: blocks resets during driver load/removal and otherwise calls `mpt3sas_base_hard_reset_handler(..., FORCE_BIG_HAMMER)`.

`mpt3sas_scsih_issue_tm()` is the shared task-management sender. It requires `ioc->tm_cmds.mutex`, checks recovery/removal/PCI states, hard-resets on doorbell/fault/coredump states, obtains a high-priority SMID, builds `MPI2_FUNCTION_SCSI_TASK_MGMT`, sets the per-target `tm_busy` flag, waits for completion, synchronizes reply IRQs, logs responses, and maps TM outcome to `SUCCESS` or `FAILED`. Target/LUN resets call `scsih_tm_post_processing()` to poll reply descriptor queues before declaring failure, because an aborted I/O completion may arrive after the TM completion.

`mpt3sas_scsih_set_tm_flag()` and `mpt3sas_scsih_clear_tm_flag()` walk all SCSI devices and toggle `tm_busy` plus `ioc->ignore_loginfos` for the target handle. `_scsih_tm_done()` completes the TM command slot and copies replies.

## Firmware Event Queue And Removal Handshakes

Firmware events are converted into `fw_event_work` objects and queued to `ioc->firmware_event_thread`:

- `_scsih_fw_event_add()` inserts the event into `ioc->fw_event_list`, initializes work, and takes references for list and work ownership.
- `_scsih_fw_event_requeue()` uses delayed work for retrying busy discovery/topology events.
- `_scsih_fw_event_del_from_list()`, `dequeue_next_fw_event()`, and `_scsih_fw_event_cleanup_queue()` coordinate teardown, mark current events ignored during recovery, cancel queued work, clear `start_scan` for port-enable cleanup, and avoid deadlocks with current events that may trigger reset.
- `mpt3sas_send_trigger_data_event()`, `_scsih_error_recovery_delete_devices()`, and `mpt3sas_port_enable_complete()` synthesize internal events.

Device removal uses a handshake with firmware:

- `_scsih_tm_tr_send()` marks the target deleted, unblocks/offlines SCSI-facing state, invalidates the target handle, obtains a high-priority SMID, sends target reset, marks `device_remove_in_progress`, and posts a master trigger. If no SMID is available, it queues a `_tr_list` entry.
- `_scsih_tm_tr_complete()` validates the TM reply, then sends `MPI2_SAS_OP_REMOVE_DEVICE` through SAS IO unit control. If no internal SMID exists, it queues a `_sc_list` entry.
- `_scsih_sas_control_complete()` clears `device_remove_in_progress` on successful SAS IO unit control completion and advances delayed internal commands.
- Volume reset/removal has parallel helpers `_scsih_tm_tr_volume_send()` and `_scsih_tm_volume_tr_complete()`.
- `mpt3sas_check_for_pending_internal_cmds()` and `_scsih_check_for_pending_tm()` reuse freed SMIDs to drain delayed event ACK, SAS IO unit control, volume target reset, and device target reset lists.

Topology sanity helpers `_scsih_check_topo_delete_events()`, `_scsih_check_pcie_topo_remove_events()`, `_scsih_check_ir_config_unhide_events()`, and `_scsih_check_volume_delete_events()` pre-block devices, send target resets, suppress stale queued add/responding events, and mark RAID targets deleted when firmware reports removal or failure.

## Blocking And Unblocking I/O

The driver uses SCSI internal block/unblock transitions to avoid dispatching I/O to disappearing or not-yet-ready devices:

- `_scsih_internal_device_block()` sets private `block` and calls `scsi_internal_device_block_nowait()`.
- `_scsih_internal_device_unblock()` clears `block`, calls `scsi_internal_device_unblock_nowait(..., SDEV_RUNNING)`, and retries via block-then-unblock on `-EINVAL`.
- `_scsih_block_io_all_device()` blocks every eligible device except SES devices marked `ignore_delay_remove`.
- `_scsih_block_io_device()` blocks all LUNs under one handle, skipping devices still pending rphy add.
- `_scsih_block_io_to_children_attached_to_ex()` recursively marks all end devices under an expander for blocking.
- `_scsih_ublock_io_all_device()` and `_scsih_ublock_io_device_wait()` optionally probe devices with TUR/START/REPORT LUNS before unblocking. Devices that never become ready are marked deleted and moved to `SDEV_OFFLINE`.
- `_scsih_ublock_io_device()` is the simpler unblock path used during delete preparation.

The readiness path depends on `issue_scsi_cmd_to_bringup_drive` and `command_retry_count`. PCIe/NVMe devices may use protocol-level reset method and device-specific timeout from `_pcie_device`.

## Internal Discovery Commands

Internal commands use the reserved discovery SMID and `ioc->scsih_cmds`:

- `_scsi_send_scsi_io()` builds a SCSI_IO or RAID pass-through request from `_scsi_io_transfer`, posts it, waits for completion, copies reply/sense metadata, and on timeout may issue a target reset using `mpt3sas_scsih_issue_locked_tm()`. It retries after successful target reset up to three times for command-aborted cases and once after host-reset completion.
- `_scsih_determine_disposition()` interprets internal command replies into `device_responsive_state`. It treats busy/resources/terminated statuses as retry, maps sense unit attention to retry-UA, NOT READY to start-unit or error depending on ASC/ASCQ, and allows some medium/hardware error cases to proceed so users can inspect failing media.
- `_scsih_report_luns()` allocates coherent memory, sends REPORT LUNS with up to four local tries, and copies successful LUN data.
- `_scsih_test_unit_ready()` sends TUR and includes one special retry for SATA initialization timeout log info `0x31111000`.
- `_scsih_start_unit()` sends START STOP UNIT with START bit set.
- `_scsih_ata_pass_thru_idd()` sends ATA_12 IDENTIFY DEVICE and marks SATA SSDs when word 217 reports nominal media rotation rate `1`.
- `_scsih_wait_for_device_to_become_ready()` and `_scsih_wait_for_target_to_become_ready()` combine TUR, START UNIT, REPORT LUNS, and per-LUN retry/error evaluation.

## SAS Host, Port, Virtual PHY, And Expander Handling

`mpt3sas_get_port_by_id()` returns an HBA port entry, using `MULTIPATH_DISABLED_PORT_ID` when HBA multipath is disabled and lazily creating the default port object in that mode. `mpt3sas_get_vphy_by_phy()` finds a virtual PHY in a port’s `vphys_list`.

Host/port refresh paths include:

- `_scsih_sas_host_add()` reads SAS IO Unit pages 0/1, allocates HBA PHY objects, records missing-delay values, creates port entries, detects virtual SES PHYs, adds host PHYs to SAS transport, obtains HBA enclosure/SAS address metadata, and logs the host.
- `_scsih_sas_host_refresh()` updates HBA handle, ports, virtual PHYs, host PHYs, and link state after port enable or reset; it also handles added/removed HBA PHYs after firmware changes.
- `_scsih_get_port_table_after_reset()`, `_scsih_look_and_get_matched_port_entry()`, `_scsih_add_or_del_phys_from_existing_port()`, `_scsih_del_dirty_vphy()`, `_scsih_del_dirty_port_entries()`, `_scsih_update_vphys_after_reset()`, and `_scsih_sas_port_refresh()` reconcile old and new HBA port tables after reset, including matching by SAS address, port ID, and PHY mask.

Expander handling is implemented by `_scsih_expander_add()` and `mpt3sas_expander_remove()`:

- `_scsih_expander_add()` reads expander page 0, recursively adds the parent expander if topology events arrive out of order, rejects duplicates by SAS address/port, allocates `_sas_node`, creates a SAS transport port, reads every expander PHY page 1, adds expander PHYs to transport, attaches enclosure logical ID if available, and links the expander into `ioc->sas_expander_list`.
- `mpt3sas_expander_remove()` finds the expander by SAS address/port and delegates to `_scsih_expander_node_remove()` unless recovery is active.

## SAS Device Add, Check, Remove, And Topology Events

`_scsih_add_device()` is the main SAS/SATA end-device discovery routine. It reads SAS device page 0, verifies the object is an end device, sets `pend_os_device_add`, verifies presence and access status, rejects duplicates by SAS address and HBA port, looks up enclosure metadata, optionally waits for the target to become ready, allocates `_sas_device`, fills handle, parent SAS address, enclosure fields, device info, SAS address, PHY, fast-path flag, port, connector/chassis metadata, device name, and port type, then inserts into either the init list or live list.

`_scsih_check_device()` handles a known device after link change. It validates the page, ignores non-matching wide-port PHYs, verifies end-device and presence/access status, updates changed firmware handles and enclosure metadata, then unblocks the device, with readiness probing if configured.

`_scsih_remove_device()` turns off IBM PFA LEDs if needed, marks the SCSI target deleted, unblocks pending I/O state, invalidates the target handle, removes the SAS transport port unless drives are hidden, and logs location metadata.

`_scsih_sas_topology_change_event()` is the process-context handler for SAS topology-change events in this chunk. It refreshes or creates the SAS host, honors ignored events, adds expanders, resolves parent SAS address and max PHY count, loops event PHY entries, and handles:

- `PHY_CHANGED`: update transport links, check existing devices on active links, and convert certain pending missing-device cases into add events.
- `TARG_ADDED`: update transport links, call `_scsih_add_device()`, increment per-entry retry counters and request event requeue if the device is busy, or mark the entry vacant once processed.
- `TARG_NOT_RESPONDING`: remove the SAS device by firmware handle.
- Expander `NOT_RESPONDING`: remove the expander after child processing.

The chunk ends inside `_scsih_sas_device_status_change_event_debug()`, which maps SAS device status reason codes such as SMART data, unsupported device, internal resets/task aborts, SATA init failure, async notification, and expander reduced functionality to strings for debug logging.

## Dependencies And Integration Points

Key dependencies and integration surfaces include:

- MPI configuration accessors: SAS device page 0, SAS IO Unit pages 0/1, SAS PHY page 0, expander pages 0/1, enclosure page 0, RAID volume page 0, physical disk page 0, volume handle/WWID, and number-of-PDs/phys helpers.
- MPI posting/completion helpers: `mpt3sas_base_get_smid_*()`, `mpt3sas_base_get_msg_frame()`, `put_smid_*()`, `mpt3sas_base_free_smid()`, reply virtual address lookup, sense buffer lookup/DMA address lookup, IRQ synchronization, hard reset, IOC state checks, and command-timeout checks.
- SAS transport helpers: port add/remove, host/expander PHY add, link updates, add/delete PHY from existing port.
- RAID class helpers: `raid_set_resync()`, `raid_set_state()`, `raid_set_level()`.
- Control/event logging: `mpt3sas_ctl_add_to_event_log()`, trigger master/SCSI hooks, debug print macros, and enclosure processor requests for PFA LEDs.
- Block/SCSI behavior: queue limits, tag lookup, request priority, SCSI protection operations, sense construction, `DID_*`/`SAM_STAT_*` result mapping, SCSI device state transitions, and EH callback contracts.

## Risks And Edge Cases

- List objects are heavily shared between interrupt, workqueue, SCSI EH, discovery, and removal paths. Correct kref and lock pairing is critical; double `put()` patterns in target destroy correspond to references taken during lookup and target allocation and are easy to break.
- `_scsih_sas_port_refresh()` allocates `port_table` but has early returns that can leak it in this chunk if `port_count` is zero; downstream code may handle or tolerate this, but this path warrants review if modified.
- `_scsih_check_pcie_topo_remove_events()` compares PCIe switch status against SAS topology constants in some paths, likely because firmware values overlap; this is brittle and should be treated cautiously.
- `_scsih_ublock_io_device_wait()` obtains `pcie_device` inside a retry loop but only releases it on the non-retry path before `continue`; changes here should check for reference leaks across retry paths.
- `scsih_sdev_configure()` drops the `sas_device` reference before issuing `_scsih_ata_pass_thru_idd()` but then passes `&sas_device->ssd_device`; that lifetime assumption is delicate and depends on the object not disappearing during configure.
- Discovery readiness is intentionally slow: default `command_retry_count` is 144, with repeated TUR/START/REPORT LUNS and sleeps. Tests should account for delayed devices and avoid assuming immediate add/remove convergence.
- Many error paths return generic `-1`, `0`, `1`, `FAILED`, or `DEVICE_RETRY`; callers interpret these differently. Preserve local return conventions when editing.
- Topology event coalescing and ignore flags are designed to handle cable pulls, out-of-order expander events, and busy devices. Removing or simplifying retry/ignore logic risks stale add events resurrecting removed devices.
- The removal handshake depends on `device_remove_in_progress` to block internal commands while firmware removal is pending. Missing a clear or set can create discovery failures or unsafe I/O to removed handles.
- Normal I/O result mapping includes numerous firmware-specific log-info exceptions. Changing status mapping can alter SCSI retry/offline behavior and cause data path regressions.

## Test Signals

Useful validation signals for this chunk include:

- Kernel build with `drivers/scsi/mpt3sas` enabled and sparse/smatch-style static analysis around locking and references.
- Boot or module load with SAS, SATA, RAID volume, and PCIe/NVMe devices attached; confirm target allocation, queue depths, max sector limits, and transport objects appear under sysfs.
- Hot-add and hot-remove direct-attached SAS/SATA devices; watch for `pend_os_device_add`, blocked/unblocked state, target reset plus SAS IO unit remove-device completion, and no stale target handles.
- Expander add/remove and cable-pull tests, including out-of-order parent/child topology events, delayed-not-responding events, and busy devices that require event requeue.
- Host reset and port enable tests; verify HBA port table, virtual PHYs, host PHYs, link rates, and expander/device handles refresh correctly.
- SCSI EH injection or fault injection for abort, logical unit reset, target reset, and host reset; verify commands are completed once and EH callbacks return expected status.
- Internal discovery command tests for REPORT LUNS, TUR, START UNIT, SATA initialization timeout, ATA IDENTIFY, and devices returning UNIT ATTENTION, NOT READY, medium error, hardware error, or illegal request.
- NVMe behind Tri-Mode HBA tests for MDTS/max_hw_sectors cap, protocol-level reset timeout, and shutdown latency recalculation on removal.
- RAID volume state/resync tests through raid class sysfs; validate volume delete/unhide events and hidden physical disk reset sequencing.
- SMART/PFA tests for ASC `0x5d`, event-log insertion, and IBM enclosure LED on/off behavior.
