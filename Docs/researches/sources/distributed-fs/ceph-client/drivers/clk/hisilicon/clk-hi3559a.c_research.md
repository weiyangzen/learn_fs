# sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi3559a.c

Purpose: implements Hi3559AV100 CRG and sensor-hub clock providers, including fixed-rate roots, muxes, gates, custom PLLs, SHUB dividers, default SHUB programming, and reset-controller integration.

Important APIs/types/functions: CRG descriptors include `hi3559av100_fixed_rate_clks_crg`, mux tables for FMC/MMC/sysbus/UART/A73, `hi3559av100_gate_clks`, and custom PLL descriptors `hi3559av100_pll_clks`. PLL ops are `clk_pll_set_rate()` and `clk_pll_recalc_rate()`. SHUB descriptors include fixed-rate I2C/UART sources, `hi3559av100_shub_mux_clks`, divider tables, and SHUB gates. `hisi_crg_funcs` selects CRG versus SHUB registration.

Control flow: matched probe initializes reset, calls the selected registration function, and stores `hisi_crg_dev`. CRG registration allocates onecell data, registers fixed rates, custom PLLs, muxes, gates, and provider. SHUB registration first calls `hi3559av100_shub_default_clk_set()` to program SSP/UART defaults through an absolute `ioremap()`, then registers fixed rates, muxes, dividers, gates, and provider.

State and persistence: CRG/SHUB register state persists while powered. PLL state is custom `clk_hw` memory allocated with devm. Default SHUB setup directly mutates global CRG registers.

Dependencies and integration points: uses Hisilicon shared helpers, `crg.h`, `reset.h`, DT bindings, OF match compatibles `hisilicon,hi3559av100-clock` and `hisilicon,hi3559av100-shub-clock`.

Risks: fixed-rate `"148p5m"` is set to `1485000000`, likely 10x the name. PLL calculation ignores `parent_rate` and uses hardcoded 24 MHz in recalc. SHUB default setup uses physical `CRG_BASE_ADDR` instead of the platform resource and does not check `ioremap()` failure. Custom PLL registration logs failures but continues, leaving missing IDs.

Test signals: compare exported rates to hardware manual, especially PLL and 148.5 MHz paths; boot both CRG and SHUB providers; verify reset consumers; test SHUB SPI/UART divider defaults; and fault-inject failed PLL registration/provider setup.
