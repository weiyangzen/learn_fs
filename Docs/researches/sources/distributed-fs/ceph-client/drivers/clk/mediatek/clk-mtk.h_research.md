# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mtk.h

Purpose: `clk-mtk.h` is the public local interface for MediaTek clock-controller data tables and common registration helpers. SoC clock drivers include it to describe fixed clocks, fixed factors, composite mux/div/gate clocks, simple dividers, reset descriptors, shared locks, runtime PM needs, and common probe/remove hooks.

Important APIs and types: it defines `struct mtk_fixed_clk`, `struct mtk_fixed_factor`, `struct mtk_composite`, `struct mtk_clk_divider`, and `struct mtk_clk_desc`. It declares the registration/unregistration APIs implemented in `clk-mtk.c`, plus `mtk_clk_get_hwv_regmap()`. Macros such as `FIXED_CLK`, `FACTOR`, `FACTOR_FLAGS`, `MUX_GATE`, `MUX_GATE_FLAGS`, `MUX`, `MUX_FLAGS`, `DIV_GATE`, `MUX_DIV_GATE`, and `DIV_ADJ` generate static table entries. `GATE_DUMMY`, `CLK_DUMMY`, `cg_regs_dummy`, and `mtk_clk_dummy_ops` support binding compatibility where hardware clock IDs do not start at zero.

Control flow: this header has no executable control flow. It shapes the control flow consumed by `clk-mtk.c`: `struct mtk_clk_desc` tells the simple probe which arrays to register, how many entries each array contains, whether MMIO is shared, whether runtime PM is needed, whether a reset controller is present, and whether a notifier must be installed for an MFG mux.

State and persistence: the header defines static descriptor state that SoC drivers compile into their modules. Runtime state lives in the common clock framework, the onecell clock array, and reset-controller structures allocated by the implementation.

Dependencies and integration points: it includes Linux clock-provider, IO, spinlock, and type headers, plus MediaTek `reset.h`. It is consumed by MediaTek SoC-specific drivers and by the local mux/gate/reset implementations. `struct mtk_clk_desc::rst_desc` integrates clock-controller probing with MediaTek reset controller registration.

Risks: most macros rely on positional initializer correctness; swapped register, shift, or width parameters produce valid C but wrong hardware behavior. `signed char` fields use `-1` as sentinel for absent mux/divider/gate parts, so table authors must avoid unsigned conversion mistakes. Count fields in `mtk_clk_desc` must match array lengths and ID ranges to avoid missing clocks or out-of-bounds onecell indexing.

Test signals: compile coverage across MediaTek SoC drivers catches initializer drift. Runtime signals include full `clk_summary` names, correct parent lists, expected rate propagation flags, reset controller registration when `rst_desc` is present, and absence of duplicate ID warnings during probe.
