# sources/distributed-fs/ceph-client/drivers/clk/mxs/clk.c

Purpose: Holds shared MXS clock infrastructure: the global spinlock and a busy-bit wait helper used by divider and fractional clocks.

Important APIs, types, and functions: `DEFINE_SPINLOCK(mxs_lock)` provides the shared serialization lock. `mxs_clk_wait(void __iomem *reg, u8 shift)` polls a bit in a register until it clears or 10 ms elapse.

Control flow: Clock set-rate paths write hardware fields, then call `mxs_clk_wait()` with the associated busy bit. The helper loops on `readl_relaxed(reg) & BIT(shift)` and returns `-ETIMEDOUT` if `time_after(jiffies, timeout)` becomes true.

State and persistence: The spinlock is global state shared by all MXS helper clocks. The wait helper does not persist state; it observes MMIO busy bits.

Dependencies and integration points: Included by all MXS helper files through `clk.h`. Depends on `jiffies`, `msecs_to_jiffies()`, relaxed IO reads, and Linux spinlock semantics.

Risks: Busy polling has no CPU relaxation call and can spin for up to 10 ms. If called while jiffies are not advancing, timeout behavior may be affected. Incorrect shift values can make rate changes appear stuck or complete prematurely.

Test signals: Inject or emulate stuck busy bits to confirm `-ETIMEDOUT`. Rate-change tests for `mxs_clk_div()` and `mxs_clk_frac()` should verify they propagate this error. Lockdep should not report issues around `mxs_lock`.
