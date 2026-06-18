# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/sdma3/irqsrcs_sdma3_5_0.h

## Purpose
Defines SDMA3 interrupt source IDs for SDMA 5.0 ASIC support. It supplies an engine-specific macro namespace for the same SDMA 5.0 event numbers used by the other SDMA instances.

## Important APIs, Types, and Functions
There are no callable APIs. The file exports `SDMA3_5_0__SRCID__*` macros for atomic return done, atomic timeout, IB preempt, ECC, page fault/null/XNACK, trap, semaphore incomplete/wait-fail timeouts, SRAM ECC, preempt, VM hole, context empty, invalid doorbell, frozen, poll timeout, and SRBM write protection.

## Control Flow
No code executes in this header. Runtime dispatch code uses the constants to branch to the correct SDMA3 fault, trap, preemption, or recovery path.

## State and Persistence
The file holds no state. Its numeric constants are persistent hardware-facing source identifiers.

## Dependencies and Integration Points
Only the include guard is required. It integrates with SDMA3 interrupt setup, GPUVM fault handling, trap reporting, and queue/hang recovery.

## Risks and Test Signals
Main risks are wrong numeric mapping or wrong SDMA instance attribution. Test signals include SDMA3-specific interrupt counters and logs for page fault, XNACK, preempt, frozen, and SRBM protection events.
