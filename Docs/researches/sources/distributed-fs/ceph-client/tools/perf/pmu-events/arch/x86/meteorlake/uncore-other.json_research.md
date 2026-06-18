# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/uncore-other.json

Purpose: defines the Meteor Lake package uncore clock event `UNC_CLOCK.SOCKET`, a 48-bit fixed counter for UCLK cycles.

Important APIs/types/functions: one static descriptor with `EventName` `UNC_CLOCK.SOCKET`, `EventCode` `0xff`, `Counter` `FIXED`, `Unit` `CNCU`, `PerPkg` `1`, and a brief description. The row is consumed by perf's PMU event generator; there are no functions.

Control flow: `jevents.py` emits the alias into generated tables. At runtime perf resolves the named event to the `CNCU` uncore PMU fixed counter and reads UCLK cycles for the socket/package during measurement.

State and persistence: no source-level state. The fixed counter is hardware state and package scoped. Perf may use it as an elapsed uncore-cycle denominator for ratios, but the JSON file only provides metadata.

Dependencies and integration points: depends on kernel support for the Meteor Lake `CNCU` PMU and fixed uncore counter access. Integrates with uncore cache, interconnect, and memory events as a normalization denominator for package-level activity.

Risks: because this is a fixed counter, treating it like a programmable event could cause scheduling or availability surprises. `PerPkg` and `Unit` are essential for correct scope. Counter width is described as 48-bit; long-running sessions must account for wraparound in lower layers.

Test signals: JSON validation, generated alias presence, `perf list` visibility, and a simple `perf stat -e UNC_CLOCK.SOCKET` run showing monotonically increasing uncore cycles. Long-duration tests can catch fixed-counter wrap or scaling issues.
