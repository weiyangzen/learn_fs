<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/pipeline.json

## Purpose
Monaka pipeline topic table. It exposes valid-cycle counters for address, prefetch, execution, floating-point, store, and L1/L1I/L2 pipelines; predicate population counters; gather/scatter flow counters; and selected TLB/store/interlock stall aliases.

## APIs, Types, and Functions
Direct event names include `EAGA_VAL`, `EAGB_VAL`, `PRX_VAL`, `EXA_VAL` through `EXD_VAL`, `FLA_VAL`, `FLB_VAL`, `STEA_VAL`, `STEB_VAL`, `STFL_VAL`, `STPX_VAL`, `L1_PIPE*`, `L1I_PIPE_*`, `L2_PIPE_*`, and predicate/gather/scatter counters. The final entries use `ArchStdEvent` for `STALL_FRONTEND_TLB`, `STALL_BACKEND_TLB`, `STALL_BACKEND_ST`, and `STALL_BACKEND_ILOCK`.

## Control Flow, State, and Persistence
The perf build merges direct event-code records and standard stall aliases into the generated Monaka table. Runtime state consists only of active PMU counters during perf sessions.

## Dependencies and Integration
Depends on Monaka pipeline event encodings and ARM64 standard stall aliases. It integrates with SVE, FP operation, L1/L2 cache, and stall topic files to localize throughput limitations inside execution, memory, and frontend pipelines.

## Risks and Test Signals
Risks include predicate-count full-width corrections changing between A64FX and Monaka (for example descriptions mention 32 or 64), nonexclusive valid-cycle counters, and gather/scatter flow counters requiring careful interpretation. Test signals are build-time alias generation, scalar/vector/store-heavy microbenchmarks exercising separate pipelines, and correlation between stall aliases here and the broader `stall.json` categories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/fujitsu/monaka/pipeline.json -->
