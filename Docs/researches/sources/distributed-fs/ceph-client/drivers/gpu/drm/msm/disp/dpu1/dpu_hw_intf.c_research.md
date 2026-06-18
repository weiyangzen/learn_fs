# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_intf.c

## Purpose
Implements DPU interface/timing-engine hardware operations: timing generator programming, timing enable, programmable fetch, PP mux binding, status counters, MISR, DSI command-mode tearcheck, autorefresh disable, vsync source selection, watchdog timer setup, and command-mode datapath flags.

## Important APIs, Types, and Functions
The public constructor is `dpu_hw_intf_init`. Core ops are `dpu_hw_intf_setup_timing_engine`, `dpu_hw_intf_enable_timing_engine`, `dpu_hw_intf_setup_prg_fetch`, `dpu_hw_intf_bind_pingpong_blk`, `dpu_hw_intf_get_status`, `dpu_hw_intf_get_line_count`, `dpu_hw_intf_setup_misr`, `dpu_hw_intf_collect_misr`, `dpu_hw_intf_enable_te`, `dpu_hw_intf_disable_te`, `dpu_hw_intf_connect_external_te`, `dpu_hw_intf_vsync_sel`, `dpu_hw_intf_vsync_sel_v8`, `dpu_hw_intf_disable_autorefresh`, and `dpu_hw_intf_program_intf_cmd_cfg`.

## Control Flow and State
Timing setup calculates hsync/vsync periods, display and active windows, polarity, panel format, data-valid window, widebus and DSC flags, and DP-specific timing adjustments, then writes INTF registers. DPU5+ gets `INTF_CONFIG2` data timing and compression/widebus registers. Programmable fetch toggles bit 31 of `INTF_CONFIG` and writes a start counter. Status reads use `INTF_STATUS` on DPU5+ or timing enable on older cores, then frame/line counters only when enabled. TE setup programs vsync counter, height, init, thresholds, read pointer IRQ, and start position. Autorefresh disable temporarily disconnects external TE, clears autorefresh, polls write pointer outside active lines, then reconnects TE.

## Dependencies and Integration Points
Consumes catalog INTF caps and MDSS version, MSM format bit depths, DPU tearcheck structs, PP vsync info, vsync source config, MISR helpers, tracepoints, and encoder timing/TE setup. Command and video physical encoders rely on these ops.

## Risks and Test Signals
High-risk areas are timing math, DP special casing, DSC/widebus data window programming, TE/autorefresh sequencing, and generation-gated ops. Tests should cover DSI video, DSI command TE, DP widebus, DSC DSI data compression, programmable fetch, frame/line counters, MISR signature collection, watchdog vsync source on DPU8, INTF_NONE skip, PP binding, and autorefresh disable timeout behavior.
