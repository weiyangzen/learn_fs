<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestLockFD.cpp -->
## sources/distributed-fs/beegfs/common/tests/TestLockFD.cpp

**Purpose:** Tests `LockFD` file locking, duplicate lock failure, cleanup unlink behavior, and lock-file content updates.

**Important APIs/types/functions:** Fixture creates a temporary directory with `mkdtemp` and removes it with `StorageTk::removeDirRecursive`. Tests call `LockFD::lock`, `FDHandle`, POSIX `flock`, `access`, `update`, and `updateWithPID`.

**Control flow:** `testInitialLock` obtains a lock, opens the same file, and confirms a nonblocking exclusive flock fails with `EWOULDBLOCK`. `testLockTwice` verifies a second `LockFD::lock` fails with that error. `testDoesUnlink` releases the lock and expects the path to disappear. `testUpdate` checks content update failure/success semantics and PID writing.

**State and persistence behavior:** Creates and removes temporary lock files. Validates that lock file content reflects update calls and that released locks unlink their files.

**Dependencies and integration points:** Directly tests `LockFD`; indirectly uses `StorageTk` cleanup. Relevant to daemon pid files and working-directory locks used by `StorageTk`.

**Risks:** Relies on local filesystem flock semantics and temporary directories under current working directory. Tests may be sensitive to platform differences in advisory locking.

**Test signals:** Good coverage for lock exclusivity and PID file update behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestLockFD.cpp -->
