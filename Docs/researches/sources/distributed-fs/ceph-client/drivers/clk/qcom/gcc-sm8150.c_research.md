# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm8150.c

## Purpose
`gcc-sm8150.c` is the Qualcomm global clock controller provider for SM8150-class SoCs. It describes the GCC MMIO block as Linux common clock framework objects and exposes clock, reset, and GDSC power-domain IDs from `dt-bindings/clock/qcom,gcc-sm8150.h`. The topology covers fixed GPLL parents, EMAC, GP test clocks, PCIe, PDM, QSPI, QUPv3 serial engines, SDCC, TSIF, UFS card and UFS PHY instances, primary and secondary USB3, camera/display/video fabric votes, GPU/NPU support clocks, and a set of block resets.

## Important APIs, Types, And Functions
The file is almost entirely static descriptor data consumed by the Qualcomm clock-controller framework. It uses `struct clk_alpha_pll` for GPLL0, GPLL7, and GPLL9 with TRION PLL register layouts, `struct clk_alpha_pll_postdiv` for `gpll0_out_even`, `struct clk_rcg2` plus `struct freq_tbl` for programmable roots, `struct clk_branch` for gates and votes, `struct gdsc` for power domains, `struct qcom_reset_map` for resets, `struct clk_rcg_dfs_data` for QUP dynamic frequency switching, `struct regmap_config`, and `struct qcom_cc_desc`.

Parent selection is encoded through the local enum and `parent_map` arrays. Firmware-provided parents are `bi_tcxo`, `sleep_clk`, and `aud_ref_clk`; in-file parents are `gpll0`, `gpll0_out_even`, `gpll7`, and `gpll9`. RCG roots include EMAC PTP/RGMII, GP1-3, PCIe AUX and refgen, PDM2, QSPI, all QUPv3 serial lanes, SDCC2/4, TSIF, UFS card/PHY AXI/ICE/AUX/UniPro, and USB3 master/mock UTMI/PHY AUX clocks. The provider arrays `gcc_sm8150_clocks[]`, `gcc_sm8150_resets[]`, and `gcc_sm8150_gdscs[]` are gathered into `gcc_sm8150_desc`.

`gcc_sm8150_probe()` is the only custom function. It maps the MMIO region with `qcom_cc_map()`, updates two MISC registers to disable GPLL0 active input to NPU and GPU, registers DFS support with `qcom_cc_register_rcg_dfs()`, and then calls `qcom_cc_really_probe()` to publish the clocks, resets, and GDSCs.

## Control Flow
The platform driver matches `qcom,gcc-sm8150` and is registered from `subsys_initcall()`, so the GCC provider is available early for dependent platform devices. Probe first obtains a regmap for the described register space. It then writes `0x3` under mask `0x3` to offsets `0x4d110` and `0x71028`, changing NPU and GPU active input selection before clock registration. DFS registration covers the twenty QUPv3 serial RCGs. A DFS registration failure is logged with `dev_err_probe()` but does not stop clock-controller registration.

Runtime behavior is table-driven. Clock consumers request rates or gates through the common clock framework; generic qcom ops translate those requests into RCG parent/divider/MND programming, branch enable bits, halt polling, or vote bits. Branches use a mix of `BRANCH_HALT`, `BRANCH_HALT_VOTED`, `BRANCH_VOTED`, `BRANCH_HALT_DELAY`, and `BRANCH_HALT_SKIP`. Delay/skip checks are used where external parent state makes direct halt polling unreliable, notably PCIe/USB/UFS symbol or pipe clocks and critical multimedia XO/AHB paths.

## State And Persistence
There is no filesystem or cross-boot persistence. Persistent state for a boot consists of the GCC register contents after firmware, bootloader, and this driver's probe writes. PLLs are represented as fixed TRION alpha PLLs; this driver does not dynamically configure their alpha parameters in probe. RCGs, branches, resets, and GDSCs mutate hardware state through regmap when consumers call CCF, reset-controller, or power-domain APIs.

Several branches are intentionally kept critical through `CLK_IS_CRITICAL`: camera, display, and video AHB/XO clocks, CPUSS DVM/GNOC support, GPU CFG AHB, and NPU CFG AHB. UFS card/PHY include hardware-controlled secondary branches for AXI, ICE, PHY AUX, and UniPro paths. GDSCs for PCIe0/1, UFS card, UFS PHY, EMAC, and USB30 primary/secondary use `PWRSTS_OFF_ON` with `POLL_CFG_GDSCR`, so power transitions are controlled and polled through the generic GDSC layer.

## Dependencies And Integration Points
The driver depends on Qualcomm qcom-clk infrastructure in the same directory: `common.h`, `clk-alpha-pll.h`, `clk-branch.h`, `clk-pll.h`, `clk-rcg.h`, `clk-regmap.h`, `reset.h`, and `gdsc.h`, plus Linux platform, regmap, clock provider, module, OF, and reset-controller APIs. Device-tree consumers bind by numeric IDs from `qcom,gcc-sm8150.h`.

Integration points include PCIe controllers and PHYs, USB3 controllers/PHYs, UFS host/card drivers and inline crypto, SDHCI for SDCC2/4, QUPv3 UART/I2C/SPI controllers, PDM audio, TSIF, QSPI, EMAC/RGMII networking, GPU and NPU drivers, camera/display/video subsystems, PRNG, and reset-controller clients. External parent availability and naming in device tree are required for XO, sleep, and audio reference parents.

## Risks
The highest risk is descriptor correctness rather than algorithmic control flow. Parent maps use sparse hardware selector values, and small mistakes can route clocks to the wrong GPLL or external parent. Fractional rate tables for QUP, EMAC RGMII, SDCC, USB, and UFS rely on exact divider/MND values. The probe-time MISC writes are unconditional after regmap mapping; an offset or mask regression could affect GPU/NPU clock sourcing before their consumers probe.

Critical-clock flags should be changed conservatively because camera/display/video boot, CPUSS, GPU, and NPU support paths may hang or fail late if disabled. PCIe/USB/UFS pipe and symbol branches deliberately avoid normal halt polling, so validation must rely on endpoint behavior rather than only clock-summary enable state. Reset entries include both full block resets and bit-specific video clock resets; wrong offsets or bit numbers can reset adjacent multimedia logic. GDSC flags differ from later SoCs, and changing `POLL_CFG_GDSCR` or power states can introduce suspend/resume and runtime-PM failures.

## Test Signals
Basic validation is a clean probe of `qcom,gcc-sm8150`, no qcom CC registration errors, and a populated `/sys/kernel/debug/clk/clk_summary` containing GPLL0/GPLL7/GPLL9, QUPv3 roots, UFS, USB, PCIe, EMAC, SDCC, and multimedia GCC clocks. DFS registration should not log `Failed to register with DFS!`.

Hardware-oriented signals include serial/I2C/SPI operation across QUPv3 wrappers, SD/eMMC activity on SDCC2/4, UFS card and UFS PHY link up including ICE clocks if used, USB3 primary and secondary enumeration, PCIe0/1 link training, EMAC RGMII rates including PTP, display/camera/video boot without AHB/XO gating regressions, GPU/NPU driver probe, and reset-controller operations for PCIe, USB, UFS, QUP, SDCC, TSIF, EMAC, PDM, PRNG, MMSS, GPU, and NPU without collateral device loss.
