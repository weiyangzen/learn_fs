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
