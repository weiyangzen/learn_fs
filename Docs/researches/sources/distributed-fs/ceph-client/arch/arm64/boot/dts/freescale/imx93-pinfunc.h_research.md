# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx93-pinfunc.h

### Purpose
`imx93-pinfunc.h` is the i.MX93 pin-function definition header for device trees. It supplies the `MX93_PAD_*__*` macro namespace used inside `fsl,pins` properties, with each macro expanding to `<mux_reg conf_reg input_reg mux_mode input_val>` and board DTS files adding the final pad-control value.

### Important APIs, Types, And Functions
There are no functions or structs. The interface consists of 609 `MX93_PAD_` macros spanning 108 pads and 516 unique signal functions. Coverage includes DAP/JTAG, GPIO_IO00 through GPIO_IO29, CCM_CLKO1-4, ENET1/ENET2, SD1/SD2/SD3, I2C1/I2C2, UART1/UART2, PDM, SAI1, and WDOG. Compared with i.MX91, this header uses i.MX93 naming conventions such as zero-padded GPIO/signal names, `S400_UART`, PDM stream names with two digits, and high mux-mode values like `0x10`, `0x11`, and `0x16` for LPI2C routes.

### Control Flow
The header participates only in compile-time DTS preprocessing. DTS files select a macro in a pin group; the resulting DTB stores five routing cells plus one config cell. At runtime the i.MX pinctrl driver consumes the cells and writes mux, config, and select-input registers. Macros with nonzero `input_reg` and `input_val` select daisy inputs for shared receiver functions, especially CAN, LPI2C, LPUART, PDM, SAI, SPDIF, USDHC3, and FLEXIO.

### State, Persistence, And Dependencies
The file has no local state. Its values persist only as programmed IOMUXC hardware state after the pinctrl driver applies a device-tree state. The include guard is `__DTS_IMX93_PINFUNC_H`, and the license is dual GPL-2.0+ or MIT. `imx91_93_common.dtsi` includes this file for the common i.MX91/i.MX93 base, and multiple i.MX93 board overlays include it directly for optional peripherals such as CAN, display, Wi-Fi/Bluetooth, JTAG, I3C, and PWM fan support.

### Integration Points
Primary consumers are `imx91_93_common.dtsi` and board `.dtso` files under the Freescale arm64 DTS tree. The macros integrate with the i.MX9 pinctrl binding and the i.MX pinctrl driver through the standard `fsl,pins` tuple shape. They also cross-reference peripheral nodes that use separate clock/power/interrupt bindings, so a pin macro is only one part of enabling a peripheral; clocks, resets, supplies, and controller status must also be correct.

### Risks
The risk profile is register-accuracy and board-routing accuracy. i.MX91 and i.MX93 share many pad names but differ in input register offsets, mux mode encodings, and function names, so using the wrong SoC header can produce a DTB that compiles but programs incorrect hardware. Nonzero daisy selections are easy to miss during review because the macro name looks sufficient. Some peripheral names in this file refer to SoC-specific internal blocks, such as S400 or CCMSRCGPCMIX, which should not be normalized without checking the reference manual and existing board DTS usage.

### Test Signals
Validation should include `make dtbs` for i.MX93 targets, `dtbs_check` against `fsl,imx9-pinctrl.yaml`, and board-level tests for the overlays that include this file. High-signal hardware checks include UART5 flow control on DAP pins, USDHC3 Wi-Fi/SDIO pin groups, display media pin groups, CAN1 on PDM pads, JTAG on GPIO_IO24-27, I3C on I2C pads, and any route using mux modes `0x10`, `0x11`, or `0x16`.
