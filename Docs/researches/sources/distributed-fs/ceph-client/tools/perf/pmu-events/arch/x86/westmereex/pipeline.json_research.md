# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereex/pipeline.json

Purpose: declares 111 Westmere EX pipeline, branch, instruction, uop, stall, and fixed-counter PMU events for perf. It is the main model table for execution pipeline analysis.

Important APIs/types/functions: rows use standard event fields plus several hardware qualifiers: `PEBS` for precise retired events, `AnyThread` for all-thread fixed/programmed cycle and instruction counts, `CounterMask`, `Invert`, and `EdgeDetect` for cycle/threshold-style events. Event families include `ARITH`, `BACLEAR`, `BPU_CLEARS`, `BR_INST_EXEC`, `BR_MISP_EXEC`, `BR_INST_RETIRED`, `BR_MISP_RETIRED`, `CPU_CLK_UNHALTED`, `ILD_STALL`, `INST_RETIRED`, `MACHINE_CLEARS`, `RAT_STALLS`, `RESOURCE_STALLS`, `SSEX_UOPS_RETIRED`, `UOPS_DECODED`, `UOPS_EXECUTED`, `UOPS_ISSUED`, and `UOPS_RETIRED`.

Control flow: no executable code. Build-time generation transforms these JSON rows into perf event tables. Runtime control is in perf and the kernel PMU driver, which interpret event code, unit mask, fixed/generic counter selection, precise-event flags, any-thread flags, and counter-mask/invert/edge settings.

State and persistence: static metadata only. During measurement it controls transient PMU programming, including fixed counters `Fixed counter 1`, `Fixed counter 2`, and `Fixed counter 3`, PEBS setup for precise events, and threshold/cycle qualification.

Dependencies: depends on Westmere EX PMU semantics and perf's parser for fixed counters, any-thread counting, PEBS, edge detect, invert, and counter masks. It also depends on `counter.json` being consistent with the fixed/generic counter inventory.

Integration points: these events are the core aliases for `perf stat`/`perf record` pipeline diagnosis. They complement `frontend.json` for decode, `floating-point.json` for operation classes, and `virtual-memory.json` for TLB behavior. Metric-generation scripts can validate and reference these names through `metric.Event` after loading the model directory.

Risks: this file has the densest mix of special qualifiers. Losing `AnyThread` changes count scope; losing `PEBS` changes sampling precision; wrong `CounterMask`/`Invert`/`EdgeDetect` changes event meaning for cycle and occurrence counts. Fixed-counter labels must remain exactly in the syntax perf expects. Some descriptions are absent from two rows, so validators should distinguish known sparse metadata from parse failures.

Test signals: JSON parse; 111 unique event names; expected fixed-counter rows for `CPU_CLK_UNHALTED` and `INST_RETIRED`; qualifier checks for 10 `AnyThread` rows, PEBS-marked retired events, and intended `CounterMask`/`Invert`/`EdgeDetect` usage. Full integration signal is successful pmu-events generation and representative `perf list` coverage for branch, uop, stall, and fixed-counter aliases.
