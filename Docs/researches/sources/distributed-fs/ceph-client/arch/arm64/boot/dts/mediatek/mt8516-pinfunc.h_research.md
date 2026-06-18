# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/mt8516-pinfunc.h

## Purpose
This MediaTek MT8516 pin-function binding header provides numeric constants for SoC pin multiplexing in device-tree sources. It defines 534 `MT8516_PIN_*__FUNC_*` macros for pins 0 through 120 and is intended to be included by MT8516 board DTS files.

## APIs, Types, And Constants
The macro API encodes a physical pin identity and mux selector with `MTK_PIN_NO(pin) | function`. Macro names retain the ball/pad role, such as `EINT`, `MSDC`, `CMPCLK`, and `MSDC0_DAT*`, and expose alternate functions such as PWM, SPI, I2C, I2S/TDM, Ethernet external MAC signals, connectivity MCU debug, antenna selection, NAND-like `NLD` signals, watchdog, and debug monitors.

## Control Flow And State
There is no runtime control flow or mutable state. DTS preprocessing substitutes these constants into pinctrl properties, and the resulting DTB persists the chosen mux values for boot-time driver consumption.

## Dependencies And Integration
The header includes `dt-bindings/pinctrl/mt65xx.h` for `MTK_PIN_NO`. It integrates with MT8516 DTS/DTSI files and the MediaTek pinctrl driver. The naming scheme differs from newer `PINMUX_GPIO` headers by including both pin number and pad signal name, which helps board authors select the correct physical pad.

## Risks And Test Signals
Risks are off-by-one pin numbers, incorrect mux mode values, and copy/paste naming errors. Those issues may pass build checks but break board peripherals. Useful tests are `make dtbs`, `dt_binding_check` for affected DTS files, boot-time pinctrl logs, and physical validation of GPIO, MMC, SPI, I2C, audio, and Ethernet pins.
