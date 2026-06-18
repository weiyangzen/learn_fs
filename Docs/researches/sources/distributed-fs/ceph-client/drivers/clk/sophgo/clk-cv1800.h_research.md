# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv1800.h

## Purpose
This header defines CV1800/CV1810 clock count limits and register offsets for PLL and clock-generator blocks. It is the register map contract consumed by the CV18xx top-level, PLL, and IP clock descriptions.

## Important APIs, Types, And Functions
`CV1800_CLK_MAX` and `CV1810_CLK_MAX` size the onecell arrays based on dt-binding IDs. The file defines PLL G2 and G6 control/status/SSC/synthesizer registers, fractional APLL registers, PLL output clock CSR registers, camera source divider registers, clock enable registers `REG_CLK_EN_0` through `REG_CLK_EN_4`, mux/bypass registers, and a large set of divider registers for CPU, TPU, storage, Ethernet, GPIO, SDMA audio, camera, AXI, DSI, VIP, codec, SPI, I2C, audio source, PWM, debug, RTC, C906, and VIP extension paths.

## Control Flow
No executable code exists. The constants are embedded into static clock declarations and pre-init functions in `clk-cv1800.c` and into register operations in the CV18xx helper files.

## State And Persistence
The constants describe persistent hardware registers relative to the controller base. Runtime writes using these offsets determine gate, divider, mux, bypass, PLL, and synthesizer state.

## Dependencies And Integration Points
The header includes `dt-bindings/clock/sophgo,cv1800.h`, so ID limits track public Device Tree ABI. It integrates with the CV1800 aggregate module and all CV18xx clock-class helpers that interpret fields at these offsets.

## Risks
Register offset mistakes propagate into all macros using the constant. `CV1800_CLK_MAX` and `CV1810_CLK_MAX` must remain synchronized with dt-bindings; otherwise provider arrays can omit clocks or expose invalid IDs. Hardware revision differences between CV1800, CV1810, and SG2000 need explicit handling in the descriptor layer.

## Test Signals
Compile checks catch missing constants but not wrong offsets. Runtime smoke tests should read back selected registers after enabling, setting rates, or changing parents for representative PLL, divider, mux, and gate clocks on each SoC variant.
