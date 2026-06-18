# sources/distributed-fs/ceph-client/drivers/scsi/libsas/sas_internal.h

## Purpose
`sas_internal.h` is the private coordination header for libsas implementation files. It centralizes shared prototypes, task-to-SCSI-command helpers, per-phy transport callback state, device/rphy helper inlines, event dispatch declarations, and conditional SATA stubs.

## Important APIs, types, and functions
- `TO_SAS_TASK` and `ASSIGN_SAS_TASK` store and retrieve `struct sas_task *` through `scsi_cmnd.host_scribble`, tying SCSI command lifetime to libsas task lifetime.
- `struct sas_phy_data` is per-transport-phy hostdata used by `sas_init.c` to queue reset and enable operations onto libsas workqueues, carrying the target `struct sas_phy`, an `event_lock`, requested operation parameters, result slots, and `sas_work` items.
- Discovery, domain, and device prototypes include `sas_discover_root_expander`, `sas_ex_revalidate_domain`, `sas_unregister_domain_devices`, `sas_init_disc`, `sas_discover_event`, `sas_init_dev`, and `sas_unregister_dev`.
- Registration prototypes expose `sas_register_phys`, `sas_unregister_phys`, `sas_register_ports`, and `sas_unregister_ports`.
- Event plumbing includes `sas_alloc_event`, `sas_free_event`, `sas_phy_event_fns`, `sas_port_event_fns`, `sas_queue_work`, `__sas_drain_work`, and individual port-event worker prototypes.
- SMP and expander helpers include `sas_smp_handler`, `sas_smp_phy_control`, `sas_smp_get_phy_events`, `sas_ex_to_ata`, `sas_ex_phy_discover`, and attached-device lookup helpers.
- `sas_fill_in_rphy` copies libsas `domain_device` identity into transport `sas_rphy` identity, mapping SATA-like end devices to `SAS_END_DEVICE`.
- `sas_phy_set_target` updates a local transport phy identity to reflect the attached target or clears it to unused.
- `sas_alloc_device` initializes a zeroed `domain_device` with sibling/discovery list heads, a kref, and `done_lock`; `sas_put_device` releases via `sas_free_device`.
- The `CONFIG_SCSI_SAS_ATA` section declares real SATA integration or provides no-op/failing stubs with a once-only notice when SATA support is disabled.

## Control flow and state
The header defines the internal contracts that allow libsas files to call across module boundaries without exposing these helpers as public UAPI. Most control-flow coupling is asynchronous: discovery and port/phy events are queued as `sas_work`; SCSI EH paths call into recovery and task-management helpers; transport sysfs operations use `struct sas_phy_data` to serialize workqueue execution.

## State and persistence behavior
No persistent storage is declared. State is held in kernel structures, lists, krefs, spinlocks, mutexes, and SCSI transport objects. `host_scribble` is a transient pointer slot and must be cleared when tasks complete or are transferred to EH ownership.

## Dependencies and integration points
The header depends on SCSI core headers, `scsi_transport_sas`, public `<scsi/libsas.h>`, libata SAS headers, and runtime PM. It is included by libsas implementation files and indirectly binds them to LLDD-provided `sas_domain_function_template` callbacks.

## Risks and edge cases
- `TO_SAS_TASK`/`ASSIGN_SAS_TASK` require exclusive ownership of `host_scribble`; other SCSI host code must not reuse it.
- Inline address matching casts SAS address bytes through `SAS_ADDR`; all callers rely on correctly populated 8-byte addresses.
- `sas_fail_probe` unregisters devices directly after logging, so callers must not continue using the `domain_device` without holding references.
- SATA-disabled stubs return success for some lifecycle hooks but fail discovery/add-device operations, so test matrices must include `CONFIG_SCSI_SAS_ATA=n`.

## Test signals
- Build coverage with and without `CONFIG_SCSI_SAS_ATA` and `CONFIG_SCSI_SAS_HOST_SMP`.
- Static analysis should verify every `ASSIGN_SAS_TASK(cmd, task)` has a clear/free path.
- Discovery tests should confirm rphy identity fields and phy target fields match domain-device type/protocol transitions.
