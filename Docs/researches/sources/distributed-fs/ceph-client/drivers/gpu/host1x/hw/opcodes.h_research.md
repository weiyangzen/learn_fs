<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/opcodes.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/opcodes.h

## Purpose

`opcodes.h` defines helpers for constructing host1x class register payloads and pushbuffer opcodes. It centralizes the command encoding consumed by channel submission, timeout recovery, and debug decoding.

## Important APIs, Types, And Functions

- Class payload helpers build wait, wait-base, load-base, increment-syncpoint, and indirect-register-access values using generated uclass field macros.
- Opcode helpers build SETCLASS, INCR, NONINCR, MASK, IMM, RESTART, GATHER, GATHER_NONINCR/INCR, SETSTREAMID, SETPAYLOAD, GATHER_W, ACQUIRE_MLOCK, and RELEASE_MLOCK words.
- `HOST1X_OPCODE_NOP` is encoded as `NONINCR(0, 0)`.

## Control Flow

All functions are pure inline encoders. Runtime flow is in `channel_hw.c`, which emits these words into the CDMA pushbuffer, and `debug_hw.c`, which decodes the same opcode nibbles.

## State And Persistence Behavior

The header stores no state. Encoded words become persistent pushbuffer contents until CDMA consumes or timeout recovery overwrites them.

## Dependencies And Integration Points

It depends on generated uclass field macros and Linux `BIT()`. It is included by each generation hardware umbrella header.

## Risks And Test Signals

The encodings are ABI-level hardware contracts. Wide gather and stream-ID opcodes are valid only on newer hardware; callers must gate them. Tests should compare emitted opcodes against known-good sequences for waits, gathers, stream-ID switching, MLOCK acquire/release, and restart padding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/opcodes.h -->
