# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-a33.c

Purpose: This driver describes the Allwinner A33 main pin controller. It is based on the A23 table but starts at PB and reflects A33-specific muxing, especially alternate UART and multimedia functions.

Important APIs, types, and data: `sun8i_a33_pins[]` defines 96 pins across PB, PC, PD, PE, PF, PG, and PH, with PA absent. Functions include `uart0`..`uart4`, `i2c0`..`i2c2`, `spi0`/`spi1`, `mmc0`..`mmc2`, `nand0`, `lcd`, `csi`, `i2s0`, `i2s1`, `pwm0`, and `pwm1`. IRQ functions use mux `0x4` across two IRQ banks, PB and PG. The descriptor sets `.irq_banks = 2` and `.disable_strict_mode = true`.

Control flow: The platform driver matches `allwinner,sun8i-a33-pinctrl`. Probe calls `sunxi_pinctrl_init()` with `sun8i_a33_pinctrl_data`, after which the common core registers pinctrl, GPIO, and IRQ services.

State and persistence: Static pin descriptors are immutable. Runtime mux selection and GPIO/IRQ state live in shared sunxi structures and MMIO registers; no persistent state exists.

Dependencies and integration points: It depends on `pinctrl-sunxi.h` and Linux platform/OF infrastructure. Integration is through DT pinctrl states consumed by UART, I2C, SPI, MMC, NAND, display, camera, audio, PWM, and GPIO users.

Risks: Because the table is similar to A23 but not identical, copy-forward mistakes are plausible. PB carries both UART2 and UART0 alternatives on early pins, making board states easy to misconfigure. IRQ bank count and mux value must match PB/PG EINT layout. Disabled strict mode can conceal multi-consumer conflicts until runtime.

Test signals: Build and boot with `allwinner,sun8i-a33-pinctrl`, verify PB and PG external interrupts, test UART0 remap options, and exercise storage/display/camera/audio pin groups on a representative A33 board.
