# subset-b-006037 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/lockdep.c -->
## sources/distributed-fs/ceph-client/kernel/locking/lockdep.c

### Purpose
`lockdep.c` is the kernel runtime locking correctness validator. It records lock classes, per-task held-lock stacks, observed lock dependency chains, IRQ-context usage states, and optional lock contention statistics, then warns when a new lock operation would make a recursive lock, circular dependency, IRQ-safe to IRQ-unsafe inversion, invalid wait-context nesting, bad unlock, or lifetime violation possible. The file is not Ceph-specific; in this source tree it is the generic Linux kernel lockdep engine used by all kernel subsystems, including any distributed filesystem client code compiled with lock debugging.

The implementation is built around static, bounded storage rather than dynamic allocation in hot paths: `lock_classes[]`, `list_entries[]`, `lock_chains[]`, `chain_hlocks[]`, `stack_trace[]`, and several hash tables. When capacity is exhausted, lockdep disables itself through `debug_locks_off()` and emits a diagnostic instead of risking recursive allocation or corrupting the validator graph.

### Important APIs, Types, and Functions
The public API exported from this file includes `lockdep_init_map_type()`, `lockdep_register_key()`, `lockdep_unregister_key()`, `lock_acquire()`, `lock_release()`, `lock_sync()`, `lock_set_class()`, `lock_downgrade()`, `lock_is_held_type()`, `lock_pin_lock()`, `lock_repin_lock()`, `lock_unpin_lock()`, `read_lock_is_recursive()`, `debug_check_no_locks_freed()`, `debug_check_no_locks_held()`, `debug_show_all_locks()`, `debug_show_held_locks()`, and `lockdep_rcu_suspicious()`. With `CONFIG_LOCK_STAT`, it also exports `lock_contended()` and `lock_acquired()` for wait/hold-time accounting.

The central data types come from `include/linux/lockdep.h` and the internal header. `struct lockdep_map` is embedded by lock primitives and carries the class key/name/cache. `struct lock_class` represents a logical lock class and stores graph links, usage masks, wait types, name versioning, optional comparison/print callbacks, and usage traces. `struct held_lock` is the per-task stack entry. `struct lock_list` is a directed dependency edge in both forward and backward lists. `struct lock_chain` caches complete observed chains by a 64-bit chain key, with compact class IDs stored in `chain_hlocks[]`. `struct pending_free` and `delayed_free` stage lock classes and chain records that have been zapped but cannot be reused until RCU readers finish.

Core helpers include:

- `lockdep_enabled()`, `lockdep_lock()`, `graph_lock()`, and `debug_locks_off_graph_unlock()` guard recursion and serialize graph mutation.
- `look_up_lock_class()`, `assign_lock_key()`, `lockdep_register_key()`, `is_dynamic_key()`, and `register_lock_class()` map a lock instance/subclass to a `struct lock_class`.
- `iterate_chain_key()`, `hlock_id()`, `lookup_chain_cache_add()`, and `add_chain_cache()` build and cache lock-chain identities.
- `__bfs()`, `check_noncircular()`, `check_irq_usage()`, and `check_redundant()` traverse the dependency graph to validate new edges.
- `mark_lock()`, `mark_usage()`, `mark_held_locks()`, `lockdep_hardirqs_on_prepare()`, `lockdep_hardirqs_on()`, `lockdep_hardirqs_off()`, `lockdep_softirqs_on()`, and `lockdep_softirqs_off()` maintain hardirq/softirq usage state and detect inconsistent use.
- `__lock_acquire()`, `__lock_release()`, `__lock_set_class()`, `__lock_downgrade()`, `reacquire_held_locks()`, and `find_held_lock()` maintain the current task's lock stack.
- `zap_class()`, `remove_class_from_lock_chains()`, `lockdep_free_key_range()`, `lockdep_reset_lock()`, and `free_zapped_rcu()` remove classes safely during module unload, dynamic-key unregister, lock reinitialization, and selftests.

### Control Flow
For normal acquisition, callers enter `lock_acquire()`. It emits the tracepoint, performs a KASAN byte check on the lock map, saves IRQ flags, validates IRQ tracking with `check_flags()`, increments recursion protection, and calls `__lock_acquire()`. The internal acquisition path optionally registers the lock class, fills a new `held_lock`, checks wait context, marks current usage bits, derives the new chain key, validates nested-lock annotations, validates the dependency chain, then pushes the entry onto `current->held_locks` unless this is a `lock_sync()` pseudo-acquisition. The validation stage first uses chain-cache lookup to avoid repeated O(N^2) work; a cache miss triggers self-deadlock checks, dependency-edge checks against prior relevant held locks, cycle detection, IRQ inversion checks, and new edge insertion.

For release, `lock_release()` performs the same trace/IRQ/recursion wrapper and calls `__lock_release()`. It finds the matching held lock within the current IRQ-context segment, updates lock-stat hold time if the exact instance is released, rejects pinned releases, decrements reference counts for nested/reference-style tracking, and either pops the top lock or rewinds the stack and replays later held locks through `reacquire_held_locks()` so chain keys and dependency validation remain consistent after out-of-order release.

For graph validation, lockdep uses breadth-first search over `locks_after` or `locks_before`. `__bfs()` tracks visited classes with a generation ID, stores parent links for diagnostics, and filters weak reader/shared paths using dependency bitmasks so only "strong" dependency paths are considered for deadlock reasoning. `check_noncircular()` searches from the new lock back toward the prior lock. `check_irq_usage()` accumulates IRQ-safe usage backward from the previous lock and searches forward from the next lock for incompatible IRQ-unsafe usage. On failure, the print helpers drop the graph lock by disabling lockdep, enter emergency console context, print held locks and the shortest dependency paths, and dump the stack.

For class lifetime, static locks use their object address or canonical percpu address as a class key. Dynamic keys must be explicitly registered before use and unregistered before memory is reused. `lockdep_free_key_range()` and `lockdep_reset_lock()` zap classes and remove related dependency records under the graph lock, but normal paths defer reinitialization and reuse through `call_rcu()` because class hash lists and dependency lists are walked by RCU readers.

### State and Persistence Behavior
All validator state is in memory and lasts until reset, module/key removal, lock reset, or reboot. Important global state includes `debug_locks`, `prove_locking`, `lock_stat`, per-CPU `lockdep_recursion`, global `__lock`, `all_lock_classes`, `free_lock_classes`, `lock_keys_hash`, `classhash_table`, `chainhash_table`, `lock_classes_in_use`, `list_entries_in_use`, `lock_chains_in_use`, `nr_lock_classes`, `nr_list_entries`, `nr_dynamic_keys`, `nr_stack_trace_entries`, and IRQ chain counters. Per-task state includes `lockdep_depth`, `curr_chain_key`, `held_locks[]`, recursion count, softirq state, hardirq chain key, and IRQ trace stamps.

The file persists historical dependencies deliberately: a future acquisition can be rejected because some prior task observed the inverse order. Stack traces are deduplicated into `stack_trace[]` by hash and retained for diagnostics. `lockdep_reset()` is available for tests and wipes the current task state plus chain hash tables, but it is not a normal runtime cleanup mechanism.

### Dependencies and Integration Points
The code depends on Linux scheduler/task state, IRQ flags, RCU, stacktrace, kallsyms, debug locks, proc/sysctl support, tracing events, KASAN, per-CPU APIs, hash helpers, and architecture spinlocks. It is invoked by lock primitive wrappers throughout the kernel through lockdep map initialization and acquire/release annotations. `lockdep_proc.c` reads many globals declared here and in `lockdep_internals.h`. Dynamic module unload and memory freeing paths call `lockdep_free_key_range()` and `debug_check_no_locks_freed()`. RCU diagnostics call `lockdep_rcu_suspicious()`. Lock-stat proc output depends on `lock_stats()` and `clear_lock_stats()`.

### Risks and Edge Cases
Capacity exhaustion is an expected failure mode: too many classes, dependency entries, stack traces, chains, chain hlocks, or BFS queue entries disables lockdep. Incorrect static/dynamic key lifetime can cause use-after-free warnings or force validator shutdown. IRQ tracking mismatches can produce diagnostics if callers fail to annotate IRQ state transitions precisely. The graph lock is a raw architecture spinlock and must be entered with interrupts disabled; any path that recurses into lockdep without recursion guards risks corrupting state. RCU-delayed class reuse is subtle: zapped records must stay visible until readers complete, and immediate freeing is restricted to selftests. Out-of-order releases are supported but expensive because the held stack must be replayed. Some paths intentionally continue diagnostics after lockdep has been disabled, so printing helpers must avoid relying on mutable graph state too strongly.

### Test Signals
Useful signals include boot-time `lockdep_init()` size messages, warnings for recursive locking, circular dependencies, IRQ-safe to IRQ-unsafe inversions, inconsistent usage states, invalid wait context, bad unlock balance, held lock freed, locks held at syscall exit, and suspicious RCU use. `/proc/lockdep`, `/proc/lockdep_chains`, `/proc/lockdep_stats`, and `/proc/lock_stat` provide runtime visibility. Selftests exercise `lockdep_reset()`, immediate key freeing, and `lockdep_set_selftest_task()`. Lock-stat testing can check contention and hold-time accounting through `lock_contended()` and `lock_acquired()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/lockdep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/lockdep_internals.h -->
## sources/distributed-fs/ceph-client/kernel/locking/lockdep_internals.h

### Purpose
`lockdep_internals.h` is the private contract shared by the lockdep engine and its proc reporting code. It defines usage-state bit numbering, mask helpers, bounded storage sizes, lock-chain context bits, externally visible lockdep counters, and debug-stat accessors that are not part of the public lockdep API.

### Important APIs, Types, and Functions
The primary type defined here is `enum lock_usage_bit`. It is generated from `lockdep_states.h` so each tracked IRQ state contributes four bits: used in state, used in state as read, enabled in state, and enabled in state as read. After generated bits, `LOCK_USED`, `LOCK_USED_READ`, and `LOCK_USAGE_STATES` are appended. The header asserts that `LOCK_TRACE_STATES` matches `LOCK_USAGE_STATES`, keeping trace arrays aligned with usage bits.

Mask definitions include `LOCK_USAGE_READ_MASK`, `LOCK_USAGE_DIR_MASK`, `LOCK_USAGE_STATE_MASK`, per-bit `LOCKF_*` constants, aggregate enabled/used masks for all IRQ states, and combined masks such as `LOCKF_IRQ`, `LOCKF_IRQ_READ`, `LOCKF_ENABLED_IRQ_ALL`, and `LOCKF_USED_IN_IRQ_ALL`. These masks drive lockdep's usage conflict checks in `lockdep.c` and summary counts in `lockdep_proc.c`.

Size controls include `MAX_LOCKDEP_ENTRIES`, `MAX_LOCKDEP_CHAINS_BITS`, `MAX_STACK_TRACE_ENTRIES`, `STACK_TRACE_HASH_SIZE`, `MAX_LOCKDEP_CHAINS`, `AVG_LOCKDEP_CHAIN_DEPTH`, and `MAX_LOCKDEP_CHAIN_HLOCKS`. `CONFIG_LOCKDEP_SMALL` provides reduced static allocations for architectures with tight kernel image limits.

The file declares shared globals and functions such as `lock_chains[]`, `get_usage_chars()`, `__get_key_name()`, `lock_chain_get_class()`, `nr_lock_classes`, `nr_zapped_classes`, `nr_zapped_lock_chains`, `nr_list_entries`, `nr_dynamic_keys`, `lockdep_next_lockchain()`, `lock_chain_count()`, chain hlock counters, `max_lockdep_depth`, `max_bfs_queue_depth`, `max_lock_class_idx`, `lock_classes[]`, and `lock_classes_in_use[]`.

Under `CONFIG_DEBUG_LOCKDEP`, it defines `struct lockdep_stats` and macros/functions for per-CPU debug counters: `debug_atomic_inc()`, `debug_atomic_dec()`, `debug_atomic_read()`, `debug_class_ops_inc()`, and `debug_class_ops_read()`. Without debug lockdep, those become no-ops or zero-valued expressions.

### Control Flow
This header has no runtime control flow of its own, but it shapes several critical flows. `lockdep.c` includes it to allocate graph storage and generate usage checks. `lockdep_proc.c` includes it to iterate `lock_classes[]`, traverse lock chains, and print counters. Any addition to `lockdep_states.h` expands the generated enum and masks here, which then changes `LOCK_USAGE_CHARS`, `/proc/lockdep` output, state conflict logic, and stats categorization.

### State and Persistence Behavior
The header declares state that persists globally while the kernel runs. Counters represent live lockdep storage and historical observations, not persisted disk data. Debug counters are per-CPU to avoid cache bouncing and are summed on read by `debug_atomic_read()`. Because many arrays are statically bounded, build-time configuration directly controls how much lockdep history can be retained before lockdep disables itself.

### Dependencies and Integration Points
The header depends on `lockdep_states.h`, public lockdep structures, per-CPU APIs, and architecture local operations for debug stats. It is a tight coupling point between lockdep graph mutation and procfs presentation. It also embeds the expectation that `include/linux/lockdep.h` keeps constants such as `XXX_LOCK_USAGE_STATES` and `LOCK_TRACE_STATES` synchronized with the generated states.

### Risks and Edge Cases
The most important maintenance risk is bit-layout drift. `lockdep.c` assumes the low bit encodes read/write and the direction bit encodes used-in versus enabled, so changing generation order would break `exclusive_mask()`, `original_mask()`, and state-printing logic. Adding a new state requires updating public constants as warned by `lockdep_states.h`. Increasing array sizes affects kernel memory footprint; decreasing them increases validator shutdown risk under complex workloads.

### Test Signals
Compile-time assertions and build failures are the first signal for enum/constant mismatch. Runtime `/proc/lockdep_stats` exposes max counts and can show exhaustion pressure in lock classes, entries, chains, stack traces, BFS queue depth, and chain hlock fragmentation. `CONFIG_DEBUG_LOCKDEP` builds expose redundant/cyclic/find-mask counters and per-class operation counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/lockdep_internals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/lockdep_proc.c -->
## sources/distributed-fs/ceph-client/kernel/locking/lockdep_proc.c

### Purpose
`lockdep_proc.c` exposes lockdep state through procfs. It implements `/proc/lockdep` for lock classes and direct dependencies, `/proc/lockdep_chains` for cached dependency chains when proving is enabled, `/proc/lockdep_stats` for aggregate counters and capacity use, and `/proc/lock_stat` for contention and timing statistics when `CONFIG_LOCK_STAT` is enabled.

### Important APIs, Types, and Functions
The class iterator is built from `l_start()`, `l_next()`, `l_stop()`, `l_show()`, and `lockdep_ops`. It iterates directly over `lock_classes[]` from index zero through `max_lock_class_idx` and filters with `lock_classes_in_use`, avoiding `all_lock_classes` because class lists can move to free or zapped lists while proc iteration is lockless.

`print_name()` mirrors lockdep's class-name formatting: key symbol fallback, name-version suffix, and subclass suffix. `l_show()` prints class key, optional debug operation count, forward/backward dependency counts, usage characters, class name, and direct `locks_after` edges when proving is enabled.

With `CONFIG_PROVE_LOCKING`, `lc_start()`, `lc_next()`, `lc_show()`, and `lockdep_chains_ops` expose `lock_chains[]`. They use `lockdep_next_lockchain()` to skip unused entries and `lock_chain_get_class()` to recover classes from compact chain storage.

`lockdep_stats_show()` aggregates usage masks across classes and prints high-level resource and classification counters: lock classes, dynamic keys, direct/indirect dependencies, chain counts, chain hlock use/loss, hardirq/softirq/process chains, stack trace counts, safe/unsafe usage categories, unused/uncategorized locks, max depth, BFS depth, zapped classes/chains, and debug state. `lockdep_stats_debug_show()` appends `CONFIG_DEBUG_LOCKDEP` counters.

With `CONFIG_LOCK_STAT`, `struct lock_stat_data` stores one class plus merged stats, and `struct lock_stat_seq` stores a full snapshot. `lock_stat_open()` snapshots all active classes with `lock_stats()`, sorts by total contentions via `lock_stat_cmp()`, and installs the snapshot as seq private data. `seq_stats()` formats wait/hold time, bounces, contention points, and contending points. `lock_stat_write()` clears stats when users write `0`. `lock_stat_release()` frees the vmalloc snapshot.

### Control Flow
`lockdep_proc_init()` registers all proc entries at init time. Reads of `/proc/lockdep` and `/proc/lockdep_chains` stream live arrays through seq_file. Reads of `/proc/lockdep_stats` calculate a fresh aggregate on each call. Reads of `/proc/lock_stat` first allocate and populate a stable sorted snapshot during open, then seq iteration formats that snapshot; release frees it. Writes to `/proc/lock_stat` do not parse full strings: a first byte of `'0'` clears all active class stats and other input is ignored as a no-op success.

### State and Persistence Behavior
This file owns no persistent lockdep graph state. Its only per-open state is the `vmalloc()`ed `struct lock_stat_seq` snapshot for `/proc/lock_stat`. All other output is a view over globals owned by `lockdep.c`. Because class and chain iteration is mostly lockless, output is diagnostic and can race with class zapping or graph mutation, but the implementation avoids the most dangerous list traversal by walking arrays and RCU-compatible chain helpers.

### Dependencies and Integration Points
The file depends on `proc_fs`, `seq_file`, `kallsyms`, `debug_locks`, `vmalloc`, `sort`, `uaccess`, division helpers, and `lockdep_internals.h`. It consumes `lock_stats()` and `clear_lock_stats()` from `lockdep.c` under `CONFIG_LOCK_STAT`. It is the main user-facing visibility layer for the lockdep engine and is commonly used in bug reports after lockdep warnings.

### Risks and Edge Cases
Proc output is not a synchronized snapshot except for `/proc/lock_stat`; classes can change while a read is in progress. `seq_stats()` intentionally returns early if both class name and key are unavailable, which can hide a zapped class from lock-stat output. The class-name buffer truncates long names and has comments noting version/subclass truncation limitations. `lock_stat_open()` allocates a `MAX_LOCKDEP_KEYS`-sized snapshot with `vmalloc`, so low-memory conditions can fail reads with `-ENOMEM`. Because `/proc/lock_stat` clearing is triggered by a single leading `0`, tooling should avoid accidental writes.

### Test Signals
Expected proc entries are `lockdep`, `lockdep_stats`, optionally `lockdep_chains`, and optionally `lock_stat`. Test signals include sane class counts, dependency counts matching active lockdep workloads, nonzero debug counters under `CONFIG_DEBUG_LOCKDEP`, sorted contention rows under lock-stat workloads, and successful clearing of stats by writing `0` to `/proc/lock_stat`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/lockdep_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/lockdep_states.h -->
## sources/distributed-fs/ceph-client/kernel/locking/lockdep_states.h

### Purpose
`lockdep_states.h` is a tiny X-macro list of lockdep IRQ usage states. It currently declares `HARDIRQ` and `SOFTIRQ`, and consumers expand each state into enum values, bitmasks, usage strings, character output, state names, and verbose handlers.

### Important APIs, Types, and Functions
The only interface is repeated invocation of `LOCKDEP_STATE(HARDIRQ)` and `LOCKDEP_STATE(SOFTIRQ)`. `lockdep_internals.h` expands these into `LOCK_USED_IN_*`, `LOCK_USED_IN_*_READ`, `LOCK_ENABLED_*`, and `LOCK_ENABLED_*_READ` enum values and masks. `lockdep.c` expands the same list into printable usage strings, usage characters, state name arrays, and per-state verbosity dispatch. `lockdep_proc.c` indirectly relies on these generated masks when counting hardirq/softirq safe and unsafe classes.

### Control Flow
This file has no standalone execution. It is included multiple times with different `LOCKDEP_STATE` definitions. The include style is intentional: consumers define the macro, include this file, and undefine the macro to keep one authoritative list of states.

### State and Persistence Behavior
There is no runtime state. Its contents define the shape of runtime state in lock classes: usage-mask width, trace arrays, printable usage character count, and proc statistics categories.

### Dependencies and Integration Points
It must stay synchronized with public lockdep constants, especially `XXX_LOCK_USAGE_STATES` in `include/linux/lockdep.h`, as the file comment warns. Adding a state affects lockdep bit layout, diagnostics, proc output, and any assertions that compare trace-state counts.

### Risks and Edge Cases
The risk is maintenance mismatch. Adding, deleting, or reordering states without updating public constants and auditing bit-layout assumptions can break IRQ inversion detection. Because the bit encoding is used arithmetically in `lockdep.c`, the generated order must preserve read and direction bit meanings.

### Test Signals
Build failures, static assertions, or malformed `/proc/lockdep` usage strings are immediate signals of an incorrect update. Runtime lockdep tests covering hardirq and softirq inversion should still produce coherent state names and usage characters after any change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/lockdep_states.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/locktorture.c -->
## sources/distributed-fs/ceph-client/kernel/locking/locktorture.c

### Purpose
`locktorture.c` is a module-based stress test facility for Linux locking primitives. It creates writer and optional reader kthreads that repeatedly acquire and release a selected lock type, inject delays and priority changes, optionally exercises nested locks, CPU hotplug, task shuffling, stuttered execution, shutdown, and RCU callback chains, then reports acquisition counts and correctness failures.

### Important APIs, Types, and Functions
The module exposes parameters through `torture_param()` and `module_param()`: `torture_type`, `nwriters_stress`, `nreaders_stress`, `long_hold`, `nested_locks`, `acq_writer_lim`, `rt_boost`, `rt_boost_factor`, `writer_fifo`, `bind_readers`, `bind_writers`, `call_rcu_chains`, `onoff_*`, `shuffle_interval`, `shutdown_secs`, `stat_interval`, `stutter`, and `verbose`.

`struct lock_torture_ops` is the abstraction for a lock family. It contains optional init/exit hooks, nested lock/unlock hooks, writer lock/delay/unlock hooks, optional reader lock/delay/unlock hooks, a task priority boost hook, IRQ flags storage, and a name. Implemented ops include deliberately broken locking, spinlock, spinlock IRQ-save, raw spinlock, raw spinlock IRQ-save, optional BPF raw-res spinlock variants, rwlock, rwlock IRQ-save, mutex, ww_mutex, optional rt_mutex, rwsem, and percpu rwsem.

`struct lock_torture_cxt` stores resolved writer/reader counts, whether debug locking is active for the chosen primitive, whether ops init ran, error count, current ops pointer, and per-thread writer/reader stats arrays. `struct lock_stress_stats` stores per-thread failure and acquisition counters. `struct call_rcu_chain` supports optional self-propagating RCU callback chains.

Key functions include `param_set_cpumask()` and `param_get_cpumask()` for CPU binding parameters, `__torture_rt_boost()` and wrappers for priority changes, many primitive-specific lock/delay/unlock functions, `lock_torture_writer()`, `lock_torture_reader()`, `lock_torture_stats_print()`, `lock_torture_stats()`, `call_rcu_chain_init()`, `call_rcu_chain_cleanup()`, `lock_torture_cleanup()`, and `lock_torture_init()`.

### Control Flow
Module initialization starts in `lock_torture_init()`. It calls `torture_init_begin()`, selects the ops table entry matching `torture_type`, validates that at least one locking thread will run, derives default writer/reader counts, runs ops-specific initialization, detects whether debug lock configs apply, allocates and zeros stats arrays, starts optional RCU callback chains, prints start parameters, initializes optional CPU hotplug/shuffle/shutdown/stutter helpers, allocates task arrays, caps `nested_locks` to `MAX_NESTED_LOCKS`, then interleaves writer and reader kthread creation. Optional CPU masks are applied after thread creation. If `stat_interval` is positive, it starts a stats kthread. Any initialization failure jumps to `unwind`, ends torture initialization, performs cleanup, and optionally powers off for shutdown tests.

Writer threads run `lock_torture_writer()`. Each loop can sleep briefly, chooses a random nested lockset, sometimes skips the main lock when nested locks are enabled to diversify dependency trees, applies priority boosting, acquires selected nested locks, optionally times main lock acquisition, verifies no writer or reader overlap for exclusive primitives, increments stats, runs the selected delay function, releases the main lock, releases nested locks in reverse order, and honors stutter/stop signals.

Reader threads run `lock_torture_reader()`. They acquire the selected read lock, increment `lock_is_read_held`, check for writer overlap, update stats, delay, decrement the reader count, unlock, and honor stutter/stop signals.

Cleanup stops writer threads, reader threads, and the stats thread, prints final stats after the stats thread is stopped, reports SUCCESS/FAILURE/LOCK_HOTPLUG, frees stats and task arrays, stops RCU callback chains with `rcu_barrier()`, runs ops-specific exit hooks, frees CPU masks, and calls `torture_cleanup_end()`.

### State and Persistence Behavior
State is module-lifetime only. Global task pointers, stats arrays, chosen ops, lock instances, nested lock arrays, CPU masks, `lock_is_write_held`, `lock_is_read_held`, `last_lock_release`, and RCU chain arrays exist until module unload or initialization unwind. Per-thread counters are read with `data_race()` for diagnostic summaries rather than synchronized exact accounting. The test intentionally preserves accumulated acquisition/failure counts until cleanup prints final results.

### Dependencies and Integration Points
The file depends on the kernel torture framework, kthreads, scheduler priority APIs, CPU affinity, spinlocks, raw spinlocks, mutexes, ww_mutex, rt_mutex when configured, rwsems, percpu rwsems, RCU callbacks, module parameters, CPU hotplug torture helpers, and reboot/shutdown helpers. It is used as a kernel module via `module_init()` and `module_exit()`, and its output is printk/pr_alert based. It also intentionally interacts with lockdep: nested lock count is capped because high nesting can exhaust `MAX_LOCKDEP_CHAIN_HLOCKS`, and debug lock configurations influence the printed `[debug]` tag.

### Risks and Edge Cases
The deliberately broken `lock_busted` ops are expected to produce failures and must not be mistaken for a valid primitive. Writer/read overlap checks use global flags that are intentionally simple stress-test sentinels rather than full synchronization primitives. `cxt.cur_ops->flags` stores IRQ flags in the ops structure, so IRQ-save torture variants rely on each tested lock being held by one writer at a time; this matches exclusive locking but is not a general per-thread flags design. `ww_mutex` initialization can continue after allocation failure only to later fail when contexts are used, so memory allocation should be watched carefully. Long holds, RT boosting, CPU hotplug, and call_rcu chains can intentionally create stalls or noisy diagnostics. High `nested_locks` is capped because lockdep chain storage can be exhausted.

### Test Signals
The main signals are periodic and final `Writes`/`Reads` totals, max/min spread warnings, nonzero `Fail` counts, module parameter echo at start/end, torture framework init errors, hotplug failure reporting, and kernel warnings from underlying lock/debug/lockdep subsystems. A successful normal run prints an end-of-test SUCCESS line with no lock torture errors. Lock-specific tests should be run across supported `torture_type` values, with reader counts only meaningful for primitives that provide read locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/locktorture.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/mcs_spinlock.h -->
## sources/distributed-fs/ceph-client/kernel/locking/mcs_spinlock.h

### Purpose
`mcs_spinlock.h` implements the generic Mellor-Crummey and Scott queue spinlock helper used by kernel locking code that needs fair handoff and local spinning. Instead of all waiters spinning on a shared word, each waiter enqueues a per-call node and spins on its own `node->locked` field, reducing cacheline bouncing under contention.

### Important APIs, Types, and Functions
The header includes `asm/mcs_spinlock.h`, which supplies `struct mcs_spinlock` and may override architecture-specific waiting/wakeup macros. If not overridden, `arch_mcs_spin_lock_contended(l)` uses `smp_cond_load_acquire(l, VAL)` to wait with acquire semantics, and `arch_mcs_spin_unlock_contended(l)` uses `smp_store_release(l, 1)` to hand the lock to the next waiter.

The public inline functions are `mcs_spin_lock(struct mcs_spinlock **lock, struct mcs_spinlock *node)` and `mcs_spin_unlock(struct mcs_spinlock **lock, struct mcs_spinlock *node)`. The caller owns the node lifetime and must pass the same node to unlock that was used to lock.

### Control Flow
`mcs_spin_lock()` initializes the caller's node, atomically exchanges the queue tail with the node, and returns immediately if there was no predecessor. If there was a predecessor, it stores itself in `prev->next` and waits until the predecessor sets `node->locked`.

`mcs_spin_unlock()` first reads `node->next`. If no successor is visible, it attempts `cmpxchg_release(lock, node, NULL)` to release an uncontended or not-yet-linked tail. If the compare-exchange fails, a successor has enqueued but not yet linked itself into `node->next`, so unlock waits until `next` appears. It then wakes the successor by storing release to `next->locked`.

### State and Persistence Behavior
The lock state is the shared tail pointer plus transient per-waiter nodes. The header does not allocate memory or maintain global state. Correctness depends on the caller keeping each node stable while queued and not reusing it until after unlock. The comments explicitly note that the acquire/release pair is not a full cross-CPU memory barrier on all architectures; callers that require a full barrier after unlock-lock pairing must use `smp_mb__after_unlock_lock()` after lock acquisition.

### Dependencies and Integration Points
This header depends on architecture definitions for `struct mcs_spinlock` and optional arch hooks. It uses atomic exchange, compare-exchange release, `READ_ONCE`, `WRITE_ONCE`, `cpu_relax`, and SMP acquire/release primitives. Queue spinlock implementations and other scalable locking algorithms can build on these helpers.

### Risks and Edge Cases
Passing a non-local or reused node can corrupt the queue. Unlocking with a different node than was used for acquisition can leave waiters stuck. The small handoff race where a successor is tail-visible but has not set `prev->next` is handled by the wait loop in unlock; removing that loop would lose wakeups. Architecture overrides must preserve acquire/release semantics and should not introduce pure busy waiting where the architecture expects wait instructions.

### Test Signals
Stress tests should show FIFO handoff under contention and no shared-cacheline storm comparable to test-and-set locks. Memory-ordering tests should cover critical-section visibility, and architecture lock tests should include the race where unlock observes no `next` but `cmpxchg_release()` fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/mcs_spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/mutex-debug.c -->
## sources/distributed-fs/ceph-client/kernel/locking/mutex-debug.c

### Purpose
`mutex-debug.c` provides debug-only helpers for Linux mutex internals. It poisons and validates mutex waiters, checks waiter/task relationships, tracks mutex initialization/destruction through a magic pointer, integrates mutex destruction with devres, and exports `mutex_destroy()` for marking a mutex unusable after teardown.

### Important APIs, Types, and Functions
`debug_mutex_lock_common()` initializes a `struct mutex_waiter` while `lock->wait_lock` is held: it fills the waiter with `MUTEX_DEBUG_INIT`, sets `waiter->magic` to itself, initializes the list node, and poisons the wound/wait context pointer. `debug_mutex_wake_waiter()` asserts `wait_lock` is held, `first_waiter` exists, and the waiter's magic value is intact. `debug_mutex_free_waiter()` verifies the waiter list node is empty and poisons the waiter with `MUTEX_DEBUG_FREE`.

`debug_mutex_add_waiter()` asserts the current task is not already blocked on a mutex. `debug_mutex_remove_waiter()` verifies the waiter belongs to the task and that any blocked-on mutex matches the lock being removed, then clears the waiter list and task pointer. `debug_mutex_unlock()` checks the mutex magic pointer when debug locks are still enabled. `debug_mutex_init()` sets `lock->magic = lock`.

`__devm_mutex_init()` registers `devm_mutex_release()` as a devres cleanup action; the release callback calls `mutex_destroy()`. `mutex_destroy()` warns if the mutex is locked and clears `lock->magic`, making later use detectable. `__devm_mutex_init()` and `mutex_destroy()` are exported GPL symbols.

### Control Flow
Mutex slow paths call these helpers around waiter lifecycle operations. A waiting task's waiter is initialized before queueing, checked before wakeup, removed when it stops waiting, and poisoned after use. Mutex initialization sets the magic field. Unlock and destroy paths validate the magic/liveness state. Device-managed mutex initialization attaches destruction to device cleanup so driver teardown marks the mutex invalid automatically.

### State and Persistence Behavior
The debug state is embedded in existing mutex and waiter objects. Waiter poison values are transient stack/queue lifetime checks. `lock->magic` persists from initialization until `mutex_destroy()`, after which it is NULL. There is no global state in this file, but behavior depends on global `debug_locks`: some checks are skipped after lock debugging has been disabled to avoid cascading diagnostics.

### Dependencies and Integration Points
The file includes mutex internals through `"mutex.h"` plus debug locks, lockdep assertions, scheduler blocked-task helpers, device devres, poison constants, and export support. It is integrated into the mutex implementation rather than called by ordinary subsystem code directly. Device-managed users reach it through devm mutex initialization wrappers.

### Risks and Edge Cases
The helpers assume callers hold `lock->wait_lock` where documented; missing that lock weakens waiter-list validation and can race with wakeups. Destroying a locked mutex triggers a warning but still clears magic, so subsequent diagnostics may report use-after-destroy rather than the original lifetime bug. Waiter poisoning catches stale waiter reuse but cannot prevent memory corruption if callers continue using a freed stack waiter. `__devm_mutex_init()` only registers cleanup; the mutex must still have been initialized by the caller/wrapper before use.

### Test Signals
Useful signals are `DEBUG_LOCKS_WARN_ON()` reports for corrupted waiter magic, nonempty waiter lists at free time, blocked-task mismatches, unlocking uninitialized/destroyed mutexes, and destroying locked mutexes. Devres tests should verify device cleanup calls `mutex_destroy()` through `devm_mutex_release()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/mutex-debug.c -->
