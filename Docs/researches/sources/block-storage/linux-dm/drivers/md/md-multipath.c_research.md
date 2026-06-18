# File Research: sources/block-storage/linux-dm/drivers/md/md-multipath.c

## Purpose
Implements the deprecated MD `multipath` personality, routing I/O over one of several equivalent block-device paths and retrying failed non-readahead I/O on another path.

## Main Interfaces
- Path selection and request handling: `multipath_map()`, `multipath_make_request()`, `multipath_end_request()`, `multipath_end_bh_io()`.
- Retry handling: `multipath_reschedule_retry()`, `multipathd()`.
- Error and membership: `multipath_error()`, `multipath_add_disk()`, `multipath_remove_disk()`.
- Lifecycle/status/size: `multipath_run()`, `multipath_free()`, `multipath_status()`, `multipath_size()`.
- Registered personality: `multipath_personality`.

## Control Flow
`multipath_run()` validates level and no-bitmap state, allocates `mpconf` and the path array, records valid rdevs, counts working paths, sets degraded count, initializes a mempool of retry buffers, starts the `multipathd` thread, sets size, and registers integrity.

`multipath_make_request()` handles flushes through MD flush logic, allocates a `multipath_bh`, selects the first in-sync non-faulty path under RCU while incrementing `nr_pending`, clones the bio into the embedded bio, remaps it by the selected rdev’s data offset, sets failfast transport, and submits it.

On completion, successful bios complete the master bio and free the mempool object. Failed non-readahead bios call `md_error()`, log the sector, and place the request on `retry_list`; readahead failures complete as errors. `multipathd()` drains retry entries, selects another path, remaps the embedded bio again, and resubmits or reports unrecoverable failure.

## State And Synchronization
`mpconf` stores the path array, raid disk count, device lock, retry list, and mempool. Path pointer reads use RCU. `device_lock` protects degraded updates and retry-list manipulation. Rdev pending counts prevent hot-remove while I/O is active.

## Integration Points
Uses MD core flush handling, error handling, recovery checks, integrity registration, thread registration, hot add/remove hooks, disk limit stacking, write-same/write-zeroes checks, and MD personality registration.

## Notable Behaviors
- Path selection is simple first-available selection; comments mention future read balancing but none is implemented.
- Only non-readahead failed I/O is retried.
- `multipath_error()` refuses to disable the last remaining path.
- Hot-remove refuses operational paths or paths with pending I/O unless removal is synchronized.
- Hot-add installs the rdev with RCU assignment and decrements degraded count.

## Risks And Review Focus
- Retry bio reinitialization copies the master bio back into the embedded bio; preserving completion/private fields afterward is critical.
- Failure and removal paths depend on `nr_pending` and RCU ordering to avoid use-after-free.
- The personality is deprecated and much simpler than DM multipath; assumptions should not be generalized to modern multipath behavior.
