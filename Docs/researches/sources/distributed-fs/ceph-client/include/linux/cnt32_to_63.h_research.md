# sources/distributed-fs/ceph-client/include/linux/cnt32_to_63.h

Purpose: This header provides a lock-free macro to extend a frequently sampled 32-bit hardware counter into a 63-bit monotonic-ish value for uses such as `sched_clock`.

Important APIs/types/functions: It defines endian-aware `union cnt32_to_63` and macro `cnt32_to_63(cnt_lo)`. The macro uses a static high word, a read memory barrier, sign-bit comparison between high and low halves, and updates the high word when the 32-bit counter crosses half-period.

Control flow: Callers pass a direct hardware counter expression to `cnt32_to_63`. The macro reads cached high state, barriers, evaluates the low counter, conditionally updates the high word when top bits differ, and returns the combined 64-bit value with bit 63 considered garbage.

State and persistence behavior: Each macro expansion site owns a `static u32 __m_cnt_hi`, so state is per call site. Correctness requires calls at least once per half period and no preemption longer than the half-period margin described in the comment.

Dependencies and integration points: It includes compiler/types and byteorder headers. It integrates with clocksource/sched_clock-style code using 32-bit free-running counters.

Risks: Passing a pre-read variable rather than a globally increasing counter expression violates the macro’s ordering requirement. Missing the half-period call frequency can lose wraps. Call-site-local static state means multiple call sites do not share extension history.

Test signals: Counter wrap simulation, high-frequency sampling, preemption stress, endian build coverage, sched_clock monotonicity tests, and explicit clearing/masking of bit 63 when callers need a true nonnegative value validate behavior.
