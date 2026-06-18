# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/mt6893-pinfunc.h

## Purpose

`mt6893-pinfunc.h` is the MT6893 pin multiplexing binding header. It exposes symbolic constants for selecting alternate functions on GPIO0 through GPIO219. Like the other MediaTek pinfunc headers, it is a compile-time ABI between DTS authors and the MediaTek pinctrl driver. It contains 1125 macro definitions and no executable C logic.

Each `PINMUX_GPIO<n>__FUNC_<name>` macro expands to `MTK_PIN_NO(n) | selector`. Selector 0 is GPIO mode; other selectors choose hardware functions. The SoC surface is broad: early pins cover SPI6, I2S5, PWM, modem interrupts, and touch-panel always-on signals; middle ranges include MSDC1, many SPI buses, I2S/TDM/PCM, DMIC, display reset/TE/PWM, SIM and modem UARTs, JTAG/DFD/UDI/debug ownership, MIPI RF sideband, SPMI, SCP SPI/I2C overlays, and RF BPI/antenna lines; high-numbered pins cover connectivity top, UFS sideband, MSDC0, power requests, PMIC wrapper SPI, RTC/watchdog, and audio MOSI/MISO pins.

## Important APIs And Types

The public interface is the macro set. There are no structs, enums, functions, or variables. Consumers use these names in devicetree pinctrl states, and the included `mt65xx.h` supplies `MTK_PIN_NO()` for packing the pin number. The header's naming also documents the alternate function matrix: SPI groups use suffixes such as `SPI4_A`, `SPI4_B`, `SPI4_C`, `SPI5_A`, `SPI5_B`, `SPI5_C`, and `SPI7_A/B`; audio groups include I2S0-9, TDM, PCM0/1, DMIC, and audio front-end MOSI/MISO lines; debug groups include ADSP, SCP, MD32, SPM, SSPM, MCUPM, APU, CCU, IPU, VPU, DFD, UDI, and IO JTAG selections.

Important contiguous regions include GPIO0-3 for SPI6/I2S5/PWM, GPIO10-25 for MSDC1 and SPI/I2S/display combinations, GPIO31-39 for I2S/PCM/SPI5/DMIC/UART, GPIO45-56 for SIM/JTAG/LVTS and MSDC1/PCM/JTAG overlaps, GPIO63-84 for BPI and connectivity BPI lines, GPIO96-113 for TDM/I2S/SPI/JTAG and PCM, GPIO118-129 for I2C/DMIC/CMFLASH/PWM/MD32, GPIO130-147 for camera reference, antenna, SCP/MD32/ADSP JTAG and SPI3, GPIO156-171 for SPI1/SPI0/SCP/MRG/PTA/antenna, GPIO172-182 for connectivity/UFS, GPIO183-194 for MSDC0, GPIO195-205 for SCP VREQ/audio/I2C/SPI, GPIO206-213 for low-power clock/watchdog/PMIC/RTC, and GPIO214-219 for audio and UFS sideband.

## Control Flow, State, And Persistence

Control flow is indirect. DTS source includes this header, the preprocessor expands selected pinmux constants, `dtc` compiles those constants into a DTB, and the MediaTek pinctrl driver consumes the packed values while applying pinctrl states. The header itself has no branches and no storage. The persistent state is only the selected board devicetree configuration and the resulting DTB.

## Dependencies And Integration Points

The file includes local `mt65xx.h` rather than the angle-bracket dt-binding path used by older headers in this directory. It integrates with MT6893 DTS files, the MediaTek pinctrl binding, and every peripheral driver whose pins are described here. The macro values must remain synchronized with the SoC pin controller tables and with hardware documentation. Because this header names many debug and secure-world-adjacent signals, board authors must also coordinate with firmware and bootloader pin ownership.

## Risks And Test Signals

The risks are mostly hardware integration risks: wrong selector values can disable storage, route modem/SIM signals incorrectly, expose or steal debug pins, break audio timing, or prevent display/UFS/PMIC sideband communication. Compatibility risk is higher than normal because DTS sources may depend on exact macro names as binding ABI.

Test signals include clean `dtc` compilation of MT6893 DTS files, `dtbs_check` for pinctrl syntax, runtime pinctrl probe without invalid mux warnings, and targeted hardware tests: eMMC/SD on MSDC0/1, I2C and SPI transfers, audio path tests, display panel reset/TE and hotplug-related paths, UFS sideband operation, PMIC wrapper access, SIM/modem status, and connectivity bring-up. Static validation should catch duplicate or out-of-range selectors, missing GPIO mode macros, and accidental changes to existing macro values.
