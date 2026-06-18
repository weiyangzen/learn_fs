
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/floating-point.json

## Purpose

This file defines 13 Skylake-X floating-point PMU events. It provides aliases for retired FP arithmetic instruction classes by vector width and precision, plus aggregate scalar/vector/floating-operation selectors and FP assist events.

The event names are `FP_ARITH_INST_RETIRED.128B_PACKED_DOUBLE`, `128B_PACKED_SINGLE`, `256B_PACKED_DOUBLE`, `256B_PACKED_SINGLE`, `512B_PACKED_DOUBLE`, `512B_PACKED_SINGLE`, `SCALAR_DOUBLE`, `SCALAR_SINGLE`, `SCALAR`, `VECTOR`, `4_FLOPS`, `8_FLOPS`, and `FP_ASSIST.ANY`. These are core inputs for FLOP-rate, vectorization, and assist-overhead metrics on Skylake-X.

## Important Schema Fields and APIs

Each object uses the core PMU event schema:

- `EventName`: public alias.
- `EventCode` and `UMask`: raw selector and subevent mask for FP arithmetic or assists.
- `Counter`: allowed programmable counters.
- `CounterMask`: present on aggregate FLOP-width style rows where thresholded behavior is needed.
- `SampleAfterValue`: default sampling period.
- `BriefDescription` and `PublicDescription`: short and detailed text shown by perf.

The file does not specify `Unit`, so events are core PMU events. `CounterMask` rows are lowered to `cmask=...` by `jevents.py`.

## Control Flow and Data Flow

Build-time control flow is standard PMU generation: parse JSON descriptors, emit generated C aliases, compile into perf, and expose aliases when the running CPU maps to Skylake-X. Runtime data flow is retired FP arithmetic/assist events from the core PMU into direct counts or into metrics that compute FLOPs, vector-width mix, FP utilization, and assist costs.

No event depends on another descriptor inside the file, but higher-level metrics may combine these events with instruction, cycle, slot, or frequency counters.

## State and Persistence

This is static metadata only. Runtime counts and samples exist in PMU registers and perf buffers. Generated aliases persist in perf build artifacts until the tool is rebuilt.

## Dependencies and Integration Points

The file integrates with `jevents.py`, generated `pmu-events.c`, `perf list`, `perf stat`, `perf record`, and Skylake-X metric definitions that include `Flops`, `HPC`, `Compute`, or topdown FP arithmetic groups. It depends on the Skylake-X core PMU encodings for AVX-512, AVX/packed, scalar, and assist events and on counter capacity defined in `counter.json`.

## Risks

FP event semantics can be misread as instruction counts, operation counts, or FLOP counts depending on the selector. The `4_FLOPS` and `8_FLOPS` aliases are especially sensitive to width/precision interpretation and `CounterMask` behavior. Workloads using mixed precision, masked AVX-512 operations, denormals, or assists may require careful interpretation. If metrics combine these aliases with frequency or instruction counts, counter multiplexing can skew derived GFLOP/s or utilization values.

## Test Signals

Build-time signals are JSON validity and generated aliases. Runtime tests should run scalar, AVX2, and AVX-512 microbenchmarks and verify the corresponding packed/scalar aliases increase as expected. `FP_ASSIST.ANY` should be tested with an assist-heavy workload if hardware and kernel permissions allow. Metric smoke tests should include Skylake-X FLOP and FP topdown metrics that depend on these aliases.
