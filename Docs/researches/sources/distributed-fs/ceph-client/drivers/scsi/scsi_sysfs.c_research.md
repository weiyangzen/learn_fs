# sources/distributed-fs/ceph-client/drivers/scsi/scsi_sysfs.c

## Purpose

`scsi_sysfs.c` implements the SCSI bus, SCSI device class, host/device sysfs attributes, SCSI driver registration, device publication, and removal paths. It is the main bridge between discovered `scsi_device`/`scsi_target` objects and the Linux driver model.

## Important APIs, types, and functions

Exported or cross-file APIs include `scsi_device_state_name()`, `scsi_host_state_name()`, `scsi_bus_type`, `scsi_sysfs_register()`, `scsi_sysfs_unregister()`, `scsi_sysfs_add_sdev()`, `__scsi_remove_device()`, `scsi_remove_device()`, `scsi_remove_target()`, `__scsi_register_driver()`, `scsi_register_interface()`, `scsi_sysfs_add_host()`, `scsi_sysfs_device_initialize()`, `scsi_is_sdev_device()`, `scsi_shost_groups`, and `blank_transport_template`.

Host attributes include scan, host state, supported/active mode, reset, EH deadline, queue/SG/protection limits, busy count, proc name, blk-mq state, and hardware queue count. Device attributes include type, SCSI level, vendor/model/rev, busy/blocked counts, timeouts, rescan/delete/state, queue depth/type/ramp-up, VPD and inquiry binary data, I/O counters, modalias, events, WWID, serial, blacklist flags, device-handler state, access state, preferred path, and CDL support/enablement.

## Control flow

`scsi_sysfs_register()` registers the `scsi` bus and the `scsi_device` class; unregister reverses that order. The bus match function only binds true SCSI device objects, rejects `no_uld_attach`, and requires connected peripheral qualifier. Bus probe/remove/shutdown delegate to `struct scsi_driver` callbacks. `__scsi_register_driver()` fills in legacy wrapper callbacks when a driver supplied generic driver callbacks instead of SCSI-specific ones, then registers the driver on `scsi_bus_type`.

Host sysfs `scan` parses `channel id lun` strings and calls the transport `user_scan()` hook or `scsi_scan_host_selected(..., SCSI_SCAN_MANUAL)`. Host reset and EH deadline attributes call low-level template hooks or update host fields under `host_lock`.

`scsi_sysfs_device_initialize()` initializes the generic SCSI device and class device, names both with `host:channel:id:lun`, attaches default groups, configures initial LUN-in-CDB behavior, sets up transport state, links the device into host and target lists, and increments the target reap reference. `scsi_sysfs_add_sdev()` ensures the target is visible, enables PM, attaches device handlers, adds the generic device and class device, adds transport state, marks the device visible, and optionally registers a BSG queue.

Removal begins with `scsi_remove_device()` taking `scan_mutex` and calling `__scsi_remove_device()`. The internal remover makes visible devices cancel/deleted, unregisters BSG, unregisters the class device, removes transport/sysfs visibility, destroys the request queue, releases tag-set references, cancels requeue work, invokes low-level `sdev_destroy()`, destroys transport state, reaps the target, and puts the final device reference. Target removal walks host devices matching the target and removes each before reaping target visibility.

## State and persistence behavior

This file persists driver-model state: registered bus/class, sysfs attribute groups, generic devices, class devices, target visibility, runtime PM enablement, BSG queues, transport devices, and list membership. Device release frees request queues, budget maps, inquiry data, events, and VPD pages using RCU replacement/freeing. Sysfs stores mutate live SCSI state such as device state, queue timeouts, queue depth, event support bits, EH deadlines, runtime scan results, device-handler state, and CDL enablement.

## Dependencies and integration points

The file depends on the Linux device model, class/bus APIs, block queues, PM runtime, BSG, SCSI hosts/devices/drivers/device handlers/transports/devinfo, and `scsi_priv.h`. It is tightly coupled with `scsi_scan.c` for device initialization/publication/removal, `scsi_pm.c` for `scsi_bus_pm_ops`, low-level driver templates for host/device callbacks, upper-level SCSI drivers for bus binding, and transport classes for transport setup/add/remove/configure/destroy.

## Risks and edge cases

Sysfs store paths are user-facing mutation points and need strict parsing and state checks. Delete uses `sysfs_break_active_protection()` to safely remove the active attribute while handling concurrent writes; changing that path risks deadlocks or duplicate removal. Removal is not reentrant beyond the explicit `SDEV_DEL` guard and depends on state transitions to stop new I/O before queue teardown. VPD pages are RCU-protected and must be replaced under `inquiry_mutex` before delayed free. Attribute visibility depends on feature availability and populated VPD pointers. Host and device state name helpers return `NULL` for unknown states, so callers must handle invalid states.

## Test signals

Tests should cover bus/class registration, SCSI driver binding and legacy callback wrapping, host sysfs scans/resets/deadline updates, device state transitions, timeout and queue-depth stores, VPD/inquiry binary reads, event toggles, blacklist rendering, device handler attributes, CDL enablement, BSG registration failures, and repeated add/remove cycles. Concurrency tests should write `delete` multiple times, remove targets while scanning, read VPD while pages are freed, and exercise removal with pending queue/requeue work. Build tests should cover `CONFIG_PM`, `CONFIG_SCSI_DH`, and `CONFIG_BLK_DEV_BSG` combinations.
