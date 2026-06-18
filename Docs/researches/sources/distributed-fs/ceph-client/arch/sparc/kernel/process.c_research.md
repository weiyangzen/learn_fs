# sources/distributed-fs/ceph-client/arch/sparc/kernel/process.c

Purpose: provides the architecture-neutral SPARC syscall wrappers for `fork`, `vfork`, `clone`, and `clone3`. It translates the SPARC register calling convention into `kernel_clone()` or `sys_clone3()` arguments and preserves SPARC's historical child/parent return-value convention.

Important APIs/functions: exported syscall entry helpers are `sparc_fork()`, `sparc_vfork()`, `sparc_clone()`, and `sparc_clone3()`. They build `struct kernel_clone_args`, call `synchronize_user_stack()` before cloning register-window state, and use `compat_ptr()` for 32-bit compat user pointers when `CONFIG_COMPAT` and `TIF_32BIT` apply.

Control flow: `fork` and `vfork` reuse the parent's frame pointer as the child stack, with `vfork` adding `CLONE_VFORK | CLONE_VM`. `clone` extracts flags, signal, TLS, parent/child TID pointers, and optional stack from incoming `%i` registers; if no child stack is supplied it falls back to the parent frame pointer. After `kernel_clone()`, all three legacy wrappers restore `%i1` if an error/restart code is returned because lower-level `copy_thread()` may have clobbered the parent's second return register. `clone3` passes the user `clone_args` pointer and size directly to `sys_clone3()`.

State and persistence: state is per-syscall only. The wrappers mutate the live `pt_regs` for `%i1` restoration and pass clone attributes onward; no persistent storage is touched.

Dependencies and integration points: depends on SPARC register-window synchronization, generic clone/fork implementation, compat pointer translation, signal constants, and `copy_thread()` in the 32-bit or 64-bit process files. It is the syscall ABI bridge used by assembly entry code.

Risks: restart handling is delicate because SPARC legacy fork/clone returns use `%o0/%o1` differently from generic Linux. Missing `synchronize_user_stack()` risks cloning stale register-window contents. Compat pointer handling must match the 32-bit ABI exactly.

Test signals: fork/vfork/clone/clone3 syscall tests on both native and compat tasks, clone with supplied and omitted stacks, `CLONE_SETTLS`, parent/child TID and pidfd paths, and forced `-ERESTART*` syscall restart cases that verify `%i1` restoration.
