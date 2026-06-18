<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/general.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/general.json

## Purpose
Minimal Monaka general event topic selecting standard cycle counters. It exposes regular CPU cycles and constant-frequency counter cycles.

## APIs, Types, and Functions
The file has two `ArchStdEvent` entries: `CPU_CYCLES` and `CNT_CYCLES`, each with a Monaka description. There are no local event codes or executable functions.

## Control Flow, State, and Persistence
The standard aliases are resolved during generated PMU table construction. At runtime, perf uses them as ordinary event aliases once the Monaka CPU table is selected. The JSON itself is static configuration.

## Dependencies and Integration
Depends on the ARM64 common event catalog and the Monaka CPUID mapfile row. It integrates broadly with every other Monaka topic because cycle counts are denominators for stalls, IPC, cache MPKI, and utilization ratios.

## Risks and Test Signals
Risks are confusing variable CPU cycles with constant counter cycles and losing aliases if standard event names drift. Test signals are successful `jevents.py` generation, `perf stat -e CPU_CYCLES,CNT_CYCLES`, and ratio checks under frequency changes showing expected differences between clock-domain and constant-rate counting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/general.json -->
