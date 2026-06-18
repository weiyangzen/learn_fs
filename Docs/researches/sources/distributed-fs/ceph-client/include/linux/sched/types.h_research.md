# sources/distributed-fs/ceph-client/include/linux/sched/types.h

Purpose: defines common scheduler CPU-time aggregate types without pulling the full scheduler header.

Important APIs and types: `struct task_cputime` groups system time, user time, and total execution runtime in nanoseconds.

Control flow: accounting and timer code passes this structure between cputime collection, adjustment, POSIX CPU timers, and thread-group accounting.

State and persistence: the structure is a value container; persistent counters live in tasks or signal structs.

Dependencies and integration points: depends only on integer types. It is shared by scheduler, signal, POSIX timer, and accounting code.

Risks and test signals: risks include field-order assumptions, unit confusion, and overflow expectations for long-lived tasks. Test CPU accounting consumers and compile paths that need this type without full `sched.h`.
