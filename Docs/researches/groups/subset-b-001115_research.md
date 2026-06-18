# subset-b-001115 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm8650.c -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm8650.c

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm8650.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm8750.c -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm8750.c

### Purpose
`camcc-sm8750.c` is the Qualcomm camera clock controller driver for the SM8750 SoC. It publishes the SM8750 camera clock tree, power domains, reset controls, PLL initialization data, and platform binding to the Linux common clock framework through Qualcomm's shared CC infrastructure. Compared with the SM8650/X1E80100-style files, this generation uses Taycan ELU PLLs and models newer camera blocks with TFE and OFE naming, including separate real-time and non-real-time CAMNOC clocks.

### Important APIs, Types, And Functions
The driver is built from standard Qualcomm CC data types: `clk_alpha_pll`, `clk_alpha_pll_postdiv`, `clk_rcg2`, `clk_branch`, `gdsc`, `qcom_reset_map`, `qcom_cc_driver_data`, and `qcom_cc_desc`. It imports IDs from `dt-bindings/clock/qcom,sm8750-camcc.h`. Parent enums describe DT-provided roots (`bi_tcxo`, `bi_tcxo_ao`, `sleep_clk`) plus internal PLL outputs.

Important definitions include:
- Seven Taycan ELU alpha PLLs, `cam_cc_pll0` through `cam_cc_pll6`, with even post-divider outputs for PLL0-6 and odd post-divider outputs for PLL0 and PLL6.
- Frequency tables for CAMNOC RT AXI, CCI0-2, CPHY RX, CRE, CSI PHY timers 0-5, CSID, fast/slow AHB, ICP0/1, IFE lite, IPE NPS, JPEG, OFE, QDSS debug, TFE0/1/2, sleep, and XO.
- Branch clocks for camera top AHB/fast AHB, CAMNOC DCD/XO/NRT/RT paths, CCI, CRE, CSI/CSID/CSIPHY, ICP0/1, IFE lite, IPE, JPEG0/1, OFE anchor/HDR/main paths, QDSS debug, and TFE bayer/main paths.
- GDSCs for Titan top, IPE0, OFE, and TFE0/1/2.
- Reset controls for DRV, ICP, IPE0, OFE, QDSS debug, and TFE0/1/2.
- `cam_cc_sm8750_probe()`, the only function with executable driver-specific logic, which delegates to `qcom_cc_probe()`.

### Control Flow
The control path is platform-driver registration followed by framework registration. The OF table matches `qcom,sm8750-camcc`; `cam_cc_sm8750_probe()` passes `cam_cc_sm8750_desc` to `qcom_cc_probe()`. The common CC code maps registers, applies PLL registration/init data from `cam_cc_sm8750_driver_data`, registers the `cam_cc_sm8750_clocks` array, registers reset controls, and registers GDSC power domains.

Clock-rate behavior is encoded in RCG tables. CAMNOC RT AXI can select TCXO or PLL0 even outputs from 200 to 400 MHz. CPHY/CSID paths derive from PLL0 main; CRE/JPEG/ICP share PLL0 and PLL6 derived rates; OFE gets dedicated rates from PLL2 even up to 841 MHz; TFE0/1/2 use PLL3/4/5 even outputs up to 833 MHz; and IPE NPS uses PLL1 even outputs up to 825 MHz. Branch clocks expose CBCR enable registers and halt semantics; several CAMNOC branches include hardware clock gating fields (`hwcg_reg`/`hwcg_bit`) and voted halt checks where hardware ownership is expected.

### State, Persistence, And Dependencies
The file keeps no allocated or private state. Hardware state persists in registers behind the CAMCC regmap, configured for 32-bit registers, 4-byte stride, 32-bit values, maximum register `0x1601c`, and fast I/O. Static tables provide all allowed frequencies, parents, enable offsets, reset offsets, and power-domain relationships.

Dependencies are the Linux platform bus, module/device-table support, regmap, CCF, Qualcomm alpha PLL/RCG/branch/reset/GDSC helpers, RPM-aware CC handling through `.use_rpm = true`, and the SM8750 binding header. Parent clock indexes must match the DT node's clock inputs. The Taycan ELU PLL ops and register layouts must be present in the shared Qualcomm PLL code.

### Integration Points
Consumers integrate through the `qcom,sm8750-camcc` device-tree compatible and the binding IDs in `qcom,sm8750-camcc.h`. Camera drivers request clocks for TFE, OFE, IFE-lite, IPE, ICP, JPEG, CSI/CSIPHY, and CAMNOC paths, and use reset IDs for block-level recovery or initialization. GDSCs expose power domains for Titan top plus IPE/OFE/TFE islands; IPE0 and OFE use `HW_CTRL_TRIGGER` in addition to polling and retention flags, signaling hardware-assisted power control. The critical CBCR list keeps DRV AHB, DRV XO, GDSC, and sleep clocks alive across unused-clock cleanup.

### Risks
The biggest risks are binding/table mismatches and hardware-data errors. The `cam_cc_sm8750_clocks` array is indexed directly by DT binding constants, so an omitted or shifted entry can return the wrong clock to a consumer. PLL Taycan ELU config values and post-divider choices are opaque hardware programming data; bad values can prevent lock or produce bad rates. OFE/TFE split paths increase the chance of assigning a consumer to the wrong real-time or non-real-time CAMNOC branch. Hardware-controlled GDSCs (`HW_CTRL_TRIGGER`) require correct sequencing assumptions in downstream drivers and firmware. Critical CBCR offsets are raw constants and should be checked against downstream power-collapse behavior.

### Test Signals
Strong validation includes SM8750 boot/probe logs, complete `debugfs` clock registration, `clk_summary` rate and prepare/enable counts during camera use, OFE/TFE/IPE camera pipeline tests at multiple sensor modes, reset-controller tests for each BCR, genpd attach/detach and runtime PM cycling for all GDSCs, suspend/resume with camera off and active, and late clock cleanup checks proving the critical DRV/GDSC/sleep CBCRs remain on. Schema checks should cover the compatible string, clock input order, and exported ID count against `qcom,sm8750-camcc.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm8750.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-x1e80100.c -->
## sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-x1e80100.c

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-x1e80100.c -->
