# sources/distributed-fs/ceph-client/drivers/clk/nxp/clk-lpc18xx-ccu.c

Purpose: Implements the LPC18xx/LPC43xx Clock Control Unit branch clocks. It registers gates and optional read-only divide-by-two stages for branch clocks sourced from CGU base clocks.

Important APIs, types, and functions: `struct lpc18xx_clk_branch` describes each branch base parent, output name, register offset, flags, stored clk, and gate. `lpc18xx_ccu_branch_clk_get()` resolves OF clock specifier offset to a registered branch clock. `lpc18xx_ccu_gate_endisable()` implements hardware-specific enable/disable. `lpc18xx_ccu_register_branch_gate_div()` creates composite clocks.

Control flow: `lpc18xx_ccu_init()` maps the CCU, reads the node's `clock-names`, registers branch clocks for each named base clock, and adds a custom OF provider. For bus branches, registration updates the parent name so later branches in that group use the bus branch as parent. Essential CPU/SDRAM-related branches are prepared and enabled immediately.

State and persistence: Branch descriptors are static and store returned `struct clk *` pointers. Gate/divider state persists in CCU MMIO registers. Allocated divider objects persist after registration.

Dependencies and integration points: Depends on CGU base clock names such as `base_cpu_clk`, DT binding offsets from `lpc18xx-ccu.h`, and CCF composite clocks.

Risks: Branch registers hang if read while the base parent clock is disabled, so `is_enabled()` carefully checks parent state first. Disable requires a two-write AUTO then clear-RUN sequence; changing it can destabilize hardware. The provider returns clocks only if both offset and base-name membership match the DT `clock-names` list.

Test signals: Boot should register all branch clocks listed in DT `clock-names`. Read `clk_summary` without hangs when base clocks are disabled. Verify essential branches `CLK_CPU_EMC`, `CLK_CPU_CORE`, `CLK_CPU_CREG`, and `CLK_CPU_EMCDIV` are enabled.
