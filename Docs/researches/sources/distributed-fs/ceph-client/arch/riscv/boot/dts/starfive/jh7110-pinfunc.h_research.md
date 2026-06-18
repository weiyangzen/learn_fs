<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/starfive/jh7110-pinfunc.h -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/dts/starfive/jh7110-pinfunc.h

## Purpose
Defines StarFive JH7110 pinmux encoding helpers and signal IDs for devicetree pinctrl nodes.

## Important APIs, Types, And Functions
Important macros are `GPIOMUX(n, dout, doen, din)` and `PINMUX(n, func)`. Constants enumerate sys/aon output selectors, output-enable selectors, input selectors, `GPI_NONE`, and peripheral signals for UART, CAN, USB, QSPI/SPI, SPDIF, HDMI, I2C, SDIO, JTAG, PDM, I2S, TDM, PWM, GMAC, trace, watchdog, and wake GPIOs.

## Control Flow
No executable flow. DTS pinctrl entries expand these macros into packed cells consumed by the JH7110 pinctrl driver.

## State And Persistence
The bit layout and numeric selectors are persistent devicetree ABI for board files and overlays.

## Dependencies And Integration Points
Depends on JH7110 pinctrl binding/driver semantics and DTS preprocessing.

## Risks And Edge Cases
Wrong bit packing or selector numbers produce misrouted pins that are difficult to diagnose at runtime. The 0xff `GPI_NONE` sentinel must be preserved for outputs without an input path.

## Test Signals
Signals are dtbs_check pinctrl schema validation, board peripheral bring-up, and pinctrl debugfs showing expected mux, output-enable, and input selections.

Source read size: 308 lines, 9645 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/starfive/jh7110-pinfunc.h -->
