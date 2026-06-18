# subset-b-001168 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos850.c -->
# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos850.c

## Purpose

`clk-exynos850.c` is the Common Clock Framework driver data and registration glue for Samsung Exynos850 clock management units. It describes register offsets, PLLs, muxes, dividers, gates, fixed-rate inputs, and CPU clock rate/divider tables for the SoC, then registers each CMU through the Samsung ARM64 clock helper layer. The file covers CMU_TOP, APM, AUD, CMGP, CPUCL0, CPUCL1, G3D, HSI, IS, MFCMSCL, PERI, CORE, and DPU.

The implementation is mostly declarative. Runtime behavior is driven by arrays of `struct samsung_*_clock` descriptors and `struct samsung_cmu_info` blocks that are consumed by `exynos_arm64_register_cmu()`.

## Important APIs, Types, And Data

- `CLKS_NR_*` constants size each CMU clock provider by using the last dt-binding clock ID plus one. These must stay synchronized with `include/dt-bindings/clock/exynos850.h`.
- Register offset macros such as `PLL_CON0_PLL_SHARED0`, `CLK_CON_MUX_MUX_CLKCMU_*`, `CLK_CON_DIV_*`, and `CLK_CON_GAT_*` encode the CMU register maps.
- `top_clk_regs`, `apm_clk_regs`, and equivalent arrays list registers saved/restored or initialized by the Samsung CMU core.
- `struct samsung_pll_clock` arrays describe PLL blocks. TOP has shared0/shared1/MMC PLLs without rate tables, AUD has its PLL without a rate table, CPU clusters provide `cpu_pll_rates`, and G3D has a PLL without a rate table.
- `PNAME(...)` arrays describe parent clock name lists for muxes. These form the main dependency graph between TOP outputs and downstream CMU user muxes.
- `struct samsung_mux_clock`, `struct samsung_div_clock`, `struct samsung_gate_clock`, `struct samsung_fixed_rate_clock`, and `struct samsung_cpu_clock` arrays describe CCF clocks registered by the Samsung helpers.
- `struct samsung_cmu_info` instances are the integration contract for each CMU. Fields include descriptor arrays, register save lists, number of clock IDs, optional `.clk_name` parent dependency, optional `.cpu_clks`, and `.manual_plls`.
- `E850_CPU_DIV0()` and `exynos850_cluster_clk_d` define CPU child divider programming data for the CPU clock framework.
- `CPU_CLK()` entries create `cluster0_clk` and `cluster1_clk`, selecting the cluster PLL and switch-user muxes with Exynos850-specific CPU clock layouts.

## Control Flow

Early boot registration happens through `CLK_OF_DECLARE()`:

- `exynos850_cmu_top_init()` registers CMU_TOP early because other CMUs depend on its exported `dout_*` and `gout_*` roots.
- `exynos850_cmu_cpucl0_init()` and `exynos850_cmu_cpucl1_init()` register CPU cluster CMUs early so CPU frequency clocks exist as soon as possible.
- `exynos850_cmu_peri_init()` registers CMU_PERI early because the MCT timer depends on it.

The rest of the CMUs are registered by a platform driver:

- `exynos850_cmu_init()` is a `core_initcall()` that registers `exynos850_cmu_driver`.
- `exynos850_cmu_of_match` maps compatible strings to CMU info blocks for APM, AUD, CMGP, G3D, HSI, IS, MFCMSCL, CORE, and DPU.
- `exynos850_cmu_probe()` retrieves the matched `struct samsung_cmu_info` with `of_device_get_match_data()` and calls `exynos_arm64_register_cmu(dev, dev->of_node, info)`.

Within each CMU, the Samsung CCF helpers register fixed-rate clocks first as needed, then PLLs, muxes, dividers, gates, and CPU clocks based on the descriptor arrays. The clock topology is encoded by clock names, so parent names must exactly match clocks registered earlier or in the same CMU.

## CMU Coverage And Integration Points

- CMU_TOP defines the SoC-wide shared PLLs, MMC PLL, derived shared dividers, and top-level mux/div/gate outputs feeding APM, AUD, CORE, CPU clusters, DPU, G3D, HSI, IS, MFCMSCL, and PERI. Several IS and MFCMSCL top gates are marked `CLK_IS_CRITICAL` because downstream CMU register access depends on them.
- CMU_APM defines always-on and low-power clocks for RTC, PMU alive, I3C PMIC, SPEEDY, GPIO alive, mailbox, and CHUB/CMGP bus paths. It provides local fixed-rate RCO/DLL clocks and marks PMU alive critical.
- CMU_AUD defines an audio PLL, audio CPU/bus/audio-interface dividers, UAIF parent muxes, fixed external audio clock inputs, ABOX gates, codec MCLK, SYSMMU, GPIO, watchdog, and USB tick derived FM/SPDY clocks.
- CMU_CMGP defines a 49.152 MHz RCO source, ADC and two USI clocks, and gates for ADC, GPIO, SYSREG, and CMGP USI IP/PCLK paths. USI mux/div/gates use `CLK_SET_RATE_PARENT` where rate propagation is expected.
- CMU_CPUCL0 and CMU_CPUCL1 each define a cluster PLL, switch-user/debug-user muxes, read-only CPU/CMUREF/PCLK and embedded cluster dividers, cluster gates, and CPU clock descriptors. `.manual_plls = true` allows managed CPU PLL rate control using the provided PLL table.
- CMU_G3D defines GPU PLL/user switch muxing, a bus divider, and GPU/bus/sysreg/tzpc gates. Its PLL intentionally has no rate table, preventing normal `set_rate`.
- CMU_HSI defines user muxes for HSI bus, SD card, USB20 DRD, and RTC selection, plus gates for USB reference clocks, MMC card clocks, PPMU, GPIO, and SYSREG.
- CMU_IS defines image subsystem user muxes for bus, GDC, ITP, and VRA, a bus peripheral divider, and gates for CSIS, DMA, IPP, ITP, MCSC, VRA, PPMU, SYSMMU, and SYSREG.
- CMU_MFCMSCL defines user muxes for MFC, M2M, MCSC, and JPEG, a bus peripheral divider, and gates for codec/image processing, PPMU, SYSMMU, TZPC, and SYSREG.
- CMU_PERI defines peripheral bus/UART/HSI2C/SPI user muxes, HSI2C and SPI dividers, and gates for HSI2C, I2C, MCT, PWM, SPI, UART, watchdogs, TMU, GPIO, and SYSREG.
- CMU_CORE defines core bus/CCI/MMC/SSS user muxes, a bus peripheral divider, and gates for CCI, GIC, embedded MMC, DMA, security subsystem, GPIO, and SYSREG. CCI and GIC are critical.
- CMU_DPU defines display user mux/divider and gates for DECON, DMA, DPP, PPMU, SMMU, SYSREG, and CMU PCLK. The CMU PCLK is ignored-unused pending the display driver.

## State And Persistence Behavior

The driver does not maintain heap state or persistent storage itself. Persistent hardware state is in memory-mapped CMU registers. The `*_clk_regs` arrays tell the Samsung clock framework which registers are important for save/restore and initialization. CCF state such as enable counts, rates, and parents is owned by the common clock core and Samsung helper code after registration.

CPU cluster dividers are read-only in descriptor flags (`CLK_DIVIDER_READ_ONLY`) and often `CLK_GET_RATE_NOCACHE`, so runtime rate reporting reads hardware rather than trusting cached values. Critical and ignore-unused flags affect boot-time clock disable behavior: critical clocks cannot be disabled, while ignore-unused protects clocks that currently lack consumers.

## Dependencies

- Linux CCF headers and platform/of infrastructure: `<linux/clk-provider.h>`, `<linux/of.h>`, `<linux/platform_device.h>`, `<linux/mod_devicetable.h>`.
- Exynos850 dt-binding IDs from `<dt-bindings/clock/exynos850.h>`.
- Samsung clock helper internals from `clk.h`, CPU clock support from `clk-cpu.h`, and ARM64 CMU registration from `clk-exynos-arm64.h`.
- Device tree compatible strings for each CMU must match the DT nodes and must provide mapped register regions and parent clocks such as `oscclk`, `rtcclk`, and the named TOP outputs.
- Consumer drivers depend on these clock names/IDs through DT `clocks` references: CPUfreq, timer/MCT, UART/I2C/SPI/HSI2C, MMC, USB, audio/ABOX, GPU, display, camera/image, MFC/JPEG, DMA, SYSMMU, and security engines.

## Risks And Edge Cases

- `CLKS_NR_*` values are fragile: if dt-binding IDs change without updating these sizes, providers can reject valid IDs or allocate sparse arrays incorrectly.
- Clock parent names are string-coupled. A typo in names such as `dout_*`, `gout_*`, or `mout_*` silently breaks parent resolution and can produce wrong rates or deferred registration.
- Several PLLs intentionally omit rate tables because manual PLL control is not enabled by default. Adding rate changes for those clocks without hardware sequencing support can fail or destabilize the SoC.
- Early registration order is important. TOP must be present before dependent CMUs, CPU clocks must exist early for CPUfreq/boot CPU setup, and PERI must be available for MCT.
- `CLK_IGNORE_UNUSED` appears on GPIO, CMU PCLK, ABOX, and XIU-like clocks where consumers are incomplete. Removing these flags before consumers are ready can hang boot or break register access.
- `CLK_IS_CRITICAL` protects CCI, GIC, PMU alive, IS/MFCMSCL access paths, and other essential buses. Incorrectly relaxing these can cause hard hangs; overusing them can hide missing consumers and increase power draw.
- CPU clock rate tables and `E850_CPU_DIV0()` values must match silicon OPP expectations. Wrong dividers can break debug/peripheral clocks while CPU frequency scaling appears superficially correct.
- Some gate parent choices use functional clocks instead of bus clocks. Changes need hardware manual validation because rate propagation and enable sequencing can affect peripheral programming.

## Test Signals

- Build coverage: compile with `CONFIG_COMMON_CLK_SAMSUNG`, `CONFIG_ARCH_EXYNOS`, and dt-binding header consistency checks.
- Boot log signals: CMU registration succeeds for TOP, CPUCL0, CPUCL1, PERI, and platform CMUs; no missing parent warnings from CCF; no failed `of_clk_add_provider` or duplicate clock names.
- Device-tree validation: each compatible in `exynos850_cmu_of_match` and each `CLK_OF_DECLARE` string appears in Exynos850 DT nodes with correct register ranges.
- Runtime CCF inspection: `/sys/kernel/debug/clk/clk_summary` shows expected parentage, rates, critical flags, and enabled consumers.
- Functional smoke tests: MCT timer boot, CPUfreq transitions on both clusters, UART console, I2C/SPI/HSI2C, eMMC/SD, USB, audio, GPU, display, camera/image, MFC/JPEG, and suspend/resume.
- Negative test indicators: boot hangs after unused-clock disable, missing parent messages, impossible CPU rates, peripheral timeouts, or inability to access downstream CMU registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos850.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos8895.c -->
# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos8895.c

## Purpose

`clk-exynos8895.c` provides Common Clock Framework support for the Samsung Exynos8895 SoC. It declares the register maps and clock topology for CMU_TOP, CMU_PERIS, CMU_FSYS0, CMU_FSYS1, CMU_PERIC0, and CMU_PERIC1, then registers early boot CMUs through `CLK_OF_DECLARE()` and remaining CMUs through a platform driver.

Compared with the Exynos850 driver, this file is narrower in downstream CMU coverage but much larger in TOP fanout. TOP exposes shared PLLs, many bus and functional roots, and fixed-factor derived clocks for ABOX, APM, camera, CPU cluster switches, debug, display, storage, USB, PCIe, G2D/G3D, image/video, modem, and peripheral domains.

## Important APIs, Types, And Data

- `CLKS_NR_TOP`, `CLKS_NR_FSYS0`, `CLKS_NR_FSYS1`, `CLKS_NR_PERIC0`, `CLKS_NR_PERIC1`, and `CLKS_NR_PERIS` size each clock provider according to the final dt-binding clock ID plus one from `dt-bindings/clock/samsung,exynos8895.h`.
- Register offset macros define TOP and downstream CMU register maps. Downstream gates use verbose hardware-generated names with `_BLK`, `_UID`, and `_IPCLKPORT` fields preserved in macro names.
- A local comment documents the name-mangling strategy from register names to clock names. This is important because most of the file is table-generated-looking data whose correctness depends on predictable naming.
- `top_clk_regs`, `peris_clk_regs`, `fsys0_clk_regs`, `fsys1_clk_regs`, `peric0_clk_regs`, and `peric1_clk_regs` enumerate registers for Samsung CMU save/restore handling.
- `pll_shared0_rate_table` through `pll_shared4_rate_table` define single fixed PLL rates for shared TOP PLLs.
- `top_pll_clks` registers five shared PLLs using `pll_1051x` and `pll_1052x` hardware types.
- TOP `PNAME(...)` arrays define parent sets for many SoC output roots. Parent choices include shared PLL outputs, fixed-factor dividers, `oscclk`, and a CP-to-AP MIF clock user path.
- `top_fixed_factor_clks` derives shared PLL div2/div4 clocks, FSYS1 PCIe divide-by-8, CP2AP MIF divide-by-2, and OTP divide-by-8 clocks without separate hardware divider descriptors.
- `struct samsung_mux_clock` and `struct samsung_gate_clock` arrays dominate downstream CMUs. FSYS and PERIC blocks use user muxes and gates but no local dividers in this file; their rates are primarily determined by TOP dividers and fixed factors.
- `struct samsung_cmu_info` blocks are the final data passed to `exynos_arm64_register_cmu()`.

## Control Flow

Early boot registration:

- `exynos8895_cmu_top_init()` registers CMU_TOP via `CLK_OF_DECLARE(exynos8895_cmu_top, "samsung,exynos8895-cmu-top", ...)`. TOP is early because all other domains consume TOP-generated clock roots.
- `exynos8895_cmu_peris_init()` registers CMU_PERIS via `CLK_OF_DECLARE(exynos8895_cmu_peris, "samsung,exynos8895-cmu-peris", ...)`. PERIS is early because the MCT timer and interrupt-controller related clocks are needed during early boot.

Platform-driver registration:

- `exynos8895_cmu_init()` registers `exynos8895_cmu_driver` at `core_initcall`.
- `exynos8895_cmu_of_match` maps `samsung,exynos8895-cmu-fsys0`, `-fsys1`, `-peric0`, and `-peric1` to their CMU info blocks.
- `exynos8895_cmu_probe()` obtains the matched CMU info through `of_device_get_match_data()` and registers it with `exynos_arm64_register_cmu(dev, dev->of_node, info)`.

Clock registration within a CMU is delegated to the Samsung helper layer. Parent-child relationships are resolved through clock names and the provider ID space declared in the dt-binding header.

## CMU Coverage And Integration Points

- CMU_TOP contains five shared PLLs and a broad SoC root clock fanout. It creates muxes, dividers, fixed-factor clocks, and gates for ABOX, APM, BUS1, BUSC, CAM, CIS clocks, CORE, CPU cluster switches, DBG, DCAM, DPU, droop detector, DSP, FSYS0, FSYS1, G2D, G3D, HPM, IMEM, ISPHQ, ISPLP, IVA, MFC, MIF switch, PERIC0, PERIC1, PERIS, SRDZ, VPU, modem shared clocks, CP2AP MIF, and OTP. Some TOP gates are `CLK_IGNORE_UNUSED` for bus/display/DSP paths that may not yet have complete consumers.
- CMU_PERIS provides the always-important peripheral system block. It has a bus-user mux, a GIC mux, and gates for PERIS CMU PCLK, AXI/APB bridges, TMU, GIC, MCT, OTP, PMU, SYSREG, sixteen TZPC clocks, watchdog clocks for both clusters, and XIU. CMU PCLK, bus bridges, GIC, and LHM paths are marked critical.
- CMU_FSYS0 covers embedded storage, USB3/USBTV, DisplayPort link timing, ETR/trace, GPIO, bus interconnects, PMU, SYSREG, UFS embedded clocks, and MMC embedded clocks. User muxes select TOP-provided FSYS0 bus, DPGTC, MMC, UFS, and USB roots. Several bus infrastructure and UFS clocks are critical or ignore-unused because disabling them can hang the system or break boot-critical storage paths.
- CMU_FSYS1 covers external/removable storage and high-speed I/O: MMC card, PCIe, UFS card, RTIC, SSS, TOE Wi-Fi, BCM, SYSREG, PMU, and XIU. It exposes user muxes for FSYS1 bus, MMC card, PCIe, and UFS card. Many AXI/APB bridge and LHM/LHS clocks are critical; UFS card unipro and XIU clocks are protected with ignore-unused.
- CMU_PERIC0 covers the first peripheral controller group: bus, debug UART, USI00-USI03, PWM, SPEEDY TSP, GPIO, PMU, SYSREG, and APB bridge clocks. Its bus/APB/LHM clocks are critical; GPIO is ignore-unused.
- CMU_PERIC1 covers the second peripheral controller group: bus, SPEEDY2, SPI_CAM0/1, UART_BT, USI04-USI13, HSI2C camera channels, GPIO, PMU, SYSREG, XIU, and multiple SPEEDY display/touch related clocks. It marks CMU PCLK, AXI2APB, and LHM clocks critical and protects GPIO/XIU with ignore-unused.

## State And Persistence Behavior

The driver itself has no mutable software state beyond CCF objects created during registration. Hardware state lives in CMU registers. The `*_clk_regs` arrays tell the Samsung CMU framework which registers belong to each CMU for initialization and save/restore. Rates and enable counts are then managed by CCF.

TOP PLL tables each contain one rate, so clock rate behavior is effectively constrained to known boot-supported PLL programming. Fixed-factor clocks avoid direct divider register programming for several derived roots. Downstream CMUs rely on `.clk_name = "bus"` for parent/domain readiness, while TOP has no `.clk_name` dependency because it is the root provider.

Critical flags persist as clock framework policy: critical gates are not disabled by unused-clock cleanup. Ignore-unused gates protect clocks lacking complete consumers. `CLK_SET_RATE_PARENT` appears on MMC-related gates and muxes so storage clocks can request parent-rate adjustments through their user muxes.

## Dependencies

- Linux CCF and platform/of headers: `<linux/clk-provider.h>`, `<linux/mod_devicetable.h>`, `<linux/of.h>`, and `<linux/platform_device.h>`.
- Exynos8895 clock binding IDs from `<dt-bindings/clock/samsung,exynos8895.h>`.
- Samsung clock framework helpers from `clk.h` and ARM64 CMU registration from `clk-exynos-arm64.h`.
- Device tree nodes must use the compatible strings in `CLK_OF_DECLARE` and `exynos8895_cmu_of_match`, provide the proper register ranges, and provide root clocks such as `oscclk` and any bus domain parent named by `.clk_name`.
- Consumers include MCT/timer, GIC/peripheral system, UART/USI/SPI/I2C-like serial controllers, GPIO, watchdogs, TMU, MMC/eMMC/SD, UFS, USB3, PCIe, DisplayPort, RTIC/SSS security blocks, camera-adjacent SPI/HSI2C, and display/touch SPEEDY blocks.

## Risks And Edge Cases

- This file is highly name-sensitive. The documented mangling strategy reduces drift, but any mismatch between clock names, binding IDs, and DT consumers can break parent lookup or consumer clock acquisition.
- TOP fanout is large and cross-domain. Incorrect TOP parent selection or divider width can affect multiple subsystems at once, especially storage, display, camera, and CPU switch roots.
- Many downstream gates are marked `CLK_IS_CRITICAL` based on boot stability requirements. Removing these flags can cause boot hangs, especially in PERIS, FSYS bridge paths, and CMU PCLK gates.
- `CLK_IGNORE_UNUSED` protects incomplete consumer coverage. It can hide missing clock references and increase power consumption, but premature removal risks disabling live hardware.
- `CLKS_NR_*` sizing must match dt-binding IDs. Sparse or reordered IDs can create provider lookup errors if the final ID changes.
- Single-entry PLL rate tables mean generic rate changes may be limited. Adding rates requires hardware validation of PLL type, lock times, and downstream divider limits.
- Several gate names are extremely long and hardware-derived; manual edits are prone to copy/paste mistakes in parent strings, register offsets, or clock IDs.
- The `.clk_name = "bus"` dependency in downstream CMUs assumes a parent clock named `bus` is supplied or resolved by the Samsung registration path. DT/domain integration needs to preserve that contract.
- FSYS0/FSYS1 include storage and boot media clocks. Wrong gating or parent-rate propagation can lead to data corruption, enumeration failures, or boot stalls.

## Test Signals

- Build signals: compile the Samsung clock driver set with the Exynos8895 dt-binding header and check for undefined clock IDs or duplicate clock names.
- Device-tree validation: confirm compatible strings for TOP, PERIS, FSYS0, FSYS1, PERIC0, and PERIC1 are present with correct MMIO ranges and parent clocks.
- Boot logs: no missing parent warnings, provider registration failures, or unused-clock disable hangs. PERIS must register early enough for MCT/GIC-related paths.
- Debugfs CCF inspection: `clk_summary` should show TOP shared PLL rates, derived fixed-factor clocks, FSYS/PERIC/PERIS mux parents, and expected critical/ignore-unused policy.
- Functional tests: serial console and debug UART, MCT timer, watchdogs, GPIO, TMU, eMMC/MMC/SD, UFS, USB3, PCIe, security engines, DisplayPort, SPEEDY, SPI camera clocks, and USI buses.
- Suspend/resume test signals: CMU register save/restore should preserve mux/div/gate state, especially for storage and PERIS critical clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos8895.c -->
