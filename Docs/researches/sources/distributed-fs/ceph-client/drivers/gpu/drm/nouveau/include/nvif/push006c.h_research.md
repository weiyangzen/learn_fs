# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/push006c.h

## Purpose
Defines NV06C-style pushbuffer packet encoders for old DMA channels and subchannel assignments.

## Important APIs, Types, And Functions
Exports default `PUSH006C_SUBC_*` assignments, `PUSH_HDR`, method/non-incrementing headers, increment fields, and `PUSH_JUMP`.

## Control Flow
Macros validate subchannel, method address, count, or jump offset, then write an encoded packet word through `PUSH_DATA__`.

## State And Persistence
No separate state; macros advance the caller's `nvif_push` cursor and emit GPU-consumed commands.

## Dependencies And Integration Points
Depends on `nvif/push.h`, `nvhw/class/cl006c.h`, and DRF helpers. Used by old host/channel classes and 2D/M2MF/copy objects.

## Risks
Wrong subchannel assignment or method increment mode can send methods to the wrong object.

## Test Signals
Legacy channel push submission, debug push traces, and absence of NV06C method faults validate behavior.
