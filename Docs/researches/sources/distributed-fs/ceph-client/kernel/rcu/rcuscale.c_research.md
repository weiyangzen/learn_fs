# sources/distributed-fs/ceph-client/kernel/rcu/rcuscale.c

## Purpose
`rcuscale.c` is a module/built-in scalability test for RCU grace-period primitives and `kfree_rcu()` behavior. It creates reader and writer kthreads, measures synchronous, expedited, or asynchronous grace-period durations, optionally stresses callback allocation/freeing, and reports per-writer measurements.

## Important APIs, types, and functions
Module parameters include `scale_type`, `gp_async`, `gp_async_max`, `gp_exp`, `holdoff`, `minruntime`, `nreaders`, `nwriters`, `shutdown_secs`, writer holdoffs, and kfree-related knobs. `struct rcu_scale_ops` abstracts RCU flavors with read lock/unlock, GP sequence, async callback, barrier, sync, expedited sync, stats, and GP-kthread accessors. Implemented flavors include `rcu`, `srcu`, dynamic `srcud`, and optional tasks/tasks-rude/tasks-tracing. Main threads are `rcu_scale_reader()`, `rcu_scale_writer()`, and `kfree_scale_thread()`.

## Control flow
`rcu_scale_init()` selects the ops vector by `scale_type`, initializes flavor state, allocates arrays, starts reader kthreads, initializes optional async freelists, and starts writer kthreads. Readers repeatedly enter and exit read-side critical sections with interrupts disabled to provide load. Writers wait for holdoff and system running state, then repeatedly measure normal, expedited, or async grace-period operations until minimum runtime and sample thresholds are met. Cleanup stops threads, prints counts and durations, frees arrays, runs flavor cleanup, and may power off for automated testing. If `kfree_rcu_test` is enabled, initialization routes to kfree-specific setup and threads.

## State and persistence behavior
State is runtime-only: task arrays, duration arrays, writer completion flags, async freelists, atomic counters, timestamps, GP batch snapshots, kfree test counters, and optional SRCU structure. Measurements are printed to the kernel log; no file output is owned by this module.

## Dependencies and integration points
The file depends on torture infrastructure, kthreads, scheduler policy APIs, CPU affinity, completions/atomics/llists, SRCU, Tasks RCU variants, lazy RCU controls, memory allocation, reboot poweroff for test automation, ftrace dumps on completion, and RCU internal helpers from `rcu.h`.

## Risks and invariants
This is test code but can stress production paths heavily. Async mode must cap in-flight callbacks and return all `writer_mblock`s to freelists before cleanup. Built-in tests must account for boot-time expedited GP behavior before measuring normal GPs. `shutdown_secs` can power off the system. Kfree lazy self-test temporarily changes lazy flush timing and must restore it. Affinity and FIFO-low scheduling can affect host responsiveness.

## Test signals
Expected signals are kernel log lines with module parameters, writer measurement counts, total duration, GP batches, per-writer durations, kfree total time/memory footprint, and warnings when requested normal/expedited mode is unavailable. RCU torture automation, boot-time built-in runs, module load/unload, async callback accounting warnings, and lazy-callback timing checks provide coverage.
