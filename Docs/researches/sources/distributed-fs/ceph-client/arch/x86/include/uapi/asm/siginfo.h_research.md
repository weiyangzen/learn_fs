<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/siginfo.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/siginfo.h

Purpose: Provides x32-specific `siginfo` alignment/type overrides before including the generic siginfo UAPI.

Important APIs/types/functions: `__kernel_si_clock_t`, `__ARCH_SI_CLOCK_T`, `__ARCH_SI_ATTRIBUTES`, and inclusion of `asm-generic/siginfo.h`.

Control flow: Signal-generation paths fill generic siginfo structures; x32 uses the alignment/type overrides selected here.

State and persistence behavior: `siginfo_t` is transient signal-delivery state but its layout is a stable userspace ABI.

Dependencies and integration points: Integrates with signal delivery, timers, x32 ABI, libc, ptrace signal injection, and generic siginfo definitions.

Risks and test signals: Risks are x32 alignment mismatch and timer clock type layout changes. Test signal delivery and POSIX timers under x32 plus ABI alignment assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/siginfo.h -->
