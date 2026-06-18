# sources/distributed-fs/ceph-client/kernel/locking/locktorture.c research

## Purpose
`locktorture.c` is a module-based stress test facility for Linux locking primitives. It creates writer and optional reader kthreads that repeatedly acquire and release a selected lock type, inject delays and priority changes, optionally exercises nested locks, CPU hotplug, task shuffling, stuttered execution, shutdown, and RCU callback chains, then reports acquisition counts and correctness failures.

## Important APIs, Types, and Functions
The module exposes parameters through `torture_param()` and `module_param()`: `torture_type`, `nwriters_stress`, `nreaders_stress`, `long_hold`, `nested_locks`, `acq_writer_lim`, `rt_boost`, `rt_boost_factor`, `writer_fifo`, `bind_readers`, `bind_writers`, `call_rcu_chains`, `onoff_*`, `shuffle_interval`, `shutdown_secs`, `stat_interval`, `stutter`, and `verbose`.

`struct lock_torture_ops` is the abstraction for a lock family. It contains optional init/exit hooks, nested lock/unlock hooks, writer lock/delay/unlock hooks, optional reader lock/delay/unlock hooks, a task priority boost hook, IRQ flags storage, and a name. Implemented ops include deliberately broken locking, spinlock, spinlock IRQ-save, raw spinlock, raw spinlock IRQ-save, optional BPF raw-res spinlock variants, rwlock, rwlock IRQ-save, mutex, ww_mutex, optional rt_mutex, rwsem, and percpu rwsem.

`struct lock_torture_cxt` stores resolved writer/reader counts, whether debug locking is active for the chosen primitive, whether ops init ran, error count, current ops pointer, and per-thread writer/reader stats arrays. Key functions include CPU-mask parameter helpers, `__torture_rt_boost()`, primitive-specific lock/delay/unlock functions, `lock_torture_writer()`, `lock_torture_reader()`, stats printing/thread functions, RCU chain init/cleanup, `lock_torture_cleanup()`, and `lock_torture_init()`.

## Control Flow
Module initialization selects the ops table entry matching `torture_type`, validates that at least one locking thread will run, derives default writer/reader counts, runs ops-specific initialization, detects debug-lock configs, allocates stats arrays, starts optional RCU callback chains, initializes optional CPU hotplug/shuffle/shutdown/stutter helpers, allocates task arrays, caps `nested_locks` to `MAX_NESTED_LOCKS`, then interleaves writer and reader kthread creation. Optional CPU masks are applied after thread creation. If `stat_interval` is positive, it starts a stats kthread. Any initialization failure jumps to cleanup.

Writer threads choose random nested locksets, sometimes skip the main lock when nested locks are enabled, apply priority boosting, acquire selected nested locks, optionally time acquisition, verify no writer or reader overlap for exclusive primitives, increment stats, delay, release the main lock, release nested locks in reverse order, and honor stutter/stop signals. Reader threads acquire the selected read lock, increment `lock_is_read_held`, check for writer overlap, update stats, delay, decrement the reader count, unlock, and honor stutter/stop signals.

Cleanup stops writer threads, reader threads, and the stats thread, prints final stats after the stats thread is stopped, reports SUCCESS/FAILURE/LOCK_HOTPLUG, frees stats and task arrays, stops RCU callback chains with `rcu_barrier()`, runs ops-specific exit hooks, frees CPU masks, and calls `torture_cleanup_end()`.

## State and Persistence Behavior
State is module-lifetime only. Global task pointers, stats arrays, chosen ops, lock instances, nested lock arrays, CPU masks, `lock_is_write_held`, `lock_is_read_held`, `last_lock_release`, and RCU chain arrays exist until module unload or initialization unwind. Per-thread counters are read with `data_race()` for diagnostic summaries rather than synchronized exact accounting. The test intentionally preserves accumulated acquisition/failure counts until cleanup prints final results.

## Dependencies and Integration Points
The file depends on the kernel torture framework, kthreads, scheduler priority APIs, CPU affinity, spinlocks, raw spinlocks, mutexes, ww_mutex, rt_mutex when configured, rwsems, percpu rwsems, RCU callbacks, module parameters, CPU hotplug torture helpers, and reboot/shutdown helpers. It is used as a kernel module via `module_init()` and `module_exit()`, and its output is printk/pr_alert based. It also intentionally interacts with lockdep: nested lock count is capped because high nesting can exhaust `MAX_LOCKDEP_CHAIN_HLOCKS`.

## Risks and Edge Cases
The deliberately broken `lock_busted` ops are expected to produce failures and must not be mistaken for a valid primitive. Writer/read overlap checks use global flags that are intentionally simple stress-test sentinels. `cxt.cur_ops->flags` stores IRQ flags in the ops structure, so IRQ-save torture variants rely on each tested lock being held by one writer at a time. Long holds, RT boosting, CPU hotplug, and call_rcu chains can intentionally create stalls or noisy diagnostics. High `nested_locks` is capped because lockdep chain storage can be exhausted.

## Test Signals
The main signals are periodic and final `Writes`/`Reads` totals, max/min spread warnings, nonzero `Fail` counts, module parameter echo at start/end, torture framework init errors, hotplug failure reporting, and kernel warnings from underlying lock/debug/lockdep subsystems. A successful normal run prints an end-of-test SUCCESS line with no lock torture errors.
