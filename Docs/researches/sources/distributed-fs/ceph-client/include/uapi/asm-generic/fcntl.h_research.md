# sources/distributed-fs/ceph-client/include/uapi/asm-generic/fcntl.h

Purpose: Defines generic UAPI open flags, fcntl command numbers, owner/lock constants, and file lock structures.

Important APIs/types/functions: Exports `O_*` flags, `F_*` fcntl commands including OFD locks, `F_OWNER_*`, `struct f_owner_ex`, `FD_CLOEXEC`, lock constants, `F_LINUX_SPECIFIC_BASE`, and generic `struct flock`/`struct flock64` unless an architecture overrides them.

Control flow: Preprocessor guards allow architectures to predefine flag or struct variants. `__BITS_PER_LONG` gates 64-bit lock commands for 32-bit userspace/kernel contexts.

State/persistence: No runtime state; constants and structures define syscall ABI for `open`, `fcntl`, `flock`, and lockf-like operations.

Dependencies/integration: Includes `linux/types.h`; consumed by libc and filesystem/syscall code.

Risks: Flag uniqueness is critical, as noted by the file. Struct layout and flag values are ABI-stable and architecture-sensitive.

Test signals: Headers ABI checks; compile and run open/fcntl/flock tests across 32-bit/64-bit user-space ABIs.
