# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx91-pinfunc.h

### Purpose
`imx91-pinfunc.h` is the i.MX91 device-tree pin-function catalog consumed by i.MX pinctrl nodes. It defines the symbolic `MX91_PAD_*__*` macros that expand to the five-cell pinmux tuple documented by the Freescale i.MX pinctrl bindings: `<mux_reg conf_reg input_reg mux_mode input_val>`. DTS pin groups then append the sixth pad-configuration cell in `fsl,pins`.

### Important APIs, Types, And Functions
There are no C functions or runtime types. The public surface is a preprocessor ABI with 650 `MX91_PAD_` macros over 108 physical pads and 510 unique alternate functions. Major pad groups include DAP/JTAG, GPIO_IO00 through GPIO_IO29, CCM clock outputs, ENET1/ENET2 RGMII pins, USDHC SD1/SD2/SD3 pins, I2C1/I2C2, UART1/UART2, PDM, SAI1, and WDOG. Each macro name encodes both the physical pad and selected signal, while the numeric tuple encodes IOMUXC register offsets, mux mode, and optional daisy-chain input select value.

### Control Flow
This header has no executable control flow. Build-time preprocessing substitutes each macro into DTS `fsl,pins` arrays. At boot, the compiled DTB is interpreted by the i.MX pinctrl driver, which writes the mux register, pad configuration register, and select-input register when `input_reg` is nonzero. The macros with `input_reg` set select one of several candidate pads for receiver paths such as CAN, LPI2C, LPUART, PDM, SAI, SPDIF, USDHC3, or FLEXIO.

### State, Persistence, And Dependencies
The file holds no mutable state. Its values become persistent hardware configuration only after board DTS files instantiate pin groups and the kernel programs the IOMUXC registers. The include guard is `__DTS_IMX91_PINFUNC_H`, and the license is dual GPL-2.0+ or MIT. It is directly included by `imx91.dtsi`, which sets `&iomuxc` compatible to `fsl,imx91-iomuxc`, and is paired with the shared `imx91_93_common.dtsi` SoC description.

### Integration Points
The integration contract is the i.MX9 `fsl,pins` binding: one `MX91_PAD_*` macro plus one pad config value per pin. The macros support i.MX91 board and SoC DTS nodes configuring Ethernet, SD/MMC, serial, I2C/I3C, audio, camera/display media pins, GPIOs, watchdog, debug, and low-power/control functions. The numeric offsets must match the i.MX91 IOMUXC register layout expected by the `fsl,imx91-iomuxc` compatible.

### Risks
This is effectively a hardware ABI. A wrong mux mode or register offset can silently route a signal to the wrong pad, while a wrong `input_val` can leave an input peripheral disconnected even though the mux mode appears correct. The i.MX91 and i.MX93 files are similar but not identical: i.MX91 uses different select-input offsets for several peripherals and names security UART as `ELE_UART`, so copying i.MX93 pin names or values across would be risky. GPIO numbering is also encoded in names and must match the SoC GPIO controllers used by board DTS files.

### Test Signals
Useful checks are `make dtbs`/`dtbs_check` for i.MX91 DTS coverage, preprocessing spot checks that `fsl,pins` entries expand to six cells, and boot tests that exercise every configured peripheral on a target board. Hardware smoke tests should include UART console, I2C/I3C buses, SD/eMMC detection and high-speed modes, Ethernet link and RX/TX traffic, GPIO interrupts, audio/PDM/SAI where used, and alternate input routes with nonzero select-input values.
