# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/mt6878-pinfunc.h

## Purpose

`mt6878-pinfunc.h` is the devicetree binding header for MT6878 pin multiplexing. It gives DTS authors symbolic names for every alternate function selectable on the SoC's GPIO pads. The file is a pure preprocessor interface: it has no executable code, structs, storage, or runtime initialization. Its value is that a board `.dts` or `.dtsi` can write `PINMUX_GPIO185__FUNC_MSDC0_CLK` instead of hard-coding a packed pin/function integer.

The header defines 992 `PINMUX_GPIO...__FUNC_...` constants over GPIO0 through GPIO195. Every macro follows the same ABI shape, `MTK_PIN_NO(pin) | function`, where `MTK_PIN_NO()` comes from the included `mt65xx.h`. Function selector values are mostly in the 0-7 range, with selector 0 consistently representing GPIO mode. The symbolic names cover touch-panel always-on pads, SRCLKENA/SRCLKENAI power request pins, SCP/SSPM/SPM/MCUPM/JTAG debug pins, SPI0-7 groups, I2C SCL/SDA buses, UART and modem UART lanes, I2S/TDM/audio pins, display reset/TE/PWM/camera clocks, RF antenna/BPI/MIPI controls, SIM, SPMI, UFS sideband, MSDC0/1 storage, connectivity top pins, and watchdog/RTC signals.

## Important APIs And Types

The exported API is the macro namespace itself. A consumer combines these constants with MediaTek pinctrl binding properties such as `pinmux = <...>;` inside a pin configuration node. There are no C types, functions, or callbacks in this file. The important dependency is `mt65xx.h`, which defines the packing convention that separates the pin number from the mux selector. The pinctrl driver later decodes the packed value and programs the SoC pinmux registers.

Notable groups include GPIO0-7 for touch/clock/modem/debug and SPI7, GPIO8-17 for multiple debug/JTAG owners, GPIO19-28 for PWM/SPI4/SPI6/I2C/USB/camera flash references, GPIO29-32 for I2S and UART/modem/connectivity serial paths, GPIO33-45 and GPIO99-122 for RF antenna/BPI/MIPI control, GPIO52-55 for keypad and display helpers, GPIO56-75 for SPI0-5 plus SCP SPI overlays, GPIO77-82 for MSDC1/SIM/JTAG/MIPI, GPIO125-148 for I2C buses and SCP I2C/DMIC overlaps, GPIO156-159 for SPMI, GPIO164-171 for audio MOSI/MISO/VOW, GPIO172-183 for connectivity top/BT/Wi-Fi control, and GPIO184-195 for MSDC0 plus UFS/USB/audio alternates.

## Control Flow, State, And Persistence

There is no runtime control flow in the header. The effective flow is build-time and boot-time: the C preprocessor expands a symbolic macro in a DTS include path, `dtc` emits the packed integer into the DTB, and the Linux MediaTek pinctrl driver applies the resulting mux values when probing the relevant pinctrl state. Persistence is the compiled devicetree blob and, practically, the board source tree. No data is mutated by this header and no state is stored across boots except through board DTS selections.

## Dependencies And Integration Points

The immediate dependency is `mt65xx.h`; the broader integration points are MediaTek pinctrl bindings, DTS files for MT6878 boards, and drivers for peripherals named in the mux constants. The header must match the SoC pin controller's register tables. Any mismatch between selector values and hardware documentation can make a board route a signal to the wrong pad even though the DTS compiles. Because many signals share pads across debug, RF, storage, USB, display, and low-power domains, integration risk is concentrated in board pin-state selection rather than in this header's mechanics.

## Risks And Test Signals

The main risks are ABI drift, typo-compatible mistakes, and invalid selector use. The macro names are the public binding for DTS authors, so renaming or changing numeric values can silently break out-of-tree board files. Dense areas such as JTAG owner selection, RF BPI/antenna pins, SPMI, UFS sideband, and MSDC0 lines need special care because wrong muxing may fail late during boot or only under a device-specific workload.

Useful test signals are `dtbs_check`, successful build of MT6878 DTBs that include this header, pinctrl probe logs without invalid mux errors, and hardware validation for each enabled board function: storage enumeration on MSDC0/1, I2C transactions on selected buses, UART console or modem links, display reset/TE behavior, audio capture/playback on selected I2S/DMIC pins, and RF/connectivity bring-up. A simple static check is that each GPIO has a selector-0 GPIO macro and that selector values remain within the encoding supported by the pinctrl driver.
