# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6sx-pinfunc.h

## Purpose

`imx6sx-pinfunc.h` is the i.MX6SX Device Tree pin-function binding include. It provides the macro table that board DTS files use when declaring i.MX6SX pinctrl groups. Each normal macro expands to:

`<mux_reg conf_reg input_reg mux_mode input_val>`

The board DTS then appends one pad-control cell, making a full `fsl,pins` entry for the i.MX pinctrl binding. In this tree, `imx6sx.dtsi` includes the header, and board files such as `imx6sx-nitrogen6sx.dts` use it for audio, SPI, Ethernet, CAN, I2C, PCIe, PWM, UART, USB, and USDHC pin groups.

The file is larger and broader than the i.MX6SLL header: it exports 1552 tuple macros plus 86 legacy alias macros, covering 166 physical pads and 1248 distinct function names. It spans GPIO1 pads, CSI, dual ENET/RGMII, keypad, LCDIF1/LCDIF2, NAND, QSPI, USDHC1-4, USB host pins, audio interfaces, CAN/CANFD, PCIe/debug/test muxing, VADC signals, M4/KITTEN trace/event signals, and SDMA/MMDC/GPU debug outputs.

## Important APIs, Types, and Macros

There are no functions, structs, or executable APIs. The exported source-level API is the set of `MX6SX_PAD_<pad>__<function>` macros protected by `__DTS_IMX6SX_PINFUNC_H`.

Important macro groups include:

- `MX6SX_PAD_GPIO1_IOxx__*`: early GPIO bank pads with I2C, USDHC, SPDIF, clocks, watchdog, SNVS, PHY/JTAG, USB, SDMA, UART, CCM, MLB, and security/debug alternatives.
- `MX6SX_PAD_CSI_*__*`: CSI1 camera pads with ESAI, AUDMUX, I2C, keypad, UART6/UART4, WEIM, SAI1, VADC, and MMDC debug alternatives.
- `MX6SX_PAD_ENET*` and `MX6SX_PAD_RGMII*`: Ethernet management, RMII/RGMII data/control/clock, GPIO, CSI2, LCDIF2, PCIe debug, and test alternatives for ENET1 and ENET2.
- `MX6SX_PAD_LCD1_*__*`: LCDIF1 data/control pads with WEIM, M4/KITTEN trace, CSI1, GPIO, boot config, SIM, VADC, VDEC, and MMDC debug alternatives.
- `MX6SX_PAD_NAND_*__*`: raw NAND pads multiplexed with QSPI2, ECSPI, ESAI, GPIO4, WEIM, TPSMP, USB PHY test, and SDMA debug signals.
- `MX6SX_PAD_QSPI1A_*` and `MX6SX_PAD_QSPI1B_*`: QSPI pins with USB, ECSPI, ESAI, CSI, GPIO, WEIM, CAN/CANFD, SIM, and SDMA debug alternatives.
- `MX6SX_PAD_SD1_*` through `MX6SX_PAD_SD4_*`: USDHC pads with audio, watchdog, GPT, UART, ENET 1588, CCM, VADC, keypad, ECSPI, MLB, LCDIF2, CAN/CANFD, and debug alternatives.
- The final alias block maps older UART-oriented names such as `MX6SX_PAD_GPIO1_IO04__UART1_RX` to explicit DCE/DTE names such as `MX6SX_PAD_GPIO1_IO04__UART1_DTE_RX`. The file itself marks these as not intended for long-term use.

The most important inline documentation is the ENET1 reference clock comment near `MX6SX_PAD_ENET1_TX_CLK__ENET1_REF_CLK1`. It explains that SION is necessary when the pad is used as an `IMX6SX_CLK_ENET_REF` clock output to feed an RMII PHY under a specific GPR1 configuration, while warning that forcing input can affect other consumers of the same pad.

## Control Flow

The file has no runtime branches. Its lifecycle is:

1. `imx6sx.dtsi` includes the header.
2. Board DTS files refer to the macros inside pinctrl nodes.
3. Preprocessing expands each tuple into numeric cells.
4. `dtc` compiles the expanded cells into DTBs.
5. During boot or pinctrl state changes, the i.MX pinctrl driver writes IOMUXC mux/config registers and optional select-input registers from `fsl,pins`.

The legacy aliases add a build-time indirection layer only: each alias expands to one of the newer DCE/DTE-specific macros, which then expands to a tuple.

## State and Persistence

The header has no mutable state. Its constants persist only in compiled DTBs and are applied to volatile IOMUXC hardware registers by the kernel. Pinctrl states may be re-applied for default, idle, and sleep modes depending on each board DTS, but the header does not manage those transitions itself.

Because the macro names are used in DTS sources and possibly out-of-tree board files, the header behaves like a source compatibility surface. Removing legacy aliases or changing tuple constants can break DTS builds or silently alter hardware muxing.

## Dependencies

Key dependencies are:

- The tuple format expected by the i.MX pinctrl Device Tree binding.
- Inclusion through `imx6sx.dtsi`.
- Linux's i.MX pinctrl driver, which interprets the expanded numeric cells.
- Correct i.MX6SX IOMUXC register offsets, mux modes, select-input offsets, and daisy-chain values from SoC documentation.
- Board DTS pad-control values appended after each macro.
- For the ENET reference-clock case, matching IOMUXC GPR1 clock direction and mux settings, as described in the source comment.

The header is independent of filesystem or Ceph logic; it is part of the vendored or mirrored kernel source layout.

## Integration Points

The primary source integration is `sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6sx.dtsi`. Board integration is visible in `imx6sx-nitrogen6sx.dts`, which uses these macros in `pinctrl_audmux`, `pinctrl_ecspi1`, `pinctrl_enet1`, `pinctrl_enet2`, `pinctrl_flexcan1`, `pinctrl_flexcan2`, I2C groups, PCIe reset/control GPIOs, PWM, UART, USB OTG, and multiple USDHC speed-state groups.

At runtime the integration is with the SoC IOMUXC block and pinctrl-imx driver. The driver only receives expanded integers, so source-level review must catch mismatches between symbolic intent and tuple values before they become compiled hardware programming data.

## Risks and Edge Cases

- The ENET1 reference-clock SION workaround is explicitly risky: it may be required for RMII PHY clock output, but forcing input on a shared pad can affect other functions such as UART DTR handling.
- The 86 legacy UART aliases can hide DCE/DTE direction. New DTS code should prefer the explicit DCE/DTE macros to avoid TX/RX or RTS/CTS confusion.
- The same physical pad often exposes production signals and debug/test functions. Accidentally selecting VDEC, MMDC, SDMA, PCIe, USB PHY test, or SIM/TPSMP functions can make a board fail in ways that compile cleanly.
- Ethernet and USDHC pads include clock, reset, card detect, write protect, voltage select, and 1588 event signals. Tuple mistakes may not show up until high-speed modes, suspend/resume, or external PHY/card interactions.
- LCDIF and boot-configuration pads overlap. Reassigning boot config pads without understanding board straps can complicate boot-mode diagnosis.
- Select-input values are especially fragile for peripherals with many possible input pads, including UART, I2C, CAN/CANFD, SPDIF, ESAI, ECSPI, and ENET.
- Since board DTS files append pad-control values, validating this header alone is insufficient; a correct mux tuple can still be paired with unsafe electrical configuration.

## Test Signals

Relevant checks include:

- Build all affected i.MX6SX DTBs and verify there are no undefined macro or `fsl,pins` cell-count failures.
- Compile with warnings visible from `dtc`; malformed tuple expansion or stale alias removal should surface during DTS preprocessing or DT compilation.
- Boot representative boards and inspect pinctrl debugfs output for applied groups and expected mux/config values.
- Exercise high-risk peripherals: ENET1/ENET2 link and RMII/RGMII clocking, CAN/CANFD RX/TX, USDHC speed modes and card-detect/write-protect, USB OTG ID/OC/PWR, UART DCE/DTE wiring, and I2C bus probing.
- For changes touching input daisy chains, verify receive paths with real hardware signals, not only successful DTB compilation.
- For alias cleanup, build out-of-tree or downstream DTS users if available, because the in-tree board set may not cover all legacy names.
