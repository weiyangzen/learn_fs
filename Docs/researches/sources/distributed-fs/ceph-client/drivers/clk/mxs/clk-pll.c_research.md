# sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-pll.c

Purpose: Implements the MXS PLL clock primitive as a fixed-rate CCF clock with prepare/unprepare power control and enable/disable output gating.

Important APIs, types, and functions: `struct clk_pll` stores `clk_hw`, base address, power bit, and fixed rate. `mxs_clk_pll()` registers a PLL with `clk_pll_ops`. The ops set and clear the power bit at `base + SET/CLR`, clear or set bit 31 for output gating, and return the fixed `rate` in `clk_pll_recalc_rate()`.

Control flow: SoC files create PLLs by passing the PLL control base, power bit, and known rate. CCF prepare powers up the PLL and waits 10 microseconds. Enable clears the gate bit; disable sets it.

State and persistence: The allocated PLL object persists after registration. PLL power/gate state is hardware-backed. The rate is fixed in memory rather than recalculated from programmable fields.

Dependencies and integration points: Used by i.MX23 and i.MX28 clock trees. Depends on MXS SET/CLR register semantics and CCF prepare/enable separation.

Risks: There is no lock-status polling, only a fixed delay on prepare. If the hardware requires longer lock time or has board-specific PLL rates, consumers can see incorrect readiness or rates. Bit 31 is assumed to be the gate for every MXS PLL instance.

Test signals: Prepare/enable sequencing should set the power bit, clear bit 31, and produce the configured fixed rate in `clk_summary`. Suspend/resume or disable tests should verify unprepare clears the power bit and disable gates the output.
