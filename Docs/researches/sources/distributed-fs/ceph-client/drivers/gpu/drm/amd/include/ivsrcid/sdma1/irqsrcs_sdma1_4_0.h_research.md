# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/sdma1/irqsrcs_sdma1_4_0.h

## Purpose
This header defines SDMA1 4.0 interrupt source IDs. It is the engine-1 namespace counterpart to the SDMA0 4.0 table for AMDGPU SDMA v4 devices.

## Important APIs, Types, And Data
The `SDMA1_4_0__SRCID__*` constants cover atomic return done, atomic timeout, IB preempt, ECC, page fault/null/XNACK, trap, semaphore incomplete and wait-fail timeouts, SRAM ECC, preempt, VM hole, context empty, invalid doorbell, frozen, poll timeout, and SRBM write protection. The numeric values match the SDMA0 4.0 table and occupy the same `0xD9`-`0xF7` ranges.

## Control Flow
There is no executable code. `amdgpu/sdma_v4_0.c` and `sdma_v4_4_2.c` include this header together with SDMA0's table to register and handle interrupts for multiple SDMA engines.

## State And Persistence
The constants are immutable. Runtime persistence is the per-engine SDMA IRQ registration, ring state, and fault/recovery bookkeeping that use these IDs.

## Dependencies And Integration Points
It integrates with SOC15 IH SDMA handling, SDMA v4 multi-engine setup, ring/fence completion, VM fault diagnostics, semaphore timeout handling, ECC/RAS, and reset recovery.

## Risks
Because SDMA0 and SDMA1 source values are identical, engine identity must come from the IH client/instance or registration context, not the numeric source alone. Using only `src_id` can conflate engines and update the wrong ring state. As with SDMA0, page fault/null/XNACK and SRBM write protection need distinct handling for useful diagnostics.

## Test Signals
Build multi-SDMA v4 paths. Runtime tests should exercise both SDMA engines independently: submissions, fences, traps, preemption, page faults, invalid doorbells, poll timeouts, SRBM write protection, ECC/SRAM ECC, and recovery after one-engine hangs without corrupting the other engine's state.
