# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-s500.c

Purpose: this is the Actions OWL S500 CMU driver. It declares all S500 PLLs, muxes, gates, dividers, factor clocks, composites, DT clock IDs, reset IDs, and the platform driver for `actions,s500-cmu`.

Important structures: register offset macros describe CMU layout through `0x00fc`, though the shared regmap max covers clock fields through `0x00cc`. PLLs include Ethernet, core, DDR, NAND, display, dev, and audio; audio uses a two-entry table for 45.1584/49.152 MHz. Tables define SD, display engine, HDE, RMII, I2S, standard, and NAND divisors. `s500_clks[]` lists every `owl_clk_common`, `s500_hw_clks` maps DT `CLK_*` IDs to `clk_hw`, and `s500_resets[]` maps reset binding IDs to CMU reset bits.

Control flow/state: `s500_clk_probe()` initializes the regmap, allocates/registers a reset controller, and calls `owl_clk_probe()`. Static descriptors persist for the lifetime of the kernel; hardware registers hold clock state.

Dependencies/integration: depends on OWL helper macros, Actions S500 clock/reset DT bindings, platform driver matching, and common clock/reset frameworks.

Risks and tests: the probe ignores the return from `owl_clk_regmap_init()`. Several clocks are `CLK_IGNORE_UNUSED` to protect firmware-enabled UART/SPI/PLL state. Shared gates are reused for related clocks such as NAND/ECC and sensors. Test signals are boot on S500, DT clock/reset consumer lookup, peripheral bring-up for UART/I2C/SD/NAND/display/audio, and reset status polarity.
