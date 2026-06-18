# Research: subset-b-001112

Grouped research for three Qualcomm camera clock-controller source files under `sources/distributed-fs/ceph-client/drivers/clk/qcom/`. Each section is delimited for reconciliation into the source-tree-aligned per-file report path.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sc7280.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sc7280.c

## Purpose

`camcc-sc7280.c` is the Qualcomm CAM_CC clock-controller driver for SC7280 camera hardware. It describes the camera clock tree, camera power domains, and the platform-device registration path that exposes those clocks and GDSCs to the Linux common clock framework and generic power-domain framework.

The file is data-driven. Most of the source is static hardware description: PLLs, post-dividers, parent maps, RCG frequency tables, branch gates, GDSCs, and the final `qcom_cc_desc`. Runtime behavior is concentrated in `cam_cc_sc7280_probe()`, which maps MMIO registers, programs PLL configuration values, and then hands registration to the shared Qualcomm clock-controller helpers.

## Important APIs, Types, and Data

- External interfaces: `platform_driver`, OF match compatible `qcom,sc7280-camcc`, and DT clock/power-domain IDs from `<dt-bindings/clock/qcom,camcc-sc7280.h>`.
- Qualcomm clock types: `struct clk_alpha_pll`, `struct clk_alpha_pll_postdiv`, `struct clk_rcg2`, `struct clk_branch`, `struct gdsc`, `struct qcom_cc_desc`, and `struct regmap_config`.
- Shared helper APIs: `qcom_cc_map()`, `qcom_cc_really_probe()`, `clk_lucid_pll_configure()`, and `clk_zonda_pll_configure()`.
- PLL inventory: seven PLLs, `cam_cc_pll0` through `cam_cc_pll6`. Most use Lucid PLL ops and the `lucid_vco` range; `cam_cc_pll2` uses Zonda ops and `zonda_vco`. Post-dividers expose even, odd, aux, or aux2 outputs where needed.
- Parent model: internal parent enum values describe XO, sleep clock, PLL main outputs, and PLL post-dividers. `parent_map` and `clk_parent_data` arrays bind those hardware parent selections to firmware names or internal `clk_hw` parents.
- RCGs and frequency tables: source clocks include BPS, CAMNOC AXI, CCI, CPHY RX, CSI PHY timers, FAST/SLOW AHB, ICP, IFE, IFE CSID, IFE Lite, IPE, JPEG, LRME, MCLK, sleep, and XO. Tables use the Qualcomm `F()` macro to encode rate, parent, divider, and M/N values.
- Branch clocks: branch gate descriptors cover the camera sub-blocks and almost all use `BRANCH_HALT` with `CLK_SET_RATE_PARENT`. `cam_cc_core_ahb_clk` uses `BRANCH_HALT_DELAY`; `cam_cc_gdsc_clk` is marked `CLK_IS_CRITICAL`.
- Power domains: six GDSCs are exported: Titan top, BPS, IFE0, IFE1, IFE2, and IPE0. The child domains point at `cam_cc_titan_top_gdsc.pd`; BPS and IPE0 use `HW_CTRL | RETAIN_FF_ENABLE`, while Titan/IFE domains retain flip-flop state.
- Registration arrays: `cam_cc_sc7280_clocks[]` maps DT clock IDs to `clk_regmap` instances, and `cam_cc_sc7280_gdscs[]` maps DT GDSC IDs to `struct gdsc` instances.
- MMIO shape: `cam_cc_sc7280_regmap_config` uses 32-bit registers, stride 4, `max_register = 0xf00c`, and `fast_io = true`.

## Control Flow

1. The platform bus matches `qcom,sc7280-camcc` and calls `cam_cc_sc7280_probe()`.
2. `qcom_cc_map()` maps the controller register resource using `cam_cc_sc7280_desc`. A mapping failure is returned directly.
3. The probe configures PLL0, PLL1, PLL3, PLL4, PLL5, and PLL6 with `clk_lucid_pll_configure()`, and PLL2 with `clk_zonda_pll_configure()`.
4. `qcom_cc_really_probe()` registers the clock provider and GDSCs from the descriptor.
5. Once registered, camera consumers select rates and enable clocks through the common clock framework; power-domain clients control GDSCs through genpd.

## State and Persistence

The source has no persistent on-disk or cross-boot state. Static C objects describe hardware topology, and probe writes hardware registers through regmap to configure PLLs and later allow common clock operations to alter rates, muxes, dividers, and branch enable bits. Power-domain state is represented by GDSC register bits and by genpd reference counts after registration. The module has no explicit remove path, so normal device-managed/common-framework lifetime rules apply.

## Dependencies and Integration Points

- Requires the SC7280 camera clock-controller DT node with compatible `qcom,sc7280-camcc`, the MMIO resource, and parent clocks named by firmware data such as `bi_tcxo` and sleep clock parents.
- Integrates with Qualcomm shared clock code in `clk-alpha-pll`, `clk-rcg`, `clk-branch`, `common`, `gdsc`, and `reset` support headers. This file includes `reset.h` but does not provide reset maps in the descriptor.
- Provides clock IDs consumed by camera, CSI, IFE, IPE, JPEG, BPS, ICP, CAMNOC, and sensor MCLK users.
- Provides GDSCs that camera pipeline devices can reference as power domains.

## Risks and Review Notes

- The DT binding ID order must match `cam_cc_sc7280_clocks[]` and `cam_cc_sc7280_gdscs[]`; any mismatch gives consumers the wrong clock or domain.
- PLL programming constants are hardware-specific and not validated locally. Wrong values can produce unstable rates or camera bring-up failures.
- Rate tables rely on parent availability and exact divider encodings, including fractional-looking divisors such as `1.5` and `7.5` encoded by the Qualcomm macros. Parent-map mistakes can silently select the wrong PLL output.
- `cam_cc_gdsc_clk` is critical, so it resists disable paths. That protects GDSC operation but can mask excess power draw if the register is wrong.
- No reset map is registered for SC7280 in this driver, unlike the larger SC8180X/SC8280XP CAMCC drivers. Consumers needing reset controls must not assume this provider offers them.
- GDSC parentage matters: enabling a child domain requires Titan top sequencing to work through genpd. Bad parent references would show up as power-domain enable timeouts.

## Test Signals

- Build coverage: compile with the relevant Qualcomm clock driver configuration enabled and ensure no missing DT binding IDs or unused descriptor breakage.
- Boot/probe: expect a successful platform probe for `qcom,sc7280-camcc` with no regmap mapping error.
- Clock provider validation: inspect `/sys/kernel/debug/clk/clk_summary` for CAM_CC clocks, rates, parent selection, and enable counts while starting camera pipelines.
- Power-domain validation: exercise BPS, IFE0/1/2, and IPE0 consumers and watch GDSC status bits or genpd debug output for correct parent/child sequencing.
- Camera functional tests: sensor streaming through CSI PHY timers, MCLKs, IFE/IFE Lite, JPEG/LRME/IPE/BPS paths should drive the relevant branch enables and rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sc7280.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sc8180x.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sc8180x.c

## Purpose

`camcc-sc8180x.c` is the Qualcomm CAMCC driver for the SC8180X camera subsystem. It registers a large camera clock tree, reset controls, and camera GDSC power domains for high-end camera blocks such as multiple IFEs, IFE Lite instances, IPEs, MCLKs, CCI controllers, CSI PHYs, BPS, ICP, JPEG, LRME, CAMNOC, and FD core clocks.

Compared with the SC7280 driver, this file leans more heavily on shared Qualcomm controller infrastructure. PLL configs are attached to each `clk_alpha_pll`, `qcom_cc_driver_data` lists the PLLs and critical CBCR registers, and probe simply calls `qcom_cc_probe()`.

## Important APIs, Types, and Data

- External interfaces: platform driver name `camcc-sc8180x`, OF compatible `qcom,sc8180x-camcc`, and DT IDs from `<dt-bindings/clock/qcom,sc8180x-camcc.h>`.
- Device-tree parent indexes: `DT_IFACE`, `DT_BI_TCXO`, and `DT_SLEEP_CLK` define the provider-side parent references used by `clk_parent_data`.
- Parent enum: internal parents cover XO, sleep clock, PLL main outputs, and PLL post-divider outputs.
- PLL inventory: seven PLLs, `cam_cc_pll0` through `cam_cc_pll6`. PLL0/1/3/4/5/6 use Trion-style ops and `trion_vco`; PLL2 uses Regera ops and `regera_vco`, with a main post-divider.
- RCG inventory: frequency-programmable roots include BPS, CAMNOC AXI, four CCI roots, CPHY RX, four CSI PHY timers, FAST/SLOW AHB, FD core, ICP, four full IFE roots, four IFE CSID roots, four IFE Lite roots, IPE0, JPEG, LRME, eight MCLK roots, and XO.
- Branch inventory: branch gates expose AHB/AXI/AREG/core clocks for the camera blocks. Most use `BRANCH_HALT`; `cam_cc_cpas_ahb_clk` uses `BRANCH_HALT_VOTED`, reflecting vote-controlled halt semantics.
- Reset controls: `cam_cc_sc8180x_resets[]` exposes BCRs for BPS, CAMNOC, CCI, CPAS, CSI0-3 PHYs, FD, ICP, IFE0-3, IFE Lite0-3, IPE0-1, JPEG, LRME, and MCLK0-7.
- Power domains: eight GDSCs are exported: BPS, IFE0-3, IPE0-1, and Titan top. All use `POLL_CFG_GDSCR`; child domains are parented to Titan top.
- Critical CBCRs: `cam_cc_sc8180x_critical_cbcrs[]` lists raw CBCR registers `0xc1e4` for `CAM_CC_GDSC_CLK` and `0xc200` for `CAM_CC_SLEEP_CLK` so shared probe code can keep them enabled.
- Descriptor details: `cam_cc_sc8180x_desc` registers clocks, resets, GDSCs, sets `.use_rpm = true`, and attaches `cam_cc_sc8180x_driver_data`. The regmap is 32-bit, stride 4, `max_register = 0xf0d4`, with `fast_io = true`.

## Control Flow

1. The platform device matches `qcom,sc8180x-camcc`.
2. `cam_cc_sc8180x_probe()` calls `qcom_cc_probe(pdev, &cam_cc_sc8180x_desc)`.
3. The shared Qualcomm probe path maps registers, applies PLL configuration from `driver_data.alpha_plls`, handles critical CBCRs from `driver_data.clk_cbcrs`, and registers clocks, resets, and GDSCs.
4. After registration, camera consumers use the common clock, reset-controller, and genpd APIs. The `.use_rpm = true` flag tells the common Qualcomm layer this controller participates in RPM-aware handling.

## State and Persistence

The driver keeps static topology and configuration in C data. It has no persistent storage and no file-backed state. Runtime state is in hardware registers: PLL configuration, RCG mux/divider/M/N programming, branch enable bits, reset bits, and GDSC status/configuration bits. Framework-visible state is maintained by common clock reference counts, reset-controller calls, and genpd power-domain state. Critical CBCRs are intentionally kept enabled by common probe handling.

## Dependencies and Integration Points

- Depends on a correct SC8180X CAMCC DT node, MMIO resource, parent clocks at the expected DT indexes, and camera consumers using the binding IDs from `qcom,sc8180x-camcc.h`.
- Integrates with `clk-alpha-pll`, `clk-rcg`, `clk-branch`, `clk-regmap`, `common`, `gdsc`, and reset-controller support.
- Provides reset controls in addition to clocks and GDSCs, so consumers may sequence reset deassertion with clock and power enable.
- Camera integration spans multiple parallel pipelines: four CCI roots, four CSI PHY timer/PHY groups, four full IFE groups, four IFE Lite groups, two IPE groups, MCLK0-7, BPS, FD, ICP, JPEG, LRME, and CAMNOC.

## Risks and Review Notes

- The file is array-index sensitive. DT IDs must align with the `cam_cc_sc8180x_clocks[]`, reset, and GDSC arrays.
- The single `qcom_cc_probe()` call hides multiple side effects. Reviewers should confirm common code still configures `.config`-backed PLLs and critical CBCRs as expected when shared helpers evolve.
- Critical CBCR addresses are raw register offsets. A typo would keep the wrong branch enabled or fail to protect a required always-on clock.
- `.use_rpm = true` makes integration dependent on RPM-aware common code paths; regressions there may appear as probe, suspend/resume, or camera power sequencing failures.
- Reset offsets cover many sub-blocks. Incorrect reset IDs or offsets can break individual camera engines while leaving most clocks apparently healthy.
- GDSCs using `POLL_CFG_GDSCR` can expose hardware timing or sequencing issues as poll timeouts. Parent-child domain ordering with Titan top is a key validation area.

## Test Signals

- Build with SC8180X CAMCC enabled and validate DT binding enum references compile cleanly.
- Probe test: boot with `qcom,sc8180x-camcc` and confirm `qcom_cc_probe()` succeeds without regmap, PLL, or GDSC registration errors.
- Clock debug: inspect CAMCC rates and parents in debugfs, especially PLL2/Regera-derived paths, IFE roots, MCLK0-7, and critical GDSC/sleep clocks.
- Reset tests: request and toggle representative resets such as BPS, CSI PHY, IFE, IPE, JPEG, LRME, and MCLK resets through camera drivers or reset-controller debug hooks.
- Runtime camera tests: exercise multiple sensors and parallel IFE/IFE Lite pipelines to validate CCI, CSI timers, MCLKs, CAMNOC, and GDSC transitions under load and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sc8180x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sc8280xp.c -->
# sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sc8280xp.c

## Purpose

`camcc-sc8280xp.c` is the Qualcomm CAMCC driver for SC8280XP camera hardware. It registers the camera clock tree, reset controls, and GDSC power domains, and it adds explicit runtime-PM handling around register access during probe.

The file is a static hardware description plus a small but important probe sequence. It programs eight camera PLLs, enables a critical GDSC branch clock, registers clocks/resets/GDSCs with shared Qualcomm code, and carefully unwinds runtime PM and the critical branch on failure.

## Important APIs, Types, and Data

- External interfaces: platform driver name `camcc-sc8280xp`, OF compatible `qcom,sc8280xp-camcc`, and DT IDs from `<dt-bindings/clock/qcom,sc8280xp-camcc.h>`.
- Runtime PM APIs: `devm_pm_runtime_enable()`, `pm_runtime_resume_and_get()`, `pm_runtime_put()`, and `pm_runtime_put_sync()`.
- Qualcomm helper APIs: `qcom_cc_map()`, `qcom_cc_really_probe()`, `qcom_branch_set_clk_en()`, `clk_lucid_pll_configure()`, `clk_zonda_pll_configure()`, and `regmap_update_bits()`.
- DT parent indexes: `DT_IFACE`, `DT_BI_TCXO`, `DT_BI_TCXO_AO`, and `DT_SLEEP_CLK`.
- PLL inventory: eight PLLs, `camcc_pll0` through `camcc_pll7`. PLL0/1/3/4/5/6/7 use Lucid 5LPE/Lucid post-divider style operations with the Lucid VCO range; PLL2 is Zonda-based. Post-divider outputs expose even and odd variants where used by downstream roots.
- RCG inventory: programmable roots cover BPS, CAMNOC AXI, four CCI roots, CPHY RX, four CSI PHY timers, FAST/SLOW AHB, ICP, IFE0-3 roots and CSID roots, IFE Lite0-3 roots and CSID roots, IPE0, JPEG, LRME, MCLK0-7, sleep, and XO.
- Branch inventory: branch gates cover AHB/AXI/AREG and functional clocks for BPS, CAMNOC, CCI, CPAS, CSI PHYs, ICP, IFEs, IFE Lites, IPE0/1, JPEG, LRME, MCLK0-7, and sleep. Most branches use `BRANCH_HALT`; CPAS AHB uses `BRANCH_HALT_DELAY`.
- Power domains: eight GDSCs are exported: BPS, IFE0-3, IPE0-1, and Titan top. BPS and IPE0/1 use `HW_CTRL | RETAIN_FF_ENABLE`; the IFE domains and Titan top retain state without HW_CTRL. Child domains are parented to Titan top.
- Reset controls: `camcc_sc8280xp_resets[]` exposes BCRs for BPS, CAMNOC, CCI, CPAS, CSI0-3 PHYs, ICP, IFE0-3, IFE Lite0-3, IPE0-1, JPEG, and LRME.
- Descriptor details: `camcc_sc8280xp_desc` registers clocks, resets, and GDSCs. The regmap uses 32-bit registers, stride 4, `max_register = 0x13020`, and `fast_io = true`.

## Control Flow

1. The platform bus matches `qcom,sc8280xp-camcc` and calls `camcc_sc8280xp_probe()`.
2. Probe enables runtime PM for the device and resumes it with `pm_runtime_resume_and_get()` so CAMCC registers are accessible.
3. `qcom_cc_map()` maps the register block. On failure, probe drops the runtime-PM reference with `pm_runtime_put_sync()`.
4. Probe programs PLL0, PLL1, PLL3, PLL4, PLL5, PLL6, and PLL7 with Lucid configuration and PLL2 with Zonda configuration.
5. Probe calls `qcom_branch_set_clk_en(regmap, 0xc1e4)` to keep `CAMCC_GDSC_CLK` enabled.
6. `qcom_cc_really_probe()` registers the descriptor. On registration failure, the error path clears bit 0 at `0xc1e4`, drops the runtime-PM reference synchronously, and returns the error.
7. On success, probe drops its runtime-PM reference with `pm_runtime_put()` and leaves framework-managed clocks, resets, and GDSCs available to consumers.

## State and Persistence

There is no persistent storage. Static C structures encode topology and register offsets. Probe mutates hardware state by configuring PLL registers and enabling the critical GDSC branch. Later state changes are driven by common clock, reset-controller, genpd, and runtime-PM users. Runtime PM state is transient and reference-counted by the PM core; the explicit probe reference only protects registration-time MMIO access.

## Dependencies and Integration Points

- Requires a DT node with compatible `qcom,sc8280xp-camcc`, a valid MMIO resource, and parent clocks matching the DT parent indexes.
- Depends on runtime-PM infrastructure being able to resume the CAMCC device before MMIO access.
- Integrates with Qualcomm shared clock code in the same qcom clock subsystem and with Linux common clock, reset-controller, genpd, platform-driver, regmap, and PM-runtime frameworks.
- Camera consumers can use the exported clocks for BPS, CAMNOC, CCI, CSI PHY timers, IFEs, IFE Lite, IPE, JPEG, LRME, MCLK, sleep, slow AHB, and XO paths.
- GDSC exports provide power domains for Titan top and camera processing blocks; reset exports let consumers reset major camera engines.

## Risks and Review Notes

- Runtime-PM sequencing is a central risk. Any early return after `pm_runtime_resume_and_get()` must drop the PM reference; this file does so through `err_put_rpm`.
- The critical `CAMCC_GDSC_CLK` enable at raw offset `0xc1e4` must match the hardware. The failure path clears the bit only after a failed `qcom_cc_really_probe()`, so incorrect offset handling can affect power or registration stability.
- The regmap `max_register` is larger than in SC7280/SC8180X. Adding clocks above `0x13020` would require updating this bound.
- PLL and frequency-table constants are opaque hardware programming values. Small mistakes can break a subset of camera rates without compile-time errors.
- Reset coverage differs from SC8180X: this file does not expose FD or MCLK reset entries. Consumers must follow the SC8280XP binding, not a sibling SoC assumption.
- GDSC flags mix HW-controlled and software-controlled domains. Wrong flags can cause hangs, unexpected power retention, or inability to collapse a block.

## Test Signals

- Build with SC8280XP CAMCC enabled and ensure all DT binding indexes resolve.
- Probe test: boot on SC8280XP hardware or an equivalent integration environment and confirm runtime PM resume, regmap mapping, PLL configuration, and `qcom_cc_really_probe()` succeed.
- Error-path review or fault injection: force regmap/probe failure and verify runtime-PM references are released and the `CAMCC_GDSC_CLK` bit is cleared after registration failure.
- Clock debug: inspect debugfs for CAMCC PLLs, MCLK0-7, IFE/IFE Lite roots, sleep clock, and the critical GDSC branch.
- Camera workload tests: exercise sensor streaming, multi-IFE paths, IPE/JPEG/LRME use, reset sequencing, and suspend/resume to validate runtime-PM and GDSC interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sc8280xp.c -->
