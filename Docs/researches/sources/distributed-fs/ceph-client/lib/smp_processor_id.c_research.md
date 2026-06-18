# sources/distributed-fs/ceph-client/lib/smp_processor_id.c

## Purpose
Provides the DEBUG_PREEMPT implementation behind `smp_processor_id()` diagnostics. It detects callers that read CPU-local identity from preemptible context where migration could make the answer unstable.

## APIs, Control Flow, and State
Exports `debug_smp_processor_id()` and `__this_cpu_preempt_check()`, both routed through `check_preemption_disabled()`. The checker accepts contexts where CPU locality is valid: non-zero preempt count, interrupts disabled, per-CPU kernel threads, migration disabled, or early boot before scheduling. Otherwise it disables preemption without tracing, enters an instrumentation-safe region, rate-limits a BUG diagnostic, prints the caller and stack, then reenables preemption without rescheduling. It returns `raw_smp_processor_id()` regardless so the caller can continue.

There is no durable state beyond printk rate limiting and current task scheduler fields.

## Dependencies, Integration, Risks, and Tests
Depends on scheduler/preemption state, current task metadata, printk, stack dumping, noinstr constraints, and export support. Integration points are debug builds of per-CPU accessors and `this_cpu` checks. Risks include false positives if a new context type legitimately pins CPU locality but is not recognized, recursion through printk or tracing, and missing diagnostics if rate limiting suppresses repeated bugs. Test signals include DEBUG_PREEMPT boot tests, intentional misuse probes, noinstr/objtool validation, and scheduler migration tests that call CPU-local helpers under allowed and disallowed contexts.
