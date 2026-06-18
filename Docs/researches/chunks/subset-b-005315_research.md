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
