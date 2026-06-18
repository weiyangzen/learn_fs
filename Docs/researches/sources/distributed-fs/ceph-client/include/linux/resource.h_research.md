# sources/distributed-fs/ceph-client/include/linux/resource.h

Purpose: this header bridges kernel-internal resource-limit/rusage support to the UAPI resource definitions.

Important APIs/types/functions: it includes `uapi/linux/resource.h`, forward-declares `struct task_struct`, and declares `getrusage(struct task_struct *p, int who, struct rusage *ru)`.

Control flow: syscall or proc code calls `getrusage()` for a task and selector such as self/children/thread, filling a UAPI `struct rusage`. Implementation lives elsewhere.

State and persistence: no state is owned by the header. The reported data comes from task accounting fields and process/thread-group state.

Dependencies and integration points: integrates with task accounting, UAPI resource constants, wait/exit accounting, and syscall implementations for `getrusage`.

Risks: this header is small, but ABI coupling to `struct rusage` is strict. Test signals include `getrusage(2)` syscall tests for self/children/thread, compatibility ABI checks, and accounting correctness under CPU time and fault-heavy workloads.
