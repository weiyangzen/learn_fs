## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-gate-93.c

### Purpose
`clk-gate-93.c` implements i.MX93 LPCG/root gate clocks with low-power-mode register support, shared enable counts, and TrustZone read-only detection.

### Important APIs, Types, And Functions
`struct imx93_clk_gate` stores register base, bit index, value, mask, lock, and optional share count. `imx93_clk_gate_do_hardware()`, enable/disable/is-enabled/disable-unused ops, and exported `imx93_clk_gate()` form the implementation.

### Control Flow
The constructor reads authorization bits; unauthorized domains get read-only ops. Enable increments shared count if present, then programs either `LPM_CUR_OFFSET` when CPU LPM is enabled or the direct register field otherwise. Disable decrements share count and disables only when the last user releases. `disable_unused` respects shared counts.

### State, Persistence, And Dependencies
Gate state persists in direct or LPM registers. Shared counts are caller-owned memory. Dependencies include i.MX93 authorization register layout and global `imx_ccm_lock`.

### Integration Points
i.MX93 SoC clock drivers use this for gates that may be shared by multiple logical clocks or controlled by secure firmware.

### Risks
Shared count correctness depends on all related clocks using the same counter. Authorization is sampled only at registration. Read-only clocks expose only `is_enabled`, so consumers cannot enable them if firmware leaves them off.

### Test Signals
Test shared gate reference counting, CPULPM enabled/disabled register paths, TrustZone read-only behavior, and unused-clock cleanup.
