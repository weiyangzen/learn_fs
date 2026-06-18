<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/run-in-irq-context.h -->
# sources/distributed-fs/ceph-client/include/kunit/run-in-irq-context.h

## Purpose
`run-in-irq-context.h` provides a KUnit helper for repeatedly running a test callback in task, softirq, and hardirq contexts. It is aimed at validating fallback paths that only execute when interrupt context or FPU/vector availability changes kernel behavior.

## Important APIs, types, and functions
`struct kunit_irq_test_state` stores the callback, caller state, failure flags for each context, atomic call counters, an adaptive `ktime_t` interval, a hard hrtimer, and a BH work item. `kunit_run_irq_test()` is the public inline helper. Internal callbacks are `kunit_irq_test_timer_func()` for hardirq context and `kunit_irq_test_bh_work_func()` for softirq context.

## Control flow
`kunit_run_irq_test()` initializes an on-stack hard hrtimer and BH work item, starts the timer, and loops in task context until `max_iterations` and at least one call from each context are observed, or one second elapses. The hrtimer callback asserts hardirq context, runs the test callback, forwards itself, and queues BH work. The BH worker asserts softirq context and runs the same callback.

## State and persistence behavior
All state is on the stack for one invocation and is cancelled/flushed before return. Atomic counters coordinate observations across contexts; boolean failure flags are sampled after all asynchronous work is drained.

## Dependencies and integration points
The header integrates KUnit assertions with `hrtimer`, `system_bh_wq`, `jiffies`, atomic counters, and interrupt-context predicates. Crypto and architecture KUnit tests can use it to exercise irq/FPU edge cases.

## Risks and test signals
Risks include callback code that is not reentrant, sleeps in interrupt context, or assumes only one caller. Very slow systems may hit the one-second timeout; the timer interval self-adjusts after repeated hardirq-only progress. Test signals are positive hardirq and softirq counters, failure flags remaining false, timer cancellation without pending work, and architecture tests that intentionally force fallback code paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/kunit/run-in-irq-context.h -->
