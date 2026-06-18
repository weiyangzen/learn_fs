# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_memcontrol.c

## Purpose

`test_memcontrol.c` is the main cgroup v2 memory controller selftest. It validates controller propagation, `memory.current`, peak reset semantics, min/low protection, high/max enforcement, synchronous throttling, reclaim, OOM events, swap peak, socket accounting, OOM group behavior, and inotify deletion events. The complete 1835-line file was read.

## Important APIs, Types, and Functions

Important globals are `has_localevents` and `has_recursiveprot`. Helpers include `get_temp_fd()`, `alloc_pagecache()`, `alloc_anon()`, `is_swap_enabled()`, `set_oom_adj_score()`, `alloc_anon_50M_check()`, `alloc_pagecache_50M_check()`, `alloc_pagecache_50M_noexit()`, `alloc_anon_noexit()`, `cg_test_proc_killed()`, `reclaim_until()`, `tcp_server()`, `tcp_client()`, and `read_event()`. Tests cover `subtree_control`, `current_peak`, `min`, `low`, `high`, `high_sync`, `max`, `reclaim`, `oom_events`, `swap_max_peak`, `sock`, three `oom_group_*` cases, and two inotify deletion cases.

## Control Flow

`main()` finds cgroup v2, verifies memory availability, enables memory at the root, reads mount options, and runs the table. Allocation helpers run in child cgroups and deliberately fault anonymous memory, page cache, socket buffers, or OOM workloads. Tests set memory knobs, trigger pressure or reclaim, read controller stats/events, and compare against expected values with tolerance.

## State and Persistence Behavior

The file creates cgroup trees, writes memory limits/protection/swap/OOM group knobs, creates temporary files via `O_TMPFILE`, allocates anonymous and page-cache memory, opens per-FD peak trackers, starts TCP sockets, sets `oom_score_adj`, and installs inotify watches. All kernel state is intended to be removed by cgroup destruction, child exit, and fd close.

## Dependencies and Integration Points

It depends on cgroup v2 memory controller files (`memory.current`, `memory.peak`, `memory.stat`, `memory.events`, `memory.min`, `memory.low`, `memory.high`, `memory.max`, `memory.reclaim`, `memory.swap.*`, `memory.oom.group`), cgroup mount options, IPv6 localhost sockets, inotify, OOM killer behavior, swap availability for swap tests, and `cgroup_util`.

## Risks and Edge Cases

Memory pressure tests are sensitive to available RAM, swap configuration, reclaim timing, rstat flushing, kernel feature availability, and host OOM policy. Peak reset tests depend on writable peak files and per-FD tracking support. Socket accounting relies on asynchronous `sock` stat drop and has polling slack. OOM event propagation differs with `memory_localevents`, and low event expectations differ with `memory_recursiveprot`.

## Test Signals

Strong signals include child cgroup controller visibility, current/peak values near 50M allocations, correct per-FD peak reset behavior, expected min/low protected reclaim values, `high` and `max` event increments, successful `memory.reclaim`, correct OOM and OOM kill counters, swap/memory peak reset behavior, socket memory matching `memory.stat sock`, OOM group killing scope, and inotify `IN_DELETE_SELF`/`IN_IGNORED` events on file and directory deletion.
