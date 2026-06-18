# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/sdma0/irqsrcs_sdma0_5_0.h

## Purpose
This header defines SDMA0 5.0 interrupt source IDs. It provides the SDMA v5 source-number contract for trap, fault, semaphore, ECC, preempt, context, doorbell, poll, and SRBM write events.

## Important APIs, Types, And Data
The constants mirror the SDMA0 4.0 numeric set: atomic return done `0xD9`, atomic timeout `0xDA`, IB preempt `0xDB`, ECC `0xDC`, page fault/null/XNACK `0xDD`-`0xDF`, trap `0xE0`, semaphore incomplete/wait-fail `0xE1`-`0xE2`, SRAM ECC `0xE4`, preempt `0xF0`, VM hole `0xF2`, context empty `0xF3`, invalid doorbell `0xF4`, frozen `0xF5`, poll timeout `0xF6`, and SRBM write protection `0xF7`.

## Control Flow
There are no functions. `amdgpu/sdma_v5_0.c` and `sdma_v5_2.c` include this header and use the constants for IRQ registration and source-ID return helpers.

## State And Persistence
The header is immutable. Runtime state is SDMA v5 interrupt registration, ring/fence state, error counters, and recovery paths that respond to these IDs.

## Dependencies And Integration Points
It integrates with SDMA v5/v5.2 ring management, SOC15 IH dispatch, VM fault handling, RAS/ECC reporting, queue preemption, and reset/recovery handling.

## Risks
Although the values match SDMA0 4.0, the generation-specific namespace matters for maintainability and avoiding accidental cross-generation edits. Missing `SDMA_TRAP` or `SDMA_POLL_TIMEOUT` registration can stall user queues or hide ring hangs. Page fault/null/XNACK distinctions are important for accurate VM diagnostics.

## Test Signals
Build SDMA v5.0 and v5.2. Runtime validation should cover SDMA ring submissions and fences, trap interrupts, VM faults and XNACK/page-null handling, semaphore timeout diagnostics, invalid doorbell events, ECC/SRAM ECC handling, preemption, and reset after queue hang.
