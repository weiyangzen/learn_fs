<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/fp_operation.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/fp_operation.json

## Purpose
NVIDIA T410 floating-point operation topic selecting standard FP precision and operation-scaling aliases. It covers half, single, double precision, scalable and fixed operation counts, minimum precision operation counts, BF16, and FP8 classes.

## APIs, Types, and Functions
The file contains only `ArchStdEvent` entries such as `FP_HP_SPEC`, `FP_SP_SPEC`, `FP_DP_SPEC`, `FP_SCALE_OPS_SPEC`, `FP_FIXED_OPS_SPEC`, `FP_HP_SCALE_OPS_SPEC`, `FP_SP_FIXED_OPS_SPEC`, `FP_DP_FIXED_OPS_SPEC`, `FP_SP_FIXED_MIN_OPS_SPEC`, `FP_BF16_FIXED_MIN_OPS_SPEC`, `FP_FP8_FIXED_MIN_OPS_SPEC`, and scalable minimum operation aliases.

## Control Flow, State, and Persistence
Build-time standard alias resolution adds these events to the generated T410 table. Runtime perf measurement uses PMU counters selected by alias; the JSON is static.

## Dependencies and Integration
Depends on ARM64 common FP event definitions. It integrates with T410 `metrics.json` for FP16/FP32/FP64 percentages and FP operations per cycle, and with SVE-related metrics where supported through standard event names.

## Risks and Test Signals
Risks include hardware support gaps for BF16 or FP8 aliases, scaled counters not equal to instruction counts, and overlap between aggregate precision counters. Test signals are alias-generation success, FP microbenchmarks by precision, BF16/FP8 tests on capable hardware, and metric sanity for `fp_ops_per_cycle`, `fp16_percentage`, `fp32_percentage`, and `fp64_percentage`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/fp_operation.json -->
