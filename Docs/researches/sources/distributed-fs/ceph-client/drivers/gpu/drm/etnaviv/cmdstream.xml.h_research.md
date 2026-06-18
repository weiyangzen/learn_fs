# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/cmdstream.xml.h

## Purpose
Generated Vivante FE command stream opcode and bitfield definitions used to construct and validate GPU command buffers.

## Important APIs, Types, and Functions
Defines `FE_OPCODE_*` values, primitive types, and `VIV_FE_*` command packet fields for LOAD_STATE, END, NOP, DRAW variants, WAIT, LINK, STALL, CALL/RETURN, CHIP_SELECT, WAIT_FENCE, DRAW_INDIRECT, and SNAP_PAGES. Macros provide masks, shifts, and field encoders such as `VIV_FE_LOAD_STATE_HEADER_COUNT(x)` and `VIV_FE_LINK_HEADER_PREFETCH(x)`.

## Control Flow
No executable control flow. Consumers combine the macros to emit 32-bit command words; `etnaviv_buffer.h` wraps common emit patterns, while `etnaviv_cmd_parser.c` decodes opcodes and LOAD_STATE fields for validation.

## State and Persistence
No mutable state. The header is generated from rules-ng-ng XML inputs and must stay synchronized with hardware definitions.

## Dependencies and Integration Points
Used by etnaviv command generation, parser validation, and low-level GPU ring manipulation. It pairs with state register headers such as `state.xml.h` and common enum definitions.

## Risks
Incorrect generated constants can corrupt command streams or weaken validation. Manual edits would be fragile because the source of truth is the XML generator.

## Test Signals
Build coverage catches missing macros. Runtime command submission, parser rejection tests, and GPU hang diagnostics indicate whether packet encodings match hardware.
