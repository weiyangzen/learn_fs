<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/Pipe.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/Pipe.h

**Purpose:** Wraps a POSIX pipe as two BeeGFS `FileDescriptor` objects with optional thread-safe read and write sides.

**Important APIs/types/functions:** Constructor `Pipe(bool threadsafeReadside, bool threadsafeWriteside)`, destructor, `getReadFD`, `getWriteFD`, and `waitForIncomingData(int timeoutMS)`. Constants define read/write fd indices.

**Control flow:** Construction initializes fd slots to `-1`, calls `pipe`, and wraps both descriptors. Destruction deletes wrappers and closes both raw descriptors. `waitForIncomingData` polls the read side for `POLLIN`, returns false only on timeout, and returns true for readiness or error so callers can read and observe the actual error.

**State and persistence behavior:** Holds process-local file descriptors and wrapper objects only. It does not persist data beyond the kernel pipe buffer.

**Dependencies and integration points:** Depends on `FileDescriptor`, POSIX `pipe`, `poll`, and `close`. It is suitable for intra-process wakeups or producer/consumer coordination where BeeGFS code expects `FileDescriptor`.

**Risks:** The constructor ignores `pipe` failure and still creates wrappers around `-1`, so callers must be careful in low-fd or resource-exhaustion scenarios. Ownership is raw-pointer based. Closing after deleting `FileDescriptor` may double-close if the wrapper also owns the fd; that depends on `FileDescriptor` semantics outside this file.

**Test signals:** No direct tests in this subset. Tests should simulate data readiness, timeout, fd creation failure if possible, and descriptor lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/Pipe.h -->
