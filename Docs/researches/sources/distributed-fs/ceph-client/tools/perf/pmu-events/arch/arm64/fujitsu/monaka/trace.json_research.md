<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/trace.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/trace.json

## Purpose
Monaka trace-related PMU topic selecting standard trace-buffer, trace trigger, external output, and CTI trigger events.

## APIs, Types, and Functions
The file contains `ArchStdEvent` entries for `TRB_WRAP`, `TRB_TRIG`, `TRCEXTOUT0`, and `CTI_TRIGOUT4`, each with a local description. There are no direct event codes or functions.

## Control Flow, State, and Persistence
`jevents.py` resolves the standard trace aliases during generated table construction. Runtime use depends on perf and hardware trace/CTI configuration; the JSON holds only static alias membership.

## Dependencies and Integration
Depends on ARM64 standard trace event definitions and Monaka PMU support. It integrates with tracing workflows that correlate PMU counts with CoreSight trace buffer wrap, trigger, and CTI signaling.

## Risks and Test Signals
Risks include trace infrastructure being disabled or unavailable, aliases resolving but counters staying zero without CoreSight setup, and CTI wiring being platform-specific. Test signals are alias generation, trace sessions that cause buffer wraps or trigger events, and platform validation of external trigger routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/trace.json -->
