# subset-b-000672 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/mt6878-pinfunc.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/mt6878-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/mt6893-pinfunc.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/mt6893-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/mt8167-pinfunc.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/mt8167-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/mt8173-pinfunc.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/mt8173-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/mt8196-gce.h -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/mt8196-gce.h

## Purpose

`mt8196-gce.h` is the MT8196 Global Command Engine devicetree binding header. It names GCE thread priority values, hardware event IDs, software synchronization tokens, resource lock tokens, GPR token ranges, and timer token ranges used by CMDQ/GCE clients. The file has 449 macro definitions and no executable code.

The header documents two event spaces. GCE0 is mainly display-oriented: display stream SOF/frame-done windows, WDMA/postmask/mutex/MDP reset events, DISP1 DSI/DP/DVO events, MML0/1 events, overlay events, DPC diagnostics, DPTX/eDPTX events, TE inputs, power-ack windows, and DSI/SPI aliases. GCE1 is mainly non-display: VENC instances, VDEC events, image pipeline events, camera events, SMI assertions, and image/camera QoS/QoF windows. It also defines software tokens for display sequencing, GPR register backup sets, image-system pools and power handshakes, secure-thread notification, user/poll/lock tokens, TZMP tokens, prebuilt lock tokens, and GPR timer tokens.

## Important APIs And Types

The exported API is a collection of integer macros. `CMDQ_THR_PRIO_LOWEST` through `CMDQ_THR_PRIO_HIGHEST` define priorities 0 through 7; lower-priority threads run only when no higher-priority thread is active and same-priority threads are round-robin scheduled. Hardware event macros are either fixed IDs or parameterized range helpers such as `CMDQ_EVENT_DISP0_STREAM_SOF(n)`, `CMDQ_EVENT_DISP1_DISP_DSI1_ENG_EVENT(n)`, `CMDQ_EVENT_IMG_QOF_ACK_EVENT(n)`, and `CMDQ_EVENT_CAM_SENINF_CFG_DONE_EVENT(n)`.

The software token API includes fixed tokens such as `CMDQ_SYNC_TOKEN_CONFIG_DIRTY`, `CMDQ_SYNC_TOKEN_STREAM_EOF`, `CMDQ_SYNC_TOKEN_ESD_EOF`, `CMDQ_SYNC_RESOURCE_WROT0`, and image-system power tokens, plus range helpers such as `CMDQ_SYNC_TOKEN_GPR_SET(n)`, `CMDQ_SYNC_TOKEN_IMGSYS_POOL(n)`, and `CMDQ_TOKEN_GPR_TIMER_R(n)`. Consumers pass these numeric IDs to CMDQ packet wait/clear/set APIs rather than interacting with C objects from this header.

## Control Flow, State, And Persistence

The header has no local control flow. It affects runtime command flow when client drivers embed event or token IDs into CMDQ packets. At runtime, the GCE firmware/hardware waits for, clears, or sets these IDs as command packets execute. State lives in the GCE event/token machinery, not in this file. Persistence is limited to DTS/kernel source ABI and compiled code or DTBs that reference these constants.

## Dependencies And Integration Points

There is no include dependency beyond the header guard. The integration points are MediaTek CMDQ/GCE client drivers, especially display, MML/MDP, overlay, DPTX/eDPTX, encoder/decoder, image pipeline, camera, SMI, secure-world/TZMP, and prebuilt-command users. Numeric values must match the MT8196 hardware event wiring and the CMDQ driver's expectations. Parameterized macros rely on callers passing indices in the documented range; the C preprocessor does not enforce bounds.

## Risks And Test Signals

The key risk is numeric collision or mismatch. Event IDs and software tokens share hardware-visible namespaces, and the file intentionally contains aliases or overlaps in the common-token area, such as `CMDQ_SYNC_TOKEN_TPR_LOCK` sharing 942 with `CMDQ_SYNC_TOKEN_USER_1` and `CMDQ_SYNC_TOKEN_TZMP_DISP_WAIT` sharing 943 with `CMDQ_SYNC_TOKEN_POLL_MONITOR`. Those overlaps may be intentional ABI compatibility but must be reviewed before changing. Parameterized windows can also generate invalid IDs if callers pass out-of-range `n`.

Validation signals include building MT8196 CMDQ clients, boot logs from the CMDQ/GCE driver, display pipeline tests exercising SOF/frame-done/mutex/TE tokens, MML/MDP and overlay reset/frame-done tests, DPTX/eDPTX hotplug or stream tests, camera and image pipeline frame completion tests, VENC/VDEC completion paths, secure-world token handshakes, and timeout-path tests using GPR timer tokens. Static review should check that documented contiguous ranges do not collide unexpectedly and that every changed ID is reflected in hardware documentation and client usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/mt8196-gce.h -->
