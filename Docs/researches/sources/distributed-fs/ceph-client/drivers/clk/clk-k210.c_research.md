# sources/distributed-fs/ceph-client/drivers/clk/clk-k210.c

Purpose: Canaan Kendryte K210 SoC clock controller driver. It registers PLL0/1/2, ACLK, and all SoC gate/divider/mux clocks from sysctl registers, plus an early helper to enable PLL1 for AI SRAM.

Important APIs, types, and functions: `k210_clk_cfg` describes per-clock gate/divider/mux fields. `k210_pll` and `k210_sysclk` hold PLL and controller state. `k210_pll_ops` and `k210_pll2_ops` implement PLL enable/disable/recalc and PLL2 parent selection. `k210_aclk_ops` manages CPU/ACLK parent and divider. `k210_clk_ops` and `k210_clk_mux_ops` implement child gates, dividers, and muxes. `k210_clk_init()` is the `CLK_OF_DECLARE` entry.

Control flow: init allocates `k210_sysclk`, maps parent sysctl registers, registers PLLs, registers ACLK, then registers critical CPU/SRAM/AI clocks and all peripheral clocks by parent group. A final loop verifies every `K210_NUM_CLKS` entry registered before publishing the onecell provider. PLL enable may reparent ACLK to the input oscillator before changing PLL0, programs PLL factors, pulses reset with reference-SDK NOPs, waits for lock, enables PLL output, then restores ACLK to PLL0.

State and persistence: state is sysctl MMIO plus in-memory clock descriptors. A global spinlock serializes PLL, mux, and gate register updates. Critical flags keep CPU/SRAM/AI clocks from being disabled.

Dependencies and integration points: depends on K210 sysctl register definitions, DT clock IDs, OF early clock registration, common clock framework, MMIO, and spinlocks.

Risks and test signals: PLL lock wait has no timeout. `k210_aclk_set_selector()` clears with `reg &= K210_ACLK_SEL`, which appears to preserve only the selector bit rather than clearing it while preserving other fields. Registration aborts silently if any clock ID remains unset. Test signals are boot-time CPU rate log, provider lookups for all IDs, PLL1 early init, critical clock retention, and mux/divider register behavior.
