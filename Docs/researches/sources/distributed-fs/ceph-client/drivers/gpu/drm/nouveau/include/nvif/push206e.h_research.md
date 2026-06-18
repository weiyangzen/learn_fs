# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/push206e.h

## Purpose
Adds NV206E call-packet support on top of NV06C-style push helpers.

## Important APIs, Types, And Functions
Defines `PUSH_CALL`, validating and encoding a call offset using `NV206E_DMA_OPCODE2_CALL` and `NV206E_DMA_CALL_OFFSET`.

## Control Flow
The macro validates offset alignment/range and writes one call instruction into the pushbuffer.

## State And Persistence
No state; it advances the caller's push cursor and changes GPU control flow when consumed.

## Dependencies And Integration Points
Depends on `push006c.h`, `nvhw/class/cl206e.h`, and DRF helpers.

## Risks
Bad call target offsets can jump into invalid pushbuffer memory or create command loops.

## Test Signals
Pushbuffer call-chain tests, debug traces, and lack of DMA call faults validate behavior.
