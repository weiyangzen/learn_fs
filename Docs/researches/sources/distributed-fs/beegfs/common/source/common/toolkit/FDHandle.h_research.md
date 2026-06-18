<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/FDHandle.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/FDHandle.h

Purpose: RAII wrapper for POSIX file descriptors.

Important APIs/types: `FDHandle` owns an `int fd`, closes it in the destructor, supports move construction/assignment, `close`, `get`, `reset`, `valid`, and `swap`.

Control flow/state/persistence: Ownership transfer is move-only. `reset` closes the existing descriptor before replacing it. No file content persistence logic beyond descriptor lifetime.

Dependencies/integration: Used by `LockFD` and other low-level POSIX helpers.

Risks/test signals: `close` returns the system close result but destructor cannot report errors. Tests should cover move transfer, reset from valid/invalid descriptors, double close prevention, and valid state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/FDHandle.h -->
