<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/Time.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/Time.h

**Purpose:** Defines BeeGFS's coarse monotonic time wrapper for elapsed-time measurement, timeout arithmetic, ordering, and serialization.

**Important APIs/types/functions:** Constructors for now, zero/uninitialized, existing `timespec`, and copy; comparisons; assignment; `getIsZero`; `addMS`; virtual `setToNow`, `elapsedMS`, `elapsedMicro`; `elapsedSinceMS`, `elapsedSinceMicro`; static clock test methods and `getClockID`; `getTimeSpec`; and template `serialize`.

**Control flow:** Default construction captures `clock_gettime(clockID)`. Elapsed methods construct a fresh `Time` and subtract the stored timestamp. `addMS` normalizes nanoseconds above one second. Serialization writes seconds and nanoseconds as signed 64-bit values through serdes casts.

**State and persistence behavior:** Stores one `timespec` per instance and a static clock ID. Serialized form can persist or transmit monotonic timestamp values, though monotonic times are only meaningful relative to the same boot/session.

**Dependencies and integration points:** Used by retry logic, lock tests, thread timing, and timeout calculations. Depends on BeeGFS serialization helpers and POSIX clocks.

**Risks:** Elapsed calculations return unsigned and can underflow if the compared time is in the future. Microsecond elapsed can overflow for long intervals. Monotonic timestamps should not be interpreted as wall-clock times.

**Test signals:** `TestRWLock` uses `Time` heavily for ordering and runtime assertions. Dedicated tests should cover zero time, add normalization, serialization round trips, and future-time underflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/Time.h -->
