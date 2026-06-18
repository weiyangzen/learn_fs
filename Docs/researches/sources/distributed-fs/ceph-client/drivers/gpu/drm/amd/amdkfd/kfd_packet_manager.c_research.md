
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_packet_manager.c

## Purpose
Provides the generic packet-manager layer that sends scheduler PM4 commands through the HIQ kernel queue and builds runlist IBs from DQM process/queue lists. ASIC-specific packet layouts are supplied by `packet_manager_funcs`.

## Important APIs, types, and functions
- `pm_init` selects VI, v9, or Aldebaran packet builders and initializes the HIQ kernel queue.
- `pm_send_set_resources`, `pm_send_runlist`, `pm_send_query_status`, `pm_send_unmap_queue`, and `pm_config_dequeue_wait_counts` serialize scheduler commands.
- `pm_create_runlist_ib` emits map-process and map-queue packets into a GTT IB.
- `pm_calc_rlib_size` computes IB size and oversubscription flags.
- `pm_release_ib` frees the active runlist IB.

## Control flow
`pm_init` selects the function table from ASIC type or GC version, creates a HIQ kernel queue, and initializes `pm->lock`. Command senders acquire the lock, reserve packet space from the kernel queue, call the ASIC builder, and submit or roll back. Runlist submission first allocates a runlist IB, writes process and queue packets grouped by XNACK mode, optionally appends a chained runlist packet for oversubscription, then submits a top-level runlist packet through HIQ.

## State and persistence behavior
`struct packet_manager` holds the selected vtable, HIQ queue, active IB memory object, allocation state, IB size, oversubscription flag, and lock. The runlist IB remains allocated after successful submission until `pm_release_ib`, allowing debugfs inspection of the active runlist. The manager does not persist user queues itself; it reflects DQM lists and counters at build time.

## Dependencies and integration points
Depends on DQM counters and queue lists, `struct qcm_process_device`, kernel queue packet-buffer APIs, GTT suballocation, ASIC-specific packet managers, and `kfd_priv.h` PM declarations. Debugfs can dump the active runlist or intentionally submit malformed data to hang HWS in debug builds.

## Risks
Runlist size depends on DQM counters matching actual list contents; stale counts can lead to overflow, underallocation, or `-ENOMEM`. Mixed XNACK processes cause a two-pass runlist and chained mode on affected GPUs. All command senders require correct rollback on builder failure. `pm->allocated` is single-IB state, so missing `pm_release_ib` blocks future allocation.

## Test signals
Test runlist generation for no queues, multiple processes, SDMA/static/user queues, oversubscription, and mixed XNACK. Inject kernel-queue allocation failure and ASIC builder errors to validate rollback. Verify debugfs runlist dump, set-resources, query-status fence completion, unmap filters, and dequeue-wait configuration on supported GC versions.
