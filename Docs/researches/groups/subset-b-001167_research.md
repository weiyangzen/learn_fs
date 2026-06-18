# Research: subset-b-001167

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos7.c -->
# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos7.c

## Purpose

`clk-exynos7.c` is a Samsung Common Clock Framework provider for the Exynos7 SoC family. It describes the SoC's clock management units as static data tables and registers each CMU from device tree using `CLK_OF_DECLARE()`. The file does not implement clock algorithms itself; it maps PLLs, muxes, dividers, fixed-rate clocks, fixed-factor clocks, and gates onto register offsets and bit fields consumed by the shared Samsung clock core in `drivers/clk/samsung/clk.c`.

The file covers many Exynos7 clock islands: `TOPC`, `TOP0`, `TOP1`, `CCORE`, `PERIC0`, `PERIC1`, `PERIS`, `FSYS0`, `FSYS1`, `MSCL`, and `AUD`. `TOPC` owns the main PLL outputs and top-level derived clocks. `TOP0` and `TOP1` distribute those top clocks into peripheral and file-system domains. Leaf CMUs expose device clocks for RTC, I2C, UART, SPI, timers, chip ID, USB, UFS, MMC, media scaler/JPEG/G2D, and audio peripherals.

## Important APIs, Types, and Tables

The main type is `struct samsung_cmu_info`. Each CMU has one instance describing the arrays to register and the number of clock IDs exported to the CCF:

- `topc_cmu_info` combines PLLs, muxes, dividers, gates, fixed-factor clocks, and a register list.
- `top0_cmu_info` and `top1_cmu_info` define top-level mux/divider/gate distribution domains.
- `ccore_cmu_info`, `peric0_cmu_info`, `peric1_cmu_info`, `peris_cmu_info`, `fsys0_cmu_info`, `fsys1_cmu_info`, `mscl_cmu_info`, and `aud_cmu_info` describe their respective leaf domains.

The file relies on Samsung clock macros from `clk.h`: `PLL()`, `MUX()`, `MUX_F()`, `DIV()`, `GATE()`, `FFACTOR()`, `FRATE()`, and `PNAME()`. These macros create `struct samsung_pll_clock`, `struct samsung_mux_clock`, `struct samsung_div_clock`, `struct samsung_gate_clock`, fixed-factor descriptors, fixed-rate descriptors, and parent-name arrays. Clock IDs come from `<dt-bindings/clock/exynos7-clk.h>`, so exported IDs must stay aligned with the binding.

Registration entry points are small wrappers such as `exynos7_clk_topc_init()`, `exynos7_clk_top0_init()`, and `exynos7_clk_aud_init()`. Each calls `samsung_cmu_register_one(np, &..._cmu_info)`. `CLK_OF_DECLARE()` binds each wrapper to a compatible string like `samsung,exynos7-clock-topc`.

## Control Flow

During early boot, the OF clock initialization path matches clock-provider device-tree nodes against the `CLK_OF_DECLARE()` compatible strings. For each matched node, the corresponding `exynos7_clk_*_init()` function passes the node and static CMU descriptor to `samsung_cmu_register_one()`. The shared Samsung code maps the CMU register region, snapshots or manages the listed `clk_regs`, creates the CCF clock hardware objects, and publishes the provider for consumer drivers.

The runtime control path is then mostly CCF-driven. A consumer asks for a clock by DT phandle/index or by clock name. The CCF invokes the registered mux/divider/gate/PLL operations from the Samsung core, which read or update the register offsets and bit positions declared here. Parent propagation is enabled selectively with flags such as `CLK_SET_RATE_PARENT`; always-on dependencies use `CLK_IS_CRITICAL` or `CLK_IGNORE_UNUSED`.

## State and Persistence Behavior

The file has no heap-owned state, no persistent storage, and no runtime data structures beyond what the shared registration helpers allocate. Its state model is declarative: hardware register state lives in CMU registers, and CCF-visible state is reconstructed at boot from static tables. The `..._clk_regs` arrays identify registers relevant for the CMU, which the Samsung core can use for register save/restore and initialization ordering. Several descriptors are `__initconst`, so the table memory is discarded after boot registration.

Critical clocks are the main persistence signal. For example `aclk_ccore_133`, `aclk_fsys0_200`, and `aclk_fsys1_200` are marked critical where register access or essential bus function depends on them. FSYS1 includes a comment that `aclk_fsys1_200` must remain enabled until proper runtime PM support exists. USB and UFS PHY fixed-rate clocks are modeled as clock inputs rather than discovered dynamically.

## Dependencies and Integration Points

This driver depends on the Linux CCF (`<linux/clk-provider.h>`), the Samsung clock provider helpers (`clk.h`), and Exynos7 clock IDs in the DT binding. It integrates with device tree through compatible strings:

- `samsung,exynos7-clock-topc`
- `samsung,exynos7-clock-top0`
- `samsung,exynos7-clock-top1`
- `samsung,exynos7-clock-ccore`
- `samsung,exynos7-clock-peric0`
- `samsung,exynos7-clock-peric1`
- `samsung,exynos7-clock-peris`
- `samsung,exynos7-clock-fsys0`
- `samsung,exynos7-clock-fsys1`
- `samsung,exynos7-clock-mscl`
- `samsung,exynos7-clock-aud`

Clock-name integration is also important. Parent strings such as `sclk_bus0_pll_a`, `aclk_peric0_66`, `sclk_mmc0`, `phyclk_ufs20_tx0_symbol`, and `fout_aud_pll` must match clocks produced by other tables in this file or by external providers. The ordering implied by device-tree availability matters because leaf CMUs use user mux parents produced by TOP CMUs.

## Risks and Edge Cases

The primary risks are data-table accuracy issues: wrong register offsets, bit shifts, bit widths, parent ordering, or clock IDs can silently produce incorrect clock rates or gate the wrong hardware block. Since many clocks share a register and differ only by bit offset, small mistakes can be difficult to diagnose. A binding mismatch can expose the wrong clock to a consumer or leave a required clock unreachable.

Critical-clock flags are another risk area. Missing `CLK_IS_CRITICAL` on clocks needed for register access, buses, interrupt paths, or early boot can hang the system during unused-clock cleanup. Overusing critical or ignore-unused flags can hide power-management bugs and keep domains unnecessarily active. The FSYS1 comment indicates an acknowledged runtime PM gap.

Parent-name dependencies are fragile because they are string-based within the provider framework. A renamed clock or a mismatched DT-provided external parent can break rate propagation or leave a mux parent unresolved. Fixed-rate PHY clocks may also become inaccurate if board or PHY revisions use different actual rates.

## Test Signals

Useful validation starts with build coverage for `CONFIG_COMMON_CLK_SAMSUNG` and Exynos7 DT bindings. Boot logs should show each CMU provider registered without missing-parent warnings. Device-tree clock consumers for UART, SPI, I2C, MMC, USB, UFS, audio, RTC, WDT, TMU, and MSCL/JPEG/G2D should probe successfully.

Runtime checks include `/sys/kernel/debug/clk/clk_summary` to confirm expected parentage, rates, enable counts, and critical clocks. Peripheral smoke tests should cover serial console stability, MMC timing modes, USB PHY operation, UFS link operation where present, audio I2S/PCM/SPDIF clocks, watchdog and thermal sensor access, and media scaler/JPEG/G2D activity. Suspend/resume testing should focus on CMU register restoration and on the domains whose register lists are enumerated here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos7870.c -->
# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos7870.c

## Purpose

`clk-exynos7870.c` provides Common Clock Framework support for the Samsung Exynos7870 SoC. It is a data-driven platform driver that describes the Exynos7870 CMU blocks and registers the matching `struct samsung_cmu_info` for each device-tree compatible. Compared with older `CLK_OF_DECLARE()`-only Samsung clock drivers, this file uses a single platform driver and an OF match table for most CMUs.

The covered CMUs are `MIF`, `DISPAUD`, `FSYS`, `G3D`, `ISP`, `MFCMSCL`, and `PERI`. `MIF` is the central source and distributor for memory/bus, media, display/audio, file-system, ISP, MFC/MSCL, and peripheral clocks. Other CMUs consume MIF outputs through user muxes and expose local PLLs, dividers, and gates for display/audio, USB/MMC/storage, GPU, camera/ISP, media codec/scaler, and low-speed peripherals.

## Important APIs, Types, and Tables

The file uses the Samsung ARM64 clock helper declared in `clk-exynos-arm64.h`. The key registration API is `exynos_arm64_register_cmu(dev, dev->of_node, info)`, called from `exynos7870_cmu_probe()`. `of_device_get_match_data(dev)` selects the correct `struct samsung_cmu_info` from `exynos7870_cmu_of_match`.

Each CMU is represented by a `struct samsung_cmu_info`: `mif_cmu_info`, `dispaud_cmu_info`, `fsys_cmu_info`, `g3d_cmu_info`, `isp_cmu_info`, `mfcmscl_cmu_info`, and `peri_cmu_info`. These descriptors collect register-offset arrays and the relevant `PLL`, `MUX`, `DIV`, `GATE`, `FRATE`, and `FFACTOR` tables. Clock IDs come from `<dt-bindings/clock/samsung,exynos7870-cmu.h>`.

Notable hardware descriptions include three MIF PLLs (`fout_mif_mem_pll`, `fout_mif_media_pll`, `fout_mif_bus_pll`), local PLLs for display/audio, USB FSYS, G3D, and ISP, fixed-rate MIPI/USB/audio clocks, and a large set of MIF output gates. Many gates use the `gout_...` naming style, matching the Exynos7870 clock binding and downstream consumer expectations.

## Control Flow

`core_initcall(exynos7870_cmu_init)` registers `exynos7870_cmu_driver` early. When a platform device with a compatible such as `samsung,exynos7870-cmu-mif` or `samsung,exynos7870-cmu-peri` probes, `exynos7870_cmu_probe()` retrieves the matched CMU descriptor and hands it to `exynos_arm64_register_cmu()`. The Samsung ARM64 helper maps the node's register range, registers PLL/mux/divider/gate/fixed clocks, and installs the OF clock provider.

At runtime, the CCF controls individual clocks through Samsung-provided clock operations. Muxes select parents using the declared parent-name arrays, dividers program rate divisors, and gates toggle bits in the declared CMU registers. Rate changes propagate through `CLK_SET_RATE_PARENT` where enabled. The platform driver has no remove path; these CMUs are expected to be permanent boot-time providers.

## State and Persistence Behavior

Driver state is almost entirely static and hardware-backed. The CMU descriptors and register lists are `__initconst`; after init, the shared Samsung registration code owns the clock hardware state. The only mutable state is in hardware CMU registers and the CCF structures created during registration. There is no file persistence, firmware state store, or dynamically updated private data in this source file.

The `..._clk_regs` arrays are important for state retention across suspend/resume and for safe registration of register-backed clocks. Many Exynos7870 gates are marked `CLK_IS_CRITICAL`, especially MIF mux/gate chains, PPMU, HSI2C, ADC, display, G3D, ISP, and MFCMSCL paths. Those flags prevent the common unused-clock cleanup from disabling clocks required for bus fabric, register access, or always-on hardware.

## Dependencies and Integration Points

The source depends on the platform bus, OF match data, Linux CCF, Samsung `clk.h`, Samsung ARM64 CMU helper code, and the Exynos7870 DT binding. Its compatible strings are:

- `samsung,exynos7870-cmu-mif`
- `samsung,exynos7870-cmu-dispaud`
- `samsung,exynos7870-cmu-fsys`
- `samsung,exynos7870-cmu-g3d`
- `samsung,exynos7870-cmu-isp`
- `samsung,exynos7870-cmu-mfcmscl`
- `samsung,exynos7870-cmu-peri`

The integration pattern is hierarchical. MIF exports clocks such as `gout_mif_cmu_fsys_bus`, `gout_mif_cmu_peri_spi0`, and `gout_mif_cmu_isp_cam`; FSYS, PERI, ISP, DISPAUD, MFCMSCL, and G3D consume those as user-mux parents. This means DT node presence and probe timing must make upstream providers available before dependent consumer clocks are resolved.

## Risks and Edge Cases

The most important risk is parent-chain correctness. A local CMU often depends on a MIF gate, a user mux, and sometimes a local PLL gate before reaching a leaf clock. Any wrong parent string, ID, bit offset, or critical flag can break a whole peripheral domain. The file also has repeated register offsets with distinct semantic names, such as mux and gate aliases sharing the same address; that is intentional for this hardware but increases maintenance risk.

Another risk is broad use of `CLK_IS_CRITICAL`. Some clocks clearly guard bus access, but critical flags can also hide missing runtime PM integration or keep power domains active. Removing or changing those flags requires hardware boot, idle, and suspend testing. Conversely, dropping one incorrectly can cause hard hangs during unused-clock cleanup.

PLL rate tables are sparse or absent for most PLLs. That is acceptable when firmware or bootloader leaves stable rates and the kernel only gates/divides, but it limits safe dynamic rate programming. Fixed-rate clocks for MIPI, USB, and audio assume specific board/PHY frequencies. Binding drift is also a risk because clock IDs and `gout_...` names must match DTS consumers.

## Test Signals

Build tests should cover the Exynos7870 binding header and the platform-driver path. Boot tests should verify that all seven compatible nodes probe, no missing-parent warnings appear, and clock providers are available before dependent devices. `clk_summary` should show MIF roots feeding DISPAUD, FSYS, G3D, ISP, MFCMSCL, and PERI user muxes.

Peripheral validation should include display/audio clocking, MMC and USB operation, GPU/G3D access if enabled, ISP/camera sensor clock paths, MFC/MSCL media paths, UART/SPI/I2C/PWM/MCT/WDT/TMU clocks, and ADC/HSI2C paths marked critical. Suspend/resume and idle tests are especially valuable because this file enumerates large register-save lists and many always-on gates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos7870.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos7885.c -->
# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos7885.c

## Purpose

`clk-exynos7885.c` provides Samsung Common Clock Framework support for the Exynos7885 SoC. It describes four CMU domains: `TOP`, `PERI`, `CORE`, and `FSYS`. `TOP` owns the shared PLLs and exports divided clocks for core, peripheral, and file-system domains. `PERI` exposes low-speed peripheral gates and user muxes. `CORE` exposes interconnect, GIC, and TREX bus clocks. `FSYS` exposes USB and MMC clocking, including a USB PLL.

The driver deliberately mixes two registration styles. `TOP` and `PERI` are registered early with `CLK_OF_DECLARE()` because later domains and early timer hardware depend on them. `CORE` and `FSYS` are registered through a platform driver selected by OF match data. This split is the main behavioral feature of the file.

## Important APIs, Types, and Tables

The file uses `struct samsung_cmu_info` descriptors named `top_cmu_info`, `peri_cmu_info`, `core_cmu_info`, and `fsys_cmu_info`. It relies on Samsung clock table macros from `clk.h`: `PLL()`, `MUX()`, `MUX_F()`, `nMUX_F()`, `DIV()`, `GATE()`, and `PNAME()`. ARM64-specific registration uses `exynos_arm64_register_cmu()`.

Clock ID bounds are computed with local macros: `CLKS_NR_TOP`, `CLKS_NR_CORE`, `CLKS_NR_PERI`, and `CLKS_NR_FSYS`. These depend on the last IDs from `<dt-bindings/clock/exynos7885.h>`, so the source and binding must evolve together.

`TOP` defines `fout_shared0_pll` and `fout_shared1_pll`, muxes for core/peri/fsys outputs, dividers for shared PLL divisions, and gates for the domain output clocks. `PERI` defines user muxes from `dout_peri_*` parents and gates for GPIO, HSI2C, I2C, PWM, SPI, UART, USI, MCT, SYSREG, and WDT. `CORE` defines user muxes for bus/CCI/G3D, a GIC mux, a bus peripheral divider, and critical interconnect/interrupt/TREX gates. `FSYS` defines the USB PLL, user muxes for bus/MMC/USB, and gates for MMC and USB PHY/controller clocks.

## Control Flow

During early OF clock initialization, `exynos7885_cmu_top_init()` registers `top_cmu_info` for `samsung,exynos7885-cmu-top`, and `exynos7885_cmu_peri_init()` registers `peri_cmu_info` for `samsung,exynos7885-cmu-peri`. Both pass `NULL` as the device pointer and use the device node directly.

Later, `core_initcall(exynos7885_cmu_init)` registers `exynos7885_cmu_driver`. Its OF match table maps `samsung,exynos7885-cmu-core` to `core_cmu_info` and `samsung,exynos7885-cmu-fsys` to `fsys_cmu_info`. `exynos7885_cmu_probe()` retrieves match data and calls `exynos_arm64_register_cmu(dev, dev->of_node, info)`.

After registration, normal CCF control paths apply. Consumers obtain clocks by DT IDs or names, and the Samsung clock operations manipulate the declared register offsets and bit fields. Mux/divider/gate parentage models the hardware clock tree: shared PLL outputs feed divided TOP clocks, TOP gates feed user muxes in PERI/CORE/FSYS, and leaf gates feed device drivers.

## State and Persistence Behavior

This file stores no private mutable driver state. Its static descriptors are `__initconst` and are consumed during boot-time registration. Hardware CMU registers hold actual enable, mux, divider, and PLL state. The Samsung registration helper creates the durable CCF objects and uses each CMU's `clk_regs` array for register management.

Persistence concerns are mostly about keeping essential gates active. In `CORE`, CCI and GIC clocks are explicitly marked `CLK_IS_CRITICAL`, as are several TREX bus clocks. In `PERI`, GPIO top PCLK is marked `CLK_IGNORE_UNUSED` with a TODO noting it should eventually be enabled by the GPIO driver or made critical. Several CMU descriptors set `.clk_name` to an always-needed domain clock, such as `dout_peri_bus`, `dout_core_bus`, and `dout_fsys_bus`, which helps the Samsung ARM64 helper manage parent/domain clocking.

## Dependencies and Integration Points

The source depends on the Linux platform bus, OF matching, CCF, Samsung `clk.h`, Samsung ARM64 CMU helper code, and the Exynos7885 clock binding. Its compatible strings are:

- `samsung,exynos7885-cmu-top`
- `samsung,exynos7885-cmu-peri`
- `samsung,exynos7885-cmu-core`
- `samsung,exynos7885-cmu-fsys`

The early `TOP` provider is an integration prerequisite for `CORE`, `PERI`, and `FSYS` because their user muxes refer to `dout_core_*`, `dout_peri_*`, and `dout_fsys_*` outputs created in TOP. `PERI` is also early because MCT timer clocking is needed during early boot. `FSYS` integrates with MMC and USB consumers, while `CORE` integrates with interconnect, interrupt-controller, and bus fabric operation.

## Risks and Edge Cases

The biggest risk is registration ordering. If TOP or PERI are moved out of early registration without compensating changes, timer or dependent CMU clocks can be unavailable during early boot. Conversely, early registration with a `NULL` device pointer means device-managed cleanup is not relevant and the provider is expected to live for the kernel lifetime.

Table correctness is also critical. Most gate registers use bit 21, while muxes commonly use bit 4 or 0. A wrong register name, offset, or parent order can select the oscillator instead of a PLL-derived clock, break rate propagation, or disable a peripheral. `nMUX_F()` for `mout_usb_pll` is notable because it differs from the normal mux macro and should be checked carefully against hardware semantics.

The TODO on `gout_gpio_top_pclk` signals an integration gap: the clock is kept from unused cleanup even though the long-term owner should be the GPIO driver or a critical-clock declaration. The USB PLL has an explicit 26 MHz rate-table entry for 50 MHz output; boards with different oscillator assumptions would need review. Sparse PLL tables and fixed clock-tree assumptions limit safe dynamic rate changes outside the modeled paths.

## Test Signals

Build tests should compile the driver with the Exynos7885 DT binding and catch clock-ID bound drift. Boot logs should show early TOP and PERI registration before platform probing of CORE and FSYS, with no unresolved parent warnings. `clk_summary` should show shared PLL/divider outputs feeding user muxes and expected gate enable counts.

Runtime tests should cover early timer/MCT operation, GPIO access, UART/SPI/I2C/USI/PWM/WDT peripherals, MMC card/eMMC/SDIO clocks, USB20/USB30 DRD clocks, and core fabric stability. Suspend/resume and unused-clock cleanup are important because the file uses critical and ignore-unused flags for essential core and GPIO-related paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos7885.c -->
