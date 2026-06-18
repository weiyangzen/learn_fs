## sources/distributed-fs/ceph-client/drivers/clk/imx/clk-gate2.c

### Purpose
`clk-gate2.c` implements i.MX two-bit CGR-style gates, including optional shared enable counters.

### Important APIs, Types, And Functions
`struct clk_gate2` stores register, bit index, gate value, mask, lock, and optional share count. `clk_gate2_enable()`, `clk_gate2_disable()`, `clk_gate2_is_enabled()`, and `clk_gate2_disable_unused()` implement ops. `clk_hw_register_gate2()` is exported.

### Control Flow
Enable and disable serialize under the provided lock. Shared clocks increment/decrement the external counter and only program hardware on first enable or final disable. Hardware programming clears the masked field and writes `cgr_val` when enabling, or zero when disabling.

### State, Persistence, And Dependencies
Gate fields persist in CCM CGR registers. Shared counts are external state supplied by SoC drivers. It depends on CCF, MMIO, and correct CGR value/mask definitions.

### Integration Points
Legacy i.MX31/i.MX35 and many newer i.MX drivers use gate2-style clocks for peripheral gating.

### Risks
Shared counters can underflow if users pass inconsistent pointers. `clk_gate2_flags` is stored but unused. Disable writes an off value of zero, which must be valid for all users.

### Test Signals
Enable/disable ordinary and shared gates, validate CGR bitfield values, run unused-clock cleanup, and test concurrent operations.
