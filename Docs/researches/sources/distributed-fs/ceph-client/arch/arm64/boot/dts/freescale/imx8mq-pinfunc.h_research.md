<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mq-pinfunc.h -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mq-pinfunc.h

## Purpose
Defines symbolic pin-function constants for the i.MX8M Quad (`MX8MQ`) device-tree pinctrl binding. Board and SoC DTS files use these constants to configure physical pads for GPIO, storage, networking, audio, serial, boot, debug, and control functions without hard-coding IOMUXC register offsets or mux selector values.

Unlike the i.MX8MP header in the same directory, this file is a pure pin tuple catalog. It does not define electrical pad-control helper bit macros. The DTS author supplies pad-control config values separately after each expanded pin tuple.

## Important APIs, Types, And Functions
- Include guard: `__DTS_IMX8MQ_PINFUNC_H`.
- Pin macro namespace: `MX8MQ_IOMUXC_<PAD>_<FUNCTION>`. This older naming style uses a single underscore between pad and function rather than the double-underscore separator used in newer i.MX8MP/ULP headers.
- Pin tuple layout: `<mux_reg conf_reg input_reg mux_mode input_val>`.
- Source coverage: 607 `MX8MQ_IOMUXC_` macros.

The table begins with always-on/control-style pads such as `PMIC_STBY_REQ`, `PMIC_ON_REQ`, `ONOFF`, `POR_B`, and `RTC_RESET_B`, then covers GPIO1_IO00-15, ENET RGMII/MDIO/MDC, USDHC1/2, NAND/QSPI, SAI1/2/3/5/6, SPDIF, ECSPI1/2, I2C1-4, UART1-4, PCIe clock request, coresight trace, boot configuration, test/observe outputs, SIM/TPSMP debug-style signals, JTAG pins, boot mode pins, and RTC.

The final entries such as `MX8MQ_IOMUXC_TEST_MODE`, `BOOT_MODE0`, `BOOT_MODE1`, JTAG pins, and `RTC` have `mux_reg` set to `0x000` and only provide config-register positions. They still use the same five-cell shape so they can fit the binding's expected cell layout.

## Control Flow
The file has no executable control flow. Its data path is:

1. DTS sources include this header.
2. `fsl,pins` arrays reference `MX8MQ_IOMUXC_*` symbols and append board-specific pad-control values.
3. Preprocessing expands each symbol into the five cells required by the i.MX pinctrl binding.
4. The DTB embeds those cells.
5. The kernel's i.MX pinctrl driver programs mux/config/input-select registers when the relevant pinctrl state is selected by a peripheral driver.

Macro order follows the hardware register/pad order, which makes diff review against reference material practical. Multiple macros can share one `input_reg` with different `input_val` selectors when the same peripheral input can be daisy-chained through multiple pads.

## State And Persistence
The header itself is immutable source data and stores no runtime state. Once compiled into a board DTB, its expanded values persist as part of the board hardware description. Runtime pinctrl state transitions, such as default/sleep states selected by drivers, are driven by DTS users of these macros rather than by this header.

## Dependencies And Integration Points
- Depends on the i.MX8MQ IOMUXC register map and input daisy-chain selector definitions.
- Integrated with ARM64 Freescale/NXP DTS and DTSI files for i.MX8MQ boards.
- Consumed by the Linux device-tree C preprocessor and `dtc`.
- Interpreted by the i.MX pinctrl driver through the standard `fsl,pins` cell contract.
- Affects peripheral integration for PMIC/power controls, USB OTG ID/PWR/OC, USDHC, ENET/RGMII, RAWNAND/QSPI, SAI/SPDIF, ECSPI, I2C, UART, PWM, SDMA events, PCIe clock request, GPIO, JTAG/debug, and boot-mode handling.

## Risks And Edge Cases
- The macro separator convention differs from i.MX8MP and i.MX8ULP. Mechanical searches or generated conversions that assume `PAD__FUNCTION` names can miss or corrupt this file.
- The tuple shape matches i.MX8MP but not i.MX8ULP. Reusing ULP four-cell macros in i.MX8MQ pinctrl states would shift the pad-control cell into the wrong position.
- Some control and JTAG/boot macros use `mux_reg` `0x000`; tooling that treats zero mux offset as invalid would report false positives.
- Many alternate functions are test, observe, SIM/TPSMP, boot-config, or coresight signals that should not be enabled accidentally on production boards.
- `input_reg`/`input_val` errors are hard to catch without hardware because transmit-only signals can still work while receive/input selection is wrong.
- This header does not provide pad-control presets. Board files must choose pull, drive, hysteresis, open-drain, and speed settings explicitly and appropriately.

## Test Signals
- Device-tree compilation catches missing macro names and gross syntax errors.
- Binding validation can verify pinctrl property shape, while tuple correctness needs register-map review or hardware tests.
- Boot and probe logs should show successful pinctrl state application and peripheral initialization.
- Hardware tests should cover Ethernet MDIO/link, USDHC card/eMMC operation, USB OTG role/power/overcurrent signals, UART console/flow control, I2C/SPI transactions, audio clocks/data lines, NAND/QSPI access, GPIO direction/value, and PMIC/power button behavior.
- For edits, compare macro offsets and daisy values against upstream Linux/NXP data and inspect affected board DTS files for tuple-shape assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mq-pinfunc.h -->
