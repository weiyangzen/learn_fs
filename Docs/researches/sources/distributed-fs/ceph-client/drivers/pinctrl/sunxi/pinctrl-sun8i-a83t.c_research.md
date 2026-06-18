# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-a83t.c

Purpose: This is the main pinctrl driver for the Allwinner A83T SoC. It defines the static mux table for 105 pins across PB, PC, PD, PE, PF, PG, and PH.

Important APIs, types, and data: `sun8i_a83t_pins[]` uses sunxi descriptor macros to expose GPIO, IRQ, and peripheral mux functions. Major functions include `uart0`..`uart4`, `i2c0`..`i2c3`, `spi0`/`spi1`, `mmc0`..`mmc2`, `nand0`, `lcd`, `csi`, `i2s`, `pwm`, and related multimedia/storage functions. IRQ functions use mux `0x6` across three IRQ banks, covering PB, PG, and PH groups. The descriptor sets `.irq_banks = 3` and `.disable_strict_mode = true`.

Control flow: OF match on `allwinner,sun8i-a83t-pinctrl` binds the platform driver. Probe calls `sunxi_pinctrl_init()` with the static descriptor, and the common core registers the pin groups, GPIO chips, and IRQ domains.

State and persistence: Pin data is static and read-only. Active mux selections, GPIO values, and IRQ state are runtime hardware/common-driver state only.

Dependencies and integration points: The file depends on the shared sunxi pinctrl macros and core. Integration points are DT pinctrl states for storage, display, camera, serial, audio, PWM, GPIO, and external interrupt consumers.

Risks: A83T has several high-pin-count peripheral groups; incomplete DTS states can leave buses partially muxed. IRQ bank mapping must match PB/PG/PH EINT layout. Since strict mode is disabled, duplicate pin ownership may be detected only by board behavior.

Test signals: Probe on A83T hardware, validate GPIO per bank, exercise all three IRQ banks, and run representative pinctrl states for MMC/NAND, LCD, CSI, UART/I2C/SPI, I2S, and PWM.
