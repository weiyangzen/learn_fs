# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sdx75.c

## Purpose

`gcc-sdx75.c` is the Qualcomm Global Clock Controller driver for the SDX75 modem platform. It exports SDX75 GCC clocks, resets, and GDSC power domains to Linux using IDs from `dt-bindings/clock/qcom,sdx75-gcc.h`. Compared with SDX65, this driver describes a larger clock topology: multiple GPLLs, dual EMAC/SGMII domains, three PCIe domains, QUPv3 serial engines with DFS support, SDCC1/SDCC2, USB3, PDM, and related reference clocks.

The implementation remains mostly data-driven. Shared Qualcomm clock operations perform PLL, RCG, mux, divider, branch, reset, and power-domain mechanics from the register metadata encoded here.

## Important APIs, Types, And Functions

- The local `DT_*` enum defines external parent indices in the GCC node's `clocks` list, including TCXO, sleep clock, EMAC SGMII clocks, PCIe pipe clocks, PCIe20 PHY aux, and USB3 PHY pipe.
- The local `P_*` enum defines hardware parent selector names used in `parent_map` arrays.
- `gpll0`, `gpll4`, `gpll5`, `gpll6`, and `gpll8` are Lucid OLE alpha PLLs enabled through `0x7d000` vote bits. `gpll0_out_even` provides the divide-by-2 GPLL0 output.
- Numerous `parent_map`/`clk_parent_data` pairs map RCG selector values to either indexed DT parents or internal GPLL hardware clocks.
- `struct clk_regmap_mux` and `struct clk_regmap_phy_mux` model EMAC SGMII RX/TX muxes and PCIe/USB pipe sources. PCIe pipe clocks use `clk_regmap_phy_mux_ops`, while SGMII and USB pipe paths use regmap mux operations.
- `struct clk_rcg2` entries define EMAC EEE/PTP/RGMII/PHY aux clocks, GP clocks, PCIe aux/rchng clocks, PDM2, QUPv3 serial sources S0-S8, SDCC1/SDCC2, USB30 master/mock UTMI, and USB3 PHY aux. Most use `clk_rcg2_shared_ops`; SDCC sources use shared floor ops to avoid overclocking storage buses.
- `struct clk_regmap_div` exposes read-only pipe div2 and USB mock UTMI postdividers.
- `struct clk_branch` entries are the exported gates and votes. SDX75 heavily uses `BRANCH_HALT_VOTED` for shared infrastructure, `BRANCH_HALT_DELAY` for PHY/pipe and SGMII paths, and `BRANCH_HALT_ENABLE` for reference-clock enable bits.
- Ten `struct gdsc` instances cover EMAC0/1, PCIe root/PHY domains for three PCIe blocks, USB30, and USB3 PHY. They include wait values and `RETAIN_FF_ENABLE`.
- `gcc_dfs_clocks[]` registers QUPv3 RCGs for dynamic frequency switching via `qcom_cc_register_rcg_dfs()`.
- `gcc_sdx75_probe()` maps registers, registers DFS data, enables two always-on PCIe link clocks, then registers the GCC descriptor.

## Control Flow

`subsys_initcall(gcc_sdx75_init)` registers the platform driver. OF matching uses `compatible = "qcom,sdx75-gcc"`. Probe proceeds in a short sequence:

1. `qcom_cc_map()` maps the regmap using a 32-bit, 4-byte-stride config with `max_register = 0x1f41f0`.
2. `qcom_cc_register_rcg_dfs()` registers QUPv3 S0-S8 RCGs for DFS. Probe aborts if this fails.
3. `qcom_branch_set_clk_en()` enables `0x3e004` and `0x3e008`, identified as `GCC_AHB_PCIE_LINK_CLK` and `GCC_XO_PCIE_LINK_CLK`.
4. `qcom_cc_really_probe()` registers the clock, reset, and GDSC arrays with the frameworks.

Runtime control is delegated to the common clock framework. Consumers request clock handles by binding ID, set rates through the RCG tables, vote or gate branches, assert resets through `qcom_reset_map`, and control GDSCs through genpd.

## State And Persistence Behavior

The file has no private mutable driver state beyond framework-registered objects. Hardware register values hold persistent state for PLL votes, RCG parent/rate programming, branch enables, GDSC power state, and resets.

Probe performs persistent writes for DFS registration and two always-on PCIe link clocks. It does not configure GPLL rates in probe; the fixed PLL definitions rely on firmware or shared PLL operations. QUPv3 DFS metadata persists as framework state, while actual frequency choices remain in hardware registers and are changed by consumers through CCF.

## Dependencies And Integration Points

- Linux CCF and Qualcomm clock helpers, including alpha PLL, branch, RCG, regmap divider, regmap mux, and regmap PHY mux support.
- `clk-regmap-phy-mux.h` is important for PCIe pipe clock switching because pipe clocks are PHY-provided and synchronized with PHY state.
- Device-tree binding order is critical because parents use `.index = DT_*`.
- Reset framework receives `gcc_sdx75_resets[]`, including EMAC, eMMC, PCIe root/PHY/link-down/NOCSR, QUSB2PHY, TCSR PCIe, USB30, USB3 PHY, and USB PHY CFG resets.
- GDSC/genpd integration exposes EMAC, PCIe, and USB power domains.
- Platform lifecycle uses `subsys_initcall()` and `module_exit()`.

## Subsystems Covered

SDX75 covers dual EMAC blocks with AXI/AHB, EEE, PTP, RGMII, SGMII MAC/RPCS/XGXS RX/TX clocks and reference enables; three PCIe clock domains with aux, config AHB, master/slave AXI, Q2A, pipe, pipe-div2, rchng, sleep, and clkref clocks; QUPv3 wrapper 0 core and nine serial source/gate pairs; SDCC1/eMMC and SDCC2; USB30 and USB3 PHY clocks; GP1-3; PDM; boot ROM AHB; USB2/USB3 reference enables; and the corresponding GDSCs and resets.

## Risks And Edge Cases

- Indexed external parents must match the binding and DTS clock order. EMAC SGMII RX/TX and PCIe pipe parents are easy to misorder because many names are similar.
- Shared RCG ops and DFS registration for QUPv3 are coupled. Adding or removing QUP sources without updating `gcc_dfs_clocks[]` can break serial-engine DFS behavior.
- SDCC clocks use floor rounding. Converting them to non-floor ops can overclock eMMC/SD paths.
- PHY pipe and SGMII clocks use delayed halt checks. Strict halt polling can fail when PHYs or MACs own status timing.
- GDSC wait values and `RETAIN_FF_ENABLE` are part of power sequencing. Incorrect changes may cause PCIe, EMAC, or USB retention/power-collapse failures.
- Probe-time always-on PCIe link clocks are not normal consumer-managed branches; removing them can affect early PCIe/link infrastructure.
- Reset coverage is dense and spans multiple PCIe instances. Instance-number mixups are a realistic maintenance risk.

## Test Signals

- Build with the SDX75 GCC config enabled and confirm all binding IDs resolve.
- Boot with `qcom,sdx75-gcc` and verify GCC probes before EMAC, PCIe, QUPv3, SDCC, and USB consumers finish probing.
- Check `clk_summary` for GPLLs, `gcc_emac0_*`, `gcc_emac1_*`, `gcc_pcie_*`, `gcc_pcie_1_*`, `gcc_pcie_2_*`, QUPv3 S0-S8 clocks, SDCC clocks, and USB3 pipe/aux clocks.
- Exercise EMAC0/1 link modes, PCIe link training on all described instances, QUP UART/SPI/I2C transfers, eMMC/SD, and USB3.
- Validate GDSC on/off sequencing through runtime PM for EMAC, PCIe, and USB.
- Test reset controls for EMAC, PCIe root/PHY/link-down paths, QUSB2PHY, USB30, USB3 PHY, and eMMC.
