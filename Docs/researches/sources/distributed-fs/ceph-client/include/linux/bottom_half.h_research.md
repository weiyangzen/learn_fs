# sources/distributed-fs/ceph-client/include/linux/bottom_half.h

Purpose: Defines the small bottom-half disable/enable API used to prevent softirq processing in critical sections. It hides differences between normal kernels, PREEMPT_RT, and IRQ flag tracing.

Important APIs/types/functions: `local_bh_disable()` calls `__local_bh_disable_ip(_THIS_IP_, SOFTIRQ_DISABLE_OFFSET)`. On non-RT/non-trace builds, `__local_bh_disable_ip()` is an inline `preempt_count_add(cnt)` plus compiler barrier. On PREEMPT_RT or IRQ trace builds it is an out-of-line function so extra tracking/locking semantics can be implemented. `_local_bh_enable()` and `__local_bh_enable_ip()` are externs, with `local_bh_enable_ip()` and `local_bh_enable()` as inline wrappers. `local_bh_blocked()` reports PREEMPT_RT state and is false otherwise.

Control flow: Callers bracket a softirq-sensitive region with `local_bh_disable()` and `local_bh_enable()`. The disable side increments preempt/softirq state immediately; the enable side may process pending softirqs or perform RT-specific unlock behavior in the implementation.

State/persistence: State is per-task/per-CPU preemption count and, on RT, extra bottom-half blocking state. It is intentionally transient and must be balanced.

Dependencies/integration: Depends on instruction pointer capture, preempt count definitions, softirq offset constants, PREEMPT_RT, and trace IRQFLAGS infrastructure. It is consumed by networking, timers, and any code needing bottom-half exclusion.

Risks/test signals: Risks are unbalanced disable/enable calls, sleeping in non-RT bottom-half-disabled regions, incorrect call-site IP for lockdep/trace diagnostics, and assuming RT semantics match non-RT. Test signals include lockdep, preempt-count underflow warnings, softirq latency tests, PREEMPT_RT boot/runtime tests, and networking stress with lockdep and IRQ tracing enabled.
