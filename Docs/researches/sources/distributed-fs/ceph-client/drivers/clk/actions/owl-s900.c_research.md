# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-s900.c

Purpose: this is the Actions S900 CMU driver for `actions,s900-cmu`, covering a larger clock tree with display, GPU, DDR, USB, EDP, NAND, SD, I2C, UART, and sensor clocks plus resets.

Important structures: the file defines register offsets through `CMU_PWM5CLK`, audio and EDP PLL tables, PLLs for core/dev/DDR/NAND/display/assist/audio/EDP, parent arrays, divider tables for NAND/APB/Ethernet/USB/I2S/HDMI audio, factor tables for SD/DMM/NOC/BISP, static clock instances, `s900_clks[]`, `s900_hw_clks`, and `s900_resets[]`. S900 includes EDP fixed and PLL clocks, multiple GPU clocks, dual NAND clocks, six I2C clocks, four SD clocks, DDR gates marked `CLK_IGNORE_UNUSED`, and a PWM2 backlight protection comment.

Control flow/state: `s900_clk_probe()` initializes regmap, registers the reset controller, then registers all clocks as a onecell provider. State is static descriptor data plus CMU hardware register contents.

Dependencies/integration: integrates with Actions S900 DT clock/reset bindings and common OWL helpers. It exposes clock IDs consumed by peripheral DT nodes.

Risks and tests: regmap init return is ignored. Several clocks intentionally preserve boot state with `CLK_IGNORE_UNUSED`; removing those flags may blank displays or break serial/DDR. UART1 uses shift `1` while other UARTs use `0`, which deserves hardware validation. Test signals include S900 board boot, EDP/display/GPU/USB/NAND/SD/UART devices, reset lines, and `clk_summary` parent/rate sanity.
