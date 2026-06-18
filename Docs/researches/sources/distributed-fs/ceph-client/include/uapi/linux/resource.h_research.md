<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/resource.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/resource.h

Purpose: defines generic resource-limit, resource-usage, and priority constants plus common `rusage`/`rlimit` structures for userspace resource accounting APIs.

Important APIs and types: `struct rusage` carries CPU time, RSS, page fault, block I/O, IPC, signal, and context-switch counters. `struct rlimit` and `struct rlimit64` carry soft/hard limits, with `RLIM64_INFINITY` as the 64-bit infinite value. Priority constants include `PRIO_MIN`, `PRIO_MAX`, and `PRIO_PROCESS/PGRP/USER`. `RUSAGE_SELF`, `RUSAGE_CHILDREN`, `RUSAGE_BOTH`, and `RUSAGE_THREAD` select usage scopes. `_STK_LIM` and `MLOCK_LIMIT` define default stack and locked-memory limits; `asm/resource.h` supplies architecture resource numbers and remaining limit constants.

Control flow: userspace calls `getpriority/setpriority`, `getrusage`, `getrlimit/setrlimit/prlimit64`; the kernel applies these constants to select target process/user/group or usage/limit scope.

State and persistence: resource limits are per process/credential state inherited across fork and usually preserved across exec. Usage counters accumulate per task/thread/process tree runtime state.

Dependencies and integration points: depends on arch UAPI `asm/resource.h`. Integrates with scheduler priority, signal/accounting, process resource limits, libc, shells, and container runtimes.

Risks and test signals: risks include architecture layout drift, signed priority range mistakes, inheritance semantics, and container/user namespace limit enforcement. Test get/set priority, rusage scopes, rlimit inheritance, prlimit permission checks, and cross-arch header exports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/resource.h -->
