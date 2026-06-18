# sources/distributed-fs/ceph-client/drivers/clk/clk-cdce706.c


### Purpose
`clk-cdce706.c` drives the TI CDCE706 programmable clock synthesizer over I2C. It exposes the input selector, three PLLs, six dividers, and six output clocks as a CCF hierarchy.

### Important APIs, Types, And Functions
`struct cdce706_dev_data` stores the I2C client, regmap, optional input clocks, and arrays of `cdce706_hw_data` for clkin, PLLs, dividers, and outputs. Register helpers wrap `regmap_read/write/update_bits()` with the device's command bit. Clock ops are `cdce706_clkin_ops`, `cdce706_pll_ops`, `cdce706_divider_ops`, and `cdce706_clkout_ops`; probe registers each layer through `cdce706_register_clkin()`, `cdce706_register_plls()`, `cdce706_register_dividers()`, and `cdce706_register_clkouts()`.

### Control Flow, State, And Persistence
Probe requires SMBus byte-data support, initializes regmap, reads the chip's existing mux/divider/multiplier state, registers clock hardware with device-managed lifetime, then installs `of_clk_cdce_get()` for output indices. PLL and divider determine-rate callbacks cache selected `mul`/`div` values in `cdce706_hw_data`, and set-rate callbacks persist those values into CDCE706 registers. Output prepare/unprepare toggles output enable bits; parent changes update mux fields.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include I2C, regmap, rational approximation, DT compatible `ti,cdce706`, optional `clk_in0` and `clk_in1` parent clocks, and CCF rate propagation via `CLK_SET_RATE_PARENT`. Risks include cached rate-selection state being shared between determine and set calls, invalid divider parent encodings, rate requests outside PLL VCO limits, and output parent mask handling. This snapshot shows duplicated source tokens around a register write/init initializer, so build coverage is a key signal. Tests should cover I2C read/write errors, OF clock index validation, input-source selection, PLL multiplier programming, divider reparenting, output enable/disable, and rate propagation from output to PLL.
