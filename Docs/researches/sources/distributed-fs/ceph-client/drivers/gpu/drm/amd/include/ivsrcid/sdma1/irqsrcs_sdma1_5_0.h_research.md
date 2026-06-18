# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/sdma1/irqsrcs_sdma1_5_0.h

## Purpose
Defines SDMA1 interrupt vector source IDs for SDMA 5.0 hardware. Consumers use these macros to translate IH source IDs into named SDMA1 events: atomic completion, page faults, traps, preemption, doorbell errors, frozen/hang conditions, and SRBM access faults.

## Important APIs, Types, and Functions
There are no functions or types. The exported API is the `SDMA1_5_0__SRCID__*` macro set: atomic return done `217`, atomic timeout `218`, IB preempt `219`, ECC `220`, page fault/null/XNACK `221`-`223`, trap `224`, semaphore timeouts `225`-`226`, SRAM ECC `228`, preempt `240`, VM hole `242`, context empty `243`, invalid doorbell `244`, frozen `245`, poll timeout `246`, and SRBM write protection `247`.

## Control Flow
No executable code exists. Runtime control flow is indirect: SDMA/IH interrupt code compares an incoming source ID against these constants and routes to fault, trap, preempt, completion, or recovery handlers for SDMA1.

## State and Persistence
The header stores no runtime state. The macro values are persistent hardware constants and should be treated as an ABI-like contract with the interrupt block.

## Dependencies and Integration Points
The only local dependency is the include guard. Integration points include SDMA1 interrupt registration, GPUVM fault reporting, queue preemption, doorbell validation, and SDMA recovery paths.

## Risks and Test Signals
Risk centers on numeric drift or wrong engine namespace use. Test signals include SDMA1 page fault/XNACK/trap/preempt injection or hardware observation, with logs and handlers confirming the expected source ID and engine.
