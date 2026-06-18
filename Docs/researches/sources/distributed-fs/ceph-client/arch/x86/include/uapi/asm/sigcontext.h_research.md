<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/sigcontext.h

Purpose: Defines x86 signal-frame CPU, FPU, and extended xstate layouts for 32-bit and 64-bit userspace, including legacy compatibility structures and magic values for XSAVE-extended signal state.

Important APIs/types/functions: `FP_XSTATE_MAGIC1`, `FP_XSTATE_MAGIC2`, `struct _fpx_sw_bytes`, `_fpreg`, `_fpxreg`, `_xmmreg`, `_fpstate_32`, `_fpstate_64`, `_header`, `_ymmh_state`, `_xstate`, `struct sigcontext_32`, `struct sigcontext_64`, and userspace `struct sigcontext` variants.

Control flow: Signal delivery builds a signal frame containing general registers and a pointer to FPU/XSAVE state. Signal return validates and restores state; userspace signal handlers and context libraries may inspect or modify fields.

State and persistence behavior: Signal frames persist on the userspace stack until handler return. The extended xstate magic fields and size fields describe variable-sized CPU state that must be preserved by user context switching and checkpointing tools.

Dependencies and integration points: Depends on Linux compiler and UAPI types. Integrates with signal delivery/return, XSAVE, AVX/YMM state, AMX and future xfeatures, ptrace/core dumps, libc ucontext, CRIU, and old 32-bit/64-bit binaries.

Risks and test signals: Risks include breaking old sigcontext aliases, mishandling `fpstate` as `_xstate`, not preserving reserved fields, x32 pointer padding mistakes, and SS/FS/GS historical quirks. Test signal selftests with FP/AVX/AMX state, sigreturn validation, 32-bit and x32 handlers, CRIU restore, alternate signal stacks, and old user context libraries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/sigcontext.h -->
