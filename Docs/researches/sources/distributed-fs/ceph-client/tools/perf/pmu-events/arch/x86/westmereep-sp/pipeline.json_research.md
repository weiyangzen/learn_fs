# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/pipeline.json

Purpose: defines 111 SP execution pipeline aliases covering arithmetic, branches, branch mispredicts, fixed/programmed cycles, instruction retirement, decoder stalls, machine clears, RAT/resource stalls, SSE uop retirement, and uop issue/execute/retire behavior.

Important APIs/types/functions: uses the same rich schema surface as DP pipeline: `CounterMask`, `EdgeDetect`, `Invert`, `AnyThread`, and `PEBS` in addition to event code fields. Important groups include `BR_INST_EXEC.*`, `BR_MISP_EXEC.*`, `BR_*_RETIRED.*`, `CPU_CLK_UNHALTED.*`, `INST_RETIRED.*`, `RESOURCE_STALLS.*`, `UOPS_EXECUTED.*`, `UOPS_ISSUED.*`, and `UOPS_RETIRED.*`.

Control flow: build-time parsing emits generated C aliases. `JsonEvent.real_event` supplies special encodings for fixed counter names such as retired instructions and unhalted cycles. Runtime perf schedules selected aliases on fixed or generic counters according to their encoded constraints.

State and persistence: static JSON only; runtime state lives in active perf events. PEBS rows support precise sampling for retirement-related aliases.

Dependencies and integration points: tied to CPUID `GenuineIntel-6-25` through `mapfile.csv`, and to `counter.json` through fixed/generic counter capacity. Integrates with top-down-style manual analysis on older Westmere hardware.

Risks: modifier-sensitive rows are easy to corrupt. Inversion plus counter masks represent cycles lacking activity for several aliases, so display names must be interpreted carefully. Port-utilization rows have `AnyThread` variants and generic-counter constraints that affect grouped measurements.

Test signals: JSON parsing, generated fixed-counter aliases, `perf list uops`/`perf list br_`, branchy microbenchmarks for branch rows, and IPC sanity checks using retired instructions and cycles.
