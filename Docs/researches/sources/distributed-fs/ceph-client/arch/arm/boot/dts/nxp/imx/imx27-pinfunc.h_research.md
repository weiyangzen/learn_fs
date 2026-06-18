# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx27-pinfunc.h

Purpose: i.MX27 pin-function binding header for DTS pinctrl groups. It names pad/function alternatives for a six-port legacy i.MX mux controller.

Important APIs/types/functions: macros use `MX27_PAD_<pad>__<function> <pin> <mux_id>`. The documented `mux_id` packs function, direction, GPIO output config, and GPIO input config fields. `pin` is `PORT * 32 + PORT_PIN`, covering six 32-pin ports. Exports cover USB host, LCD, SD/MSHC, CSI, UART, SSI, I2C, SPI, FEC, keypad, ATA/PCMCIA, ETM trace, CLKO, GPIO, and memory bus pins. The include guard is `__DTS_IMX27_PINFUNC_H`.

Control flow: no executable flow. Macro expansion happens at DTB build time; runtime behavior is in the i.MX pinctrl driver.

State and persistence: the header is stateless. The compiled DTB persists board pin selections and pinctrl programs registers at boot/probe time.

Dependencies and integration: consumed by i.MX27 `.dts`/`.dtsi` files. It integrates with the legacy i.MX pinctrl binding that decodes a two-cell pin and mux identifier.

Risks: i.MX27 has many alternate functions on LCD, CSI, ATA, and communication pins. Values can compile while selecting the wrong direction or GPIO input mode. Test with full i.MX DTB builds, targeted DTB builds for modified boards, and hardware checks of display, camera, SD, USB host, FEC, ATA/PCMCIA, and console paths.
