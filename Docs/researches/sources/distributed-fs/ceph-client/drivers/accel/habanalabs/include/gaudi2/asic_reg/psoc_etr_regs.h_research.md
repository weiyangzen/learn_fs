<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_etr_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_etr_regs.h

## Purpose
`psoc_etr_regs.h` is the PSOC ETR address map for Gaudi2 tracing. It is auto-generated, guarded by `ASIC_REG_PSOC_ETR_REGS_H_`, and exports 47 `mmPSOC_ETR_*` register addresses from `0x6C44004` through `0x6C44FFC`.

## Important APIs, Types, And Functions
No functions or types are present. Address groups include trace RAM size/status/read/write pointers, trigger/control/read-write data/mode/buffer level/watermark, AXI control and data buffer base, formatter and flush status/control, prescaler, integration-test registers, claim/lock/authentication registers, and CoreSight device/peripheral/component ID registers.

## Control Flow
The file participates in CoreSight trace setup and teardown. Runtime code unlocks `LAR`, checks/disables `CTL`, manipulates `FFCR` to flush, waits on `STS`/`FFCR` readiness bits, programs buffer size/mode/base and AXI control, enables trace capture, and later reads `RWP`/`RWPHI` to locate captured data.

## State And Persistence
The ETR MMIO block stores trace capture configuration and live trace state. Capture state, buffer pointers, flush status, lock state, and ID registers are hardware-owned. Values persist until reset or reprogramming; pointer and level values evolve while tracing is active.

## Dependencies
Runtime use depends on `psoc_etr_masks.h`, the Gaudi2 CoreSight implementation, PSOC global trace address/AXUSER registers, and register helpers.

## Integration Points
`gaudi2_coresight.c` uses these addresses for PSOC trace sink operations. The block integrates with device debug flows and with memory-management setup for trace buffer writes.

## Risks
Incorrect addresses can make CoreSight control write into unrelated PSOC registers. Misordered ETR programming can corrupt host/device memory or hang while polling flush/readiness status. Because this is debug infrastructure, failures may only appear during diagnostics unless trace capture is part of test coverage.

## Test Signals
Run CoreSight capture tests, enable/disable cycles, flush timeout checks, trace buffer address validation, read-pointer validation, and ID-register sanity comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_etr_regs.h -->
