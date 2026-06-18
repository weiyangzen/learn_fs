<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/TimeFine.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/TimeFine.h

**Purpose:** Defines a high-resolution monotonic time subclass for sub-millisecond elapsed measurements.

**Important APIs/types/functions:** Constructor, overridden `setToNow`, `elapsedMS`, and `elapsedMicro`.

**Control flow:** Construction calls `Time(false)` to skip base initialization, then captures `CLOCK_MONOTONIC` directly. Elapsed methods compare against a freshly constructed `TimeFine`, bypassing the possibly coarse static `Time::clockID`.

**State and persistence behavior:** Holds inherited `timespec` only. No persistence beyond any caller serialization through base facilities.

**Dependencies and integration points:** Used when coarse monotonic clock precision is insufficient. Shares base comparison and elapsed-since helpers with `Time`.

**Risks:** Always uses `CLOCK_MONOTONIC` and does not test availability itself. Same unsigned underflow/overflow concerns as `Time` apply.

**Test signals:** Tests should compare ordering and elapsed precision against `Time`, and verify override behavior after `Time::clockID` fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/TimeFine.h -->
