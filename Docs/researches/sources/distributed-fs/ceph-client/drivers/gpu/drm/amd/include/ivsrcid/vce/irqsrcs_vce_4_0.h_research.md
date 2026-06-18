# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/vce/irqsrcs_vce_4_0.h

## Purpose
Defines VCE 4.0 trap context IDs for general-purpose, low-latency, and real-time encode queues.

## Important APIs, Types, and Functions
There are no functions or structs. The constants are `VCE_4_0__CTXID__VCE_TRAP_GENERAL_PURPOSE` `0`, `VCE_4_0__CTXID__VCE_TRAP_LOW_LATENCY` `1`, and `VCE_4_0__CTXID__VCE_TRAP_REAL_TIME` `2`.

## Control Flow
The header has no executable code. Trap handling uses these context IDs to attribute a VCE event to the right queue class and service the matching ring/fence.

## State and Persistence
No state is stored. The context IDs are stable firmware/hardware contract values.

## Dependencies and Integration Points
Only the include guard is local. Integration points include VCE trap decoding, ring interrupt handlers, and queue-specific encode completion paths.

## Risks and Test Signals
Misnumbering can complete or diagnose the wrong VCE ring. Test signals include encode workloads on all three VCE queue classes and confirmation that completion is attributed to the expected context.
