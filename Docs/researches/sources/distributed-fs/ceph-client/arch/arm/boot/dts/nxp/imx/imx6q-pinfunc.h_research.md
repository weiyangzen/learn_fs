# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6q-pinfunc.h

## Purpose
`imx6q-pinfunc.h` is the device-tree pin-function binding table for the NXP/Freescale i.MX6 Quad/Dual IOMUX controller. It maps human-readable pad/function names to the five register-selector cells consumed by the Linux i.MX pinctrl binding.

The file allows board DTS sources to express pinmux choices as symbols such as `MX6QDL_PAD_EIM_D21__I2C1_SCL` rather than raw IOMUXC offsets. Board files then append the pad-control word to complete each `fsl,pins` entry.

## Important APIs, Types, And Functions
There are no runtime functions or types. The public API is 1,030 `#define` macros for 197 physical pads, using the tuple format `<mux_reg conf_reg input_reg mux_mode input_val>`.

The macro namespace is `MX6QDL_PAD_<PAD_NAME>__<FUNCTION_NAME>`. Although the prefix is shared with i.MX6DL/Solo, this header represents the i.MX6Q/D register layout. Function families include SD1 through SD4, RGMII/ENET, EIM, dual IPU display and CSI routing, CSI0, NAND, GPIO banks 1 through 7, ECSPI1 through ECSPI5, I2C1 through I2C3, UART1 through UART5, ESAI/AUD, KEY matrix, HDMI DDC/CEC, SPDIF, FLEXCAN, SDMA, USB, boot strap `SRC_BOOT_CFG*`, watchdog, PWM/GPT/EPIT, MLB, HSI, and ARM trace/JTAG.

The Quad/Dual file differs from the DualLite file in meaningful ways. It includes IPU2 alternatives, ECSPI5 alternatives on SD pads, and Quad-specific select-input offsets, while i.MX6DL includes some EPDC-oriented alternatives absent here. For shared macro names, the symbolic name may match but the numeric tuple can differ.

## Control Flow
The file has no executable control flow. It is protected by `__DTS_IMX6Q_PINFUNC_H`, defines the tuple-format comment, lists the pad-function macros, and ends with the include guard close.

During DTS preprocessing, every macro expands inline into five cells. The device-tree compiler treats the expansion as integer data. Later, when a pinctrl state is selected by the kernel, the i.MX pinctrl driver writes the mux register at `mux_reg`, the pad-control register at `conf_reg`, and, when nonzero, the select-input register at `input_reg` with `input_val`.

## State, Persistence, And Dependencies
This header contains static hardware-description constants only. It has no mutable state, allocation, persistence, or side effects.

Its correctness depends on the i.MX6Q/D IOMUXC register map and on the Linux `fsl,imx-pinctrl` binding. The numbers are not self-validating: `mux_mode` must correspond to the named alternate function for that pad, and `input_val` must select the same physical pad in daisy-chain registers used by UART, I2C, ECSPI, ENET, IPU, USB, and similar peripherals.

## Integration Points
`imx6q.dtsi` includes this header, making the macros available to i.MX6Q/D board files and common `imx6qdl-*.dtsi` fragments. In-tree consumers use it in pinctrl groups for Ethernet, HDMI, I2C, SPI, UART, SD/eMMC, USB power/over-current, GPIO keys, displays, audio, CAN, and board-specific control signals.

The primary integration boundary is with the sibling i.MX6DL header: common board fragments rely on shared `MX6QDL_PAD_*` names, while the SoC root dtsi chooses either the Quad/Dual or DualLite/Solo numeric mapping. The kernel pinctrl driver and device-tree binding form the runtime consumer.

## Risks
The highest risk is silent hardware misconfiguration. A wrong register offset, mux mode, or select-input value can leave a peripheral unresponsive even when the DTB builds cleanly. This is especially likely around functions with many daisy-chain alternatives such as UART RX/RTS, I2C SCL/SDA, ECSPI chip selects, ENET clocks/data, IPU CSI inputs, USB ID/OC, and HDMI DDC/CEC.

The shared macro namespace can hide SoC-family differences. A board fragment that is valid for i.MX6Q may not have equivalent electrical routing or select-input values on i.MX6DL, despite using the same macro spelling. Conversely, adding new names here without considering common `imx6qdl` include files can break portability.

Special-case entries such as USB ID values and `GPIO_6__ENET_IRQ` carry non-obvious select-input or mux information. Boot-strap and reset-related pads also need care because changing them can affect early boot behavior or external reset lines.

## Test Signals
Build affected i.MX6Q/D DTBs with `make dtbs` and run `dtbs_check` to catch binding-shape regressions. Static checks should confirm exactly five cells per macro, no duplicate names, legal numeric tokens, and tuple values aligned with the i.MX6Q/D reference manual.

Runtime validation should focus on peripherals touched by changed macros: RGMII/ENET link and interrupts, I2C bus detection, SPI loopback or device probes, UART TX/RX and flow control, SD/eMMC card modes, HDMI DDC/CEC, USB host/OTG ID and over-current handling, display/camera paths, GPIO interrupts, and wake/reset pins.
