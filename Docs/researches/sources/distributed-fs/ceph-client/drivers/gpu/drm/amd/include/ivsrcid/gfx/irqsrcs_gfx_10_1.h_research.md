# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/gfx/irqsrcs_gfx_10_1.h

## Purpose
This header defines GFX 10.1 graphics interrupt source IDs for command-processor, RLC, GRBM, and SQ events. It is used by the GFX 10 AMDGPU interrupt setup and decode paths.

## Important APIs, Types, And Data
The file defines `GFX_10_1__SRCID__*` macros from the `0xB0` to `0xEF` source range. Important IDs include ring-buffer/IB interrupt packets, `CP_GENERIC_INT`, PM4 reserved-bit errors, EOP, bad opcode, privileged register/instruction faults, wait-memory-semaphore faults, context empty/busy, wait-reg-mem timeout, signal incomplete, preempt ack, GPF, GDS allocation error, ECC/FUE errors, compute query status, unattached VM doorbell, RLC streaming performance monitor, GRBM read timeout, GUI idle, and SQ interrupt.

`CP_GENERIC_INT` and `CP_IB1_INTERRUPT_PKT` both use source ID 177, so consumers must understand the generation's aliasing behavior.

## Control Flow
There is no executable code. `amdgpu/gfx_v10_0.c` registers selected source IDs with `amdgpu_irq_add_id()` for EOP and fault interrupts, then uses the same constants while processing IH entries.

## State And Persistence
The constants are immutable. Runtime state consists of registered IRQ handlers and per-source enablement in AMDGPU's interrupt framework.

## Dependencies And Integration Points
The header integrates with SOC15 IH client `GRBM_CP`, GFX 10 ring/fence handling, CP fault handling, RLC/performance events, and GPU reset/error recovery paths.

## Risks
Numeric source IDs are hardware ABI. An incorrect value can route CP faults to the wrong handler or leave fault interrupts unregistered. Alias source 177 requires careful decode semantics. Newer GFX generations have related but not identical tables, so sharing constants across generations is unsafe unless explicitly verified.

## Test Signals
Build GFX 10. Runtime tests include ring interrupt/fence completion, EOP delivery, bad PM4/opcode fault injection where possible, privileged register fault handling, preemption, GPU reset after CP faults, and SQ/RLC diagnostic interrupts.
