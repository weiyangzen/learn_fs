<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/floating-point.json

## Purpose
This JSON file defines Granite Rapids core floating-point PMU events for perf. The complete 242-line file was read, containing 28 event records. It exposes floating-point divider active cycles, FP assists, SSE/AVX transition assists, dispatched FP operations by execution port/vector alias, and retired FP arithmetic instruction classes including half-precision variants.

## Important APIs, Types, and Functions
The file uses `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, optional `PublicDescription`, and optional `CounterMask`. There are no functions or classes. Event families are `FP_ARITH_INST_RETIRED` (12), `FP_ARITH_INST_RETIRED2` (7), `FP_ARITH_DISPATCHED` (6), `ASSISTS` (2), and `ARITH.FPDIV_ACTIVE` (1). All records target core counters `0,1,2,3,4,5,6,7`. `ARITH.FPDIV_ACTIVE` uses `CounterMask` `1`; dispatch port events include aliases between `PORT_0/1/5` and `V0/V1/V2`; retired arithmetic records separate scalar, packed single/double, vector aggregate, and FP16 half-precision classes.

## Control Flow, State, and Persistence
The file is consumed by the perf PMU event generator. `jevents.py` converts each record into a generated core PMU alias, maps `SampleAfterValue` to `period=`, `UMask` to `umask=`, and `CounterMask` to `cmask=`. Runtime perf commands use the aliases for counting or sampling FP-heavy workloads. The source JSON is static; generated C tables are the persistent build product.

## Dependencies and Integration Points
It depends on Granite Rapids core PMU support and perf's x86 model mapping. It integrates with HPC and vectorization analysis, compiler/codegen investigations, and assist diagnostics for FP pipelines. It also connects to Granite Rapids `counter.json`, since all events draw from the eight generic core counters when scheduled together.

## Risks and Test Signals
The main risks are alias duplication and mask aggregation semantics. The port and vector dispatch names are intentional aliases with identical encodings, so duplicate-looking definitions should not be removed without checking user-facing compatibility. Aggregate retired events such as `4_FLOPS`, `8_FLOPS`, `SCALAR`, and `VECTOR` use combined masks and can be misread as derived metrics even though they are raw PMU events. Test signals include JSON syntax validation, `jevents.py` generation, alias visibility in `perf list`, generated event strings with `period=` and `cmask=` for `ARITH.FPDIV_ACTIVE`, and workload checks using scalar, AVX2/AVX-512, and FP16 instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/floating-point.json -->
