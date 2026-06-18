# sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm8750.c

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
