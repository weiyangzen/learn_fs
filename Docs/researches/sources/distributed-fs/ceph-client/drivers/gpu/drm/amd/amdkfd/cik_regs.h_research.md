# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cik_regs.h

## Purpose
`cik_regs.h` provides CIK KFD register-field helper macros and default values for queue, memory, HQD, doorbell, and scheduling setup.

## Important APIs, Types, And Functions
There are no functions or types. Important macros include `PRIVATE_BASE`, `SHARED_BASE`, `PTR32`, `ALIGNMENT_MODE`, memory type constants, `DEFAULT_CP_HQD_PERSISTENT_STATE`, `PRELOAD_REQ`, `MQD_CONTROL_PRIV_STATE_EN`, `DEFAULT_MIN_IB_AVAIL_SIZE`, `IB_ATC_EN`, quantum fields, read-pointer block/min-available defaults, `PQ_ATC_EN`, `NO_UPDATE_RPTR`, `DOORBELL_OFFSET`, `DOORBELL_EN`, `PRIV_STATE`, `KMD_QUEUE`, `AQL_ENABLE`, and `GRBM_GFX_INDEX`.

## Control Flow
Callers use these macros while initializing MQDs, HQDs, queue properties, memory apertures, and doorbells. The macros expand into bit patterns consumed by GPU registers.

## State And Persistence
The header owns no state. Its values become persistent hardware queue state in MQDs and registers, including memory aperture behavior, ATC enablement, read pointer behavior, queue privilege, and scheduling quantum.

## Dependencies And Integration Points
It is used by CIK KFD queue/device-queue/MQD managers, and indirectly depends on CIK hardware register semantics. A repository search shows `PRIVATE_BASE` and `DEFAULT_CP_HQD_PERSISTENT_STATE` used by CIK queue manager and MQD manager code.

## Risks
Incorrect bit positions can corrupt queues or memory aperture configuration. Default ATC, pointer, and doorbell flags affect address translation, ring progress, and interrupt behavior. The macros are raw shifts without validation, so callers must bound and sanitize inputs.

## Test Signals
Signals include successful CIK queue creation/destruction, AQL dispatch, doorbell writes, HQD scheduling, scratch/LDS aperture correctness, ATC-enabled memory access, and no queue hangs under preemption or pointer-update stress.
