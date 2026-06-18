# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx1-pinfunc.h

Purpose: i.MX1 pin-function binding header for DTS pinctrl nodes. It names pad/function combinations for the first-generation i.MX mux controller.

Important APIs/types/functions: macros use `MX1_PAD_<pad>__<function> <pin> <mux_id>`. The comment documents the two-cell tuple: `<pin mux_id>`. `pin` is `PORT * 32 + PORT_PIN` across four 32-pin ports. `mux_id` packs function, direction, GPIO output config, and GPIO input config fields. Exported functions cover address/data bus, CSI, I2C, SPI, SD/MS, SIM, UART, LCD, timer, PWM, and GPIO alternatives. The file has include guard `__DTS_IMX1_PINFUNC_H`.

Control flow: no executable flow. DTS preprocessing expands the selected macro into the two-cell pinctrl value consumed by the i.MX pinctrl driver.

State and persistence: stateless header. Board DTBs persist selected pad functions; hardware state is programmed by pinctrl at runtime.

Dependencies and integration: consumed by i.MX1 DTS files and the legacy i.MX pinctrl binding that expects the two-cell tuple. It integrates board pad names with driver mux register programming.

Risks: the packed `mux_id` is compact and easy to misencode. GPIO direction/input configuration bits are part of the macro value, so a wrong alias can compile but leave a pin electrically wrong. Test with `make ARCH=arm dtbs`, schema checks where available, and hardware validation for boot bus, SD, serial console, LCD, and GPIO interrupts.
