<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/poll/PollList.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/poll/PollList.h

**Purpose:** Declares the `PollList` fd-to-`Pollable*` container.

**Important APIs/types/functions:** Type aliases `PollMap`, `PollMapIter`, `PollMapVal`; class methods `add`, `remove`, `removeByFD`, `getPollableByFD`, and `getPollMap`.

**Control flow:** The header exposes the underlying map by pointer, allowing callers to iterate or build poll arrays externally.

**State and persistence behavior:** Holds only in-memory raw pointer mappings.

**Dependencies and integration points:** Depends on `Pollable` and BeeGFS common typedefs. Integrates with event loops that need to translate fd readiness back to owning objects.

**Risks:** Exposing `getPollMap` permits unsynchronized external mutation and invariant bypass. No ownership semantics are expressed.

**Test signals:** Compile and unit tests should ensure external map iteration matches add/remove behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/poll/PollList.h -->
