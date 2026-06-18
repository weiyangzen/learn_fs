# sources/distributed-fs/ceph-client/include/linux/sched/cond_resched.h

Purpose: compatibility include for conditional reschedule helpers.

Important APIs and types: the file defines no new symbols; it exposes `cond_resched()`, `cond_resched_lock()`, and rwlock variants from `linux/sched.h`.

Control flow: callers include this narrow header but compile against the central scheduler declarations. Actual voluntary preemption behavior is implemented through `sched.h` and scheduler core.

State and persistence: no state is stored here.

Dependencies and integration points: depends entirely on `linux/sched.h`; useful for code that wants to name the latency-reduction dependency explicitly.

Risks and test signals: risk is include bloat or circular inclusion after scheduler header refactors. Compile-test source files including this header alone.
