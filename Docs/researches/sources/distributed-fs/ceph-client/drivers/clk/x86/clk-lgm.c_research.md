<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-lgm.c -->
# sources/distributed-fs/ceph-client/drivers/clk/x86/clk-lgm.c

## Purpose

`clk-lgm.c` is the LGM CGU platform inventory. It defines PLLs, divider tables, parent relationships, branch clocks, hardware/software gates, dual dividers, and the platform-driver probe for `intel,cgu-lgm`.

## Important APIs, Types, And Functions

The file defines register offsets, gate bit shifts, `pll_div[]` and `dcl_div[]`, parent-data arrays, `lgm_pll_clks[]`, `lgm_branch_clks[]`, and `lgm_ddiv_clks[]`. `lgm_cgu_probe()` allocates a provider, gets the syscon regmap, registers PLLs, branches, dual dividers, and adds a onecell OF provider.

## Control Flow

On platform probe, clocks are registered in dependency order: PLLs first, standard branches next, and dual-divider clocks last. The branch list covers CPU, DDR, NOC, PP, storage, PCM, CBPHY, and many peripheral gates. Critical interconnect clocks such as NGI and NOC4 are marked ignore-unused/critical.

## State And Persistence Behavior

State persists in CGU registers. Software mux CBPHY entries use `MUX_CLK_SW` and do not touch hardware. Provider state is devm-managed and sized to `LGM_GCLK_USB2 + 1`.

## Dependencies And Integration Points

It depends on DT binding IDs from `intel,lgm-clk.h`, syscon regmap, LGM common CGU helpers, and OF onecell provider semantics.

## Risks And Test Signals

Risks include dense gate-shift tables, `CGU_GATE3` sharing the same offset as `CGU_GATE1` in the source, NULL slots for non-hardware gates, and parent-name binding sensitivity. Test every binding ID lookup, critical-clock persistence, storage/PCIe/USB/Ethernet peripheral bring-up, and `clk_summary` rate trees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/clk-lgm.c -->
