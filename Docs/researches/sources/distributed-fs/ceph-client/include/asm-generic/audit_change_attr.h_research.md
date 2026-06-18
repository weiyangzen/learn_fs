# sources/distributed-fs/ceph-client/include/asm-generic/audit_change_attr.h

Purpose: Lists syscall numbers that change file attributes for generic audit syscall class construction.

Important APIs, types, and functions: Emits conditional entries for chmod/chown/fchown variants, xattr set/remove variants including `*xattrat`, `fchmodat`, `fchmodat2`, 32-bit ownership calls, and link/linkat.

Control flow: Preprocessor conditionals include only syscalls defined by the architecture ABI.

State and persistence: No runtime state. The resulting compiled audit class table is persistent kernel metadata.

Dependencies and integration points: Included by audit architecture syscall-class definitions after syscall numbers are available. Integrates with Linux audit filtering for attribute-changing operations.

Risks and test signals: Risks include missing new attribute-changing syscalls, architecture syscall-name differences, and over/under-auditing. Test audit rules for chmod/chown/xattr/link syscalls on multiple architectures and verify new syscall additions update the list.
