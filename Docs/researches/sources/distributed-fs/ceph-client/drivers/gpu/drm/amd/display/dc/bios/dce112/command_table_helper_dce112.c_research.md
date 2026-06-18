# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/dce112/command_table_helper_dce112.c

## Purpose
This file defines the legacy helper vtable for DCE11.2 and DCE11.22, adding combo PHY PLL, DCE clock type, and transmitter color-depth mapping needed by later ATOM command table revisions.

## Important APIs, Types, And Functions
- `dal_cmd_tbl_helper_dce112_get_table()` returns the helper table.
- Static functions map signal modes, HPD selection, clock sources, encoder actions, display power gating, DCE clock type, and transmitter color depth.
- The table reuses legacy shared helpers for controller, engine, PHY, encoder ID, and encoder mode conversions.

## Control Flow
The helper uses V6 ATOM transmitter modes and combo PHY clock source constants. It maps `ENCODER_CONTROL_SETUP` to `ATOM_ENCODER_CMD_STREAM_SETUP`, unlike older helpers that use `ATOM_ENCODER_CMD_SETUP`.

## State And Persistence
The helper table is immutable static data and stores no mutable state.

## Dependencies And Integration Points
It depends on `atom.h`, BIOS parser types, and `command_table_helper.h`. It is selected by the legacy helper initializer for DCE11.2-family ASICs.

## Risks
Unsupported clock source IDs cause helper failure and upstream command failure. Unknown DCE clock types assert but still return `true`, which may hide an invalid output if not examined. Several legacy callbacks are intentionally `NULL`.

## Test Signals
Signals include successful `SetPixelClock` v7, `SetDCEClock`, and UNIPHY transmitter programming on DCE11.2, plus correct deep-color ratios for HDMI pixel-clock programming.
