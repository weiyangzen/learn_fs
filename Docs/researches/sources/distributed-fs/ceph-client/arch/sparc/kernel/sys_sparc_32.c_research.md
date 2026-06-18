# sources/distributed-fs/ceph-client/arch/sparc/kernel/sys_sparc_32.c

Purpose: provides 32-bit native SPARC implementations of SPARC-specific or ABI-unusual syscalls and mmap placement checks.

Important APIs/types/functions: `sys_getpagesize()`, `arch_get_unmapped_area()`, `sys_sparc_pipe()`, `sparc_mmap_check()`, `sys_mmap2()`, `sys_mmap()`, `sys_sparc_remap_file_pages()`, `sys_nis_syscall()`, `sparc_breakpoint()`, `sys_sparc_sigaction()`, `sys_rt_sigaction()`, and `sys_getdomainname()`.

Control flow: mmap placement enforces task-size limits and shared-cache aliasing alignment unless hugepage files supply their own mask. `sparc_pipe()` returns the second fd in register `UREG_I1`, matching SPARC ABI. `mmap2()` converts 4KB units to native pages; `mmap()` shifts byte offsets by `PAGE_SHIFT`; remap converts 4KB units. Legacy unsupported syscall logging is rate-limited by a static count. Breakpoints send `SIGTRAP`; signal-action wrappers handle SPARC's negative legacy signal convention and explicit restorer argument.

State and persistence: static `nis_syscall` count limits logs. Syscalls may create mappings, pipes, or VFS effects through generic helpers; the file owns no persistence.

Dependencies and integration points: generic MM/VFS/signal/UTS helpers, `current_pt_regs()`, SPARC register ABI, hugetlb alignment helpers, and syscall tables.

Risks: cache-color alignment is required for shared mappings. Offset conversions differ between `mmap` and `mmap2`. Domain-name copying must release `uts_sem` on all paths.

Test signals: native 32-bit mmap alignment and range failures, pipe register return ABI, signal action/restorer behavior, breakpoints, unsupported syscall logging capped after six messages, and getdomainname length/fault cases.
