# sources/distributed-fs/ceph-client/drivers/clk/qcom/apss-ipq-pll.c

## Purpose
`apss-ipq-pll.c` is a shared APSS CPU PLL provider for several Qualcomm IPQ SoCs. It selects Huayra, Stromer, or Stromer Plus alpha PLL definitions and applies SoC-specific fixed configurations for CPU clock roots.

## Important APIs, Types, And Functions
Important objects are `ipq_pll_huayra`, `ipq_pll_stromer`, `ipq_pll_stromer_plus`, per-SoC `alpha_pll_config` structures for IPQ5018/IPQ5332/IPQ6018/IPQ8074/IPQ9574, `struct apss_pll_data`, and `apss_ipq_pll_probe()`. The probe uses `of_device_get_match_data()`, `clk_alpha_pll_configure()`, `clk_stromer_pll_configure()`, `devm_clk_register_regmap()`, and `devm_of_clk_add_hw_provider()`.

## Control Flow, State, And Persistence
Probe maps the PLL MMIO resource, creates a small regmap, fetches match data, configures the chosen PLL type, registers the single `a53pll` clock, and publishes it as an OF provider. Runtime persistence is the programmed PLL hardware state. The `SUPPORTS_DYNAMIC_UPDATE` flag allows later rate changes through the alpha PLL ops where supported.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include qcom alpha PLL helpers, DT compatibles, `xo` parent clock, IPQ APSS consumers, and Kconfig/Makefile wiring through `IPQ_APSS_PLL`. Risks include static PLL object reuse across multiple instances, unconditional reconfiguration of firmware-programmed PLLs, mismatched type/config pairs, and all variants exposing the same logical clock name. Test signals include provider probe for each compatible, CPU/APSS clock consumers obtaining `a53pll`, dynamic rate changes, register dumps matching expected L/config fields, and build coverage for Huayra and Stromer paths.
