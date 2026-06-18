# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/pushc97b.h

## Purpose
Defines NVC97B Blackwell display push method encoding.

## Important APIs, Types, And Functions
Exports `PUSH_HDR`, `PUSH_MTHD_HDR`, and `PUSH_MTHD_INC` using `NVC97B_DMA_METHOD_OFFSET`, `METHOD_COUNT`, and method opcode fields.

## Control Flow
The macro validates method offset/count and emits one encoded method packet word.

## State And Persistence
No local state; the caller's pushbuffer cursor advances.

## Dependencies And Integration Points
Depends on `nvif/push.h`, `nvhw/class/clc97b.h`, and GB202 display channel code.

## Risks
Incorrect field masks or using an older encoder for GB202 can fault display DMA processing.

## Test Signals
GB202 display modesets, debug push traces, and absence of display DMA faults validate behavior.
