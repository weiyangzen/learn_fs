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
