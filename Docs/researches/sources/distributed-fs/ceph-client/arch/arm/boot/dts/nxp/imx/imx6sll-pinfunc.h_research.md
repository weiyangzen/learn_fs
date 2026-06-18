# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6sll-pinfunc.h

## Purpose

`imx6sll-pinfunc.h` is the i.MX6SLL Device Tree pin-function binding include. It is not executable C; it is a preprocessor table consumed by DTS/DTSI files before Device Tree compilation. Each `MX6SLL_PAD_<pad>__<function>` macro expands to the five-cell tuple documented at the top of the file:

`<mux_reg conf_reg input_reg mux_mode input_val>`

Board-level pinctrl groups append the sixth pad-control cell after one of these macros in `fsl,pins`, so the macro describes where and how to mux a pad while the board DTS chooses electrical flags such as pull, drive strength, hysteresis, open drain, or SION-related bits. In this tree, `imx6sll.dtsi` includes this header, and board files such as `imx6sll-kobo-clarahd.dts` consume the macros in pinctrl groups for I2C, UART, USB OTG, USDHC, LEDs, GPIO keys, EPDC PMIC control, and other board signals.

The file exports 864 tuple macros across 148 physical pads and 516 distinct muxed function names. The pad families are organized roughly in SoC register order: watchdog/reference clock pins, keypad pads, EPDC data/control/power pins, LCD data/control pads, audio pads, UART/I2C/ECSPI pads, USDHC pads, and late GPIO-only or multifunction pads.

## Important APIs, Types, and Macros

There are no C functions, structs, enums, or runtime APIs. The interface is entirely preprocessor macros protected by `__DTS_IMX6SLL_PINFUNC_H`.

The central API shape is:

`#define MX6SLL_PAD_<physical-pad>__<mux-function> mux_reg conf_reg input_reg mux_mode input_val`

Important macro groups include:

- `MX6SLL_PAD_EPDC_*`: EPDC data, timing, power, VCOM, border, and PMIC-facing pins. These dominate the file and reflect the display-controller focus of i.MX6SLL designs.
- `MX6SLL_PAD_LCD_*`: LCDIF data/control pins, with alternatives for ECSPI, CSI, UART5, AUD4, ARM trace, GPIO, and `SRC_BOOT_CFG*` boot configuration sampling.
- `MX6SLL_PAD_KEY_*`: keypad matrix pins with I2C2, ECSPI4, LCD, CSI, SD, UART4, USB, and GPIO alternatives.
- `MX6SLL_PAD_SD1_*`, `MX6SLL_PAD_SD2_*`, `MX6SLL_PAD_SD3_*`: USDHC pad sets and alternate card-detect/write-protect/vselect/reset, keypad, EPDC, UART, CSI, audio, SPDIF, USB, and GPIO uses.
- `MX6SLL_PAD_AUD_*`, `MX6SLL_PAD_ECSPI*`, `MX6SLL_PAD_I2C*`, `MX6SLL_PAD_UART1_*`: audio, SPI, I2C, and serial alternatives.
- GPIO alternatives such as `GPIO1_IOxx` through `GPIO5_IOxx`, usually with `input_reg` set to `0x0000` because no select-input daisy register is needed for plain GPIO output/input muxing.

The third tuple cell, `input_reg`, is nonzero when the selected peripheral input has a daisy-chain select register. The fifth tuple cell, `input_val`, is the value written to that select-input register. For output-only muxes and many GPIO cases, both are often `0x0000`.

## Control Flow

This header has no runtime control flow. Its effective flow is build-time and boot-time:

1. `imx6sll.dtsi` includes this header.
2. Board DTS files include or inherit the SoC DTSI and reference macros in pinctrl nodes under `fsl,pins`.
3. The C preprocessor expands each macro into five integer cells; the DTS source supplies a sixth pad-control value.
4. `dtc` emits the flattened Device Tree.
5. At boot, the Freescale/NXP i.MX pinctrl driver parses `fsl,pins` and writes the mux register, pad config register, and optional input select register for each entry.

Changing a macro changes every DTS board that uses that exact symbol, but only after recompilation of the affected Device Trees.

## State and Persistence

The file stores no runtime state and performs no persistence. Its constants become persistent only as part of built Device Tree blobs. At runtime, the pinctrl driver writes IOMUXC registers based on those DTB constants. Those register writes are volatile hardware state; they are re-applied during boot, probe, or pinctrl state transitions such as default and sleep states.

Because the macros encode register offsets and mux values, they are part of the ABI-like source contract between DTS authors and the kernel pinctrl binding. Renaming or changing macro values can break out-of-tree DTS users even though no binary ABI exists.

## Dependencies

Direct dependencies are minimal:

- The DTS C preprocessor must see this header through `imx6sll.dtsi`.
- The tuple layout must match the i.MX pinctrl binding and the Linux `pinctrl-imx` parser.
- Register offsets and mux/input values must match the i.MX6SLL reference manual and the SoC's IOMUXC hardware.
- Board DTS files must provide compatible pad-control values after each macro.

This file has no dependency on the distributed filesystem or Ceph-specific code despite living under the copied kernel source tree.

## Integration Points

The immediate integration point is `sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6sll.dtsi`, which includes the header. Board DTS files integrate it through pinctrl groups. In the observed tree, `imx6sll-kobo-clarahd.dts` uses these macros for default and sleep pin states, including I2C buses, touchscreen GPIO, EPDC PMIC control, UARTs, USB OTG, LEDs, GPIO keys, and USDHC.

At runtime the integration crosses into the i.MX pinctrl driver: the driver does not know macro names, only the expanded numeric cells. The macro names are therefore a source-level affordance for board authors and reviewers, while the numeric tuples are the machine-consumed contract.

## Risks and Edge Cases

- A wrong `mux_reg` or `conf_reg` offset can program the wrong pad and cause unrelated board signals to fail.
- A wrong `input_reg` or `input_val` can select the wrong daisy-chain input, producing hard-to-debug receive failures while the mux mode appears correct.
- Many pads expose boot configuration, watchdog reset, USB ID/overcurrent, card-detect/write-protect, and PMIC-ready functions. Accidental reuse as GPIO or another peripheral can affect boot mode, reset behavior, storage detection, or power sequencing.
- EPDC-heavy pads are highly shared with LCD, CSI, UART, SPI, I2C, SD, and GPIO alternatives. Board DTS reviews need to catch duplicate assignment of the same pad in multiple active pinctrl states.
- Sleep-state pinctrl groups must use compatible muxes and pad-control values; an apparently valid default-state mux can still leak power or break wakeup behavior when reused for suspend.
- Macro names encode DCE/DTE UART direction explicitly for many pins. Selecting the opposite naming variant can silently swap TX/RX or RTS/CTS semantics even when the numeric mux mode is valid.

## Test Signals

Useful validation signals are mostly build-time and board-boot oriented:

- `make dtbs` or the repository's equivalent DTB build should compile all i.MX6SLL Device Trees without undefined macro errors.
- `dtc` warnings should not report malformed `fsl,pins` cell counts; each macro use must expand to five cells plus one board pad-control cell.
- Boot logs should show the i.MX pinctrl driver applying groups without errors.
- Peripheral smoke tests should cover I2C, UART, USDHC card detect/write protect, USB OTG ID/OC, EPDC power sequencing, and any GPIO wake keys on affected boards.
- For changes to tuple values, hardware-level checks with pinmux register dumps or `/sys/kernel/debug/pinctrl` are stronger than compile-only validation.
