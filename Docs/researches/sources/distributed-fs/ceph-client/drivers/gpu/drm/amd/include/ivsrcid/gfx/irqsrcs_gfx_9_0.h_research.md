# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/gfx/irqsrcs_gfx_9_0.h

## Purpose
This header defines GFX 9.0 graphics interrupt source IDs for command processor, RLC, GRBM, and SQ events. It is the GFX9 SOC15 interrupt-source contract used by AMDGPU GFX initialization and fault handling.

## Important APIs, Types, And Data
The table defines CP ring-buffer and IB interrupt packet IDs, PM4 reserved-bit error, EOP, bad opcode, privileged register/instruction faults, wait-memory-semaphore fault, context empty/busy, wait-reg-mem timeout, signal incomplete, preempt ack, GPF, GDS allocation error, ECC/FUE, compute query status, VM doorbell, RLC streaming performance monitor, GRBM read timeout, GUI idle, and SQ interrupt. IDs occupy the `0xB0` through `0xEF` range.

## Control Flow
There is no executable code. `amdgpu/gfx_v9_0.c` and `gfx_v9_4_3.c` register selected IDs via `amdgpu_irq_add_id()` and process incoming IH entries using the same constants.

## State And Persistence
The constants are immutable. They persist indirectly in AMDGPU's IRQ registration tables and determine runtime dispatch of GFX9 interrupts.

## Dependencies And Integration Points
The header integrates with SOC15 IH client `GRBM_CP`, GFX ring/fence handling, CP fault processing, RLC diagnostics, SQ error handling, and GPU reset/RAS paths on GFX9-class devices.

## Risks
The table is similar to GFX 10 but lacks the `CP_GENERIC_INT` alias. Reusing a newer-generation source table can create off-by-one or alias mistakes. Missing or wrong EOP IDs can stall fences; wrong fault IDs can hide CP errors and delay recovery.

## Test Signals
Build GFX9 and GFX9.4.3. Runtime tests include ring submission and fence completion, EOP IRQ delivery, bad packet/fault handling, privileged access faults, preemption, GRBM timeout diagnostics, SQ interrupt reporting, and reset after CP failures.
