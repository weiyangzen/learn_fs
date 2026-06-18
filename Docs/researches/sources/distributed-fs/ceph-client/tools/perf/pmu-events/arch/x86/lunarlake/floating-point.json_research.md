<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/floating-point.json

## Purpose
This JSON file defines Lunar Lake floating-point, SIMD/vector integer, FP assist, FP divide, and FP retirement PMU events for perf. The complete 484-line array was read and contains 51 records: 29 `cpu_core` records and 22 `cpu_atom` records for the hybrid Lunar Lake PMU model.

## Important APIs, Types, and Functions
The file uses `EventName`, `EventCode`, `UMask`, `Unit`, `Counter`, `SampleAfterValue`, and `BriefDescription`, with optional `PublicDescription`, `CounterMask`, and `Deprecated`. There are no functions or classes. Event families include `FP_ARITH_INST_RETIRED` (11), `FP_ARITH_OPS_RETIRED` (11), `FP_INST_RETIRED` (7), `FP_VINT_UOPS_EXECUTED` (7), `ARITH` (4), `FP_ARITH_DISPATCHED` (4), `FP_FLOPS_RETIRED` (3), `ASSISTS` (2), plus `MACHINE_CLEARS` and `UOPS_RETIRED`.

The P-core side exposes detailed FP arithmetic retirement aliases, deprecated compatibility aliases under `FP_ARITH_INST_RETIRED.*`, port dispatch aliases `FP_ARITH_DISPATCHED.V0` through `.V3`, and assist/machine-clear events. The atom side exposes `ARITH.FPDIV_*`, `FP_INST_RETIRED.*`, `FP_FLOPS_RETIRED.*`, and `FP_VINT_UOPS_EXECUTED.*` events. `ARITH.FPDIV_ACTIVE` exists for both `cpu_atom` and `cpu_core` with different encodings.

## Control Flow
The file is discovered by `tools/perf/pmu-events/Build` and parsed by `jevents.py`. `Unit` is mapped directly to `cpu_core` or `cpu_atom`; `EventCode` and `UMask` become generated config terms; `CounterMask` becomes `cmask=` for active-cycle style events; `SampleAfterValue` becomes `period=`, and `Deprecated` is preserved in the generated event metadata. The Lunar Lake map row `GenuineIntel-6-BD,v1.21,lunarlake,core` selects the generated aliases at runtime.

## State and Persistence
The JSON file has no mutable state. Its durable effect is the generated perf event table, including unit-specific alias definitions and deprecated flags. Runtime state is in hardware counters and perf scheduling. Because this is a hybrid CPU event file, users may see different FP visibility and event availability depending on whether a workload runs on P-cores or E-cores.

## Dependencies and Integration Points
Dependencies are perf's PMU event schema, `jevents.py`, x86 mapfile selection, and hybrid `cpu_core`/`cpu_atom` PMU support. The file integrates with HPC and numerical workload profiling, vector width/FLOP accounting, FP divide bottleneck analysis, SSE/AVX transition diagnostics, and assist detection. It should be read together with Lunar Lake cache and execution/topdown events when separating arithmetic throughput limits from memory stalls or frontend/backend pipeline pressure.

## Risks
The main risk is hybrid semantic mismatch. Some concepts exist on both units with different event codes and masks, while other families are unit-specific; scripts must filter by `Unit` rather than assuming one alias applies to all cores. Nine `FP_ARITH_INST_RETIRED.*` records are deprecated in favor of `FP_ARITH_OPS_RETIRED.*`, so user-facing tooling should surface deprecation and avoid recommending old aliases. Aggregate aliases such as scalar/vector or FLOPS groups overlap narrower width/type records, creating double-counting risk. Public descriptions are present on only 12 records, leaving many atom-side aliases terse.

## Test Signals
Validation should include JSON syntax checks and generated event inspection for `pmu=cpu_core`, `pmu=cpu_atom`, `period=`, `cmask=`, and `deprecated=1` where expected. `perf list` should expose both unit-specific `ARITH.FPDIV_ACTIVE` forms without collapsing them. Hardware smoke tests should pin FP-heavy workloads to P-cores and E-cores separately, exercising scalar FP, 128-bit and 256-bit vectors, FP divide/sqrt loops, SSE/AVX mix cases, vector integer operations, and FP assists. Regression checks should confirm deprecated aliases remain aliases while newer `FP_ARITH_OPS_RETIRED.*` names are available for preferred analysis.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/floating-point.json -->
