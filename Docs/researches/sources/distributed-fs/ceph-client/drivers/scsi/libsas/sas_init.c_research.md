# sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_init.c

## Purpose
`sas_init.c` is the libsas transport initialization and host-adapter control glue. It allocates the core task and event caches, registers and unregisters SAS HAs, binds libsas callbacks into the SCSI SAS transport template, exposes transport operations for phy reset/enable/link-rate/error counters, and coordinates HA suspend/resume with libsas workqueues and SCSI request blocking.

## Important APIs, types, and functions
- `sas_alloc_task`, `sas_alloc_slow_task`, and `sas_free_task` allocate libsas `struct sas_task` objects from `sas_task_cache`; slow tasks additionally allocate `struct sas_task_slow`, initialize a timer and completion, and are used by internal TMF paths in `sas_scsi_host.c`.
- `sas_hash_addr` computes the 24-bit SAS address hash with polynomial `0x00DB2777` and stores it in `sas_ha->hashed_sas_addr`.
- `sas_register_ha` initializes `sas_ha_struct` locks, queues, lists, state flags, event threshold, phys, ports, and ordered event/discovery workqueues.
- `sas_unregister_ha` disables event ingress, unregisters ports, drains pending work, and destroys discovery/event workqueues.
- `transport_sas_phy_reset`, `sas_phy_enable`, `sas_phy_reset`, and `sas_set_phy_speed` implement SAS transport callbacks by dispatching either to LLDD `lldd_control_phy` for local phys or SMP helper paths for expander phys.
- `sas_try_ata_reset` routes non-hard-reset SATA links through libata EH when a probed SATA `domain_device` is attached.
- `sas_prep_resume_ha`, `sas_resume_ha`, `sas_resume_ha_no_sync`, and `sas_suspend_ha` coordinate host power-state transitions, stale event cleanup, request blocking/unblocking, suspended-phy timeout handling, deferred work replay, and expander broadcast revalidation.
- `queue_phy_reset` and `queue_phy_enable` run user-requested transport operations in libsas workqueue context under runtime PM and `sas_phy_data.event_lock`.
- `sas_domain_attach_transport` creates the SAS transport template, stores the LLDD `sas_domain_function_template`, enables a transport workqueue, and installs `sas_scsi_recover_host` as the EH strategy.
- `sas_alloc_event` and `sas_free_event` manage event cache entries and per-phy event throttling. Bursty event production can schedule `PHYE_SHUTDOWN` or refuse allocation when LLDD phy control is unavailable.

## Control flow and state
HA registration follows an unwind-safe sequence: initialize locks/lists and set `SAS_HA_REGISTERED`, register phys, register ports, allocate `event_q`, allocate `disco_q`, then initialize EH queues. Failure destroys only the resources already acquired. Unregistration clears `SAS_HA_REGISTERED` under `sas_ha->lock`, drains work under `drain_mutex`, unregisters ports, drains again, and finally destroys workqueues.

Transport phy operations split on `scsi_is_sas_phy_local()`. Local phys retrieve `asd_sas_phy` from `sas_ha->sas_phy[phy->number]` and call LLDD control hooks. Remote expander phys resolve `sas_rphy` to `domain_device` and use SMP helpers. Link reset paths prefer libata-managed reset for SATA devices when the operation is not a hard reset.

Suspend clears event acceptance, blocks SCSI requests, emits `DISCE_SUSPEND` on every port, and drains suspend work while unregistered. Resume marks the HA registered and resuming, clears stale `attached_sas_addr` and frame data, waits up to 25 seconds for suspended phys, emits `PHYE_RESUME_TIMEOUT` for late phys, unblocks SCSI, optionally drains work, clears `SAS_HA_RESUMING`, queues deferred work, and broadcasts revalidation to expander ports.

## State and persistence behavior
State is in kernel memory only: kmem caches, `sas_ha_struct` flags/lists/workqueues, `asd_sas_phy` frame/event counters, and sysfs-visible `event_thres`. There is no disk persistence. `phy_event_threshold_store` updates `sas_ha->event_thres` from sysfs and clamps values below 32. Runtime PM references are taken around queued user phy operations.

## Dependencies and integration points
This file depends on the SCSI transport SAS layer (`sas_attach_transport`, `sas_phy_*`, `sas_port_*`), libata integration (`sas_ata_schedule_reset`, `sas_ata_wait_eh`), SMP helpers in libsas discovery code, LLDD callbacks in `sas_domain_function_template`, and shared declarations in `sas_internal.h`. It exports symbols used by low-level SAS drivers and other libsas modules.

## Risks and edge cases
- Event throttling depends on balanced `sas_alloc_event`/`sas_free_event`; leaks keep `event_nr` elevated and can trigger unnecessary phy shutdown.
- `queue_phy_reset` and `queue_phy_enable` assume `phy->hostdata` was initialized by `sas_phy_setup`; missing setup returns `-ENOMEM`.
- SATA reset routing requires a successfully probed `domain_device`; otherwise reset falls back to SAS/SMP control.
- Resume timeout handling intentionally races with late LLDD resume events and rechecks `phy->suspended` in the event worker.
- `sas_set_phy_speed` mutates the caller-provided link-rate structure to hardware min/max bounds before dispatching.

## Test signals
- Module load/unload should create and destroy `sas_task` and `asd_sas_event` caches without leaks.
- HA register failure injection should unwind phys, ports, and workqueues cleanly.
- Sysfs phy reset/enable paths should run in libsas workqueue context and return LLDD/SMP errors.
- SATA link reset should exercise libata EH rather than direct LLDD reset for non-hard resets.
- Suspend/resume tests should show request blocking, deferred work replay, timeout event emission, and expander broadcast revalidation.
