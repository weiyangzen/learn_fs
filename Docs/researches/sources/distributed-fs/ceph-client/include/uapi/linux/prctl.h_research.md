<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/prctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/prctl.h

Purpose: defines the large `prctl(2)` command namespace for per-process and per-thread controls spanning signals, credentials, seccomp, capabilities, memory layout, architecture features, speculation mitigations, scheduling, memory execution policy, timers, futex/rseq, and CFI.

Important APIs and types: early commands cover parent-death signal, dumpability, unaligned/FPU behavior, keepcaps, process name, endian, seccomp, capability bounding/ambient sets, TSC, securebits, timerslack, perf events, MCE kill, and `PR_SET_MM` with `struct prctl_mm_map`. Later commands include ptracer control, subreaper, no-new-privs, THP disable, FP modes, SVE/SME vector length, speculation controls, PAC, tagged address/MTE/RISC-V pointer masks, IO flusher, syscall user dispatch, scheduler core sharing, MDWE, VMA naming, auxv retrieval, memory merge, RISC-V vector/icache controls, PowerPC DEXCR, shadow stack, timer restore IDs, futex hash, rseq slice extension, and branch-landing-pad CFI.

Control flow: userspace calls `prctl(option, arg2, arg3, arg4, arg5)`. The kernel dispatches on `option`, validates privilege and architecture support, mutates task/mm/security/arch state, or returns current settings. Several controls are inherited across fork/exec or have explicit on-exec bits.

State and persistence: state is per task, thread group, mm, credentials, security state, or architecture context. Most settings persist for process/thread lifetime and may inherit across fork/exec depending on command-specific flags; none are durable after process exit.

Dependencies and integration points: depends on Linux types and bit helpers. Integrates with scheduler, LSM/commoncap, seccomp, perf, MM, CRIU, ptrace/Yama, architecture-specific vector/tag/PAC/DEXCR/shadow-stack code, futex, rseq, and libc process-control wrappers.

Risks and test signals: risks are severe because this is security- and ABI-sensitive: option number stability, privilege enforcement, inheritance semantics, architecture config gating, pointer validation, and irreversible locks. Test each command family with positive/negative permissions, fork/exec inheritance, seccomp/no-new-privs interactions, CRIU `PR_SET_MM`, arch selftests for SVE/SME/MTE/RISC-V/PowerPC/shadow stack, MDWE enforcement, and unknown option rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/prctl.h -->
