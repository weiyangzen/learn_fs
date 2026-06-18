<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/TimeException.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/TimeException.h

**Purpose:** Declares the named exception type used for fatal time/clock initialization failures.

**Important APIs/types/functions:** `DECLARE_NAMEDEXCEPTION(TimeException, "TimeException")`.

**Control flow:** The macro expands to an exception class consistent with BeeGFS named exception conventions. `Time::testClock` throws this type when even the safe monotonic clock fails.

**State and persistence behavior:** No state besides exception payload inherited from the macro-generated type.

**Dependencies and integration points:** Depends on `NamedException` and common headers. It keeps time errors distinguishable from generic config or system exceptions.

**Risks:** Macro-generated behavior is defined elsewhere, so changes to `NamedException` affect this type. It is very small and has no local tests.

**Test signals:** Compile-time use by `Time.cpp`; exception-specific tests should check type and message propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/TimeException.h -->
