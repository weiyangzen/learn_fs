# sources/distributed-fs/ceph-client/arch/sh/kernel/sys_sh32.c

Purpose: provides 32-bit SH syscall wrappers for ABI return/register conventions and split 64-bit arguments.

Important APIs and control flow: `sys_sh_pipe()` calls `do_pipe_flags()`, returns the first fd in r0 and writes the second fd to saved r1. `sys_pread_wrapper()` and `sys_pwrite_wrapper()` reconstruct 64-bit file offsets from split 32-bit registers and call `ksys_pread64()`/`ksys_pwrite64()`. `sys_fadvise64_64_wrapper()` reconstructs split offset and length arguments for `ksys_fadvise64_64()`.

State, dependencies, and risks: state is only the current syscall `pt_regs` return registers. Dependencies include 32-bit syscall argument ordering, VFS helpers, and entry code preserving r1. Risks include wrong high/low word ordering and pipe ABI compatibility. Test signals are libc pipe convention, pread/pwrite/fadvise with offsets above 4 GiB, and syscall table argument ABI tests.
