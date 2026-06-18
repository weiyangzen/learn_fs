# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/gfx/irqsrcs_gfx_12_0_0.h

## Purpose
This header defines GFX 12.0.0 interrupt source IDs. It continues the GFX 11-style contract for UTCL2, SDMA, RLC, CP, GRBM, and SQ events while adjusting selected source IDs for the GFX 12 generation.

## Important APIs, Types, And Data
The table contains `UTCL2_FAULT`, `UTCL2_DATA_POISONING`, `MEM_ACCES_MON`, SDMA IDs `0x30` through `0x46`, `RLC_GC_FED_INTERRUPT`, CP generic/fault/EOP/preempt/query/doorbell/ECC/FUE events, `RLC_STRM_PERF_MONITOR_INTERRUPT`, `GRBM_RD_TIMEOUT_ERROR`, `GRBM_REG_GUI_IDLE`, and `SQ_INTERRUPT_ID`.

Relative to GFX 11, `SDMA_FENCE` is defined at `0x46` rather than `0x43`, so consumers must use the generation-specific header rather than assuming the previous value.

## Control Flow
No functions are present. `amdgpu/gfx_v12_0.c` registers CP/fault interrupts with these IDs, and `amdgpu/sdma_v7_0.c` uses the SDMA subset for SDMA v7 interrupt registration and processing.

## State And Persistence
The constants are immutable. They determine persistent IRQ registration and runtime dispatch behavior for GFX 12 devices.

## Dependencies And Integration Points
The header integrates with GFX 12 command processor handling, SDMA v7, SOC15 IH dispatch, VM fault handling, data-poisoning/RAS paths, and reset diagnostics.

## Risks
The `SDMA_FENCE` value change is a compatibility risk for shared SDMA code. CP and RLC IDs overlap conceptually with earlier generations but should not be deduplicated without a generation audit. Wrong IDs can manifest as missing fence completion, unhandled page faults, or failure to reset after CP faults.

## Test Signals
Build GFX 12 and SDMA v7. Runtime validation should cover CP EOP/fence completion, SDMA user fence/trap/page-fault handling, VM fault reporting, poisoning/FED events, queue hang recovery, and GRBM/SQ diagnostics.
