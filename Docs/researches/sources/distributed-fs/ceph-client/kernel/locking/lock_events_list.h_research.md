# sources/distributed-fs/ceph-client/kernel/locking/lock_events_list.h

## Purpose
`lock_events_list.h` is an X-macro list of supported locking statistics. It is included once to generate enum values and again to generate debugfs names.

## Important APIs, Types, and Functions
It defines `LOCK_EVENT(name)` if not already defined, then lists conditional PV qspinlock events, queued spinlock events, resilient queued spinlock timeout, rwsem events, rtlock/rtmutex slowpath events, and lockdep events.

Representative events include `pv_hash_hops`, `pv_kick_unlock`, `lock_pending`, `lock_slowpath`, `lock_use_node2/3/4`, `lock_no_node`, `rqspinlock_lock_timeout`, `rwsem_sleep_reader`, `rwsem_wake_writer`, `rwsem_opt_fail`, `rtmutex_slowlock`, `rtmutex_deadlock`, `lockdep_acquire`, and `lockdep_nocheck`.

## Control Flow
There is no executable flow. Inclusion context determines whether each `LOCK_EVENT()` expands into an enum constant, string table entry, or another generated artifact. Configuration guards include or exclude PV and queued spinlock-specific events.

## State and Persistence Behavior
The file defines the compile-time event namespace. Runtime state is allocated by `lock_events.c`/`lock_events.h` based on the generated `lockevent_num`.

## Dependencies and Integration Points
It is integrated into `lock_events.h` and `lock_events.c`, and event names are referenced by locking code macros and debugfs output.

## Risks and Test Signals
Adding, reordering, or conditionally compiling events changes enum IDs and debugfs file lists. Because names double as debugfs filenames, they should remain stable and descriptive. Tests should build all relevant config combinations and verify debugfs names match event macro call sites.
