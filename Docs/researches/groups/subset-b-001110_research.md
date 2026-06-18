# subset-b-001110 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/pxa/clk-pxa3xx.c -->
## sources/distributed-fs/ceph-client/drivers/clk/pxa/clk-pxa3xx.c

### Purpose
`clk-pxa3xx.c` registers the Marvell PXA3xx clock tree for legacy, mostly non-devicetree PXA platforms, with a small DT entry point for `marvell,pxa300-clocks`. It models the 13 MHz oscillator, 32.768 kHz oscillator, ring oscillator, system PLL, core PLL, run/core/system-bus muxes, AC97 and static-memory clocks, plus CKEN-gated peripheral clocks.

### Important APIs, Types, And Functions
Important exported or external entry points are `pxa3xx_get_clk_frequency_khz()`, `pxa3xx_clk_update_accr()`, `pxa3xx_clocks_init()`, and the `CLK_OF_DECLARE()` init hook. The file builds `desc_clk_cken` tables for common PXA3xx devices and PXA300/PXA310, PXA320, and PXA93x variants. Rate helpers include `clk_pxa3xx_ac97_get_rate()`, `clk_pxa3xx_smemc_get_rate()`, `clk_pxa3xx_system_bus_get_rate()`, `clk_pxa3xx_core_get_parent()`, `clk_pxa3xx_run_get_rate()`, and `clk_pxa3xx_cpll_get_rate()`.

### Control Flow, State, And Persistence
Global state is the mapped `clk_regs` pointer. Init records the register base, registers fixed/factor PLL roots, derived core and bus clocks, dummy compatibility clocks, and CKEN gates. CPU identification chooses the variant-specific CKEN table. Runtime state is entirely hardware register backed: ACCR/ACSR select PLL ratios, turbo mode is read through CP14 XCLKCFG, CKENA/CKENB gate peripherals, and `pxa3xx_clk_update_accr()` writes ACCR then busy-waits until ACSR reflects masked bits.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on PXA common clock helpers, clkdev names used by legacy platform devices, `cpu_is_pxa*()` SoC detection, SMEMC memory-divider helpers, MMIO, CP14 instructions, and DT clock binding IDs. Risks include indefinite waits if ACCR changes never settle, division by zero from malformed hardware state, fragile legacy device-name lookup, and a stray `pr_info()` in CPLL rate calculation that can spam logs. Test signals include boot on PXA300/310/320/93x, expected `/sys/kernel/debug/clk` rates, peripheral probe success for UART/I2C/MMC/USB/AC97/LCD, DT clock provider registration, and frequency-change paths reaching matching ACSR values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/pxa/clk-pxa3xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/Kconfig

### Purpose
This Kconfig file defines the selectable Qualcomm common clock controller matrix. It enables the shared `COMMON_CLK_QCOM` framework and per-SoC controllers for global, camera, display, GPU, video, TCSR, RPM/RPMh, LPASS, APSS CPU, NSS, PMIC, HFPLL, Krait, and related clock blocks.

### Important APIs, Types, And Functions
The important symbols for this subset are `COMMON_CLK_QCOM`, `QCOM_GDSC`, `QCOM_A53PLL`, `QCOM_A7PLL`, `QCOM_CLK_APCS_MSM8916`, `QCOM_CLK_APCC_MSM8996`, `QCOM_CLK_APCS_SDX55`, `IPQ_APSS_PLL`, `IPQ_APSS_5424`, `IPQ_APSS_6018`, `CLK_KAANAPALI_CAMCC`, and `SM_CAMCC_8750`. Most controller symbols are tristates, allowing built-in or module builds. Selections wire dependencies such as `REGMAP_MMIO`, `RESET_CONTROLLER`, `INTERCONNECT`, `QCOM_GDSC`, SoC GCC providers, SMEM, APCS IPC, and architecture limits.

### Control Flow, State, And Persistence
There is no runtime control flow, but the Kconfig graph determines which C files compile and which provider drivers can satisfy DT compatibles. `COMMON_CLK_QCOM` gates the menu and selects shared infrastructure. Multimedia controllers usually select their SoC GCC to ensure upstream parent clocks are present. CPU/APSS options select or depend on PLL, IPC, SMEM, interconnect, and architecture symbols so CPU clock scaling pieces build together.

### Dependencies, Integration Points, Risks, And Test Signals
This file integrates the clock drivers with kernel configuration, devicetree-described platforms, reset and generic power-domain support, RPM/RPMh firmware interfaces, and interconnect clocks. Risks are missing `select` statements causing parent clocks, GDSCs, or reset support to be absent; overly narrow architecture dependencies hiding COMPILE_TEST coverage; and Makefile/Kconfig drift. Test signals include `allmodconfig`/`allyesconfig`/SoC defconfig builds, module link checks for every selected symbol, DT boot logs finding the expected clock providers, and camera/APSS symbols pulling their paired files from the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/Makefile -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/Makefile

### Purpose
The Qualcomm clock Makefile maps Kconfig symbols to shared framework objects and per-controller object files. It is the build contract connecting the symbols in `Kconfig` to regmap, PLL, RCG, branch, reset, GDSC, RPM, APSS, camera, display, GPU, video, and SoC-specific drivers.

### Important APIs, Types, And Functions
The composite `clk-qcom.o` is built from common infrastructure: `common.o`, `clk-regmap.o`, alpha and legacy PLL helpers, RCG/RCG2, branch clocks, regmap dividers/muxes/mux-divs, PHY muxes, HFPLL, reset, optional Krait support, and optional GDSC support. Subset-relevant mappings include `QCOM_A53PLL -> a53-pll.o`, `QCOM_A7PLL -> a7-pll.o`, `QCOM_CLK_APCS_MSM8916 -> apcs-msm8916.o`, `QCOM_CLK_APCC_MSM8996 -> apcs-msm8996.o clk-cpu-8996.o clk-cbf-8996.o`, `QCOM_CLK_APCS_SDX55 -> apcs-sdx55.o`, `IPQ_APSS_PLL -> apss-ipq-pll.o`, `IPQ_APSS_5424 -> apss-ipq5424.o`, `IPQ_APSS_6018 -> apss-ipq6018.o`, `CLK_KAANAPALI_CAMCC -> cambistmclkcc-kaanapali.o camcc-kaanapali.o`, and `SM_CAMCC_8750 -> cambistmclkcc-sm8750.o camcc-sm8750.o`.

### Control Flow, State, And Persistence
There is no runtime state. Build-time state is the ordered set of `obj-$(CONFIG_...)` and `clk-qcom-$(CONFIG_...)` assignments. The file asks maintainers to keep per-controller entries alphabetically sorted by config, which reduces merge conflicts in a high-churn driver directory.

### Dependencies, Integration Points, Risks, And Test Signals
It integrates Kbuild with Kconfig, generated DT binding constants, module autoloading through each driver, and shared `clk-qcom.o` support. Risks include missing objects for new Kconfig entries, duplicated objects under multiple configs, accidental module link failures when a controller uses helpers not included in `clk-qcom.o`, and sort drift hiding conflicts. Test signals are kernel builds for each selected symbol, `modpost` without unresolved symbols, camera configs building both CAMBISTMCLKCC and CAMCC objects, and MSM8996 APCC building the auxiliary CPU/CBF clock objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/a53-pll.c -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/a53-pll.c

### Purpose
`a53-pll.c` provides a Qualcomm A53 CPU PLL clock provider for MSM8226/MSM8916/MSM8939 style platforms. It exposes a single SR2 PLL clock sourced from `xo`, with rates either derived from OPP data or a built-in frequency table above 1 GHz.

### Important APIs, Types, And Functions
The main functions are `qcom_a53pll_get_freq_tbl()` and `qcom_a53pll_probe()`. It uses `struct clk_pll`, `struct pll_freq_tbl`, `struct regmap_config`, `clk_pll_sr2_ops`, `devm_clk_register_regmap()`, and `devm_of_clk_add_hw_provider()`. The match table supports `qcom,msm8226-a7pll`, `qcom,msm8916-a53pll`, and `qcom,msm8939-a53pll`.

### Control Flow, State, And Persistence
Probe allocates a `clk_pll`, maps the MMIO resource, creates a regmap, fills PLL register offsets, chooses an OPP-derived frequency table when possible, otherwise falls back to static rates, creates a unique clock name from the DT unit address, registers the regmap clock, and publishes the OF clock provider. The driver has no remove path because all resources are devm-managed. Persistent state is hardware PLL register state plus the devm-owned `clk_pll` data.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include platform DT resources, the common clock framework, regmap MMIO, PM OPP tables, and qcom PLL helpers. It integrates with APCS CPU mux drivers that use this PLL as a parent and with cpufreq/OPP data for dynamic rates. Risks include silently falling back to a limited static table if OPP parsing fails, leaked OPP references on skipped frequencies, malformed OPP frequencies not divisible by XO, and name uniqueness depending on DT node names. Test signals include provider registration, CPUfreq rate changes, OPP-derived table coverage, fallback rates on boards without OPP data, and deferred probes when parent `xo` is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/a53-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/a7-pll.c -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/a7-pll.c

### Purpose
`a7-pll.c` registers the SDX55/SDX65 Qualcomm A7 CPU PLL. It models a Lucid alpha PLL named `a7pll`, configured from a fixed table when the hardware L register indicates the PLL is not already configured.

### Important APIs, Types, And Functions
The driver centers on static `struct clk_alpha_pll a7pll`, `struct alpha_pll_config a7pll_config`, `lucid_vco`, and `qcom_a7pll_probe()`. It uses `clk_alpha_pll_lucid_ops`, `clk_lucid_pll_configure()`, `devm_clk_register_regmap()`, and `devm_of_clk_add_hw_provider()`. The sole OF compatible is `qcom,sdx55-a7pll`.

### Control Flow, State, And Persistence
Probe maps MMIO, creates a regmap over a 0x1000 register range, reads the Lucid PLL L register at `offset + 0x04`, configures the PLL only if that value is zero, registers the PLL as a regmap-backed clock, and adds an OF clock provider. Runtime state persists in PLL registers. The static clock object is shared by the module instance, so the DT binding effectively expects one controller instance.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include the qcom alpha PLL framework, platform MMIO resources, the `bi_tcxo` parent clock, and the APCS SDX55 mux driver that consumes `pll`. Risks include relying on nonzero L as proof that firmware configured the PLL correctly, static object reuse if multiple matching devices appeared, missing explicit error logging, and incorrect VCO/config values affecting CPU stability. Test signals include boot-time provider registration, no reconfiguration when boot firmware already programmed L, CPUfreq transitions through the APCS mux, and clk summary showing `a7pll` with the expected parent and rate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/a7-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/apcs-msm8916.c -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/apcs-msm8916.c

### Purpose
`apcs-msm8916.c` registers the MSM8916 APCS CPU mux/divider clock. It selects between an auxiliary GPLL0-derived parent and the A53 PLL, and uses a notifier to move the CPU clock to a safe 400 MHz configuration before PLL rate changes.

### Important APIs, Types, And Functions
Important pieces are `struct clk_regmap_mux_div`, `gpll0_a53cc_map`, `pdata`, `a53cc_notifier_cb()`, `qcom_apcs_msm8916_clk_probe()`, and `qcom_apcs_msm8916_clk_remove()`. The clock uses `clk_regmap_mux_div_ops`, `mux_div_set_src_div()`, `clk_notifier_register()`, and `devm_of_clk_add_hw_provider()`.

### Control Flow, State, And Persistence
Probe obtains the parent regmap from the APCS IPC parent device, allocates the mux/divider, names it uniquely using the parent's unit address, programs register layout at offset `0x50`, gets the parent PLL clock, registers a PLL notifier, registers the regmap clock, and publishes it to DT. On `PRE_RATE_CHANGE`, the notifier selects source 4 and divider 3 as a safe temporary rate. Remove unregisters the notifier. State is hardware-backed in the APCS mux/divider register and notifier membership.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include a parent APCS regmap device, `aux`/`gpll0_vote` and `pll`/`a53pll` clocks, qcom mux-div helpers, common clock notifiers, and DT clock consumers for CPUfreq. Risks include CPU instability if the safe source/divider is wrong, notifier cleanup only after successful registration, probe deferral for the PLL parent, and fragile parent-name fallback. Test signals include CPUfreq PLL changes, notifier execution before PLL changes, clock provider availability, removal/unbind notifier cleanup, and boot logs without failed regmap or parent clock acquisition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/apcs-msm8916.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/apcs-msm8996.c -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/apcs-msm8996.c

### Purpose
`apcs-msm8996.c` provides the early MSM8996 `sys_apcs_aux` clock used while CPU cluster PLLs are initialized. It programs the APCS auxiliary divider and exposes the result as a fixed 300 MHz clock to simplify early CPU-clock bootstrapping.

### Important APIs, Types, And Functions
The driver uses `qcom_apcs_msm8996_clk_probe()`, `dev_get_regmap()`, `regmap_read()`, `regmap_update_bits()`, `udelay()`, `devm_clk_hw_register_fixed_rate()`, and `devm_of_clk_add_hw_provider()`. Register definitions cover `APCS_AUX_OFFSET`, `APCS_AUX_DIV_MASK`, and `APCS_AUX_DIV_2`.

### Control Flow, State, And Persistence
Probe obtains the parent regmap, reads the APCS auxiliary register, writes divider bits to divide by two, waits 5 microseconds for hardware stability, registers fixed-rate `sys_apcs_aux`, and publishes it as the OF clock provider. Driver registration uses `postcore_initcall()` so the provider is available early enough for CPU cluster clock setup. Runtime state is the hardware divider plus the fixed-rate clock registration.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include the parent APCS regmap, early platform-driver registration, CCF fixed-rate clocks, and MSM8996 CPU cluster clock drivers that use the auxiliary source during PLL setup. Risks include declaring a fixed 300 MHz rate that must match the parent/divider reality, insufficient stabilization delay, register write failures not being checked, and early init ordering regressions that can break CPU bring-up. Test signals include early boot on MSM8996, CPU PLL setup success, `sys_apcs_aux` visible before dependent CPU clocks, no fw_devlink delay of CPU clock drivers, and stable secondary CPU bring-up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/apcs-msm8996.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/apcs-sdx55.c -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/apcs-sdx55.c

### Purpose
`apcs-sdx55.c` registers the SDX55 APCS CPU mux/divider clock and attaches the CPU device to its PM domain. Like MSM8916, it provides a safe temporary CPU clock path while the A7 PLL is reconfigured.

### Important APIs, Types, And Functions
The key functions are `a7cc_notifier_cb()`, `qcom_apcs_sdx55_clk_probe()`, and `qcom_apcs_sdx55_clk_remove()`. It uses `struct clk_regmap_mux_div`, `mux_div_set_src_div()`, `clk_notifier_register()`, `devm_clk_register_regmap()`, `dev_pm_domain_attach()`, `dev_pm_domain_detach()`, and `get_cpu_device(0)`.

### Control Flow, State, And Persistence
Probe obtains the parent regmap, allocates and initializes `a7mux` at register offset `0x8`, gets the `pll` clock from the parent, registers a notifier that switches to aux/divider safe configuration on `PRE_RATE_CHANGE`, registers and publishes the mux, stores driver data, and attaches CPU0 to its power domain with power-on semantics. Errors after notifier registration unwind by unregistering it. Remove unregisters the notifier and detaches the CPU PM domain.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include APCS IPC/regmap parent, `ref`, `aux`, and `pll` clocks, CCF notifiers, qcom mux-div helpers, generic PM domains, and CPU device registration. Risks include a driver-name typo (`acps`), CPU0 device or PM-domain absence, notifier lifetime across partial probe failures, and safe mux values that are hardware-specific. Test signals include SDX55/SDX65 CPUfreq transitions, PM domain attachment in boot logs, PLL rate-change notifier activity, clean module unload, and correct `a7mux` parent/rate under debugfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/apcs-sdx55.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/apss-ipq-pll.c -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/apss-ipq-pll.c

### Purpose
`apss-ipq-pll.c` is a shared APSS CPU PLL provider for several Qualcomm IPQ SoCs. It selects Huayra, Stromer, or Stromer Plus alpha PLL definitions and applies SoC-specific fixed configurations for CPU clock roots.

### Important APIs, Types, And Functions
Important objects are `ipq_pll_huayra`, `ipq_pll_stromer`, `ipq_pll_stromer_plus`, per-SoC `alpha_pll_config` structures for IPQ5018/IPQ5332/IPQ6018/IPQ8074/IPQ9574, `struct apss_pll_data`, and `apss_ipq_pll_probe()`. The probe uses `of_device_get_match_data()`, `clk_alpha_pll_configure()`, `clk_stromer_pll_configure()`, `devm_clk_register_regmap()`, and `devm_of_clk_add_hw_provider()`.

### Control Flow, State, And Persistence
Probe maps the PLL MMIO resource, creates a small regmap, fetches match data, configures the chosen PLL type, registers the single `a53pll` clock, and publishes it as an OF provider. Runtime persistence is the programmed PLL hardware state. The `SUPPORTS_DYNAMIC_UPDATE` flag allows later rate changes through the alpha PLL ops where supported.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include qcom alpha PLL helpers, DT compatibles, `xo` parent clock, IPQ APSS consumers, and Kconfig/Makefile wiring through `IPQ_APSS_PLL`. Risks include static PLL object reuse across multiple instances, unconditional reconfiguration of firmware-programmed PLLs, mismatched type/config pairs, and all variants exposing the same logical clock name. Test signals include provider probe for each compatible, CPU/APSS clock consumers obtaining `a53pll`, dynamic rate changes, register dumps matching expected L/config fields, and build coverage for Huayra and Stromer paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/apss-ipq-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/apss-ipq5424.c -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/apss-ipq5424.c

### Purpose
`apss-ipq5424.c` registers the IPQ5424 APSS clock controller. It provides APSS and L3 PLLs, RCG sources, critical core branch clocks, and an interconnect hardware clock relation between CPU and L3.

### Important APIs, Types, And Functions
Key objects include `ipq5424_apss_pll`, `apss_silver_clk_src`, `apss_silver_core_clk`, `ipq5424_l3_pll`, `l3_clk_src`, `l3_core_clk`, `apss_ipq5424_clks`, `icc_ipq5424_cpu_l3`, `apss_ipq5424_desc`, and `apss_ipq5424_probe()`. It uses `clk_alpha_pll_huayra_ops`, `clk_rcg2_ops`, `clk_branch2_ops`, `qcom_cc_probe()`, and `icc_sync_state()`.

### Control Flow, State, And Persistence
The static descriptor defines register layout, two configured Huayra 2290 PLLs, APSS silver and L3 RCG frequency tables, critical branches, interconnect hardware clock data, and driver data listing PLLs for common initialization. Probe delegates all mapping, registration, reset/GDSC-style setup, and provider publication to `qcom_cc_probe()`. State is MMIO-backed clock configuration and generic clock/interconnect provider registration.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include qcom common clock helpers, alpha PLL/RCG/branch implementations, DT binding IDs, two parent clocks by DT index, interconnect provider support, and GCC/firmware supplying reference clocks. Risks include a likely `ipa5424` naming typo in local arrays, incorrect interconnect node IDs, critical branches masking unused-clock cleanup issues, and PLL/frequency table mismatches affecting CPU or L3 stability. Test signals include IPQ5424 boot, APSS CPU frequency selection at 816 MHz to 1.8 GHz, L3 frequencies at 816 MHz to 1.272 GHz, interconnect sync-state behavior, and `clk_summary` showing critical APSS/L3 core clocks enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/apss-ipq5424.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/apss-ipq6018.c -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/apss-ipq6018.c

### Purpose
`apss-ipq6018.c` registers a compact APSS clock controller for IPQ platforms. It exposes a muxed APSS alias CPU clock source and core branch, and conditionally installs a safe-parent notifier for IPQ53xx variants that support CPU scaling.

### Important APIs, Types, And Functions
The file defines `apcs_alias0_clk_src`, `apcs_alias0_core_clk`, `apss_ipq6018_clks`, `apss_ipq6018_desc`, `cpu_clk_notifier_fn()`, and `apss_ipq6018_probe()`. It uses `qcom_smem_get_soc_id()`, `dev_get_regmap()`, `qcom_cc_really_probe()`, `clk_rcg2_mux_closest_ops`, and `devm_clk_notifier_register()`.

### Control Flow, State, And Persistence
Probe reads the SoC ID from SMEM, obtains the parent APCS regmap, registers the controller using the existing regmap, and for IPQ5332/IPQ5322/IPQ5300 allocates a notifier on the CPU mux clock. The notifier switches to GPLL0 before a rate change and back to APSS PLL after successful or aborted changes. State persists in the mux/branch registers and notifier registration; no explicit remove path is needed due to devm.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include a parent regmap, SMEM SoC ID service, `xo`, `gpll0`, and `pll` parents, qcom common clock helpers, and APSS PLL provider selection from Kconfig. Risks include failed SMEM blocking all probe, notifier registration against `hw->clk` after provider setup, scaling policy being restricted to listed SoC IDs, and parent index mismatches causing unsafe rate transitions. Test signals include probe on IPQ6018 and IPQ53xx, CPU rate transitions switching parents around PLL changes, branch enable state, SMEM ID fallback behavior, and `clk_summary` parent selection before and after cpufreq operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/apss-ipq6018.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/cambistmclkcc-kaanapali.c -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/cambistmclkcc-kaanapali.c

### Purpose
`cambistmclkcc-kaanapali.c` registers the Kaanapali camera BIST master-clock controller. It supplies eight camera test/master MCLK sources and branch clocks from a single 960 MHz Rivian EKO-T alpha PLL or the TCXO parent.

### Important APIs, Types, And Functions
Important state includes `cam_bist_mclk_cc_pll0`, `ftbl_cam_bist_mclk_cc_mclk0_clk_src`, eight `clk_rcg2` MCLK source instances, eight `clk_branch` MCLK gates, `cam_bist_mclk_cc_kaanapali_clocks`, critical CBCR list, `cam_bist_mclk_cc_kaanapali_desc`, and `cam_bist_mclk_cc_kaanapali_probe()`. It uses `clk_alpha_pll_rivian_eko_t_ops`, `clk_rcg2_shared_ops`, `clk_branch2_ops`, and `qcom_cc_probe()`.

### Control Flow, State, And Persistence
The descriptor lists PLL data, RCGs, branches, a register map up to `0x5010`, `use_rpm = true`, and a critical sleep-clock CBCR at `0x40e0`. Probe delegates to `qcom_cc_probe()`, which maps MMIO, configures PLLs from driver data, registers clocks, and publishes the provider. Runtime state is MMIO-backed PLL, RCG, and branch configuration. Frequency tables provide 19.2 MHz TCXO, 24 MHz divided PLL, and about 68.57 MHz PLL-main outputs.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include Kaanapali CAMBISTMCLKCC DT bindings, GCC/always-on parent clocks by DT index, qcom common clock code, RPM-aware clock handling, and camera/test clock consumers. Risks include duplicate tables copied across all eight MCLKs, critical CBCR offset errors leaving sleep clock gated, MCLK rate coverage gaps for sensors/tests, and no reset/GDSC coverage despite including headers. Test signals include module probe on `qcom,kaanapali-cambistmclkcc`, all eight MCLKs selectable, 24 MHz sensor-style output validation, sleep clock remaining on, and clk debugfs showing shared RCG behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/cambistmclkcc-kaanapali.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/cambistmclkcc-sm8750.c -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/cambistmclkcc-sm8750.c

### Purpose
`cambistmclkcc-sm8750.c` registers the SM8750 camera BIST master-clock controller. It is similar to the Kaanapali controller but uses a Rivian ELU PLL, adds a 12 MHz MCLK table entry, and exposes a sleep clock source RCG.

### Important APIs, Types, And Functions
Important objects are `cam_bist_mclk_cc_pll0`, `rivian_elu_vco`, MCLK parent maps and frequency table, `cam_bist_mclk_cc_sleep_clk_src`, eight MCLK `clk_rcg2` sources, eight MCLK branches, `cam_bist_mclk_cc_sm8750_clocks`, critical CBCR list, `cam_bist_mclk_cc_sm8750_desc`, and `cam_bist_mclk_cc_sm8750_probe()`. It uses `clk_alpha_pll_rivian_elu_ops`, `clk_rcg2_shared_ops`, `clk_branch2_ops`, and `qcom_cc_probe()`.

### Control Flow, State, And Persistence
Probe is descriptor-driven through `qcom_cc_probe()`. The descriptor covers a 0x5010 regmap, one alpha PLL, MCLK source/gate clock IDs, sleep source ID, `use_rpm = true`, and a critical sleep-clock CBCR at `0x40f8`. Runtime state is held in PLL, RCG, and CBCR hardware registers. Supported MCLK source rates include 12 MHz, 19.2 MHz, 24 MHz, and about 68.57 MHz; the sleep source is fixed to 32 kHz from `DT_SLEEP_CLK`.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include SM8750 CAMBISTMCLKCC bindings, TCXO and sleep parents by DT index, qcom common clock infrastructure, RPM handling, and camera sensor/test clock consumers. Risks include separate sleep-source and critical-CBCR offsets diverging, VCO table/config mismatch, repeated static definitions for eight channels, and missing parent clocks causing all camera MCLK consumers to defer. Test signals include SM8750 camera clock provider probe, MCLK rate requests at 12/19.2/24 MHz, sleep clock source operation, critical CBCR preservation across unused-clock cleanup, and module unload/reload on test builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/cambistmclkcc-sm8750.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-kaanapali.c -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-kaanapali.c

### Purpose
`camcc-kaanapali.c` registers the main Kaanapali camera clock controller. It provides PLLs, postdividers, RCGs, branch clocks, resets, and GDSC power domains for camera front-end, image processing, JPEG, CSIPHY/CSID, CAMNOC, debug, and top-level camera infrastructure.

### Important APIs, Types, And Functions
Major objects include eight Taycan EKO-T alpha PLLs (`cam_cc_pll0` through `cam_cc_pll7`), postdiv outputs for selected even/odd PLL paths, many `clk_rcg2` sources for CAMNOC, CCI, CPHY RX, CRE, CSIPHY timers, CSID, AHB, ICP, IFE lite, IPE, JPEG, OFE, QDSS, TFE, and XO, and many `clk_branch` gates consuming those sources. Power domains are `cam_cc_titan_top_gdsc`, `cam_cc_ipe_0_gdsc`, `cam_cc_ofe_gdsc`, and `cam_cc_tfe_0/1/2_gdsc`. The descriptor also exports reset maps and critical CBCRs. Probe is `cam_cc_kaanapali_probe()` calling `qcom_cc_probe()`.

### Control Flow, State, And Persistence
The file is generated-style static data. PLL configs establish root camera frequencies from TCXO, postdividers expose even/odd outputs, parent maps connect RCGs to PLL outputs, frequency tables constrain supported functional rates, branch clocks gate each hardware leaf, GDSCs describe power-domain topology under Titan top, resets map BCR offsets, and the `qcom_cc_desc` ties everything to a fast regmap up to `0x2601c` with `use_rpm = true`. Runtime state is persisted in camera CC MMIO registers and Linux clock/reset/genpd registrations.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include Kaanapali camera DT bindings, qcom alpha PLL/RCG/branch/reset/GDSC helpers, RPM-aware common clock probing, TCXO/sleep/AHB parents, camera subsystem consumers, reset-controller clients, and generic PM domains. Risks include table-size or binding-ID drift, incorrect PLL calibration values destabilizing camera rates, critical CBCR mistakes gating driver/GDSC/sleep clocks, GDSC parent/flag mistakes breaking power sequencing, and rate-table gaps causing camera pipeline failures. Test signals include provider probe on `qcom,kaanapali-camcc`, camera pipeline streaming through CSIPHY/CSID/TFE/OFE/IPE/JPEG paths, reset control assertions, GDSC on/off transitions, `clk_summary` rate/parent checks for major sources, and unused-clock cleanup preserving critical CBCRs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-kaanapali.c -->
