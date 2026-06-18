<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/TimeAbs.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/TimeAbs.h

**Purpose:** Provides a wall-clock, epoch-based time wrapper using `gettimeofday`, intended for absolute timestamps rather than monotonic intervals.

**Important APIs/types/functions:** Constructors, comparisons, assignment, `setToNow`, `elapsedSinceMS`, `elapsedSinceMicro`, `elapsedMS`, `getTimeval`, `getTimeS`, `getTimeMS`, and `getTimeMicroSecPart`.

**Control flow:** Instances capture `gettimeofday`. Elapsed methods subtract an earlier `TimeAbs` from the stored timestamp. Accessors expose seconds, milliseconds, and the microsecond field.

**State and persistence behavior:** Holds a `timeval` that represents system wall clock time and may be persisted or displayed as epoch time. It can move backward or forward if system time changes.

**Dependencies and integration points:** Used where BeeGFS needs real timestamps rather than steady durations. Includes only common/POSIX time dependencies.

**Risks:** Wall-clock jumps can make elapsed calculations negative; unsigned returns can underflow. `getTimeval` exposes a mutable pointer to internal state. Microsecond elapsed can overflow for long intervals.

**Test signals:** Tests should cover epoch conversion, assignment/comparison, and behavior when earlier/later order is inverted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/TimeAbs.h -->
