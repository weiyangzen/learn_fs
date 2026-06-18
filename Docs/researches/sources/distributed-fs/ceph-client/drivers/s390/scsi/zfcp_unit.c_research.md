# sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_unit.c

Purpose: manages manually configured zfcp LUN objects and bridges them to the SCSI midlayer. It creates per-port unit devices, queues/manual scans matching FCP LUNs, looks up units and associated SCSI devices, and removes units cleanly.

Important APIs/types/functions: `zfcp_unit_scsi_scan()` converts a zfcp unit FCP LUN to a SCSI LUN and calls `scsi_scan_target()`. `zfcp_unit_queue_scsi_scan()` queues scan work for all units on a port. `zfcp_unit_find()` returns a referenced unit by FCP LUN. `zfcp_unit_add()` allocates/registers a unit device and scans it. `zfcp_unit_sdev()` and `zfcp_unit_sdev_status()` resolve the live `struct scsi_device`. `zfcp_unit_remove()` deletes the unit, removes any SCSI device, and unregisters the unit device.

Control flow: a new unit is added under `zfcp_sysfs_port_units_mutex`, first rejecting ports marked removing and duplicate LUNs. The unit is initialized with sysfs groups and scan work, registered as a child of the port device, counted in `port->units`, inserted under `unit_list_lock`, and then scanned outside the mutex to preserve the documented lock order. Removal takes the unit list write lock, finds and deletes the unit, removes the backing SCSI device if present, unregisters the unit device, and drops the lookup reference.

State and persistence: unit state is a kernel device object with FCP LUN, parent port pointer, list node, and delayed scan work. The unit count on the parent port is decremented in `zfcp_unit_release()`. No persistent storage is used; configured units exist for the lifetime of the zfcp port/device instance.

Dependencies and integration: depends on zfcp port lists, zfcp sysfs attribute groups, FC rport state, SCSI scan/remove APIs, and `zfcp_sysfs_port_units_mutex` from `zfcp_sysfs.c`. The workqueue path uses the adapter's SCSI host queue.

Risks and test signals: scan work holds a device reference and must always drop it when queueing fails or work completes. `zfcp_unit_add()` deliberately unlocks before scanning to avoid `scan_mutex` inversion, so tests should cover port/rport state changing immediately after insertion. Removal deletes the unit from the zfcp list before SCSI device removal, so concurrent lookup and sysfs status reads depend on device references. Test duplicate add, add while port is removing, scan with offline/missing rport, remove nonexistent LUN, remove while SCSI device exists, queue work failure, and reference count release after unregister.
