<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/ucontext.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/ucontext.h

Purpose: Defines RISC-V `ucontext_t` ABI wrapper for signal/user context.

Important APIs/types/functions: Defines `struct ucontext` fields including flags, link, stack, signal mask, and machine context.

Control flow: Signal setup populates ucontext; userspace signal handlers and `setcontext`-style code consume it.

State and persistence: Signal-frame ABI state.

Dependencies and integration points: Used by libc, signal delivery, sigreturn, and checkpoint/restore tooling.

Risks: Struct layout changes break user signal handlers and unwinding.

Test signals: Signal/ucontext libc tests, altstack, and headers ABI checks.

Source read size: 38 lines, 1348 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/ucontext.h -->
