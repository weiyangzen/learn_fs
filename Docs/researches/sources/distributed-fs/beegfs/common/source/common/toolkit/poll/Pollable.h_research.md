<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/poll/Pollable.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/poll/Pollable.h

**Purpose:** Defines the abstract interface for objects that can expose a file descriptor to polling code.

**Important APIs/types/functions:** Virtual destructor and pure virtual `int getFD() const`.

**Control flow:** Implementers return a descriptor suitable for `poll` and `select`; `PollList` and event loops consume the descriptor.

**State and persistence behavior:** Interface-only; no state.

**Dependencies and integration points:** It is the base contract for fd-backed sockets, pipes, or other pollable resources in BeeGFS common code.

**Risks:** The interface cannot express descriptor lifetime, ownership, readiness semantics, or invalid fd states. Callers must handle stale descriptors externally.

**Test signals:** Mock implementations are sufficient for tests of `PollList` and poll dispatchers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/poll/Pollable.h -->
