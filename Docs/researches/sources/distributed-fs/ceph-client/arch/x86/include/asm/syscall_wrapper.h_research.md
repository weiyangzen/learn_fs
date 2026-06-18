<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/syscall_wrapper.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/syscall_wrapper.h

Purpose: generates x86 syscall wrapper functions that decode `pt_regs`, invoke typed syscall implementations, and support native and compat syscall tables. Important macros include `__SYSCALL_DEFINEx`, `COMPAT_SYSCALL_DEFINEx`, register argument extraction macros, aliasing helpers, and conditional wrappers for `CONFIG_ARCH_HAS_SYSCALL_WRAPPER`.

Control flow: entry code dispatches to generated wrapper symbols; wrappers pull arguments from ABI-specific registers, call `__do_sys_*` functions, then return long results. Compat wrappers convert 32-bit argument types as required.

State and persistence: no persistent state; wrappers operate on syscall regs and user arguments. Dependencies include syscall metadata generation, ptrace register layout, compat types, asmlinkage conventions, and tracing/syscall table build logic. Risks include wrong argument order/sign-extension, symbol alias mismatches, and tracing metadata drift. Test signals include syscall ABI selftests, compat syscalls, strace argument decoding, generated table builds, and allnoconfig/compat configuration coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/syscall_wrapper.h -->
