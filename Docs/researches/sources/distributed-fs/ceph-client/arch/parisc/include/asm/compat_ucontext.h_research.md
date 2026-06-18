# sources/distributed-fs/ceph-client/arch/parisc/include/asm/compat_ucontext.h

Purpose: defines the PA-RISC 32-bit compatible `ucontext` layout for signal frames on 64-bit kernels.

Important APIs/types/functions: `struct compat_ucontext` contains compat flags, link pointer, stack, signal mask, and machine context fields used by signal delivery and return.

Control flow: compat signal setup writes this structure to userspace; signal return reads it back to restore register and mask state.

State and persistence: the structure persists on the user stack for the lifetime of a delivered signal frame. Dependencies and integration: depends on `linux/compat.h`, PA-RISC signal context, and syscall/signal return code.

Risks and test signals: wrong padding or field order breaks user signal handlers. Test with 32-bit signal stress, alternate signal stacks, nested signals, and `sigreturn` validation.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
