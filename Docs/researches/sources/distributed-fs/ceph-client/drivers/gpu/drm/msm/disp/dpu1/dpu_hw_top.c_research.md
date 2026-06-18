# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_top.c

## Purpose
Implements the MDP TOP hardware wrapper for split-pipe control, clock-force control, danger/safe status reads, watchdog/vsync source programming, audio interface selection, and DP PHY/interface routing.

## Important APIs, types, and functions
- `dpu_hw_mdptop_init()` allocates and initializes `struct dpu_hw_mdp`.
- `dpu_hw_setup_split_pipe()` programs split display lower/upper controls and split flush.
- `dpu_hw_setup_clk_force_ctrl()` uses catalog clock-control registers.
- `dpu_hw_get_danger_status()` and `dpu_hw_get_safe_status()` decode top-level and SSPP status registers.
- `dpu_hw_setup_vsync_sel()` and `dpu_hw_setup_wd_timer()` configure pingpong vsync sources and watchdog timers.
- `dpu_hw_dp_phy_intf_sel()` programs SC8180X-style DP PHY mapping.

## Control flow
Initialization sets the top register base and installs ops based on MDSS major version: older cores get full vsync source selection, mid-generation cores use watchdog timer setup, v5+ get DP PHY interface selection, and v4/v5 get interface audio selection. Split-pipe setup chooses control bits differently for command versus video mode and for INTF_2 versus other interfaces. Vsync selection updates per-pingpong nibble fields and then programs a watchdog timer when requested.

## State and persistence
The wrapper stores catalog pointer, MMIO base, and ops. Hardware TOP registers persist split configuration, watchdog state, vsync source mapping, DP PHY mapping, and danger/safe status until reprogrammed or reset.

## Dependencies and integration points
Depends on `dpu_hwio.h` register offsets, catalog clock-control metadata, `FIELD_PREP`, and utility MMIO helpers. KMS init creates this object; debugfs danger/safe paths and encoder setup use its ops.

## Risks
`dpu_hw_setup_vsync_sel()` has a sparse static pingpong offset table and silently skips out-of-range indexes, so new pingpong IDs need care. Watchdog load calculation divides by frame rate and assumes valid nonzero values. DP PHY mapping is currently hard-coded by platform logic in KMS rather than data-driven DT, so future platforms can regress if they need different mappings.

## Test signals
Signals include correct split display operation, command-mode TE/vsync timing, watchdog timer behavior, debugfs danger/safe status, DP output routing on SC8180X, and MDP top register snapshots.
