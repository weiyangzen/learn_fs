<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/pipeline.json

## Purpose
Defines 60 Elkhart Lake core pipeline events for retired branches, branch mispredicts, clock/reference cycles, topdown slots, machine clears, uop retirement/issue behavior, load blocks, and divide busy cycles.

## Important APIs, Types, And Functions
The file uses `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, `Counter`, `PEBS`, and `Deprecated`. Major groups include `BR_INST_RETIRED.*`, `BR_MISP_RETIRED.*`, `CPU_CLK_UNHALTED.*`, `INST_RETIRED.*`, `TOPDOWN_*`, `MACHINE_CLEARS.*`, `UOPS_RETIRED.*`, `UOPS_ISSUED.*`, `LD_BLOCKS.*`, `CYCLES_DIV_BUSY.*`, and `BTCLEAR.*`.

## Control Flow
`jevents.py` parses the entries and emits raw-event aliases selected for `GenuineIntel-6-9[6C]` systems. The metrics file depends on this table for `INST_RETIRED.ANY`, `BR_INST_RETIRED.ALL_BRANCHES`, `BR_MISP_RETIRED.ALL_BRANCHES`, `CPU_CLK_UNHALTED.REF_TSC`, and `cycles`-adjacent clock analysis. Runtime perf programs the named events directly or as dependencies of metrics.

## State And Persistence
The file is static repository data; generated aliases persist in perf. Runtime state is PMU counter values and, for precise-capable entries, PEBS sample records.

## Dependencies And Integration Points
Integrates with perf topdown analysis and Elkhart Lake metrics. Twenty-six entries carry `PEBS`, so precise sampling workflows depend on these annotations. Branch aliases integrate with frontend `BACLEARS.*`; machine-clear aliases integrate with memory ordering and FP assist events.

## Risks And Edge Cases
Topdown events use slot accounting and can be misinterpreted if treated as normal retired-event counts. Three entries are deprecated. PEBS flags must match hardware or perf may advertise unsupported precise sampling. Metric formulas will fail if foundational aliases such as `INST_RETIRED.ANY` or `BR_MISP_RETIRED.ALL_BRANCHES` are renamed.

## Test Signals
Run JSON validation and perf pmu-events generation. Metric tests for `IPC`, `CPI`, `IpBranch`, and `IpMispredict` cover key dependency names. On hardware, `perf stat -e INST_RETIRED.ANY,CPU_CLK_UNHALTED.REF_TSC,BR_MISP_RETIRED.ALL_BRANCHES` and a topdown event group should resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/elkhartlake/pipeline.json -->
