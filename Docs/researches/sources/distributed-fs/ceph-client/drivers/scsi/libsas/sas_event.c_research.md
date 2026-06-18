# sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_event.c

## Purpose

`sas_event.c` provides libsas asynchronous event queuing, workqueue draining, deferred-event replay, runtime PM pairing, and revalidation gating around ATA error handling. It is the bridge between low-level PHY/port notifications and the libsas event/discovery workers.

## Important APIs, Types, and Functions

Exported or externally used APIs include `sas_queue_work()`, `sas_queue_deferred_work()`, `sas_drain_work()`, `sas_disable_revalidation()`, `sas_enable_revalidation()`, `sas_notify_port_event()`, and `sas_notify_phy_event()`. Internal helpers include `sas_queue_event()`, `__sas_drain_work()`, `sas_port_event_worker()`, `sas_phy_event_worker()`, and `sas_defer_event()`.

The key structures are `struct sas_ha_struct`, `struct sas_work`, `struct asd_sas_event`, `struct asd_sas_phy`, and HA state bits `SAS_HA_REGISTERED`, `SAS_HA_DRAINING`, `SAS_HA_RESUMING`, and `SAS_HA_ATA_EH_ACTIVE`.

## Control Flow

Low-level drivers call `sas_notify_port_event()` or `sas_notify_phy_event()`. The function allocates an event, takes a runtime PM reference with `pm_runtime_get_noresume()`, initializes the event work item with the appropriate worker and event ID, optionally defers events for new phys during resume, and queues the event under the HA lock. The worker dispatches through `sas_port_event_fns[event]` or `sas_phy_event_fns[event]`, drops the PM reference, and frees the event.

`sas_queue_work()` refuses events before registration, appends them to `ha->defer_q` while draining, or queues them to `ha->event_q`. `sas_drain_work()` serializes with `drain_mutex`, marks the HA draining, flushes submitters with a lock round trip, drains both event and discovery workqueues, clears draining, and requeues deferred work. If deferred work can no longer be queued, the code drops the PM reference and frees the event.

ATA EH calls `sas_disable_revalidation()` to set `SAS_HA_ATA_EH_ACTIVE` under `disco_mutex`. `sas_enable_revalidation()` clears the bit and scans all ports for pending domain revalidation; when found and a phy is present, it synthesizes a broadcast-received port event to replay the deferred topology check.

## State and Persistence Behavior

State is volatile and centered on HA workqueues, `defer_q`, HA state bits, and per-event allocations. Runtime PM references are paired across event allocation and worker/free paths. Revalidation deferral persists only as pending discovery bits and the `SAS_HA_ATA_EH_ACTIVE` HA bit.

## Dependencies and Integration Points

The file depends on libsas event function tables from internal code, kernel workqueues, runtime PM, HA locking, and discovery state in each port. It integrates tightly with `sas_discover.c` for revalidation events and with `sas_ata.c` for ATA EH deferral.

## Risks and Edge Cases

PM reference balancing is critical when an event is deferred, queued, rejected, or freed. During drain, the lock round trip is used to flush submitters before workqueue drain; incorrect locking would allow work to escape teardown. `sas_defer_event()` only defers during resume for phys not marked suspended, so resume sequencing depends on correct phy suspended flags. `sas_enable_revalidation()` synthesizes events only if a port has a phy; empty ports keep no replay target.

## Test Signals

Useful tests include notification before and after HA registration, event queueing during drain, deferred queue replay, failed requeue cleanup PM balance, runtime suspend/resume event deferral, ATA EH revalidation suppression and replay, and concurrent port/phy notifications while draining workqueues.
