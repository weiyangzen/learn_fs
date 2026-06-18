<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/prctl.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/prctl.h

Purpose: Defines x86 `arch_prctl` command numbers and feature bits for FS/GS base, CPUID faulting, extended xstate permission, vDSO mapping, LAM/tagged addresses, and user shadow stack control.

Important APIs/types/functions: `ARCH_SET_GS`, `ARCH_SET_FS`, `ARCH_GET_FS`, `ARCH_GET_GS`, `ARCH_GET_CPUID`, `ARCH_SET_CPUID`, `ARCH_GET_XCOMP_*`, `ARCH_REQ_XCOMP_*`, `ARCH_XCOMP_TILECFG`, `ARCH_XCOMP_TILEDATA`, `ARCH_MAP_VDSO_*`, `ARCH_GET_UNTAG_MASK`, `ARCH_ENABLE_TAGGED_ADDR`, `ARCH_GET_MAX_TAG_BITS`, `ARCH_FORCE_TAGGED_SVA`, `ARCH_SHSTK_*`, `ARCH_SHSTK_SHSTK`, and `ARCH_SHSTK_WRSS`.

Control flow: Userspace calls `arch_prctl`; kernel dispatches by command to mutate or query thread FS/GS base, CPUID execution policy, dynamic xstate permissions, vDSO placement, LAM tagging, or CET shadow-stack state.

State and persistence behavior: State persists per task or mm: FS/GS base, CPUID faulting mode, xstate permission bits, optional vDSO mapping, LAM mode, and shadow-stack enable/lock/status bits.

Dependencies and integration points: Integrates with TLS, context switching, CPUID faulting, AMX dynamic xstate, vDSO, Linear Address Masking, CET user shadow stacks, ptrace, and signal restore.

Risks and test signals: Risks include command-number collision, security policy bypass, and per-thread state not restored across fork/exec/signal. Test arch_prctl selftests, TLS runtimes, CPUID-faulting tests, AMX permission requests, LAM tagged-address tests, vDSO mapping tests, and shadow-stack enable/lock/unlock/status flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/prctl.h -->
