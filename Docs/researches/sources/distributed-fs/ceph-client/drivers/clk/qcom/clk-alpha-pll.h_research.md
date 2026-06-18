# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-alpha-pll.h

## Purpose
Defines the internal Qualcomm alpha PLL contract shared by SoC clock controller drivers and `clk-alpha-pll.c`. It enumerates supported PLL register layouts, register offset slots, data structures for PLLs, post-dividers, VCOs, and configuration values, plus exported operation tables and configuration functions.

## Important APIs, Types, And Functions
Important declarations include `clk_alpha_pll_regs`, `struct pll_vco`, `VCO()`, `struct clk_alpha_pll`, `struct clk_alpha_pll_postdiv`, and `struct alpha_pll_config`. Feature flags include `SUPPORTS_OFFLINE_REQ`, `SUPPORTS_FSM_MODE`, `SUPPORTS_DYNAMIC_UPDATE`, and `SUPPORTS_FSM_LEGACY_MODE`. The header exports many `clk_ops` variants and aliases compatible families with macros, such as Lucid using Trion fixed ops, Taycan using Lucid Evo ops, and Pongo/Rivian family aliases.

## Control Flow
SoC drivers instantiate `struct clk_alpha_pll`, choose a `regs` table entry, optional VCO table, feature flags, CCF init data, and optional `alpha_pll_config`. They either call a family-specific configure function directly or call `qcom_clk_alpha_pll_configure()` to dispatch based on the selected register table. CCF then enters the exported ops for enable, disable, recalc, determine, post-divide, and rate changes.

## State And Persistence
The header describes software metadata rather than runtime storage. Persistent fields in descriptors determine which hardware registers are touched, how VCO validation is applied, and whether updates can happen under FSM or dynamic-update rules. Configuration structs persist as static SoC data and are treated as the source of boot-time PLL programming.

## Dependencies And Integration Points
Includes CCF provider APIs and `clk-regmap.h`. It is consumed by Qualcomm clock controller files across the tree, including `clk-cpu-8996.c`, `clk-cbf-8996.c`, and multiple generated CC drivers. Its declarations are tightly coupled to `clk-alpha-pll.c` and the common regmap clock wrapper.

## Risks And Edge Cases
Register layout selection is critical because offsets are family-specific but accessed through common macros. Alias macros simplify family reuse but can hide behavioral differences if a new PLL variant diverges. Callers must provide consistent `width`, `post_div_shift`, VCO ranges, and config masks or rate and enable operations will program invalid fields.

## Test Signals
Compile coverage from multiple SoC drivers, successful registration of all ops aliases, static descriptor sanity checks for register tables, and runtime smoke tests for each configured PLL family are useful signals.
