# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/push507c.h

## Purpose
Defines NV507C display/base-channel pushbuffer packet encoders.

## Important APIs, Types, And Functions
Exports `PUSH_HDR`, `PUSH_MTHD_HDR`, `PUSH_MTHD_INC`, and `PUSH_JUMP` using `NV507C_DMA_*` fields.

## Control Flow
Macros validate method/count/jump fields and emit DMA method or jump packets.

## State And Persistence
No independent state; emitted words update the pushbuffer and hardware state when processed.

## Dependencies And Integration Points
Depends on `nvif/push.h`, `nvhw/class/cl507c.h`, and display channel code.

## Risks
Incorrect method count or offset validation can corrupt display push streams.

## Test Signals
NV50 display channel updates, modesets, debug traces, and no EVO DMA faults validate behavior.
