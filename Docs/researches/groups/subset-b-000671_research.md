# subset-b-000671 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx94-power.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx94-power.h

### Purpose
This header is a devicetree binding constant file for NXP i.MX94 power and performance domains. It gives DTS authors stable integer IDs for SCMI or platform power-domain references, so board `.dts` files can request domains such as A55 cores, DDR, display, HSIO, NETC, NPU, wakeup, and NoC without embedding raw numeric literals.

### Important APIs, Types, And Functions
There are no C functions or types. The exported API is the macro namespace: `IMX94_PD_*` for 19 power domains and `IMX94_PERF_*` for 11 performance domains. The domain IDs are contiguous, starting at zero, and therefore behave like ABI values rather than arbitrary local constants.

### Control Flow
The file has no executable control flow. It is preprocessed into DTS/DTSI sources or other binding consumers. Runtime behavior happens later in the Linux power-domain and performance-domain providers that interpret the numeric IDs from the flattened device tree.

### State, Persistence, And Dependencies
The header has only include guards and numeric macros. It depends on consumers preserving the firmware-facing ID order implied by the comment history and NXP platform binding. It persists no state, but compiled DTBs persist these values as firmware/kernel boot ABI data.

### Integration Points
Integration points are i.MX94 SoC DTSI files, board DTS files, SCMI or NXP GPC/power-domain providers, generic PM domain users, and OPP/performance-domain bindings. Kernel drivers indirectly depend on these IDs when their device nodes list `power-domains` or performance constraints.

### Risks
The primary risk is ABI drift: renumbering or reusing an existing macro would silently change the domain requested by already-authored device trees. A second risk is mismatch with firmware domain ordering, especially for similarly named M70/M71, A55 core/package, and HSIO top/wake-always-on domains.

### Test Signals
Useful signals include `dtbs_check` on i.MX94 DTS files, successful boot with power-domain provider probe logs, runtime PM suspend/resume of devices in display/HSIO/NETC/NPU domains, and comparison against the SCMI firmware domain table. Source reading signal: 41 lines; 31 `#define` entries; no includes or functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx94-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx95-clock.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx95-clock.h

### Purpose
This file defines the devicetree clock IDs for NXP i.MX95. It is the symbolic binding layer between DTS `clocks` properties and the i.MX95 clock provider, with the opening source IDs explicitly matching i.MX95 SCMI firmware indices.

### Important APIs, Types, And Functions
There are no C functions or structs. The public API is the `IMX95_CLK_*` macro set. IDs 1-40 cover fixed or firmware-visible clock sources such as 32 kHz, 24 MHz, FRO, system/audio/video/ARM/DRAM/HSIO/LDB PLLs, and external inputs. `IMX95_CCM_NUM_CLK_SRC` is set to 41 and roots are then expressed as offsets from it, covering peripheral roots, bus roots, GPU/NPU/VPU/camera/display/HSIO/NETC clocks, wakeup clocks, selector clocks, and a GPU CGC gate.

### Control Flow
The header has no executable control flow. During DTS compilation, these macros become integer clock specifiers. At runtime, platform clock drivers decode those IDs from the device tree and route operations through the common clock framework or SCMI clock provider.

### State, Persistence, And Dependencies
The header carries no runtime state. Its persistent effect is in compiled DTBs. It depends on the i.MX95 SCMI firmware clock index contract for the first block and on the Linux i.MX95 CCM driver understanding the root and gate IDs after `IMX95_CCM_NUM_CLK_SRC`.

### Integration Points
Integration points include `imx95.dtsi`, board-level DTS files, the i.MX95 CCM/SCMI clock provider, common clock framework consumers, and peripheral nodes for UART, I2C, SPI, CAN, USDHC, audio, display, GPU, NPU, VPU, camera, HSIO, and NETC.

### Risks
Changing existing values is an ABI break for DTBs. The offset scheme around `IMX95_CCM_NUM_CLK_SRC` makes insertion errors easy: adding a source or root in the wrong position can shift many downstream IDs. Reserved source IDs 20-23 are deliberate holes and should not be casually repurposed without matching firmware and driver support.

### Test Signals
Useful signals include ARM64 `dtbs_check`, boot-time clock provider probe success, `/sys/kernel/debug/clk/clk_summary` entries for i.MX95 roots, and functional tests for clock-sensitive peripherals such as USDHC, LPUART, NETC, GPU/NPU/VPU, and display. Source reading signal: 188 lines; 176 `#define` entries; no includes or functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx95-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx95-pinfunc.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx95-pinfunc.h

### Purpose
This is the i.MX95 pin-function binding catalog. It maps each SoC pad/function combination to the five-cell tuple consumed by the Freescale/NXP IOMUXC pinctrl driver: `<mux_reg conf_reg input_reg mux_mode input_val>`.

### Important APIs, Types, And Functions
There are no C functions or types. The exported API is 726 `IMX95_PAD_*__*` macros. Each macro describes one alternate function for a physical pad, including DAP/JTAG, GPIO banks, ENET/NETC, CAN, FLEXIO, LPI2C/I3C, LPSPI, LPUART, SAI, PDM, USDHC, FLEXSPI/XSPI, MIPI/display/audio support, and wake/AON-mix signals.

### Control Flow
There is no executable control flow. DTS pinctrl groups reference these macros, the C preprocessor expands them into cells, and the pinctrl driver writes mux, pad configuration, and input-select registers when the state is applied during probe, suspend/resume, or pinctrl state changes.

### State, Persistence, And Dependencies
The header itself stores no state. Its values persist in compiled DTBs and become hardware register programming inputs. It depends on the i.MX95 IOMUXC register map, input select register layout, mux mode encoding, and the Freescale pinctrl binding that expects exactly five cells per pin function.

### Integration Points
Integration points include i.MX95 SoC and board DTSI pinctrl nodes, the `pinctrl-imx` family driver, and every peripheral node selecting a pinctrl state. It also intersects with clock and power-domain setup because many alternate functions belong to mixes such as AONMIX, NETCMIX, HSIO, display, and wakeup.

### Risks
The highest risk is an incorrect tuple: a wrong mux offset, input-select offset, mux mode, or daisy value can produce a board that boots but has one dead peripheral. `0x0000` input registers are meaningful for output-only or non-daisy paths, so validation must distinguish intentional zeros from missing input-select data. Shared pads with JTAG, boot media, watchdog, and wake pins have board-level risk if pin groups override critical functions.

### Test Signals
Useful signals include `dtbs_check`, successful pinctrl probe without malformed property warnings, scope or loopback tests for UART/I2C/SPI/CAN/SAI/USDHC/ENET/FLEXSPI pins, suspend/resume pin retention tests, and comparing generated tuples against the NXP reference manual. Source reading signal: 865 lines; 726 `#define` entries; five-cell tuple format; no includes or functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx95-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx95-power.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx95-power.h

### Purpose
This header defines devicetree binding IDs for i.MX95 power domains and performance domains. It lets DTS files refer to platform domains symbolically instead of hard-coding firmware or GPC numeric IDs.

### Important APIs, Types, And Functions
There are no C functions or types. The public macros are `IMX95_PD_*` for 23 power domains and `IMX95_PERF_*` for 13 performance domains. The domains cover analog, always-on, BBSM, camera, CCM/SRC/GPC, six A55 cores plus A55 package, DDR, display, GPU, HSIO top and wake-always-on, M7, NETC, NoC, NPU, VPU, and wakeup.

### Control Flow
The header has no control flow. DTS compilation turns macro names into cells, and runtime power management providers later interpret those cells when attaching devices to genpd or performance-domain abstractions.

### State, Persistence, And Dependencies
No runtime state is stored here. The numeric IDs persist in compiled DTBs and must remain aligned with NXP firmware and kernel provider tables. The file depends on include guards only, but semantically depends on i.MX95 power-management firmware/domain layout.

### Integration Points
Integration points include i.MX95 DTSI nodes, NXP GPC or SCMI power/performance providers, Linux generic PM domains, OPP/performance-domain consumers, and drivers for display, GPU, VPU, NPU, camera, NETC, HSIO, DDR, and Cortex-A55 clusters.

### Risks
The main risk is stable-ID breakage. i.MX95 has more A55 core domains than i.MX94/i.MX952, so copy/paste between SoC variants can attach devices or CPUs to the wrong domain. GPU/VPU/NPU/camera/display domains also tend to expose failures only when a workload first accesses the accelerator.

### Test Signals
Useful signals include `dtbs_check`, boot logs from the i.MX95 power-domain provider, CPU idle and hotplug tests for A55 domains, runtime PM tests for accelerators and display, and firmware table comparison. Source reading signal: 47 lines; 37 `#define` entries; no includes or functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx95-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx952-clock.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx952-clock.h

### Purpose
This header defines clock IDs for the NXP i.MX952 devicetree binding. It is a symbolic ABI for clock consumers in DTS files and for the i.MX952 clock provider that decodes clock specifier cells.

### Important APIs, Types, And Functions
There are no functions or types. The exported `IMX952_CLK_*` macro API is organized into clock source IDs, clock root IDs, GPR selector IDs, and CGC gate IDs. It includes PLLs, external clocks, A55/DRAM/display/GPU/HSIO/M7/NETC/NoC/NPU/VPU roots, wakeup and peripheral roots, audio mix roots, general-purpose timers, and clock gates for accelerators and mix-local resources.

### Control Flow
No executable flow exists in this file. DTS macros expand into integers, then runtime clock lookup and enable/rate operations are handled by the common clock framework and the i.MX952 provider.

### State, Persistence, And Dependencies
The header has no local state. Its IDs persist in DTBs. It depends on the i.MX952 clock-controller register/firmware numbering and on matching provider code that treats sources, roots, GPR selectors, and CGCs as one shared ID namespace.

### Integration Points
Integration points include i.MX952 DTSI clock-controller definitions, peripheral `clocks` properties, common clock framework consumers, assigned-clock setup, and SoC subsystems such as camera, display, GPU, NPU, VPU, HSIO, NETC, audio, and wakeup peripherals.

### Risks
The flat numeric namespace is easy to damage through insertion or renumbering. Reserved placeholders intentionally preserve numbering and should not be removed. i.MX952 diverges from i.MX95 by adding or renaming several roots and CGCs, so sharing DTS snippets across SoCs can reference unavailable clocks.

### Test Signals
Useful signals include `dtbs_check`, boot-time clock registration logs, `clk_summary` inspection, assigned-clock application, and functional testing of USB/PCIe, NETC, audio, display, camera, GPU/NPU/VPU, and storage. Source reading signal: 215 lines; 199 `#define` entries; no includes or functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx952-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx952-pinfunc.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx952-pinfunc.h

### Purpose
This is the i.MX952 pin-function binding catalog. It gives board DTS files symbolic names for pad mux alternatives and expands each one to the five-cell Freescale/NXP IOMUXC tuple `<mux_reg conf_reg input_reg mux_mode input_val>`.

### Important APIs, Types, And Functions
There are no functions or types. The API consists of 728 `IMX952_PAD_*__*` macros. Compared with i.MX95, the names emphasize mix prefixes such as `WAKEUPMIX_TOP`, `AONMIX_TOP`, `NETCMIX_TOP`, `HSIOMIX_TOP`, `CCMSRCGPCMIX_TOP`, and `VPUMIX_TOP`. The catalog covers GPIO, DAP/JTAG, CAN, FLEXIO, LPI2C/I3C, LPSPI, LPUART, SAI/PDM/TDM, USB/HSIO, USDHC, XSPI/FLEXSPI, NETC timer, watchdog, and debug/observe functions.

### Control Flow
There is no executable control flow. DTS pin groups expand the macros to register cells; pinctrl applies the selected state by programming mux, config, and input-select registers.

### State, Persistence, And Dependencies
The header stores no runtime state. The register offsets and mux/daisy values persist in compiled DTBs. It depends on the i.MX952 IOMUXC layout and on consumers using the Freescale pinctrl binding with exactly five cells per selected pin.

### Integration Points
Integration points are i.MX952 SoC/board DTSI files, the `pinctrl-imx` driver family, peripheral pinctrl states, wakeup and always-on mix configuration, and subsystem nodes for NETC, HSIO, audio, display, storage, serial buses, and GPIO.

### Risks
Tuple mistakes are silent until hardware use. The i.MX952 offsets differ from i.MX95, so reusing i.MX95 pin macros or DTS fragments is unsafe even when pad names look similar. Wakeup and AON pads can affect suspend/resume behavior; HSIO USB over-current/power pins and boot-media pins need board-level electrical validation.

### Test Signals
Useful signals include `dtbs_check`, pinctrl probe logs, hardware loopback or bus enumeration for UART/I2C/SPI/CAN/USDHC/USB/NETC/audio, suspend/resume wake testing, and reference-manual comparison of mux and input-select cells. Source reading signal: 867 lines; 728 `#define` entries; no includes or functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx952-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx952-power.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx952-power.h

### Purpose
This header defines i.MX952 power-domain and performance-domain binding IDs for devicetree users. It is the symbolic mapping from DTS `power-domains` and performance-domain references to the provider's numeric domain table.

### Important APIs, Types, And Functions
There are no C functions or types. The exported macros are `IMX952_PD_*` for 21 power domains and `IMX952_PERF_*` for 12 performance domains. Domains cover analog, always-on, BBSM, camera, CCM/SRC/GPC, four A55 core domains plus A55 package, DDR, display, GPU, HSIO, M7, NETC, NoC, NPU, VPU, and wakeup.

### Control Flow
The header has no control flow. Its only behavior is preprocessor expansion into DTS cells, later decoded by Linux power/performance-domain providers during device attachment and runtime PM.

### State, Persistence, And Dependencies
The file persists no runtime state; compiled DTBs persist the numeric IDs. The values depend on the i.MX952 domain order exposed by firmware and the matching Linux provider tables.

### Integration Points
Integration points include i.MX952 DTSI files, generic PM domains, SCMI or NXP GPC providers, OPP/performance-domain bindings, and drivers for CPU clusters, DDR, camera, display, GPU, NPU, VPU, NETC, and HSIO devices.

### Risks
The key risk is cross-SoC confusion: i.MX952 has fewer A55 core domains than i.MX95 and lacks some i.MX95-specific performance IDs. Renumbering or transplanting macros between variants can power down the wrong block or fail to attach devices to PM domains.

### Test Signals
Useful signals include `dtbs_check`, provider probe logs, runtime PM cycling of each major domain, CPU idle/hotplug tests, suspend/resume, and comparison with firmware domain enumeration. Source reading signal: 44 lines; 34 `#define` entries; no includes or functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx952-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/hisilicon/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/hisilicon/Makefile

### Purpose
This Kbuild fragment declares which HiSilicon ARM64 DTBs are built when `CONFIG_ARCH_HISI` is enabled. It is a device-tree build manifest rather than executable source.

### Important APIs, Types, And Functions
There are no functions or types. The important interface is seven `dtb-$(CONFIG_ARCH_HISI) += ...` entries: HiKey 960, HiKey 970, Poplar, HiKey, and Hip05/Hip06/Hip07 server boards. These lines are consumed by the kernel DTB build system.

### Control Flow
Kbuild evaluates the conditional `dtb-y` additions based on the active configuration. If `CONFIG_ARCH_HISI=y`, the listed `.dts` files are compiled into `.dtb` artifacts as part of `make dtbs` or architecture builds.

### State, Persistence, And Dependencies
The file has no runtime state. Its persistent output is the set of DTB artifacts included in build trees, packages, or install targets. It depends on the referenced DTS files existing and on Kbuild's `dtb-*` convention.

### Integration Points
Integration points include `arch/arm64/boot/dts/Makefile`, distro/kernel packaging, CI `dtbs` targets, bootloader DTB selection, and board DTS files under the same HiSilicon directory.

### Risks
Missing an entry prevents a valid board DTB from being built in standard workflows. Stale entries break `make dtbs`. Incorrect Kconfig guards can build DTBs under the wrong SoC family or omit them from distribution packages.

### Test Signals
Useful signals include `make ARCH=arm64 dtbs` with `CONFIG_ARCH_HISI`, build logs showing all seven DTBs, and boot smoke tests on representative HiKey/Poplar/Hip boards. Source reading signal: 8 lines; 7 DTB references; no functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/hisilicon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/intel/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/intel/Makefile

### Purpose
This Kbuild fragment declares Intel ARM64 DTBs for SoCFPGA and Keem Bay platforms. It controls which board device trees are compiled for matching architecture config options.

### Important APIs, Types, And Functions
There are no functions or types. The exported build interface is `dtb-$(CONFIG_ARCH_INTEL_SOCFPGA)` with a multiline list of Agilex, Agilex3, Agilex5, and N5X board DTBs, plus `dtb-$(CONFIG_ARCH_KEEMBAY)` for `keembay-evm.dtb`.

### Control Flow
Kbuild conditionally appends DTB targets when the relevant `CONFIG_ARCH_*` symbols are enabled. The backslash-continued SoCFPGA list is parsed as one assignment containing multiple output targets.

### State, Persistence, And Dependencies
There is no runtime state. The persistent outputs are compiled DTBs. Dependencies are Kbuild syntax, the referenced DTS files, and the configuration symbols for Intel SoCFPGA and Keem Bay.

### Integration Points
Integration points include parent ARM64 DTB makefiles, Intel platform DTS sources, CI and package `dtbs` targets, U-Boot/firmware DTB loading, and board support documentation.

### Risks
Continuation-line mistakes can drop or merge DTB names. Missing entries reduce build coverage for a board. Incorrect config guards can cause DTB artifacts to disappear from expected build products.

### Test Signals
Useful signals include `make ARCH=arm64 dtbs` with Intel SoCFPGA and Keem Bay configs, checking that 11 DTB targets are produced, and booting or schema-validating the Agilex/N5X/Keem Bay DTBs. Source reading signal: 12 lines; 11 DTB references; no functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/intel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/lg/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/lg/Makefile

### Purpose
This Kbuild fragment lists LG1K ARM64 board DTBs. It exists so standard ARM64 DTB builds include LG reference platform device trees when `CONFIG_ARCH_LG1K` is enabled.

### Important APIs, Types, And Functions
There are no functions or types. The build-facing API is two `dtb-$(CONFIG_ARCH_LG1K)` entries: `lg1312-ref.dtb` and `lg1313-ref.dtb`.

### Control Flow
Kbuild evaluates the two conditional additions during `make dtbs`. With `CONFIG_ARCH_LG1K` enabled, both referenced DTS files are compiled.

### State, Persistence, And Dependencies
The file has no runtime state. Its persistent effect is build output selection. It depends on Kbuild conventions, the `CONFIG_ARCH_LG1K` symbol, and the two referenced DTS files.

### Integration Points
Integration points include the parent ARM64 DTS Makefile, LG platform DTS files, CI build matrices, and any bootloader or image packaging workflow expecting LG reference DTBs.

### Risks
Because the file is tiny, the main risks are omission or stale target names. A missing line can silently remove board DTB coverage from generic ARM64 builds.

### Test Signals
Useful signals include `make ARCH=arm64 dtbs` with `CONFIG_ARCH_LG1K`, verifying both DTBs exist, and `dtbs_check` on the generated outputs. Source reading signal: 3 lines; 2 DTB references; no functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/lg/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/marvell/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/marvell/Makefile

### Purpose
This Kbuild fragment enumerates Marvell/Mvebu ARM64 DTBs and descends into the `mmp` child directory. It is the build manifest for Armada 37xx, 7k/8k/80x0, CN913x, AC5/AC5X, Clearfog, EspressoBin, Turris MOX, and related boards.

### Important APIs, Types, And Functions
There are no functions or types. The important build interface is a set of `dtb-$(CONFIG_ARCH_MVEBU)` assignments containing 34 DTB targets, plus `subdir-y += mmp` to include Marvell MMP DTB targets from the child directory.

### Control Flow
Kbuild conditionally includes the listed DTBs when `CONFIG_ARCH_MVEBU` is active and always descends into `mmp` via `subdir-y`. Each `.dtb` target resolves to a same-directory DTS source or generated DTB dependency graph.

### State, Persistence, And Dependencies
There is no runtime state. Build artifacts persist as DTBs. Dependencies include the referenced DTS files, parent ARM64 Kbuild traversal, and the `CONFIG_ARCH_MVEBU` symbol.

### Integration Points
Integration points include parent ARM64 DTS builds, Marvell platform DTS/DTSI files, board image packaging, firmware/bootloader DTB selection, and CI coverage for network/storage-oriented Marvell boards.

### Risks
The broad board list is susceptible to stale filenames, missed board additions, and accidental removal from distro DTB packages. The `subdir-y` entry is also important: removing it would suppress child MMP DTBs even if their own Makefile is correct.

### Test Signals
Useful signals include `make ARCH=arm64 dtbs` with `CONFIG_ARCH_MVEBU`, verifying all 34 listed DTBs plus child MMP outputs, `dtbs_check`, and boot tests for representative Armada 3720, 8040, CN913x, and AC5 boards. Source reading signal: 38 lines; 34 DTB references; one child subdir.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/marvell/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/marvell/mmp/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/marvell/mmp/Makefile

### Purpose
This child Kbuild fragment declares the ARM64 Marvell MMP DTB target for the PXA1908 Samsung Core Prime LTE VE platform.

### Important APIs, Types, And Functions
There are no functions or types. The exported build interface is one `dtb-$(CONFIG_ARCH_MMP)` target: `pxa1908-samsung-coreprimevelte.dtb`.

### Control Flow
When the parent Marvell Makefile descends into this directory and `CONFIG_ARCH_MMP` is enabled, Kbuild compiles the referenced DTS into a DTB.

### State, Persistence, And Dependencies
No runtime state exists. The persistent result is the compiled DTB artifact. Dependencies are parent `subdir-y` traversal, the `CONFIG_ARCH_MMP` symbol, and the referenced DTS file.

### Integration Points
Integration points include the parent Marvell DTS Makefile, ARM64 `dtbs` builds, mobile-device image packaging, and bootloader DTB selection for PXA1908 hardware.

### Risks
The main risk is loss of build coverage if either this target or the parent `subdir-y += mmp` entry is removed. A stale filename will fail `make dtbs`.

### Test Signals
Useful signals include `make ARCH=arm64 dtbs` with `CONFIG_ARCH_MMP`, existence of `pxa1908-samsung-coreprimevelte.dtb`, `dtbs_check`, and target boot smoke testing. Source reading signal: 2 lines; 1 DTB reference; no functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/marvell/mmp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/Makefile

### Purpose
This Kbuild fragment is the ARM64 MediaTek DTB and DTBO build manifest. It lists evaluation boards, phones, Chromebooks, routers, Genio platforms, Banana Pi/Radxa boards, and overlay-based composite DTB targets under `CONFIG_ARCH_MEDIATEK`.

### Important APIs, Types, And Functions
There are no C functions or types. The interface is the set of `dtb-$(CONFIG_ARCH_MEDIATEK)` entries, intermediate `*-dtbs :=` composite target definitions, and `DTC_FLAGS_* := -@` overlay-symbol flags. The file references 161 DTB/DTBO names and defines composite DTBs for Banana Pi BPI-R3/BPI-R4 and Radxa panel combinations.

### Control Flow
Kbuild appends direct DTB and DTBO targets when `CONFIG_ARCH_MEDIATEK` is enabled. Composite `*-dtbs` variables describe base-DTB plus overlay inputs; the corresponding `.dtb` targets trigger overlay composition. `DTC_FLAGS_* := -@` enables symbol generation required for overlays.

### State, Persistence, And Dependencies
The file has no runtime state. Persistent outputs are built DTBs/DTBOs and composed DTBs. Dependencies include the referenced DTS/DTSO files, Kbuild overlay support, `dtc` symbol generation, and `CONFIG_ARCH_MEDIATEK`.

### Integration Points
Integration points include the parent ARM64 DTS Makefile, MediaTek platform DTS files, overlay-aware boot flows, OpenWrt/router board packaging, ChromeOS-style board DTBs, and CI coverage through `dtbs` and `dtbs_check`.

### Risks
The main risks are overlay composition breakage, missing `-@` flags for bases that must accept overlays, stale DTB names, and accidental omission of a board from standard build artifacts. Because the file spans many SoC generations, edits can unintentionally affect unrelated products.

### Test Signals
Useful signals include `make ARCH=arm64 dtbs`, `dtbs_check`, verifying `.dtbo` and composed `.dtb` artifacts for BPI-R3/BPI-R4/Radxa combinations, and boot tests on representative MT2712, MT798x, MT818x, MT819x, MT83xx, and MT85xx hardware. Source reading signal: 182 lines; 130 `dtb-$(...)` entries; 161 DTB/DTBO references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/mt2712-pinfunc.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/mt2712-pinfunc.h

### Purpose
This header is the MediaTek MT2712 pin-function binding catalog. It maps each physical pin and alternate function to the packed value format consumed by MediaTek pinctrl bindings.

### Important APIs, Types, And Functions
There are no functions or local types. The exported API is 902 `MT2712_PIN_*__FUNC_*` macros. Each macro uses `MTK_PIN_NO(n) | function_index`, so the pin number and mux function are encoded in one integer. The file includes `<dt-bindings/pinctrl/mt65xx.h>` for `MTK_PIN_NO`. It covers 210 pins, including EINT, PWM, USB ID/VBUS, keypad, camera clocks, NAND/MSDC/NOR, Ethernet, UART, I2C, SPI, JTAG/debug monitor, PCIe sideband, I2S/TDM/PCM audio, display, and GPIO functions.

### Control Flow
The header has no executable control flow. DTS pinctrl nodes reference these macros; the C preprocessor emits packed pin/function integers; the MediaTek pinctrl driver decodes them and programs mux registers when applying pin states.

### State, Persistence, And Dependencies
The file stores no state. Its packed values persist inside compiled DTBs. Dependencies are the MT65xx pinctrl binding format, the MT2712 pin numbering scheme, the mux function indexes for each pin, and the MediaTek pinctrl driver that interprets `MTK_PIN_NO`.

### Integration Points
Integration points include MT2712 SoC and board DTS files, the MediaTek pinctrl driver, GPIO/EINT infrastructure, and peripheral drivers for MMC, Ethernet, USB, display, camera, serial buses, and audio. Board pinctrl states depend on these names to select the correct mux.

### Risks
The packed format makes both parts of the value important: a wrong pin number or function index can silently mux the wrong signal. Function indexes are sparse on some pins, so assuming all alternate functions are contiguous is unsafe. Debug monitor and boot/storage pins can interfere with bring-up or board recovery if selected accidentally.

### Test Signals
Useful signals include `dtbs_check`, MediaTek pinctrl probe logs, GPIO/EINT interrupt tests, bus-level validation for MMC/NAND/NOR/Ethernet/USB/UART/I2C/SPI/audio/display/camera, and comparison with the MT2712 datasheet mux table. Source reading signal: 1123 lines; 902 `#define` entries; one include; no functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/mt2712-pinfunc.h -->
