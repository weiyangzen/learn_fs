# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce80/dce80_timing_generator.c

## Purpose
Implements the DCE 8.0 timing-generator specialization by reusing the DCE 11 timing-generator core and overriding the timing-programming and advanced-request behavior needed by older DCE8 CRTC/DMIF hardware. It wires an instance-specific `timing_generator_funcs` table into `struct dce110_timing_generator`.

## Important APIs, Types, And Functions
The local `enum black_color_format` is defined but unused in this file. `reg_offsets[]` maps DCE8 CRTC and DCP instance register offsets for six controllers. `program_pix_dur()` computes and writes the DMIF pixel duration from `pix_clk_100hz`. `dce80_timing_generator_program_timing()` optionally programs pixel duration, then delegates mode programming to `dce110_tg_program_timing()`. `dce80_timing_generator_enable_advanced_request()` toggles legacy requestor mode and prefetch/start-line fields based on vertical sync plus front porch. `dce80_timing_generator_construct()` initializes base fields, offsets, vblank limits, porch minima, BIOS pointer, and the DCE8 function table.

## Control Flow
Construction stores caller-provided offsets, selects derived offsets from `reg_offsets[instance]`, assigns `dce80_tg_funcs`, and defines timing limits. During timing programming, VBIOS-owned modes skip `program_pix_dur()`, while driver-owned modes update `DMIF_PG0_DPG_PIPE_ARBITRATION_CONTROL1.PIXEL_DURATION` before forwarding to the DCE110 implementation. Advanced request programming reads `CRTC_START_LINE_CONTROL`, sets `CRTC_LEGACY_REQUESTOR_EN`, selects advanced start-line position `3` with prefetch disabled for very short vertical blanking, otherwise position `4` with prefetch enabled, and forces progressive/interlace early start flags.

## State And Persistence
Persistent state is hardware register state and fields inside the provided `dce110_timing_generator` object. The file does not allocate memory or persist software state beyond function pointers, offsets, and timing limits. Register writes persist until later display mode programming or CRTC reset.

## Dependencies And Integration Points
Depends on DCE8 register definitions, `dm_services` register accessors, DCE110 timing-generator helpers, BIOS pointers from `dc_context`, and the common `timing_generator` interface. It integrates into resource construction for DCE8 display pipes and exposes behavior through the `timing_generator_funcs` vtable.

## Risks
`reg_offsets[instance]` assumes a valid instance index; invalid resource construction could index beyond the six-entry table. `program_pix_dur()` divides by pixel clock and silently skips zero clocks; callers must not rely on register refresh when pixel clock is zero. Advanced-request heuristics depend on vblank geometry and can affect underrun/prefetch behavior on edge timings.

## Test Signals
Useful signals are successful mode set on all DCE8 CRTCs, no DMIF arbitration underflows, correct `PIXEL_DURATION` register values for non-VBIOS mode programming, and regression tests around very small `v_sync_width + v_front_porch` timings.
