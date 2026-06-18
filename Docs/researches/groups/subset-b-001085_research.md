# subset-b-001085 Clock Driver Research

This grouped research report covers the subset-b-001085 source list. Each section is bounded with source-path markers so the reconciliation lane can split the report into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/sama5d3.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/sama5d3.c

Purpose: This file provides the early device-tree clock initialization for the AT91 SAMA5D3 Power Management Controller. It builds the SoC clock tree around slow/main clocks, PLLA, UTMI, master clocks, programmable clocks, system clocks, and peripheral clocks, then publishes the result through the common clock framework using `of_clk_add_hw_provider()`.

Important APIs, types, and functions: The central entry point is `sama5d3_pmc_setup()`, registered with `CLK_OF_DECLARE(..., "atmel,sama5d3-pmc", ...)` because timer clocks are needed before normal platform probing. Static tables define `mck_characteristics`, PLLA characteristics, `sama5d3_pcr_layout`, `sama5d3_systemck[]`, and `sama5d3_periphck[]`. The implementation depends on AT91 PMC helpers from `pmc.h`, including `pmc_data_allocate()`, `at91_clk_register_main_rc_osc()`, `at91_clk_register_main_osc()`, `at91_clk_register_sam9x5_main()`, `at91_clk_register_pll()`, `at91_clk_register_plldiv()`, `at91_clk_register_utmi()`, `at91_clk_register_master_pres()`, `at91_clk_register_master_div()`, `at91sam9x5_clk_register_usb()`, `at91sam9x5_clk_register_smd()`, `at91_clk_register_programmable()`, `at91_clk_register_system()`, and `at91_clk_register_sam9x5_peripheral()`.

Control flow: Setup first locates `slow_clk` and `main_xtal` in `clock-names`, obtains the PMC regmap with `device_node_to_regmap()`, allocates `pmc_data`, and then registers the clock tree in dependency order: RC oscillator, crystal oscillator, main clock mux, PLLA, PLLA divider, UTMI, master prescaler/divider, USB/SMD clocks, three programmable clocks, system clocks, and peripheral clocks. Each registration failure jumps to `err_free` and frees the `pmc_data`.

State and persistence behavior: Runtime state is held in registered `clk_hw` objects and the `pmc_data` arrays (`chws`, `shws`, `phws`, `pchws`). Hardware state lives in PMC registers accessed through regmap. `mck_lock` serializes master-clock register updates; peripheral PCR access uses shared `pmc_pcr_lock`. DDR-related clocks are marked `CLK_IS_CRITICAL` so the framework will not gate bootloader-enabled DDR paths without a Linux consumer.

Dependencies and integration points: It integrates with the DT binding IDs in `dt-bindings/clock/at91.h`, the syscon/regmap representation of the PMC node, and AT91 common PMC code. Consumers refer to exported clock indices through `of_clk_hw_pmc_get()`.

Risks and test signals: Risks are mostly table accuracy and clock ordering: wrong peripheral IDs, ranges, or parents can break UART, TCB, DDR, USB, and display consumers. Test signals include successful early boot, working TCB clocksource, stable DDR, visible `/sys/kernel/debug/clk/clk_summary` hierarchy, and DT consumers resolving all SAMA5D3 clock phandles without deferred or missing clock errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/sama5d3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/sama5d4.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/sama5d4.c

Purpose: This file initializes the SAMA5D4 PMC clock tree at early boot. It is similar to SAMA5D3 but adds an `h32mxck` branch for 32-bit peripheral clocks and splits peripherals into those clocked from `masterck_div` and those clocked from `h32mxck`.

Important APIs, types, and functions: `sama5d4_pmc_setup()` is the only functional entry point and is registered with `CLK_OF_DECLARE(..., "atmel,sama5d4-pmc", ...)`. Static data includes `mck_characteristics`, `plla_characteristics`, `sama5d4_pcr_layout`, `sama5d4_systemck[]`, `sama5d4_periph32ck[]`, and `sama5d4_periphck[]`. The code uses AT91 common helpers such as `at91_clk_register_main_rc_osc()`, `at91_clk_register_main_osc()`, `at91_clk_register_sam9x5_main()`, `at91_clk_register_pll()`, `at91_clk_register_plldiv()`, `at91_clk_register_utmi()`, `at91_clk_register_master_pres()`, `at91_clk_register_master_div()`, `at91_clk_register_h32mx()`, `at91sam9x5_clk_register_usb()`, `at91sam9x5_clk_register_smd()`, `at91_clk_register_programmable()`, `at91_clk_register_system()`, and `at91_clk_register_sam9x5_peripheral()`.

Control flow: The setup requires `slow_clk` and `main_xtal`, maps the PMC regmap, allocates `pmc_data`, registers main oscillators and PLLA, creates the master clock, derives `h32mxck`, registers USB/SMD and three programmable clocks, then iterates through system, normal peripheral, and 32-bit peripheral tables. Failures free `pmc_data` and abort before provider registration.

State and persistence behavior: Clock hardware state is represented by registered `clk_hw` objects stored in the `pmc_data` export arrays. Register state persists in the PMC and PCR registers. `mck_lock` protects master-clock updates and `pmc_pcr_lock` protects PCR programming. `ddrck` and `mpddr_clk` are critical to keep bootloader-enabled DDR clocks active.

Dependencies and integration points: The file depends on syscon regmap conversion of the PMC node, AT91 shared PMC implementations in `pmc.h`, and the AT91 clock binding IDs. It exports clocks through `of_clk_hw_pmc_get()` for DT consumers.

Risks and test signals: The key risks are wrong split between `masterck_div` and `h32mxck` peripherals, incorrect IDs in the static tables, and PLL/master limits that do not match silicon. Boot tests should verify DDR stability, early console, USB, MMC, timer operation, and that `clk_summary` shows expected parents for the 32-bit peripheral set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/sama5d4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/sama7d65.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/sama7d65.c

Purpose: This file describes and registers the SAMA7D65 PMC clock tree. It covers main clocks, nine PLL groups, ten master clocks, programmable clocks, system clocks, peripheral clocks, and generated clocks for a modern Microchip SoC.

Important APIs, types, and functions: `sama7d65_pmc_setup()` is registered via `CLK_OF_DECLARE(..., "microchip,sama7d65-pmc", ...)` for early availability. Static definitions include PLL component/type enums, PLL layouts (`pll_layout_frac`, `pll_layout_divpmc`, `pll_layout_divio`), PLL range/characteristic tables, the multi-dimensional `sama7d65_plls[][]` descriptor table, `sama7d65_mckx[]`, `sama7d65_systemck[]`, `sama7d65_periphck[]`, `sama7d65_gck[]`, master/program/PCR layouts, and the programmable mux table. Registration uses AT91/SAM9x60 helpers such as `sam9x60_clk_register_frac_pll()`, `sam9x60_clk_register_div_pll()`, `at91_clk_register_master_div()`, `at91_clk_sama7g5_register_master()`, `sam9x60_clk_register_usb()`, `at91_clk_register_programmable()`, `at91_clk_register_system()`, `at91_clk_register_sam9x5_peripheral()`, and `at91_clk_register_generated()`.

Control flow: The setup obtains `td_slck`, `md_slck`, and `main_xtal` as parent `clk_hw`s, maps the PMC regmap, allocates `pmc_data`, then registers the main RC/oscillator/main mux. It loops over all PLL descriptors and registers fractional PLLs before their divider outputs. It registers CPU `mck0`, then dynamic MCK1-MCK9 clocks by constructing per-clock mux tables that combine slow/main parents with descriptor-specific PLL parents. After USB and programmable clocks, it registers system clocks, peripheral clocks with MCK-specific parents, and generated clocks with generated-clock mux tables. Temporary mux tables are tracked in `alloc_mem` for cleanup on failure.

State and persistence behavior: Static descriptor tables hold registered `clk_hw` pointers after initialization, so setup is not purely const data. Registered hardware objects are persisted in `pmc_data` export arrays. Hardware register state lives in PMC registers accessed through regmap. `pmc_pll_lock`, `pmc_mck0_lock`, `pmc_mckX_lock`, and shared `pmc_pcr_lock` serialize PLL, master, and PCR operations. Critical flags preserve CPU, DDR, system, and timer-sensitive clock paths.

Dependencies and integration points: This file relies heavily on common AT91 PMC code for actual clock ops. DT consumers use IDs from `dt-bindings/clock/at91.h`; external parents are expected by name from the PMC DT node. The generated clocks feed peripherals such as GMAC, SDMMC, MCAN, audio, QSPI, LCD/DSI/LVDS, PIT, and timers.

Risks and test signals: Risks include descriptor/table drift from the SoC reference manual, invalid mux-table construction, wrong `eid` exports, unsafe PLL reparenting, and missing critical flags for clocks used by CPU, DDR, or clocksources. Useful tests are boot through early timers, clock provider registration without missing parents, exercising CPUfreq or PLL rate changes, validating generated clock rates for Ethernet/SDMMC/audio/CAN, and inspecting `clk_summary` for expected MCK and GCK parentage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/sama7d65.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/sama7g5.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/sama7g5.c

Purpose: This file provides the early PMC clock-tree definition for Microchip SAMA7G5. It registers the SoC's main clock, fractional/divider PLLs, MCK0-MCK4, UTMI, programmable clocks, system clocks, peripheral clocks, and generated clocks.

Important APIs, types, and functions: The entry point is `sama7g5_pmc_setup()`, registered by `CLK_OF_DECLARE(..., "microchip,sama7g5-pmc", ...)`. The file defines PLL ID/component/type enums, fractional and divider PLL layouts, PLL characteristics, `sama7g5_plls[][]`, `sama7g5_mckx[]`, `sama7g5_systemck[]`, `sama7g5_periphck[]`, `sama7g5_gck[]`, and register-layout metadata for MCK0, programmable clocks, and PCR. It delegates clock implementations to AT91/SAM9x60 helpers including `sam9x60_clk_register_frac_pll()`, `sam9x60_clk_register_div_pll()`, `at91_clk_register_master_div()`, `at91_clk_sama7g5_register_master()`, `at91_clk_sama7g5_register_utmi()`, `at91_clk_register_programmable()`, `at91_clk_register_system()`, `at91_clk_register_sam9x5_peripheral()`, and `at91_clk_register_generated()`.

Control flow: Setup resolves the three required external parents (`td_slck`, `md_slck`, `main_xtal`), obtains the PMC regmap, allocates `pmc_data`, registers the main RC oscillator, main oscillator, and main clock, then walks the PLL descriptor matrix to register each fractional PLL and its divider outputs. It creates CPU `mck0`, then builds and registers MCK1-MCK4 from slow/main and PLL parents. It registers UTMI, eight programmable clocks, system clocks backed by programmable clock hardware, peripheral clocks tied to MCK parents, and generated clocks with dynamically allocated mux tables.

State and persistence behavior: Registered hardware pointers are stored both in static descriptor entries and in `pmc_data` arrays. Hardware persists in PMC register state; temporary mux tables must remain allocated after registration and are only freed on error. Locks split register serialization by PLL, MCK0, MCKx, and PCR domains. Critical clock flags protect CPU, DDR, system, and other always-on paths.

Dependencies and integration points: The file depends on the common AT91 PMC implementation, syscon regmap, DT parent clocks, and `dt-bindings/clock/at91.h`. Consumers include camera, Ethernet, SDMMC, audio, CAN, timer, QSPI, PWM, USB, and generated-clock users in board DTs.

Risks and test signals: Risks include wrong generated-clock parent mux values, missing parent hardware before registration, memory lifetime mistakes in dynamic mux tables, and rate-change side effects on shared PLLs. Tests should cover early boot, timer stability, `clk_summary` inspection, peripheral probe success, generated-clock rate requests, and any CPU/DDR-related frequency changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/sama7g5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/sckc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/sckc.c

Purpose: This file implements AT91 slow clock controller support for multiple SoC generations. It registers internal slow RC oscillators, external 32 kHz oscillators, and slow-clock muxes used by timer and low-power domains.

Important APIs, types, and functions: Custom clock types include `clk_slow_osc`, `clk_sama5d4_slow_osc`, `clk_slow_rc_osc`, and `clk_sam9x5_slow`, all wrapping `struct clk_hw`. The major operations are `clk_slow_osc_prepare/unprepare/is_prepared`, `clk_slow_rc_osc_prepare/unprepare/is_prepared/recalc_rate/recalc_accuracy`, and `clk_sam9x5_slow_set_parent/get_parent`. Registration helpers include `at91_clk_register_slow_osc()`, `at91_clk_register_slow_rc_osc()`, `at91_clk_register_sam9x5_slow()`, plus matching unregister helpers. DT entry points are `of_at91sam9x5_sckc_setup()`, `of_sama5d3_sckc_setup()`, `of_sam9x60_sckc_setup()`, and `of_sama5d4_sckc_setup()`.

Control flow: The SAM9x5/SAMA5D3 path maps the SCKC register, registers slow RC, resolves the crystal and bypass mode from either modern DT or backward-compatible child nodes, registers slow oscillator, creates `slowck` mux, and publishes a simple provider. The SAM9X60 path exposes onecell outputs for `md_slck` and `td_slck`. The SAMA5D4 path uses fixed-rate RC plus a special slow oscillator that tracks preparation in software rather than controlling enable bits directly.

State and persistence behavior: Hardware state is in SCKC control bits (`cr_rcen`, `cr_osc32en`, `cr_osc32byp`, `cr_oscsel`). Preparation delays use `udelay()` before `SYSTEM_RUNNING` and `usleep_range()` afterward. SAMA5D4 maintains a `prepared` boolean because its oscillator handling differs. Registered providers are early boot state and are not devm-managed.

Dependencies and integration points: This integrates with DT clock providers, `of_iomap()`, common clock framework ops, and clock IDs from `dt-bindings/clock/at91.h`. It feeds later AT91 PMC drivers that require `slowck`, `md_slck`, or `td_slck`.

Risks and test signals: Risks include incorrect startup delays, backward-compatible DT parsing regressions, slow-clock parent switch timing, and leaks on partial registration failure. Tests should check early timer boot, low-power clock parent selection, clock accuracy/rate reporting, old and new DT layouts, and absence of missing slow-clock parent errors in SAMA5/SAM9/SAMA7 PMC setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/sckc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/axis/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/axis/Makefile

Purpose: This Makefile connects the Axis ARTPEC-6 clock controller implementation to the kernel build. It builds `clk-artpec6.o` when `CONFIG_MACH_ARTPEC6` is enabled.

Important APIs, types, and functions: There are no C APIs in this file. Its single functional line is `obj-$(CONFIG_MACH_ARTPEC6) += clk-artpec6.o`, under an SPDX header.

Control flow: Kbuild evaluates the configuration symbol and includes the object in the built-in or modular object list according to the symbol value. Because the driver itself uses `builtin_platform_driver()` and `CLK_OF_DECLARE_DRIVER()`, this build inclusion is what makes both early and platform-driver phases available for ARTPEC-6 systems.

State and persistence behavior: The file has no runtime state. Its persistent behavior is build graph selection.

Dependencies and integration points: It depends on `CONFIG_MACH_ARTPEC6`, which is expected to be selected for Axis ARTPEC-6 platforms. The object implements the DT-compatible `"axis,artpec6-clkctrl"` provider.

Risks and test signals: The main risk is build omission: without this line or with a wrong config symbol, ARTPEC-6 DT clock consumers cannot resolve their clocks. Test signals are successful ARTPEC-6 builds, `clk-artpec6.o` present in the link, and runtime registration of the ARTPEC-6 clock provider.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/axis/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/axis/clk-artpec6.c -->
# sources/distributed-fs/ceph-client/drivers/clk/axis/clk-artpec6.c

Purpose: This file implements ARTPEC-6 clock initialization. It performs an early fixed-clock setup needed before all platform devices probe, then completes the clock table in a built-in platform driver.

Important APIs, types, and functions: `artpec6_clkctrl_drvdata` stores the clock table, syscon base, onecell provider data, and I2S mux lock. `of_artpec6_clkctrl_setup()` is registered with `CLK_OF_DECLARE_DRIVER()` and initializes CPU, CPU peripheral, UART, SPI, debug, and onecell provider state. `artpec6_clkctrl_probe()` completes clocks for NAND, Ethernet, DMA, PTP, SD, I2S, I2C, timer, and fractional-divider input. It uses `clk_register_fixed_factor()`, `clk_register_fixed_rate()`, `clk_register_mux()`, and `of_clk_add_provider()`.

Control flow: Early setup requires the `sys_refclk` parent, allocates a global `clkdata`, initializes every table slot to `ERR_PTR(-EPROBE_DEFER)`, maps the syscon, reads strap-selected PLL mode from the syscon register, derives CPU PLL factors, registers early clocks, and publishes the onecell provider. Later probe reuses the global `clkdata`, resolves optional I2S parents, initializes the I2S mux lock, registers remaining fixed and mux clocks, optionally programs the I2S mux register at offset `0x14`, and reports non-defer registration failures.

State and persistence behavior: The global `clkdata` persists across early declaration and platform probe. Hardware strap state determines CPU rate factors and is read only once. I2S mux selection may be locked to internal or external parent by writing syscon bits when only one parent is present.

Dependencies and integration points: It depends on Axis clock DT bindings, `sys_refclk`, optional `i2s_refclk` and fractional clocks, and the common clock onecell provider interface. The AMBA APB clock comment explains why some clocks must be available early.

Risks and test signals: Risks include global state assumptions, `BUG_ON()` if syscon mapping fails, optional I2S parent handling, and unregistered clocks left as `-EPROBE_DEFER`. Tests should verify ARTPEC-6 boot, UART/SPI early clocks, I2S parent selection, provider indices from `axis,artpec6-clkctrl.h`, and no unexpected clock registration errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/axis/clk-artpec6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/axs10x/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/axs10x/Makefile

Purpose: This Makefile always builds the AXS10x I2S PLL and generic PLL clock drivers for this directory when the parent directory is included by Kbuild.

Important APIs, types, and functions: The functional lines are `obj-y += i2s_pll_clock.o` and `obj-y += pll_clock.o`. There are no runtime APIs.

Control flow: Kbuild includes both objects unconditionally within the AXS10x clock directory. The C files themselves decide their DT compatibility and platform-driver behavior.

State and persistence behavior: The file has no runtime state. Its persistent effect is to include both clock providers in the kernel image for the relevant build.

Dependencies and integration points: It integrates with the broader clock-driver Makefile that descends into `drivers/clk/axs10x`. The resulting drivers bind to Synopsys AXS10x PLL clock nodes.

Risks and test signals: The risk is build coverage rather than runtime logic. Test signals include successful allmodconfig/AXS10x builds and presence of both driver objects so ARC, PGU, and I2S PLL DT nodes can bind or initialize.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/axs10x/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/axs10x/i2s_pll_clock.c -->
# sources/distributed-fs/ceph-client/drivers/clk/axs10x/i2s_pll_clock.c

Purpose: This platform driver exposes the Synopsys AXS10x I2S PLL as a common-clock provider. It supports a fixed table of audio-related output rates for two supported parent oscillator rates.

Important APIs, types, and functions: `i2s_pll_cfg` stores output rate and register programming values for IDIV, FBDIV, ODIV0, and ODIV1. `i2s_pll_clk` stores MMIO base, `clk_hw`, and device pointer. Clock ops are `i2s_pll_recalc_rate()`, `i2s_pll_determine_rate()`, and `i2s_pll_set_rate()`. Probe is `i2s_pll_clk_probe()`, remove is `i2s_pll_clk_remove()`, and matching uses `"snps,axs10x-i2s-pll-clock"`.

Control flow: Probe allocates state, maps the PLL register resource, initializes one-parent `clk_init_data` using the DT node name, registers the clock with `devm_clk_register()`, and adds a simple OF provider. Rate determination selects a configuration table based on `best_parent_rate` (`27000000` or `28224000`) and accepts only exact table rates. Setting a rate writes all four PLL divider registers from the matching table entry.

State and persistence behavior: Runtime state is minimal and devm-managed. Hardware state persists in the PLL divider registers. The driver does not poll for lock or validate hardware status after writes; it assumes table entries are safe.

Dependencies and integration points: It depends on MMIO resources, a single parent clock in DT, and the common clock framework. It is a module-capable platform driver and exports the PLL clock through a simple provider.

Risks and test signals: Risks include unsupported parent rates, exact-rate matching that rejects near rates, no lock/status check, and recalc division by malformed zero register values if hardware is uninitialized. Test signals include successful DT binding, accepted common audio sample rates, correct recalc rate after programming, and audible/stable I2S operation at all table entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/axs10x/i2s_pll_clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/axs10x/pll_clock.c -->
# sources/distributed-fs/ceph-client/drivers/clk/axs10x/pll_clock.c

Purpose: This file implements generic Synopsys AXS10x PLL clocks, covering an early ARC PLL provider and a built-in platform driver for the PGU PLL.

Important APIs, types, and functions: `axs10x_pll_cfg` contains allowed rates and divider triplets. `axs10x_pll_clk` stores `clk_hw`, divider MMIO base, lock/status MMIO base, selected config table, and device pointer. Helper macros encode and decode LOW/HIGH/EDGE/BYPASS/NOUPDATE divider fields. Clock ops are `axs10x_pll_recalc_rate()`, `axs10x_pll_determine_rate()`, and `axs10x_pll_set_rate()`. DT setup/probe paths are `of_axs10x_pll_clk_setup()` for `"snps,axs10x-arc-pll-clock"` and `axs10x_pll_clk_probe()` for `"snps,axs10x-pgu-pll-clock"`.

Control flow: Recalc reads IDIV, FBDIV, and ODIV registers, decodes effective divisors, and computes `(parent * fbdiv) / (idiv * odiv)`. Determine-rate chooses the closest configured rate. Set-rate writes encoded IDIV/FBDIV/ODIV values, delays up to `PLL_MAX_LOCK_TIME`, then checks `PLL_LOCK` and `PLL_ERROR`. The early ARC path manually maps resources and registers a provider; the platform path uses devm-managed resources and match data.

State and persistence behavior: Hardware state is in PLL divider and lock/status registers. The early path has manual cleanup on failure, while the platform path is devm-managed. Rate state is table-driven and not persisted in software outside the registered clock object.

Dependencies and integration points: It depends on DT resources for divider and lock registers, one parent clock, common clock ops, and OF match data for the PGU configuration. ARC PLL is registered early with `CLK_OF_DECLARE`; PGU uses `builtin_platform_driver()`.

Risks and test signals: Risks include lock polling via fixed delay rather than a true timeout loop, exact configured rates only, divider encoding mistakes, and inconsistent cleanup between early and platform paths. Tests should verify ARC early clock availability, PGU pixel rates, timeout/error handling, and recalc consistency after set-rate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/axs10x/pll_clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/Kconfig

Purpose: This Kconfig file defines build-time options for Broadcom clock drivers in the BCM clock directory, including BCM2711 DVP, BCM2835 CPRMAN, BCM63xx, Kona, iProc, Cygnus, Hurricane 2, Northstar, Northstar 2, Stingray, and Raspberry Pi firmware clocks.

Important APIs, types, and functions: There are no C symbols here, but the config symbols are integration APIs for the build: `CLK_BCM2711_DVP`, `CLK_BCM2835`, `CLK_BCM_63XX`, `CLK_BCM_63XX_GATE`, `CLK_BCM63268_TIMER`, `CLK_BCM_KONA`, `COMMON_CLK_IPROC`, `CLK_BCM_CYGNUS`, `CLK_BCM_HR2`, `CLK_BCM_NSP`, `CLK_BCM_NS2`, `CLK_BCM_SR`, and `CLK_RASPBERRYPI`.

Control flow: Kconfig gates driver visibility and selection. Some symbols default on for their architecture, some allow `COMPILE_TEST`, and several select `COMMON_CLK_IPROC` or reset-controller support. `CLK_RASPBERRYPI` depends on firmware support or compile-test without firmware.

State and persistence behavior: Runtime state is unaffected directly. The persistent effect is the generated `.config`, which determines which objects the BCM Makefile compiles.

Dependencies and integration points: This file links architecture symbols (`ARCH_BCM2835`, `ARCH_BRCMSTB`, `BMIPS_GENERIC`, `ARCH_BCM_MOBILE`, `ARCH_BCM_CYGNUS`, `ARCH_BCM_HR2`, `ARCH_BCM_5301X`, `ARCH_BCM_NSP`, `ARCH_BCM_IPROC`, `ARCH_BCMBCA`) to clock-provider implementations and reset-controller dependencies.

Risks and test signals: Risks include missing `select` dependencies, overly broad defaults, and compile-test gaps. Test signals include allyesconfig/allmodconfig builds, architecture defconfigs selecting expected clock drivers, and no unresolved symbols when reset or iProc helper drivers are selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/Makefile

Purpose: This Makefile maps Broadcom clock Kconfig symbols to object files in the BCM clock driver directory.

Important APIs, types, and functions: The object mappings include BCM63xx gate/timer/core drivers, Kona core/setup plus BCM281xx and BCM21664 tables, iProc ARM PLL/PLL/ASIU helpers, BCM2711 DVP, BCM2835 CPRMAN and AUX drivers, Raspberry Pi firmware clocks, BCM53573 ILP, and iProc SoC-specific tables for Cygnus, HR2, NSP, NS2, and Stingray.

Control flow: Kbuild evaluates each `obj-$(CONFIG_...)` line and includes matching objects. `CONFIG_COMMON_CLK_IPROC` pulls the shared iProc helpers; SoC-specific configs add their descriptor files.

State and persistence behavior: The file has no runtime state. It persists build graph decisions from Kconfig to object linkage.

Dependencies and integration points: It depends on symbols defined in `Kconfig` and on helper/source files in the same directory. Several descriptors only make sense when their helper object is also selected.

Risks and test signals: Risks include omitting shared helper objects, compiling table files without their helpers, or using wrong config symbols. Test signals are successful Broadcom defconfig builds and linker coverage for each enabled DT compatible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm21664.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm21664.c

Purpose: This file declares Kona-style CCU clock data for the Broadcom BCM21664 mobile SoC. It maps DT-compatible CCU nodes to clock tables for root, always-on, master, and slave clock control units.

Important APIs, types, and functions: The file is almost entirely descriptor data using `peri_clk_data`, `ccu_data`, and macros from `clk-kona.h`, including `KONA_CCU_COMMON`, `KONA_CLK`, `HW_SW_GATE`, `HYST`, `CLOCKS`, `SELECTOR`, `DIVIDER`, `FRAC_DIVIDER`, `TRIGGER`, `CCU_LVM_EN`, and `CCU_POLICY_CTL`. Setup callbacks are `kona_dt_root_ccu_setup()`, `kona_dt_aon_ccu_setup()`, `kona_dt_master_ccu_setup()`, and `kona_dt_slave_ccu_setup()`, all calling `kona_dt_ccu_setup()`.

Control flow: At boot, each `CLK_OF_DECLARE()` compatible invokes the corresponding setup function. The common Kona setup code consumes the static `ccu_data`, maps registers, creates clocks for the indexed `kona_clks` array, and registers the onecell provider.

State and persistence behavior: This file has no custom mutable runtime state. Runtime clock state is managed by the Kona common driver through hardware gate, selector, divider, trigger, hysteresis, and policy-control registers. Some sleep-clock entries are marked with "Verify" comments, indicating known uncertainty in parent definitions.

Dependencies and integration points: It depends on `clk-kona.h`, BCM21664 DT clock binding indices, and DT compatible strings from those bindings. It provides clocks for SDIO, UART, BSC/I2C, hub timer, and fractional root clock consumers.

Risks and test signals: Risks are descriptor accuracy: wrong offsets, trigger bits, parent names, or clock IDs can silently produce bad peripheral clocks. Test signals include successful BCM21664 boot, SDIO/UART/I2C operation, hub timer function, and `clk_summary` showing expected Kona CCU clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm21664.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm2711-dvp.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm2711-dvp.c

Purpose: This platform driver exposes the BCM2711 DVP controller's two HDMI 108 MHz gated clocks and six reset lines.

Important APIs, types, and functions: `clk_dvp` stores a onecell clock array and `reset_simple_data`. `clk_dvp_probe()` maps the controller registers, registers a reset controller with `reset_simple_ops`, registers two gate clocks (`hdmi0-108MHz`, `hdmi1-108MHz`) using `clk_hw_register_gate_parent_data()`, and publishes an OF clock provider. `clk_dvp_remove()` unregisters the gate clocks.

Control flow: Probe allocates state, maps MMIO, sets the reset controller base at `DVP_HT_RPI_SW_INIT`, registers the reset controller, creates the two gate clocks backed by `DVP_HT_RPI_MISC_CONFIG` bits 3 and 4 with `CLK_GATE_SET_TO_DISABLE`, and adds the onecell provider. Failure after clock registration unwinds the created gates.

State and persistence behavior: The gate and reset state lives in DVP MMIO registers. A single spinlock in `reset_simple_data` protects both reset and gate register access. Driver allocations are devm-managed except explicit gate unregisters.

Dependencies and integration points: It depends on the reset controller framework, common clock framework, one parent clock from DT index 0, and compatible `"brcm,brcm2711-dvp"`. Consumers are HDMI/DVP-related drivers needing clock and reset control.

Risks and test signals: Risks include shared lock assumptions, gate polarity (`SET_TO_DISABLE`), missing provider cleanup in remove, and reset count/index mismatch. Tests should verify HDMI clock enables, reset assertion/deassertion, provider indices, and module unload/reprobe if built modular.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm2711-dvp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm281xx.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm281xx.c

Purpose: This file declares Kona-style clock-control-unit data for Broadcom BCM281xx SoCs. It covers root, always-on, hub, master, and slave CCUs and their peripheral clocks.

Important APIs, types, and functions: It uses `peri_clk_data`, `ccu_data`, and `clk-kona.h` macros such as `KONA_CCU_COMMON`, `KONA_CLK`, `HW_SW_GATE`, `CLOCKS`, `SELECTOR`, `DIVIDER`, `FRAC_DIVIDER`, `FIXED_DIVIDER`, and `TRIGGER`. Setup callbacks `kona_dt_root_ccu_setup()`, `kona_dt_aon_ccu_setup()`, `kona_dt_hub_ccu_setup()`, `kona_dt_master_ccu_setup()`, and `kona_dt_slave_ccu_setup()` pass static descriptors to `kona_dt_ccu_setup()`.

Control flow: `CLK_OF_DECLARE()` binds BCM281xx CCU DT-compatible strings to the setup callbacks. The common Kona code interprets each descriptor, registers clocks at the binding-defined indices, and exposes the clock provider.

State and persistence behavior: No custom state is allocated here. Hardware state is controlled through the described gate, selector, divider, trigger, and fractional-divider registers. Critical persistence is table data matching the SoC's register layout.

Dependencies and integration points: It depends on BCM281xx binding IDs, Kona common clock support, and DT parent clock names like `ref_crystal`, `var_52m`, `ref_96m`, `var_156m`, and `bbl_32k`. It feeds SDIO, USB/HSIC, UART, SSP, BSC, PWM, PMU BSC, timer, and thermal-monitor clocks.

Risks and test signals: Risks are off-by-one binding indices, wrong shared register offsets, parent-name drift, and inaccurate fixed/pre-divider definitions. Test signals include peripheral probe success, usable SDIO/USB/UART/I2C/PWM clocks, and matching rates in `clk_summary` for divider-driven clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm281xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm2835-aux.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm2835-aux.c

Purpose: This driver exposes the BCM2835 auxiliary peripheral gate clocks for AUX UART, SPI1, and SPI2.

Important APIs, types, and functions: The only entry point is `bcm2835_aux_clk_probe()`. It obtains the parent clock with `devm_clk_get()`, maps the AUX register block, allocates `clk_hw_onecell_data`, and registers three `clk_hw_register_gate()` gates at `BCM2835_AUXENB` bits 0, 1, and 2. The compatible is `"brcm,bcm2835-aux"`.

Control flow: Probe resolves the parent clock name, maps MMIO, allocates onecell data sized by `BCM2835_AUX_CLOCK_COUNT`, registers the gate clocks, and adds the onecell provider. The driver is built in with `builtin_platform_driver()`.

State and persistence behavior: Gate state persists in the AUX enable register. Allocated onecell state is devm-managed, but the individual gates are registered with the non-devm gate API and there is no remove path in this built-in driver.

Dependencies and integration points: It depends on `dt-bindings/clock/bcm2835-aux.h`, a parent clock from DT, and common clock onecell consumers. The clocks gate the mini UART and auxiliary SPI blocks.

Risks and test signals: Risks include partial registration errors not checked per gate, no explicit cleanup, and parent clock lookup failure blocking all AUX clocks. Tests should validate AUX UART/SPI operation, provider indices, and correct gating in `clk_summary`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm2835-aux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm2835.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm2835.c

Purpose: This file implements the BCM2835/BCM2711 CPRMAN clock controller. It exposes PLLs, PLL channels/dividers, muxed peripheral clocks, VPU clocks, MASH/fractional dividers, and a small gate clock through a onecell common-clock provider.

Important APIs, types, and functions: Core state is `bcm2835_cprman`, holding the device, MMIO base, global register spinlock, SoC mask, real parent names, and `clk_hw_onecell_data`. Descriptor types include `bcm2835_pll_data`, `bcm2835_pll_divider_data`, `bcm2835_clock_data`, `bcm2835_gate_data`, and `bcm2835_clk_desc`. Clock families have separate ops: `bcm2835_pll_clk_ops`, `bcm2835_pll_divider_clk_ops`, `bcm2835_clock_clk_ops`, and `bcm2835_vpu_clock_clk_ops`. Registration helpers are `bcm2835_register_pll()`, `bcm2835_register_pll_divider()`, `bcm2835_register_clock()`, and `bcm2835_register_gate()`. The platform entry point is `bcm2835_clk_probe()`.

Control flow: Probe gets platform match data to distinguish BCM2835 and BCM2711, allocates onecell state sized to `clk_desc_array`, maps CPRMAN registers, fills external parent names from DT, verifies the oscillator parent, and iterates through `clk_desc_array`, registering descriptors whose SoC mask matches. It then permanently prepares the SDRAM clock parent via `bcm2835_mark_sdc_parent_critical()` before publishing `of_clk_hw_onecell_get()`.

Rate/control behavior: PLL rate selection clamps requested rates, computes integer and fractional NDIV values, optionally uses feedback predivision on BCM2835, writes analog registers in hardware-required order, controls oscillator reference enable masks, and waits for lock on prepare. PLL divider ops enable/disable channels via A2W disable bits and CM hold/load bits. Generic clocks choose fixed-point dividers, support MASH minimum divider constraints, optionally propagate rate requests to selected parents, avoid PLLC parents unless already selected because firmware may retune PLLC, and set mux source/divider registers under `regs_lock`. VPU clocks cannot be disabled and therefore use special ops without prepare/unprepare.

State and persistence behavior: Hardware state persists in CPRMAN CM and A2W registers. `CM_PASSWORD` is ORed into writes. `regs_lock` serializes multi-register updates and shared gate/divider access. Software state is mostly immutable descriptors plus registered `clk_hw` instances. Debugfs regsets expose key registers for PLLs, dividers, and clocks.

Dependencies and integration points: The driver depends on `dt-bindings/clock/bcm2835.h`, common clock APIs, DT parent clocks including oscillator and optional DSI PHY clocks, and platform compatibles `"brcm,bcm2835-cprman"` and `"brcm,bcm2711-cprman"`. Consumers include VPU, H264, ISP, V3D, camera, DPI/DSI, EMMC, GP clocks, PCM, PWM, UART, VEC, and SDRAM recalibration paths.

Risks and test signals: Risks are high because this driver programs PLL analog state, handles SoC differences, and shares clocks with firmware. Specific risks include incorrect predivider behavior on BCM2711, lock timeouts, unsafe parent propagation, fractional divider jitter, clock-critical flag mistakes, and missing DSI parents on older DTs. Test signals include successful boot on BCM2835 and BCM2711, stable VPU/SDRAM, display and camera clocks, EMMC/EMMC2 rates, audio PCM/PWM jitter behavior, `clk_summary` consistency, debugfs register dumps, and timeout/error logging under bad PLL conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm2835.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm53573-ilp.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm53573-ilp.c

Purpose: This early clock provider implements the BCM53573 ILP low-power clock, including enable/disable programming and rate measurement from PMU registers.

Important APIs, types, and functions: `bcm53573_ilp` wraps `clk_hw` and a parent syscon `regmap`. Clock ops are `bcm53573_ilp_enable()`, `bcm53573_ilp_disable()`, and `bcm53573_ilp_recalc_rate()`. Initialization is `bcm53573_ilp_init()`, registered with `CLK_OF_DECLARE(..., "brcm,bcm53573-ilp", ...)`.

Control flow: Init allocates the clock object, resolves its parent name, gets the parent node's syscon regmap, registers the clock, and adds a simple OF provider. Enable writes fixed PMU values to `PMU_SLOW_CLK_PERIOD` and offset `0x674`; disable clears them. Recalc enables measurement via `PMU_XTAL_FREQ_RATIO`, samples up to 20 changing ratio values or gives up after repeated identical reads, disables measurement, averages the ratio, and returns `parent_rate * 4 / avg`.

State and persistence behavior: Hardware state is in PMU registers. Software keeps only the regmap and clock object. Measurement is transient and disabled afterward to save power.

Dependencies and integration points: It depends on syscon/regmap for the parent PMU, a parent clock in DT, and early registration because architecture code needs the clock before the full device model.

Risks and test signals: Risks include division by zero if measurement returns no usable sample, magic register value fragility, busy-loop measurement latency, and inaccurate averages under unstable hardware. Test signals include early boot success on BCM53573, plausible ILP rate reporting, enable/disable register effects, and no PMU measurement timeout-like stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm53573-ilp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm63268-timer.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm63268-timer.c

Purpose: This built-in platform driver provides BCM63268 timer block clocks and resets from a shared register.

Important APIs, types, and functions: `bcm63268_tclkrst_hw` contains the MMIO base, spinlock, reset controller, and onecell clock data. `bcm63268_timer_clocks[]` maps clock names to bit IDs. Reset operations are implemented by `bcm63268_timer_reset_update()`, assert/deassert/reset/status helpers, and `bcm63268_timer_reset_ops`. Probe is `bcm63268_tclk_probe()`.

Control flow: Probe computes onecell size from the maximum clock bit, allocates state, initializes all clock slots to `ERR_PTR(-ENODEV)`, maps the register, registers one gate clock per table entry using `devm_clk_hw_register_gate()` with `CLK_GATE_BIG_ENDIAN`, publishes the clock provider, and registers a reset controller using the same register and bit convention.

State and persistence behavior: Clock and reset state share a big-endian hardware register. The spinlock protects read-modify-write sequences. Reset assertion clears a bit, deassertion sets it, and full reset pulses the bit with two sleep intervals to let hardware settle.

Dependencies and integration points: It depends on `dt-bindings/clock/bcm63268-clock.h`, common clock, reset-controller framework, and compatible `"brcm,bcm63268-timer-clocks"`. Consumers are Ethernet PHY, DSL, wake-on, FAP PLL, UTO, and USB reference blocks.

Risks and test signals: Risks include shared clock/reset polarity confusion, reset ID count not explicitly set in `rcdev`, big-endian gate assumptions, and using one register for multiple semantics. Tests should verify each gate bit, reset pulse/status behavior, provider indices, and operation of timer/PHY/USB users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm63268-timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm63xx-gate.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm63xx-gate.c

Purpose: This driver provides simple big-endian gate clock providers for multiple BCM63xx MIPS DSL SoCs and related UBUS clock blocks.

Important APIs, types, and functions: `clk_bcm63xx_table_entry` describes a gate name, bit, and flags. `clk_bcm63xx_hw` stores MMIO, lock, and onecell data. Static tables cover BCM3368, BCM6318, BCM6318 UBUS, BCM6328, BCM6358, BCM6362, BCM6368, and BCM63268 clocks. `clk_bcm63xx_probe()` registers gates from match-data tables; `clk_bcm63xx_remove()` unregisters them.

Control flow: Probe gets the table from OF match data, computes `maxbit`, allocates onecell data with missing slots as `ERR_PTR(-ENODEV)`, maps the gate register, registers each gate with `clk_hw_register_gate()` and `CLK_GATE_BIG_ENDIAN`, stores it at `hws[bit]`, and adds an OF provider. On failure it unregisters any gates already created. Remove deletes the provider and unregisters all valid gates.

State and persistence behavior: Runtime state is the MMIO register and registered gate objects. A spinlock serializes gate bit updates. Several CPU, SDR, and UBUS clocks are marked `CLK_IS_CRITICAL` to avoid disabling essential infrastructure.

Dependencies and integration points: It depends on many BCM63xx DT binding headers for bit IDs, the common clock framework, platform devices, and compatibles such as `"brcm,bcm6318-clocks"` and `"brcm,bcm63268-clocks"`. It feeds BMIPS platform peripheral and bus clocks.

Risks and test signals: Risks include wrong bit IDs, missing critical flags, big-endian access assumptions, sparse onecell arrays, and incomplete cleanup on provider-add failure. Test signals include boot on each matched SoC, active CPU/bus critical clocks, peripheral gate control, and DT consumers resolving expected indices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm63xx-gate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm63xx.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm63xx.c

Purpose: This small file registers the BCM63138 ARM PLL using the shared iProc ARM PLL helper.

Important APIs, types, and functions: The only function is `bcm63138_armpll_init()`, which calls `iproc_armpll_setup(node)`. It is registered with `CLK_OF_DECLARE(..., "brcm,bcm63138-armpll", ...)`.

Control flow: During early OF clock initialization, a matching DT node invokes the wrapper, and the shared iProc implementation maps registers, registers a `clk_hw`, and exposes it as a simple provider.

State and persistence behavior: This file has no local runtime state. State is managed by `clk-iproc-armpll.c` and hardware ARM PLL registers.

Dependencies and integration points: It depends on `clk-iproc.h` and `CONFIG_COMMON_CLK_IPROC` build inclusion. It bridges the BCM63138 DT compatible to the generic iProc ARM PLL code.

Risks and test signals: Risks are limited to compatible matching and helper availability. Test signals include early clock provider registration for `"brcm,bcm63138-armpll"` and plausible ARM PLL rate reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm63xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-cygnus.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-cygnus.c

Purpose: This file declares iProc clock-controller descriptors for the Broadcom Cygnus SoC, including ARM PLL, GENPLL, LCPLL0, MIPI PLL, ASIU clocks, and audio PLL.

Important APIs, types, and functions: It uses descriptor types from `clk-iproc.h`: `iproc_pll_ctrl`, `iproc_clk_ctrl`, `iproc_pll_vco_param`, `iproc_asiu_div`, and `iproc_asiu_gate`. Helper macros define register fields for reset, AON, software control, dividers, status, VCO, enable, ASIU gate, and digital filter fields. Setup callbacks call `iproc_armpll_setup()`, `iproc_pll_clk_setup()`, or `iproc_asiu_setup()` for their respective DT compatibles.

Control flow: Each `CLK_OF_DECLARE()` compatible invokes a setup function with a static descriptor set. PLL setup passes PLL control metadata, optional VCO parameter tables, and channel descriptor arrays. ASIU setup passes divider and gate tables for keypad, ADC, and PWM clocks.

State and persistence behavior: This file is descriptor-only; runtime state and register access are handled by iProc helper code. Descriptor flags encode persistent hardware behavior such as AON, software configuration needs, fractional NDIV support, read-back requirements, reset polarity, and calculated parameters.

Dependencies and integration points: It depends on `dt-bindings/clock/bcm-cygnus.h`, `clk-iproc.h`, and DT compatibles for Cygnus PLL/ASIU nodes. The clocks feed AXI, Ethernet, CAN, PCIe/DDR/SDIO/USB, LCD/V3D, keypad/ADC/PWM, and audio channels.

Risks and test signals: Risks include descriptor field errors, mismatched channel indices, VCO table mistakes, and flags that do not match hardware behavior. Test signals include successful Cygnus boot, correct rates for GENPLL/LCPLL/MIPI/audio outputs, ASIU gate/divider operation, and no PLL lock or read-back errors from shared helper code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-cygnus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-hr2.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-hr2.c

Purpose: This wrapper registers Hurricane 2 ARM PLL support through the shared iProc ARM PLL helper.

Important APIs, types, and functions: `hr2_armpll_init()` calls `iproc_armpll_setup(node)`. It is registered by `CLK_OF_DECLARE(..., "brcm,hr2-armpll", ...)`.

Control flow: Early OF initialization matches the HR2 compatible and delegates all setup to the common iProc ARM PLL implementation.

State and persistence behavior: There is no local state. Hardware mapping, rate calculation state, and provider registration are handled in `clk-iproc-armpll.c`.

Dependencies and integration points: It depends on `clk-iproc.h`, the common iProc helper object, and the HR2 DT compatible. It provides the ARM PLL clock for Broadcom Hurricane 2 platforms.

Risks and test signals: Risks are limited to missing helper build coverage or compatible mismatch. Test signals include provider registration and correct ARM clock rate calculation on HR2 hardware or DT tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-hr2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-iproc-armpll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-iproc-armpll.c

Purpose: This shared helper implements rate reporting for iProc ARM PLLs and registers them as early OF clock providers for SoC wrapper files.

Important APIs, types, and functions: `iproc_arm_pll` stores `clk_hw`, MMIO base, and cached rate. Internal helpers `__get_fid()`, `__get_mdiv()`, and `__get_ndiv()` decode active frequency policy, post divider, and integer/fractional multiplier from hardware registers. `iproc_arm_pll_recalc_rate()` computes the clock rate. Public setup is `iproc_armpll_setup()`.

Control flow: Setup allocates state, maps the DT register resource, builds a single-parent clock from the DT parent if present, registers the hardware clock, and adds a simple provider. Recalc checks bypass mode, verifies PLL lock, decodes PDIV/NDIV/MDIV according to active frequency ID, and computes `((ndiv * parent_rate) >> 20) / pdiv / mdiv`.

State and persistence behavior: The only software state is the registered clock and last rate. Hardware state includes policy, debug active frequency, PLL control, fractional offset, lock, and divider registers. `BUG_ON()` is used if decoded policy exceeds the maximum, so invalid hardware state can become fatal.

Dependencies and integration points: It depends on SoC wrapper files that call `iproc_armpll_setup()` for specific compatibles, common clock framework APIs, and OF MMIO mapping. It is selected through `COMMON_CLK_IPROC`.

Risks and test signals: Risks include fatal `BUG_ON()` on bad policy, returning 0 if unlocked or invalid divider, handling offset mode correctly, and matching hardware bitfields across SoCs. Tests should check rate reporting under each FID path, bypass mode, locked/unlocked states, and wrapper compatibles for Cygnus, HR2, and BCM63138.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-iproc-armpll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-iproc-asiu.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-iproc-asiu.c

Purpose: This shared helper implements iProc ASIU gate and divider clocks, registering a onecell provider from SoC-specific divider/gate descriptor arrays.

Important APIs, types, and functions: `iproc_asiu_clk` stores a `clk_hw`, name, parent ASIU object, cached rate, and per-clock `iproc_asiu_div`/`iproc_asiu_gate` descriptors. `iproc_asiu` stores divider/gate MMIO bases, onecell data, and the clock array. Clock ops are `iproc_asiu_clk_enable()`, `iproc_asiu_clk_disable()`, `iproc_asiu_clk_recalc_rate()`, `iproc_asiu_clk_determine_rate()`, and `iproc_asiu_clk_set_rate()`. Public setup is `iproc_asiu_setup()`.

Control flow: Setup validates descriptor pointers, allocates onecell data and clock storage, maps divider and gate resources, then loops over `clock-output-names`, registering one clock per descriptor with a common parent. Enable/disable toggles gate bits unless the descriptor marks the gate offset invalid. Recalc reads the divider enable bit and high/low divider fields; if disabled, the clock follows the parent rate. Set-rate either disables the divider for parent rate or computes a rounded divider and writes high/low fields.

State and persistence behavior: Hardware state is split between divider and gate register spaces. The driver has no locking around read-modify-write sequences, so it relies on early/static setup and limited concurrent mutation. Software state persists in allocated arrays referenced by registered clocks.

Dependencies and integration points: It depends on `clk-iproc.h` descriptor definitions, common clock framework, OF `clock-output-names`, one parent clock, and SoC descriptor files such as `clk-cygnus.c`.

Risks and test signals: Risks include no register lock, odd-divider rounding because both high and low fields are derived from `div >> 1`, invalid gate offsets for always-on clocks, and cleanup correctness on partial registration. Tests should verify enable/disable bits, exact and rounded rates, parent-rate passthrough, ASIU clock-output-name ordering, and cleanup paths under registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-iproc-asiu.c -->
