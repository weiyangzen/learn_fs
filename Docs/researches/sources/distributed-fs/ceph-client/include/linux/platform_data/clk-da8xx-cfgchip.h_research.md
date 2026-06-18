# sources/distributed-fs/ceph-client/include/linux/platform_data/clk-da8xx-cfgchip.h

Purpose: defines platform data for the TI DaVinci DA8xx CFGCHIP clock driver.

Important APIs and types: `struct da8xx_cfgchip_clk_platform_data` carries a `struct regmap *cfgchip` pointing at the CFGCHIP syscon register block.

Control flow: platform code creates the clock device with this regmap; the clock driver uses it to read/modify CFGCHIP bits that gate or select DA8xx miscellaneous clocks.

State and persistence: the regmap points to hardware-backed system configuration registers. Platform data itself is static; clock state is runtime register state.

Dependencies and integration points: depends on `linux/regmap.h` and integrates platform devices, syscon/regmap, and common clock framework providers.

Risks and test signals: risks include invalid regmap lifetime, incorrect CFGCHIP bit updates affecting unrelated functions, and clock registration before syscon availability. Test clock registration, enable/disable/set-parent operations, concurrent regmap users, probe deferral, and suspend/resume register state.
