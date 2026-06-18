# sources/distributed-fs/ceph-client/include/uapi/asm-generic/errno-base.h

Purpose: Defines the base POSIX/Linux errno values 1-34 for generic UAPI.

Important APIs/types/functions: Exports macros such as `EPERM`, `ENOENT`, `EINTR`, `EIO`, `EAGAIN`, `ENOMEM`, `EACCES`, `EINVAL`, `EMFILE`, `ENOSPC`, `EPIPE`, `EDOM`, and `ERANGE`.

Control flow: Preprocessor constants only; included by `asm-generic/errno.h` and user-space headers.

State/persistence: No state; constants are ABI.

Dependencies/integration: Baseline errno namespace for architectures using generic error numbering.

Risks: Numeric changes are ABI-breaking. Comments are less critical than values but influence user understanding.

Test signals: User-space compile checks and ABI comparison against expected errno values.
