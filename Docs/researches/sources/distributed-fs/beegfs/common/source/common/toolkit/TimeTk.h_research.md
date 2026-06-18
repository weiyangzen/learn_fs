<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/TimeTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/TimeTk.h

**Purpose:** Provides `std::chrono` helper aliases and stream formatting utilities for durations.

**Important APIs/types/functions:** `highest_resolution_steady_clock`, `as_double_duration`, `operator<<` for `std::chrono::duration`, `print_nice_time_t`, `operator<<` for nice printing, and `print_nice_time`.

**Control flow:** The duration stream operator prints count plus a unit derived from the period, with specializations for ns, microseconds, ms, s, min, and hr. `print_nice_time` chooses the largest unit whose duration exceeds three of that unit, falling back to the original duration.

**State and persistence behavior:** Stateless formatting helpers. No persistence.

**Dependencies and integration points:** Integrates standard chrono code with BeeGFS logging/CLI output. `highest_resolution_steady_clock` chooses high-resolution clock only if it is steady, otherwise steady clock.

**Risks:** The microsecond unit literal uses a non-ASCII symbol, which can matter for terminals or logs. Threshold comparisons use `>` rather than `>=`, so exactly three units prints in the next smaller unit. It overloads `operator<<` for standard duration in namespace `TimeTk`, so callers need namespace visibility.

**Test signals:** Formatting tests should cover SI unit specializations, generic ratio formatting, and nice-time thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/TimeTk.h -->
