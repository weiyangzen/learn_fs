# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/uvd/irqsrcs_uvd_7_0.h

## Purpose
Defines UVD 7.0 video interrupt source IDs for encoder and system-message events.

## Important APIs, Types, and Functions
No functions or types are declared. The macros are `UVD_7_0__SRCID__UVD_ENC_GEN_PURP` `119`, `UVD_7_0__SRCID__UVD_ENC_LOW_LATENCY` `120`, and `UVD_7_0__SRCID__UVD_SYSTEM_MESSAGE_INTERRUPT` `124`.

## Control Flow
No executable flow exists. UVD interrupt handlers use these constants to route encoder completions and firmware/system messages to the correct ring or fence path.

## State and Persistence
There is no runtime state. The source IDs are persistent hardware constants.

## Dependencies and Integration Points
The header has only its include guard. It integrates with UVD ring interrupt setup, video encode job completion, fence signaling, and firmware message processing.

## Risks and Test Signals
Wrong IDs could leave video fences unsignaled or ignore system messages. Tests should run UVD general-purpose and low-latency encode workloads and verify system-message interrupts complete expected flows.
