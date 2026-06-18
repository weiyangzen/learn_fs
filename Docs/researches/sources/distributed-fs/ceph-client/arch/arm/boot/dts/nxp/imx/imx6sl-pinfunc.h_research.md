# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6sl-pinfunc.h

## Purpose
`imx6sl-pinfunc.h` is the device-tree pin-function binding table for the NXP/Freescale i.MX6 SoloLite IOMUX controller. It defines symbolic pinmux constants for the SoC's pad set, including its display, e-paper, SD, FEC, audio, serial, USB, keypad, and GPIO routing options.

Like the other i.MX pin-function headers, each macro expands to `<mux_reg conf_reg input_reg mux_mode input_val>`. Board DTS files use these macros in `fsl,pins` arrays and append the pad-control word that configures electrical behavior.

## Important APIs, Types, And Functions
There are no C functions or data types. The interface is 1,059 `#define` macros covering 150 physical pads, all using the `MX6SL_PAD_<PAD_NAME>__<FUNCTION_NAME>` naming convention.

The covered pad families reflect the SoloLite feature mix: AUD, ECSPI1 through ECSPI4, EPDC/SPDC e-paper signals, FEC Ethernet, HSIC USB, I2C1 through I2C3, keypad rows/columns, LCD data and control, PWM, reference clocks, SD1 through SD3 plus SD4 alternatives, UART1 through UART5, watchdog, GPIO banks 1 through 5, CSI, EIM, GPT/EPIT, SPDIF, USB ID/power/over-current, boot strap `SRC_BOOT_CFG*`, and ARM trace/JTAG.

The `input_reg/input_val` cells are heavily used for shared input signals. Examples include I2C, UART RX/RTS, ECSPI, FEC, CSI, keypad, LCD, SD card detect/write-protect, USB ID/OC, GPT capture, EPDC power status/IRQ, and CCM PMIC ready.

## Control Flow
There is no executable control flow. The header uses the `__DTS_IMX6SL_PINFUNC_H` include guard, defines the tuple-format comment, emits a flat macro table, and closes the guard.

At build time, DTS preprocessing expands the macros into integer cells. At runtime, the pinctrl state selected by the kernel causes the i.MX pinctrl driver to program IOMUXC registers according to those cells. Whether and when a group is applied depends on the consuming device node's pinctrl state, not on this header.

## State, Persistence, And Dependencies
The file is pure static hardware description. It creates no persistent state and has no side effects by itself.

It depends on the i.MX6SL IOMUXC register map and the Linux i.MX pinctrl binding. The macro values must stay synchronized with the SoC reference manual, especially because SoloLite has a different pad inventory and display/e-paper-oriented mux map from i.MX6QDL. Board-level correctness also depends on matching the symbolic pinmux to the external schematic and supplying an appropriate pad-control value.

## Integration Points
`imx6sl.dtsi` includes this header, and i.MX6SL board files consume the macros in their pinctrl groups. In this source tree, `imx6sl-tolino-shine3.dts` uses the header extensively for touch, power key, hall sensor, LCD/EPDC-related GPIOs, I2C buses, UARTs, USB OTG ID, SD card pin states, charger/PMIC interrupts, and e-paper power control signals.

The runtime integration point is the same i.MX pinctrl driver family used by other i.MX SoCs, but the macro namespace is distinct (`MX6SL_PAD_*`) and not interchangeable with `MX6QDL_PAD_*`.

## Risks
The key risk is silent board failure from incorrect tuple data. A valid-looking macro with an incorrect mux register, mode, or select-input value can cause one peripheral input to listen to the wrong pad. This is particularly risky for SoloLite because many pads offer dense alternatives among EPDC, LCD, CSI, SD, FEC, UART, I2C, ECSPI, and GPIO functions.

Display and e-paper pads are high-impact: mistakes can disable panels, power sequencing, VCOM, or EPDC status/IRQ lines. USB ID/OC/power macros, watchdog/reset alternatives, boot strap signals, and PMIC-ready routes can affect boot, reset, power, or wake behavior.

Another risk is using a `MX6SL_PAD_*` macro spelling in common DTS content meant for other i.MX6 families, or copying numeric tuples from Q/DL headers. The pad inventory, offsets, and daisy-chain values are SoC-specific.

## Test Signals
Build all i.MX6SL DTBs with `make dtbs` and run `dtbs_check`. Static validation should check exactly five cells per macro, no duplicate definitions, valid hexadecimal numeric tokens, and reference-manual alignment for mux modes and select-input registers.

Hardware validation should cover panel or EPDC operation, e-paper power sequencing and IRQ/status signals, SD card detection and bus modes, FEC link and traffic, I2C scans, SPI devices, UART consoles, USB OTG ID/host behavior, GPIO interrupts, keypad signals where used, watchdog/reset routing, and suspend/resume wake lines.
