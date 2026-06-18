# sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm8650.c

### Purpose
`camcc-sm8650.c` is the Qualcomm camera clock controller driver for the SM8650 SoC. It describes the camera subsystem's PLLs, root clock generators, branch clocks, resets, GDSC power domains, always-critical CBCRs, MMIO register map, and platform-device binding. The file is almost entirely declarative: runtime enable, disable, rate selection, reset, and power-domain operations are handled by shared Qualcomm clock-controller code after this driver passes a populated `qcom_cc_desc` to `qcom_cc_probe()`.

### Important APIs, Types, And Functions
The file uses Linux CCF and Qualcomm clock types: `clk_alpha_pll`, `clk_alpha_pll_postdiv`, `clk_rcg2`, `clk_branch`, `gdsc`, `qcom_reset_map`, `regmap_config`, `qcom_cc_driver_data`, and `qcom_cc_desc`. It imports the public DT clock/reset/GDSC IDs from `dt-bindings/clock/qcom,sm8650-camcc.h`. Local parent enums map DT parent indexes (`bi_tcxo`, `bi_tcxo_ao`, `sleep_clk`) and internal parent IDs used by RCG parent maps.

Key data blocks are:
- Eleven alpha PLLs, `cam_cc_pll0` through `cam_cc_pll10`, using Lucid OLE ops for most PLLs and Rivian EVO ops for `cam_cc_pll2`.
- Post-divider outputs for selected PLLs, including even outputs for PLL0/1/3/4/5/6/7/8/9/10 and odd outputs for PLL0 and PLL9.
- RCGs for BPS, CAMNOC real-time AXI, CCI0-2, CPHY RX, CRE, CSI PHY timers 0-7, CSID, fast/slow AHB, ICP, IFE0-2, IFE lite, IPE NPS, JPEG, MCLK0-7, QDSS debug, SFE0-2, sleep, and XO.
- Branch clocks for the same camera blocks, plus CPAS votes, CSIPHY0-7, SBI, shift clocks, and Titan top shift.
- GDSCs for Titan top, BPS, IFE0/1/2, IPE0, SBI, and SFE0/1/2.
- Reset lines for BPS, DRV, ICP, IFE0/1/2, IPE0, QDSS debug, SBI, and SFE0/1/2.
- `cam_cc_sm8650_probe()`, which simply calls `qcom_cc_probe(pdev, &cam_cc_sm8650_desc)`.

### Control Flow
Probe-time control flow is short and framework-driven. The OF platform match table binds compatible `qcom,sm8650-camcc` to `camcc-sm8650`; module registration installs a `platform_driver`; `cam_cc_sm8650_probe()` calls `qcom_cc_probe()` with `cam_cc_sm8650_desc`. The common Qualcomm CC layer then maps the camera CC register range using `cam_cc_sm8650_regmap_config`, configures the listed alpha PLLs through `qcom_cc_driver_data`, registers every `clk_regmap` pointer from `cam_cc_sm8650_clocks`, registers reset controls from `cam_cc_sm8650_resets`, and exposes GDSC power domains from `cam_cc_sm8650_gdscs`.

Rate control is encoded in each RCG's frequency table and parent map. For example, BPS selects TCXO or PLL8 even outputs up to 785 MHz; IFE0/1/2 use PLL3/4/5 even outputs; SFE0/1/2 use PLL6/7/10; sensor MCLKs share a table with 19.2 MHz, 24 MHz, and 68.571429 MHz entries; and CSI/CSID paths select PLL0-derived rates. Branch clocks each provide a CBCR register, enable bit, halt check mode, and one parent `clk_hw`, so framework ops can vote clocks on/off and poll halt state.

### State, Persistence, And Dependencies
The driver has no private mutable runtime state. Persistent hardware state lives in CAMCC registers addressed by the regmap, with `.reg_bits = 32`, `.reg_stride = 4`, `.val_bits = 32`, `.max_register = 0x1603c`, and fast I/O enabled. Static C structures are the source of truth for register offsets, allowed rates, parent relationships, reset offsets, and power-domain hierarchy.

Dependencies include Linux platform-device and module infrastructure, regmap, the common clock framework, Qualcomm alpha PLL/RCG/branch/reset/GDSC helpers, RPM-aware Qualcomm CC registration (`.use_rpm = true`), and the SM8650 CAMCC DT binding. Parent clocks are supplied by DT parent indexes, so a wrong DT binding or missing parent clock breaks downstream rate derivation.

### Integration Points
This file integrates with the device tree through `qcom,sm8650-camcc` and the SM8650 CAMCC binding IDs. Camera, ISP, sensor, JPEG, debug, and interconnect consumers request these clocks and resets by ID. GDSC entries become power domains under genpd, with all functional domains except Titan top parented to `cam_cc_titan_top_gdsc`. The `cam_cc_sm8650_critical_cbcrs` list keeps CAM_CC_GDSC_CLK, CAM_CC_SLEEP_CLK, CAM_CC_DRV_XO_CLK, and CAM_CC_DRV_AHB_CLK from being disabled by late clock cleanup.

### Risks
Most risk is data accuracy rather than algorithmic complexity. A wrong register offset, parent map, frequency-table entry, reset offset, or DT ID array index can silently affect camera bring-up. The large `cam_cc_sm8650_clocks` table must stay aligned with the binding header; sparse or shifted IDs can register the wrong clock to consumers. PLL configuration values are hardware-specific and not validated here beyond common PLL registration. `CLK_SET_RATE_PARENT` on most RCGs and branches means consumer rate requests can propagate to shared PLL parents, so parent reuse must match hardware expectations. GDSC parent ordering and flags (`POLL_CFG_GDSCR | RETAIN_FF_ENABLE`) are also important because child domains depend on Titan top sequencing. Critical CBCRs are raw register offsets; mistakes can either leave required root clocks gated or keep unnecessary clocks always on.

### Test Signals
Useful validation signals include successful probe on an SM8650 device tree, `clk_summary` entries for all CAM_CC IDs, rate-set/readback tests for representative RCGs, camera pipeline smoke tests covering BPS/IFE/SFE/IPE/JPEG/MCLK/CSIPHY clocks, genpd on/off tests for all GDSCs, reset pulse tests for each BCR, suspend/resume with camera idle and active, and late clock cleanup logs showing the four critical CBCRs remain enabled. Binding/schema checks should verify the compatible string and DT clock indexes match `qcom,sm8650-camcc.h`.
