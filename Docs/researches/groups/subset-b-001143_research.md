# subset-b-001143

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm8150.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm8150.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm8250.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm8250.c

## Purpose
`gcc-sm8250.c` is the Qualcomm global clock controller provider for SM8250-class SoCs. It registers the GCC register block with the common clock framework, reset controller, and generic power-domain infrastructure using IDs from `dt-bindings/clock/qcom,gcc-sm8250.h`. The covered hardware includes Lucid GPLLs, CPUSS AHB roots and post-divider, three PCIe instances, UFS card and UFS PHY clocks, USB3 primary and secondary clocks, QUPv3 serial engines, SDCC, TSIF, PDM, GPU and NPU support clocks, multimedia fabric votes, and MMU TBU vote GDSCs.

## Important APIs, Types, And Functions
The driver uses `struct clk_alpha_pll` for GPLL0, GPLL4, and GPLL9 with LUCID PLL register layouts, `struct clk_alpha_pll_postdiv` for `gpll0_out_even`, `struct clk_rcg2` for programmable roots, `struct clk_regmap_div` for read-only CPUSS AHB and USB mock-UTMI post-dividers, `struct clk_branch` for gates and vote-controlled branches, `struct gdsc` for power domains, `struct qcom_reset_map` for resets, `struct clk_rcg_dfs_data` for QUP DFS, and `struct qcom_cc_desc` for the provider descriptor.

Parent data arrays combine firmware parents `bi_tcxo`, `bi_tcxo_ao`, `sleep_clk`, and `aud_ref_clk` with in-file PLL hardware. `bi_tcxo_ao` is used for always-on style CPUSS AHB and PCIe refgen roots. RCG frequency tables cover CPUSS AHB, GP1-3, three PCIe AUX roots, PCIe PHY refgen, PDM2, QUPv3 serial lanes, SDCC2/4, TSIF, UFS card/PHY AXI/ICE/AUX/UniPro, and USB3 master/mock UTMI/PHY AUX roots. The clock array also exposes read-only dividers for CPUSS AHB and USB mock UTMI post-dividers.

`gcc_sm8250_probe()` maps registers with `qcom_cc_map()`, applies two GPU/NPU GPLL0 input MISC writes, force-enables several always-on branches with `qcom_branch_set_clk_en()`, registers QUP DFS data with `qcom_cc_register_rcg_dfs()`, and then calls `qcom_cc_really_probe()`.

## Control Flow
The platform driver matches `qcom,gcc-sm8250` and registers at `subsys_initcall()` time. Probe maps the GCC regmap, disables GPLL0 active input to NPU and GPU by writing offsets `0x4d110` and `0x71028`, and then enables several critical branches directly: video AHB at `0x0b004`, camera AHB at `0x0b008`, display AHB at `0x0b00c`, CPUSS DVM bus at `0x4818c`, GPU CFG AHB at `0x71004`, and the system NoC CPUSS AHB vote register at `0x52000`. If DFS registration fails, probe returns the error and does not register the provider.

After registration, normal clock operations are handled by generic qcom regmap clock ops. RCG roots select parents and dividers from the frequency tables; branch clocks assert enable bits and perform halt/vote checks; reset clients toggle mapped reset registers; GDSC clients transition power domains. SM8250 commonly uses `BRANCH_HALT_VOTED` for fabric and peripheral branches, `BRANCH_HALT_DELAY` or `BRANCH_HALT_SKIP` for externally dependent pipe/symbol clocks, and `clk_regmap_div_ro_ops` for read-only divider state owned by hardware or firmware.

## State And Persistence
The driver has no filesystem persistence. It persists only live hardware state for the current boot: probe-time MISC writes, direct branch enables, DFS registrations, and subsequent CCF/reset/GDSC changes. PLLs are fixed LUCID alpha PLL descriptors rather than probe-programmed PLL configurations. The CPUSS AHB and USB mock UTMI post-dividers are read-only views into GCC registers, so consumers can observe derived topology without the driver writing those divider fields.

Power domains include PCIe0/1/2 and USB30 primary/secondary with `PWRSTS_RET_ON`, UFS card and UFS PHY with `PWRSTS_OFF_ON`, and four votable HLOS1 MMNOC MMU TBU GDSCs with `VOTABLE`. Unlike SM8150, several always-on AHB/XO paths are not expressed as `CLK_IS_CRITICAL` branch descriptors in the same way; probe force-enables them before registration. This makes boot-time register programming part of the driver's state contract.

## Dependencies And Integration Points
The driver depends on Linux CCF, platform, OF, regmap, module, and qcom clock-controller helpers: `clk-alpha-pll.h`, `clk-branch.h`, `clk-rcg.h`, `clk-regmap.h`, `clk-regmap-divider.h`, `common.h`, `gdsc.h`, and `reset.h`. Device-tree consumers use IDs from `qcom,gcc-sm8250.h` and must provide the firmware-named parent clocks.

Integration points include CPU/NoC infrastructure through CPUSS AHB and DVM clocks, PCIe0/1/2 controllers and PHYs including modem/Wi-Fi/WiGig reference enables, UFS card and UFS PHY controllers, USB3 primary/secondary controllers and PHYs, QUPv3 UART/I2C/SPI serial engines, SDCC2/4, TSIF, PDM, PRNG, GPU, NPU and NPU BWMON, camera/display/video subsystems, reset-controller users, and genpd consumers for PCIe/UFS/USB/MMU TBU power domains.

## Risks
The main risk is that SM8250 is close to SM8150 but not register-compatible. Many offsets are shifted, PCIe has a third instance, PLLs are Lucid rather than Trion, USB mock UTMI uses read-only post-dividers, and several always-on clocks are enabled imperatively in probe. Copying SM8150 descriptors or flags into this file can break clock routing or silently leave required boot clocks gateable.

Parent-map and rate-table mistakes can affect QUP baud rates, SDCC tuning, UFS link rates, USB UTMI timing, and PCIe refgen behavior. The unconditional probe writes and `qcom_branch_set_clk_en()` calls must remain tied to the correct offsets, because they run before consumers probe. Pipe and symbol clocks have delayed or skipped halt checking due to external PHY dependencies, so software-visible halt status is not a complete correctness signal. Reset maps contain many PCIe link, PHY, NOCSR, USB PHY, and video ARES entries; wrong offsets, bits, or delays can cause hard-to-debug link and multimedia failures. Votable MMU TBU GDSCs add a shared-power-domain risk where one consumer's vote behavior can affect camera/display/video memory translation paths.

## Test Signals
Basic signals are successful probe for `qcom,gcc-sm8250`, successful DFS registration, no qcom CC registration errors, and expected clocks visible in `/sys/kernel/debug/clk/clk_summary`, including Lucid GPLLs, CPUSS AHB source/post-divider, QUPv3 DFS roots, PCIe0/1/2, UFS, USB, SDCC, GPU, NPU, and multimedia fabric clocks.

Hardware validation should cover UART/I2C/SPI operation on all populated QUPv3 wrappers, SDCC2/4 operation, UFS card and UFS PHY link-up including ICE, USB3 primary and secondary enumeration with correct mock UTMI/post-divider behavior, PCIe0/1/2 link training and modem/Wi-Fi/WiGig refclk users, camera/display/video boot with MMU TBU GDSC voting, GPU and NPU probe including BWMON clocks, runtime suspend/resume for PCIe/UFS/USB GDSCs, and reset-controller assertions for PCIe link/PHY/NOCSR, USB PHY, QUP, UFS, SDCC, TSIF, PDM, PRNG, MMSS, GPU, NPU, and video ARES entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm8250.c -->
