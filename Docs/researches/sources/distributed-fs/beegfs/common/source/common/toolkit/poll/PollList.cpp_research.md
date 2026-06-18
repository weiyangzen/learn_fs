<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/poll/PollList.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/poll/PollList.cpp

**Purpose:** Implements a minimal map from file descriptors to `Pollable` objects.

**Important APIs/types/functions:** `add`, `remove`, `removeByFD`, and `getPollableByFD`.

**Control flow:** `add` inserts the pollable under `pollable->getFD()`. `remove` delegates to `removeByFD`. Lookup returns `NULL` when the fd is absent.

**State and persistence behavior:** Mutates an in-memory `std::map<int, Pollable*>`. It does not own pollable objects or persist state.

**Dependencies and integration points:** Used by code that builds `poll`/`select` dispatch tables over objects implementing `Pollable`.

**Risks:** `insert` does not replace an existing fd mapping, so adding a second object with the same fd silently leaves the old mapping. Raw pointers require external lifetime management. No synchronization.

**Test signals:** Tests should cover duplicate fd insertion, removal by pointer/fd, absent lookup, and lifetime expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/poll/PollList.cpp -->
