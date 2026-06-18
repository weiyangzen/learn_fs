# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_pingpong.c

## Purpose
Implements DPU pingpong block operations for command-mode tear-check, autorefresh handling, line-count reads, dither setup, and older-generation DSC glue.

## Important APIs, types, and functions
- `dpu_hw_pingpong_init()` constructs the block and installs generation-specific ops.
- Tear-check functions: `dpu_hw_pp_enable_te()`, `dpu_hw_pp_disable_te()`, `dpu_hw_pp_connect_external_te()`, `dpu_hw_pp_get_line_count()`, and `dpu_hw_pp_disable_autorefresh()`.
- Dither path: `dpu_hw_pp_setup_dither()` and `dither_depth_map`.
- DSC path: `dpu_hw_pp_setup_dsc()`, `dpu_hw_pp_dsc_enable()`, and `dpu_hw_pp_dsc_disable()`.

## Control flow
Initialization installs tear-check/autorefresh ops only for MDSS core versions below 5, older DSC ops below 7, and dither support for core versions 3 and newer. Tear-check enable writes vsync counter, sync height, init, IRQ, start position, thresholds, and finally enables the block. External TE toggles bit 20 in `PP_SYNC_CONFIG_VSYNC` and returns the original state. Autorefresh disable temporarily disconnects external TE, clears autorefresh, polls write-pointer line count until frame transfer is outside the active display area or timeout, then reconnects TE.

## State and persistence
The wrapper stores MMIO base, pingpong index, catalog caps, optional merge_3d pointer, and ops. Programmed state persists in pingpong registers: TE settings, autorefresh bit/count, dither matrix, DSC mode, and line counters.

## Dependencies and integration points
Depends on MDSS structures, register helpers, KMS timeout constants, tracepoints, and catalog sub-block offsets. Encoder command-mode code uses tear-check and autorefresh paths; output/DSC code uses DSC ops on older hardware; post-processing uses dither.

## Risks
Dither bit-depth indexes are used directly into a 9-element table, so callers must pass valid bit depths. Autorefresh disable is timing-sensitive and logs but does not hard-fail on timeout. The PP dither matrix loop writes offsets using `i` increments, which matches existing register packing but is sensitive to matrix size assumptions. Ops availability varies by core version, so callers must check function pointers.

## Test signals
Signals include command-mode panel TE stability, autorefresh disable logs, line-count reads during commits, DSC enablement on pre-v7 cores, visual dithering, and pingpong register snapshots. Tracepoint `trace_dpu_pp_connect_ext_te` captures TE mux changes.
