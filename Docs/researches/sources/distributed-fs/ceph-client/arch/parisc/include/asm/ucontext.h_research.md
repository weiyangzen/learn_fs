<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/ucontext.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/ucontext.h

Source read size: 13 lines, 327 bytes.

Purpose: provides the kernel-internal PA-RISC `ucontext` wrapper by including the UAPI signal-context contract. Important APIs and types: `struct ucontext` with flags, link pointer, stack, `struct sigcontext`, and signal mask. Control flow: signal setup and return code populate or consume this layout when building user signal frames. State and persistence: state is transient but user-visible on the signal stack; ABI layout persists across kernel versions. Dependencies and integration points: includes `uapi/asm/sigcontext.h` and `asm/sigmask.h`, and is consumed by `signal.c`, `signal32.c`, and `asm-offsets.c`. Risks: layout changes break signal ABI and unwind/debug tooling. Test signals: signal frame round trips, `sigaltstack`, `rt_sigreturn`, ptrace over signal stops, and compat signal tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/ucontext.h -->
