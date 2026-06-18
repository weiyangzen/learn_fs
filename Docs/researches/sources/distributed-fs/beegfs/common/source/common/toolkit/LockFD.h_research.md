<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/LockFD.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/LockFD.h

Purpose: Declares an RAII lock-file handle.

Important APIs/types: `LockFD` is final and move-only, stores `path` and `FDHandle`, and exposes `lock`, `update`, `updateWithPID`, `valid`, and `swap`.

Control flow/state/persistence: Lock ownership follows fd ownership. File contents can be updated after acquisition when opened for update.

Dependencies/integration: Depends on `FDHandle` and `nu::error_or`. Used by daemon/process coordination code.

Risks/test signals: Move semantics should preserve single ownership. Tests should cover invalid handles, swap, update without write permission, and destructor unlock through fd close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/LockFD.h -->
