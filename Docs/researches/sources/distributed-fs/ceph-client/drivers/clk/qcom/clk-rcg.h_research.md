# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-rcg.h

## Purpose
Defines frequency-table and descriptor types for Qualcomm root clock generators, both legacy RCGs and second-generation CMD_RCGR-based RCG2 clocks.

## Important APIs, Types, And Functions
Macros `F()`, `C()`, `FM()`, and `FMS()` create frequency table entries. Types include `struct freq_tbl`, `struct freq_conf`, `struct freq_multi_tbl`, `struct mn`, `struct pre_div`, `struct src_sel`, `struct clk_rcg`, `struct clk_dyn_rcg`, `struct clk_rcg2`, `struct clk_rcg2_gfx3d`, and `struct clk_rcg_dfs_data`. The header declares exported ops for legacy RCGs, dynamic RCGs, RCG2 variants, display/byte/GPU/shared clocks, DP clocks, and `qcom_cc_register_rcg_dfs()`.

## Control Flow
SoC drivers define parent maps and frequency tables, embed one of the RCG descriptor structs, and register clocks with the matching ops. For DFS RCGs, drivers use `DEFINE_RCG_DFS()` entries and call `qcom_cc_register_rcg_dfs()` before registration so RCG2 DFS ops can replace normal ops when hardware DFS is enabled.

## State And Persistence
The header exposes descriptor state that maps software clock parents and rates to hardware register fields. Runtime persistence includes `clk_rcg2.parked_cfg` for shared RCGs and possibly allocated DFS frequency tables in the implementation.

## Dependencies And Integration Points
Includes CCF and `clk-regmap.h`. It integrates with `common.h` parent maps and frequency helpers, plus many Qualcomm SoC clock controllers.

## Risks And Edge Cases
Frequency table macros encode half-integer dividers as `(2 * h) - 1`; misuse creates wrong rates. Parent maps must match hardware source values. Shared RCGs depend on `safe_src_index` and `parked_cfg` semantics. DFS initialization mutates `clk_init_data` ops and flags.

## Test Signals
Compile coverage across SoC clock tables, table-driven rate selection, shared parked RCG behavior, and DFS registration are the main signals.
