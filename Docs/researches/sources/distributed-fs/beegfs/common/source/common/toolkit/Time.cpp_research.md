<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/Time.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/Time.cpp

**Purpose:** Implements global clock selection and validation for the monotonic `Time` class.

**Important APIs/types/functions:** Static `Time::clockID`, `Time::testClock`, and `Time::testClockID`.

**Control flow:** `testClock` calls `clock_gettime` using the current default clock. If it fails and the current clock is not the safe clock, it switches to `CLOCK_MONOTONIC` and retries. If the safe clock fails, it throws `TimeException`. `testClockID` simply returns whether `clock_gettime` succeeds for a supplied id.

**State and persistence behavior:** Mutates process-global `Time::clockID` if the preferred coarse monotonic clock is unavailable. No persistence.

**Dependencies and integration points:** Depends on `System::getErrString`, `TimeException`, and POSIX clocks. All `Time` instances use the selected static clock unless derived classes override.

**Risks:** `clockID` is a mutable static without synchronization; clock testing should happen during startup before concurrent use. The unreachable `return false` after throw is defensive only.

**Test signals:** Tests should force or mock invalid clock IDs where possible, verify fallback to safe clock, and confirm `TimeFine` remains independent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/Time.cpp -->
