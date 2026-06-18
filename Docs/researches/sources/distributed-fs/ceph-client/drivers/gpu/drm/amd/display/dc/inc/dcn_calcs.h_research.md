# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/dcn_calcs.h

## Purpose

`dcn_calcs.h` defines early DCN bandwidth, watermark, and mode-support data structures and APIs. It mirrors Display Mode Library concepts for DCN 1.x using float-heavy internal state, SoC/IP bounding boxes, and validation/update helper functions.

## Important APIs, Types, And Functions

Important constants define plane/state counts and DDR4 parameters. `enum dcn_bw_defs` represents voltage states, support flags, swizzle/surface/pixel/output formats, and encoder bpc. `struct dcn_bw_internal_vars` is the large formula workspace. `struct dcn_soc_bounding_box` and `struct dcn_ip_params` define hardware bounds with external defaults `dcn10_soc_defaults` and `dcn10_ip_defaults`. Public functions include `dcn_validate_bandwidth`, `dcn_get_soc_clks`, PPLIB clock update/notify helpers, `dcn_bw_sync_calcs_and_dml`, and `swizzle_mode_to_macro_tile_size`.

## Control Flow

Validation populates `dcn_bw_internal_vars` from `dc_state` pipe data, SoC/IP limits, and PowerPlay clocks, then evaluates bandwidth, DPP/DET/LB sizing, prefetch, urgent/stutter/DRAM-clock watermarks, clock support, DIO support, writeback support, and selected voltage level. PPLIB update functions refresh clock tables and notify firmware of watermark ranges.

## State And Persistence Behavior

`dcn_bw_internal_vars` is embedded in `dc_state`, not stack-allocated. Final outputs flow into `dc_state.bw_ctx.bw.dcn`, including clocks, watermarks, writeback arb params, compbuf/MALL sizes, mcache allocations, and FAMS config in newer code paths. There is no direct register programming in this header.

## Dependencies And Integration Points

It includes `bw_fixed.h` and `dml/display_mode_lib.h`. It integrates with resource validation, clock manager/PPLIB, HUBBUB watermark programming, DML synchronization, and swizzle/tile interpretation used by memory-fetch programming.

## Risks And Edge Cases

The workspace has many fixed-size arrays based on six planes and five states; exceeding those assumptions is unsafe. Float comparisons around support thresholds can change validation at mode boundaries. `dcn_bw_defs` mixes support values, voltage states, formats, and output types in one enum, so assigning the wrong category may compile. Legacy DCN calcs and newer DML/DML2 data must stay synchronized.

## Test Signals

Golden validation should cover DCN10 clocks, DPP split, ODM/DSC capability, DCC, swizzle modes, writeback, GPUVM/PTE, prefetch, p-state/stutter support, and PowerPlay clock-table changes. Runtime signals include watermark ranges, selected clocks, validation status, underflow, and PPLIB notifications.
