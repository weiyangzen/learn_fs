# sources/distributed-fs/ceph-client/include/asm-generic/audit_write.h

Purpose: Builds a generic audit write syscall class by including directory writes and adding other filesystem-affecting write syscalls.

Important APIs, types, and functions: Includes `audit_dir_write.h`, then emits `acct`, `swapon`, `quotactl`, truncation variants, socket `bind`, and `fallocate` where defined.

Control flow: Compile-time syscall-number checks specialize the list.

State and persistence: No runtime state; contributes to audit syscall class tables.

Dependencies and integration points: Depends on syscall numbers and directory-write fragment. Integrates with Linux audit watches and syscall filtering.

Risks and test signals: Risks include broad or narrow write classification, especially `bind` for filesystem namespace sockets and quota/fallocate effects. Test audit write rules for directory operations, truncation, fallocate, swapon, and Unix socket bind paths.
