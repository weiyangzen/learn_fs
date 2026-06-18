# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm6125.c

## Purpose
`gcc-sm6125.c` is the Qualcomm Global Clock Controller driver for the SM6125 SoC. It publishes the GCC clock, reset, and GDSC providers defined by `dt-bindings/clock/qcom,gcc-sm6125.h` to Linux CCF, reset-controller, and genpd consumers. The clock plan covers GPLL-derived roots, a large camera subsystem with CSI/VFE/CPP/JPEG/MCLK paths, QUPv3 wrap0 and wrap1 serial engines, SDCC and ICE, UFS, USB3, display, GPU, voltage-sensor/voltage-scaling support clocks, crypto engine clocks, NoC votes, and multimedia power domains.

Like most Qualcomm GCC drivers, this file is primarily a static hardware description. It declares PLL, fixed-factor, RCG, branch, reset, GDSC, and descriptor tables. Runtime logic is concentrated in `gcc_sm6125_probe()`, which maps GCC registers, applies a few required register tweaks, registers DFS support for QUPv3 RCGs, and hands the descriptor to the common qcom CC registration path.

## Important APIs, Types, And Functions
`struct clk_alpha_pll` objects model GPLL0, GPLL3, GPLL4, GPLL5, GPLL6, GPLL7, GPLL8, and GPLL9 outputs. Unlike `gcc-sm6115.c`, this driver does not provide explicit `alpha_pll_config` tables or call `clk_alpha_pll_configure()`; it represents the PLLs using `CLK_ALPHA_PLL_TYPE_DEFAULT` layouts and expects the shared PLL ops and boot firmware state to supply usable PLL state.

`struct clk_fixed_factor` exposes several half-rate GPLL outputs: `gpll0_out_aux2`, `gpll0_out_main`, `gpll6_out_main`, `gpll7_out_main`, `gpll8_out_main`, and `gpll9_out_main`. These are gathered in `gcc_sm6125_hws[]` because they are standalone `clk_hw` providers rather than `clk_regmap` clocks. PLL early outputs and other register-backed clocks are exported through `gcc_sm6125_clocks[]`.

`struct parent_map` and `struct clk_parent_data` arrays map hardware RCG parent selectors to `bi_tcxo`, `sleep_clk`, PLL early outputs, and fixed-factor GPLL outputs. The file defines 15 parent-map families to cover simple XO/GPLL roots, QUP roots, camera CSI/CSIPHY/JPEG/VFE/CPP roots, SDCC roots, and sleep-clock capable roots.

`struct freq_tbl` tables encode selectable RCG rates. Important tables cover camera AHB, CCI, CPP, CSI0-3, CSI PHY timers, CSIPHY, camera GP0/GP1, JPEG, MCLK0-3, VFE0/VFE1, GP1-3, PDM2, QUPv3 wrap0/wrap1 serial sources, SDCC1 apps and ICE, SDCC2 apps, UFS PHY AXI/ICE/AUX/UNIPRO, USB30 master/mock UTMI/PHY aux, VS control, and VSENSOR. QUP tables include fractional serial rates, SDCC uses floor ops, and camera MCLK tables use M/N division from GPLL9 for 24 and 64 MHz sensor clocks.

`struct clk_rcg2` implements all root generators. The file mostly uses `clk_rcg2_ops`; SDCC apps roots use `clk_rcg2_floor_ops`. `gcc_sm6125_probe()` registers DFS data for 12 QUPv3 RCGs, covering six serial sources in wrap0 and six in wrap1.

`struct clk_branch` objects provide leaf gates for camera, crypto, display, GPU, QUP, storage, USB, voltage-scaling, video, and NoC paths. Many leaf clocks set `CLK_SET_RATE_PARENT`, several infrastructure clocks are `CLK_IS_CRITICAL`, and branch halt behavior includes plain, delayed, voted, and vote-only variants. The driver also includes voltage-related branches such as `gcc_apc_vs_clk`, `gcc_mss_vs_clk`, `gcc_vdda_vs_clk`, `gcc_vddcx_vs_clk`, `gcc_vddmx_vs_clk`, `gcc_vs_ctrl_clk`, `gcc_vs_ctrl_ahb_clk`, and `gcc_wcss_vs_clk`.

`struct gdsc` entries describe USB30 primary, UFS PHY, CAMSS VFE0, CAMSS VFE1, CAMSS top, CAM CPP, and four HLOS vote TBU domains. `struct qcom_reset_map gcc_sm6125_resets[]` maps reset IDs for QUSB2 PHYs, UFS PHY, USB30 primary, USB PHY CFG AHB2PHY, USB3 PHY/controller SP0, and CAMSS micro reset. `struct qcom_cc_desc gcc_sm6125_desc` ties together regmap config, `gcc_sm6125_clocks[]`, `gcc_sm6125_hws[]`, resets, and GDSCs.

## Control Flow
The module registers `gcc_sm6125_driver` from `subsys_initcall(gcc_sm6125_init)`, matching device-tree nodes with `compatible = "qcom,gcc-sm6125"`. Probe follows this sequence:

1. `qcom_cc_map(pdev, &gcc_sm6125_desc)` maps the MMIO block into a regmap with 32-bit registers, 4-byte stride, `max_register = 0xc7000`, and `fast_io = true`.
2. `regmap_update_bits(regmap, 0x80258, 0x1, 0x1)` disables the GPLL0 active input to the video block through a MISC register. This is a probe-time hardware policy write, not an exported clock operation.
3. Four MCLK RCG registers at `0x51004`, `0x51020`, `0x5103c`, and `0x51058` are updated with mask `0x3000` and value `0x2000` to enable dual-edge mode, which the comments state is required for MND divider mode.
4. `qcom_cc_register_rcg_dfs()` registers DFS support for QUPv3 wrap0 and wrap1 serial sources. Failure aborts probe before the provider is registered.
5. `qcom_cc_really_probe()` registers all clocks, hardware-only fixed-factor clocks, reset controls, and GDSCs with the relevant frameworks.

After registration, consumer drivers interact through CCF, reset-controller, and genpd APIs. RCG ops select frequency-table rows and program parent/divider/M/N fields. Branch ops control gate/vote bits and poll according to each branch's halt behavior. Reset and GDSC operations write the offsets listed in the reset and power-domain tables.

## Clock And Subsystem Coverage
The camera subsystem is broad. It includes AHB and XO roots, CCI, CPP AHB/AXI/core/VBIF clocks, four CSI instances with AHB/core/pixel/RDI paths, CPHY CSID clocks, CSI VFE bridges, three CSIPHY clocks, camera GP0/GP1, JPEG AHB/AXI/core, four MCLK sensor roots, micro AHB, top AHB, VFE0/VFE1 AHB/core/stream, VFE timestamp counter, VFE VBIF AHB/AXI, NRT/RT throttle votes, and GDSCs for VFE0, VFE1, CAMSS top, and CAM CPP.

QUPv3 coverage includes two wraps. Each wrap has a core 2x clock, core clock, six serial engine branches, six serial RCG sources, and master/slave AHB branches. The shared QUP table supports UART/SPI/I2C friendly fractional rates and high-speed rates up to 128 MHz. DFS registration covers all 12 serial sources.

Storage and I/O coverage includes SDCC1/SDCC2 AHB/apps clocks, SDCC1 ICE, UFS PHY AHB/AXI/ICE/AUX/RX symbol/TX symbol/UNIPRO, UFS memory clkref, USB30 primary master/mock UTMI/sleep, USB3 PHY aux/com aux/pipe/clkref, and resets for UFS and USB PHY/controller blocks. Crypto engine CE1 clocks are present as AHB, AXI, and core branches.

Display, GPU, video, voltage-sensor, and NoC support includes display AHB/HF AXI/XO/throttle and GPLL0 divider branches, GPU CFG AHB/GPLL0 source/divider/MEMNOC/SNOC DVM/throttle/XO, video AHB/AXI/throttle/XO, VS control and VSENSOR RCGs, several voltage-scaling branches, CPUSS GNOC, system NoC clocks for compute/UFS/USB, PRNG, PDM, GP clocks, and QMIP vote branches.

## State And Persistence Behavior
The driver's own state is static C data. It allocates no per-device private structure, starts no workers, writes no files, and has no suspend/resume callbacks. Live state is in GCC registers plus framework-managed clock/reset/genpd objects.

Probe-time register updates persist for the current boot. The video MISC write at `0x80258` changes the video block's GPLL0 active input behavior before consumers can enable video clocks. The four MCLK dual-edge writes alter RCG mode bits so MND-divided sensor clocks can operate correctly. These writes are not rolled back at remove time; hardware reset or later register programming would be required to change them.

PLL state is less explicitly owned here than in SM6115. The driver registers GPLL early outputs and fixed-factor main/aux outputs but does not configure PLL rate registers during probe. That makes bootloader/firmware PLL setup and shared PLL ops part of the operational assumption. GDSCs use `PWRSTS_OFF_ON`, with four HLOS vote domains marked `VOTABLE` for shared vote semantics.

## Dependencies And Integration Points
The driver depends on Linux CCF, regmap, platform bus, OF matching, reset-controller, genpd/GDSC support, and Qualcomm clock helper headers `clk-alpha-pll.h`, `clk-branch.h`, `clk-rcg.h`, `clk-regmap.h`, `common.h`, `gdsc.h`, and `reset.h`. It also uses `clk_fixed_factor_ops` from the common clock framework for hardware-only GPLL-derived outputs.

Device-tree integration requires the SM6125 GCC compatible, `bi_tcxo` and `sleep_clk` parent names, and consumers using IDs from `qcom,gcc-sm6125.h`. Main integration consumers are camera/VFE/CPP/JPEG/CSI drivers, QUPv3 serial controllers, SDHCI and ICE, UFS, USB3 and PHY drivers, crypto engine, display, GPU, video, voltage-sensor or voltage-scaling clients, PRNG/PDM, NoC vote users, reset consumers, and GDSC power-domain consumers.

## Risks And Edge Cases
The probe-time MISC and MCLK writes are unversioned register writes. Offset or mask mistakes can affect video and camera sensor-clock behavior before any consumer driver has a chance to compensate. The four MCLK writes are necessary for MND divider mode; missing them can produce broken 24/64 MHz camera MCLKs even when the rate table looks correct.

PLL ownership differs from SM6115. Because this file does not configure GPLLs in probe, incorrect firmware PLL setup or an unexpected reset state can make downstream RCG rates wrong. Fixed-factor GPLL main outputs also assume the parent PLL early output frequency matches the expected clock plan.

Camera coverage is large and selector-sensitive. CSI, CSIPHY, VFE, CPP, JPEG, MCLK, and VFE bridge branches reuse similar parent maps and rate families. Wrong parent selectors can produce valid-looking but incorrect rates, especially between GPLL4, GPLL5, GPLL8, GPLL9, and GPLL6 options.

QUPv3 has two wraps and 12 DFS-registered RCGs. Missing a DFS entry or mapping a wrap1 source to a wrap0 register would affect only some serial ports and can be hard to detect without testing every SE.

Halt checks and critical flags should be preserved carefully. Shared/voted branches use `BRANCH_HALT_VOTED` or `BRANCH_VOTED`, delayed branches tolerate asynchronous hardware, and critical fabric/GPU/display/video related clocks are protected from unused-clock cleanup. Simplifying these can introduce probe-time timeouts or late boot hangs.

Reset and GDSC arrays are sparse binding-indexed tables. Adding or moving binding IDs without matching array designators can expose wrong reset or power-domain controls. CAMSS micro reset is the only camera reset in this map, so consumers must not infer broader camera reset coverage from the clock list.

## Test Signals
Build testing should compile the SM6125 GCC driver and catch missing binding names, array designator drift, or CCF type mismatches between `clk_hw` fixed-factor entries and `clk_regmap` entries. Probe testing should boot a device tree with `compatible = "qcom,gcc-sm6125"` and verify the GCC provider registers before camera, serial, storage, USB, display, GPU, video, and voltage-sensor consumers complete probing.

Clock debugfs should show GPLL early outputs, fixed-factor GPLL main/aux outputs, all QUPv3 wrap0 and wrap1 serial sources, SDCC/ICE roots, UFS/USB roots, camera CPP/CSI/CSIPHY/JPEG/MCLK/VFE roots, VSENSOR/VS control roots, and expected branch enable counts as devices probe. Functional coverage should exercise all active QUPv3 SEs, SD/eMMC including ICE, UFS, USB3, camera MCLK plus CSI/VFE/CPP/JPEG paths, CE1 crypto, display/GPU, video, and voltage-sensor clients.

Specific regression checks should confirm camera MCLKs can produce MND-derived 24 MHz and 64 MHz rates after the dual-edge mode writes, video clocks behave correctly after the GPLL0 active input MISC write, and DFS works independently for wrap0 and wrap1 serial clocks. Reset/GDSC tests should cover UFS, USB30, USB PHY, CAMSS micro reset, camera VFE/top/CPP domains, and votable TBU domains while watching for unexpected branch halt timeouts.
