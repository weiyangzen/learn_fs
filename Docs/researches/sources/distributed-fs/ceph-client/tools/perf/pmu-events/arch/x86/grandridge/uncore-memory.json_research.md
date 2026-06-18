<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/uncore-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/uncore-memory.json

## Purpose
This JSON file defines Grand Ridge integrated memory controller (`IMC`) uncore PMU events for perf. The complete 789-line file was read, containing 80 event records. It exposes DRAM command counts, subchannel CAS counts, read/write queue inserts and occupancy, powerdown cycles, MR4/refresher activity, and throttle cycles.

## Important APIs, Types, and Functions
Records use the perf PMU JSON schema fields `EventName`, `EventCode`, `UMask`, `Unit`, `Counter`, `PerPkg`, `BriefDescription`, optional `PublicDescription`, and optional `Experimental`. Every event uses `Unit` `IMC` and counters `0,1,2,3`. Event families include `UNC_M_CAS_COUNT_SCH0` and `UNC_M_CAS_COUNT_SCH1` (7 each), `UNC_M_POWERDOWN_CYCLES` (8), `UNC_M_RPQ_INSERTS` and `UNC_M_WPQ_INSERTS` (6 each), `UNC_M_ACT_COUNT` (4), `UNC_M_PRE_COUNT` (5), MR4 and PDC activity (4 each), bandwidth/power throttle records, and queue occupancy records with separate event codes for each subchannel/physical channel.

## Control Flow, State, and Persistence
The file has no executable control flow. During perf build, `jevents.py` converts these records into generated event descriptors for the `uncore_imc` PMU. `EventCode` and `UMask` define the raw event config; `PerPkg` identifies package-level uncore aggregation. At runtime, perf resolves symbolic aliases and the kernel reads memory-controller PMU counters. No state is written back to this JSON; generated `pmu-events.c` is the derived persistent artifact.

## Dependencies and Integration Points
The file depends on Grand Ridge IMC uncore PMU support and on the perf PMU event build pipeline. It integrates with memory bandwidth and latency diagnostics, DRAM page policy analysis, queue occupancy analysis, and power/throttle investigations. It is a downstream counterpart to cache and interconnect events: CHA and B2CMI events describe requests before the IMC, while this file describes command and queue activity at the controller.

## Risks and Test Signals
Forty-eight records are marked `Experimental`, and only 31 include `PublicDescription`. Risk centers on subchannel and slot/rank mask correctness: SCH0/SCH1 and PCH0/PCH1 variants use nearby masks, making transposition easy. Occupancy events use distinct event codes instead of masks, so generator output should be checked for both encoded styles. Test signals include `jq` validation, `jevents.py` generation, presence of `unc_m_*` aliases, consistency checks that all/read/write CAS and activate/precharge events behave monotonically under memory load, and sanity checks that throttle/powerdown counters remain low or zero on unconstrained systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/uncore-memory.json -->
