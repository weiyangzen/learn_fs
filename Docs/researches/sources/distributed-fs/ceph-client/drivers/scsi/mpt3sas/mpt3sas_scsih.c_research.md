# Research: sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_scsih.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-005314`: lines 1-8936, `Docs/researches/chunks/subset-b-005314_research.md`
- `subset-b-005315`: lines 8937-14182, `Docs/researches/chunks/subset-b-005315_research.md`

## Chunk Research

### subset-b-005314: lines 1-8936

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

### subset-b-005315: lines 8937-14182

# sources/distributed-fs/ceph-client/drivers/scsi/mpt3sas/mpt3sas_scsih.c lines 8937-14182

## Scope

This chunk is the tail of the `mpt3sas_scsih.c` SCSI host driver. It starts in the SAS device-status event handling area and covers PCIe/NVMe device discovery, PCIe topology and status events, SAS enclosure and broadcast events, Integrated RAID (IR) volume/physical-disk events, reset-time device reconciliation, firmware event workqueue dispatch, expander removal, NVMe/IR shutdown notifications, PCI remove/shutdown, initial SCSI scanning, host queue mapping, PCI probe, power-management and PCI error recovery callbacks, the supported PCI ID table, callback registration, and module init/exit.

The chunk depends heavily on earlier code in the same file for the SCSI command path, target/device allocation, SAS topology helpers, firmware-event queue helpers, task-management completions, transport callbacks, boot-device selection, and sysfs/debugfs attributes. It also integrates with the broader `mpt3sas` core/config/transport/control modules through functions prefixed `mpt3sas_base_*`, `mpt3sas_config_*`, `mpt3sas_transport_*`, and `mpt3sas_ctl_*`.

## Purpose

The visible code is the driver lifecycle and event-reconciliation layer. It converts asynchronous MPI firmware events and reset notifications into Linux SCSI/SAS transport state, and it turns PCI probe/remove/shutdown callbacks into a configured `Scsi_Host` backed by one `struct MPT3SAS_ADAPTER`.

Its main responsibilities are:

- maintain runtime lists for SAS end devices, PCIe/NVMe devices, RAID volumes, expanders, enclosures, HBA ports, firmware events, and pending delayed actions;
- process firmware events from interrupt context by copying event payloads into `struct fw_event_work`, then dispatching them in an ordered workqueue in process context;
- add, remove, block, unblock, or reprobe devices in response to PCIe topology changes, SAS broadcast primitives, enclosure status changes, RAID configuration changes, RAID volume/PD state transitions, and reset recovery;
- reconcile device state after controller reset by marking existing objects as responding, pruning unresponding objects, refreshing handles/enclosure metadata, and scanning firmware config pages for new devices;
- publish devices to the SCSI midlayer and SAS transport during initial scan while preserving boot-device ordering;
- issue shutdown notifications to NVMe and Integrated RAID firmware before suspend, shutdown, or remove;
- allocate and initialize the adapter object during PCI probe, set host-template parameters, register workqueues/debugfs, attach the base hardware layer, add the SCSI host, and trigger scanning;
- register PCI error-recovery, PM, PCI-driver, SCSI-host-template, SAS transport, RAID transport, and module entry/exit integration points.

## Important APIs, Types, and Functions

### Event and Device Discovery

- `_scsih_sas_device_status_change_event()` handles SAS internal device-reset start/complete events for sufficiently new MPI firmware. It looks up a SAS device by SAS address and physical port under `ioc->sas_device_lock` and toggles `MPT3SAS_TARGET.tm_busy`.
- `_scsih_check_pcie_access_status()` normalizes `MPI26_PCIEDEV0_ASTATUS_*` access statuses. It treats no-error, needs-initialization, and device-blocked as non-fatal for list creation, logs all other discovery failures, and returns nonzero for add/check abort.
- `_scsih_pcie_check_device()` rereads PCIe Device Page 0 for an attached handle, validates it as NVMe or PCIe-SCSI, updates changed handles/enclosure fields for an existing `_pcie_device`, verifies presence/access status, and unblocks I/O for the device.
- `_scsih_pcie_add_device()` creates a new `_pcie_device` from PCIe Device Page 0 and, for NVMe, Page 2. It records ID/channel/handle/WWID/device info, port number, fast-path capability, enclosure/connector metadata, MDTS, shutdown latency, and reset timeout. It returns `1` when the topology event should be requeued because the target is not ready.
- `_scsih_pcie_topology_change_event()` processes each PCIe topology entry. Add and link-rate-change paths call `_scsih_pcie_add_device()` or `_scsih_pcie_check_device()`; not-responding paths remove by handle. Requeue state is stored per entry in `fw_event->retries`.
- `_scsih_pcie_device_status_change_event()` handles PCIe internal reset start/complete events and toggles `MPT3SAS_TARGET.tm_busy` using `_pcie_device` lookup by WWID.
- `_scsih_sas_enclosure_dev_status_change_event()` adds/removes `_enclosure_node` objects from `ioc->enclosure_list` based on enclosure add/remove events and Enclosure Page 0 reads.
- `_scsih_sas_broadcast_primitive_event()` handles SAS asynchronous event notifications by blocking I/O, iterating outstanding SCSI I/O, issuing QUERY TASK, aborting commands no longer owned by IOC/target, retrying bounded loops, and unblocking I/O when complete.
- `_scsih_sas_discovery_event()`, `_scsih_sas_device_discovery_error_event()`, and `_scsih_pcie_enumeration_event()` mainly log discovery/enumeration progress and important SAS SMP discovery errors.

### Integrated RAID Handling

- `_scsih_ir_fastpath()` issues a RAID ACTION command to hide an IR physical disk and enable fast path for MPI 2.5+ devices.
- `_scsih_sas_volume_add()` and `_scsih_sas_volume_delete()` maintain `_raid_device` objects, create/remove SCSI devices on `RAID_CHANNEL`, and preserve discovery-time boot ordering when `ioc->wait_for_discovery_to_complete` is true.
- `_scsih_sas_pd_expose()`, `_scsih_sas_pd_hide()`, `_scsih_sas_pd_delete()`, and `_scsih_sas_pd_add()` update physical-disk membership in volumes, `pd_handles`, target flags, volume handles/WWIDs, fast-path state, transport links, and SCSI visibility through `scsi_device_reprobe()`.
- `_scsih_sas_ir_config_change_event()` dispatches IR config elements for volume add/delete and physical-disk hide/unhide/create/delete. During reset recovery on newer HBAs it only refreshes fast-path state for hide events.
- `_scsih_sas_ir_volume_event()` removes missing/failed volumes and adds online/degraded/optimal volumes that are not already present.
- `_scsih_sas_ir_physical_disk_event()` handles online/degraded/rebuilding/optimal/hot-spare PD state by refreshing SAS link state and adding the SAS device if absent.
- `_scsih_sas_ir_operation_status_event()` records RAID resync percent complete in the matching `_raid_device` for raid-class transport reporting.

### Reset Reconciliation

- `_scsih_prep_device_scan()` marks all `MPT3SAS_TARGET` objects behind current SCSI devices as deleted before reset reconciliation.
- `_scsih_update_device_qdepth()` reapplies firmware-reported queue-depth policy after Gen3.5 reset recovery, choosing NVMe, SSP wide/narrow, or SATA queue depths.
- `_scsih_mark_responding_sas_device()`, `_scsih_mark_responding_pcie_device()`, `_scsih_mark_responding_raid_device()`, and `_scsih_mark_responding_expander()` update in-memory objects found in firmware config pages after reset. They clear `deleted`/`tm_busy`, set `responding`, refresh handles and enclosure metadata, and update WarpDrive properties for RAID volumes.
- `_scsih_create_enclosure_list_after_reset()` rebuilds `ioc->enclosure_list` from Enclosure Page 0 entries after freeing the old list.
- `_scsih_search_responding_sas_devices()`, `_scsih_search_responding_pcie_devices()`, `_scsih_search_responding_raid_devices()`, and `_scsih_search_responding_expanders()` scan firmware config pages and call the mark helpers.
- `_scsih_remove_unresponding_devices()` removes list objects not marked responding after reset. It first drains init lists, moves unresponding SAS and PCIe devices to temporary lists to drop locks before SCSI/transport removal, removes dead RAID volumes and expanders, resets responding flags for survivors, and unblocks I/O.
- `_scsih_refresh_expander_links()` rereads Expander Page 1 for each expander PHY and refreshes SAS transport links.
- `_scsih_scan_for_devices_after_reset()` performs a full post-reset discovery sweep: refresh HBA phys, add or refresh expanders, add missing IR physical disks, add missing volumes, add missing SAS end devices, and add missing PCIe/NVMe devices with retry loops for not-ready targets.
- `mpt3sas_scsih_clear_outstanding_scsi_tm_commands()` marks pending internal SCSI/task-management commands reset, frees their SMIDs, completes waiters, clears pending add/remove bitmaps, cleans firmware events, and flushes running commands.
- `mpt3sas_scsih_reset_done_handler()` is the reset completion callback. It refreshes multipath port state, prepares deletion flags, rebuilds enclosures, marks responding SAS/PCIe/RAID/expander objects, and schedules error-recovery deletion of nonresponders.

### Firmware Event Queue

- `_mpt3sas_fw_work()` is the process-context dispatcher for `struct fw_event_work`. It removes work from the adapter queue, ignores events during host removal or PCI error recovery, dispatches each supported event, requeues SAS/PCIe topology events when add retries are needed, and drops the work reference on completion.
- `_firmware_event_work()` and `_firmware_event_work_delayed()` are wrappers for immediate and delayed work items.
- `mpt3sas_scsih_event_callback()` runs at interrupt time. It validates the event reply, triggers diagnostic event hooks, performs fast in-interrupt filtering or state changes for selected events, allocates `fw_event_work`, copies event data, allocates per-entry retry arrays for topology events, and queues the event to the ordered firmware event workqueue.

### Probe, Scan, Remove, Shutdown

- `_scsih_nvme_shutdown()` sends an MPI 2.6 IO Unit Control shutdown operation when PCIe devices exist, waiting up to `ioc->max_shutdown_latency`.
- `_scsih_ir_shutdown()` sends RAID ACTION SYSTEM SHUTDOWN INITIATED when IR firmware and RAID volumes exist.
- `_scsih_get_shost_and_ioc()` retrieves and validates the `Scsi_Host` and adapter private data from `pci_get_drvdata()`.
- `scsih_remove()` stops new work with `remove_host`, flushes firmware events, destroys the workqueue, restores Aero IOC Page 1 copy, notifies IR shutdown, removes SAS host/RAID/PCIe/SAS transport objects, frees port and HBA PHY state, detaches base resources, releases control/debugfs state, removes the adapter from the global IOC list, and drops the SCSI host reference.
- `scsih_shutdown()` is a lighter system-shutdown path. It cleans event work, restores Aero IOC Page 1, sends IR and NVMe shutdowns, masks interrupts, stops watchdog, makes the IOC ready through soft reset, and frees IRQ/MSI-X resources.
- `_scsih_probe_boot_devices()`, `_scsih_probe_raid()`, `_scsih_probe_sas()`, and `_scsih_probe_pcie()` publish discovered devices to the SCSI midlayer and SAS transport, moving objects from init lists to active lists with reference-count adjustments.
- `_scsih_probe_devices()` orders boot-device, RAID, SAS, and PCIe publication. For IR firmware it honors low-volume versus default volume mapping; without IR it probes SAS then PCIe.
- `scsih_scan_start()` enables diagnostic buffers and starts firmware discovery via `mpt3sas_port_enable()`.
- `_scsih_complete_devices_scanning()` probes devices after discovery, starts the watchdog, and clears `is_driver_loading`.
- `scsih_scan_finished()` polls port-enable completion, handles 300-second timeout, controller fault/coredump reset cases, port-enable reset aborts, and start-scan failures.
- `scsih_map_queues()` maps SCSI block-mq hardware queues to MSI-X reply queues, with default and optional poll maps for host-tagset Gen3.5 configurations.
- `_scsih_determine_hba_mpi_version()` maps PCI device IDs to MPI2, MPI2.5, or MPI2.6 families.
- `_scsih_probe()` is the PCI probe callback. It selects the SCSI host template, allocates `Scsi_Host`, initializes `struct MPT3SAS_ADAPTER`, assigns callback indices and driver features, initializes all locks/lists, configures host limits/protection, creates the ordered firmware event workqueue, attaches base hardware resources, applies WarpDrive/hide-drive policy, configures host tagset queues, adds the SCSI host, starts scanning, and creates debugfs.
- `scsih_suspend()` and `scsih_resume()` handle PM by stopping/starting the watchdog, blocking/unblocking SCSI requests, issuing NVMe shutdown before resource free, remapping resources, and forcing a hard reset on resume.
- `scsih_pci_error_detected()`, `scsih_pci_slot_reset()`, `scsih_pci_resume()`, and `scsih_pci_mmio_enabled()` implement PCI AER/EEH recovery.
- `mpt3sas_pci_table[]`, `_mpt3sas_err_handler`, `scsih_pm_ops`, and `mpt3sas_driver` register the supported device IDs and PCI callback surfaces.
- `scsih_init()` registers callback-handler indices with the base layer; `scsih_exit()` releases them and releases RAID/SAS transport templates/debugfs.
- `_mpt3sas_init()` attaches SAS and RAID transport templates, initializes SCSI-host callbacks/control device support, and registers the PCI driver. `_mpt3sas_exit()` unregisters the PCI driver, exits control support, and releases callback/transport state.

## Control Flow

Firmware events enter through `mpt3sas_scsih_event_callback()` at interrupt time. The callback ignores events during PCI error recovery, obtains the event notification reply, and handles only events relevant to this SCSI host layer. Some events update state immediately: SAS broadcast primitives coalesce through `broadcast_aen_busy`/`broadcast_aen_pending`, topology delete events are prechecked, IR unhide/delete events are prechecked, SAS device internal reset events toggle `tm_busy`, temperature and active-cable events log immediately, and unsupported events return without queuing work. For queued events, the callback allocates `fw_event_work`, copies the firmware payload, attaches retry arrays for topology lists, and pushes the work onto `ioc->firmware_event_thread`.

The ordered workqueue calls `_mpt3sas_fw_work()`. It removes the event from the list, drops it if host removal or PCI recovery is active, then dispatches by event code. SAS and PCIe topology handlers can return a requeue request when device bringup returns retryable readiness states; the worker requeues those events after 1000 ms and keeps the event object alive. Other events are processed once and released.

PCIe topology add flow reads PCIe Device Page 0, validates presence/access status and device type, optionally reads PCIe Device Page 2 for NVMe-only metadata, waits for target readiness if configured, allocates `_pcie_device`, fills identity and enclosure fields, records NVMe transfer/shutdown/reset data, adds the object to either `pcie_device_init_list` during initial discovery or `pcie_device_list` for runtime add, then drops its local reference. Link-rate-change flow can turn into an add event if the existing device is absent but `pend_os_device_add` says the handle had a pending OS add. Removal flow calls the PCIe remove-by-handle helper and eventually `_scsih_pcie_device_remove_from_sml()`, which marks target data deleted, invalidates the handle, removes the SCSI target unless the device is firmware-blocked, and frees the serial number.

SAS broadcast primitive flow is more conservative. It serializes on `ioc->tm_cmds.mutex`, blocks all device I/O, and walks the outstanding SCSI lookup table under `scsi_lookup_lock`. It skips hidden RAID components, volumes, and PCIe devices. For each SAS command it temporarily drops the lookup lock to issue QUERY TASK. If firmware reports the I/O is still known/queued, it leaves it alone; otherwise it retries ABORT TASK up to a bounded count. Pending broadcast notifications cause the scan loop to restart before I/O is unblocked.

IR configuration flow maps firmware element reason codes to list and SCSI visibility operations. Native volume created/added events create `_raid_device` objects and may call `scsi_add_device()`. Native volume deleted/removed events mark/delete the target and remove it from SCSI. Physical-disk created/deleted/hide/unhide events toggle `pd_handles`, target RAID-component flags, volume linkage, fast-path enablement, SAS link state, and SCSI reprobe behavior. Foreign configs are logged but not used for volume add/delete.

Reset completion is split into two phases. `mpt3sas_scsih_reset_done_handler()` performs the immediate reconciliation after base reset: refresh multipath/HBA port data, mark every SCSI target deleted, rebuild enclosure state, scan config pages for SAS/PCIe/RAID/expander objects still present, and mark corresponding in-memory objects responding while refreshing handles and metadata. A later `MPT3SAS_REMOVE_UNRESPONDING_DEVICES` firmware work item waits until SCSI recovery is idle, removes unmarked objects, deletes dirty virtual PHY/port entries, updates queue depths for Gen3.5, and scans config pages to add newly visible devices. If reset occurred during driver load, the worker completes scanning itself so the watchdog and `is_driver_loading` state do not remain stuck.

Initial probe starts in `_scsih_probe()`. The PCI device ID selects MPI generation and therefore the SCSI host template and driver name. Probe allocates `Scsi_Host` with `struct MPT3SAS_ADAPTER` private data, initializes locks and lists, copies globally registered callback indices, configures host transport/protection limits, creates the firmware event workqueue, calls `mpt3sas_base_attach()` to initialize hardware/base resources, configures hide-drive and host-tagset queue policy, registers the host with SCSI, starts asynchronous scanning, and sets up debugfs. The SCSI scan callbacks kick off port enable, wait for discovery completion, handle fault/coredump reset cases, and eventually call `_scsih_probe_devices()` to move discovered devices from init lists to active lists/SCSI transport.

Removal and shutdown stop entry points before tearing down resources. `scsih_remove()` sets `remove_host`, flushes and destroys the firmware event workqueue, restores saved Aero config, sends IR shutdown, removes SAS host and all remaining RAID/PCIe/SAS/expander/port state, detaches base resources, releases control/debugfs state, unlinks the adapter globally, and releases the host. `scsih_shutdown()` uses similar event cleanup but sends both IR and NVMe shutdown, masks interrupts, stops the watchdog, soft-resets the IOC to a ready state, and frees interrupt resources rather than fully unregistering every object.

## State and Persistence

All state in this chunk is kernel runtime state or controller firmware state; it does not persist filesystem metadata directly. Important state includes:

- `struct MPT3SAS_ADAPTER` list heads for `sas_device_list`, `sas_device_init_list`, `sas_expander_list`, `enclosure_list`, `pcie_device_list`, `pcie_device_init_list`, `fw_event_list`, `raid_device_list`, `delayed_*` lists, `reply_queue_list`, and `port_table_list`.
- Spinlocks and mutexes guarding those objects: `sas_device_lock`, `pcie_device_lock`, `sas_node_lock`, `raid_device_lock`, `fw_event_lock`, `scsi_lookup_lock`, `tm_cmds.mutex`, `scsih_cmds.mutex`, reset/pci access locks, and diagnostic locks.
- Per-target flags in `struct MPT3SAS_TARGET`: `deleted`, `tm_busy`, handle, and flags such as `MPT_TARGET_FLAGS_RAID_COMPONENT`, `MPT_TARGET_FLAGS_VOLUME`, and `MPT_TARGET_FLAGS_PCIE_DEVICE`.
- Per-device identity and discovery fields: SAS address, WWID, handle, target ID, channel, enclosure handle/logical ID, slot, enclosure level, connector name, port, link state, fast-path capability, access status, reset timeout, NVMe MDTS, and NVMe shutdown latency.
- `responding` booleans used only as reset-reconciliation marks. Search helpers set them for objects still reported by firmware; removal clears surviving marks and prunes the rest.
- `pend_os_device_add` and `device_remove_in_progress` bitmaps, cleared during outstanding command reset cleanup and used to avoid duplicate add/remove races.
- `broadcast_aen_busy` and `broadcast_aen_pending`, which coalesce SAS broadcast primitives while a task-management cleanup loop is already running.
- `fw_event_work` reference counts, event payload copies, delayed work state, and per-topology-entry retry counters.
- `ioc->max_shutdown_latency`, initialized to a minimum and increased based on NVMe Page 2 shutdown latency; it bounds IO Unit Control shutdown wait time.
- Global module/session state: `mpt2_ids`, `mpt3_ids`, callback indices, SAS/RAID transport templates, PCI driver registration, and global `mpt3sas_ioc_list` membership.

The code intentionally copies back `ioc_pg1_copy` for Aero IOC devices during remove/shutdown so driver-modified IOC Page 1 settings do not carry across the next driver load. It also saves/restores PCI state through the base layer and PCI error paths outside this chunk.

## Dependencies and Integration Points

- Linux SCSI midlayer: `scsi_host_alloc()`, `scsi_add_host()`, `scsi_scan_host()`, `scsi_add_device()`, `scsi_remove_target()`, `scsi_block_requests()`, `scsi_unblock_requests()`, `scsi_device_reprobe()`, `shost_for_each_device()`, `starget_for_each_device()`, `scsi_host_template`, and error-handler callbacks.
- SAS transport class: `sas_attach_transport()`, `sas_release_transport()`, `sas_remove_host()`, and `mpt3sas_transport_*` link/port helpers.
- RAID class transport: `raid_class_attach()`, `raid_class_release()`, and `raid_function_template` callbacks for RAID state and resync percent.
- PCI core: `pci_driver`, `pci_device_id`, `pci_error_handlers`, `pci_restore_state()`, `pci_disable_link_state()`, PM ops, AER/EEH channel-state callbacks, shutdown/remove/probe callbacks, and device ID matching.
- mpt3sas base layer: callback registration/release, message frame allocation, SMID handling, hard reset, attach/detach, watchdog, resource map/free, IRQ/MSI-X free, interrupt masking, IOC ready transition, coredump handling, fault printing, config-page completions, and diagnostic trigger processing.
- mpt3sas config layer: reads/writes of PCIe Device Pages 0/2, SAS Device Page 0, Enclosure Page 0, Expander Pages 0/1, RAID Volume Pages 0/1, Physical Disk Page 0, volume handles/WWIDs, and Aero IOC Page 1 restoration.
- mpt3sas control/debugfs: `mpt3sas_ctl_init/exit/release`, `mpt3sas_setup_debugfs()`, `mpt3sas_destroy_debugfs()`, `mpt3sas_init_debugfs()`, and `mpt3sas_exit_debugfs()`.
- MPI firmware protocol constants and payload types: `Mpi2EventNotificationReply_t`, `Mpi26EventDataPCIeTopologyChangeList_t`, `Mpi26EventDataPCIeDeviceStatusChange_t`, `Mpi2EventDataSas*`, `Mpi2EventDataIr*`, `Mpi26PCIeDevicePage*`, `Mpi2SasDevicePage0_t`, `Mpi2Raid*`, `Mpi2Expander*`, and related status/reason macros.

## Risks and Edge Cases

- Topology add retry relies on per-entry `fw_event->retries` and delayed requeue. If an event is repeatedly retryable, discovery can be delayed; if retry arrays fail allocation in interrupt context, topology retries are lost.
- `_scsih_pcie_add_device()` sets `pend_os_device_add` early but does not clear it on several failure returns after the bit is set. Later code uses this bitmap to reinterpret link-rate changes as adds, so stale bits can affect event handling.
- Device-blocked PCIe/NVMe access status is treated as successful for internal list creation but intentionally not exposed through SCSI. This is correct for firmware policy, but any code assuming a listed `_pcie_device` has a `starget` must check access status.
- Reset reconciliation depends on stable matching keys: SAS address/slot/port for SAS devices, WWID/slot for PCIe devices, WWID for RAID, and SAS address/port for expanders. Firmware bugs or enclosure slot changes can cause remove/add churn rather than handle refresh.
- Many list transitions intentionally drop locks before calling SCSI or transport removal. Reference counts (`sas_device_get/put`, `pcie_device_get/put`) are critical; missing a reference in adjacent changes can produce use-after-free or leaks.
- Broadcast primitive handling holds `tm_cmds.mutex`, blocks all I/O, and can retry QUERY/ABORT loops. Bugs here can stall I/O globally or leave `broadcast_aen_busy` set if exit paths are changed incorrectly.
- Shutdown paths issue firmware commands through `scsih_cmds`. If another internal command is active, shutdown notification may be skipped after logging `scsih_cmd in use`.
- `_scsih_create_enclosure_list_after_reset()` uses GET_NEXT_HANDLE until config read failure/status break; malformed firmware enumeration can leave a partially rebuilt enclosure list.
- `scsih_scan_finished()` has long timeouts and hard reset branches for fault/coredump states. Probe behavior changes here can affect boot time and whether devices are registered during degraded firmware states.
- PCI probe returns literal `1` for invalid/tampered secure HBA IDs rather than a conventional negative errno. Callers generally treat nonzero as failure, but error-code expectations are unusual.
- Host-tagset queue mapping assumes default map has queues and uses `BUG_ON()` otherwise. Incorrect reply queue/high-I/O/poll queue counts during probe can panic rather than fail gracefully.
- Remove and shutdown destroy the firmware event workqueue after clearing `ioc->firmware_event_thread`; concurrent event callbacks must respect `remove_host` and queue cleanup to avoid use-after-free.
- Several debug strings and comments contain typos, but they do not change behavior. Tests that assert exact log messages should account for existing wording.

## Test Signals

Useful validation signals for this chunk include:

- PCI probe with representative MPI2, MPI2.5, MPI2.6, Gen3.5, Aero secure, invalid, tampered, WarpDrive, and Atlas PCIe switch device IDs selects the expected host template, flags, queue settings, and failure path.
- Driver load creates one ordered `fw_event_*` workqueue per adapter, registers the SCSI host, completes port enable, calls `_scsih_probe_devices()`, starts the watchdog, and clears `is_driver_loading`.
- PCIe/NVMe hot-add events create `_pcie_device` entries with correct WWID, channel, ID, handle, access status, enclosure fields, reset timeout, MDTS, and shutdown latency; blocked devices stay internal and are not added to SCSI.
- PCIe topology add retry path requeues while `_scsih_wait_for_target_to_become_ready()` returns retryable states and eventually clears or converts the topology entry.
- PCIe/SAS internal device reset status events set `tm_busy` at reset start and clear it at reset complete.
- SAS broadcast primitive testing shows I/O blocked, QUERY TASK issued for outstanding SAS end-device commands, ABORT TASK issued only when needed, pending AENs coalesced, and I/O unblocked.
- Enclosure add/remove events update `ioc->enclosure_list`; reset recovery rebuilds the list and refreshes device enclosure logical IDs, slots, enclosure levels, and connector names.
- IR config and state-change events add/delete RAID volumes, hide/expose physical disks, update `pd_handles`, and reprobe SCSI devices as expected.
- Host reset tests verify that responding devices keep their SCSI targets and have refreshed handles, while unresponding SAS/PCIe/RAID/expander objects are removed after SCSI recovery is idle.
- Post-reset scans add newly visible expanders, physical disks, volumes, SAS end devices, and PCIe devices without duplicating already active objects.
- Shutdown/suspend paths send NVMe IO Unit Control shutdown when PCIe devices exist, use the maximum observed shutdown latency, send IR shutdown for RAID volumes, stop the watchdog, and block/free resources in the correct order.
- PCI AER/EEH tests cover normal, frozen, and permanent-failure states: request blocking, watchdog stop, resource free, hard reset on slot reset, and request unblocking on resume.
- Module init/exit tests verify SAS/RAID transport template attach/release symmetry, callback index registration/release symmetry, control module init/exit, PCI driver registration/unregistration, and debugfs init/exit.
