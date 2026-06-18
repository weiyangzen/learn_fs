# sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm8550.c

## Purpose

`camcc-sm8550.c` is the Qualcomm camera clock controller driver for SM8550. It describes a larger CAMCC topology with thirteen PLLs, many RCGs, camera block branch clocks, resets, critical CBCRs, and GDSC power domains. It supports BPS, IFE0/1/2, IFE Lite, IPE, SBI, SFE0/1, CRE, ICP, JPEG and JPEG_1, CPAS paths, CCI0/1/2, CSI0-7 timers and CSIPHY0-7, driver/XO clocks, QDSS debug, sensor MCLK0-7, CAMNOC, sleep, slow AHB, and XO sources.

## Important APIs, Types, and Functions

- DT parent enums include indexed `DT_BI_TCXO`, `DT_BI_TCXO_AO`, and `DT_SLEEP_CLK`; parent maps also expose `P_BI_TCXO_AO`.
- Thirteen `struct clk_alpha_pll` instances define PLL0 through PLL12. Lucid OLE VCO/config is used for most PLLs, while PLL2 uses a Rivian OLE VCO and Rivian Evo ops/register layout. Post-dividers exist for PLL0/1/3/4/5/6/7/8/9/10/11/12, with PLL0 also exposing an odd divider.
- `struct clk_rcg2` roots define rate plans for all major camera domains, including newer CRE, IFE DSP roots, expanded CSI/CSIPHY timers, and JPEG-specific rates.
- `struct clk_branch` entries expose gates and halt checks for block clocks, CPAS proxy clocks, fast AHB clocks, driver clocks, QDSS debug clocks, and sensor clocks.
- `struct gdsc` entries use SM8550-specific names (`cam_cc_*_gdsc`) and include wait values plus `RETAIN_FF_ENABLE` on all domains.
- `cam_cc_sm8550_plls[]` and `cam_cc_sm8550_critical_cbcrs[]` populate `struct qcom_cc_driver_data` for framework-managed PLL initialization and critical CBCR handling.
- `cam_cc_sm8550_desc` enables `.use_rpm = true` and supplies clock, reset, GDSC, regmap, and driver-data tables.
- `cam_cc_sm8550_probe()` is intentionally thin and calls `qcom_cc_probe()` directly.

## Control Flow

OF matching binds the platform driver to `qcom,sm8550-camcc`. Probe immediately calls `qcom_cc_probe(pdev, &cam_cc_sm8550_desc)`. The common Qualcomm CC code maps CAMCC MMIO according to `cam_cc_sm8550_regmap_config`, initializes alpha PLLs from `cam_cc_sm8550_plls[]`, registers all clocks in `cam_cc_sm8550_clocks[]`, registers reset lines from `cam_cc_sm8550_resets[]`, registers GDSCs from `cam_cc_sm8550_gdscs[]`, and applies critical CBCR handling for the GDSC and sleep clocks. All later runtime behavior is performed by common CCF, reset, and GDSC callbacks referenced by the static table entries.

## State and Persistence

There is no disk-backed state. CAMCC hardware register state is addressed through a 32-bit, stride-4, fast-IO regmap with maximum register `0x16320`. Static tables describe topology for the module lifetime and are not variant-mutated in this file. PLL programming, RCG source/divider selection, branch gate state, reset state, and GDSC state are retained only in hardware while powered. GDSCs include explicit enable/rest/few and clock-disable wait values plus `RETAIN_FF_ENABLE`, indicating power-collapse sequencing must preserve flip-flop retention behavior.

## Dependencies and Integration Points

The file depends on Linux platform-device, OF match, regmap, CCF, reset-controller, genpd, and Qualcomm clock helpers from `clk-alpha-pll.h`, `clk-branch.h`, `clk-rcg.h`, `clk-regmap.h`, `common.h`, `gdsc.h`, and `reset.h`. Binding constants come from `dt-bindings/clock/qcom,sm8550-camcc.h`. Camera and media drivers consume its exported clocks, resets, and power domains through DT phandles. RPM integration is enabled, so firmware/resource-power-management behavior is part of the integration contract. Always-on TCXO is used for XO-derived roots such as `cam_cc_xo_clk_src`.

## Risks and Edge Cases

The driver is almost entirely hardware data, so correctness depends on exact register offsets, parent selectors, frequency tables, PLL constants, and GDSC wait/retention settings. Expanded topology raises mapping risk: CCI2, CSI/CSIPHY6-7, CRE, DRV clocks, JPEG_1, IFE DSP roots, and additional PLLs must all align with the binding IDs. Critical CBCRs include both GDSC and sleep clocks; incorrect critical handling can affect suspend, idle power, or camera power-up. Because `qcom_cc_probe()` initializes PLLs via driver data, missing a PLL from `cam_cc_sm8550_plls[]` would leave dependent roots unusable even though their clock entries register.

## Test Signals

Probe should create clocks for all SM8550 binding IDs and expose PLL0-12, MCLK0-7, CSI0-7, CSIPHY0-7, CCI0-2, CRE, IFE DSP, SFE, JPEG/JPEG_1, CPAS, and QDSS debug entries in clock debugfs. Hardware validation should exercise multi-sensor capture across all CSI lanes, IFE/SFE/BPS/IPE processing, JPEG paths, CRE users, reset operations for all BCRs, GDSC on/off transitions with retention enabled, RPM-aware suspend/resume, and unused-clock cleanup while critical GDSC/sleep CBCRs remain enabled.
