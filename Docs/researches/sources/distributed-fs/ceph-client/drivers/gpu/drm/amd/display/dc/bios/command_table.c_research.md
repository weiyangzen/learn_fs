# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table.c

## Purpose
This file implements the legacy ATOM BIOS command-table dispatcher for AMD display BIOS parser instances. `dal_bios_parser_init_cmd_tbl()` probes the command table parameter revisions exposed by the VBIOS and fills `bp->cmd_tbl` with revision-specific handlers for encoder, transmitter, clock, CRTC, DAC, external encoder, power-gating, and DCE clock commands.

## Important APIs, Types, And Functions
- `dal_bios_parser_init_cmd_tbl()` is the external initializer consumed by the BIOS parser.
- `EXEC_BIOS_CMD_TABLE`, `BIOS_CMD_TABLE_REVISION`, and `BIOS_CMD_TABLE_PARA_REVISION` wrap `amdgpu_atom_execute_table()` and `amdgpu_atom_parse_cmd_header()` against `adev->mode_info.atom_context`.
- DIG encoder handlers cover legacy split tables (`DIG1EncoderControl`, `DIG2EncoderControl`) and `DIGxEncoderControl` parameter revisions 3, 4, and 5.
- Transmitter handlers cover `UNIPHYTransmitterControl` command revisions 2, 3, 4, 1.5, and 1.6.
- Pixel clock handlers cover `SetPixelClock` revisions 3, 5, 6, and 7; `program_clock_v5/v6()` reuse that VBIOS table to program display/engine clocks.
- Spread-spectrum, display PLL adjustment, CRTC source/timing, CRTC enable/memory request, DAC encoder/output/load detection, external encoder control, display power gating, and `SetDCEClock` each have revision-gated handlers.

## Control Flow
Initialization probes every relevant ATOM command table and assigns either a compatible handler or `NULL`. Runtime callers go through the function pointers in `struct cmd_tbl`, so unsupported VBIOS revisions naturally become unavailable operations. Each handler builds a packed ATOM parameter structure, translates DC enums through `bp->cmd_helper`, converts units and endian fields, calls the VBIOS table, and returns a `bp_result`.

Key conversion flow includes KHz to 10 KHz or 100 Hz units, HDMI deep-color pixel/symbol clock inflation, DP lane/link-rate selection, controller and PLL ID translation, and interlace polarity/timing bit packing. Some handlers also consume VBIOS outputs, such as adjusted display PLL frequency and `SetDCEClock` returning the actual programmed frequency.

## State And Persistence
The file persists no standalone data. It mutates `bp->cmd_tbl` during initialization and updates caller-provided parameter objects when VBIOS returns adjusted clock values, divisors, or DFS bypass clocks. Hardware and firmware state changes are performed through ATOM BIOS table execution.

## Dependencies And Integration Points
Dependencies include `amdgpu_atom_execute_table()`, ATOMBIOS structures/macros from `atom.h`, BIOS parser public/internal types, `bios_parser_helper`, `dm_services`, and the selected `command_table_helper`. It integrates with upper display core code through `dc_bios->funcs`, which delegates into the initialized command table operations.

## Risks
Revision handling is brittle: unrecognized command table revisions silently disable function pointers or fall back to older flows. Several paths assume helper function pointers are populated for the active DCE family. Unit conversions and 16-bit fields can truncate unexpected clocks. Some invalid inputs only trigger debugger assertions and continue with defaults. Legacy DAC/CRT and external-encoder paths have narrow enum support and return `BADINPUT` for unsupported combinations.

## Test Signals
Useful validation signals are successful display light-up across DCE generations, DP/HDMI/DVI clock accuracy including deep color, spread-spectrum enable/disable behavior, DP link training on different lane counts, suspend/resume with CRTC memory requests, DAC load detection on SI/CI hardware, and kernel logs from `dm_output_to_console`, `dm_error`, assertions, or ATOM table execution failures.
