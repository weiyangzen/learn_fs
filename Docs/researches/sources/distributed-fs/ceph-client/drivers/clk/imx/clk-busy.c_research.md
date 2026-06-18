## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-busy.c

### Purpose
`clk-busy.c` wraps standard divider and mux clocks with an i.MX busy-bit wait after rate or parent changes.

### Important APIs, Types, And Functions
`clk_busy_wait()` polls a busy register for up to 10 ms. `struct clk_busy_divider` and `struct clk_busy_mux` embed standard CCF divider/mux objects plus delegated ops and busy-bit location. Public constructors are `imx_clk_hw_busy_divider()` and `imx_clk_hw_busy_mux()`.

### Control Flow
The wrapper delegates recalc/determine/get operations to standard `clk_divider_ops` or `clk_mux_ops`. On set-rate or set-parent, it performs the standard register update, then polls until the busy bit clears or returns `-ETIMEDOUT`.

### State, Persistence, And Dependencies
State is allocated wrapper objects and MMIO register fields. The configured divider/mux values persist in hardware. It depends on global `imx_ccm_lock`, CCF primitive ops, jiffies, and `msecs_to_jiffies()`.

### Integration Points
i.MX SoC clock tables use these constructors for CCM fields that require hardware handshaking before consumers rely on the new rate or parent.

### Risks
Busy polling has no delay or CPU relaxation inside the loop. The clocks are registered as critical, which can prevent unused-clock cleanup. Timeout handling depends on jiffies progressing and the hardware busy bit being correctly described.

### Test Signals
Exercise parent/rate changes on busy clocks, force a stuck busy bit to see `-ETIMEDOUT`, inspect critical-clock behavior, and verify no consumers observe transient rates before busy clears.
