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
