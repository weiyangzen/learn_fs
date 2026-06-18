# sources/distributed-fs/ceph-client/drivers/clk/qcom/a7-pll.c

## Purpose
`a7-pll.c` registers the SDX55/SDX65 Qualcomm A7 CPU PLL. It models a Lucid alpha PLL named `a7pll`, configured from a fixed table when the hardware L register indicates the PLL is not already configured.

## Important APIs, Types, And Functions
The driver centers on static `struct clk_alpha_pll a7pll`, `struct alpha_pll_config a7pll_config`, `lucid_vco`, and `qcom_a7pll_probe()`. It uses `clk_alpha_pll_lucid_ops`, `clk_lucid_pll_configure()`, `devm_clk_register_regmap()`, and `devm_of_clk_add_hw_provider()`. The sole OF compatible is `qcom,sdx55-a7pll`.

## Control Flow, State, And Persistence
Probe maps MMIO, creates a regmap over a 0x1000 register range, reads the Lucid PLL L register at `offset + 0x04`, configures the PLL only if that value is zero, registers the PLL as a regmap-backed clock, and adds an OF clock provider. Runtime state persists in PLL registers. The static clock object is shared by the module instance, so the DT binding effectively expects one controller instance.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include the qcom alpha PLL framework, platform MMIO resources, the `bi_tcxo` parent clock, and the APCS SDX55 mux driver that consumes `pll`. Risks include relying on nonzero L as proof that firmware configured the PLL correctly, static object reuse if multiple matching devices appeared, missing explicit error logging, and incorrect VCO/config values affecting CPU stability. Test signals include boot-time provider registration, no reconfiguration when boot firmware already programmed L, CPUfreq transitions through the APCS mux, and clk summary showing `a7pll` with the expected parent and rate.
