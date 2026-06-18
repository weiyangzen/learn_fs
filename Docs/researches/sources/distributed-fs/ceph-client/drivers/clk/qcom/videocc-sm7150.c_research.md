# sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm7150.c

Purpose: This file describes the Qualcomm SM7150 video clock controller. It registers a Fabia PLL, Iris and XO RCG sources, MVS0/MVS1/MVSC branch clocks, and Venus/vcodec GDSCs.

Important APIs, types, and functions: Key objects are `videocc_pll0`, `videocc_iris_clk_src`, `videocc_xo_clk_src`, `clk_branch` instances, `gdsc` definitions, and `videocc_sm7150_desc`. `videocc_sm7150_probe()` uses `qcom_cc_map()`, `clk_fabia_pll_configure()`, `qcom_branch_set_clk_en()` for `VIDEOCC_XO_CLK`, and `qcom_cc_really_probe()`.

Control flow: OF match `qcom,sm7150-videocc` loads the platform driver. Probe maps registers, programs PLL0 at offset `0x42c`, writes the XO CBCR at `0x984` on, then registers the descriptor. Later clock control is fully table-driven through CCF ops.

State and persistence: Hardware registers maintain PLL, RCG, branch, and GDSC state. GDSC `cxcs` arrays bind Venus and vcodec power domains to their core/AXI clock registers. There is no module-level mutable state beyond hardware.

Dependencies and integration: It depends on `dt-bindings/clock/qcom,sm7150-videocc.h`, Qualcomm clock helpers, regmap, platform bus, and the GDSC framework. Consumers include Venus/video codec nodes and any interconnect or power-domain users referencing the exported IDs.

Risks: Parent maps expose PLL main/even/odd as the same `videocc_pll0` hardware, which is a common Qualcomm table pattern but can be confusing when adding new rates. The always-on XO register is literal. GDSC polling and hardware trigger flags must match silicon.

Test signals: Compile, boot SM7150 DT, confirm `videocc-sm7150` probe, inspect video clocks and power domains, verify XO stays enabled, and run video decode/encode while watching clock framework and GDSC logs.
