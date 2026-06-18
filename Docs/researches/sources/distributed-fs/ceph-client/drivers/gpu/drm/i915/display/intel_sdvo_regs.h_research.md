# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sdvo_regs.h

## Purpose
`intel_sdvo_regs.h` defines the SDVO command protocol ABI used by `intel_sdvo.c`: output flag bits, packed command request/reply structures, SDVO I2C register offsets, command opcodes, status codes, timing structures, TV format/resolution structures, panel/enhancement structures, DDC bus switch bits, and HDMI/audio host-buffer command definitions.

## Important APIs, Types, And Functions
- Output bit definitions: `SDVO_OUTPUT_TMDS*`, `SDVO_OUTPUT_RGB*`, `SDVO_OUTPUT_CVBS0`, `SDVO_OUTPUT_SVID0`, `SDVO_OUTPUT_YPRPB0`, `SDVO_OUTPUT_LVDS*`, and `SDVO_OUTPUT_LAST`.
- Core packed structs: `struct intel_sdvo_caps`, `struct intel_sdvo_dtd`, `struct intel_sdvo_pixel_clock_range`, `struct intel_sdvo_preferred_input_timing_args`, `struct intel_sdvo_get_trained_inputs_response`, and `struct intel_sdvo_in_out_map`.
- Command transport registers: `SDVO_I2C_ARG_*`, `SDVO_I2C_OPCODE`, `SDVO_I2C_CMD_STATUS`, `SDVO_I2C_RETURN_*`, and `SDVO_I2C_VENDOR_BEGIN`.
- Command status codes: success, not supported, invalid argument, pending, target-not-specified, and scaling-not-supported.
- Timing and clock commands: target input/output, input/output timing part 1/2, preferred input timing, pixel clock ranges, and clock multiplier commands.
- TV/LVDS/enhancement structures: TV format bitfields, SDTV/HDTV resolution request/reply structures, panel power sequencing, backlight/ambient light replies, and enhancement limit/value commands.
- HDMI/audio host-buffer definitions: encode/colorimetry, pixel replication, audio state bits, host-buffer index/data/tx-rate commands, AVI/ELD buffer indices, and `SDVO_NEED_TO_STALL`.

## Control Flow
The header has no executable logic. Its structure mirrors the SDVO command interface: clients write arguments into `SDVO_I2C_ARG_*`, issue an opcode, poll `SDVO_I2C_CMD_STATUS`, and read `SDVO_I2C_RETURN_*`. Timing commands are split into part 1 and part 2 records, matching the packed `intel_sdvo_dtd` layout used by the implementation.

## State And Persistence
The file defines the wire/storage shape of SDVO state but does not own state. Most structs are `__packed` because their layout is directly exchanged with SDVO firmware over I2C. Bitfields represent persistent device capabilities, supported formats, selected power states, enhancement values, and host-buffer state once programmed.

## Dependencies And Integration Points
It depends on Linux compiler and integer types. It is consumed by `intel_sdvo.c` and any SDVO command code needing exact opcode and layout definitions. The DTD layout intentionally aligns with EDID detailed timing concepts, and HDMI definitions integrate with DRM HDMI infoframe/audio handling through the implementation.

## Risks And Edge Cases
Packed bitfield layout is compiler- and endian-sensitive, so changes must be treated as ABI changes against SDVO firmware. Several comments indicate legacy typos or quirks, such as zero-based host-buffer size and output-function ordering assumptions. Command result lengths must match `BUILD_BUG_ON()` checks in the implementation. Adding new opcodes without debug-name coverage reduces diagnostic quality but not functionality.

## Test Signals
Compile-time `BUILD_BUG_ON()` checks in `intel_sdvo.c` validate key structure sizes. Runtime signals include successful capability reads, timing programming, TV format/resolution queries, enhancement property creation, HDMI AVI/ELD host-buffer transfers, and correct command-status handling for unsupported features.
