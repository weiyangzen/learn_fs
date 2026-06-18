# sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm8450.c

## Purpose

`camcc-sm8450.c` implements the Qualcomm CAMCC driver for SM8450 and SM8475. It provides the camera clock, reset, PLL, and GDSC description for the Titan camera subsystem, including BPS, IPE NPS/PPS, IFE0/1/2, IFE Lite, SFE0/1, SBI, ICP, JPEG, CAMNOC, CSI/CSIPHY, CCI, QDSS debug, sensor MCLK, sleep, and XO-related clocks. Compared with SM8250, it has more PLLs, more camera processing blocks, RPM integration, critical CBCR registration, and variant-specific SM8475 PLL mutation in probe.

## Important APIs, Types, and Functions

- The DT parent enum (`DT_IFACE`, `DT_BI_TCXO`, `DT_BI_TCXO_AO`, `DT_SLEEP_CLK`) and `clk_parent_data` entries use indexed DT clocks rather than only firmware names.
- Nine `struct clk_alpha_pll` instances cover PLL0 through PLL8. Most are Lucid Evo on SM8450; SM8475 probe rewrites several to Lucid OLE register layouts/configuration and changes PLL2 to a Rivian OLE VCO table/config.
- `sm8475_cam_cc_pll*_config` and `sm8475_cam_cc_pll*_out_even/_odd_init` hold the variant overrides used only when compatible is `qcom,sm8475-camcc`.
- `struct clk_rcg2` entries define rate plans for BPS, CAMNOC, CCI, CPHY RX, CSI timers, CSID, AHB roots, ICP, IFEs, IFE Lite, IPE NPS, JPEG, MCLK0-7, QDSS debug, SFE0/1, sleep, slow AHB, and XO.
- `struct clk_branch` entries expose the gated outputs consumed by camera blocks, CPAS votes, debug clocks, and sensor paths.
- `cam_cc_sm8450_plls[]` and `cam_cc_sm8450_critical_cbcrs[]` feed `struct qcom_cc_driver_data`, allowing `qcom_cc_probe()` to initialize alpha PLLs and keep the GDSC CBCR critical.
- `cam_cc_sm8450_resets[]`, `cam_cc_sm8450_gdscs[]`, and `cam_cc_sm8450_desc` provide reset, genpd, and common CC registration data.
- `cam_cc_sm8450_probe()` applies SM8475 overrides if needed and then calls `qcom_cc_probe()`.

## Control Flow

The platform driver matches either `qcom,sm8450-camcc` or `qcom,sm8475-camcc`. On SM8450, probe immediately delegates to `qcom_cc_probe()` with `cam_cc_sm8450_desc`; the common framework maps registers, initializes PLLs listed in driver data, registers clocks, resets, critical CBCRs, and GDSCs, and enables RPM-aware handling because `.use_rpm = true`.

On SM8475, probe first mutates static PLL objects in place. PLL0/1/3/4/5/6/7/8 and their post-dividers switch from Lucid Evo register tables and ops init data to Lucid OLE-compatible register tables/init data. PLL2 changes VCO table, and all PLL config pointers are redirected to SM8475-specific `alpha_pll_config` structures. After these mutations, the same descriptor and clock arrays are registered through `qcom_cc_probe()`.

## State and Persistence

The driver has no persistent storage. Hardware state resides in CAMCC registers described by `cam_cc_sm8450_regmap_config` up to `0x1601c`. Static object state is significant because SM8475 support mutates global PLL and post-divider objects during probe; this is safe for a single SoC instance but means the object graph is no longer purely constant after variant detection. PLL, RCG, branch, reset, and GDSC state persists only in hardware registers until reset or power loss. `qcom_cc_driver_data` marks a GDSC support CBCR critical so framework cleanup does not gate it unexpectedly.

## Dependencies and Integration Points

The driver depends on Linux CCF, reset-controller and genpd integration, regmap, OF matching, and Qualcomm CC helpers from `clk-alpha-pll.h`, `clk-branch.h`, `clk-pll.h`, `clk-rcg.h`, `clk-regmap-divider.h`, `clk-regmap-mux.h`, `clk-regmap.h`, `common.h`, `gdsc.h`, and `reset.h`. Its binding IDs come from `dt-bindings/clock/qcom,sm8450-camcc.h`. DT supplies indexed parents, including normal TCXO, always-on TCXO, and sleep clock. Camera, media, sensor, interconnect/CPAS, and debug consumers integrate through clock IDs, reset IDs, and GDSC IDs in the binding.

## Risks and Edge Cases

Variant handling is the main code risk. SM8475 support mutates shared static structures based on `of_device_is_compatible()`, so any future multi-instance or mixed-compatible scenario would be unsafe. Missing a PLL override, post-divider init override, or config pointer update can silently program SM8475 PLLs with SM8450 values. Register offsets and parent selector values are dense and hardware-specific; mistakes affect only particular camera blocks and can appear as camera stream failures rather than probe failures. `.use_rpm = true` and critical CBCR handling must align with firmware power management; wrong critical clocks can either waste power or break GDSC transitions.

## Test Signals

Probe should succeed for both `qcom,sm8450-camcc` and `qcom,sm8475-camcc`, with clock debugfs showing PLL0-8, MCLK0-7, IFE0/1/2, SFE0/1, IPE NPS/PPS, CPAS, CSI, CSIPHY, and QDSS debug clocks. Variant testing should compare PLL register programming on SM8475 against expected Lucid OLE/Rivian OLE settings. Functional tests should cover camera capture across all sensors and CSI lanes, SFE and IFE paths, JPEG and BPS/IPE processing, genpd on/off transitions for all GDSCs, reset toggles for all BCRs, suspend/resume, and unused-clock cleanup with the critical GDSC CBCR still active.
