<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/ucontext.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/ucontext.h

Purpose: defines LoongArch `ucontext_t` ABI for signal handlers and user context APIs.
Important APIs and types: declares `struct ucontext` with flags, link pointer, stack, sigmask, sigcontext, and extension-space fields.
Control flow: signal delivery fills the structure; user handlers and `rt_sigreturn` consume it to inspect or restore context.
State and persistence: stored on user stacks as ABI-visible signal context state.
Dependencies and integration: aligns with `sigcontext.h`, signal frame setup, libc `ucontext_t`, and debugger expectations.
Risks and test signals: layout mismatch breaks signal handling and context switching libraries. Signals include signal ABI tests, `getcontext` consumers where present, and GDB signal unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/ucontext.h -->
