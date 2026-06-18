# sources/distributed-fs/ceph-client/kernel/scftorture.c

## Purpose
`scftorture.c` is a torture-test module for `smp_call_function()` and related IPI primitives. It repeatedly invokes reschedule, single-CPU, many-CPU, all-CPU, wait, no-wait, and RPC-like variants under randomized load, optional CPU hotplug, stutter, long waits, and shutdown control.

## Important APIs, Types, And Functions
Module parameters control holdoff, long waits, thread count, CPU hotplug cadence, shutdown, stats interval, stutter, hotplug locking mode, verbosity, and operation weights. `struct scf_statistics` records per-thread counts. `struct scf_selector` stores weighted primitive choices. `struct scf_check` is passed to IPI handlers to validate memory ordering, target CPU, completion, and wait/no-wait ownership. Main functions include `scf_sel_add()`, `scf_sel_rand()`, `scf_handler()`, `scf_handler_1()`, `scftorture_invoke_one()`, `scftorture_invoker()`, `scf_torture_stats_print()`, `scf_torture_init()`, and `scf_torture_cleanup()`.

## Control Flow
Initialization computes default weights when all weights are unset, rejects an all-zero workload, initializes optional hotplug/shutdown/stutter torture services, allocates per-thread statistics, starts invoker kthreads, and optionally starts a stats printer thread. Each invoker pins itself to a CPU, waits for all invokers to start, drains its per-CPU no-wait free list, selects a primitive randomly by cumulative weight, and invokes the chosen SMP call-function primitive. Wait calls validate that handlers observed input state and set output state; no-wait calls return `scf_check` objects later through a lockless per-CPU free pool.

Cleanup stops invokers, issues one final synchronous `smp_call_function()` to flush in-flight no-wait handlers, stops the stats thread, prints final counters, frees stats/free-pool objects, and reports success/failure based on atomic error counters and hotplug failures.

## State And Persistence
State is module-global and volatile: selection arrays, stats, task pointers, per-CPU invoked counts, per-CPU lockless free pools, atomic error counters, and `scfdone`. Module parameters are runtime configuration. The test produces printk output but no persistent artifacts.

## Dependencies And Integration Points
The file depends on torture framework helpers, kthreads, completions, lockless lists, CPU hotplug APIs, SRCU/RCU headers, SMP call-function APIs, scheduler preemption controls, and optional built-in-only `resched_cpu()`. It integrates with kernel module init/exit or built-in torture boot flows.

## Risks
Because this is stress code, risks include false positives under CPU hotplug races, leaked `scf_check` allocations when no-wait handlers are delayed, unsafe assumptions about CPU availability, and long-wait configurations that create extreme latency. The code deliberately uses `GFP_ATOMIC` and tolerates allocation failure, but allocation failure counts differ under KASAN. Memory-ordering checks depend on barriers and handler/caller conventions.

## Test Signals
Healthy runs print periodic and final `scf_invoked_count` statistics without `!!!`, with zero `ste`, `stnmie`, and `stnmoe` counters. `LOCK_HOTPLUG` signals hotplug torture failures. Workload coverage is visible through per-primitive counters and overflow counts. Boot/module unload should complete without leaks, hung kthreads, or WARN splats except expected stress warnings under injected failures.
