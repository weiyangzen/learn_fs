<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/prctl.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/prctl.h

Purpose: this header defines numeric operations and sub-flags for the `prctl(2)` process-control syscall. It covers process attributes, security controls, architecture features, memory-map manipulation, scheduler-core controls, and recent architecture extensions.

Important APIs/types: it is mostly macro constants (`PR_SET_*`, `PR_GET_*`) plus `struct prctl_mm_map` for `PR_SET_MM_MAP`. Major groups include death signal, dumpability, unaligned/FPU/endian controls, keepcaps/capability bounding/ambient caps, seccomp, timerslack, perf event enable/disable, memory corruption policy, checkpoint/restore MM mutation, `no_new_privs`, THP disable, SVE/SME vector length, speculation controls, pointer authentication, tagged address/MTE/RISC-V pointer masking, syscall user dispatch, core scheduling, MDWE, named VMAs, memory merge, RISC-V vector and icache controls, PowerPC DEXCR, shadow stack status, timer restore IDs, and futex hash sizing.

Control flow: userspace calls `prctl(option, arg2, arg3, arg4, arg5)`, and the kernel dispatches by option. Some options set persistent per-thread or per-mm state, some query into user pointers, and some affect later `execve`, signal, scheduling, or memory behavior.

State and persistence: many settings persist per task, thread group, mm, or across exec when flagged. ABI stability is numeric: removed features such as MPX retain reserved numbers.

Dependencies/integration: depends on `linux/types.h`; integrated by runtimes, sandboxes, CRIU, language VMs, architecture feature probes, and security hardening code. `seccomp.h` supplies related filter-mode constants.

Risks and test signals: risk comes from architecture-specific availability, privilege checks, pointer arguments, inheritance semantics, and option numbers being permanent. Tests should cover expected `EINVAL`/`EPERM`, get-after-set behavior, exec inheritance flags, and per-architecture guarded options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/prctl.h -->
