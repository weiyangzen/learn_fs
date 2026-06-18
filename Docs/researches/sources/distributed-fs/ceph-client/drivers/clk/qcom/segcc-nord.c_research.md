# sources/distributed-fs/ceph-client/drivers/clk/qcom/segcc-nord.c

## Purpose
This driver registers the NORD SEGCC controller, covering south/east general clocks for dual Ethernet MACs and QUPv3 serial engine wrappers. It provides PLLs, RCGs, branches, DFS-capable serial clocks, GDSCs, and reset lines.

## Important APIs, types, and functions
- `se_gcc_gpll0`, `se_gcc_gpll2`, `se_gcc_gpll4`, `se_gcc_gpll5`, and `se_gcc_gpll0_out_even` define GPLL sources and a postdivider.
- Parent maps/data describe XO, sleep, GPLL, EMAC/SGMII/RGMII/XGXS, and QUP parent choices.
- Frequency tables configure EMAC EEE/PTP/RGMII/PHY AUX, GP clocks, and QUPv3 S0-S6 serial sources.
- `clk_branch` descriptors expose EMAC AXI/PHY/PTP/RGMII/RPCS/XGXS and QUP wrapper AHB/core/serial clocks.
- `se_gcc_emac0_gdsc` and `se_gcc_emac1_gdsc` power-gate the two Ethernet MAC domains with polling and retention flags.
- `se_gcc_nord_dfs_clocks[]` registers DFS support for all QUPv3 wrap0/wrap1 S0-S6 RCGs.
- `se_gcc_nord_desc` wires clocks, resets, GDSCs, and driver data into `qcom_cc_probe()`.

## Control flow
The platform driver matches `"qcom,nord-segcc"` and invokes `se_gcc_nord_probe()`. The qcom common clock probe maps the MMIO range, registers clocks by binding ID, registers EMAC GDSCs and reset controls, and enables DFS metadata for QUP RCGs. After probe, serial and Ethernet consumers control clock rates and branch enables through CCF and genpd/reset APIs.

## State and persistence behavior
SEGCC hardware registers persist PLL, RCG, divider, branch, reset, DFS, and GDSC power state. The driver stores only static descriptors. GDSCs use `PWRSTS_OFF_ON`, `POLL_CFG_GDSCR`, and `RETAIN_FF_ENABLE`, so power-domain transitions are hardware-visible and retain selected flip-flop state.

## Dependencies and integration points
The file depends on qcom CCF helpers for alpha PLLs, PLLs, branches, RCGs, dividers, GDSCs, DFS, resets, regmap, and `dt-bindings/clock/qcom,nord-segcc.h`. It integrates with Ethernet MAC drivers, QUPv3 serial controllers, and reset/power-domain consumers through device-tree clock, reset, and power-domain references.

## Risks
This descriptor-heavy file has high binding-index and register-offset risk. QUP DFS lists must stay aligned with RCG definitions; missing an RCG would prevent dynamic frequency scaling. Ethernet clock parent/frequency tables must match PHY mode expectations or link timing may fail. GDSC wait values and retention flags are hardware-sensitive.

## Test signals
Boot should register SEGCC and show all EMAC/QUP/GP clocks in `clk_summary`. Ethernet link tests should cover both MACs and PTP/RGMII/SGMII paths. Serial tests should exercise QUP instances and rate changes across supported frequencies. Power-domain tests should toggle EMAC GDSCs, and reset tests should assert/deassert EMAC and QUP wrapper resets.
