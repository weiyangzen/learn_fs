# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/gfx/irqsrcs_gfx_12_1_0.h

## Purpose
This header defines GFX 12.1.0 interrupt source IDs for newer graphics and SDMA handling. It refines UTCL2 fault/retry/poison separation and adds newer CP/RLC/PMR-related source aliases.

## Important APIs, Types, And Data
`UTCL2_FAULT`, `UTCL2_RETRY`, and `UTCL2_DATA_POISONING` occupy IDs 0, 1, and 2. SDMA IDs include the GFX 12 SDMA range plus renamed or expanded error cases: `SDMA_INVALID_ADDR` at `0x3D`, `SDMA_INVALID_RB_PTR` at `0x43`, `SDMA_BE_EXCEPTION` at `0x44`, and `SDMA_FENCE` at `0x46`.

CP IDs include ring-buffer, IB1, IB2, DMA watch, PM4 reserved-bit, EOP, bad opcode, privileged fault, context, timeout, preempt, GPF, GDS, ECC, VM doorbell, FUE, suspend completion, and resume completion events. `RLC_STRM_PERF_MONITOR_INTERRUPT` and `CP_SUSPEAND_REQ_INTERRUPT` both use `0xCA`, while `RLC_POISON_INTERRUPT` and `CP_RESUME_REQ_INTERRUPT` both use `0xCB`, reflecting source aliasing that must be decoded with client/context semantics. `PMR_EA_ERROR_INTERRUPT`, GRBM, and SQ IDs complete the table.

## Control Flow
There are no functions. `amdgpu/gfx_v12_1.c` uses these IDs for CP/RLC poison interrupt registration and handling, and `amdgpu/sdma_v7_1.c` uses the SDMA subset for SDMA v7.1 interrupts.

## State And Persistence
The file is immutable hardware ABI. Runtime persistence is the per-device IRQ registration and decode tables created from these constants.

## Dependencies And Integration Points
It integrates with GFX 12.1 CP, RLC poisoning/RAS, SDMA v7.1 queue/fence handling, SOC15 IH dispatch, VM fault handling, and error-recovery code.

## Risks
Several source IDs are aliases with different semantic names. Consumers must account for IH client and context information when deciding whether `0xCA` or `0xCB` is CP suspend/resume or RLC poison/perf. The macro `CP_SUSPEAND_REQ_INTERRUPT` preserves a typo in the public name; changing it would require all users to migrate.

## Test Signals
Build GFX 12.1 and SDMA v7.1. Runtime validation should cover SDMA fence, trap, invalid address, invalid ring pointer, BE exception, CP EOP and fault interrupts, suspend/resume completion interrupts, RLC poison handling, PMR EA error reporting, and GPU reset paths.
