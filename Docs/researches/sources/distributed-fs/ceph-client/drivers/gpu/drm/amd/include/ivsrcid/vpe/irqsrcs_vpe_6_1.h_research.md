# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vpe/irqsrcs_vpe_6_1.h

## Purpose
Defines VPE 6.1 interrupt source IDs for command completion, traps, preemption, VM/MMHUB errors, queue hangs, timeouts, and doorbell validation.

## Important APIs, Types, and Functions
No functions or types are declared. `VPE_6_1_SRCID__*` macros map IDs `0`-`12`: atomic return done, trap, SRBM write protection, context empty, preempt, queue hang/command timeout, atomic timeout, poll timeout, VM hole, MMHUB NACK general error, MMHUB PRT NACK, invalid doorbell, and IB preempt.

## Control Flow
No code executes here. VPE interrupt handlers use the constants to route events to queue completion, trap, fault, preemption, or hang recovery paths.

## State and Persistence
No state exists. The macro values are compile-time hardware constants.

## Dependencies and Integration Points
The header depends only on its include guard. It integrates with VPE ring scheduling, MMHUB fault interpretation, interrupt registration, doorbell validation, and recovery paths.

## Risks and Test Signals
Risks include conflating VPE-specific MMHUB NACKs with generic VM faults or missing queue-hang recovery. Tests should exercise VPE submissions, IB preempt, invalid doorbell, VM-hole access, and timeout recovery.
