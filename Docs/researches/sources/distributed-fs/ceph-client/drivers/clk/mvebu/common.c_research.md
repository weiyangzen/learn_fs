# sources/distributed-fs/ceph-client/drivers/clk/mvebu/common.c

Purpose: shared MVEBU clock infrastructure for SAR-derived core clocks, spread-spectrum correction, and common clock-gating controllers.

Important APIs/functions: `kirkwood_fix_sscg_deviation`, `mvebu_coreclk_setup`, and `mvebu_clk_gating_setup`. Internal gating helpers include `clk_gating_get_src` and syscore suspend/resume callbacks.

Control flow: core setup maps SAR registers, allocates a onecell table for TCLK, CPU clock, ratio clocks, and optional refclk, registers fixed-rate/fixed-factor clocks, unmaps SAR, and publishes provider. Gating setup maps the gate register, determines default parent from input clock, registers gates from a descriptor array, adds a custom provider that indexes by gate bit, and registers syscore save/restore.

State and persistence: core clock data is static onecell storage; gating control is a single global `ctrl` with saved register state for suspend. Gates are hardware-backed.

Dependencies and integration: OF, CCF, syscore ops, MMIO, and SoC descriptors from `common.h`.

Risks: only one gating controller can instantiate because `ctrl` is global. Several allocations are permanent early-init allocations. SSCG helper logs errors if the optional `sscg` node is missing and returns unadjusted clocks.

Test signals: core provider clock counts, gating provider bit-index lookup, suspend/resume restore of gate register, and SSCG-corrected CPU rate validation.
