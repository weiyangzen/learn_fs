# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/mt8173-pinfunc.h

## Purpose

`mt8173-pinfunc.h` is the MT8173 pin function binding header. It defines 528 macros over GPIO0 through GPIO134. The file gives devicetree sources readable names for MT8173 pad mux selectors and preserves the SoC-specific function matrix in a kernel-tree binding file.

The header covers EINT pads, IRDA, I2S, SPDIF, UART, display PWM and DSI TE, serial flash, AP/MD32/MFG/DFD JTAG, HDMI/HDCP/CEC/hotplug pins, MSDC0/1/2/3 storage groups, PCM/MRG/audio pins, PMIC wrapper SPI pins, RTC/watchdog/SRCLKENA pins, keypad rows/columns, I2C buses, USB VBUS/IDDIG sideband, camera/NAND-like CMDAT/CM* pins, and debug monitor functions. Several macro names preserve legacy punctuation-like suffixes from generated bindings, such as `_0_`, `_1_`, and `MSDC0_RST__`.

## Important APIs And Types

The API is the `MT8173_PIN_<n>_<pad>__FUNC_<function>` macro namespace. Macros use `MTK_PIN_NO(n) | selector`, with `MTK_PIN_NO()` supplied by `<dt-bindings/pinctrl/mt65xx.h>`. There are no C data structures or routines. DTS consumers embed the resulting integers in pinctrl nodes.

Important regions include GPIO0-15 for EINT/IRDA/I2S/UART/display/serial flash and camera flash pads, GPIO16-21 for IDDIG/watchdog/CEC/HDMI pins, GPIO22-28 for MSDC3, GPIO29-36 for UART2/MRG/PCM, GPIO37-46 for EINT/connectivity/camera/debug and I2C, GPIO47-56 for camera/NAND-style receive pins, GPIO57-68 for MSDC0, GPIO69-72 for SPI0/PWM/I2S/display, GPIO73-82 for MSDC1 and PMIC wrapper SPI, GPIO83-91 for audio/RTC/display/SRCLKENA, GPIO92-99 for PCM and UART1, GPIO100-107 for MSDC2 plus USB/I2C/UART/PWM/SPI, GPIO108-112 for JTAG, GPIO113-118 for UART0/3, GPIO119-124 for keypad/IRDA/PWM/USB, GPIO125-127 for I2C/display reset, GPIO128-132 for I2S0 and SPI2 overlays, and GPIO133-134 for I2C4.

## Control Flow, State, And Persistence

The header has no executable control flow. It participates in a compile-time-to-boot-time path: DTS source includes the header, selected constants are compiled into the DTB, and the MediaTek pinctrl driver decodes and applies them. It stores no state. Board pinmux choices persist only as DTS/DTB configuration.

## Dependencies And Integration Points

The direct dependency is `<dt-bindings/pinctrl/mt65xx.h>`. Integration points are MT8173 DTS files and the kernel drivers for display, HDMI/CEC, audio, MMC/SD, SPI, I2C, UART, PMIC wrapper, USB, IRDA, and debug/JTAG facilities. The header must remain consistent with the MT8173 pinctrl driver's supported pin range and selector encoding.

## Risks And Test Signals

Primary risks are binding ABI breakage and hardware misrouting. Because several macro names include legacy spelling quirks, cleanup-style renames are dangerous unless all DTS users are changed in lockstep. Incorrect mux values can prevent boot from eMMC, break HDMI/CEC, disable UART console, misconfigure PMIC communication, or route debug pins over production interfaces.

Test signals include DTB build success for MT8173 boards, `dtbs_check` pinctrl coverage, pinctrl driver logs without invalid pin/function messages, and hardware validation of storage, UART console, HDMI hotplug/CEC, display reset/TE/PWM, I2C/SPI buses, PMIC wrapper access, USB VBUS/id behavior, audio paths, and any board-specific JTAG/debug pin use.
