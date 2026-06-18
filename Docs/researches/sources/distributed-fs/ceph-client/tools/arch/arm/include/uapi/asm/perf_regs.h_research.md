# sources/distributed-fs/ceph-client/tools/arch/arm/include/uapi/asm/perf_regs.h

## Purpose
Defines ARM register identifiers used by perf event sample register masks.

## Important APIs, Types, And Functions
- `enum perf_event_arm_regs` lists `R0` through `R10`, `FP`, `IP`, `SP`, `LR`, `PC`, and `PERF_REG_ARM_MAX`.

## Control Flow
No runtime flow.

## State And Persistence
No state. Enum values become ABI-facing register ids in tools.

## Dependencies And Integration Points
Used by perf and other tooling that decodes or requests ARM user register samples.

## Risks
Changing enum order breaks perf sample ABI interpretation.

## Test Signals
Run perf register sampling/decoding tests for ARM and compare ids against kernel UAPI.
