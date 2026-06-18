# sources/distributed-fs/ceph-client/include/asm-generic/audit_dir_write.h

Purpose: Lists directory-modifying syscall numbers for generic audit write-directory classification.

Important APIs, types, and functions: Conditionally emits `rename`, `mkdir`, `rmdir`, `creat`, `link`, `unlink`, `symlink`, `mknod`, `mkdirat`, `mknodat`, `unlinkat`, `renameat`, `linkat`, `symlinkat`, and `renameat2`.

Control flow: Compile-time syscall-number conditionals tailor the list to each architecture ABI.

State and persistence: No runtime state; contributes constants to audit class tables.

Dependencies and integration points: Used by audit syscall filters to identify directory write operations across architectures.

Risks and test signals: Risks are omitted syscalls causing audit gaps and including nonexistent syscalls causing build failures. Test audit directory watches for create/delete/rename/link operations and architecture builds with sparse syscall sets.
