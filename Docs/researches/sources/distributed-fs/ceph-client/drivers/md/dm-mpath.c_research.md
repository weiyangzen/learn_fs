
# sources/distributed-fs/ceph-client/drivers/md/dm-mpath.c

## Purpose
Implements the device-mapper `multipath` target. It routes I/O across multiple paths grouped into priority groups, delegates path choice to pluggable path selectors, integrates SCSI device handlers for path-group activation, handles failover/reinstatement, supports request-based and bio-based queue modes, and exposes messages/status/ioctls for multipath management.

## Important APIs, Types, And Functions
`struct pgpath` wraps a `dm_path`, active flag, fail count, owning priority group, and activation work. `struct priority_group` owns a `path_selector` and path list. `struct multipath` tracks flags, current/next PG/path, valid path count, queue mode, hardware-handler settings, work items, queued bios, wait queues, and no-path timer. Constructor parsing is split across `parse_features()`, `parse_hw_handler()`, `parse_priority_group()`, `parse_path_selector()`, and `parse_path()`. Mapping uses `multipath_clone_and_map()` for request-based mode and `multipath_map_bio()`/`__multipath_map_bio()` for bio mode. Path state changes use `fail_path()`, `reinstate_path()`, `bypass_pg()`, `switch_pg_num()`, and `pg_init_done()`.

## Control Flow
Constructor parses feature arguments, chooses queue mode, attaches path selectors/devices, initializes SCSI device-handler activation where needed, and sets the initial priority group. Mapping selects `current_pgpath` or calls `choose_pgpath()`, queues/requeues if path-group initialization is needed or no paths are available, and invokes selector `start_io`. End I/O reports selector `end_io`, fails paths on transport errors, and requeues or completes based on queue-if-no-path and valid-path state. Workqueues resubmit queued bios, run path activation, and trigger dm events.

## State And Persistence
All state is runtime only: flags, valid path counts, fail counts, selected PG/path, queued bios, handler activation counters, and timer state. There is no disk metadata. Userspace multipathd or dm table reloads are responsible for persistent policy.

## Dependencies And Integration Points
Depends on dm core target hooks, request-based dm-rq, per-bio metadata, path-selector registry, SCSI device handler APIs, block-mq request allocation, uevents, workqueues, timers, module parameters, and dm ioctl command `DM_MPATH_PROBE_PATHS`.

## Risks
Concurrency is complex: spinlocks, atomics, workqueues, timers, and suspend paths coordinate path switching and queued I/O. Incorrect queue-if-no-path handling can hang I/O indefinitely or fail I/O prematurely. Hardware handler activation may need retries and delayed switching. Bio-based queued bios require saved/restored bio details. Path selector callbacks must be balanced for start/end I/O. `queue_if_no_path_timeout_secs` changes failure behavior globally.

## Test Signals
Exercise both `queue_mode rq/mq` and `queue_mode bio`, path selector modules, no-path queueing and timeout, fail/reinstate/switch/disable/enable messages, SCSI handler success/retry/temp-busy/offline errors, suspend/resume with and without noflush, path probing ioctl, path failure during map/end I/O, status/IMA output, and concurrent path changes under load.
