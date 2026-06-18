<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ucontext.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ucontext.h

Purpose: Defines x86 ucontext flags for extended FP/XSAVE state and 64-bit signal-context SS restore semantics before including generic ucontext.

Important APIs/types/functions: `UC_FP_XSTATE`, `UC_SIGCONTEXT_SS`, `UC_STRICT_RESTORE_SS`, and generic ucontext inclusion.

Control flow: Signal delivery sets flags in `ucontext`; sigreturn uses them to decide whether extended xstate is present and how strictly to restore SS on x86_64/x32.

State and persistence behavior: Ucontext lives on userspace signal frames and can be saved/restored by context libraries or checkpoint tools.

Dependencies and integration points: Integrates with signal delivery/return, sigcontext, XSAVE, espfix, old DOSEMU/CRIU compatibility, libc `ucontext_t`, and x32.

Risks and test signals: Risks include incorrect SS restore compatibility, missing xstate flag, and old userspace breakage. Test signal selftests, segmented-context sigreturn, CRIU restore, x32 signals, and FP/XSAVE signal frame handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ucontext.h -->
