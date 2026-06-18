# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-suniv-f1c100s.c

Purpose: This driver describes the suniv F1C100s pin controller, a compact Allwinner F-series SoC with banks PA through PF and a mix of LCD/camera/storage/audio/touch functions.

Important APIs, types, and data: `suniv_f1c100s_pins[]` defines 53 pins: PA0-PA3, PB0-PB3, PC0-PC3, PD0-PD21, PE0-PE12, and PF0-PF5. Functions include `rtp`, `i2s`, `uart0`..`uart2`, `spi0`/`spi1`, `dram`, `i2c0`/`i2c1`, `lcd`, `csi`, `mmc0`, `jtag`, `ir0`, `ir`, `pwm0`, `pwm1`, `clk0`, and GPIO/IRQ. IRQ entries use mux `0x6` across three IRQ banks. `suniv_f1c100s_pinctrl_data` sets `.irq_banks = 3`.

Control flow: The platform driver matches `allwinner,suniv-f1c100s-pinctrl`. Probe calls `sunxi_pinctrl_init()` with the static descriptor.

State and persistence: The file contains only static pin descriptors. Runtime mux, GPIO, and IRQ settings are common-driver/hardware state and do not persist across reboot.

Dependencies and integration points: It integrates with DT pinctrl states for resistive touch, DRAM-related pins, LCD, CSI, MMC0, serial buses, audio, IR, PWM, clock output, JTAG, GPIO, and external interrupts. It uses the standard sunxi descriptor path without variant filtering.

Risks: Some mux names are unusual or typo-prone, including `dgb0` in the PF1 JTAG/debug entry, so binding/users must match existing names. DRAM-related alternate functions are board-critical. The absence of `.disable_strict_mode` means conflicts may be enforced more strictly than in many older sunxi files.

Test signals: Probe on F1C100s hardware, validate GPIO and IRQ across banks, test LCD/CSI/MMC0 and UART/I2C/SPI states, and check touch/audio/IR/PWM/clock outputs on boards that expose them.
