# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/push.h

## Purpose
Provides the generic NVIF pushbuffer writer abstraction and macro framework for emitting method/data packets safely.

## Important APIs, Types, And Functions
Defines `struct nvif_push`, `PUSH_WAIT`, `PUSH_KICK`, debug printing/assertion helpers, `PUSH_DATA`, reserved writes, bulk data writes, `PUSH()` generic arity dispatcher, and convenience forms `PUSH_IMMD`, `PUSH_MTHD`, `PUSH_1INC`, and `PUSH_NINC`.

## Control Flow
`PUSH_WAIT` ensures enough room, possibly calling the channel wait hook. Push macros emit a packet header then data words, checking segment and end bounds. `PUSH_KICK` submits accumulated words when `cur != bgn`.

## State And Persistence
`nvif_push` tracks memory object, GPU address, hardware get/max, and CPU pointers `bgn/cur/seg/end`. State persists for the channel/pushbuffer lifetime and changes on every emitted word or kick.

## Dependencies And Integration Points
Depends on `nvif/mem.h`, `nvif/printf.h`, `nvhw/drf.h`, and class-specific push headers that define packet encoders.

## Risks
Macro complexity and variadic dispatch make argument ordering critical. Segment/end bugs can corrupt pushbuffers; missing wait/kick can hang submissions.

## Test Signals
Debug push traces, overrun WARNs, channel submission tests, GPFIFO wrap tests, and GPU method-fault absence validate behavior.
