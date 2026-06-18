# sources/distributed-fs/ceph-client/include/uapi/asm-generic/errno.h

Purpose: Extends base errno definitions with generic Linux error numbers 35-133 and aliases.

Important APIs/types/functions: Includes `errno-base.h`; defines `EDEADLK`, `ENOSYS`, networking errors (`ENOTSOCK`, `ECONNRESET`, `ETIMEDOUT`, etc.), filesystem/media/key errors (`ESTALE`, `EUCLEAN`, `ENOKEY`, etc.), robust mutex errors, `ERFKILL`, and `EHWPOISON`. Also aliases `EWOULDBLOCK` to `EAGAIN`, `EDEADLOCK` to `EDEADLK`, and `EFSCORRUPTED` to `EUCLEAN`.

Control flow: Preprocessor-only ABI definitions.

State/persistence: No runtime state; values are user-kernel ABI.

Dependencies/integration: Used by libc/kernel headers for generic architectures and syscall error reporting.

Risks: Returning `ENOSYS` from real syscalls is explicitly discouraged because arch syscall entry uses it for nonexistent syscalls. Numeric changes are ABI-breaking.

Test signals: Header ABI checks and userspace compile/runtime errno value comparisons.
