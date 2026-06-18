# subset-b-001154 research

Grouped research for Qualcomm VIDEO_CC drivers, Ralink/MTMIPS clock/reset drivers, and selected Renesas CPG/MSTP clock files. Each section is source-tree aligned and bounded by reconciliation markers for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sc7280.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sc7280.c

Purpose: This platform driver describes the SC7280 Qualcomm video clock controller. It exports the Video CC PLL, Iris/MVS/MVSC clocks, sleep clock path, and two GDSC power domains through the common Qualcomm clock controller framework.

Important APIs, types, and functions: The file builds `clk_alpha_pll`, `clk_rcg2`, `clk_branch`, `gdsc`, `regmap_config`, and `qcom_cc_desc` tables. `video_cc_sc7280_probe()` maps the MMIO block with `qcom_cc_map()`, configures `video_pll0` with `clk_lucid_pll_configure()`, and registers clocks/GDSCs with `qcom_cc_really_probe()`. It matches `qcom,sc7280-videocc` and uses IDs from `dt-bindings/clock/qcom,videocc-sc7280.h`.

Control flow: Probe maps registers, programs the 400 MHz Lucid PLL configuration, then hands the static descriptor to the Qualcomm CC core. Runtime clock operations are delegated to shared CCF ops: `clk_alpha_pll_lucid_ops`, `clk_rcg2_shared_ops`, `clk_rcg2_ops`, and `clk_branch2_ops`.

State and persistence: State is hardware register state in the Video CC block. `video_pll0_config`, RCG frequency tables, branch enable registers, and GDSC control registers define boot-time programming and later CCF-mediated changes. No filesystem state is persisted.

Dependencies and integration: The driver depends on platform DT, regmap, CCF, Qualcomm `common.c`, alpha PLL, RCG, branch, reset, and GDSC helpers. Video consumers obtain clocks and power domains by DT IDs, especially MVS0 and MVSC codec paths.

Risks: Frequency table entries for Iris all use the same even PLL parent but rely on hardware divider interpretation; bad values can break video performance. GDSC flags differ between MVS0 (`HW_CTRL_TRIGGER`) and MVSC, so power-domain sequencing mistakes can hang video hardware. Always-on or reset handling is absent here, unlike some later SoCs.

Test signals: Build with `CONFIG_COMMON_CLK_QCOM`, boot on SC7280 DT containing the compatible, confirm clocks appear in `/sys/kernel/debug/clk/clk_summary`, exercise Venus/video codec power domains, and check that GDSCs transition without timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sc7280.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sdm845.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sdm845.c

Purpose: This is the SDM845 Video CC provider. It registers a Fabia alpha PLL, a Venus source RCG, debug/QDSS/APB/AHB/AXI/core branch clocks, and three GDSC power domains for Venus and two vcodec engines.

Important APIs, types, and functions: Static tables use `clk_alpha_pll`, `clk_rcg2`, `clk_branch`, `gdsc`, and `qcom_cc_desc`. `video_cc_sdm845_probe()` calls `qcom_cc_map()`, `clk_fabia_pll_configure()`, then `qcom_cc_really_probe()`. The exported clock and GDSC indices come from `qcom,videocc-sdm845.h`.

Control flow: The module platform driver binds to `qcom,sdm845-videocc`. During probe the register block is mapped, `video_pll0` at offset `0x42c` is configured with L/alpha values, and CCF resources are registered. Branch operations later enable or disable CBCRs at fixed offsets such as `0x850`, `0x890`, and `0x9b0`.

State and persistence: Persistent state is Video CC register state and GDSC state. `cxcs` arrays associate GDSCs with clock/control registers, allowing the GDSC layer to manage domain collapse around the relevant clock branches. No software state survives driver unload.

Dependencies and integration: It integrates with Linux platform bus, OF matching, Qualcomm CCF helpers, the GDSC framework, and SDM845 video/venus device tree consumers. There is no reset map in this older driver.

Risks: `BRANCH_VOTED` and `BRANCH_HALT` modes are selected per branch and must match hardware. PLL comments leave even/odd outputs disabled in the parent maps, so accidental consumers of those parents would not work. GDSC `POLL_CFG_GDSCR` and `HW_CTRL_TRIGGER` are sensitive to correct register offsets.

Test signals: Compile-test the driver, boot SDM845, confirm `sdm845-videocc` probes after the MMIO resource is available, inspect clk summary for Venus/vcodec clocks, and run video encode/decode workloads while checking for GDSC timeout or halt-check errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sdm845.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm6350.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm6350.c

Purpose: This driver provides the SM6350 Video CC clock and GDSC description. It exposes a Fabia PLL plus post-divider, Iris clock source, sleep source, video branch clocks, and MVSC/MVS0 GDSCs.

Important APIs, types, and functions: It defines `video_pll0`, `video_pll0_out_even`, two `clk_rcg2` sources, several `clk_branch` gates, and a `qcom_cc_desc`. `video_cc_sm6350_probe()` maps hardware with `qcom_cc_map()`, configures the Fabia PLL with `clk_fabia_pll_configure()`, forces `VIDEO_CC_XO_CLK` on via `qcom_branch_set_clk_en(regmap, 0x7018)`, and calls `qcom_cc_really_probe()`.

Control flow: Binding to `qcom,sm6350-videocc` triggers a single probe path. Parent data indexes expect firmware-supplied `iface`, `bi_tcxo`, and `sleep_clk` inputs. Once registered, CCF rate changes flow through `video_cc_iris_clk_src` and its frequency table, while branch enables operate at their CBCR offsets.

State and persistence: PLL programming, RCG selection/divider fields, branch CBCRs, and GDSC registers hold all state. The always-on XO branch write persists until reset or a later hardware write. No driver-private persistent state is maintained.

Dependencies and integration: Depends on Qualcomm alpha PLL, RCG, branch, regmap, GDSC, and common clock helpers. Video hardware and power-domain consumers reference IDs from `qcom,sm6350-videocc.h`.

Risks: The `F()` macro entries include fractional dividers such as `1.5`; correctness depends on the RCG macro/type supporting that representation in this tree. The always-on XO workaround is hard-coded by address. GDSC flags are leaner than SC7280, so suspend/resume and retention behavior need board validation.

Test signals: Build with the SM6350 binding header, boot a matching DT, verify the XO CBCR remains enabled, check Iris rate requests, and run video playback/codec tests across runtime PM transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm6350.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm7150.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm7150.c

Purpose: This file describes the Qualcomm SM7150 video clock controller. It registers a Fabia PLL, Iris and XO RCG sources, MVS0/MVS1/MVSC branch clocks, and Venus/vcodec GDSCs.

Important APIs, types, and functions: Key objects are `videocc_pll0`, `videocc_iris_clk_src`, `videocc_xo_clk_src`, `clk_branch` instances, `gdsc` definitions, and `videocc_sm7150_desc`. `videocc_sm7150_probe()` uses `qcom_cc_map()`, `clk_fabia_pll_configure()`, `qcom_branch_set_clk_en()` for `VIDEOCC_XO_CLK`, and `qcom_cc_really_probe()`.

Control flow: OF match `qcom,sm7150-videocc` loads the platform driver. Probe maps registers, programs PLL0 at offset `0x42c`, writes the XO CBCR at `0x984` on, then registers the descriptor. Later clock control is fully table-driven through CCF ops.

State and persistence: Hardware registers maintain PLL, RCG, branch, and GDSC state. GDSC `cxcs` arrays bind Venus and vcodec power domains to their core/AXI clock registers. There is no module-level mutable state beyond hardware.

Dependencies and integration: It depends on `dt-bindings/clock/qcom,sm7150-videocc.h`, Qualcomm clock helpers, regmap, platform bus, and the GDSC framework. Consumers include Venus/video codec nodes and any interconnect or power-domain users referencing the exported IDs.

Risks: Parent maps expose PLL main/even/odd as the same `videocc_pll0` hardware, which is a common Qualcomm table pattern but can be confusing when adding new rates. The always-on XO register is literal. GDSC polling and hardware trigger flags must match silicon.

Test signals: Compile, boot SM7150 DT, confirm `videocc-sm7150` probe, inspect video clocks and power domains, verify XO stays enabled, and run video decode/encode while watching clock framework and GDSC logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm7150.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm8150.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm8150.c

Purpose: This SM8150 Video CC driver provides the Trion PLL, Iris source, MVS/MVSC core clocks, reset lines, and three GDSC domains for the video subsystem.

Important APIs, types, and functions: The file uses `devm_pm_runtime_enable()`, `pm_runtime_resume_and_get()`, `qcom_cc_map()`, `clk_trion_pll_configure()`, `regmap_update_bits()`, and `qcom_cc_really_probe()`. It defines `qcom_reset_map` entries for MVSC interface/MVS reset lines and `gdsc` entries for Venus, vcodec0, and vcodec1.

Control flow: Probe enables runtime PM and resumes the device before touching registers. It maps the block, configures the PLL, forces `VIDEO_CC_XO_CLK` on at `0x984`, registers the CC descriptor, then runtime-suspends the device with `pm_runtime_put_sync()`.

State and persistence: Video CC register state is modified during probe and by future CCF operations. Runtime PM controls access around probe. The reset map exposes block-reset bits and an MVSC core clock async reset with delay. No persistent software configuration is stored.

Dependencies and integration: The driver needs platform PM runtime, regmap, Qualcomm reset/GDSC/common helpers, and `qcom,videocc-sm8150.h`. Video devices depend on these clocks and GDSCs to power their codec paths.

Risks: Probe error paths must balance PM runtime references; the driver handles map failure and post-register cleanup with `pm_runtime_put_sync()`. The XO keepalive is a raw register update. Branch set selections are minimal compared to newer MVS drivers, so missing AHB/AXI clocks must be accounted for by hardware design or other providers.

Test signals: Build and boot SM8150, verify PM runtime does not leave the device active after probe, confirm reset controls exist, inspect the always-on XO CBCR, and test video across suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm8150.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm8250.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm8250.c

Purpose: This SM8250 Video CC driver registers two Lucid PLLs, MVS0/MVS1 sources and read-only dividers, core clocks, four GDSCs, and reset controls for CVP/MVS blocks.

Important APIs, types, and functions: It uses `clk_alpha_pll`, `clk_rcg2`, `clk_regmap_div`, `clk_branch`, `gdsc`, `qcom_reset_map`, and `qcom_cc_desc`. `video_cc_sm8250_probe()` enables PM runtime, maps registers, configures both PLLs with `clk_lucid_pll_configure()`, keeps AHB and XO clocks on via `qcom_branch_set_clk_en()`, registers the CC descriptor, and drops the PM runtime reference.

Control flow: The probe path runs only for `qcom,sm8250-videocc`. After PLL setup, clock consumers use RCG tables for MVS0 and MVS1 and fixed hardware dividers for MVS/MVSC branches. Reset users trigger BCR or ARES entries through the Qualcomm reset framework.

State and persistence: PLL config, branch state, read-only divider values, reset bits, and GDSC power state are all in hardware registers. The driver does not maintain runtime caches except static object tables.

Dependencies and integration: It depends on PM runtime, regmap, Qualcomm alpha PLL/RCG/divider/branch/GDSC/reset helpers, and DT clock/reset IDs from `qcom,videocc-sm8250.h`.

Risks: `clk_regmap_div_ro_ops` means divider values must be programmed by firmware or hardware reset defaults; the driver cannot correct bad divider state. Hard-coded keepalive CBCR offsets must remain valid. GDSC hierarchy is flat here, unlike later drivers with parented MVS domains.

Test signals: Compile-test, boot SM8250, check AHB/XO clocks remain enabled, request supported MVS rates, verify reset controls with video firmware bring-up, and watch for PM runtime imbalance or GDSC failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm8250.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm8350.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm8350.c

Purpose: This driver describes SM8350 and SC8280XP Video CC hardware. It provides AHB/XO/sleep sources, two Lucid 5LPE PLLs, MVS0/MVS1 clocks and dividers, reset lines, and four retained GDSCs.

Important APIs, types, and functions: The driver uses PM runtime, `qcom_cc_map()`, `clk_lucid_pll_configure()`, `qcom_branch_set_clk_en()`, `qcom_cc_really_probe()`, and OF compatibility checks. Static descriptors include `video_cc_sm8350_clocks`, `video_cc_sm8350_resets`, `video_cc_sm8350_gdscs`, and `video_cc_sm8350_desc`.

Control flow: Probe resumes the device. If compatible is `qcom,sc8280xp-videocc`, it mutates sleep/XO register offsets, PLL VCO tables, and MVS frequency tables before mapping. It then maps registers, configures two PLLs, enables AHB and XO CBCRs, registers clocks/resets/GDSCs, and releases PM runtime.

State and persistence: Register state holds all live behavior. The static driver tables are intentionally mutated for SC8280XP before registration, so probe order matters and the module is not written for independent simultaneous variants in one kernel instance. GDSCs use `RETAIN_FF_ENABLE`, and MVS domains have hardware-triggered power state.

Dependencies and integration: Integrates with DT compatibles `qcom,sm8350-videocc` and `qcom,sc8280xp-videocc`, Qualcomm clock helpers, GDSC, reset framework, PM runtime, and video/CVP consumers.

Risks: Variant mutation of global static objects is the main maintainability risk. Wrong compatible selection changes register offsets and VCO/frequency ceilings. PM runtime references must stay balanced. Read-only dividers depend on hardware defaults.

Test signals: Boot both SM8350 and SC8280XP DTs, confirm variant-specific clocks and CBCR offsets, inspect reset IDs from `qcom,sm8350-videocc.h`, and run video workloads at high MVS rates including suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm8350.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm8450.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm8450.c

Purpose: This Video CC driver covers SM8450 and SM8475. It registers two Lucid EVO/OLE PLLs, MVS0/MVS1 RCGs, read-only dividers, branch clocks, nested GDSCs, reset controls, and critical CBCRs through the RPM-aware Qualcomm CC path.

Important APIs, types, and functions: Static data includes `clk_alpha_pll` with `.config` pointers, `clk_regmap_div`, `clk_branch`, `gdsc`, `qcom_reset_map`, `qcom_cc_driver_data`, and `qcom_cc_desc`. `video_cc_sm8450_probe()` switches PLL register layouts and configs for `qcom,sm8475-videocc`, then calls `qcom_cc_probe()`.

Control flow: The generic `qcom_cc_probe()` path handles mapping, PLL/critical clock setup from `driver_data`, and descriptor registration. No manual PM runtime handling appears in this file. Variant handling happens before the common probe by changing PLL `regs` and `config` pointers.

State and persistence: Hardware registers hold PLL, RCG, divider, branch, reset, and GDSC state. The descriptor sets `.use_rpm = true`, so integration includes RPM-managed sequencing. Critical CBCRs keep AHB, XO, and sleep clocks on.

Dependencies and integration: Depends on `qcom,sm8450-videocc.h`, Qualcomm clock core data-driver support, alpha PLL, RCG, divider, branch, reset, GDSC, and platform bus. Video codec firmware depends on the MVS/MVSC power-domain hierarchy.

Risks: SM8475 support mutates static PLL fields. If a future multi-instance platform binds both variants, state could collide. The driver relies on common code honoring `qcom_cc_driver_data` critical CBCR and alpha PLL lists. GDSC parent relationships must match hardware power collapse order.

Test signals: Compile, boot SM8450 and SM8475 targets, verify `use_rpm` probe path configures PLLs, confirm critical clocks stay enabled, check reset delays, and exercise both MVS0 and MVS1 video paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm8450.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm8550.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm8550.c

Purpose: This driver supports SM8550, SM8650, and X1E80100 Video CC. It exports two Lucid OLE PLLs, MVS0/MVS1 RCGs, optional shift/XO clocks, dividers, GDSCs, resets, and critical CBCRs.

Important APIs, types, and functions: It defines variant frequency tables, `clk_alpha_pll` configs, `clk_rcg2`, `clk_regmap_div`, `clk_branch`, four `gdsc`s, `qcom_reset_map`, `qcom_cc_driver_data`, and `qcom_cc_desc`. `video_cc_sm8550_probe()` checks compatibles and mutates PLL L/alpha values, RCG tables, clock-array entries, and critical CBCR tables before invoking `qcom_cc_probe()`.

Control flow: `qcom_cc_probe()` performs common mapping and registration using `.use_rpm = true` and `driver_data`. For X1E80100 only PLL values and MVS tables are changed. For SM8650, shift clocks and `video_cc_xo_clk_src` are added to the exported clock array and the sleep critical CBCR offset changes.

State and persistence: Static tables are modified during probe for variant support. Hardware state includes PLL, RCG, divider, branch, GDSC, and reset registers. Critical clocks are maintained by common Qualcomm CC code rather than manual writes here.

Dependencies and integration: Integrates with `qcom,sm8550-videocc`, `qcom,sm8650-videocc`, and `qcom,x1e80100-videocc` DT compatibles, Qualcomm RPM-aware CC support, reset/GDSC frameworks, and video/CVP consumers.

Risks: Variant-specific mutation is broad: frequency tables, PLL configs, clock exports, and critical CBCRs can diverge. The base clock array intentionally has `VIDEO_CC_XO_CLK_SRC = NULL`, so consumers must not request it except on variants that install it. Reset delays are hardware-sensitive.

Test signals: Boot each compatible, verify exported clock count and NULL slots, check SM8650 shift clocks appear, confirm critical CBCRs, run high-rate video tests, and validate reset/GDSC sequencing under suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm8550.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm8750.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm8750.c

Purpose: This is the SM8750 Video CC driver. It exposes a Taycan ELU PLL, AHB/XO/sleep sources, MVS0/MVS0C clocks including freerun and shift branches, two GDSCs, reset controls, and critical CBCRs.

Important APIs, types, and functions: It uses `clk_alpha_pll_taycan_elu_ops`, `clk_rcg2`, `clk_regmap_div_ro_ops`, regular `clk_branch`, `clk_mem_branch` with `clk_branch2_mem_ops`, `gdsc`, `qcom_reset_map`, `qcom_cc_driver_data`, and `qcom_cc_desc`. `clk_sm8750_regs_configure()` programs shifter-done fields and an extra register bit through `regmap_update_bits()`. `video_cc_sm8750_probe()` calls `qcom_cc_probe()`.

Control flow: The driver is registered at `subsys_initcall`, earlier than normal module platform registration. Common Qualcomm CC code maps and registers resources, configures the alpha PLL and critical clocks from `driver_data`, and invokes the custom register configuration callback.

State and persistence: Hardware register state includes PLL programming, RCG/divider state, branch memory enable/ack bits, GDSC state, reset bits, and callback-programmed delay accumulator fields. The module has no dynamic state beyond static descriptors.

Dependencies and integration: Requires `qcom,sm8750-videocc.h`, Qualcomm alpha PLL/RCG/divider/mux/branch memory helpers, GDSC, reset, platform bus, and RPM-aware common CC support.

Risks: This newer driver uses memory branch semantics for `video_cc_mvs0_freerun_clk`; ack polarity and masks must match hardware. Custom register writes are unguarded by variant checks. `subsys_initcall` changes probe timing relative to dependencies. Reset entries use compact initializer forms, increasing the need to verify bit positions.

Test signals: Boot SM8750, verify early platform driver registration, inspect critical AHB/XO/sleep clocks, request MVS0/MVS0C clocks and freerun paths, and validate register callback effects through vendor debug or hardware behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm8750.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ralink/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/ralink/Kconfig

Purpose: This Kconfig file declares build switches for Ralink/MediaTek MIPS clock drivers in this directory.

Important APIs, types, and functions: It defines `CONFIG_CLK_MT7621` and `CONFIG_CLK_MTMIPS`. Both are `bool` symbols gated by `RALINK || COMPILE_TEST`, and both select `MFD_SYSCON` because the drivers obtain SoC system-controller registers through syscon/regmap.

Control flow: Kconfig selection determines whether the corresponding objects are compiled by the local Makefile. `CLK_MT7621` builds the MT7621-specific clock/reset provider, while `CLK_MTMIPS` builds the shared provider for RT2880/RT305x/RT3352/RT3883/RT5350/MT7620/MT76x8 class SoCs.

State and persistence: No runtime state. The file controls kernel configuration state and therefore object inclusion in built kernels.

Dependencies and integration: Integrates with top-level clock Kconfig inclusion and the local Makefile. The selected drivers also require reset-controller and clk-provider APIs in code, but this Kconfig only explicitly selects syscon support.

Risks: Because the symbols are bools rather than tristates, drivers are built in when selected. Missing dependency selections here can surface as link errors in unusual COMPILE_TEST configurations. Separating MT7621 from MTMIPS is important because their DT compatibles and clock topologies differ.

Test signals: Run `make ARCH=mips allmodconfig` or relevant Ralink defconfig, ensure both symbols select cleanly under COMPILE_TEST, and verify the Makefile emits exactly `clk-mt7621.o` or `clk-mtmips.o` for the matching symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ralink/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ralink/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/ralink/Makefile

Purpose: This Makefile maps Ralink clock Kconfig symbols to object files.

Important APIs, types, and functions: It has two object assignments: `obj-$(CONFIG_CLK_MT7621) += clk-mt7621.o` and `obj-$(CONFIG_CLK_MTMIPS) += clk-mtmips.o`.

Control flow: During kernel build, kbuild expands the two `obj-$()` expressions based on Kconfig values. Enabled symbols compile the corresponding clock/reset provider into the built-in object list for this directory.

State and persistence: No runtime state. It affects build graph state only.

Dependencies and integration: This file is consumed by kbuild after the parent clock Makefile descends into `drivers/clk/ralink`. It depends on symbol definitions in the adjacent Kconfig and on the two C files existing with matching names.

Risks: The simplicity reduces risk. The main risk is stale symbol/object naming if either C file or Kconfig symbol is renamed. Because these drivers use `arch_initcall` and `CLK_OF_DECLARE_DRIVER`, build inclusion directly affects early boot clock availability.

Test signals: Configure each symbol independently and run `make drivers/clk/ralink/`. Inspect build logs or `scripts/Makefile.build` output to ensure only the selected object compiles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ralink/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ralink/clk-mt7621.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ralink/clk-mt7621.c

Purpose: This driver provides MT7621 clock and reset support. It has an early clock provider for boot-critical `xtal`, `cpu`, and `bus`, then a platform-driver phase that registers fixed clocks, gated peripheral clocks, a full onecell provider, and a reset controller.

Important APIs, types, and functions: Key types are `mt7621_clk_priv`, `mt7621_clk`, `mt7621_fixed_clk`, `mt7621_gate`, and `mt7621_rst`. Rate callbacks include `mt7621_xtal_recalc_rate()`, `mt7621_cpu_recalc_rate()`, and `mt7621_bus_recalc_rate()`. Registration functions include `mt7621_register_early_clocks()`, `mt7621_register_fixed_clocks()`, `mt7621_register_gates()`, `mt7621_reset_init()`, and `mt7621_clk_probe()`.

Control flow: `CLK_OF_DECLARE_DRIVER()` registers early clocks for `mediatek,mt7621-sysc`, leaving later clock IDs as `-EPROBE_DEFER`. `arch_initcall()` registers the platform driver, whose probe reuses early clock handles, registers fixed-rate clocks and gates, adds the managed provider, and registers reset ops.

State and persistence: `sysc` and `memc` regmaps expose SoC registers. CPU rate is derived from clock selection, current divider/fraction fields, and MEMC CPU PLL fields. Gate state is controlled by `SYSC_REG_CLKCFG1`. Reset state is `SYSC_REG_RESET_CTRL`. The static `mt7621_clk_early` array bridges early and platform phases.

Dependencies and integration: Depends on syscon/regmap, CCF, reset-controller, DT bindings for MT7621 clock/reset IDs, and the `ralink,memctl` phandle. Consumers reference onecell clock IDs and reset IDs in DT.

Risks: `mt7621_cpu_recalc_rate()` divides by `ffiv`; invalid hardware values could fault. All peripheral gates are marked `CLK_IS_CRITICAL` to preserve legacy drivers, which can hide unused-clock issues. Early and late providers must agree on clock array ordering.

Test signals: Boot MT7621, confirm early console/timer clocks before platform probe, inspect onecell clock IDs after `arch_initcall`, test reset controller phandles except disallowed system reset, and verify CPU/bus rates against hardware strap values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ralink/clk-mt7621.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ralink/clk-mtmips.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ralink/clk-mtmips.c

Purpose: This shared MTMIPS/Ralink driver provides early clock providers and reset controller support for RT2880, RT3050/3052, RT3352, RT3883, RT5350, MT7620, MT7628, and MT7688 style system-controller blocks.

Important APIs, types, and functions: It defines data-driven `mtmips_clk_data` tables containing base, fixed, factor, and peripheral clocks. Rate callbacks decode SoC-specific system registers, including `rt2880_cpu_recalc_rate()`, `rt305x_cpu_recalc_rate()`, `rt3352_cpu_recalc_rate()`, `rt3883_bus_recalc_rate()`, `rt5350_xtal_recalc_rate()`, `mt7620_pll_recalc_rate()`, `mt7620_cpu_recalc_rate()`, and `mt76x8_cpu_recalc_rate()`. Main paths are `mtmips_clk_init()` and `mtmips_clk_probe()`.

Control flow: `CLK_OF_DECLARE_DRIVER()` runs `mtmips_clk_init()` early for each sysc compatible. It selects the matching `mtmips_clk_data`, optionally adjusts MT7620 CPU bus fractional dividers for USB behavior, registers base/fixed/factor/peripheral clocks, and publishes a onecell provider. Separately, an `arch_initcall()` platform driver registers reset-controller operations for the same compatibles.

State and persistence: Clock rates are computed from syscon registers and fixed tables. Peripheral clocks are critical pass-through clocks. Reset state is controlled by `SYSC_REG_RESET_CTRL`; reset ID 0 is rejected. No persistent software state survives boot.

Dependencies and integration: Depends on syscon/regmap, CCF, reset-controller, OF compatibles, and legacy Ralink DT clock names such as device-address-derived peripheral clocks. Consumers often use named clocks rather than numeric bindings.

Risks: The driver intentionally uses `BUG()` for impossible strap values in several rate callbacks, making bad emulation or corrupted register state fatal. There is a spelling inconsistency in `pherip` names but it is internal. MT7620 register writes during init alter bus fractional dividers globally.

Test signals: Boot representative SoCs or QEMU/device-tree tests, compare reported rates to datasheets, verify USB on MT7620 after divider adjustment, confirm reset phandles reject ID 0, and check no duplicate provider registration warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ralink/clk-mtmips.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/Kconfig

Purpose: This Kconfig file defines the Renesas common clock driver selection matrix. It maps architecture symbols to SoC clock providers and family helper libraries.

Important APIs, types, and functions: It declares the umbrella `CLK_RENESAS` bool and many SoC symbols such as `CLK_EMEV2`, `CLK_RZA1`, `CLK_R7S9210`, `CLK_R8A73A4`, `CLK_R8A7740`, `CLK_R8A7742`, `CLK_R8A7743`, `CLK_R8A7745`, `CLK_R8A77470`, `CLK_R8A7778`, `CLK_R8A7779`, and `CLK_SH73A0`. It also declares family symbols `CLK_RCAR_CPG_LIB`, `CLK_RCAR_GEN2_CPG`, `CLK_RENESAS_CPG_MSSR`, `CLK_RENESAS_CPG_MSTP`, `CLK_RENESAS_DIV6`, and `CLK_RENESAS_VBATTB`.

Control flow: When `ARCH_RENESAS` or COMPILE_TEST selects `CLK_RENESAS`, architecture-specific symbols select SoC drivers and helper families. For example, RZ/G1 SoCs select `CLK_RCAR_GEN2_CPG`, which selects `CLK_RENESAS_CPG_MSSR`; R-Mobile/legacy SoCs select MSTP and sometimes DIV6.

State and persistence: No runtime state. It controls kernel configuration and whether drivers are built.

Dependencies and integration: Integrates with the local Makefile and broader arch Kconfig. Some family symbols select reset-controller or CPG libraries required by their implementation files.

Risks: This file is a dependency hub; missing `select` lines can cause link failures or absent boot clocks. Because many symbols are bools, built-in ordering matters for early OF clock declarations. Formatting inconsistencies exist around some RZV2H entries but do not change semantics.

Test signals: Run `make ARCH=arm64 allmodconfig` and Renesas defconfigs, verify each selected object appears in `drivers/clk/renesas/`, and confirm COMPILE_TEST builds without missing helper symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/Makefile

Purpose: This Makefile maps Renesas clock Kconfig symbols to SoC-specific and family helper object files.

Important APIs, types, and functions: It contains object rules for the selected files in this work item: `clk-emev2.o`, `clk-rz.o`, `r7s9210-cpg-mssr.o`, `clk-r8a73a4.o`, `clk-r8a7740.o`, `r8a7742-cpg-mssr.o`, `r8a7743-cpg-mssr.o`, `r8a7745-cpg-mssr.o`, `r8a77470-cpg-mssr.o`, `clk-r8a7778.o`, `clk-r8a7779.o`, `clk-sh73a0.o`, plus helper objects `renesas-cpg-mssr.o`, `clk-mstp.o`, `clk-div6.o`, and `clk-vbattb.o`.

Control flow: Kbuild evaluates `obj-$(CONFIG_...)` lines to include only objects selected by Kconfig. Some symbols map multiple SoCs to shared objects, such as `CLK_R8A77960` and `CLK_R8A77961` both using `r8a7796-cpg-mssr.o`.

State and persistence: No runtime state. Build-time state controls which early `CLK_OF_DECLARE` providers and platform drivers exist in the kernel.

Dependencies and integration: Closely tied to `drivers/clk/renesas/Kconfig`, DT compatible tables in central CPG-MSSR code, and exported `cpg_mssr_info` symbols from SoC files.

Risks: Object name mismatches or missing helper object selection can break early clock support. Because many Renesas clock drivers are built-in early providers, omitted objects can produce boot-time clock lookup failures rather than obvious runtime module-load errors.

Test signals: Configure each symbol in isolation or through defconfig, run `make drivers/clk/renesas/`, and inspect that helper objects are built when family symbols are selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-div6.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-div6.c

Purpose: This file implements Renesas CPG DIV6 clocks, which are 6-bit divider clocks with optional parent selection and clock-stop control. It supports both direct DT registration and internal registration by Renesas CPG drivers.

Important APIs, types, and functions: The main type is `struct div6_clock`, with CCF ops in `cpg_div6_clock_ops`. Important functions include enable/disable/is-enabled, `cpg_div6_clock_determine_rate()`, `cpg_div6_clock_set_rate()`, parent get/set helpers, `cpg_div6_clock_notifier_call()`, exported `cpg_div6_register()`, and OF init `cpg_div6_clock_init()`.

Control flow: `CLK_OF_DECLARE()` binds `renesas,cpg-div6-clock` nodes. The init path counts parents, maps the register, reads parent names, calls `cpg_div6_register()`, and adds a simple clock provider. Internal callers can pass a notifier chain for resume handling.

State and persistence: The driver caches the divisor in `clock->div` because stopping a DIV6 clock can require writing the divisor field. Hardware state is the divisor bits, CKSTP bit, and optional source-select field. A PM notifier restores enabled/disabled state on resume, but does not restore multi-parent source selection.

Dependencies and integration: Depends on CCF, OF address mapping, bitfield helpers, PM notifiers, and `clk-div6.h`. Other Renesas CPG drivers use this helper for SD/MMC and similar clock outputs.

Risks: Parent filtering mutates the `parent_names` array supplied by the caller. Multi-parent resume is explicitly incomplete. Invalid parent counts return `-EINVAL`. Writes are not protected by a spinlock in this helper, so callers rely on CCF serialization and hardware tolerance.

Test signals: Register DT DIV6 nodes with 1, 4, and 8 parents, test rate rounding and parent switching, suspend/resume with enabled and disabled clocks, and verify stopped clocks re-enable with the cached divider.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-div6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-div6.h -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-div6.h

Purpose: This header declares the internal Renesas DIV6 registration helper.

Important APIs, types, and functions: It exposes `struct clk *cpg_div6_register(const char *name, unsigned int num_parents, const char **parent_names, void __iomem *reg, struct raw_notifier_head *notifiers);`. The include guard is `__RENESAS_CLK_DIV6_H__`.

Control flow: SoC or family CPG drivers include this header when they need to create DIV6 clocks from already-mapped CPG registers instead of relying on a standalone DT node.

State and persistence: No state. The function it declares creates state in `clk-div6.c`.

Dependencies and integration: The declaration references `struct clk`, `void __iomem`, and `struct raw_notifier_head`, relying on includers or prior headers for full declarations. It integrates with Renesas CPG helper code and the Linux CCF.

Risks: This is a minimal internal header. API changes must be synchronized with all Renesas CPG users. Because the helper accepts mutable `parent_names`, callers should not pass const storage they cannot tolerate being compacted by the implementation.

Test signals: Compile all Renesas drivers that include the header, especially Gen2/legacy CPG files using DIV6 registration, and verify no prototype mismatch warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-div6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-emev2.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-emev2.c

Purpose: This legacy EMMA Mobile EV2 clock file initializes the SMU block, deasserts selected peripheral resets, and registers SMU divider and gate clocks from device tree.

Important APIs, types, and functions: It uses global `smu_base`, `DEFINE_SPINLOCK(lock)`, `emev2_smu_write()`, `emev2_smu_init()`, `emev2_smu_clkdiv_init()`, and `emev2_smu_gclk_init()`. Clock registration uses `clk_register_divider()` and `clk_register_gate()`.

Control flow: `CLK_OF_DECLARE()` handlers bind `renesas,emev2-smu-clkdiv` and `renesas,emev2-smu-gclk`. Each clock init lazily calls `emev2_smu_init()` if `smu_base` is unset. SMU init finds `renesas,emev2-smu`, maps its registers, programs the STI timer clock, and deasserts UART/IIC resets.

State and persistence: The mapped `smu_base` is global init-time state. Hardware reset and clock-select registers persist until reset. The spinlock protects divider/gate clock register updates.

Dependencies and integration: Depends on OF matching, OF address mapping, CCF divider/gate helpers, and EMEV2 DT nodes. It predates modern reset-controller modeling and directly writes reset registers.

Risks: Uses `BUG_ON()` for missing SMU node or map failures, which can panic the kernel on malformed DT. Global `smu_base` assumes a single SMU. Reset deassertion is hard-coded and not exposed through reset-controller APIs.

Test signals: Boot EMEV2 DT, verify the SMU node is present, confirm divider/gate providers register, check UART/IIC/STI devices leave reset, and compile-test with `CLK_EMEV2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-emev2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-mstp.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-mstp.c

Purpose: This file implements legacy Renesas MSTP module-stop gate clocks and a companion always-on generic PM domain that attaches device clocks through PM clock helpers.

Important APIs, types, and functions: Core types are `mstp_clock_group` and `mstp_clock`. Key functions are `cpg_mstp_clock_endisable()`, `cpg_mstp_clock_register()`, `cpg_mstp_clocks_init()`, `cpg_mstp_attach_dev()`, `cpg_mstp_detach_dev()`, `cpg_mstp_add_clk_domain()`, and `cpg_mstp_pd_init_provider()`.

Control flow: `CLK_OF_DECLARE()` handles `renesas,cpg-mstp-clocks`, maps SMSTPCR and optional MSTPSR registers, parses output names and clock indices, registers per-bit gate clocks, and exposes a onecell provider. Enabling clears the module-stop bit and optionally polls MSTPSR until the module reports enabled.

State and persistence: Each group holds MMIO pointers, a spinlock, optional 8-bit mode, onecell data, and clock pointers. Hardware SMSTPCR/MSTPSR registers hold module-stop state. PM domain globals temporarily store the DT node and genpd until `postcore_initcall()` publishes the provider.

Dependencies and integration: Depends on CCF, OF, IO polling, PM clock, PM domain, and `linux/clk/renesas.h` declarations used by legacy SoC CPG files. Devices get module clocks either directly or via the MSTP PM domain attach path.

Risks: Enable polling timeout is only 10 microseconds, so slow hardware or wrong status wiring fails. `intc-sys` is marked critical by name. 8-bit support is special-cased for RZ/A1. PM-domain globals allow one pending provider.

Test signals: Boot legacy Renesas SoCs with MSTP DT nodes, enable/disable module clocks, validate MSTPSR polling, check PM domain attach adds the first MSTP clock to devices, and confirm `intc-sys` is never disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-mstp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-r8a73a4.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-r8a73a4.c

Purpose: This legacy CPG provider registers core clocks for the Renesas R-Mobile APE6 (`r8a73a4`) SoC.

Important APIs, types, and functions: The file defines `struct r8a73a4_cpg`, DIV4 clock tables, PLL register offsets, `r8a73a4_cpg_register_clock()`, and `r8a73a4_cpg_clocks_init()`. It registers fixed-factor clocks and divider-table clocks through CCF helpers.

Control flow: `CLK_OF_DECLARE()` binds `renesas,r8a73a4-cpg-clocks`. Init counts `clock-output-names`, allocates onecell data, maps the CPG registers, then iterates names and dispatches each through the string-based clock registration function.

State and persistence: Hardware CPG registers select the main clock parent/divider, PLL multipliers/dividers, Z/Z2 ratios, and DIV4 settings. The driver stores a spinlock for divider writes and an allocated onecell clock array for provider lookup.

Dependencies and integration: Depends on OF, CCF, IO mapping, spinlocks, and legacy Renesas clock declarations. It selects `CLK_RENESAS_CPG_MSTP` and `CLK_RENESAS_DIV6` via Kconfig for related module clocks.

Risks: Unknown clock names return `-EINVAL`, so DT output names must match the string dispatcher. Several PLL enable bits are noted as TODO/XXX and PLLs are modeled as fixed-factor clocks. Allocation failures intentionally leak partial state because early boot cannot recover cleanly.

Test signals: Boot an R8A73A4 DT, confirm all listed output names register, compare PLL and divider rates to hardware registers, test DIV4 rate changes, and ensure BSC/`zb_clk` integration with MSTP PM domain works.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-r8a73a4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-r8a7740.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-r8a7740.c

Purpose: This file registers core CPG clocks for the Renesas R-Mobile A1 (`r8a7740`) SoC.

Important APIs, types, and functions: It defines `struct r8a7740_cpg`, DIV4 clock metadata, divider tables, global `cpg_mode`, `r8a7740_cpg_register_clock()`, and `r8a7740_cpg_clocks_init()`. It registers fixed-factor and divider-table clocks.

Control flow: `CLK_OF_DECLARE()` binds `renesas,r8a7740-cpg-clocks`. Init reads `renesas,mode`, counts output names, maps CPG registers, and registers each named clock. Clock registration chooses parent, multiplier, divider, and optional register/shift by name.

State and persistence: `cpg_mode` is init-only software state from DT, used to select `r`, `system`, and other clock relationships. Hardware registers provide PLLC multipliers, USB clock source/divider, and DIV4 settings. A spinlock serializes divider writes.

Dependencies and integration: Depends on legacy Renesas CPG/MSTP/DIV6 support, OF, IO mapping, CCF, and DT output-name ordering.

Risks: Missing `renesas,mode` only warns, potentially producing wrong clock topology. PLLs are modeled as fixed factors even though hardware is configurable. String-based dispatch makes DT spelling critical. Some allocation failure paths intentionally do not clean up.

Test signals: Boot R8A7740, verify warning-free mode parsing, compare `system`, `pllc*`, USB, and DIV4 rates with datasheet straps, inspect onecell provider indices, and test module clocks that consume these parents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-r8a7740.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-r8a7778.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-r8a7778.c

Purpose: This legacy CPG provider registers R-Car M1A (`r8a7778`) core clocks derived from MODEMR strap bits.

Important APIs, types, and functions: The file defines PLL multiplier tables `r8a7778_rates`, divider table `r8a7778_divs`, init-only mode indexes, `r8a7778_cpg_register_clock()`, and `r8a7778_cpg_clocks_init()`.

Control flow: `CLK_OF_DECLARE()` binds `renesas,r8a7778-cpg-clocks`. Init reads mode pins via `rcar_rst_read_mode_pins()`, asserts expected mode bit 19, computes rate/divider indexes, allocates onecell data, registers each output name as a fixed-factor clock, adds the provider, and calls `cpg_mstp_add_clk_domain()`.

State and persistence: CPG mode indexes are init-only globals. Runtime clock state is simple fixed-factor CCF state derived from strap pins. The MSTP PM domain is installed for module clock management.

Dependencies and integration: Depends on `rcar-rst` mode-pin reading, OF, CCF, Renesas MSTP domain support, and DT output names.

Risks: `BUG_ON(!(mode & BIT(19)))` can panic on invalid mode data. Missing or misspelled clock names fail individually. Rates are fixed after init and cannot reflect dynamic PLL changes.

Test signals: Boot R8A7778 hardware, verify mode-pin table selection, compare `plla`, `pllb`, and divided clocks against straps, ensure MSTP PM domain provider appears, and compile-test with `CLK_R8A7778`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-r8a7778.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-r8a7779.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-r8a7779.c

Purpose: This file registers legacy R-Car H1 (`r8a7779`) CPG core clocks using fixed factors selected from mode pins.

Important APIs, types, and functions: It defines `struct cpg_clk_config`, `cpg_clk_configs`, `cpg_plla_mult`, `r8a7779_cpg_register_clock()`, and `r8a7779_cpg_clocks_init()`. It includes `dt-bindings/clock/r8a7779-clock.h` to size the clock array.

Control flow: `CLK_OF_DECLARE()` binds `renesas,r8a7779-cpg-clocks`. Init reads mode pins, allocates onecell data, selects PLLA multiplier and divider config, registers each named output as a fixed-factor clock, adds a provider, and installs the MSTP clock PM domain.

State and persistence: Mode pins determine static clock factors. No dynamic clock programming is performed. Provider state is the allocated clock pointer array.

Dependencies and integration: Depends on `rcar_rst_read_mode_pins()`, OF output names, CCF fixed-factor clocks, and MSTP helper functions. Module stop clocks use these core parents.

Risks: The onecell allocation uses `CPG_NUM_CLOCKS` while `clk_num` is set from DT output count, so DT must remain consistent with binding expectations. Unsupported output names return errors. Clock model is fixed-factor only.

Test signals: Boot R8A7779, verify rates for `plla`, `z`, `zs`, `s`, `s1`, `p`, `b`, and `out`, confirm module devices attach through MSTP PM domain, and compile-test `CLK_R8A7779`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-r8a7779.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-rz.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-rz.c

Purpose: This legacy RZ/A1 CPG provider registers the PLL, I, and G clocks and installs the MSTP PM domain for module clocks.

Important APIs, types, and functions: Key functions are `rz_cpg_read_mode_pins()`, `rz_cpg_register_clock()`, and `rz_cpg_clocks_init()`. It uses hard-coded PPR0 and PIBC0 addresses to read MD_CLK from pin state.

Control flow: `CLK_OF_DECLARE()` binds `renesas,rz-cpg-clocks`. Init counts output names, maps the CPG register block if possible, registers each named clock, adds a onecell provider, then calls `cpg_mstp_add_clk_domain()`. `pll` registration reads mode pins and chooses the external parent and multiplier.

State and persistence: Hardware CPG registers hold FRQCR/FRQCR2 dividers for I and G clocks. Mode pin reads are performed through temporary ioremaps. The driver treats I/G as fixed current-speed factors due to known non-integer constraints.

Dependencies and integration: Depends on OF, CCF, IO mapping, Renesas MSTP helpers, and RZ/A1 DT output names. Module clocks depend on this provider for parent rates.

Risks: `BUG_ON()` is used if mode-pin ioremaps fail. Non-PLL clocks fail with `-ENXIO` if CPG register mapping fails, though the system may still boot with PLL only. I/G modeling is approximate and not suitable for dynamic scaling.

Test signals: Boot RZ/A1, verify MD_CLK parent choice, compare PLL/I/G rates against FRQCR values, ensure MSTP power domain registers, and test timer/peripheral module clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-rz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-sh73a0.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-sh73a0.c

Purpose: This file registers SH-Mobile AG5 (`sh73a0`) core CPG clocks including main, PLL, DSI PHY, Z, and DIV4-derived clocks.

Important APIs, types, and functions: It defines `struct sh73a0_cpg`, DIV4 and Z divider tables, `sh73a0_cpg_register_clock()`, and `sh73a0_cpg_clocks_init()`. It uses `clk_register_fixed_factor()` and `clk_register_divider_table()`.

Control flow: `CLK_OF_DECLARE()` binds `renesas,sh73a0-cpg-clocks`. Init counts outputs, allocates onecell data, maps CPG registers, writes known values to SDHI clock control registers, then registers each output name.

State and persistence: Hardware registers determine main parent, PLL enable/multiplier state, DSI PHY factors, and divider fields. The init writes to SD0/SD1/SD2 clock control registers persist as known SDHI defaults. A spinlock protects divider table changes.

Dependencies and integration: Depends on OF, CCF, IO mapping, spinlocks, and Renesas MSTP/DIV6 support selected by Kconfig. Consumers rely on DT output-name ordering.

Risks: PLL handling models configurable PLLs as fixed factors. Unsupported names fail. SDHI register writes are board-wide policy embedded in the provider. Allocation failure paths intentionally leak.

Test signals: Boot SH73A0, compare CPG rates and SDHI initial state with datasheet expectations, test DSI PHY clock derivation, inspect onecell provider outputs, and run MSTP module-clock attach tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-sh73a0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-vbattb.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-vbattb.c

Purpose: This platform driver registers clocks for the Renesas VBATTB block, including the low-speed crystal gate, bypass fixed factor, mux, and critical VBATTCLK output for RTC counter use.

Important APIs, types, and functions: The driver defines `struct vbattb_clk`, load-capacitance constants, `vbattb_clk_validate_load_capacitance()`, cleanup action `vbattb_clk_action()`, and `vbattb_clk_probe()`. It uses devm CCF helpers for gate, fixed-factor, mux, and parent-hw gate clocks.

Control flow: Probe reads `quartz-load-femtofarads` with a 4 pF default, validates it, allocates clock data, maps MMIO, enables PM runtime, obtains and deasserts a shared reset, registers a cleanup action, creates four clocks, programs oscillator load capacitance, marks `vbattclk` critical, and adds an OF onecell provider.

State and persistence: Hardware state includes VBATTB registers for source select, oscillator stop, oscillator output enable, and load capacitance. Runtime PM and reset state are active while the provider exists. Cleanup asserts reset, runtime-suspends, and removes the clock provider.

Dependencies and integration: Depends on platform bus, PM runtime, reset framework, CCF devm helpers, OF, and `renesas,r9a08g045-vbattb.h`. RTC consumers depend on `VBATTB_VBATTCLK`.

Risks: The cleanup error message says "de-assert" while asserting reset, a minor diagnostic bug. Invalid capacitance values fail probe. `vbattclk` is critical, so it will not be disabled by unused-clock cleanup. Ordering of capacitance programming before output registration matters.

Test signals: Probe with each supported capacitance, check invalid DT value fails, verify reset/runtime PM balance on unbind, inspect four exported clocks, and confirm RTC remains functional through unused-clock cleanup and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-vbattb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r7s9210-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r7s9210-cpg-mssr.c

Purpose: This file describes the RZ/A2 (`r7s9210`) CPG/MSSR clock topology, including early timer clocks, core clocks, module clocks, and custom RZ/A2 clock registration.

Important APIs, types, and functions: It defines `r7s9210_early_core_clks`, `r7s9210_early_mod_clks`, `r7s9210_core_clks`, `r7s9210_mod_clks`, `r7s9210_update_clk_table()`, `rza2_cpg_clk_register()`, `r7s9210_cpg_mssr_info`, and `r7s9210_cpg_mssr_early_init()`.

Control flow: `CLK_OF_DECLARE_DRIVER()` calls `cpg_mssr_early_init()` for `renesas,r7s9210-cpg-mssr`, allowing early OSTM clocks. The CPG-MSSR core later consumes `r7s9210_cpg_mssr_info`. Custom registration updates divider tables from `CPG_FRQCR` and extal rate, then registers main/PLL fixed-factor clocks.

State and persistence: Init-only `cpg_mode` and mutable `r7s9210_core_clks` divider fields reflect EXTAL/FRQCR hardware state. Module clock state is handled by the generic MSSR core using RZ/A standby register layout.

Dependencies and integration: Depends on `renesas-cpg-mssr.h`, DT bindings, CCF, and generic CPG-MSSR infrastructure. Early module clocks support timers before the full driver is ready.

Risks: Illegal FRQCR values trigger `BUG_ON(1)`. Divider tables are mutated at init, so they must not be treated as const. EXTAL > 12 MHz is used as a mode heuristic. `num_hw_mod_clks` includes nonexistent STBCR0 intentionally.

Test signals: Boot RZ/A2, verify early OSTM clocks, compare FRQCR-derived I/G/B/P rates, check module clock gating for SCIF/USB/Ethernet/SDHI, and compile-test `CLK_R7S9210`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r7s9210-cpg-mssr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7742-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7742-cpg-mssr.c

Purpose: This RZ/G1H (`r8a7742`) data file describes Gen2 CPG core clocks, module standby clocks, critical module clocks, and PLL initialization for the generic Renesas CPG-MSSR driver.

Important APIs, types, and functions: It defines clock IDs, `r8a7742_core_clks`, `r8a7742_mod_clks`, `r8a7742_crit_mod_clks`, PLL config table `cpg_pll_configs`, `r8a7742_cpg_mssr_init()`, and exported `r8a7742_cpg_mssr_info`.

Control flow: The central CPG-MSSR driver selects this `cpg_mssr_info` for the matching compatible. Its `.init` callback reads mode pins with `rcar_rst_read_mode_pins()`, selects a PLL config using bits 14/13/19, and calls `rcar_gen2_cpg_init()`. The generic core registers listed core and module clocks.

State and persistence: All live clock state is held by generic CPG-MSSR and Gen2 CPG code. This file provides const init tables. Critical module clocks keep RWDT and INTC-SYS enabled.

Dependencies and integration: Depends on `renesas-cpg-mssr.h`, `rcar-gen2-cpg.h`, `rcar-rst`, and `r8a7742-cpg-mssr.h`. Module clocks cover display, video, USB, storage, serial, audio, GPIO, CAN, Ethernet, and DMA blocks.

Risks: Large module tables are offset-sensitive; a wrong module ID gates the wrong hardware. PLL config index must match MODEMR encoding. Critical clock omissions can break watchdog or interrupt controller operation.

Test signals: Boot RZ/G1H, compare PLL/core rates with mode pins, verify RWDT and INTC-SYS stay enabled, exercise representative module clocks such as SDHI, USB, VIN, DU, SCIF, and Ethernet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7742-cpg-mssr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7743-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7743-cpg-mssr.c

Purpose: This RZ/G1M and RZ/G1N (`r8a7743`/`r8a7744`) data file supplies Gen2 CPG-MSSR clock and module tables.

Important APIs, types, and functions: It defines mutable `r8a7743_core_clks`, `r8a7743_mod_clks`, `r8a7743_crit_mod_clks`, PLL config table, `r8a7743_cpg_mssr_init()`, and exported `r8a7743_cpg_mssr_info`.

Control flow: The generic CPG-MSSR core invokes `.init`. The callback reads mode pins, selects the Gen2 PLL config, and if the DT node is `renesas,r8a7744-cpg-mssr`, adjusts the ZG divider from the default to 1/5 before calling `rcar_gen2_cpg_init()`.

State and persistence: The core clock table is intentionally mutable for the RZ/G1N variant adjustment. Runtime register state is managed by the generic CPG-MSSR and Gen2 CPG libraries. Critical module clocks protect RWDT and INTC-SYS.

Dependencies and integration: Depends on OF compatibility checks, `rcar-rst`, `renesas-cpg-mssr.h`, `rcar-gen2-cpg.h`, and `r8a7743-cpg-mssr.h`. The module table spans timers, serial, USB, display, VIN, Ethernet, storage, GPIO, CAN, audio, and DMA.

Risks: Static table mutation for RZ/G1N must occur before generic registration. Module IDs are numerous and easy to misalign. `num_hw_mod_clks = 12 * 32` assumes the Gen2 MSSR register bank size.

Test signals: Boot both R8A7743 and R8A7744 compatibles, verify ZG divider difference, check critical clocks, run peripheral clock enable tests, and compare core rates to mode-pin tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7743-cpg-mssr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7745-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7745-cpg-mssr.c

Purpose: This file provides RZ/G1E (`r8a7745`) Gen2 CPG-MSSR tables and PLL initialization data.

Important APIs, types, and functions: It defines `r8a7745_core_clks`, `r8a7745_mod_clks`, `r8a7745_crit_mod_clks`, a four-entry effective PLL config table, `r8a7745_cpg_mssr_init()`, and `r8a7745_cpg_mssr_info`.

Control flow: The generic CPG-MSSR driver uses this info object for the matching SoC. The `.init` callback reads mode pins, selects a PLL config from bits 14/13, and calls `rcar_gen2_cpg_init(cpg_pll_config, 3, cpg_mode)`, reflecting PLL0 VCO/3 behavior for this SoC.

State and persistence: This source is mostly const init data. Runtime state is in generic CPG-MSSR registers and Gen2 CPG helpers. RWDT and INTC-SYS are listed as critical module clocks.

Dependencies and integration: Depends on Gen2 CPG helper code, CPG-MSSR core, `rcar-rst`, and `r8a7745-cpg-mssr.h`. Module entries cover the reduced RZ/G1E peripheral set.

Risks: PLL0 multiplier semantics differ from adjacent Gen2 files, so the `3` divider argument is important. Sparse module coverage must match silicon capabilities. Wrong critical clock IDs can destabilize watchdog or interrupt handling.

Test signals: Boot RZ/G1E, validate PLL0/PLL1/PLL3 rates from mode pins, verify SDHI/MMC, USB, serial, display, and Ethernet clocks, and confirm RWDT/INTC-SYS are protected from disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a7745-cpg-mssr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a77470-cpg-mssr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a77470-cpg-mssr.c

Purpose: This RZ/G1C (`r8a77470`) data file supplies Gen2 CPG core clocks, module standby clocks, critical module IDs, and mode-pin PLL setup for the generic CPG-MSSR framework.

Important APIs, types, and functions: It defines `r8a77470_core_clks`, `r8a77470_mod_clks`, `r8a77470_crit_mod_clks`, `cpg_pll_configs`, `r8a77470_cpg_mssr_init()`, and exported `r8a77470_cpg_mssr_info`.

Control flow: The central CPG-MSSR driver selects this info object. The `.init` callback reads mode pins, indexes PLL configuration from bits 14/13, and calls `rcar_gen2_cpg_init(cpg_pll_config, 2, cpg_mode)`. Core and module clock registration is then performed by generic code.

State and persistence: Tables are const init data. Runtime module-stop, reset, and core clock state are owned by the generic CPG-MSSR and Gen2 CPG layers. Critical module clocks protect RWDT and INTC-SYS.

Dependencies and integration: Depends on `renesas-cpg-mssr.h`, `rcar-gen2-cpg.h`, `rcar-rst`, and `r8a77470-cpg-mssr.h`. The module table covers G1C-specific USB channel naming, SDHI, display, serial, Ethernet, GPIO, CAN, QSPI, I2C, and audio blocks.

Risks: PLL config index 2 is explicitly invalid/prohibited in the table; if hardware straps select it, the resulting zeroed config would be dangerous unless generic code rejects it. Module IDs are sparse and hardware-specific. Critical clock protection is minimal but essential.

Test signals: Boot RZ/G1C with valid mode pins, verify Gen2 PLL rates, confirm USB/SDHI/SCIF/Ethernet module clocks, check critical RWDT/INTC-SYS behavior, and compile-test `CLK_R8A77470`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/r8a77470-cpg-mssr.c -->
