# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-gate.c

Purpose: provides an MMP-specific CCF gate for registers where enable and disable values are multi-bit patterns rather than a single bit.

Important APIs/functions: `mmp_clk_gate_ops` supplies `enable`, `disable`, and `is_enabled`. `mmp_clk_register_gate` allocates `struct mmp_clk_gate` and registers it with the common clock framework.

Control flow: enable and disable read the target register, clear the configured mask, OR in `val_enable` or `val_disable`, and write back under an optional spinlock. When `MMP_CLK_GATE_NEED_DELAY` is set, enable waits about two clock cycles based on `clk_hw_get_rate`.

State and persistence: no software state beyond the allocated gate metadata; enable state is the masked MMIO value. Persistence across suspend is handled by SoC-level code if required.

Dependencies and integration: used by the MMP registration helpers and SoC tables for APBC/APMU gates. Depends on CCF, MMIO, delays, and locks supplied in table entries.

Risks: if the clock rate is zero, the delay calculation can divide by zero. Incorrect masks or enable values can overwrite adjacent control bits. `is_enabled` requires exact equality with `val_enable`, so partially enabled hardware encodings are treated as off.

Test signals: per-clock enable/disable smoke tests, `clk_summary` gate status, boot testing peripherals with reset-sensitive APBC clocks, and static review of mask/value pairs.
