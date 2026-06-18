# sources/distributed-fs/ceph-client/include/linux/clk/ti.h

Purpose: This header is the TI OMAP clock-driver support contract. It describes OMAP register references, DPLL data, OMAP-specific `clk_hw` state, low-level register/clockdomain operations, init hooks, feature flags, and context save/restore helpers.

Important APIs/types/functions: Main structures are `struct clk_omap_reg`, `struct dpll_data`, `struct clk_hw_omap_ops`, `struct clk_hw_omap`, `struct ti_clk_ll_ops`, and `struct ti_clk_features`. Flags include `ENABLE_REG_32BIT`, `CLOCK_IDLE_CONTROL`, `CLOCK_NO_IDLE_PARENT`, `ENABLE_ON_INIT`, `INVERT_ENABLE`, `CLOCK_CLKOUTX2`, DPLL mode constants, `DPLL_J_TYPE`, and feature bits such as `TI_CLK_DPLL_HAS_FREQSEL`, `TI_CLK_DPLL4_DENY_REPROGRAM`, `TI_CLK_DISABLE_CLKDM_CONTROL`, `TI_CLK_ERRATA_I810`, `TI_CLK_CLKCTRL_COMPAT`, and `TI_CLK_DEVICE_TYPE_GP`. APIs include autoidle controls, DPLL recalc/reprogram helpers, clockdomain setup, low-level ops setup, DT/legacy provider init for many OMAP/AM/DRA SoCs, feature setup/getters, standby checks, and DPLL context save/restore.

Control flow: TI clock init registers low-level ops, maps PRCM/CM regions, initializes DT or legacy providers, and exposes OMAP-specific hardware clocks through CCF. Clock operations use `clk_hw_omap` state and low-level ops for MMIO/regmap access and clockdomain coordination. DPLL helpers cache rounded parameters and reprogram PLL registers. Context save/restore functions preserve DPLL state across low-power transitions.

State and persistence behavior: The structures include persistent runtime state such as fixed rates, enable registers, DPLL rounded-rate caches, clockdomain pointers, autoidle counts, context fields, and global feature flags. Hardware state lives in PRCM/CM/DPLL registers.

Dependencies and integration points: It includes `<linux/clk-provider.h>` and `<linux/clkdev.h>`, and integrates with OMAP clockdomain code, DT clock providers, legacy board files, DPLL implementations, PM context handling, and CCF helpers.

Risks: Several `dpll_data` fields are runtime caches mixed with fixed data, and comments warn they should ideally be separated. Incorrect low-level ops or register indices can corrupt PRCM state. Autoidle and clockdomain control mistakes can cause hangs or power regressions. Legacy init stubs return `-ENXIO`, so callers must handle unavailable SoC support.

Test signals: OMAP/AM/DRA boot tests, DPLL rate-change and lock tests, clockdomain idle/active transitions, suspend/resume DPLL context validation, DT and legacy provider compile paths, and clock tree/rate inspection are primary signals.
