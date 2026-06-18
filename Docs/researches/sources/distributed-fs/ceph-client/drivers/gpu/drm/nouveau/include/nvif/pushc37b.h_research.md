# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/pushc37b.h

## Purpose
Defines NVC37B display immediate/window-channel push method encoding.

## Important APIs, Types, And Functions
Exports `PUSH_HDR`, `PUSH_MTHD_HDR`, and `PUSH_MTHD_INC` using `NVC37B_DMA_*` fields.

## Control Flow
The macro validates method offset/count and emits a method packet word.

## State And Persistence
No state; it writes into the caller's pushbuffer.

## Dependencies And Integration Points
Depends on `nvif/push.h`, `nvhw/class/clc37b.h`, and Volta display channel code.

## Risks
Wrong class encoder on another display generation can emit incompatible packets.

## Test Signals
GV100 display channel submissions, modesets, and push traces validate behavior.
