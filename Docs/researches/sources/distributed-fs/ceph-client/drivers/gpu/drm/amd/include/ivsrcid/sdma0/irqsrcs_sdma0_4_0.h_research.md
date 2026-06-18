# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/sdma0/irqsrcs_sdma0_4_0.h

## Purpose
This header defines SDMA0 4.0 interrupt source IDs for SDMA queue, memory, semaphore, ECC, preemption, and fault events.

## Important APIs, Types, And Data
The `SDMA0_4_0__SRCID__*` constants include atomic return done, atomic timeout, IB preempt, ECC, page fault/null/XNACK, trap, semaphore incomplete and wait-fail timeouts, SRAM ECC, preempt, VM hole, context empty, invalid doorbell, frozen, poll timeout, and SRBM write protection. Values occupy the `0xD9` through `0xF7` range with gaps.

## Control Flow
There are no functions. `amdgpu/sdma_v4_0.c` and `sdma_v4_4_2.c` use these constants when registering SDMA0 interrupt IDs and when dispatching SDMA fault/trap/status events.

## State And Persistence
The file is immutable hardware ABI. Runtime persistence is AMDGPU's SDMA IRQ registration and per-ring state changes driven by received interrupts.

## Dependencies And Integration Points
It integrates with SOC15 IH SDMA client handling, SDMA v4 ring/fence code, VM fault reporting, SRBM write protection handling, ECC/RAS handling, queue preemption, and GPU reset recovery.

## Risks
The SDMA0 4.0 and SDMA1 4.0 tables have the same numeric values but different macro namespaces; code must use the right namespace for clarity and per-engine registration. Misrouting XNACK/page fault/null events can produce poor VM fault diagnostics or fail to recover a ring hang.

## Test Signals
Build SDMA v4.0 and v4.4.2. Runtime tests include SDMA trap and fence events, preemption, page fault/XNACK reporting, invalid doorbell, poll timeout, SRBM write protection, ECC/SRAM ECC, context empty, and reset after SDMA hang.
