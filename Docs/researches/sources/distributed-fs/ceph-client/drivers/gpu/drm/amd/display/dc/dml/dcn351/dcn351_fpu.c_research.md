# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn351/dcn351_fpu.c

## Purpose
This file is the DCN3.51 variant of the DCN35 FPU support layer. It defines DCN351-specific IP/SOC bounding boxes, updates DML and DML2 bounding-box data from runtime clock tables and overrides, customizes DML pipe inputs, and decides z-state support with DCN351-specific restrictions.

## Important APIs, Types, And Functions
`dcn3_51_ip` is closely aligned with DCN35 IP settings: HostVM/GPUVM enabled, ROB/DET/config return buffer sizing, chunk/meta sizes, DSC and line-buffer capabilities, DPP/OTG limits, scaler limits, DPTE buffers, delay values, DCC, and `VBlankNomDefaultUS`. `dcn3_51_soc` differs materially from DCN35 by providing eight default clock states with DCFCLK/FCLK/SOCCLK/DRAM/DISPCLK/DPPCLK values, default four channels, and a 2400 MHz VCO. Public functions are `dcn351_update_bw_bounding_box_fpu()`, `dcn351_populate_dml_pipes_from_context_fpu()`, and `dcn351_decide_zstate_support()`. Private helpers mirror DCN35 dual-plane detection, microsecond-to-line conversion, and vertical back porch calculation.

## Control Flow And State
The update function asserts FPU availability, sets IP DPP/OTG counts and channel count, derives max display clocks, maps SMU clock entries to closest static clock-limit rows, copies clock data into scratch/global SOC tables, applies debug and `bb_overrides` latencies, reinitializes DML as `DML_PROJECT_DCN31`, and mirrors clocks/latencies into DML2 override tables. Pipe population calls the DCN31 base population, adjusts `vblank_nom`, forces immediate flip, disables unbounded request by default, zeros DCC fractions, sets DCC rate/DSC input bpc/GPUVM page size, changes DET size based on single-pipe, CRB policy, or upscaled multi-display cases, and applies eDP seamless boot ODM policy. Z-state logic explicitly notes DCN351 does not support z9/z10 and should allow at most Z8.

## State And Persistence Behavior
The file mutates global `dcn3_51_ip` and `dcn3_51_soc`, `dc->scratch.update_bw_bounding_box.clock_limits`, `dc->dml`, DML2 bounding-box overrides, per-context DML IP state, `pipes[]`, ODM policy in `context->bw_ctx.dml.vba`, and final z-state support. It has no persistent storage but carries mutable global runtime defaults.

## Dependencies And Integration Points
Includes DCN31/DCN32/DCN35/DCN351 resource headers, `dml/dcn31/dcn31_fpu.h`, `dml/dcn35/dcn35_fpu.h`, `dml_inline_defs.h`, and `link_service.h`. DCN351 resource code calls `dcn351_update_bw_bounding_box_fpu()` and `dcn351_populate_dml_pipes_from_context_fpu()`; the resource search also showed DCN351 init paths may reuse DCN35 z-state decisions in places, so naming and call-site choice matter.

## Risks
The z-state function contains a suspicious assignment-like ternary result: `support = allow_z8 ? allow_z8 : DCN_ZSTATE_SUPPORT_DISALLOW;`, which stores boolean `true` rather than an explicit `DCN_ZSTATE_SUPPORT_ALLOW_Z8_ONLY` enum value if `allow_z8` is true. That may only be safe if enum value `1` matches Z8-only. Like DCN35, the code assumes valid clock-table counts, uses a post-loop `pipe` pointer for single-pipe logic, and globally mutates bounding-box tables. DML is initialized as `DML_PROJECT_DCN31`, so DCN351 remains dependent on older DML function selection while feeding DML2 overrides separately.

## Test Signals
Tests should verify the eight-state default table is replaced correctly by SMU clocks, DML2 override clocks include DRAM speed and DTBCLK, latency overrides propagate, DET and unbounded request decisions match DCN351 policy, DSC input bpc is correct, and z-state outputs never allow unsupported z9/z10. A focused test should validate the `allow_z8` ternary maps to the intended enum.
