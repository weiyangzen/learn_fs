<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_vbt_defs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_vbt_defs.h

## Purpose
This header defines the packed VBT data structures and constants for MIPI DSI panel configuration, PPS delays, and sequence blocks.

## Important APIs, Types, and Functions
Core definitions are `enum mipi_seq`, `enum mipi_seq_element`, `MIPI_DSI_UNDEFINED_PANEL_ID`, `MIPI_DSI_GENERIC_PANEL_ID`, `struct mipi_config`, and `struct mipi_pps_data`. `struct mipi_config` includes panel id, general panel flags, command/video mode, transfer mode, CABC/PWM control, pixel format, rotation, dual-link layout, lane count, DCS port masks, controller usage, burst/reference clocks, LP byte-clock selector, DPHY flags, timeout/timer values, DPHY timing fields, and GPIO indexes.

## Control Flow
There is no control flow. The values guide `intel_dsi_vbt.c` parsing and sequence execution, including handling of renamed assert/deassert reset sequence IDs to correct VBT spec wording confusion.

## State and Persistence Behavior
The packed structs mirror BIOS/VBT binary data and must preserve field order, bit widths, and packing. PPS delays are stored in 100us units and converted by consumers. Sequence and element enum values are persistent VBT ABI values.

## Dependencies and Integration Points
The header depends only on Linux integer types. It integrates with BIOS VBT parsing, DSI VBT initialization, panel power sequencing, and MIPI command execution.

## Risks
Changing packed bitfields or enum ordering would break VBT decoding. Some fields are only valid for specific VBT BDB versions, so consumers must gate behavior. Rotation, dual-link, DCS port, and byte-clock constants are small numeric ABI values and should not be conflated with DRM/MIPI runtime enums without conversion.

## Test Signals
Signals include binary VBT parsing tests, structure-size/offset checks where available, DSI panel init on multiple VBT versions, correct delay conversion, and sequence ID logs matching BIOS-defined panel sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_vbt_defs.h -->
