<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/LockFD.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/LockFD.cpp

Purpose: Implements file-based process locking and lock-file content updates.

Important APIs/functions: `LockFD::lock(path, forUpdate)` opens/truncates/creates a path and takes a non-blocking flock-style lock through `flock`. `update` rewrites lock-file contents. `updateWithPID` writes the current PID.

Control flow/state/persistence: Successful lock returns an owning `LockFD` with an `FDHandle`. `update` writes new content to the lock file and truncates/resets as needed. Persistent effect is lock-file contents; lock lifetime is fd lifetime.

Dependencies/integration: Uses POSIX `open`, `flock`, `write`, `ftruncate`, `lseek`, `FDHandle`, and `nu::error_or`.

Risks/test signals: `O_TRUNC` before lock acquisition can erase another process's lock-file content. Tests should cover contention, update errors, read-only mode, PID writes, and fd close unlock behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/LockFD.cpp -->
