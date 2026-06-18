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
