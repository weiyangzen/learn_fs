<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/taskstats_kern.h -->
# sources/distributed-fs/ceph-client/include/linux/taskstats_kern.h

## Purpose
declares kernel internals for the taskstats subsystem, including exit hooks and per-thread-group statistics cache handling.

## Important APIs, Types, and Functions
The file is 38 lines and exports these visible symbol families: types/enums none; macros/constants none; function-like macros none; inline helpers `taskstats_tgid_free`, `taskstats_exit`, `taskstats_init_early`; external prototypes `kmem_cache_free`, `taskstats_exit`, `taskstats_init_early`.

## Control Flow
When CONFIG_TASKSTATS is enabled, early init creates the cache, exit paths call `taskstats_exit()`, and signal teardown frees thread-group stats with `taskstats_tgid_free()`. Disabled builds use empty stubs.

## State and Persistence Behavior
State is in `taskstats_cache`, `taskstats_exit_mutex`, and optional `signal_struct::stats` allocations. The header only exposes lifecycle hooks.

## Dependencies and Integration Points
It depends on taskstats UAPI structures, scheduler signal state, slab allocation, and mutex protection in the implementation. Direct includes are `linux/taskstats.h`, `linux/sched/signal.h`, `linux/slab.h`.

## Risks and Edge Cases
Exit accounting is sensitive to group-dead ordering and locking. Failing to free `sig->stats` leaks memory, while racing netlink/taskstats queries against exit can expose partially updated data.

## Test Signals
Run taskstats netlink tests across single-threaded and thread-group exits, build CONFIG_TASKSTATS off, and check kmem-cache lifetime with slab debugging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/taskstats_kern.h -->
