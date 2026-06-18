# sources/distributed-fs/ceph-client/arch/sh/kernel/sys_sh.c

Purpose: implements SH-specific syscall wrappers with nonstandard ABI details.

Important APIs and control flow: `old_mmap()` validates page-aligned byte offset and delegates to `ksys_mmap_pgoff()`. `sys_mmap2()` delegates using page-offset units. `sys_cacheflush()` validates the requested range with `access_ok()` and calls `cacheflush_user_range()` for user-visible cache maintenance.

State, dependencies, and risks: no persistent state. Dependencies include syscall table entries, user access validation, mmap core, SH cacheflush operations, and cachectl ABI constants. Risks include offset overflow/ABI compatibility, user range validation gaps, and cacheflush semantics expected by JIT/self-modifying code. Test signals are mmap/mmap2 ABI tests, invalid offset/range errors, and user cacheflush correctness for generated code.
