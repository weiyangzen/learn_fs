# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_intf.h

## Purpose
Declares the DPU INTF hardware wrapper API, timing parameter structures, status/config payloads, and init function.

## Important APIs, Types, and Functions
`struct dpu_hw_intf_timing_params` describes active panel size, programmed width/height, porches, sync widths, polarity, colors, skew, widebus, compression, and compressed bytes per line. `struct dpu_hw_intf_prog_fetch` carries fetch enable and start counter. `struct dpu_hw_intf_status` reports timing enable, programmable fetch enable, frame count, and line count. `struct dpu_hw_intf_cmd_mode_cfg` carries command-mode compression and widebus flags. `struct dpu_hw_intf_ops` exposes timing, fetch, status, PP binding, MISR, tearcheck, vsync selection, autorefresh disable, and command-mode config ops. `struct dpu_hw_intf` stores register map, INTF index, catalog cap, MDSS version, and ops. `dpu_hw_intf_init` constructs the wrapper.

## Control Flow and State
The header’s ops assume clocks are enabled and the caller coordinates CTL flush/start. Ops are generation- and interface-type-gated in implementation: PP binding appears on DPU5+, tearcheck only for DPU5+ DSI, command config on DPU7+.

## Dependencies and Integration Points
Depends on catalog, MDSS, utility types, `struct msm_format`, `struct dpu_hw_tear_check`, `struct dpu_hw_pp_vsync_info`, and `struct dpu_vsync_source_cfg`. It is consumed by command/video physical encoders and diagnostics.

## Risks and Test Signals
Callers must handle optional ops and must pass coherent timing parameters after split, widebus, and DSC adjustments. Tests should assert op availability by core major/interface type, validate timing params from video encoder, and verify command-mode TE paths use INTF ops only when advertised.
