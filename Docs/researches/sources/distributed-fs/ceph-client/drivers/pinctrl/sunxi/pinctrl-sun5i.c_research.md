# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun5i.c

Purpose: This driver describes the pin controller for sun5i-family SoCs: Allwinner A10s, A13, and NextThing GR8. It is a classic static sunxi pin table, enumerating 119 pins across banks A through G and their mux alternatives for GPIO, storage, display, camera, audio, serial, network, and interrupt use.

Important APIs, types, and data: The variant bits `PINCTRL_SUN5I_A10S`, `PINCTRL_SUN5I_A13`, and `PINCTRL_SUN5I_GR8` gate pins and functions that exist only on specific chips. `sun5i_pins[]` is an array of `struct sunxi_desc_pin` built with `SUNXI_PIN`, `SUNXI_PIN_VARIANT`, `SUNXI_FUNCTION`, `SUNXI_FUNCTION_VARIANT`, and `SUNXI_FUNCTION_IRQ`. Banks include PA0-PA17, PB0-PB20, PC0-PC19, PD0-PD27, PE0-PE11, PF0-PF5, and PG0-PG13, with several documented holes. Major functions include `emac`, `ts0`, `keypad`, `uart0`..`uart3`, `i2c0`..`i2c2`, `spi0`/`spi1`, `nand`, `mmc0`/`mmc1`/`mmc2`, `lcd`, `csi`, `i2s`, `pwm`, `ir`, and `jtag`. The descriptor sets `.irq_banks = 1` and `.disable_strict_mode = true`.

Control flow: OF matching selects one of three compatible strings and stores the matching variant bit in `.data`. `sun5i_pinctrl_probe()` retrieves that with `of_device_get_match_data()` and calls `sunxi_pinctrl_init_with_flags()`, causing the common pinctrl code to filter variant-gated entries and register pinctrl/GPIO/IRQ resources.

State and persistence: The pin/function table is read-only static kernel data. Runtime state such as selected muxes, GPIO state, and IRQ handlers lives in the shared sunxi pinctrl core and hardware registers. There is no persistence across reboot.

Dependencies and integration points: This file depends on the common sunxi macros and core registration in `pinctrl-sunxi.h`. It integrates with board DT nodes using compatible strings `allwinner,sun5i-a10s-pinctrl`, `allwinner,sun5i-a13-pinctrl`, and `nextthing,gr8-pinctrl`; downstream peripheral drivers consume the named functions through pinctrl states.

Risks: The main risks are variant mistakes, especially exposing A10s/GR8-only pins to A13 or hiding shared pins from GR8. `.disable_strict_mode` permits mux sharing patterns that can be necessary on older SoCs, but it weakens conflict detection. The single IRQ bank and `SUNXI_FUNCTION_IRQ(0x6, n)` encoding must match the external interrupt hardware.

Test signals: Build coverage should catch macro/descriptor errors. Runtime validation should cover each compatible, probe variant filtering, GPIO toggling per bank, EINT handling, and representative peripheral states: MMC, NAND, LCD, CSI, EMAC, UART, I2C, SPI, I2S, PWM, and IR.
