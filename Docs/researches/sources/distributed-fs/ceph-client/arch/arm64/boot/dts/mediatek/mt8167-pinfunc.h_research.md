# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/mt8167-pinfunc.h

## Purpose

`mt8167-pinfunc.h` is the MT8167 devicetree pin function binding. It defines 610 macros for GPIO0 through GPIO124. The naming style includes both the numeric pin and the primary pad signal, for example `MT8167_PIN_68_MSDC2_CMD__FUNC_MSDC2_CMD`, which helps board authors understand the default pad role while choosing alternate functions.

The file is a static mapping table encoded as C preprocessor macros. It does not implement pin control logic. It lets MT8167 DTS files express mux choices for EINT-capable GPIOs, display DPI/DSI/HDMI/CEC pins, I2S/TDM/PCM/audio paths, UARTs, SPI and serial flash pins, I2C buses, keypad rows/columns, PMIC wrapper SPI pins, RTC/watchdog/SRCLKENA pins, JTAG/DFD/UDI debug pins, MSDC0/1/2 storage, NAND/camera-style CMDAT/CM* pins, MIPI D-PHY-like pins, USB sideband, and antenna/debug monitor signals.

## Important APIs And Types

The exported API is the `MT8167_PIN_<n>_<pad>__FUNC_<function>` macro namespace. Every macro expands to `MTK_PIN_NO(n) | selector`, with `MTK_PIN_NO()` included from `<dt-bindings/pinctrl/mt65xx.h>`. Selector 0 generally selects GPIO or GPI mode, while selector 1 and above choose peripheral functions.

Important regions include GPIO0-25 for EINT pads with DPI, I2S, Ethernet-style EXT signals, SQI, antenna, PWM, and debug monitor alternates; GPIO26-33 for PMIC wrapper, RTC, watchdog, and SRCLKENA; GPIO34-39 for UART2 and MRG/I2S/PCM/DPI/EXT MDIO/MDC; GPIO40-47 for keypad and JTAG/debug; GPIO48-51 for SPI and I2S overlays; GPIO52-61 for I2C, display PWM, and I2S; GPIO62-67 for UART0/1 and display reset/TE; GPIO68-73 for MSDC2 plus I2S/DPI/I2C/USB/UART/PWM alternates; GPIO74-99 for transmit/receive differential-style pins with camera CMDAT/CM* alternates; GPIO100-103 for camera/NAND/TDM style pins; GPIO104-120 for MSDC1 and MSDC0 with SQI, NAND, watchdog, and debug alternates; and GPIO121-124 for CEC/HDMI hotplug/I2C-like HDMI pins.

## Control Flow, State, And Persistence

There is no local control flow. During build, DTS files include this binding header and receive integer constants. At boot, the pinctrl driver interprets those constants from the DTB and writes hardware mux registers as it applies pin states. The header itself has no mutable state and no persistence. Persistence comes from DTS source, DTB artifacts, and any bootloader/kernel pinctrl sequencing that uses the same binding ABI.

## Dependencies And Integration Points

The direct dependency is `<dt-bindings/pinctrl/mt65xx.h>`. Integration points include MT8167 board DTS files, the MediaTek pinctrl driver, display drivers, audio drivers, MMC/SD drivers, SPI/I2C/UART drivers, HDMI/CEC support, PMIC wrapper, USB, and debug tooling. The older `MT8167_PIN...` naming style is part of the DTS-facing ABI and should be kept stable.

## Risks And Test Signals

The file is sensitive to off-by-one pin numbers and selector mistakes. Risks include breaking boot storage on MSDC0, losing console or Bluetooth/modem UART pins, misrouting display/HDMI/CEC pins, or selecting debug/JTAG functions over production interfaces. The high-numbered GPI-style differential pins have unusual `GPI` macro names instead of `GPIO`; they should be preserved if they reflect the existing binding ABI.

Validation should include building MT8167 DTBs, running `dtbs_check`, and boot-testing boards that use the affected pin groups. Hardware signals include eMMC/SD card enumeration, UART console, I2C peripheral probing, SPI/SQI transfers, display and HDMI hotplug/CEC operation, audio I2S/TDM playback/capture, USB VBUS/id behavior, and absence of pinctrl invalid-function warnings.
