# sources/distributed-fs/ceph-client/arch/s390/include/asm/preempt.h

Purpose: This header implements s390 preempt-count handling with the inverted NEED_RESCHED bit folded into lowcore `preempt_count`.

Important APIs/types/functions: `PREEMPT_NEED_RESCHED`, `PREEMPT_ENABLED`, `preempt_count()`, `preempt_count_set()`, need-resched set/clear/test helpers, `__preempt_count_add/sub()`, `__preempt_count_dec_and_test()`, `should_resched()`, idle init stubs, and preempt schedule declarations/dynamic dispatch macros are defined.

Control flow: Fast paths read or update lowcore `preempt_count` directly, using alternatives for relocated lowcore and short immediate atomic instructions when possible. Decrement-and-test returns true when the count reaches the encoded resched-enabled value.

State and persistence: Persistent state is per-CPU lowcore `preempt_count`; dynamic preemption state lives in generic static calls/keys used by declared schedule functions.

Dependencies and integration points: It depends on current/thread info, atomic ops, cmpxchg, march features, lowcore, and scheduler preemption core.

Risks and test signals: The inverted bit convention is subtle: comparisons must mask or preserve it correctly. Tests should include preempt count debugging, voluntary/full/dynamic preemption configs, IRQ/softirq nesting, scheduler selftests, and relocated lowcore builds.
