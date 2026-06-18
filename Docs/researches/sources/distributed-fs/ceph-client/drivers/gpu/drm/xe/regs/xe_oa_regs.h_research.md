# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_oa_regs.h

## Purpose

`xe_oa_regs.h` defines observability/performance counter registers for OA/OAR/OAG/OAC/OAM/OAMERT units, EU performance counters, OA buffer pointers, OA control/debug/status bits, media GT adjusted bases, and OA-related TLB invalidation.

## Important APIs, Types, and Definitions

- Global/EU controls: `RPM_CONFIG1`, `GT_NOA_ENABLE`, and `EU_PERF_CNTL*`.
- OAR/OAG controls: `OAR_OACONTROL`, `OACTXCONTROL(base)`, `OAG_OAGLBCTXCTRL`, `OAG_OAHEADPTR`, `OAG_OATAILPTR`, `OAG_OABUFFER`, `OAG_OACONTROL`, and `OAG_OA_DEBUG`.
- Common bits: counter enable/select masks, buffer pointer masks, memory-select bit, report/counter-size bits, overflow/lost-report status bits.
- OAM helpers: offset constants plus `OAM_HEAD_POINTER(base)`, `OAM_TAIL_POINTER(base)`, `OAM_BUFFER(base)`, `OAM_CONTROL(base)`, `OAM_DEBUG(base)`, and `OAM_STATUS(base)`.
- Media and MERT bases: `XE_OAM_*_BASE_ADJ` and `OAMERT_*` registers.

## Control Flow

The header has no local control flow. OA/perf code uses it to program counter selection, enable timers, set/report buffer head/tail pointers, configure debug behavior, trigger MMIO reports, and poll/clear overflow or lost-report conditions.

## State and Persistence Behavior

OA control/debug registers persist while a perf stream is configured. Head/tail pointers and status bits are runtime producer/consumer state. Buffer-overflow and report-lost bits are diagnostic state that must be handled carefully by perf stream code.

## Dependencies and Integration Points

It relies on `XE_REG`, `REG_BIT`, and `REG_GENMASK` through included register infrastructure at use sites. It integrates with Xe OA/perf, metrics set programming, media GT performance streams, and MERT/OAM telemetry on newer platforms.

## Risks and Edge Cases

- Multiple OA units have similar but not identical control layouts; mixing OAG/OAM/OAMERT helpers can program the wrong block.
- `OAG_OA_DEBUG` is marked masked, so consumers should use masked-register write semantics.
- Head/tail pointer masks imply alignment; unaligned buffer positions can be truncated.
- Overflow/lost-report status must be surfaced to userspace to avoid silently corrupting performance data.

## Test Signals

Signals include OA stream open/close, counter enable/disable, report generation, MMIO trigger behavior, overflow/lost-report handling, media GT OA streams, and metrics validation against known workloads.
