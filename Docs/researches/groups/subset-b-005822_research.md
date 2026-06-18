# subset-b-005822 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3399-cru.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3399-cru.h

## Purpose
`rk3399-cru.h` is the device-tree ABI header for the Rockchip RK3399 clock and reset unit. It gives DTS files and the RK3399 CRU/PMUCRU clock driver stable integer IDs for PLLs, ARM core clocks, special clocks, ACLK/PCLK/HCLK bus gates, display/media clocks, and soft-reset lines.

## Important APIs, types, and functions
There are no C functions or types; the exported API is the macro namespace. Important families are `PLL_*` for PLL IDs, `ARMCLKL`/`ARMCLKB` for little/big CPU clusters, `SCLK_*` for special/peripheral source clocks, `ACLK_*`, `PCLK_*`, and `HCLK_*` for bus-domain gates, `DCLK_*` for display clocks, and `SRST_*` for reset specifiers. The reset block is grouped by `cru_softrst_con0` through later CRU reset registers plus PMU reset IDs.

## Control flow
The header has compile-time inclusion flow only: the guard `_DT_BINDINGS_CLK_ROCKCHIP_RK3399_H` prevents duplicate definitions, and consumers include the macros into device trees or drivers. At runtime, a clock phandle cell using one of these IDs is resolved by the RK3399 CRU provider, which maps the ID to clock/reset operations in the driver tables.

## State and persistence
No state is stored in the header. The numeric IDs are persistent ABI values: changing or reusing them would break existing device trees and any compiled DTBs that reference RK3399 clock or reset specifiers.

## Dependencies and integration points
It integrates with RK3399 DTS nodes, `drivers/clk/rockchip` clock tables, reset-controller users, power-domain descriptions, and peripheral drivers requesting clocks by phandle. The PMU clock indices are part of the same ABI for always-on/low-power domains.

## Risks and test signals
Main risks are renumbering stable IDs, assigning a peripheral to the wrong bus family, missing reset lines when adding device-tree nodes, and confusing CRU and PMU reset spaces. Test signals include `dtbs_check`, successful boot-time CRU registration, no unresolved clock/reset phandles, and peripheral probes for UART, I2C, MMC, USB, VOP, VPU, GPU, and PCIe blocks that consume these IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3399-cru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3399-ddr.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3399-ddr.h

## Purpose
`rk3399-ddr.h` defines RK3399 DDR3 speed-bin constants for device-tree or firmware-facing memory timing descriptions. The comments tie each constant to JEDEC-style DDR3 data rates and CAS timing groups.

## Important APIs, types, and functions
The ABI consists of `DDR3_800D` through `DDR3_2133N` plus `DDR3_DEFAULT`. There are no functions or structs. The IDs are compact enum-like values from `0` through `21` and represent timing bins such as DDR3-800, DDR3-1066, DDR3-1333, DDR3-1600, DDR3-1866, and DDR3-2133 with different latency suffixes.

## Control flow
Consumers include the header and place one of the constants in data consumed by RK3399 DDR initialization logic. Runtime selection happens in the memory controller or firmware code that interprets the selected bin and chooses matching timing parameters.

## State and persistence
The header is stateless, but the constants are ABI: a device tree compiled with `DDR3_1600K` must continue to mean the same bin. The selected bin affects hardware memory-controller state programmed during initialization and may persist until reset.

## Dependencies and integration points
It integrates with RK3399 board device trees, DDR timing data, boot firmware, and kernel-side Rockchip DDR support that reads memory timing properties. It is separate from the CRU clock IDs but influences memory clock/timing compatibility.

## Risks and test signals
Risks include mapping a board to the wrong speed bin, assuming `DDR3_DEFAULT` is universally safe, or changing numeric IDs. Test signals are stable memory training, no early boot memory faults, stress tests under high memory bandwidth, and board DTS review against the actual DDR3 part datasheet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3399-ddr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3568-cru.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3568-cru.h

## Purpose
`rk3568-cru.h` is the clock/reset binding ABI for RK3568 and closely related RK356x Rockchip SoCs. It describes PMUCRU clocks, main CRU clocks, SCMI-managed clocks, and a large reset namespace.

## Important APIs, types, and functions
The file exports macro IDs only. It separates PMUCRU PLLs and clocks (`PLL_PPLL`, `PLL_HPLL`, RTC, PMU, GPIO0, UART0, I2C0, PWM0) from main CRU PLLs and peripheral clocks (`PLL_APLL`, `PLL_GPLL`, `PLL_CPLL`, `PLL_NPLL`, `PLL_VPLL`, `PLL_HPLL`, `PLL_USB480M`). Families include `CLK_*`, `SCLK_*`, `ACLK_*`, `HCLK_*`, `PCLK_*`, `MCLK_*`, `DCLK_*`, and `DBCLK_*`. `SCMI_*` IDs expose firmware-mediated clock handles, and `SRST_*` IDs cover PMU and main CRU soft resets through high-numbered PHY and delay-line resets.

## Control flow
The header participates only in preprocessing. Runtime control flows from a DT clock or reset specifier to the RK3568 clock/reset provider; if the ID belongs to SCMI, firmware may be the effective clock manager. Reset consumers use the `SRST_*` values through reset-controller phandles.

## State and persistence
No mutable state exists here. The macro numbers are persistent DT ABI and must remain stable. Actual clock enable, mux, divider, and reset state is held in CRU/PMUCRU hardware registers or firmware-controlled SCMI state.

## Dependencies and integration points
The header is consumed by RK3568 DTS files, `drivers/clk/rockchip` RK3568 tables, SCMI clock users, reset-controller users, and peripheral drivers for GPU, NPU, VOP, VPU, RGA, crypto, USB, PCIe/SATA/pipe PHY, GMAC, MMC, I2S/PDM, CAN, UART, SPI, and I2C.

## Risks and test signals
Risks include confusing PMUCRU and main CRU ID spaces, adding DTS nodes with raw numbers instead of macros, unstable SCMI IDs, and missing resets for PHY-heavy blocks. Test signals include `dtbs_check`, complete clock summary registration, SCMI clock availability, reset deassertion during driver probe, and peripheral smoke tests across storage, display, network, USB, and audio.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3568-cru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rk3506-cru.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rk3506-cru.h

## Purpose
`rockchip,rk3506-cru.h` defines the RK3506 clock binding IDs for the CRU. It is a modern Rockchip binding header focused on clock IDs rather than reset IDs.

## Important APIs, types, and functions
The exported API is numeric macros from PLL IDs through peripheral clocks. Major identifiers include `PLL_GPLL`, `PLL_V0PLL`, `PLL_V1PLL`, `ARMCLK`, `CLK_DDR`, root/gated PLL outputs, `ACLK_*`, `HCLK_*`, `PCLK_*`, `SCLK_*`, `MCLK_*`, `LRCK_*`, `TCLK_*`, and `DBCLK_*`. The highest entries include 32 kHz/PMU/ref PHY/Wi-Fi and PLL reference helper clocks such as `CLK_WIFI_OUT`, `CLK_V0PLL_REF`, `CLK_V1PLL_REF`, and `CLK_32K_FRAC_MUX`.

## Control flow
Preprocessor inclusion is the only flow in the header. At runtime, device-tree clock cells referencing these constants are looked up by the RK3506 CRU driver, which performs the actual gate, mux, divider, and rate operations.

## State and persistence
The header has no runtime state. Its integer assignments are persistent ABI for RK3506 device trees and drivers. Hardware clock state lives in CRU registers and can persist across low-power transitions depending on the SoC domain.

## Dependencies and integration points
It integrates with RK3506 board DTS files, Rockchip CRU driver tables, and peripheral drivers for DDR, buses, DMA, crypto, audio, PWM, GPIO, UART, SPI, I2C, timers, touch key, PHY reference outputs, and Wi-Fi clock output.

## Risks and test signals
Risks are duplicate values, typoed identifiers in DTS, missing reset coverage if consumers expect reset macros here, and clock-output IDs that must match IO/PMU routing. Test signals include clean DT compilation, no unknown clock IDs in probe logs, correct rate reporting in `/sys/kernel/debug/clk/clk_summary`, and functional board bring-up for serial console, storage, network or wireless, and audio.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rk3506-cru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rk3528-cru.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rk3528-cru.h

## Purpose
`rockchip,rk3528-cru.h` provides the stable clock ID namespace for the RK3528 CRU, including normal CRU clocks and SCMI-visible secure/firmware clocks.

## Important APIs, types, and functions
The macro API starts with PLL and CPU/root clocks (`PLL_APLL`, `PLL_CPLL`, `PLL_GPLL`, `PLL_PPLL`, `PLL_DPLL`, `ARMCLK`) and continues through `CLK_*`, `ACLK_*`, `HCLK_*`, `PCLK_*`, `SCLK_*`, `MCLK_*`, `DCLK_*`, `CCLK_*`, `TCLK_*`, and `DBCLK_*`. The file also defines `SCMI_*` IDs for CPU, GPU, crypto, key ladder, TRNG, and related secure clock consumers.

## Control flow
No executable flow exists. DTS files use these names in clock specifiers; the RK3528 CRU driver or SCMI firmware backend interprets the numeric ID and applies the requested enable/rate/parent operation.

## State and persistence
The ABI state is the fixed integer mapping. Runtime state is maintained by CRU registers or by firmware for SCMI clocks. The header itself stores nothing and should not be reordered.

## Dependencies and integration points
Integration points include Rockchip RK3528 DTS, the CRU driver, SCMI clock bindings, reset/power-domain coordinated peripheral probes, and drivers for crypto, display, video, GMAC, USB, SDMMC/SDIO, eMMC, audio, UART, I2C, SPI, PWM, timers, and GPIO.

## Risks and test signals
Risks include misuse of SCMI IDs as direct CRU IDs, numeric ABI changes, and incorrect sample/drive clock IDs for MMC/SDIO interfaces. Test signals are clean schema checks, clock provider registration without gaps that drivers need, MMC tuning success, crypto secure clock access through SCMI, and working display/network/storage peripherals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rk3528-cru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rk3562-cru.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rk3562-cru.h

## Purpose
`rockchip,rk3562-cru.h` defines RK3562 clock IDs for device-tree consumers of the CRU. It covers PLLs, CPU/GPU/NPU/DDR roots, bus gates, media/display clocks, and secure crypto clocks.

## Important APIs, types, and functions
The header exports `PLL_DMPLL0`, `PLL_APLL`, `PLL_GPLL`, `PLL_VPLL`, `PLL_HPLL`, `PLL_CPLL`, `PLL_DPLL`, `PLL_DMPLL1`, followed by `ARMCLK`, `CLK_GPU`, `ACLK_RKNN`, `CLK_DDR`, and peripheral families `CLK_*`, `ACLK_*`, `HCLK_*`, `PCLK_*`, `SCLK_*`, `DCLK_*`, `MCLK_*`, `CCLK_*`, `FCLK_*`, and `TMCLK_*`. The tail includes display and secure crypto IDs such as `DCLK_VOP`, `DCLK_VOP1`, `ACLK_CRYPTO_S`, and `CLK_PKA_CRYPTO_S`.

## Control flow
The only control path is inclusion into DTS or C driver code. Runtime requests travel from DT clock specifiers to the RK3562 CRU provider, which maps IDs to hardware gates, muxes, and dividers.

## State and persistence
The file is stateless. Numeric assignments are persistent ABI; CRU hardware contains the real state. Secure clock IDs may be subject to firmware or trust-zone policy outside the header.

## Dependencies and integration points
It integrates with RK3562 board descriptions, Rockchip CRU clock tables, power domains, and drivers for RKNN, GPU, DDR, crypto, VOP, CSI/DSI PHYs, audio, UART/I2C/SPI/CAN, SD/eMMC, USB, GMAC, and timers.

## Risks and test signals
Risks include mixing RK3562 IDs with RK3568 IDs, misdescribing secure crypto clocks, and assigning display or PHY clocks to the wrong consumer. Test signals include `dtbs_check`, clk-summary inspection, boot with console and storage, GPU/RKNN/display probe logs, CSI/DSI PHY initialization, and crypto self-tests when secure clocks are available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rk3562-cru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rk3576-cru.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rk3576-cru.h

## Purpose
`rockchip,rk3576-cru.h` is the RK3576 clock binding header. It exposes a broad CRU clock ID space, secure clock IDs, SCMI aliases, and IO-controlled output clocks for a recent Rockchip SoC.

## Important APIs, types, and functions
The macro namespace begins with PLLs (`PLL_BPLL`, `PLL_LPLL`, `PLL_VPLL`, `PLL_AUPLL`, `PLL_CPLL`, `PLL_GPLL`, `PLL_PPLL`) and CPU clocks (`ARMCLK_L`, `ARMCLK_B`). It defines many `CLK_*`, `ACLK_*`, `HCLK_*`, `PCLK_*`, `MCLK_*`, `SCLK_*`, `DCLK_*`, `TCLK_*`, `DBCLK_*`, and `FCLK_*` IDs. Later sections include secure clock IDs, `SCMI_ARMCLK_L`, `SCMI_ARMCLK_B`, `SCMI_CLK_GPU`, and IO output clocks such as `CLK_SAI*_MCLKOUT_TO_IO` and `CLK_FSPI*_TO_IO`.

## Control flow
The header has no runtime logic. Device-tree users reference IDs; the RK3576 CRU provider, SCMI firmware, or IO mux/output-clock path carries out the requested operation.

## State and persistence
No state is stored in the file. The duplicate `CLK_SAI4_MCLKOUT_TO_IO` definition documents the same value twice and should be treated carefully because external users may already rely on that spelling/value. Hardware and firmware hold clock state.

## Dependencies and integration points
It integrates with RK3576 DTS, the Rockchip clock driver, SCMI firmware, secure-world clock management, audio SAI output pins, FSPI clock output routing, and drivers for CPU/GPU, display, video, ISP, storage, network, USB/PCIe PHYs, crypto, watchdog/timers, and serial buses.

## Risks and test signals
Risks include SCMI/direct ID confusion, accidental renumbering in a dense ABI, duplicated definitions hiding merge mistakes, and output clocks requiring coordinated pinctrl/IO-domain setup. Test signals include schema validation, clk-summary coverage, SCMI get-rate/set-rate for CPU/GPU clocks, audio MCLK output validation, FSPI operation, and peripheral probe success across secure and non-secure domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rk3576-cru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rk3588-cru.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rk3588-cru.h

## Purpose
`rockchip,rk3588-cru.h` defines the clock binding ABI for RK3588/RK3588S-class CRU consumers. It is one of the larger Rockchip clock headers, reflecting multiple CPU clusters, display/video islands, storage/network PHYs, and secure/SCMI clocks.

## Important APIs, types, and functions
The file exports PLL IDs (`PLL_B0PLL`, `PLL_B1PLL`, `PLL_LPLL`, `PLL_V0PLL`, `PLL_AUPLL`, `PLL_CPLL`, `PLL_GPLL`, `PLL_NPLL`, `PLL_PPLL`), CPU cluster clocks (`ARMCLK_L`, `ARMCLK_B01`, `ARMCLK_B23`), and hundreds of `CLK_*`, `ACLK_*`, `HCLK_*`, `PCLK_*`, `MCLK_*`, `SCLK_*`, `DCLK_*`, `TCLK_*`, and `DBCLK_*` constants. `SCMI_*` IDs cover secure/non-secure HCLK/PCLK, key ladder, crypto, SPLL, and SD host clocks.

## Control flow
Compile-time inclusion is the only header behavior. Runtime clock operations flow through the RK3588 CRU driver or SCMI firmware depending on the ID and DT provider. Reset and power-domain sequencing in consumers relies on these clock IDs being paired with matching domain descriptions elsewhere.

## State and persistence
The header has no state, but it is ABI. Real state is in CRU registers, firmware-managed secure clocks, and possibly retention domains across suspend.

## Dependencies and integration points
It is used by RK3588 DTS files, clock drivers, SCMI providers/clients, and drivers for CPU clusters, GPU/NPU, VOP and HDMI/DP, AV1/VPU/RKVDEC/RKVENC, ISP, PCIe/SATA/USB/pipe PHY, GMAC, SD/eMMC/SDIO, I2S/PDM/SPDIF, CAN, UART, SPI, I2C, PWM, watchdogs, and secure crypto/key ladder blocks.

## Risks and test signals
Risks include wrong ID selection between similar media islands, SCMI security policy mismatches, and breaking precompiled DTBs by renumbering. Test signals include `dtbs_check`, successful CRU and SCMI clock registration, no `-ENOENT` clock probe failures, display/video pipeline bring-up, PCIe/USB/storage/network operation, and suspend/resume clock retention checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rk3588-cru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rk808.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rk808.h

## Purpose
`rockchip,rk808.h` defines the clock-output indices for the Rockchip RK808 PMIC clock provider.

## Important APIs, types, and functions
The complete API is `RK808_CLKOUT0` and `RK808_CLKOUT1`. There are no functions or data structures.

## Control flow
Consumers include the header and reference one of the clock-output IDs in a PMIC clock phandle. The RK808 PMIC clock driver resolves the index and controls or exposes the matching hardware clock output.

## State and persistence
The header is stateless. PMIC register state determines whether each output is enabled and what downstream devices receive it.

## Dependencies and integration points
It integrates with Rockchip board DTS files, RK808 MFD/PMIC support, common clock framework registration, and peripherals that use PMIC-provided 32 kHz or reference outputs.

## Risks and test signals
Risks are limited but include swapping clockout indexes and breaking boards that route one output to Wi-Fi, Bluetooth, RTC, or codec components. Test signals include PMIC clock provider registration, correct `assigned-clocks` behavior, and downstream peripheral probe success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rk808.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rv1103b-cru.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rv1103b-cru.h

## Purpose
`rockchip,rv1103b-cru.h` defines CRU clock IDs for Rockchip RV1103B, a compact video/AI-oriented SoC. It covers PLL/root clocks, UART and peripheral clocks, media interfaces, SRAM, USB PHY reference clocks, and audio codec clocks.

## Important APIs, types, and functions
The macro API starts with `PLL_GPLL`, `ARMCLK`, `PLL_DPLL`, and root divider clocks such as `XIN_OSC0_HALF` and `CLK_GPLL_DIV*`. Families include `CLK_*`, `ACLK_*`, `HCLK_*`, `PCLK_*`, `SCLK_*`, `LSCLK_*`, `MCLK_*`, `TCLK_*`, `DCLK_*`, `CCLK_*`, and `DBCLK_*`. Tail IDs include `SCLK_UART*_SRC`, `XIN_RC_SRC`, `CLK_UTMI_USBOTG`, and `CLK_REF_USBPHY`.

## Control flow
The header is included by DTS and driver code. Runtime control flows from clock phandle cells to the RV1103B CRU driver, which implements parent selection, rate division, gating, and enable sequencing.

## State and persistence
No state is maintained in the header. The numeric values are persistent ABI, while CRU registers and low-power domains carry actual clock state.

## Dependencies and integration points
It integrates with RV1103B board DTS files, Rockchip CRU support, audio codec and I2S/PDM users, video/camera blocks, USB PHY, UART/I2C/SPI/PWM/timer/GPIO drivers, SRAM/DMA paths, and PMU/RC oscillator users.

## Risks and test signals
Risks include selecting source clocks instead of effective leaf clocks, RC/USB reference misconfiguration, and wrong media-clock IDs causing camera or display probe failures. Test signals include serial console, USB PHY lock, audio codec clocking, camera pipeline bring-up, clk-summary rates, and clean DT validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rv1103b-cru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rv1126-cru.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rv1126-cru.h

## Purpose
`rockchip,rv1126-cru.h` is the clock/reset binding header for RV1126. It includes PMUCRU and main CRU clock IDs plus PMU and main soft-reset IDs.

## Important APIs, types, and functions
The file exports PMU clock macros beginning at `PLL_GPLL`, RTC/Wi-Fi/PMU clocks, and UART/I2C/GPIO/PWM PMU-domain clocks. The main CRU section defines PLLs, many `SCLK_*`, `DCLK_*`, `ACLK_*`, `HCLK_*`, `PCLK_*`, `MCLK_*`, and `DBCLK_*` IDs for CPU, DDR, ISP, CIF, video, crypto, storage, USB, GMAC, and serial peripherals. Reset macros `SRST_*` cover PMU reset registers and CRU reset registers.

## Control flow
DTS clock/reset specifiers include the IDs; the RV1126 CRU/PMUCRU clock and reset providers interpret them at runtime. Reset control flows through the reset-controller API and clock control through the common clock framework.

## State and persistence
The header has no state. Numeric mappings are persistent ABI. Hardware register state is split between PMUCRU and CRU domains and may survive some low-power transitions.

## Dependencies and integration points
It integrates with RV1126 board DTS, Rockchip clock/reset drivers, PMU-domain devices, and drivers for camera/ISP, video encode/decode, display, crypto, GMAC, USB PHY, SD/eMMC, I2S/PDM, UART/I2C/SPI/PWM, TSADC/PVTM, OTP, and watchdog/timer blocks.

## Risks and test signals
Risks include using main CRU IDs in PMUCRU contexts, reset IDs that do not match register-bit positions, and camera/video clocks that require coordinated power domains. Test signals include clock and reset provider registration, `dtbs_check`, media pipeline probe, GMAC/USB/storage smoke tests, PMU-domain GPIO/RTC behavior, and reset assertion/deassertion during driver remove/probe cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rv1126-cru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rv1126b-cru.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rv1126b-cru.h

## Purpose
`rockchip,rv1126b-cru.h` defines the RV1126B clock ID ABI. It covers PLLs, root dividers, DDR and CPU clocks, many peripheral gates, and a secure clock subsection.

## Important APIs, types, and functions
The exported macros start with `PLL_GPLL`, `PLL_CPLL`, `PLL_AUPLL`, `ARMCLK`, `SCLK_DDR`, and CPLL/GPLL divider roots. Families include `CLK_*`, `ACLK_*`, `HCLK_*`, `PCLK_*`, `SCLK_*`, `DCLK_*`, `MCLK_*`, `DBCLK_*`, `TCLK_*`, `BUSCLK_*`, and `LRCK_*`. Secure-tail IDs include `PCLK_OTPC_S`, `PCLK_KEY_READER_S`, `HCLK_KL_RKCE_S`, `PCLK_WDT_S`, `TCLK_WDT_S`, secure timers, RNG, PKA, and `ACLK_RKCE_S`.

## Control flow
Consumers use the macro IDs in device trees; runtime operations are handled by the RV1126B CRU provider. Secure clock requests may require firmware or secure-world cooperation depending on platform policy.

## State and persistence
The file itself is immutable macro data. The ABI persists across kernel versions, while hardware clock state lives in CRU registers and secure register banks.

## Dependencies and integration points
It integrates with RV1126B DTS, Rockchip CRU support, secure crypto/key ladder/OTPC/RNG devices, watchdog/timer blocks, audio clocks, camera/video/display blocks, storage, networking, USB, UART/I2C/SPI/PWM/GPIO, and DDR/CPU frequency management.

## Risks and test signals
Risks include accidental misspelling such as `PLK_STIMER` becoming part of ABI, confusing secure and non-secure clock names, and regression from numeric changes. Test signals include schema validation, secure clock probe behavior, watchdog and secure timer operation, crypto self-tests, and media/storage/network smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rv1126b-cru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rv1108-cru.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/rv1108-cru.h

## Purpose
`rv1108-cru.h` is the Rockchip RV1108 clock/reset binding header. It exposes PLLs, bus/peripheral clocks, and reset IDs for this older Rockchip SoC.

## Important APIs, types, and functions
The clock API includes `PLL_APLL`, `PLL_DPLL`, `PLL_GPLL`, `ARMCLK`, many `SCLK_*` special clocks, `ACLK_*`, `PCLK_*`, and `HCLK_*` gate IDs, plus display/media IDs. Reset macros use several prefixes: `SRST_*`, `PRST_*`, `HRST_*`, `ARST_*`, `MRST_*`, and `NRST_*`, reflecting soft, peripheral, HCLK, ACLK, media, and other reset domains.

## Control flow
The header is consumed by DTS and drivers. Runtime clock/reset operations go through the RV1108 CRU driver and reset-controller implementation.

## State and persistence
No state is stored here. The numeric ID mapping is a stable ABI; hardware registers hold clock and reset state.

## Dependencies and integration points
It integrates with RV1108 device trees, Rockchip CRU support, reset consumers, and drivers for NAND, SDMMC/SDIO/eMMC, UART, I2C, SPI, PWM, GPIO, USB OTG, CIF, VPU, display, DSP, PMU, PVTM, and audio.

## Risks and test signals
Risks include mixing the many reset prefixes, assuming gaps can be reused, and using wrong clock IDs for storage sample/drive paths. Test signals include DT validation, reset-controller coverage, boot console, storage tuning, USB and camera/video operation, and clk-summary checks for expected gates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/rv1108-cru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/s5pv210-audss.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/s5pv210-audss.h

## Purpose
`s5pv210-audss.h` defines clock IDs for the Samsung S5PV210 audio subsystem clock controller.

## Important APIs, types, and functions
The header exports `CLK_MOUT_AUDSS`, `CLK_MOUT_I2S_A`, `CLK_DOUT_AUD_BUS`, `CLK_DOUT_I2S_A`, `CLK_I2S`, `CLK_HCLK_I2S`, `CLK_HCLK_UART`, `CLK_HCLK_HWA`, `CLK_HCLK_DMA`, `CLK_HCLK_BUF`, `CLK_HCLK_RP`, and `AUDSS_MAX_CLKS`. There are no functions or structs.

## Control flow
Audio-related DTS nodes use these constants in clock phandles. The S5PV210 AUDSS clock driver maps the ID to mux, divider, or gate operations in the audio subsystem.

## State and persistence
The header is stateless. The values are ABI and must remain stable. Runtime state lives in AUDSS clock-controller registers.

## Dependencies and integration points
It integrates with S5PV210 DTS, the AUDSS clock driver, I2S/audio DMA, UART/HWA audio support, and common clock framework consumers.

## Risks and test signals
Risks include off-by-one changes relative to `AUDSS_MAX_CLKS`, confusing mux/divider/gate IDs, and breaking audio codec clock trees. Test signals are DT compilation, AUDSS provider registration, I2S playback/capture, DMA clock enablement, and correct clock rates in clk debugfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/s5pv210-audss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/s5pv210.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/s5pv210.h

## Purpose
`s5pv210.h` provides device-tree clock IDs for the Samsung S5PV210 clock controller, including core PLLs, muxes, dividers, gates, special clocks, S5P6442-specific entries, and CLKOUT controls.

## Important APIs, types, and functions
The macro API includes `FIN_PLL`, `FOUT_*` PLL outputs, `MOUT_*` muxes, `DOUT_*` dividers, `CLK_*` gates, `SCLK_*` special clocks, and `NR_CLKS`. Later entries include S5P6442-specific clocks and `FOUT_APLL_CLKOUT`, `FOUT_MPLL_CLKOUT`, `DOUT_APLL_CLKOUT`, `MOUT_CLKSEL`, `DOUT_CLKOUT`, and `MOUT_CLKOUT`.

## Control flow
The header has no executable flow. DTS clock specifiers reference these IDs; the Samsung S5PV210 clock driver maps IDs to clock framework nodes and operations.

## State and persistence
The file contains no state. Numeric IDs are stable ABI. Clock state lives in Samsung CMU registers and is modified by the common clock framework at runtime.

## Dependencies and integration points
It integrates with S5PV210/S5P6442 device trees, Samsung clock-controller drivers, CPU/bus/display/audio/storage/USB/peripheral drivers, and board-level CLKOUT routing.

## Risks and test signals
Risks include changing `NR_CLKS`, confusing S5PV210 and S5P6442-specific IDs, and using a divider or mux ID where a gate is expected. Test signals include `dtbs_check`, CMU registration, boot console, storage/display/audio peripheral probes, and clk-summary validation of parent/rate relationships.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/s5pv210.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,exynos2200-cmu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,exynos2200-cmu.h

## Purpose
`samsung,exynos2200-cmu.h` defines clock IDs for Exynos2200 CMU domains. It supports top-level and domain-specific clock controllers used by DTS and Samsung CMU drivers.

## Important APIs, types, and functions
All exported IDs use the `CLK_*` namespace. Sections cover `CMU_TOP`, `CMU_ALIVE`, `CMU_PERIS`, `CMU_CMGP`, `CMU_HSI0`, `CMU_PERIC0`, `CMU_PERIC1`, `CMU_PERIC2`, `CMU_UFS`, and `CMU_VTS`. The IDs include PLL outputs, muxes, dividers, and gate outputs such as shared PLLs, MMC PLL, CMU bus feeds, UART/I2C/SPI/USI clocks, UFS, and voice-trigger-system clocks.

## Control flow
There is no runtime code in the header. DTS nodes for each CMU domain use these IDs; the Exynos CMU driver registers the matching clocks and applies common clock framework operations.

## State and persistence
The header is stateless. Each section's numbers are ABI for its corresponding provider domain and may restart numbering within a domain. Actual state is in CMU registers and low-power always-on domains.

## Dependencies and integration points
It integrates with Exynos2200 DTS, Samsung CMU driver data, always-on/peripheral/high-speed/UFS/VTS devices, serial interfaces, storage, and power-domain sequencing.

## Risks and test signals
Risks include using an ID with the wrong CMU provider because domain-local numbering repeats, altering IDs used by shipped DTBs, and misdescribing always-on or VTS clocks. Test signals include schema checks, domain CMU probe logs, no unresolved clock phandles, UART/USI/I2C/SPI operation, UFS bring-up, and VTS/audio clock checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,exynos2200-cmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,exynos7870-cmu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,exynos7870-cmu.h

## Purpose
`samsung,exynos7870-cmu.h` defines clock IDs for Exynos7870 CMU domains. It is split by hardware clock-controller domain rather than one global namespace.

## Important APIs, types, and functions
The header exports `CLK_*` IDs plus domain count macros: `MIF_NR_CLK`, `DISPAUD_NR_CLK`, `FSYS_NR_CLK`, `G3D_NR_CLK`, `ISP_NR_CLK`, `MFCMSCL_NR_CLK`, and `PERI_NR_CLK`. Sections include MIF, DISPAUD, FSYS, G3D, ISP, MFCMSCL, and PERI clocks, covering bus dividers, CMU interconnect outputs, display/audio, USB/MMC, GPU, camera/ISP, codec/scaler, UART, SPI, I2C, PWM, ADC, TMU, and watchdog clocks.

## Control flow
The header supplies constants for DT clock specifiers. Runtime behavior is implemented by Exynos7870 CMU provider instances; each provider interprets IDs in its own domain.

## State and persistence
The header has no state. Domain count macros bound driver arrays and DT-visible IDs, so changing them or reordering IDs can break ABI and provider table indexing.

## Dependencies and integration points
It integrates with Exynos7870 device trees, Samsung CMU driver data, MIF/FSYS/DISPAUD/G3D/ISP/MFCMSCL/PERI providers, and peripheral drivers for display, audio, USB, MMC, GPU, camera, video, UART/I2C/SPI/PWM, thermal, and watchdog.

## Risks and test signals
Risks include provider-domain mixups, incorrect `*_NR_CLK` values, and clock IDs that look globally unique but are only local. Test signals include DT validation, each CMU domain registering its declared clock count, boot logs free of clock lookup failures, and smoke tests for display/audio/storage/USB/GPU/camera and PERI serial devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,exynos7870-cmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,exynos8895.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,exynos8895.h

## Purpose
`samsung,exynos8895.h` defines device-tree clock IDs for Exynos8895 CMU domains including TOP, PERIS, FSYS0, FSYS1, PERIC0, and PERIC1.

## Important APIs, types, and functions
All IDs are `CLK_*` macros. `CMU_TOP` provides shared PLLs, top-level muxes/dividers, and gated outputs to subsystem CMUs. `CMU_PERIS` covers system/peripheral infrastructure. `CMU_FSYS0` and `CMU_FSYS1` cover high-speed storage and connectivity paths. `CMU_PERIC0` and `CMU_PERIC1` cover USI, UART, I2C/SPI-style peripheral clocks and bus gates.

## Control flow
The header only defines constants. DT clock specifiers select IDs under a particular CMU provider; the Exynos8895 CMU driver registers and controls those clocks through the common clock framework.

## State and persistence
The header has no mutable state. IDs are persistent ABI and are domain-local, so the same numeric value can mean different clocks under different CMU nodes.

## Dependencies and integration points
It integrates with Exynos8895 DTS, Samsung CMU driver data, subsystem CMUs, high-speed storage/USB, PERIC serial buses, system register blocks, and power management.

## Risks and test signals
Risks include cross-domain ID misuse, renumbering shipped bindings, and omission of top-level CMU gate clocks required by child domains. Test signals include schema validation, CMU probe for all domains, functional UART/USI/I2C/SPI, storage/USB bring-up through FSYS, and clk-summary parent chains from TOP to child CMUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,exynos8895.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,exynos990.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,exynos990.h

## Purpose
`samsung,exynos990.h` defines Exynos990 clock-controller binding IDs for TOP, HSI0, PERIC0, PERIC1, and PERIS CMU domains.

## Important APIs, types, and functions
The exported `CLK_*` constants include shared and G3D/MMC PLL outputs, top-level muxes/dividers/gates, high-speed interface clocks in `CMU_HSI0`, many USI/UART/SPI/I2C-style peripheral clocks in `CMU_PERIC0` and `CMU_PERIC1`, and PERIS infrastructure clocks for GIC, MCT, OTP, TZPC, and TMU.

## Control flow
There are no functions. Consumers use the macros in device-tree clock cells; Exynos990 CMU provider drivers interpret them by domain and expose operations through the common clock framework.

## State and persistence
The file is stateless but ABI-sensitive. Hardware CMU registers store runtime state; always-on/peris clocks may interact with suspend and security policy.

## Dependencies and integration points
It integrates with Exynos990 DTS, Samsung CMU driver data, high-speed interface drivers, PERIC serial drivers, PERIS system blocks, thermal/timer/security-related devices, and power domains.

## Risks and test signals
Risks include domain-local numbering mistakes, missing parent gates from TOP to child CMUs, and breaking boot-critical PERIS clocks. Test signals include DT schema checks, all CMU nodes probing, serial console and USI peripherals working, high-speed interface bring-up, timer/thermal initialization, and clk-summary parent/rate verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,exynos990.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,exynosautov9.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,exynosautov9.h

## Purpose
`samsung,exynosautov9.h` defines clock IDs for the Exynos Auto V9 CMU hierarchy used in automotive Samsung SoCs.

## Important APIs, types, and functions
The header uses families `FOUT_*`, `MOUT_*`, `DOUT_*`, `GOUT_*`, and `CLK_*`. Sections cover `CMU_TOP`, `CMU_BUSMC`, `CMU_CORE`, `CMU_DPUM`, `CMU_FSYS0`, `CMU_FSYS1`, `CMU_FSYS2`, `CMU_PERIC0`, `CMU_PERIC1`, and `CMU_PERIS`. IDs describe shared PLLs, top-level mux/divider/gates, display processing, storage, USB/UFS/MMC-like high-speed domains, peripheral IP clocks, and watchdog clocks.

## Control flow
The header has compile-time constant flow only. Runtime clock operations are handled by domain CMU providers referenced by DTS nodes.

## State and persistence
The file is stateless. Numeric IDs are binding ABI and section-local where a CMU provider owns a subsection. Runtime state is in CMU registers and automotive power/retention domains.

## Dependencies and integration points
It integrates with Exynos Auto V9 device trees, Samsung CMU driver tables, automotive display, core/bus interconnect, storage/high-speed IO, PERIC serial controllers, PERIS watchdog/system blocks, and power management.

## Risks and test signals
Risks include using `GOUT_*` top-domain outputs directly under a child CMU, provider-domain numbering mistakes, and breaking watchdog or safety-related clocks. Test signals include `dtbs_check`, CMU provider registration, serial/storage/display smoke tests, watchdog clocks visible and enabled, and suspend/resume validation for automotive always-on domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,exynosautov9.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,exynosautov920.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,exynosautov920.h

## Purpose
`samsung,exynosautov920.h` defines clock binding IDs for ExynosAuto v920 CMU domains, including top-level, CPU cluster, peripheral, miscellaneous, high-speed, media, and GPU domains.

## Important APIs, types, and functions
The macro families are `FOUT_*`, `MOUT_*`, `DOUT_*`, and `CLK_*`. Sections cover `CMU_TOP`, `CMU_CPUCL0`, `CMU_CPUCL1`, `CMU_CPUCL2`, `CMU_PERIC0`, `CMU_PERIC1`, `CMU_MISC`, `CMU_HSI0`, `CMU_HSI1`, `CMU_HSI2`, `CMU_M2M`, `CMU_MFC`, `CMU_MFD`, and `CMU_G3D`. IDs represent shared/MMC/G3D PLLs, top-level mux/divider clocks, CPU cluster switches, PERIC buses, high-speed interfaces, memory-to-memory and media codec clocks, and GPU clocks.

## Control flow
DTS files include these constants under the appropriate CMU provider. Runtime control is delegated to ExynosAuto v920 CMU driver data and common clock framework operations.

## State and persistence
The header contains no state. Domain-local numeric IDs are stable ABI; CMU registers and power domains hold runtime state.

## Dependencies and integration points
It integrates with automotive Exynos device trees, Samsung CMU support, CPU frequency/cluster management, PERIC serial buses, HSI storage/connectivity blocks, M2M/MFC/MFD media engines, G3D GPU, and power management.

## Risks and test signals
Risks include confusing CPU cluster provider IDs, changing section-local numbering, and missing top-level parent clocks for child CMUs. Test signals include successful CMU registration for every domain, CPU cluster clock rate changes, PERIC console/serial tests, storage/high-speed IO smoke tests, media codec probing, GPU clock registration, and `dtbs_check`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,exynosautov920.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,s2mps11.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,s2mps11.h

## Purpose
`samsung,s2mps11.h` defines clock IDs for fixed-rate clocks provided by the Samsung S2MPS11 PMIC.

## Important APIs, types, and functions
The macro API is `S2MPS11_CLK_AP`, `S2MPS11_CLK_CP`, `S2MPS11_CLK_BT`, and `S2MPS11_CLKS_NUM`. There are no functions or structs.

## Control flow
DTS consumers reference a PMIC clock phandle with one of these IDs. The S2MPS11 clock provider returns the corresponding fixed-rate or PMIC-controlled output clock to consumers.

## State and persistence
The header is stateless. PMIC register configuration and physical board routing determine whether AP, CP, or BT consumers receive usable clocks.

## Dependencies and integration points
It integrates with S2MPS11 MFD/PMIC support, Samsung board DTS files, common clock framework fixed-rate outputs, and modem/Bluetooth/application-processor clock consumers.

## Risks and test signals
Risks include swapped AP/CP/BT indexes and incorrect `S2MPS11_CLKS_NUM` if outputs are extended. Test signals include PMIC clock provider registration, consumer probe success, and measured or debugfs-visible fixed clock outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,s2mps11.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,s3c64xx-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,s3c64xx-clock.h

## Purpose
`samsung,s3c64xx-clock.h` defines stable clock IDs for Samsung S3C64xx DT-enabled platforms. Its comments explicitly mark the IDs as ABI and require additions only in free spaces or at the end.

## Important APIs, types, and functions
The header exports core clocks (`CLK27M`, `CLK48M`, `FOUT_*`, `ARMCLK`, `HCLKX2`, `HCLK`, `PCLK`), HCLK/PCLK bus gates, `SCLK_*` special clocks, S3C6410-specific `MEM0_*` clocks, `MOUT_*` muxes, `DOUT_*` dividers, and `NR_CLKS`. There are intentional gaps between groups to preserve ABI.

## Control flow
There is no executable flow. Device trees use the IDs in clock phandles; the S3C64xx clock driver maps them to Samsung clock framework entries.

## State and persistence
The file has no state. Numeric IDs are persistent ABI and especially sensitive because the header documents non-renumbering rules. Runtime state is in S3C64xx clock registers.

## Dependencies and integration points
It integrates with S3C64xx/S3C6410 DTS files, Samsung clock drivers, bus/peripheral drivers, display, camera, USB host, SD/MMC, audio, UART, SPI, I2C, IrDA, scaler, and memory-bus clock users.

## Risks and test signals
Risks include filling gaps incorrectly, changing `NR_CLKS`, or applying S3C6410-specific MEM0 IDs to incompatible SoCs. Test signals include DT compilation, clock provider registering all expected IDs, boot console, USB/storage/display/audio peripheral tests, and clk-summary validation of mux/divider/gate relationships.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,s3c64xx-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/sh73a0-clock.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/sh73a0-clock.h

## Purpose
`sh73a0-clock.h` defines clock IDs for the Renesas SH73A0 CPG and MSTP module-stop controllers.

## Important APIs, types, and functions
All macros use the `SH73A0_CLK_*` namespace. The CPG section defines root and derived clocks such as `MAIN`, `PLL0` through `PLL3`, DSI PHY clocks, and bus clocks. MSTP sections `MSTP0` through `MSTP5` define module clock bits for peripherals including I2C/IIC, SCIFA, SDHI, MMCIF, USB, FSI, CEU/CSI, TPU, KEYSC, and interrupt controller blocks. Values in MSTP sections are bit positions rather than one global monotonic index.

## Control flow
The header provides constants for device-tree clock specifiers. Runtime enable/disable flows through the SH73A0 CPG/MSTP clock provider, which interprets the ID according to the referenced provider/register group.

## State and persistence
The header is stateless. CPG and MSTP hardware registers hold the actual clock and module-stop state. ABI stability is required because DTS consumers depend on these numeric IDs or bit positions.

## Dependencies and integration points
It integrates with SH73A0 DTS, Renesas CPG/MSTP drivers, serial, storage, USB, camera, audio, timer, keypad, and interrupt-controller related devices.

## Risks and test signals
Risks include treating MSTP bit numbers as global IDs, using a clock under the wrong provider, and changing values that correspond to hardware register bits. Test signals include DT validation, CPG/MSTP provider registration, serial console, SDHI/MMCIF, USB, FSI audio, camera, keypad, and timer operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/sh73a0-clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/sifive-fu540-prci.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/sifive-fu540-prci.h

## Purpose
`sifive-fu540-prci.h` defines device-tree clock indexes for the SiFive FU540 PRCI clock provider.

## Important APIs, types, and functions
The API consists of `FU540_PRCI_CLK_COREPLL`, `FU540_PRCI_CLK_DDRPLL`, `FU540_PRCI_CLK_GEMGXLPLL`, and `FU540_PRCI_CLK_TLCLK`. There are no functions or structs.

## Control flow
FU540 DTS nodes reference these IDs in clock specifiers. The PRCI driver maps each ID to the corresponding PLL or tile-link clock and implements rate/enable operations where supported.

## State and persistence
The header has no state. PRCI registers store actual PLL configuration and may be initialized by firmware before Linux takes ownership.

## Dependencies and integration points
It integrates with FU540 device trees, the SiFive PRCI driver, CPU/core clocking, DDR clocking, GEMGXL Ethernet clocking, and TLCLK consumers.

## Risks and test signals
Risks include renumbering the small ABI, requesting unsupported rate changes, and mismatches with firmware-initialized PLL state. Test signals include PRCI provider probe, CPU/DDR/Ethernet operation, clk-summary rates, and boot stability on HiFive Unleashed-class boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/sifive-fu540-prci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/sifive-fu740-prci.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/sifive-fu740-prci.h

## Purpose
`sifive-fu740-prci.h` defines PRCI clock indexes for the SiFive FU740 SoC.

## Important APIs, types, and functions
The header exports `FU740_PRCI_CLK_COREPLL`, `DDRPLL`, `GEMGXLPLL`, `DVFSCOREPLL`, `HFPCLKPLL`, `CLTXPLL`, `TLCLK`, `PCLK`, and `PCIE_AUX`. These IDs cover CPU, DDR, Ethernet, DVFS, high-frequency peripheral, cluster/TileLink, peripheral bus, and PCIe auxiliary clocks.

## Control flow
The constants are used in DT clock phandles. Runtime operations are handled by the FU740 PRCI driver, which maps IDs to PRCI PLL or derived clock registers.

## State and persistence
The header has no state. PRCI register settings and firmware initialization determine runtime clock rates and persistence across resets or low-power states.

## Dependencies and integration points
It integrates with FU740 DTS, SiFive PRCI support, CPU DVFS, DDR, Ethernet, PCIe, peripheral bus devices, and platform firmware assumptions.

## Risks and test signals
Risks include wrong clock ID for PCIe or peripheral bus consumers, unstable ABI numbering, and rate-change conflicts with firmware. Test signals include PRCI registration, CPU DVFS behavior, DDR stability, Ethernet and PCIe bring-up, and clk-summary rate consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/sifive-fu740-prci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/sophgo,cv1800.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/sophgo,cv1800.h

## Purpose
`sophgo,cv1800.h` defines clock IDs for Sophgo CV1800-family clock providers.

## Important APIs, types, and functions
All exported IDs use `CLK_*`. The namespace begins with PLLs (`CLK_MPLL`, `CLK_TPLL`, `CLK_FPLL`, `CLK_MIPIMPLL`, `CLK_A0PLL`, display/camera PLLs), derived PLL divisors, TPU, buses, AXI/AHB/APB clocks, video/camera/display blocks, audio, UART/I2C/SPI/PWM/GPIO, timers, watchdog, USB, Ethernet, SD/eMMC, crypto, sensor/image pipelines, CPU-related clocks (`CLK_C906_*`, `CLK_A53`, `CLK_CPU_AXI0`, `CLK_CPU_GIC`), and reference outputs.

## Control flow
The header has no functions. DTS files use these IDs in clock specifiers, and the Sophgo CV1800 clock driver maps them to gates, dividers, muxes, and PLLs.

## State and persistence
No state exists in the header. Numeric IDs are persistent ABI. Runtime state resides in CV1800 clock-controller registers and may be seeded by boot firmware.

## Dependencies and integration points
It integrates with Sophgo CV1800 DTS, the CV1800 clock driver, RISC-V/Arm CPU clock consumers depending on variant, TPU/NPU-style acceleration, image/video/display pipelines, storage, Ethernet, USB, serial buses, and watchdog/timer blocks.

## Risks and test signals
Risks include SoC-variant mismatches, clock IDs for CPU architectures not present on a board, and media pipeline clocks with tight parent/rate requirements. Test signals include DT validation, clock provider probe, console/storage/network boot, watchdog/timer operation, camera/display pipeline tests, and clk-summary verification of PLL-derived rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/sophgo,cv1800.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/sophgo,sg2042-clkgen.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/sophgo,sg2042-clkgen.h

## Purpose
`sophgo,sg2042-clkgen.h` defines IDs for the Sophgo SG2042 clock generator block.

## Important APIs, types, and functions
The exported namespace is organized by function: `DIV_*` divider IDs, `GATE_*` gate IDs, and `MUX_*` mux IDs. Divider clocks cover MPLL/FPLL-derived CPU, DDR, A53, UART, LPC, EFUSE, Ethernet TX/PTP, GMAC, SD, TPU, PCIe, video, and timer-related paths. Gates cover the corresponding derived clocks and DDR/RP/AXI outputs. Mux IDs select DDR01, DDR23, RP CPU normal, and AXI DDR sources.

## Control flow
Device-tree clock cells reference these IDs under the SG2042 clkgen provider. Runtime control is in the Sophgo clock driver, which interprets whether an ID names a divider, gate, or mux.

## State and persistence
The header has no state. Clock generator registers hold selected parents, divisors, and gate state. IDs are stable ABI for DTBs.

## Dependencies and integration points
It integrates with SG2042 DTS, Sophgo clkgen driver data, CPU/DDR interconnect clocks, Ethernet, UART, SD, PCIe, TPU, video, timer, EFUSE, and LPC-style peripheral consumers.

## Risks and test signals
Risks include confusing divider/gate/mux IDs for the same signal, breaking DDR or CPU parent selection, and renumbering a dense ABI. Test signals include clock provider registration, DDR stability, CPU/interconnect rate checks, Ethernet/PTP behavior, PCIe/SD/UART operation, and debugfs verification that mux/divider/gate chains align.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/sophgo,sg2042-clkgen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/sophgo,sg2042-pll.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/sophgo,sg2042-pll.h

## Purpose
`sophgo,sg2042-pll.h` defines the PLL clock IDs for the Sophgo SG2042 PLL provider.

## Important APIs, types, and functions
The complete API is `MPLL_CLK`, `FPLL_CLK`, `DPLL0_CLK`, and `DPLL1_CLK`. There are no functions or structs.

## Control flow
DTS clock specifiers select one of these PLL outputs. The SG2042 PLL driver exposes the selected PLL to downstream clkgen or device consumers.

## State and persistence
The header is stateless. PLL frequency and lock state are held in hardware registers and may be initialized by firmware.

## Dependencies and integration points
It integrates with SG2042 DTS, the Sophgo PLL driver, the SG2042 clkgen provider, CPU, fabric, DDR, and peripheral clock trees that consume PLL roots.

## Risks and test signals
Risks include swapped PLL IDs, unsafe rate changes to shared roots, and firmware/kernel disagreement on PLL configuration. Test signals include PLL provider probe, clock summary root rates, stable CPU/DDR operation, and downstream clkgen consumers receiving expected parent rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/sophgo,sg2042-pll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/sophgo,sg2042-rpgate.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/sophgo,sg2042-rpgate.h

## Purpose
`sophgo,sg2042-rpgate.h` defines gate IDs for SG2042 reset/power or receive/processing gate-style clock control.

## Important APIs, types, and functions
The exported API is a contiguous set of `GATE_CLK_*` macros. It starts with `GATE_CLK_RXU0` through `GATE_CLK_RXU23`, continues with `GATE_CLK_RXU24`, `GATE_CLK_RXU25`, and then `GATE_CLK_MP0` through `GATE_CLK_MP15`. There are no functions or structs.

## Control flow
DTS consumers or provider data reference these gate IDs. Runtime enable/disable behavior is implemented by the SG2042 rpgate clock driver, which maps each ID to a hardware gate bit.

## State and persistence
The header has no state. Gate enable state lives in SG2042 hardware registers and is ABI-addressed by these numeric constants.

## Dependencies and integration points
It integrates with SG2042 DTS, the rpgate clock provider, multi-processor or receive-unit clock domains, and any consumers that require per-unit gate control.

## Risks and test signals
Risks include off-by-one gate-to-bit mapping, assuming RXU and MP gates are independent providers when they share one ID space, and changing the contiguous ABI. Test signals include provider registration, per-gate enable/disable tests, debugfs gate state inspection, and functional tests for devices or cores behind RXU/MP gates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/sophgo,sg2042-rpgate.h -->
