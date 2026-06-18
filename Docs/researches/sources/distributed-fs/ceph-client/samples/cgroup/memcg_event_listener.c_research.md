<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/cgroup/memcg_event_listener.c -->
# sources/distributed-fs/ceph-client/samples/cgroup/memcg_event_listener.c

## Purpose
`memcg_event_listener.c` is a cgroup v2 memory event listener. It reads `/sys/fs/cgroup/<cgroup>/memory.events`, stores baseline counters, watches the file with inotify, and prints counter deltas when memory events occur.

## Important APIs, Types, And Functions
Important types are `struct memcg_counters` and `struct memcg_events`. Functions include `print_memcg_counters()`, `get_memcg_counter()`, `read_memcg_events()`, `process_memcg_events()`, `monitor_events()`, `initialize_memcg_events()`, `cleanup_memcg_events()`, and `main()`.

## Control Flow
Initialization builds the memory.events path, reads baseline counters, creates an inotify fd, and watches for `IN_MODIFY`. `monitor_events()` polls forever, reads inotify events, validates watch descriptor and mask, then calls `read_memcg_events(show_diff=true)`. The reader parses expected lines in order, compares new values to old values, prints deltas, and updates stored counters.

## State And Persistence
Persistent process state is the path, inotify fd/watch descriptor, and last-seen counters. Kernel cgroup counters persist independently in cgroupfs.

## Dependencies And Integration Points
It depends on cgroup v2 `memory.events`, inotify, poll, and the exact counter names `low`, `high`, `max`, `oom`, `oom_kill`, and `oom_group_kill`.

## Risks And Edge Cases
The parser expects counters in fixed order; cgroup files are generally stable but extensions could require changes. Cleanup after `monitor_events()` is unreachable because the monitor loops forever. Counter decreases are ignored, which is appropriate for monotonic event counters.

## Test Signals
On startup it prints initialized counters. Memory pressure or OOM events should produce `Received event` followed by delta lines for increased counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/cgroup/memcg_event_listener.c -->
