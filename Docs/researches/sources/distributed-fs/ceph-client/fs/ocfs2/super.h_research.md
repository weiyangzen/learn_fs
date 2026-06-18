# sources/distributed-fs/ceph-client/fs/ocfs2/super.h

Purpose: provides the small public superblock/error interface shared by OCFS2 source files. It centralizes formatted filesystem error and abort reporting and exposes signal-mask helpers used around kernel threads or blocking sections.

Important APIs and types: declares `__ocfs2_error`, `ocfs2_error`, `__ocfs2_abort`, `ocfs2_abort`, `ocfs2_block_signals`, and `ocfs2_unblock_signals`. The macros pass `__PRETTY_FUNCTION__` into the underlying implementation so diagnostics identify the failing call site.

Control flow: callers invoke `ocfs2_error` for detected on-disk corruption that should follow the mount error policy, or `ocfs2_abort` for more critical journal-style failures. Signal helpers wrap `sigprocmask` to block all signals and later restore the saved mask.

State and persistence behavior: the header itself carries no state. Its functions in `super.c` set runtime error flags, may mark the VFS superblock read-only, may panic, and do not themselves repair metadata.

Dependencies and integration points: used by allocator, inode, journal, and metadata validation code to report corruption consistently. The error behavior depends on mount options stored in `struct ocfs2_super`.

Risks: choosing `ocfs2_error` versus `ocfs2_abort` affects whether the filesystem continues, remounts read-only, or panics. Signal helper misuse could leave kernel context with an incorrect signal mask, though the implementations BUG on impossible `sigprocmask` failures.

Test signals: corruption injection paths that call `ocfs2_error`, journal abort paths that call `ocfs2_abort`, mount options for all error policies, and lockdep/runtime checks around signal blocking and restoration.
