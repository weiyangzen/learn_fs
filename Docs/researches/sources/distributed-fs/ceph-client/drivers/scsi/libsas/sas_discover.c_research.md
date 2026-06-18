# sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_discover.c

## Purpose

`sas_discover.c` drives libsas domain discovery, device registration, unregistration, suspend/resume handling, and discovery work scheduling for SAS ports. It creates root domain devices from port-attached identify/FIS frames, delegates to end-device, SATA, or expander discovery, notifies low-level drivers, manages rphy lifetime, and cleans up devices after hotplug or port teardown.

## Important APIs, Types, and Functions

Device initialization and notification APIs include `sas_init_dev()`, `sas_notify_lldd_dev_found()`, `sas_notify_lldd_dev_gone()`, `sas_free_device()`, `sas_unregister_dev()`, `sas_unregister_domain_devices()`, `sas_destruct_devices()`, `sas_device_set_phy()`, and `sas_fail_probe()` integration. Discovery work functions are `sas_discover_domain()`, `sas_revalidate_domain()`, `sas_discover_event()`, and `sas_init_disc()`. Helpers include `sas_get_port_device()`, `sas_probe_devices()`, `sas_suspend_devices()`, `sas_resume_devices()`, `sas_destruct_ports()`, and `sas_abort_device_scsi_cmds()`.

The primary data structures are `struct asd_sas_port`, `struct asd_sas_phy`, `struct sas_discovery`, `struct sas_discovery_event`, `struct domain_device`, `struct sas_rphy`, `struct sas_ha_struct`, and low-level driver callbacks in `struct sas_internal`.

## Control Flow

A discovery event queues `sas_discover_domain()` on the discovery workqueue. If the port has no `port_dev`, `sas_get_port_device()` allocates a domain device, copies the received frame from the first port phy, classifies SATA versus SAS OOB, initializes type-specific fields, allocates the correct rphy, fills identify data, records link rates/pathways, sets the target on each port phy, and places the device on either the discovery list or device list. Root end devices and SATA devices are staged on `disco_list`; expanders go directly to `dev_list`.

`sas_discover_domain()` then delegates to `sas_discover_end_dev()`, `sas_discover_root_expander()`, or `sas_discover_sata()`. On failure it frees the rphy, removes list entries, drops the device, and clears `port_dev`. Regardless of initial result, `sas_probe_devices()` moves staged devices into `dev_list`, probes SATA links with libata, adds rphys to the SAS transport, and fails probes that cannot be surfaced.

Revalidation runs under `ha->disco_mutex`, skips active ATA EH by leaving the pending bit set, and calls `sas_ex_revalidate_domain()` for expander roots. After revalidation it destructs pending devices and ports and probes newly staged devices. Suspend work disables SATA devices, notifies low-level drivers that devices are gone, calls optional `lldd_port_deformed()` for each phy, and marks phys/port suspended. Resume work resumes SATA devices.

Unregistration marks devices destroyed, aborts in-flight SCSI commands for gone non-expander devices, unlinks rphys, moves devices to `destroy_list`, and later `sas_destruct_devices()` removes children, deletes rphys, notifies low-level drivers, removes list links, ends SATA EH if needed, and drops references. Root and child device references are balanced through krefs, rphy device refs, parent refs, and phy refs.

## State and Persistence Behavior

Discovery state is held in `port->port_dev`, `port->disc.pending`, `port->disco_list`, `port->dev_list`, `port->destroy_list`, `port->sas_port_del_list`, root discovery fields such as `fanout_sas_addr`, `eeds_a`, `eeds_b`, and `max_level`, and per-device state bits like `SAS_DEV_FOUND`, `SAS_DEV_DESTROY`, `SAS_DEV_GONE`, and `SAS_DEV_EH_PENDING`. No persistent storage is written; all state is in kernel memory and SAS transport devices.

## Dependencies and Integration Points

This file integrates with SCSI transport SAS rphy/port objects, libata helpers when SATA is enabled, low-level libsas driver callbacks `lldd_dev_found`, `lldd_dev_gone`, and `lldd_port_deformed`, block tagset busy iteration for fast abort on removal, and libsas expander discovery/revalidation. It relies on event queuing from `sas_event.c` and topology details from `sas_expander.c`.

## Risks and Edge Cases

Root device classification depends on the first phy's received frame and OOB mode; a PHY-down race returns `-ENODEV`. Discovery must handle devices that fail before `sas_rphy_add()` differently from devices already visible to the transport class. Reference balancing is subtle when low-level drivers accept devices and `SAS_DEV_FOUND` adds a kref. Revalidation is deferred during ATA EH to avoid conflicting with SATA resets; pending bits must be preserved so the event is replayed. Device removal with active I/O relies on aborting tagset commands quickly for gone devices.

## Test Signals

Signals include direct SAS end-device discovery, direct SATA discovery, root expander discovery, failed rphy allocation/add paths, low-level `lldd_dev_found()` rejection, hot-remove with active I/O aborts, revalidation deferral during ATA EH and replay after `sas_enable_revalidation()`, suspend/resume notifications, rphy unlink/delete order, and cleanup of devices that never reached `sas_rphy_add()`.
