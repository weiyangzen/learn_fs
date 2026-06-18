# sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm8450.c

### Purpose
`dispcc-sm8450.c` is the Display Clock Controller driver for SM8450 and SM8475. It exposes a high-end MDSS clock tree with two display PLLs, dual DSI byte/pixel roots, four DPTX groups with AUX/link/pixel/crypto/interface clocks, MDP/ROT/PCLK/VSYNC roots, sleep/XO sources, RSCC support clocks, two MDSS GDSCs, and core/INT2/RSCC resets.

### Important APIs, Types, And Functions
The driver uses `clk_alpha_pll`, `clk_rcg2`, `clk_regmap_div`, `clk_regmap_mux` support, `clk_branch`, `gdsc`, reset maps, PM runtime, regmap, and `qcom_cc_desc`. `disp_cc_sm8450_probe()` enables runtime PM, maps registers, selects either Lucid Evo or SM8475 Lucid OLE PLL setup, updates the MDP clock-gating register `DISP_CC_MISC_CMD`, keeps XO enabled, registers the descriptor, and balances PM runtime references on success and failure.

### Control Flow
The OF table matches `"qcom,sm8450-dispcc"` and `"qcom,sm8475-dispcc"`. Probe enables and resumes the hardware before touching registers. For SM8475, it changes PLL register tables to `CLK_ALPHA_PLL_TYPE_LUCID_OLE`, swaps both PLL init structures to reset Lucid OLE ops, and configures PLLs with SM8475-specific control/test values. Otherwise it uses Lucid Evo reset ops and configs. After PLL setup, it enables MDP clock gating with `regmap_update_bits(regmap, DISP_CC_MISC_CMD, 0x10, 0x10)`, forces `DISP_CC_XO_CLK` at `0xe05c`, registers the clocks/GDSCs/resets, and releases runtime PM.

### State And Persistence
Hardware state spans a `0x11008` regmap. State includes PLL0/PLL1 programming, root generator parent/rate selections, byte and DPTX link dividers, branch enables, reset bits, `mdss_gdsc` at `0x9000`, and `mdss_int2_gdsc` at `0xb000`. The SM8475 path mutates static PLL descriptors for the module lifetime, which is acceptable for one compatible instance but important for reasoning about reprobe.

### Dependencies And Integration Points
Dependencies include `qcom,sm8450-dispcc.h`, PM runtime, regmap, CCF, Qualcomm alpha PLL/branch/RCG/divider/mux/common helpers, GDSC/reset helpers, DSI PHY parents, four DP PHY parent pairs, AHB/sleep/XO DT parents, and DRM/MSM display consumers. The two GDSCs integrate with Linux generic power domains.

### Risks
The large clock table increases binding-alignment risk. SM8475 mutates PLL descriptor ops/register tables at probe time, so partial failure and later reprobe must remain consistent. Four DPTX groups have many near-identical branch and divider definitions; wrong offsets or parent maps can break only one port. Runtime PM cleanup uses `pm_runtime_put_sync()` on failures and `pm_runtime_put()` on success; changes must preserve balance.

### Test Signals
Validation should cover both compatibles. Check probe, PM runtime balance, PLL rates, all DPTX AUX/link/pixel clocks, DSI byte/pixel clocks, MDP/ROT/VSYNC rates, two GDSC domains, reset controls, multi-display modesets, and suspend/resume across active DP and DSI outputs.
