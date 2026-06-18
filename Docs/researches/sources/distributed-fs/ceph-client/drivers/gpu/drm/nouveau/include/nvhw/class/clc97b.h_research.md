# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc97b.h

## Purpose
Defines the NVC97B DMA pushbuffer instruction encoding used by Blackwell-era display immediate/window channels.

## Important APIs, Types, And Functions
Exports `NVC97B_DMA_*` macros for opcode, method count, method offset, data payload, jump offset, and subdevice-mask values. Supported opcodes are method, jump, non-incrementing method, and set-subdevice-mask.

## Control Flow
No executable flow exists. The macros are used by `nvif/pushc97b.h` to encode pushbuffer words; the GPU command processor then interprets the stream.

## State And Persistence
No local state is stored. The encoded commands mutate display/object state when consumed by hardware.

## Dependencies And Integration Points
Depends on `nvhw/drf.h` accessors through consumers such as `PUSH_HDR`. It pairs with Blackwell display class IDs in `nvif/class.h`.

## Risks
The method offset and count fields are compact bitfields. Bad validation or shift math in consumers can emit malformed DMA words and wedge the display channel.

## Test Signals
Compile-time macro use, debug push traces, successful GB202 display channel submissions, and absence of DMA opcode faults validate this header.
