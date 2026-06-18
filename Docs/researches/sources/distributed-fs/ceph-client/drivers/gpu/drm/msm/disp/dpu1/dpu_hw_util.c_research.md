# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_util.c

## Purpose
Provides shared DPU hardware utilities: logged register reads/writes, QSEED3/QSEED3Lite scaler programming, CSC programming, QoS LUT setup, MISR control, CDP programming, clock-force helper, and built-in CSC matrices.

## Important APIs, types, and functions
- `dpu_reg_write()` and `dpu_reg_read()` wrap relaxed MMIO and optional hardware logging.
- `dpu_hw_setup_scaler3()` programs QSEED scaler mode, phase, preload, LUTs, detail enhancer, source/destination sizes, and alpha filtering.
- `dpu_hw_csc_setup()` converts S15.16 matrix coefficients to hardware fields and writes clamp/bias values.
- `_dpu_hw_get_qos_lut()`, `_dpu_hw_setup_qos_lut()`, and `dpu_hw_setup_qos_lut_v13()` support pipe/WB QoS programming.
- `dpu_hw_setup_misr()` and `dpu_hw_collect_misr()` handle signature capture.
- `dpu_setup_cdp()` and `dpu_hw_clk_force_ctrl()` provide common block helpers.

## Control flow
Scaler setup exits with only opmode write when disabled, otherwise builds opmode from format and scaler config, optionally programs detail enhancer and LUTs, writes phase registers using either old packed phase or newer per-axis phase registers, then writes opmode. LUT setup validates lengths and indexes before writing directional/circular/separable tables. CSC setup writes a fixed register sequence from the provided config. MISR setup clears status, uses `wmb()`, then enables free-run capture.

## State and persistence
The only file-static state is `dpu_hw_util_log_mask`, exposed to debugfs. All other state is written to hardware registers or read from caller-provided config. CSC constants are immutable global data.

## Dependencies and integration points
Used by SSPP, WB, LM, TOP, VBIF, and other hardware wrappers. Depends on MSM format helpers for YUV/DX/UBWC decisions, catalog QoS tables, and common MDSS structures.

## Risks
Scaler LUT programming is size/index-sensitive and uses caller-provided pointers. `dpu_hw_clk_force_ctrl()` returns whether the clock was previously not forced, not the final state, so callers use it to know whether to undo. `dpu_setup_cdp()` assumes `fmt` is valid. CSC coefficient shifts and clamp widths differ for 10-bit versus 8-bit paths.

## Test signals
Signals include hardware log output when `hw_log_mask` matches block masks, visual scaling/CSC correctness, QoS tracepoints, MISR read status, CDP register dumps, and absence of underruns when clock-force wrapped VBIF programming runs.
