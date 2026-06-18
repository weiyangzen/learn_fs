# sources/distributed-fs/ceph-client/drivers/clk/clk-cdce925.c


### Purpose
`clk-cdce925.c` supports the TI CDCE913/925/937/949 multi-PLL clock synthesizer family. It exposes chip-specific PLL and Y-output clocks and can configure output frequencies and spread-spectrum properties from device tree.

### Important APIs, Types, And Functions
`struct clk_cdce925_chip_info` records model-specific PLL/output counts. `struct clk_cdce925_chip` owns regmap and arrays of `clk_cdce925_pll` and `clk_cdce925_output`. PLL callbacks calculate and program N/M state with `cdce925_pll_find_rate()`, `cdce925_pll_prepare()`, and `cdce925_pll_unprepare()`. Output callbacks calculate p-dividers, program Y output divider registers, and activate or disable outputs. Custom `regmap_cdce925_bus` implements the device's I2C command protocol.

### Control Flow, State, And Persistence
Probe enables `vdd` and `vddout`, initializes a regcache-backed regmap, reads the parent crystal clock, applies optional `xtal-load-pf`, clears powerdown, registers PLL clocks, optionally applies child-node `clock-frequency` and spread-spectrum settings, registers Y1 as an input-clock child, registers other Y outputs as PLL children with `CLK_SET_RATE_PARENT`, and adds an OF provider. Runtime state is cached in each PLL's `m/n` and each output's `pdiv`; actual hardware programming happens mostly in prepare/unprepare because I2C operations can sleep.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include I2C transfers, regulator framework, regmap, DT compatibles for all four chip variants, a parent clock, and child node naming such as `PLL1`. Risks include first-come PLL rate allocation, cached `pdiv` not being persisted until prepare, no explicit provider removal in this file, register encoding edge cases for Q/R/P values, and different divider width for Y1 versus other outputs. This snapshot includes duplicated declarations/braces in visible source, so all variant build tests matter. Test signals include regulator failure paths, parent-clock absence, model-specific output counts, PLL bypass mode, PLL range rejection, output enable programming, OF output index lookup, spread-spectrum property writes, and I2C short-transfer handling.
