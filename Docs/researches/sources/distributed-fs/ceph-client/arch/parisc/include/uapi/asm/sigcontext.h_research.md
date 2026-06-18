<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/sigcontext.h

Source read size: 21 lines, 557 bytes.

Purpose: defines the PA-RISC user signal context saved in signal frames. Important APIs/types: `PARISC_SC_FLAG_ONSTACK`, `PARISC_SC_FLAG_IN_SYSCALL`, and `struct sigcontext` with flags, general registers, floating-point registers, instruction space/offset queues, and SAR. Control flow: signal delivery fills the structure; `rt_sigreturn` restores user state from it. State and persistence: signal frame state exists on the user stack until consumed and is user-visible ABI. Dependencies and integration points: `signal.c`, `signal32.c`, `entry.S`, ptrace, debuggers, and libc signal trampolines. Risks: incomplete or changed register state corrupts signal return or debugger unwinding; flags encode syscall interruption semantics. Test signals: signal delivery/return, altstack, interrupted syscall restart, FP register preservation, and ptrace over signal frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/sigcontext.h -->
