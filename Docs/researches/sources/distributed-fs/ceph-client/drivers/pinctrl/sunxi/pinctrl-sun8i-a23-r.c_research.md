# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/pinctrl-sun8i-a23-r.c

Purpose: This driver describes the A23 reduced/always-on pin controller, covering the special PL bank used for standby and low-power peripherals.

Important APIs, types, and data: `sun8i_a23_r_pins[]` defines PL0-PL11. Every pin supports GPIO in/out, most have interrupt function `SUNXI_FUNCTION_IRQ_BANK(0x4, 0, n)`, and peripheral functions include `s_rsb`, `s_i2c`, `s_uart`, `s_jtag`, `s_twi`, and `s_pwm`. The descriptor sets `.pin_base = PL_BASE`, `.irq_banks = 1`, and `.disable_strict_mode = true`.

Control flow: The platform driver matches `allwinner,sun8i-a23-r-pinctrl`. Probe calls `sunxi_pinctrl_init()` with the static descriptor, registering the PL pins with the shared sunxi pinctrl implementation.

State and persistence: All source-level pin metadata is const. Runtime mux, GPIO direction/value, and IRQ setup are managed by the common driver and hardware registers, with no persistent storage in this file.

Dependencies and integration points: The `PL_BASE` numbering convention links this special controller to the wider sunxi pin numbering scheme. It integrates with DT pinctrl consumers for PMIC/control buses (`s_rsb`, `s_i2c`, `s_twi`), standby UART, standby JTAG, standby PWM, GPIO, and wake-capable EINT.

Risks: Low-power bus pins are board-critical; wrong mux values can prevent PMIC access or wake behavior. IRQ mux `0x4` and the PL interrupt numbering must match the hardware. Because strict mode is disabled, runtime conflicts rely on board definitions and testing.

Test signals: Probe the A23 R controller, verify PL0/PL1 RSB or I2C operation, test PL EINT lines including wake from suspend, and validate GPIO direction/value on non-bus pins.
