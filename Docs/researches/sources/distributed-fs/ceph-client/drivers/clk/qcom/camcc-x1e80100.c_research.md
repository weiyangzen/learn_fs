# sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-x1e80100.c

### Purpose
`camcc-x1e80100.c` is the Qualcomm camera clock controller driver for the X1E80100 platform. It defines the camera PLLs, RCG sources, branch gates, GDSC power domains, resets, critical registers, and platform binding required for the common Qualcomm CC framework to expose the camera clock tree to Linux consumers. The hardware model is close to the SM8650 generation but smaller: fewer PLLs, fewer CSI lanes, two IFE blocks, one SFE block, and X1E80100-specific register offsets.

### Important APIs, Types, And Functions
The file relies on `clk_alpha_pll`, `clk_alpha_pll_postdiv`, `clk_rcg2`, `clk_branch`, `gdsc`, `qcom_reset_map`, `regmap_config`, `qcom_cc_driver_data`, and `qcom_cc_desc`. It uses DT IDs from `dt-bindings/clock/qcom,x1e80100-camcc.h`. Parent enums represent DT roots and internal PLL outputs.

Important definitions include:
- Seven alpha PLLs: Lucid OLE PLLs `cam_cc_pll0`, `cam_cc_pll1`, `cam_cc_pll3`, `cam_cc_pll4`, `cam_cc_pll6`, and `cam_cc_pll8`, plus Rivian EVO `cam_cc_pll2`.
- Post-divider outputs for PLL0 even/odd and even outputs for PLL1/3/4/6/8.
- RCGs for BPS, CAMNOC RT AXI, CCI0/1, CPHY RX, CSI PHY timers 0-5, CSID, fast/slow AHB, ICP, IFE0/1, IFE lite, IPE NPS, JPEG, MCLK0-7, SFE0, sleep, and XO.
- Branch clocks for BPS, CAMNOC, CCI, CPAS, CSI/CSID/CSIPHY0-5, ICP, IFE0/1 including DSP and fast AHB branches, IFE lite, IPE, JPEG, MCLK0-7, and SFE0.
- GDSCs for BPS, IFE0, IFE1, IPE0, SFE0, and Titan top, with child domains parented to Titan top.
- Reset controls for BPS, ICP, IFE0, IFE1, IPE0, and SFE0.
- `cam_cc_x1e80100_probe()`, which delegates registration to `qcom_cc_probe()`.

### Control Flow
The module registers a platform driver named `camcc-x1e80100`. The OF match table accepts compatible `qcom,x1e80100-camcc`; probe invokes `qcom_cc_probe(pdev, &cam_cc_x1e80100_desc)`. From there, common Qualcomm CC code maps the register space using `cam_cc_x1e80100_regmap_config`, initializes/registers the listed PLLs and critical CBCRs from `cam_cc_x1e80100_driver_data`, registers the clock array, reset map, and GDSC power domains, then services consumer CCF and reset-controller requests.

Rate selection is table-driven. BPS and JPEG can use TCXO and PLL0-derived rates up to 600 MHz; CAMNOC RT AXI uses PLL0 even/odd rates up to 400 MHz; CCI sources use TCXO, PLL8 even, or PLL0 even; IFE0/1 use PLL3/4 even up to 727 MHz; SFE0 uses PLL6 even up to 727 MHz; IPE NPS uses PLL1 even up to 700 MHz; sensor MCLKs share a 19.2 MHz, 24 MHz, and 68.571429 MHz table. Unlike SM8650, several leaf RCGs use `clk_rcg2_ops` instead of shared ops, notably CCI, CPHY, CSI timers, MCLKs, sleep, and XO.

### State, Persistence, And Dependencies
The driver contains no private runtime allocation or persistent software state. CAMCC register state persists in MMIO hardware accessed through a 32-bit regmap with 4-byte stride, maximum register `0x1603c`, and fast I/O. Static structures encode register offsets, allowed rates, parent hardware, reset offsets, and power-domain topology.

Dependencies include platform-driver and module support, regmap, the Linux common clock framework, Qualcomm alpha PLL/RCG/branch/GDSC/reset helpers, RPM-aware common CC handling (`.use_rpm = true`), and the X1E80100 CAMCC DT binding. Correct behavior also depends on DT parent clock order for interface, TCXO, always-on TCXO, and sleep clock inputs.

### Integration Points
The integration surface is the `qcom,x1e80100-camcc` DT node and the `qcom,x1e80100-camcc.h` binding IDs used by camera, sensor, ISP, JPEG, CSI, and power-management consumers. GDSCs are exposed as genpd domains with Titan top as the parent for BPS/IFE/IPE/SFE islands. Reset IDs provide block reset controls for major camera engines. `cam_cc_x1e80100_critical_cbcrs` keeps CAM_CC_GDSC_CLK and CAM_CC_SLEEP_CLK enabled across framework cleanup.

### Risks
This file's risk is concentrated in hardware description correctness. Register offsets differ significantly from SM8650 despite similar block names, so copy/paste mistakes can target the wrong CBCR or BCR. The forward declaration of `cam_cc_titan_top_gdsc` is necessary because child GDSCs reference its `pd` before its definition; reordering must preserve that relationship. The `cam_cc_x1e80100_clocks` array must remain aligned with the X1E80100 binding header. Mixed `clk_rcg2_ops` and `clk_rcg2_shared_ops` usage should match hardware ownership; choosing the wrong ops can alter rate/enable coordination. Critical CBCR coverage is smaller than on phone SoCs, so platform suspend and camera resume tests are important.

### Test Signals
Validation should include successful probe on X1E80100 DT, complete `clk_summary` coverage for all exported CAMCC IDs, rate programming checks for BPS/JPEG/IFE/SFE/IPE/MCLK/CSI clocks, end-to-end camera capture or ISP smoke tests, GDSC power-domain cycling under runtime PM, reset assertion/deassertion for each BCR, suspend/resume with camera consumers idle and active, and late clock cleanup checks confirming GDSC and sleep critical clocks remain enabled. DT schema checks should verify compatible, parent-clock ordering, and binding ID coverage.
