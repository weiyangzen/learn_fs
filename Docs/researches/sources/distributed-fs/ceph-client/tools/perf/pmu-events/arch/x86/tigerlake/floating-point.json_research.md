# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/floating-point.json

## Purpose
`floating-point.json` defines 13 Tiger Lake core PMU events for floating-point assists and retired floating-point arithmetic instruction classes. It distinguishes scalar single/double, packed 128-bit, packed 256-bit, packed 512-bit, and aggregate scalar/vector/FLOP-width categories.

## Important APIs, Types, and Fields
Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`. All events can use generic counters `0,1,2,3,4,5,6,7`. The core event family is `FP_ARITH_INST_RETIRED.*`, with aggregation aliases such as `FP_ARITH_INST_RETIRED.SCALAR`, `VECTOR`, `4_FLOPS`, and `8_FLOPS`. `ASSISTS.FP` captures floating-point hardware assists and is a different diagnostic signal from retired arithmetic counts.

## Control Flow and Data Flow
Perf parses the file into Tiger Lake event tables. At runtime, named events program core PMU selectors and unit masks, then count retired FP instruction categories or assist occurrences. Aggregate masks allow users to request broad scalar/vector groups without combining many separate events manually.

## State and Persistence Behavior
The file is static. Hardware counters accumulate events during measurement. Retired instruction class events count instructions or categories, not necessarily mathematical operations unless the specific aggregate mask is documented as FLOP-oriented; users computing FLOP rates must apply the correct width semantics and denominator.

## Dependencies and Integration Points
The file depends on Tiger Lake core PMU support and perf's JSON event loader. It integrates with metric groups such as `Flops`, `FpScalar`, `FpVector`, and `Compute`, and with pipeline events such as divider activity or vector-width mismatch when diagnosing FP-heavy workloads.

## Risks and Edge Cases
Tiger Lake exposes 512-bit FP event categories even though actual instruction availability and frequency behavior may vary by SKU and instruction set support. Aggregate names can be misinterpreted as exact FLOP counts without accounting for vector width and instruction type. Assist counts may be rare but important; zero counts are normal for well-behaved FP code.

## Test Signals
Validate syntax and generated tables, then check `perf list` for `FP_ARITH_INST_RETIRED.*`. Runtime tests should run scalar and vector FP kernels and compare scalar, 128-bit, 256-bit, and aggregate vector counters. A denormal or exception-heavy FP workload can be used to see whether `ASSISTS.FP` increments on supported systems.
