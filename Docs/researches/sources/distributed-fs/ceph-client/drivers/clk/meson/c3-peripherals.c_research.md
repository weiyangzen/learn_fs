# sources/distributed-fs/ceph-client/drivers/clk/meson/c3-peripherals.c

## Purpose
`c3-peripherals.c` describes the Amlogic C3 peripheral clock controller. It is mostly declarative clock-tree data: RTC, system/APB gates, AXI gates, 12/24 MHz output, general-purpose clocks, PWM, SPI, eMMC/SD, transport stream, Ethernet, display, video codec, ISP, NNA, GE2D, and VAPB clocks. The controller is exposed as a platform driver for `amlogic,c3-peripherals-clkc`.

## Important APIs, Types, And Functions
The file defines register offsets for the C3 peripheral clock block and uses `struct clk_regmap`, `struct clk_fixed_factor`, `struct clk_parent_data`, `struct meson_clk_dualdiv_param`, and `struct meson_clkc_data`. `C3_SYS_PCLK()` and `C3_AXI_PCLK()` wrap `MESON_PCLK()` gate declarations, while `C3_COMP_SEL()`, `C3_COMP_DIV()`, and `C3_COMP_GATE()` build common mux/divider/gate triplets. The final `c3_peripherals_hw_clks[]` array maps dt-binding `CLKID_*` indices to `clk_hw` objects, and `c3_peripherals_clkc_driver` delegates probe to `meson_clkc_mmio_probe()`.

## Control Flow
There is no custom runtime algorithm. At platform probe, `meson_clkc_mmio_probe()` ioremaps the clock controller register resource, creates a regmap, registers each non-null hardware clock from `c3_peripherals_clkc_data`, and installs the OF clock provider. Later common clock framework calls operate through the generic regmap gate, mux, divider, fixed-factor, and dual-divider ops selected in each initializer.

## State, Persistence, And Dependencies
State persists in the C3 clock controller registers and in kernel `clk_hw` registrations. Gate clocks mutate individual enable bits in `SYS_CLK_EN0_REG*`, `AXI_CLK_EN0`, and per-block clock-control registers. Muxes and dividers mutate parent-select and divisor bitfields. The RTC 32 kHz path uses `meson_clk_dualdiv_ops` with a table entry designed to synthesize 32.768 kHz from the oscillator. Dependencies include `clk-regmap.h`, `clk-dualdiv.h`, `meson-clkc-utils.h`, Linux common clock framework APIs, platform-device probing, and `dt-bindings/clock/amlogic,c3-peripherals-clkc.h`.

## Integration Points
The dt-binding IDs are the public contract for device-tree consumers. Parent clocks are resolved by firmware names such as `oscin`, `xtal_24m`, `sysclk`, `axiclk`, `fix`, `gp0`, `gp1`, `hifi`, and fixed PLL divider names. Several clocks are marked `CLK_IS_CRITICAL` because disabling them would break CPU control, interrupt routing, GIC, system NIC, or CPU-to-DDR access. Media and peripheral drivers consume the registered clocks through normal `clocks = <&clkc CLKID_...>` phandles.

## Risks And Edge Cases
The file is data-heavy, so the main risks are wrong register offsets, parent order, bit shifts, or dt-binding indices. Critical-clock annotations are part of platform safety; missing one can allow Linux unused-clock cleanup to disable essential interconnects. Some comments describe hardware quirks: DDR-related `sys_mmc_pclk` is read-only because firmware initializes DDR, and some divider encodings have non-obvious zero behavior. Sparse `c3_peripherals_hw_clks[]` entries also need to stay aligned with the binding header.

## Test Signals
Useful signals include kernel build coverage with C3 clock configs enabled, probe success for `amlogic,c3-peripherals-clkc`, `clk_summary` inspection for all expected IDs, parent/rate changes for PWM/SPI/eMMC/Ethernet/display/video clocks, RTC 32 kHz rate checks, and boot tests verifying critical clocks remain enabled. Device-tree validation should confirm all provider references use valid C3 peripheral IDs.
