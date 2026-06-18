# sources/distributed-fs/ceph-client/lib/test_objpool.c

## Purpose

`sources/distributed-fs/ceph-client/lib/test_objpool.c` is a stress and performance test module for the lockless object pool API. It runs synchronous and asynchronous per-CPU pool scenarios with normal thread users and optional hrtimer users. The source was read as a complete 681-line file.

## Important APIs, Types, and Functions

Key structures are `struct ot_mem_stat`, `struct ot_obj_stat`, `struct ot_data`, `struct ot_test`, `struct ot_item`, `struct ot_node`, and `struct ot_context`. Important routines include `ot_init_data`, `ot_init_node`, `ot_hrtimer_handler`, `ot_init_cpu_item`, `ot_thread_worker`, `ot_perf_report`, `ot_init_sync_m0`, `ot_fini_sync`, `ot_bulk_sync`, `ot_start_sync`, `ot_fini_async_rcu`, `ot_fini_async`, `ot_objpool_release`, `ot_init_async_m0`, `ot_nod_recycle`, `ot_bulk_async`, `ot_start_async`, and `ot_mod_init`. Test scenarios are in `g_testcases`.

## Control Flow

On load, `ot_mod_init` iterates predefined scenarios. Each scenario initializes per-test control state, creates an object pool sized at `num_possible_cpus() << 3`, starts one worker per online CPU, releases them from an rwsem start gate, lets them run for the configured duration, sets a stop flag, waits for completion, finalizes the pool, and reports per-CPU hit/miss counts plus memory accounting. Synchronous tests recycle objects with `objpool_push`; asynchronous tests use `objpool_drop` under stop conditions and an RCU callback to finalize pool lifetime.

## State and Persistence Behavior

State lives in the global per-CPU `ot_pcup_items` and in `g_testcases` result fields during module load. Pool contexts and backing allocations are created per scenario and released. Memory counters track `kmalloc` allocations and frees for leak reporting. The module deliberately returns `-EAGAIN` after printing summaries so it does not remain loaded.

## Dependencies and Integration Points

Direct dependencies include module parameters, completions, kthreads, slab/vmalloc, delay, hrtimer, and `<linux/objpool.h>`. Integration points are `objpool_init`, `objpool_fini`, `objpool_pop`, `objpool_push`, `objpool_drop`, per-CPU workers, high-resolution timers, RCU callbacks, and atomic release/acquire stop signaling.

## Risks and Edge Cases

The module is stress-oriented and can consume CPU for one second per scenario across all online CPUs. It mixes thread and hrtimer contexts, so lockless pool correctness under interrupt-like timing is central. Async teardown is subtle: stop visibility, RCU callback ordering, and pool ref drops must align or use-after-free/leak issues can appear. Error returns from individual scenario starts are not propagated by `ot_mod_init`, which always finishes with `-EAGAIN`.

## Test Signals

Useful signals are per-case hit/miss summaries, memory allocation summaries with zero deltas, absence of WARNs, and successful completion of all scenarios. The expected final module init return is `-EAGAIN`, used to unload after benchmark completion rather than to indicate failure.
