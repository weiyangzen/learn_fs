<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/stall.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/stall.json

## Purpose
Monaka stall taxonomy table. It selects ARM64 standard topdown-style stall aliases for frontend, backend, slot-level, memory-bound, cache/TLB-bound, core-bound, rename, flow, flush, busy, store, atomic, and memory-copy/set stall causes.

## APIs, Types, and Functions
All records are `ArchStdEvent` aliases with Monaka descriptions. Key aliases are `STALL_FRONTEND`, `STALL_BACKEND`, `STALL`, `STALL_SLOT_BACKEND`, `STALL_SLOT_FRONTEND`, `STALL_SLOT`, `STALL_BACKEND_MEM`, `STALL_FRONTEND_MEMBOUND`, `STALL_FRONTEND_L1I`, `STALL_FRONTEND_L2I`, `STALL_BACKEND_L1D`, `STALL_BACKEND_L2D`, `STALL_BACKEND_BUSY`, and `STALL_BACKEND_RENAME`.

## Control Flow, State, and Persistence
The build resolves standard aliases into generated Monaka PMU tables. Runtime state is the active set of counters in perf and the kernel PMU driver; the JSON is immutable metadata.

## Dependencies and Integration
Depends on ARM64 standard stall event definitions. It integrates with cache, TLB, branch, cycle accounting, and pipeline files to implement topdown-style diagnosis on Monaka.

## Risks and Test Signals
Risks include nonexclusive stall subcategories, denominator confusion between cycles and slots, and standard event availability depending on PMU architecture level. Test signals are `jevents.py` success, `perf stat` topdown-style groups, frontend miss workloads increasing frontend memory/cache stalls, data cache miss workloads increasing backend memory stalls, and rename/resource pressure tests increasing core-bound subevents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/stall.json -->
