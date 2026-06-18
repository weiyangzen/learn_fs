# Research Report: subset-b-000673

This grouped report covers the exact source files assigned to `subset-b-000673`. Each file section is delimited for the reconciliation splitter and preserves the source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/mt8196-pinfunc.h -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/mt8196-pinfunc.h

## Purpose
This MediaTek MT8196 device-tree binding header enumerates pinmux constants for the arm64 MT8196 SoC. It maps each GPIO pin and alternate function to the integer encoding consumed by MediaTek pinctrl device-tree nodes, using `MTK_PIN_NO(n) | mux` from `dt-bindings/pinctrl/mt65xx.h`. The file is purely declarative and contains 1,289 pin-function macros spanning GPIO0 through GPIO270.

## APIs, Types, And Constants
There are no C functions or runtime types. The exported API is a macro namespace of the form `PINMUX_GPIO<n>__FUNC_<name>`. Mode `0` is consistently the GPIO function, while higher mux values select peripheral functions. Covered functions include display, audio, I2C, SPI, UART, JTAG, debug monitor, SCP/ADSP, USB VBUS/IDDIG, and GBE/AVB signals.

## Control Flow And State
There is no control flow, state, allocation, or persistence. The preprocessor expands constants into DTS pinctrl properties at build time. Once a DTB is built, the encoded values become persistent hardware configuration data in the device tree blob.

## Dependencies And Integration
The file depends on the generic MediaTek pinctrl binding macro `MTK_PIN_NO`. It integrates with MT8196 DTS/DTSI files and the kernel MediaTek pinctrl driver that interprets pin number plus mux function values.

## Risks And Test Signals
The main risk is numeric or naming drift from the silicon datasheet: a wrong mux value can silently route a board signal to the wrong peripheral. DTC only validates syntax and include availability, not hardware correctness. Test signals are successful DTB compilation, pinctrl binding checks, boot logs without unknown pinmux errors, and board-level validation of affected peripherals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/mt8196-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/mt8516-pinfunc.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/mt8516-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/microchip/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/microchip/Makefile

## Purpose
This Makefile declares Microchip arm64 DTBs built by the kernel device-tree build. It gates LAN969x and Sparx5 board DTBs behind their architecture Kconfig symbols.

## APIs, Types, And Functions
The file exports no code APIs. Its build interface is `dtb-$(CONFIG_ARCH_LAN969X)` and `dtb-$(CONFIG_ARCH_SPARX5)` assignments. It lists one LAN9696 EVB DTB and five Sparx5 PCB variants, including eMMC variants for PCB134 and PCB135.

## Control Flow, State, And Persistence
Kbuild evaluates the conditional `dtb-y` fragments during `make dtbs` or kernel builds. There is no runtime state. The persistent output is the selected `.dtb` files in the build tree.

## Dependencies And Integration
The Makefile depends on the corresponding DTS files and Kconfig symbols. It integrates with `scripts/Makefile.lib` device-tree rules through the architecture DTS directory hierarchy.

## Risks And Test Signals
Risks include stale board names, missing DTS files, or DTBs not being built because the wrong Kconfig symbol is used. Test by enabling `CONFIG_ARCH_LAN969X` or `CONFIG_ARCH_SPARX5` and running `make dtbs`; missing-source failures or absent output DTBs indicate integration breakage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/microchip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/microchip/clk-lan9691.h -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/microchip/clk-lan9691.h

## Purpose
This binding header assigns clock IDs for the Microchip LAN9691 clock controller. DTS files use these numeric IDs in `clocks` or clock-controller specifier cells.

## APIs, Types, And Constants
The macro API defines generic clock IDs `GCK_ID_QSPI0` through `GCK_ID_USB_REFCLK` with values 0 through 11, followed by gate clock IDs `GCK_GATE_USB_DRD`, `GCK_GATE_MCRAMC`, and `GCK_GATE_HMATRIX` with values 12 through 14.

## Control Flow And State
There is no executable control flow or state. The constants are compiled into DTBs and then interpreted by the LAN9691 clock provider driver.

## Dependencies And Integration
The header is protected by `_DTS_CLK_LAN9691_H` and uses no includes. Its integration point is the binding contract between LAN9691 DTS nodes and the clock driver.

## Risks And Test Signals
The risk is ABI mismatch: changing IDs or inserting values can break existing DTBs and driver lookup tables. Build tests catch missing includes, but functional tests require booting LAN9691 boards and verifying clock consumers probe successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/microchip/clk-lan9691.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/nuvoton/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/nuvoton/Makefile

## Purpose
This Makefile registers Nuvoton arm64 board DTBs for the MA35 and NPCM families.

## APIs, Types, And Functions
There are no runtime APIs. Kbuild consumes three `dtb-$(CONFIG_...)` assignments: two MA35D1 boards under `CONFIG_ARCH_MA35` and the `nuvoton-npcm845-evb.dtb` under `CONFIG_ARCH_NPCM`.

## Control Flow, State, And Persistence
Kbuild conditionally appends DTB targets based on the selected architecture config. The only persisted artifacts are built DTBs.

## Dependencies And Integration
The Makefile depends on the named DTS files and on architecture Kconfig symbols. It integrates with the arm64 DTS build target list.

## Risks And Test Signals
Risks are omitted boards, renamed DTS files, or incorrect Kconfig gating. Run `make ARCH=arm64 dtbs` with each architecture enabled and confirm all three DTB outputs are produced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/nuvoton/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/nvidia/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/nvidia/Makefile

## Purpose
This Makefile lists NVIDIA Tegra arm64 board DTBs and enables overlay symbol generation for selected boards. It covers Tegra132, Tegra210, Tegra186, Tegra194, Tegra234, and Tegra264 platforms.

## APIs, Types, And Functions
The build-facing API is a series of `DTC_FLAGS_<dtb-base> := -@` assignments and 21 `dtb-$(CONFIG_ARCH_TEGRA_*_SOC)` entries. The `-@` flag causes the device-tree compiler to emit symbols for overlay support on chosen Jetson and reference boards.

## Control Flow, State, And Persistence
Kbuild evaluates config-guarded DTB targets. There is no runtime state. The persistent outputs are `.dtb` files, with symbol sections included for boards covered by `DTC_FLAGS_*`.

## Dependencies And Integration
The file depends on DTS files named after Tegra boards and SOC Kconfig options. It integrates with overlay workflows because symbol-enabled DTBs can accept runtime or bootloader-applied overlays.

## Risks And Test Signals
Risks include missing `-@` on a board that needs overlays, stale board names, and incorrect SoC gating. Test with `make dtbs`, inspect generated DTBs for `__symbols__` when overlays are required, and boot representative Tegra platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/nvidia/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/Makefile

## Purpose
This Qualcomm arm64 DTS Makefile is a large target registry for Qualcomm phones, laptops, routers, development boards, automotive boards, and composed overlay products. It is guarded by `CONFIG_ARCH_QCOM`.

## APIs, Types, And Functions
The build API is Kbuild DTB target assignment. The file has 359 `dtb-$(CONFIG_ARCH_QCOM)` lines, 58 `*-dtbs :=` composition rules, 62 `.dtbo` mentions, and over 500 `.dtb` mentions. Composition rules combine a base DTB with one or more overlays, for example camera mezzanine, EL2, IFP, navigation, and vision mezzanine variants.

## Control Flow, State, And Persistence
Kbuild evaluates all target lists when Qualcomm architecture support is enabled. `*-dtbs := base.dtb overlay.dtbo` tells Kbuild to produce a combined DTB target from components. There is no runtime state in the Makefile, but the produced DTBs are persistent boot artifacts.

## Dependencies And Integration
The file depends on a broad set of Qualcomm DTS/DTSI/DTBO sources and Kbuild overlay-composition support. It integrates tightly with board bring-up because adding or removing a board normally requires a synchronized Makefile entry.

## Risks And Test Signals
The dominant risks are target omission, invalid composition order, stale overlay names, and unintended build coverage changes across hundreds of boards. Test signals include `make ARCH=arm64 dtbs`, `make ARCH=arm64 dtbs_check` for changed boards, and explicit verification that composed `.dtb` outputs are generated for overlay variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/glymur-ipcc.h -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/glymur-ipcc.h

## Purpose
This Qualcomm binding header defines IPCC mailbox client and signal IDs for the Glymur platform. DTS mailbox specifiers use these constants to address remote processors and interrupt channels.

## APIs, Types, And Constants
The macro API is split into physical client IDs (`IPCC_MPROC_*`), compute low-power level IDs (`IPCC_COMPUTE_L0_*`, `IPCC_COMPUTE_L1_*`), and peripheral IDs (`IPCC_PERIPH_*`). It covers AOP, TZ, modem, LPASS, SLPI, SDC, CDSP, NPU, APSS, GPU, PCIe instances, SPSS, TME, WPSS, SOCCP, and media/display units.

## Control Flow And State
There is no executable flow or state. Constants become numeric mailbox cells in DTBs and are interpreted by Qualcomm IPCC/mailbox-related drivers.

## Dependencies And Integration
The header has only include guards and no includes. It integrates with Glymur DTS files and the Qualcomm IPCC binding, where client and signal IDs must match firmware/hardware routing tables.

## Risks And Test Signals
Risks are ABI mismatches against firmware, duplicate or wrong numeric IDs, and confusing platform-specific IDs with another SoC. Tests are DTB compilation, mailbox driver probe, remoteproc bring-up, and functional IPC between APSS and remote processors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/glymur-ipcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/kaanapali-ipcc.h -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/kaanapali-ipcc.h

## Purpose
This binding header defines Qualcomm Kaanapali platform IPCC mailbox identifiers for use in device-tree mailbox specifiers.

## APIs, Types, And Constants
It exports physical client IDs such as `IPCC_MPROC_AOP`, `TZ`, `MPSS`, `LPASS`, `SDC`, `CDSP`, `APSS`, `SOCCP`, `DCP`, `SPSS`, `TME`, and `WPSS`. It also defines compute L0/L1 IDs, peripheral IDs for CDSP/APSS/PCIe, and fence IDs for CDSP, APSS, GPU, CVP, camera, DCP, VPU, and SOCCP.

## Control Flow And State
The file is declarative. Numeric constants are expanded into DTBs and consumed at runtime by mailbox/IPCC drivers and remote processor integrations.

## Dependencies And Integration
There are no includes. The integration contract is the Kaanapali firmware and hardware IPCC routing table. DTS files must include this platform-specific header rather than reusing IDs from related Qualcomm SoCs.

## Risks And Test Signals
Risks include duplicate aliases with different meanings, wrong fence IDs, and mismatched values across firmware revisions. Build tests only validate preprocessing; runtime signals are successful mailbox probe, remoteproc startup, and IPC/fence operations without timeout errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/kaanapali-ipcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/realtek/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/realtek/Makefile

## Purpose
This Makefile registers Realtek arm64 DTBs under `CONFIG_ARCH_REALTEK`.

## APIs, Types, And Functions
It contains 12 `dtb-$(CONFIG_ARCH_REALTEK)` entries. These select board DTBs for Realtek SoC families when the architecture option is enabled.

## Control Flow, State, And Persistence
Kbuild conditionally includes all listed DTB targets. No runtime code or mutable state exists. The outputs are built DTB artifacts.

## Dependencies And Integration
The file depends on matching DTS sources in the Realtek DTS directory and on the Realtek architecture Kconfig symbol. It integrates with the global arm64 `dtbs` build.

## Risks And Test Signals
Risks are missing board entries, renamed DTS files, or a DTB entry left behind after source removal. Run `make ARCH=arm64 dtbs` with Realtek support and confirm all listed targets build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/realtek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/renesas/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/renesas/Makefile

## Purpose
This Makefile declares Renesas arm64 DTBs and overlay compositions across R-Car, RZ/G, RZ/V, and related families. It uses many SoC-specific Kconfig guards.

## APIs, Types, And Functions
The build interface consists of 145 `dtb-$(CONFIG_...)` assignments and 39 `*-dtbs :=` composition rules. It references 66 `.dtbo` overlays and 223 `.dtb` names. It also sets a specific DTC warning suppression, `DTC_FLAGS_r8a779g3-sparrow-hawk += -Wno-spi_bus_bridge`, for a named board.

## Control Flow, State, And Persistence
Kbuild evaluates targets according to the enabled Renesas SoC symbols. Overlay composition rules build combined board variants. The Makefile does not hold runtime state; built DTBs persist as boot artifacts.

## Dependencies And Integration
Dependencies include the named DTS/DTBO files, Renesas Kconfig symbols, and Kbuild composition rules. The file is the bridge between board DTS additions and the arm64 build.

## Risks And Test Signals
Risks include incorrect SoC guards, missing overlay components, and DTC warning suppression hiding a real binding issue if overused. Test with `make ARCH=arm64 dtbs`, focused `dtbs_check` for changed boards, and verification that composed board variants appear in the build output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/renesas/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/renesas/rzg3s-smarc-switches.h -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/renesas/rzg3s-smarc-switches.h

## Purpose
This board-configuration header documents and encodes on-board switch settings for the Renesas RZ/G3S SMARC module and RZ SMARC Carrier II.

## APIs, Types, And Constants
The macro API defines `SW_OFF` and `SW_ON`, then sets board switch constants: `SW_CONFIG2` selects SD0 connected to eMMC, `SW_CONFIG3` selects SCIF1/SSI0/IRQ0/IRQ1 connected to the SoC, and `SW_OPT_MUX4` routes SMARC SER0 signals to PMOD1.

## Control Flow And State
There is no runtime control flow. These macros are a source-level representation of physical board switch state and are expanded into DTS conditional configuration.

## Dependencies And Integration
The header has no includes and is consumed by RZ/G3S SMARC DTS files. It integrates physical board assembly/switch positions with device-tree descriptions.

## Risks And Test Signals
The risk is documentation drift from actual switch positions, causing DTS to describe unavailable peripherals. Tests are DTB compilation plus board validation of SD/eMMC, serial, audio, IRQ, and PMOD routing under the documented switch settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/renesas/rzg3s-smarc-switches.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/Makefile

## Purpose
This Makefile registers Rockchip arm64 board DTBs and overlay compositions under `CONFIG_ARCH_ROCKCHIP`.

## APIs, Types, And Functions
It contains 247 `dtb-$(CONFIG_ARCH_ROCKCHIP)` lines, 20 `*-dtbs :=` composition rules, 44 `.dtbo` mentions, and 297 `.dtb` mentions. A comment notes symbol generation behavior for base DTBs used with overlay composition.

## Control Flow, State, And Persistence
Kbuild assembles direct DTB targets and composed DTB targets from base DTBs plus overlays. There is no runtime state in the Makefile. Built DTBs are persistent boot artifacts.

## Dependencies And Integration
The file depends on the named Rockchip DTS/DTBO files, `CONFIG_ARCH_ROCKCHIP`, and Kbuild overlay support. It integrates board DTS additions into the global arm64 build.

## Risks And Test Signals
Risks include missing overlay symbol support, stale composed target names, and accidental omission of a board from `dtbs`. Test with `make ARCH=arm64 dtbs`, inspect outputs for composed targets, and run `dtbs_check` for changed boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/rk8xx.h -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/rk8xx.h

## Purpose
This binding header defines device-tree constants for Rockchip RK8xx PMIC reset behavior.

## APIs, Types, And Constants
The exported constants are `RK806_RESTART`, `RK806_RESET`, and `RK806_RESET_NOTIFY` for the `rockchip,reset-mode` property. They encode how the RK806 PMIC should participate in restart/reset flows.

## Control Flow And State
There is no code flow or state. DTS sources use these constants, and the PMIC driver interprets the resulting property at runtime.

## Dependencies And Integration
The header has no includes. Its integration point is the Rockchip RK8xx/RK806 PMIC binding and any board DTS node that sets `rockchip,reset-mode`.

## Risks And Test Signals
Risks are semantic mismatch between DTS value and driver behavior, especially because reset behavior affects reboot reliability. Build tests catch include failures; runtime tests should exercise reboot, reset, and notification paths on boards using the property.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/rk8xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/socionext/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/socionext/Makefile

## Purpose
This Makefile registers Socionext UniPhier arm64 board DTBs.

## APIs, Types, And Functions
It exposes one `dtb-$(CONFIG_ARCH_UNIPHIER)` assignment containing eight UniPhier DTB targets.

## Control Flow, State, And Persistence
Kbuild appends the target list when UniPhier support is enabled. There is no runtime state; the outputs are DTB files.

## Dependencies And Integration
The file depends on the listed UniPhier DTS sources and `CONFIG_ARCH_UNIPHIER`. It integrates with the arm64 DTB build pipeline.

## Risks And Test Signals
Risks are stale target names or missing board coverage. `make ARCH=arm64 dtbs` with UniPhier enabled should produce all listed DTBs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/socionext/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/sophgo/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/sophgo/Makefile

## Purpose
This Makefile registers the Sophgo arm64 DTB target.

## APIs, Types, And Functions
It contains one `dtb-$(CONFIG_ARCH_SOPHGO)` assignment for `sg2042-milkv-pioneer.dtb`.

## Control Flow, State, And Persistence
Kbuild conditionally appends the DTB when Sophgo architecture support is enabled. The built DTB is the only artifact.

## Dependencies And Integration
The Makefile depends on the matching DTS source and the Sophgo Kconfig symbol. It integrates the board into `make dtbs`.

## Risks And Test Signals
Risks are limited to stale target naming or missing DTS source. Build `dtbs` with `CONFIG_ARCH_SOPHGO` enabled and verify the output exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/sophgo/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/sprd/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/sprd/Makefile

## Purpose
This Makefile registers Spreadtrum/Unisoc arm64 board DTBs.

## APIs, Types, And Functions
It has one `dtb-$(CONFIG_ARCH_SPRD)` assignment containing five DTB targets.

## Control Flow, State, And Persistence
Kbuild includes the target list when `CONFIG_ARCH_SPRD` is enabled. No runtime state exists; outputs are DTBs.

## Dependencies And Integration
It depends on the named DTS sources and the architecture Kconfig symbol. It is consumed by the arm64 DTS Kbuild hierarchy.

## Risks And Test Signals
Risks are missing or renamed DTS files and incomplete board coverage. `make ARCH=arm64 dtbs` with Spreadtrum support is the primary test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/sprd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/st/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/st/Makefile

## Purpose
This Makefile registers STMicroelectronics STM32 arm64 board DTBs.

## APIs, Types, And Functions
It contains one `dtb-$(CONFIG_ARCH_STM32)` assignment with four STM32MP257 board DTBs.

## Control Flow, State, And Persistence
Kbuild conditionally includes the targets when STM32 support is enabled. It has no runtime behavior or mutable state.

## Dependencies And Integration
The file depends on corresponding DTS files and `CONFIG_ARCH_STM32`. It integrates STM32 board descriptions with the arm64 DTB build.

## Risks And Test Signals
Risks are stale target references and incomplete board build coverage. Run `make ARCH=arm64 dtbs` with STM32 enabled and verify all four outputs build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/st/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/synaptics/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/synaptics/Makefile

## Purpose
This Makefile registers Synaptics Berlin arm64 board DTBs.

## APIs, Types, And Functions
It has two `dtb-$(CONFIG_ARCH_BERLIN)` entries for AS370 reference boards.

## Control Flow, State, And Persistence
Kbuild evaluates the target list when Berlin architecture support is enabled. There is no runtime state.

## Dependencies And Integration
It depends on the matching DTS files and `CONFIG_ARCH_BERLIN`. It integrates with the global arm64 DTS build.

## Risks And Test Signals
Risks are stale file names and missing build coverage. Test with `make ARCH=arm64 dtbs` under Berlin support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/synaptics/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/tesla/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/tesla/Makefile

## Purpose
This Makefile registers the Tesla FSD arm64 EVB DTB.

## APIs, Types, And Functions
It contains one `dtb-$(CONFIG_ARCH_TESLA_FSD)` entry for `fsd-evb.dtb`.

## Control Flow, State, And Persistence
Kbuild conditionally appends the DTB target based on the Tesla FSD architecture option. The output is a DTB artifact.

## Dependencies And Integration
The file depends on `fsd-evb.dts` and `CONFIG_ARCH_TESLA_FSD`. It integrates the board into the arm64 DTB build.

## Risks And Test Signals
Risks are stale source names or missing architecture gating. Build `dtbs` with Tesla FSD enabled and check for `fsd-evb.dtb`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/tesla/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/tesla/fsd-pinctrl.h -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/tesla/fsd-pinctrl.h

## Purpose
This binding header defines Tesla FSD pinctrl constants for pull, drive strength, and function selectors.

## APIs, Types, And Constants
It exports pull constants `FSD_PIN_PULL_NONE`, `FSD_PIN_PULL_DOWN`, and `FSD_PIN_PULL_UP`; drive levels `FSD_PIN_DRV_LV1`, `LV2`, `LV4`, and `LV6`; and function selectors for input, output, alternate functions 2 through 6, and external interrupt function `0xf`.

## Control Flow And State
There is no executable control flow. DTS files use these numeric constants in pin configuration properties, and the pinctrl driver interprets them at boot.

## Dependencies And Integration
The file has only include guards. It integrates with Tesla FSD DTS pinctrl nodes and the Samsung-derived/Tesla FSD pinctrl binding.

## Risks And Test Signals
Risks include wrong numeric encoding for drive strength or function mode, which can cause electrical or routing faults. Tests are DTB compilation, pinctrl driver probe, and board-level validation of configured GPIO/peripheral pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/tesla/fsd-pinctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/ti/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/ti/Makefile

## Purpose
This Makefile registers Texas Instruments K3-family arm64 DTBs and overlays. Entries are grouped by SoC family and board class.

## APIs, Types, And Functions
The build interface includes 115 `dtb-$(CONFIG_ARCH_K3)` lines, 69 `*-dtbs :=` composition rules, 113 `.dtbo` mentions, and 311 `.dtb` mentions. Groups cover AM62x, AM62Ax, AM62Dx, AM62Lx, AM62Px, AM64x, AM65x, J7200, J721E, J721S2, J722S, J784S4, and J742S2. A build-time-test section uses `dtb- += ...` entries enabled by `CONFIG_OF_ALL_DTBS`, and the file sets global `DTC_FLAGS := -@` for overlay symbol support.

## Control Flow, State, And Persistence
Kbuild conditionally builds board DTBs and overlay-composed DTBs. There is no runtime state in the Makefile. The persistent outputs are direct DTBs, DTBOs, and composed DTBs.

## Dependencies And Integration
The file depends on TI K3 DTS/DTBO sources, `CONFIG_ARCH_K3`, `CONFIG_OF_ALL_DTBS`, and Kbuild overlay support. It is a central integration point for TI board enablement and overlay test coverage.

## Risks And Test Signals
Risks include incomplete composed-target coverage, missing `-@` symbols for overlays, stale board references, and `dtb-` build-test entries diverging from real overlay combinations. Test with `make ARCH=arm64 dtbs`, `make ARCH=arm64 dtbs_check`, and output checks for composed overlay DTBs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/ti/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/ti/k3-pinctrl.h -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/ti/k3-pinctrl.h

## Purpose
This binding header provides pinctrl bit definitions and SoC-specific IOPAD helper macros for the TI K3 SoC family.

## APIs, Types, And Constants
The API defines bit shifts for wake, debounce, Schmitt trigger, pull, input, drive strength, isolation, and deep-sleep fields. User-facing macros include `PIN_OUTPUT`, `PIN_INPUT`, pull-up/down variants, no-Schmitt input variants, debounce levels, drive strength values, deep-sleep pin state helpers, wakeup helpers, and `PIN_GPIO_RANGE_IOPAD`. IOPAD helpers such as `AM62X_IOPAD`, `AM64X_IOPAD`, `AM65X_IOPAD`, `J721E_IOPAD`, and `J784S4_IOPAD` emit address offset plus config value cells.

## Control Flow And State
There is no runtime control flow. The macros build packed pin configuration values in DTS source; those values persist in DTBs and are consumed by K3 pinctrl drivers.

## Dependencies And Integration
The header has no includes and is included by TI K3 DTS files. It integrates with K3 pinctrl register layout and the `pinctrl-single`/TI pinctrl binding style.

## Risks And Test Signals
Risks include bit-shift errors, wrong pad-offset masking, and applying a SoC helper to the wrong pad domain. Tests include DTB compilation, `dtbs_check`, pinctrl probe logs, suspend/resume wake tests, and board-level validation of pull, input, and drive behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/ti/k3-pinctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/ti/k3-serdes.h -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/ti/k3-serdes.h

## Purpose
This binding header defines SERDES lane mux constants for TI K3 SoCs.

## APIs, Types, And Constants
The exported constants map SoC, SERDES instance, lane, and function to numeric mux values. Covered families include J721E, J7200, AM64, J721S2, J784S4, and J722S. Functions include PCIe lanes, USB/USB swap, QSGMII/SGMII lanes, eDP lanes, and unused IP slots.

## Control Flow And State
There is no code flow or state. DTS files use these constants in SERDES mux properties; the chosen values become persistent DTB data interpreted by TI SERDES/PHY drivers.

## Dependencies And Integration
The header has no includes. It integrates with K3 board DTS files that route high-speed lanes among PCIe, USB, Ethernet, and display functions.

## Risks And Test Signals
Risks are lane swap mistakes, selecting a mux value not supported by board wiring, or using constants from the wrong SoC family. Test signals include DTB compilation, PHY/PCIe/USB/Ethernet/display probe success, link training, and board-level high-speed interface validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/ti/k3-serdes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/toshiba/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/toshiba/Makefile

## Purpose
This Makefile registers Toshiba Visconti arm64 board DTBs.

## APIs, Types, And Functions
It contains two `dtb-$(CONFIG_ARCH_VISCONTI)` assignments for `tmpv7708-rm-mbrc.dtb` and `tmpv7708-visrobo-vrb.dtb`.

## Control Flow, State, And Persistence
Kbuild appends the targets when Visconti support is enabled. There is no runtime state.

## Dependencies And Integration
The file depends on matching DTS files and `CONFIG_ARCH_VISCONTI`. It integrates with the global arm64 DTB build.

## Risks And Test Signals
Risks are stale target names or omitted board entries. Test by building arm64 DTBs with Visconti enabled and confirming both outputs are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/toshiba/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/xilinx/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/xilinx/Makefile

## Purpose
This Makefile registers Xilinx ZynqMP and Versal Net arm64 DTBs, including composed Kria starter-kit variants.

## APIs, Types, And Functions
The build API contains 35 `dtb-$(CONFIG_ARCH_ZYNQMP)` entries, 14 `*-dtbs :=` composition rules, 14 `.dtbo` mentions, and 63 `.dtb` mentions. It lists Ultra96, ZCU, ZC, K24/K26 SOM/starter-kit, and Versal Net board targets.

## Control Flow, State, And Persistence
Kbuild builds direct targets and combines SOM base DTBs with starter-kit overlays into composed DTBs. No runtime state exists in the Makefile.

## Dependencies And Integration
The file depends on ZynqMP/Versal DTS and DTBO sources and `CONFIG_ARCH_ZYNQMP`. It integrates with Kbuild overlay composition for Kria board variants.

## Risks And Test Signals
Risks include stale revision-specific target names, invalid base-plus-overlay composition, and missing board coverage. Test with `make ARCH=arm64 dtbs`, ensure composed K24/K26 outputs build, and run `dtbs_check` for changed boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/xilinx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/xilinx/xlnx-zynqmp-clk.h -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/xilinx/xlnx-zynqmp-clk.h

## Purpose
This binding header defines clock IDs for the Xilinx ZynqMP firmware clock interface.

## APIs, Types, And Constants
It exports numeric IDs from `IOPLL` 0 through `LPD_WDT` 112. The constants cover PLLs, PLL routing and mux nodes, CPU clocks, debug clocks, display/audio clocks, DMA, DDR, SATA, PCIe, GPU, USB, R5, CSU, GEM TX/RX/reference clocks, QSPI, SDIO, UART, SPI, NAND, I2C, CAN, PL fabric clocks, watchdog, and miscellaneous firmware-managed clocks.

## Control Flow And State
There is no executable flow. DTS clock specifiers use these IDs, and firmware-backed clock drivers map them to runtime operations. The IDs persist in DTBs as ABI data.

## Dependencies And Integration
The header has no includes. It integrates with ZynqMP DTS files and the ZynqMP firmware clock provider.

## Risks And Test Signals
The major risk is ABI breakage if IDs diverge from firmware definitions or driver tables. Tests are DTB compilation, clock provider probe, and peripheral probe success for consumers using these clock IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/xilinx/xlnx-zynqmp-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/install.sh -->
# sources/distributed-fs/ceph-client/arch/arm64/boot/install.sh

## Purpose
This shell script implements `make install` behavior for the AArch64 Linux port. It installs the kernel image and matching `System.map` into the requested install path.

## APIs, Types, And Functions
The script interface is positional: `$1` kernel version, `$2` kernel image, `$3` system map file, and `$4` install path. It chooses basename `vmlinuz` for `Image.gz` or `vmlinuz.efi`, otherwise `vmlinux`. It preserves previous outputs by renaming existing `$base-$version` and `System.map-$version` to `.old`.

## Control Flow, State, And Persistence
With `set -e`, failures stop the install. The script branches on `basename $2`, moves old files if present, writes the kernel image with `cat $2 > $4/$base-$1`, and copies the map with `cp $3 $4/System.map-$1`. Persistent state is the installed kernel, map, and `.old` backups.

## Dependencies And Integration
It depends on POSIX shell utilities `basename`, `mv`, `cat`, and `cp`. It is called from the arm64 kernel build install target and assumes the install path exists.

## Risks And Test Signals
Arguments are mostly unquoted, so paths containing whitespace are risky. An empty or unexpected install path could install in the wrong location. Test with `make ARCH=arm64 install INSTALL_PATH=...`, compressed and uncompressed images, and verification of backup rotation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm64/crypto/Kconfig

## Purpose
This Kconfig menu exposes arm64 accelerated cryptographic algorithms to kernel configuration.

## APIs, Types, And Functions
It defines tristate options for GHASH with ARMv8 Crypto Extensions, AES CE block modes, AES NEON block modes, AES bit-sliced NEON modes, SM4 CE cipher, SM4 CE block modes, SM4 NEON block modes, AES CE CCM, SM4 CE CCM, and SM4 CE GCM. Options depend on `KERNEL_MODE_NEON` and select crypto core helpers such as `CRYPTO_SKCIPHER`, `CRYPTO_AEAD`, `CRYPTO_LIB_AES`, `CRYPTO_LIB_AES_CBC_MACS`, `CRYPTO_SM4`, and GF128 helpers.

## Control Flow, State, And Persistence
There is no runtime flow. Kconfig selection persists in `.config`, which drives compilation of the corresponding modules or built-in objects.

## Dependencies And Integration
The file integrates the arm64 crypto directory with the kernel crypto API and module build. It coordinates with the local Makefile object names and with CPU feature gating in the modules themselves.

## Risks And Test Signals
Risks are missing `select` dependencies, incorrectly broad CPU capability claims, and enabling code paths without kernel-mode SIMD support. Test signals include Kconfig dependency resolution, `allyesconfig`/`allmodconfig` builds, crypto selftests, and runtime algorithm registration on CPUs with and without relevant features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm64/crypto/Makefile

## Purpose
This Makefile maps arm64 crypto Kconfig options to kernel objects and sub-object composition.

## APIs, Types, And Functions
It declares `obj-$(CONFIG_...)` targets for SM4 CE cipher, SM4 CE block, SM4 CE CCM/GCM, SM4 NEON, GHASH CE, AES CE CCM, AES CE block, AES NEON block, and AES NEON bit-sliced implementations. Composite variables such as `aes-ce-ccm-y := aes-ce-ccm-glue.o aes-ce-ccm-core.o` define module internals.

## Control Flow, State, And Persistence
Kbuild evaluates selected config symbols and compiles linked objects accordingly. There is no runtime state in the Makefile; the persistent result is built-in objects or loadable modules.

## Dependencies And Integration
The Makefile depends on the Kconfig options in the same directory and on matching `.c`/`.S` source files. It integrates C glue with assembly cores, including wrappers `aes-glue-ce.o` and `aes-glue-neon.o` that include the shared `aes-glue.c`.

## Risks And Test Signals
Risks include object composition mismatches, missing assembly cores, or config names diverging from Kconfig. Test with arm64 `allmodconfig`, module load tests, and crypto manager selftests for the registered algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-ce-ccm-core.S -->
# sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-ce-ccm-core.S

## Purpose
This arm64 assembly file implements the AES-CCM encrypt/decrypt transform using ARMv8 Crypto Extensions.

## APIs, Types, And Functions
It exports `ce_aes_ccm_encrypt` and `ce_aes_ccm_decrypt`, matching the C glue declarations. Internal macros include `load_round_keys`, `dround`, `aes_encrypt`, and `aes_ccm_do_crypt`. The local function `ce_aes_ccm_crypt_tail` handles partial final blocks and optional final MAC encryption.

## Control Flow, State, And Persistence
The entry points load expanded AES round keys, load the current MAC, update the counter, run AES rounds, XOR plaintext/ciphertext into the MAC, write output blocks, update the IV counter, and optionally finalize the tag with the original IV. Tail handling rewinds pointers for short blocks, uses a `.rodata` permutation table, masks plaintext/ciphertext selection, and writes back the MAC. State is entirely caller-provided buffers and SIMD registers; there is no persistent global state.

## Dependencies And Integration
The file depends on arm64 assembler support, `linux/linkage.h`, `asm/assembler.h`, and ARMv8 Crypto Extension instructions. It is linked with `aes-ce-ccm-glue.o`.

## Risks And Test Signals
Risks include counter endian mistakes, tail-block out-of-bounds accesses, incorrect final-round key cancellation, and register clobber assumptions. Test through crypto API AES-CCM vectors, partial-block cases, in-place encryption/decryption, and CPUs with AES feature support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-ce-ccm-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-ce-ccm-glue.c -->
# sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-ce-ccm-glue.c

## Purpose
This C glue registers and implements the kernel crypto API AEAD algorithm `ccm(aes)` backed by ARMv8 AES Crypto Extensions.

## APIs, Types, And Functions
Important functions are `ccm_setkey`, `ccm_setauthsize`, `ccm_init_mac`, `ce_aes_ccm_auth_data`, `ccm_calculate_auth_mac`, `ccm_encrypt`, and `ccm_decrypt`. It declares assembly entry points `ce_aes_ccm_encrypt` and `ce_aes_ccm_decrypt`. The exported algorithm is `ccm_aes_alg` with driver name `ccm-aes-ce`, priority 300, AES block IV size, max auth size 16, and crypto API callbacks.

## Control Flow, State, And Persistence
Setkey expands AES keys into `crypto_aes_ctx`. Encryption validates CCM `L`, initializes B0/MAC state, preserves the original IV, walks AEAD scatterlists, enters `scoped_ksimd`, authenticates AAD, invokes assembly for data, and appends the auth tag. Decryption mirrors this flow, subtracts authsize from cryptlen, decrypts, reads the stored tag, and returns `-EBADMSG` on `crypto_memneq`. Persistent state is only the per-transform AES context.

## Dependencies And Integration
It depends on crypto AEAD/skcipher internals, scatterwalk, AES helpers, `ce_aes_expandkey`, `ce_aes_mac_update`, and `asm/simd.h`. Module init checks `cpu_have_named_feature(AES)` before `crypto_register_aead`.

## Risks And Test Signals
Risks include CCM length-field overflow, AAD length-tag handling, scatterlist/tail handling, and SIMD context misuse. Tests are crypto manager AES-CCM vectors, non-contiguous scatterlists, invalid auth sizes, short final blocks, bad-tag detection, and CPU feature-gated module loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-ce-ccm-glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-glue-ce.c -->
# sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-glue-ce.c

## Purpose
This wrapper builds the shared AES skcipher glue as the ARMv8 Crypto Extensions implementation.

## APIs, Types, And Functions
It defines `USE_V8_CRYPTO_EXTENSIONS` and includes `aes-glue.c`. That macro switches the shared implementation to CE mode, setting `MODE` to `ce`, priority to 300, using `ce_aes_*` assembly/core routines, and enabling CPU feature match registration.

## Control Flow, State, And Persistence
All control flow is inherited from `aes-glue.c`. This wrapper has no state, but its compile-time macro changes algorithm names, driver names, priority, function bindings, and module init gating.

## Dependencies And Integration
It depends on `aes-glue.c` and the CE backend symbols linked into `aes-ce-blk.o`. Kbuild uses it for `CONFIG_CRYPTO_AES_ARM64_CE_BLK`.

## Risks And Test Signals
Risks are compile-time macro drift or missing CE symbols. Test by building `aes-ce-blk`, checking registered drivers such as `ecb-aes-ce`, and running AES skcipher selftests on an AES-capable arm64 CPU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-glue-ce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-glue-neon.c -->
# sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-glue-neon.c

## Purpose
This wrapper builds the shared AES skcipher glue as the plain NEON implementation.

## APIs, Types, And Functions
It includes `aes-glue.c` without defining `USE_V8_CRYPTO_EXTENSIONS`. The shared code therefore sets `MODE` to `neon`, priority to 200, and binds operations to `neon_aes_*` backend routines.

## Control Flow, State, And Persistence
Runtime behavior is inherited from `aes-glue.c`. This wrapper contributes compile-time selection only; it has no mutable state.

## Dependencies And Integration
Kbuild uses this file for `CONFIG_CRYPTO_AES_ARM64_NEON_BLK`. It depends on shared glue and NEON backend symbols in the arm64 crypto directory.

## Risks And Test Signals
Risks are missing NEON symbols or algorithm registration conflicts with CE and bit-sliced implementations. Test by building `aes-neon-blk`, loading it on arm64 with kernel-mode NEON, and running AES skcipher selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-glue-neon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-glue.c -->
# sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-glue.c

## Purpose
This shared C glue registers arm64 accelerated AES skcipher algorithms for either ARMv8 Crypto Extensions or NEON, depending on the including wrapper.

## APIs, Types, And Functions
It defines contexts `crypto_aes_xts_ctx` and `crypto_aes_essiv_cbc_ctx`, key callbacks `skcipher_aes_setkey`, `xts_set_key`, and `essiv_cbc_set_key`, and request handlers for ECB, CBC, CTS-CBC, ESSIV-CBC, CTR, XCTR, and XTS encryption/decryption. The `aes_algs[]` table registers `ecb(aes)`, `cbc(aes)`, `ctr(aes)`, `xctr(aes)`, `xts(aes)`, `cts(cbc(aes))`, and `essiv(cbc(aes),sha256)` with mode-specific driver names and priorities.

## Control Flow, State, And Persistence
Requests use `skcipher_walk_virt` over scatterlists and enter `scoped_ksimd` around backend SIMD/AES operations. CBC and ECB process full blocks; CTR/XCTR copy sub-block tails into aligned temporary buffers to avoid out-of-bounds access; CTS-CBC and XTS split requests when ciphertext stealing crosses scatterwalk boundaries; ESSIV derives a second AES key from `sha256(in_key)`. Persistent state is per-transform AES expanded keys.

## Dependencies And Integration
The file depends on kernel crypto skcipher internals, AES/CTR/XTS/SHA helpers, scatterwalk, SIMD context helpers, and backend symbols selected by macros. CE builds use `module_cpu_feature_match(AES, aes_init)`; NEON builds use normal `module_init`.

## Risks And Test Signals
Risks include tail handling in CTR/XCTR, CTS/XTS scatterlist splitting, IV mutation semantics, incorrect key verification, SIMD usage in invalid contexts, and registration conflicts when bit-sliced AES is enabled. Test with crypto selftests and testmgr vectors for all modes, in-place and fragmented scatterlists, non-block-size lengths for stream-like modes, invalid XTS keys, and CPU feature matrix builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-glue.c -->
