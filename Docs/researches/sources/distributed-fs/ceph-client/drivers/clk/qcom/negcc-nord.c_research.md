# sources/distributed-fs/ceph-client/drivers/clk/qcom/negcc-nord.c

## Purpose
`negcc-nord.c` implements the Qualcomm NORD NE_GCC clock controller. It provides clocks, resets, DFS metadata, and GDSC power domains for a peripheral-oriented clock block covering UFS PHY, primary and secondary USB/USB3 paths, QUPv3 wrapper 2 serial engines, SDCC4, a secondary GPU-related clock group, and general-purpose clocks. Clock and reset IDs are sourced from `dt-bindings/clock/qcom,nord-negcc.h`.

## Important APIs, Types, And Functions
The driver uses the Qualcomm common clock framework data structures: `clk_alpha_pll` and `clk_alpha_pll_postdiv` for Lucid OLE PLLs, `clk_rcg2` for root clock generators, `clk_branch` for gates and halt checks, `clk_regmap_div` for post-dividers, `clk_regmap_mux` and `clk_regmap_phy_mux` for PHY pipe/symbol source selection, `gdsc` for power domains, `qcom_reset_map` for block resets, `clk_rcg_dfs_data` for dynamic frequency scaling RCGs, `qcom_cc_driver_data` for probe-time extras, and `qcom_cc_desc` for final registration.

The functional entry points are small. `clk_nord_regs_configure()` sets `FORCE_MEM_CORE_ON` for the UFS ICE core and UFS AXI branches with `qcom_branch_set_force_mem_core()`. `ne_gcc_nord_probe()` calls `qcom_cc_probe()` with `ne_gcc_nord_desc`. The match table binds `qcom,nord-negcc`, and `module_platform_driver()` installs the platform driver.

## Clock Model And Control Flow
The provider starts with Lucid OLE PLLs `ne_gcc_gpll0`, its even post-divider `ne_gcc_gpll0_out_even`, and `ne_gcc_gpll2`, all ultimately sourced from DT parent index `DT_BI_TCXO`. Parent maps combine TCXO, GPLL0 main/even, GPLL2, sleep clock, UFS RX/TX symbol parents, and USB3 PHY pipe clocks. PHY symbol and pipe inputs are represented through dedicated regmap mux helpers so UFS and USB PHY wrappers can provide recovered or pipe clocks to the controller.

RCGs define programmable rates for `gp1`, `gp2`, QUPv3 wrapper 2 serial engines `s0` through `s6`, SDCC4 applications, UFS PHY AXI/ICE/aux/unipro, USB20 master/mock UTMI, USB31 primary and secondary master/mock UTMI, and USB3 primary/secondary PHY aux clocks. Branch gates expose the usable clocks for aggregate NoC paths, CNOC USB paths, GPU secondary paths, QUP wrapper core and serial lines, SDCC4, UFS PHY subclocks, USB sleep/master/mock/pipe/aux/com-aux paths, and frequency measurement.

Probe-time control flow is declarative: `qcom_cc_probe()` maps registers, registers clocks/resets/GDSCs, applies driver data, and installs DFS support for the listed QUP RCGs. The custom register callback is part of `qcom_cc_driver_data`, so UFS force-memory settings are applied during common registration rather than in a hand-written probe sequence.

## State And Persistence Behavior
Persistent state lives in the NE_GCC hardware registers up to `0xf41f0`, with 32-bit values and 4-byte stride. PLL enable bits use shared registers, RCGs persist their command/source/divider fields, branch clocks persist enable bits and memory-core override settings, reset lines persist only while asserted, and GDSCs persist power-domain state for UFS and USB islands. The driver has no local dynamic allocation or remove path; the common framework owns provider state after probe.

DFS metadata for QUPv3 serial clocks is static state used by the clock framework to coordinate runtime rate transitions. `clk_nord_regs_configure()` intentionally changes branch memory-retention behavior for UFS ICE/AXI, so storage stability depends on this setup being applied before UFS consumers aggressively gate or power-manage those clocks.

## Dependencies And Integration Points
The driver depends on DT parent ordering, `qcom,nord-negcc` bindings, Linux CCF, regmap, Qualcomm PLL/RCG/branch/divider/mux/PHY-mux helpers, reset support, and GDSC power domains. External parent clocks include TCXO, sleep, UFS PHY symbol clocks, and primary/secondary USB3 pipe clocks. Consumers include UFS host/PHY and ICE, USB2/USB3 controllers and PHYs, QUPv3 serial controllers, SDCC4/eMMC or SD card paths, GPU-related NoC/SMMU voting clocks, and reset-controller users for USB/UFS/QUP/SDCC blocks.

GDSC integration exposes seven domains: UFS memory PHY, UFS PHY, USB20 primary, USB31 primary, USB31 secondary, USB3 PHY, and USB3 secondary PHY. Reset integration covers GPU secondary, QUP wrapper 2, SDCC4, UFS PHY, USB20/USB31 blocks, USB3 DP PHY blocks, USB3 PHY blocks, and USB3PHY PHY sub-blocks.

## Risks And Edge Cases
The highest risk is mismatched DT parent order because many parent references use `.index` rather than names. A binding/order mismatch would route serial, UFS, or USB clocks to the wrong source. PHY muxes for UFS symbol and USB pipe clocks are also sensitive to hardware readiness; consumers may see bad rates or enable failures if PHY drivers are not registered or if parent clock flags are wrong.

UFS has a targeted force-memory-core workaround. Removing or moving it could introduce data-path instability during low-power transitions. QUP DFS tables must stay aligned with serial-engine expectations; incomplete DFS coverage can cause rate switches to fail for some UART/SPI/I2C instances. Because the driver is mostly generated-style tables, small offset or bit mistakes in branch/reset/GDSC data can have broad runtime effects.

## Test Signals
Probe should register the `qcom,nord-negcc` provider without missing parent errors and show PLLs, RCGs, branches, and GDSCs in debugfs. UFS tests should cover link startup, high-speed modes, ICE activity, suspend/resume, and runtime PM. USB tests should cover primary and secondary USB3 pipe clocks, USB2 UTMI mock clocks, connect/disconnect, and suspend/resume. QUP tests should change rates on all seven wrapper 2 serial engines. Reset signals can be validated through peripheral reinitialization after reset-controller assertions, and GDSC signals through power-domain on/off transitions while clocks are enabled.
