# sources/distributed-fs/ceph-client/include/asm-generic/audit_read.h

Purpose: Lists syscall numbers that read filesystem metadata or extended attributes for audit read classification.

Important APIs, types, and functions: Emits `readlink`, `readlinkat`, `quotactl`, listxattr/getxattr variants including `*xattrat`, and link-specific xattr variants.

Control flow: Architecture-specific preprocessor checks include available syscall numbers.

State and persistence: No runtime state; compiled tables use the emitted constants.

Dependencies and integration points: Integrated into audit syscall-class generation.

Risks and test signals: Risks include missing modern xattr-at syscalls or classifying quotactl inconsistently. Test audit read rules against xattr, readlink, and quota queries on architectures with and without at-style syscalls.
