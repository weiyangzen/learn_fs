# sources/distributed-fs/ceph-client/include/linux/sched/affinity.h

Purpose: compatibility include that exposes the scheduler affinity API by including `linux/sched.h`.

Important APIs and types: this file defines no new symbols; users get affinity helpers such as `set_cpus_allowed_ptr()`, `sched_setaffinity()`, `sched_getaffinity()`, and task CPU-mask fields from `sched.h`.

Control flow: including this header forwards compilation to the central scheduler header. Runtime behavior belongs to the affinity code declared there.

State and persistence: no state is owned here.

Dependencies and integration points: the dependency is intentionally broad because it pulls `linux/sched.h`. It preserves include-path compatibility for code that wants an affinity-themed header.

Risks and test signals: risk is header dependency churn or circular include exposure. Compile-test users that include only `sched/affinity.h` for affinity declarations.
