# sources/distributed-fs/ceph-client/arch/sparc/kernel/systbls.h

Purpose: declares SPARC-specific syscall entry points and compat wrappers used by syscall tables and assembly entry code.

Important APIs/types/functions: declares native helpers such as `sys_getpagesize()`, `sys_sparc_pipe()`, `sys_nis_syscall()`, `sys_getdomainname()`, `do_rt_sigreturn()`, `sys_mmap()`, and `sparc_breakpoint()`. Under `CONFIG_SPARC32` it declares `sys_mmap2()` and `sys_sparc_remap_file_pages()`. Under `CONFIG_SPARC64` it declares `sys_sparc_ipc()`, `sparc64_personality()`, `sys64_munmap()`, `sys64_mremap()`, `sys_utrap_install()`, context functions, and many compat large-file/stat/io wrappers.

Control flow: no runtime flow; it provides prototypes to keep C and assembly-visible syscall symbols consistent.

State and persistence: none.

Dependencies and integration points: included by syscall C files and table assembly, and depends on `asm/utrap.h`, `linux/compat.h`, `linux/signal.h`, and syscall ABI types.

Risks: duplicate or mismatched prototypes can hide ABI/signature bugs until link or runtime. Conditional blocks must match the objects built for 32-bit versus 64-bit kernels.

Test signals: sparse/build warnings for syscall prototype mismatches, successful native/compat table assembly, and no undefined symbols from syscall tables.
