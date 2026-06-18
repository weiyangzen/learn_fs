# sources/distributed-fs/ceph-client/tools/perf/util/lock-contention.h

## Purpose

`lock-contention.h` defines the data model and helper interface for perf's lock contention reporting, including classic trace-event state tracking and optional BPF-backed collection hooks.

## Important APIs, Types, and Functions

Core types are `struct lock_filter`, `struct lock_delay`, `struct lock_stat`, `struct lock_seq_stat`, `struct thread_stat`, `struct lock_contention_fails`, and `struct lock_contention`. `lock_stat` stores address, name, optional call stack, counts, flags, timing aggregates, and sorting/combine metadata. Sequence states define acquire/acquired/contended/released transitions. Public helpers include `parse_call_stack()`, `needs_callstack()`, `lock_stat_find()`, `lock_stat_findnew()`, and `match_callstack_filter()`. With `HAVE_BPF_SKEL`, BPF lifecycle functions are declared; without it, inline stubs return success or NULL.

## Control Flow

The header itself has no runtime flow. It defines the state machine values consumed by perf lock event handlers and provides compile-time selection between real BPF hooks and no-op fallbacks.

## State and Persistence Behavior

`lockhash_table` is declared as shared global storage. `lock_contention` carries command-level state: evlist, target, machine, filters, delays, fail counters, cgroup tree, BTF handle, stack settings, aggregation mode, owner mode, and saved call-stack behavior. `lock_seq_stat` instances persist per-thread in `thread_stat.seq_list` while matching event sequences.

## Dependencies and Integration Points

It depends on Linux list/rbtree infrastructure and perf `evlist`, `machine`, and `target` abstractions. It integrates with tracepoints such as `lock:contention_begin`, kernel lock type flags, cgroup filters, BPF skeleton code, and perf lock reporting/sorting code.

## Risks and Edge Cases

The imported constants (`MAX_LOCK_DEPTH`, contention stack skip/depth, and `LCB_F_*`) must remain compatible with kernel trace-event definitions. Sequence tracking must tolerate missing first events because perf records can begin mid-sequence or lose events. The no-op BPF stubs mean feature availability must be checked by build configuration and command behavior, not just successful function calls.

## Test Signals

Validation should exercise trace-event and BPF builds, lock sequence transitions, read and trylock flags, owner-stack extraction, filters by type/address/symbol/cgroup/slab, and aggregation modes. Header compile tests should cover `HAVE_BPF_SKEL` on and off.
