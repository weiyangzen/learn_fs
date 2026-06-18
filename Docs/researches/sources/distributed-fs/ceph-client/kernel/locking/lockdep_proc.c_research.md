# sources/distributed-fs/ceph-client/kernel/locking/lockdep_proc.c research

## Purpose
`lockdep_proc.c` exposes lockdep state through procfs. It implements `/proc/lockdep` for lock classes and direct dependencies, `/proc/lockdep_chains` for cached dependency chains when proving is enabled, `/proc/lockdep_stats` for aggregate counters and capacity use, and `/proc/lock_stat` for contention and timing statistics when `CONFIG_LOCK_STAT` is enabled.

## Important APIs, Types, and Functions
The class iterator is built from `l_start()`, `l_next()`, `l_stop()`, `l_show()`, and `lockdep_ops`. It iterates directly over `lock_classes[]` from index zero through `max_lock_class_idx` and filters with `lock_classes_in_use`, avoiding `all_lock_classes` because class lists can move to free or zapped lists while proc iteration is lockless.

`print_name()` mirrors lockdep's class-name formatting: key symbol fallback, name-version suffix, and subclass suffix. `l_show()` prints class key, optional debug operation count, forward/backward dependency counts, usage characters, class name, and direct `locks_after` edges when proving is enabled.

With `CONFIG_PROVE_LOCKING`, `lc_start()`, `lc_next()`, `lc_show()`, and `lockdep_chains_ops` expose `lock_chains[]`. They use `lockdep_next_lockchain()` to skip unused entries and `lock_chain_get_class()` to recover classes from compact chain storage.

`lockdep_stats_show()` aggregates usage masks across classes and prints high-level resource and classification counters. With `CONFIG_LOCK_STAT`, `lock_stat_open()` snapshots all active classes with `lock_stats()`, sorts by total contentions via `lock_stat_cmp()`, and installs the snapshot as seq private data. `seq_stats()` formats wait/hold time, bounces, contention points, and contending points. `lock_stat_write()` clears stats when users write `0`.

## Control Flow
`lockdep_proc_init()` registers all proc entries at init time. Reads of `/proc/lockdep` and `/proc/lockdep_chains` stream live arrays through seq_file. Reads of `/proc/lockdep_stats` calculate a fresh aggregate on each call. Reads of `/proc/lock_stat` first allocate and populate a stable sorted snapshot during open, then seq iteration formats that snapshot; release frees it. Writes to `/proc/lock_stat` do not parse full strings: a first byte of `'0'` clears all active class stats and other input is ignored as a no-op success.

## State and Persistence Behavior
This file owns no persistent lockdep graph state. Its only per-open state is the `vmalloc()`ed `struct lock_stat_seq` snapshot for `/proc/lock_stat`. All other output is a view over globals owned by `lockdep.c`. Because class and chain iteration is mostly lockless, output is diagnostic and can race with class zapping or graph mutation, but the implementation avoids the most dangerous list traversal by walking arrays and RCU-compatible chain helpers.

## Dependencies and Integration Points
The file depends on `proc_fs`, `seq_file`, `kallsyms`, `debug_locks`, `vmalloc`, `sort`, `uaccess`, division helpers, and `lockdep_internals.h`. It consumes `lock_stats()` and `clear_lock_stats()` from `lockdep.c` under `CONFIG_LOCK_STAT`. It is the main user-facing visibility layer for the lockdep engine and is commonly used in bug reports after lockdep warnings.

## Risks and Edge Cases
Proc output is not a synchronized snapshot except for `/proc/lock_stat`; classes can change while a read is in progress. `seq_stats()` intentionally returns early if both class name and key are unavailable, which can hide a zapped class from lock-stat output. The class-name buffer truncates long names and has comments noting version/subclass truncation limitations. `lock_stat_open()` allocates a `MAX_LOCKDEP_KEYS`-sized snapshot with `vmalloc`, so low-memory conditions can fail reads with `-ENOMEM`.

## Test Signals
Expected proc entries are `lockdep`, `lockdep_stats`, optionally `lockdep_chains`, and optionally `lock_stat`. Test signals include sane class counts, dependency counts matching active lockdep workloads, nonzero debug counters under `CONFIG_DEBUG_LOCKDEP`, sorted contention rows under lock-stat workloads, and successful clearing of stats by writing `0` to `/proc/lock_stat`.
