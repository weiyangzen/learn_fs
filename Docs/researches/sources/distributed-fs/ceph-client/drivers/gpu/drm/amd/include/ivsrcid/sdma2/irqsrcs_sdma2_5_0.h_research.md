# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/sdma2/irqsrcs_sdma2_5_0.h

## Purpose
Defines SDMA2 interrupt source IDs for SDMA 5.0. The file mirrors the SDMA 5.0 event map in an SDMA2-specific namespace so dispatch code can attribute events to the correct SDMA engine.

## Important APIs, Types, and Functions
No functions or structs are declared. `SDMA2_5_0__SRCID__*` macros cover atomic completion/timeout, IB preemption, ECC and SRAM ECC, UTCL2 page fault/null/XNACK, trap, semaphore timeouts, run-list preempt, VM hole, context empty, invalid doorbell, frozen, poll timeout, and SRBM write protection. Values span `217` through `247` with hardware-defined gaps.

## Control Flow
The header has no executable flow. It shapes runtime branch decisions in SDMA/IH handlers that decode the interrupt vector and select SDMA2-specific handling.

## State and Persistence
No mutable state is present. The constants persist into compiled interrupt decode logic and must remain aligned with SDMA 5.0 hardware tables.

## Dependencies and Integration Points
The file depends only on its include guard. Integration points are SDMA engine setup, interrupt handler registration, GPUVM/KFD fault reporting, and queue recovery logic.

## Risks and Test Signals
Potential failures include copy/paste divergence from sibling SDMA headers or wiring SDMA2 handlers with SDMA1/SDMA3 macros. Tests should exercise per-engine page faults, preemption, context-empty, and doorbell-invalid interrupts.
