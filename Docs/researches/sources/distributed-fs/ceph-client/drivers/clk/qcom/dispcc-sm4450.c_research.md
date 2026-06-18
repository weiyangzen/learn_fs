# sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm4450.c

### Purpose
`dispcc-sm4450.c` is the SM4450 Display Clock Controller driver. It describes a newer single-DSI MDSS clock tree with two Lucid Evo display PLL instances, AHB/MDP/ROT/PCLK/VSYNC roots, byte and escape clocks, two MDSS core GDSCs, and core/RSCC reset lines.

### Important APIs, Types, And Functions
The driver uses `clk_alpha_pll` for `disp_cc_pll0` and `disp_cc_pll1`, `clk_rcg2` for programmable roots, `clk_regmap_div` for byte dividers, `clk_branch` for gate/halt controlled leaf clocks, `gdsc` for `disp_cc_mdss_core_gdsc` and `disp_cc_mdss_core_int2_gdsc`, and `qcom_cc_desc` for registration. `disp_cc_sm4450_probe()` maps registers, configures both PLLs with `clk_lucid_evo_pll_configure()`, forces sleep/XO branches on with `qcom_branch_set_clk_en()`, and registers the descriptor.

### Control Flow
The OF match table binds `"qcom,sm4450-dispcc"`. Probe maps the controller using `qcom_cc_map()`, programs both PLLs with the 600 MHz Lucid Evo config, marks `DISP_CC_SLEEP_CLK` and `DISP_CC_XO_CLK` always enabled at offsets `0xe070` and `0xe054`, then calls `qcom_cc_really_probe()`. After registration, clock operations are data-driven through the static parent maps and frequency tables.

### State And Persistence
State lives in hardware registers under the `0x11008` regmap window. PLL0 and PLL1 register programming persists until reset or power loss. GDSC descriptors model two power islands at `0x9000` and `0xb000` with `HW_CTRL`, polling, and `RETAIN_FF_ENABLE`. Reset lines cover MDSS core, MDSS core INT2, and RSCC at `0x8000`, `0xa000`, and `0xc000`.

### Dependencies And Integration Points
The driver depends on DT parent indices for XO, always-on XO, AHB, sleep, and DSI0 PHY clocks from `qcom,sm4450-dispcc.h`. It integrates with MDSS display consumers through exported `DISP_CC_*` IDs, with power-domain consumers through GDSC registration, and with reset consumers through Qualcomm reset maps.

### Risks
Both PLLs use the same config object; this is intentional for this hardware but fragile if future SM4450 revisions need distinct rates. The `_ao` parent data is only safe if the binding order stays fixed. Always-on sleep/XO branch programming is done before `qcom_cc_really_probe()`, so wrong offsets can leave critical clocks gated or inadvertently enable unrelated branches. The dual-GDSC model requires display consumers to reference the correct domain.

### Test Signals
Probe success, visible `disp_cc_pll0`/`disp_cc_pll1` rates, MDP/ROT rates from debugfs, DSI panel modeset, GDSC retention behavior across blanking, and reset exercise for core/INT2/RSCC are the main validation signals.
