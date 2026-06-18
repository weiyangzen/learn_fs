# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx7d-pinfunc.h

## Purpose
This header is the Devicetree pin-function catalog for the NXP/Freescale i.MX7D and i.MX7S IOMUX controllers. It defines `MX7D_PAD_*__*` macros that expand to the five-cell i.MX `PIN_FUNC_ID` tuple used by board DTS `fsl,pins` properties. It is included by `imx7s.dtsi`.

The file contains 1,139 pin-function macros over 158 physical pad names. It covers LPSR pads and the main IOMUXC pad set spanning GPIO1, EPDC, LCD, SD/MMC, SAI, ECSPI, UART, ENET/RGMII, QSPI, EIM, CSI, KPP, CCM, USB, watchdog, SDMA, and security/debug observation routes.

## Important APIs, Types, and Functions
The public API is `MX7D_PAD_<pad>__<signal> <mux_reg conf_reg input_reg mux_mode input_val>`. Board DTS entries append one pad setting cell, producing six-cell `fsl,pins` entries. `Documentation/devicetree/bindings/pinctrl/fsl,imx7d-pinctrl.yaml` documents this order and supports both `fsl,imx7d-iomuxc` and `fsl,imx7d-iomuxc-lpsr`.

Main-controller macros and LPSR-controller macros live in the same header but are consumed by different compatible nodes. LPSR entries begin at zero offsets and require `ZERO_OFFSET_VALID`; some LPSR input-select writes use `fsl,input-sel` because daisy-chain registers are shared with the main controller. The file uses mux modes 0 through 8 and has 425 macros with nonzero input select registers.

## Control Flow
`imx7s.dtsi` includes the header and declares main and LPSR IOMUXC nodes. Board DTS files compile macro plus config values into six-cell `fsl,pins` entries. `drivers/pinctrl/freescale/pinctrl-imx7d.c` matches `fsl,imx7d-iomuxc` or `fsl,imx7d-iomuxc-lpsr`; `pinctrl-imx.c` validates `FSL_PIN_SIZE`, parses tuples, maps offsets to pin ids, handles SION, and stores input-select metadata. State selection writes mux and pad registers, and writes input-select values relative to either the current base or `input_sel_base` for LPSR cases.

## State and Persistence Behavior
The header stores no mutable state. It persists hardware routing through DTS source and compiled DTBs. Runtime state is created when Linux writes main IOMUXC, LPSR IOMUXC, input-select, and pad configuration registers.

## Dependencies and Integration Points
It is included by `imx7s.dtsi`, used by i.MX7D/i.MX7S board files, parsed by `pinctrl-imx.c`, matched by `pinctrl-imx7d.c`, and described by `fsl,imx7d-pinctrl.yaml`. Peripheral integration spans EPDC/LCD display, SD/QSPI storage, ENET/RGMII networking, UART/I2C/ECSPI/SAI serial and audio, keypad, CAN, USB, watchdog, clock, SDMA, and security/debug routes.

## Risks
Wrong register offsets, select-input values, or cross-controller placement can silently misroute hardware. Main macros under an LPSR node or LPSR macros under the main node can produce valid-looking data that writes the wrong register space. Daisy-chain errors can break UART RX, CTS/RTS, I2C, card-detect/write-protect, MDIO, CAN RX, and clock inputs. LPSR nodes also require `fsl,input-sel`. Board pad config cells can still create electrical failures.

## Test Signals
Build i.MX7 DTBs and run `dtbs_check` for `Documentation/devicetree/bindings/pinctrl/fsl,imx7d-pinctrl.yaml`, including main and LPSR paths. Runtime validation should cover UART/I2C/SPI/CAN receive paths, SD card-detect/write-protect, Ethernet MDIO/RGMII, display pins, and LPSR GPIO behavior. For edits, compare DTB tuple output and inspect pinctrl debugfs.
