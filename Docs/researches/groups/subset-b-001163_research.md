# sources/distributed-fs/ceph-client/drivers/clk/samsung subset-b-001163 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-artpec8.c -->
# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-artpec8.c

## Purpose

`clk-artpec8.c` is the ARTPEC-8 SoC clock controller description for the Linux common clock framework using Samsung's shared clock registration helpers. It defines the register offsets, parent name arrays, PLLs, muxes, dividers, gates, and `samsung_cmu_info` descriptors for ARTPEC-8 CMU domains, then binds those descriptors to device-tree compatible strings. The file is almost entirely declarative clock-topology data, with minimal procedural code for early IMEM registration and platform-driver probing.

The covered domains are `CMU_CMU`, `CMU_BUS`, `CMU_CORE`, `CMU_CPUCL`, `CMU_FSYS`, `CMU_IMEM`, and `CMU_PERI`. `CMU_CMU` is the root-like shared clock domain with audio/shared PLLs and many cross-domain exported `dout_clkcmu_*` clocks. Domain CMUs then select those exported clocks through user muxes and expose peripheral-facing gates.

## Important APIs, types, and functions

- `samsung_pll_clock`, `samsung_fixed_factor_clock`, `samsung_fixed_rate_clock`, `samsung_mux_clock`, `samsung_div_clock`, and `samsung_gate_clock` arrays describe the actual common clock framework hardware clocks through Samsung macros such as `PLL()`, `FFACTOR()`, `FRATE()`, `MUX()`, `nMUX()`, `MUX_F()`, `DIV()`, `DIV_F()`, and `GATE()`.
- `struct samsung_cmu_info` instances (`cmu_cmu_info`, `cmu_bus_info`, `cmu_core_info`, `cmu_cpucl_info`, `cmu_fsys_info`, `cmu_imem_info`, `cmu_peri_info`) bundle the per-domain arrays, clock ID count, and register save list used by `samsung_cmu_register_one()` via `exynos_arm64_register_cmu()`.
- `artpec8_pll_audio_rates` provides programmed audio PLL rates for `pll_1031x`; the shared PLLs and FSYS/CPUCL PLLs do not include file-local rate tables.
- `artpec8_clk_cmu_imem_init()` registers the IMEM CMU directly through `samsung_cmu_register_one()`, and is wired through `CLK_OF_DECLARE(artpec8_clk_cmu_imem, "axis,artpec8-cmu-imem", ...)`.
- `artpec8_cmu_probe()` obtains the matched `samsung_cmu_info` with `of_device_get_match_data()` and calls `exynos_arm64_register_cmu(dev, dev->of_node, info)`.
- `artpec8_cmu_of_match` maps each platform compatible to the correct CMU info block. `artpec8_cmu_init()` registers the `artpec8-cmu` platform driver at `core_initcall()`.

## Control flow and integration

Boot-time control splits into two paths. The IMEM domain is registered early by the OF clock declaration for `"axis,artpec8-cmu-imem"`; this avoids depending on the platform driver for clocks needed very early by timers, thermal, or interrupt-related infrastructure. Other domains bind through the platform driver registered by `core_initcall()`. On probe, the driver does not parse clock details manually; it selects a static `samsung_cmu_info` and delegates bus-clock enablement, initial manual/auto gate setup, and common Samsung CMU registration to `exynos_arm64_register_cmu()`.

`CMU_CMU` is the source domain. It registers `fout_pll_shared0`, `fout_pll_shared1`, and `fout_pll_audio`, creates divided shared PLL branches (`dout_pll_shared{0,1}_div{2,3,4}`), then uses muxes/dividers to create exported clocks for bus, core, CPU cluster, FSYS, IMEM, MIF, PERI, GPU, video, and accelerator domains. Many performance-domain dividers use `CLK_SET_RATE_PARENT` through `DIV_F()` so downstream requests can propagate upward.

`CMU_CPUCL` defines a CPU cluster PLL path, a switch-user path from `CMU_CMU`, CPU and debug dividers, and critical gates for CPU, shortstop, and CoreSight debug clocks. Unlike the generic `clk-cpu.c` CPU-clock abstraction, this file models CPUCL as ordinary PLL/mux/div/gate hardware clocks; no `samsung_cpu_clock` array appears here.

`CMU_FSYS` contains the storage/network/serial-facing clocks: FSYS PLL, bus/MMC/scan user muxes, dividers for PCIe, ADC, QSPI, EQOS, MMC, UART, NAND, OTP, and gates for PCIe, EQOS, QSPI, MMC, SFMC, UART, I2C, PWM, USB, and XHB. Several bus and serial clocks are marked `CLK_IS_CRITICAL`, indicating boot or console dependencies.

`CMU_PERI` provides peripheral IP clocks for DSIM, I2S, SPI, UART, I2C, and audio out. It has a fixed-rate `clk_peri_audio` at 100 MHz, audio/display/IP user muxes, peripheral dividers, and both Q-channel gates plus direct IP port gates. I2S clocks are marked `CLK_IGNORE_UNUSED`, which prevents common-clock cleanup from shutting off clocks that may be needed by hardware state not fully represented by consumers.

## State and persistence behavior

The file itself owns no mutable runtime state beyond the static `__initconst` clock descriptors. Register state is represented by the `*_clk_regs` arrays in each `samsung_cmu_info`; those arrays are consumed by Samsung framework helpers for registration and, when used with PM-capable flows, for save/restore. ARTPEC-8 uses `exynos_arm64_register_cmu()`, not the PM-specific `exynos_arm64_register_cmu_pm()`, so this file does not install explicit suspend/resume callbacks.

Clock state persists in hardware registers after registration. Gate criticality (`CLK_IS_CRITICAL`), ignore-unused policy, and rate-parent flags influence the common clock framework's later enable and rate behavior. The early IMEM registration directly calls `samsung_cmu_register_one()` and does not run the ARTPEC platform driver's bus-clock enablement helper, so it assumes the IMEM registers are accessible at early init time.

## Dependencies

The driver depends on the Samsung clock framework helpers from `clk.h`, the arm64 Exynos CMU wrapper from `clk-exynos-arm64.h`, Linux CCF provider APIs, platform-device probing, and clock IDs from `dt-bindings/clock/axis,artpec8-clk.h`. Correct operation also depends on matching device-tree CMU nodes with `reg` ranges, optional parent/bus clock names consumed by `exynos_arm64_register_cmu()`, and consumers referencing the exported clock IDs from the binding header.

## Risks and edge cases

- `CMU_*_NR_CLK` values must remain exactly one greater than the last valid binding ID used in each domain. If the binding header changes without these constants, clock lookup arrays can be undersized.
- Parent names are string contracts. Typos or mismatches against other CMU-produced names cause orphaned parents or failed rate propagation.
- Early IMEM registration bypasses the common arm64 init wrapper used by the platform-driver domains, so any future IMEM need for parent-clock enablement, manual gate initialization, or auto-gating setup must be handled explicitly.
- `CLK_IS_CRITICAL` is used heavily for boot-essential peripheral and CPUCL clocks. Missing critical flags can break boot or console access after unused-clock cleanup; excessive critical flags can hide real clock ownership bugs and increase power.
- Hardware register offsets and bit widths are raw TRM data. Off-by-one divider widths or incorrect Q-channel bit positions usually compile cleanly but fail only on hardware.
- Some clocks use ID `0` intentionally for internal-only clocks. Accidental use of `0` for a consumer-visible clock would make it unavailable through the provider.

## Test signals

Useful validation includes a kernel build with `dt_binding_check`, ARTPEC-8 boot logs without `failed to register clock` or unresolved parent warnings, `/sys/kernel/debug/clk/clk_summary` showing all ARTPEC domains and expected parentage, console/UART and storage/network peripherals working after late unused-clock cleanup, and rate-change tests on `CLK_SET_RATE_PARENT` clocks such as CPUCL/FSYS/PERI paths. Suspend/resume coverage is limited by the absence of a file-local PM path; hardware testing should still verify that registered ARTPEC clocks remain sane after any platform-level low-power transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-artpec8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-artpec9.c -->
# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-artpec9.c

## Purpose

`clk-artpec9.c` provides the ARTPEC-9 SoC clock topology for the Linux common clock framework using Samsung's clock description macros and arm64 Exynos CMU registration helpers. It defines static CMU descriptors for `CMU_CMU`, `CMU_BUS`, `CMU_CORE`, `CMU_CPUCL`, `CMU_FSYS0`, `CMU_FSYS1`, `CMU_IMEM`, and `CMU_PERI`, then associates them with Axis ARTPEC-9 device-tree compatible strings.

The file is a data-heavy hardware description rather than an algorithmic driver. ARTPEC-9 expands the ARTPEC-8 pattern with separate FSYS0 and FSYS1 domains, two CPUCL PLLs for CPU and SCU-related paths, newer fractional PLL types, and more boot-critical gates for PCIe, USB, UART, I3C, MMU/Q-channel, and timer-related infrastructure.

## Important APIs, types, and functions

- The clock arrays use Samsung CCF description macros: `PLL()`, `MUX()`, `nMUX()`, `MUX_F()`, `DIV()`, `DIV_F()`, `FFACTOR()`, and `GATE()`.
- `artpec9_pll_audio_rates`, `artpec9_pll_cpucl_rates`, and `artpec9_pll_fsys1_rates` provide explicit programmed rates for the audio PLL, CPUCL PLLs, and FSYS1 PLL. The CPUCL table comment requires descending order.
- `struct samsung_cmu_info` instances collect each CMU domain's PLL, mux, divider, fixed-factor, gate, register-list, and clock-ID metadata.
- `artpec9_cmu_imem_init()` registers IMEM through `exynos_arm64_register_cmu(NULL, np, &cmu_imem_info)` and is installed with `CLK_OF_DECLARE(artpec9_cmu_imem, "axis,artpec9-cmu-imem", ...)`.
- `artpec9_cmu_probe()` handles platform-driven CMU domains by calling `exynos_arm64_register_cmu(dev, dev->of_node, info)` using match data from `artpec9_cmu_of_match`.
- `artpec9_cmu_init()` registers the `artpec9-cmu` platform driver with `core_initcall()`.

## Control flow and integration

At early boot, the IMEM node is initialized through `CLK_OF_DECLARE`. That path calls the shared arm64 wrapper even without a `struct device`, allowing the wrapper to enable any named parent clock through OF lookup, initialize CMU gate/PLL mode, and register the CMU. The remaining CMUs bind through the platform driver. For each matching compatible, the platform bus supplies the corresponding `samsung_cmu_info`; probe delegates all register mapping and clock provider registration behavior to `exynos_arm64_register_cmu()`.

`CMU_CMU` is the root distribution domain. It declares shared and audio PLLs, shared divider outputs, and many `dout_clkcmu_*` exported clocks for bus, core, CPUCL switch, FSYS0/FSYS1, GPU, IMEM, MIF, PERI, RSP, TRFM, VIO, VIP, and VPP. Many parent arrays include `mout_clk_pll_fsys1` or `fout_pll_fsys1`, making the FSYS1 PLL an upstream source for multiple non-FSYS branches.

`CMU_CPUCL` declares two CPU PLLs, `fout_pll0_cpucl` and `fout_pll1_cpucl`, both using the same CPUCL rate table. The first feeds `dout_clk_cpucl_cpu`; the second feeds the SCU mux/divider path. CPU cluster, GIC, PCLK, ATCLK, CMUREF, debug, shortstop, and CoreSight gates are represented as ordinary clocks, with CPU and debug paths marked critical.

`CMU_FSYS0` covers Ethernet, I3C, MMC, QSPI, ADC, PWM, and NAND-facing clocks. It uses user muxes for bus/IP/main sources, dividers for 125 MHz, ADC, 300 MHz bus, EQOS, MMC, QSPI, and SFMC, and gates for both Q-channel and direct IP port registers. `CMU_FSYS1` covers FSYS1 PLL, UART0, PCIe, USB, XHB, TZC400, and MMU TBU Q-channel clocks.

`CMU_PERI` covers DSIM, I3C2/I3C3, I2C2/I2C3, SPI0, UART1, and UART2. It has IP/display user muxes, peripheral dividers, and many critical direct IP-port gates. `CMU_BUS` and `CMU_CORE` are intentionally small user-mux domains selecting top-level bus/core clocks from `CMU_CMU`.

## State and persistence behavior

Runtime state is primarily in the hardware clock registers described by each `*_clk_regs` array. The static arrays are `__initconst` and disappear after init where allowed; they configure the Samsung registration helpers but are not long-lived mutable state. The common clock framework owns registered `clk_hw` state after probe, while register contents persist in hardware.

This file does not define suspend/resume callbacks or call `exynos_arm64_register_cmu_pm()`. Any power-state save/restore is therefore outside this file's local control. Critical and ignore-unused flags influence persistence by preventing selected clocks from being disabled by CCF cleanup or by ordinary consumer release behavior.

## Dependencies

The file depends on `dt-bindings/clock/axis,artpec9-clk.h` for ID values, Samsung's `clk.h` macros and registration APIs, `clk-exynos-arm64.h` for CMU setup, Linux platform-driver and CCF provider APIs, and device-tree nodes matching the ARTPEC-9 compatible strings. It also depends on cross-domain parent-name consistency: many domains consume clock names produced by `CMU_CMU` or `CMU_FSYS1`.

## Risks and edge cases

- Clock parent strings are a central contract. Several ARTPEC-9 parents reference FSYS1 PLL paths from the top CMU; a typo or registration-order issue can leave broad portions of the topology orphaned.
- The `CMU_CMU_NR_CLK` and other `*_NR_CLK` constants must track the binding header exactly. Undersized `clk_hw_onecell_data` tables cause missing provider entries.
- Some register-list arrays omit trailing commas in a few places but compile; future edits around those lines should avoid accidental token concatenation or formatting mistakes.
- The CPUCL PLL rate table must remain descending for Samsung PLL lookup behavior. Adding rates in the wrong order can make rate selection wrong even when entries are numerically valid.
- Heavy `CLK_IS_CRITICAL` use protects boot-critical hardware but can mask missing runtime consumers. Reducing those flags requires hardware boot and suspend validation.
- The IMEM early-init path is special. If IMEM gains runtime PM needs or resource dependencies that require a `struct device`, this early registration model may need rework.

## Test signals

Build-time signals include successful compilation of the ARTPEC-9 clock driver and binding consistency checks. Runtime signals include ARTPEC-9 boot without clock registration failures, a complete `clk_summary` tree for all eight CMU domains, working console/UART, timers/MCT, thermal, MMC/QSPI, Ethernet, PCIe, USB, I3C/I2C/SPI, and DSIM clocks after unused-clock cleanup. CPU frequency or PLL rate tests should verify the CPUCL PLL table entries and the SCU path. PCIe/USB/Ethernet tests are particularly useful because FSYS0/FSYS1 split parentage and critical gates are dense there.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-artpec9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-cpu.c -->
# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-cpu.c

## Purpose

`clk-cpu.c` implements Samsung Exynos CPU-clock registration and coordinated CPU-domain rate switching for the common clock framework. A Samsung CPU clock is modeled as a CCF `clk_hw` whose visible output rate equals its primary parent PLL rate, while auxiliary CPU-domain dividers and muxes are programmed around parent PLL transitions to keep CPU, debug, AXI, ATCLK, PCLKDBG, and related clocks within safe limits.

The driver supports multiple register layouts: Exynos4210-style, Exynos5433-style, and Exynos850 cluster 0/cluster 1 style. Platform clock drivers provide `struct samsung_cpu_clock` descriptors and tables of parent-rate-specific divider values; this file turns those descriptors into registered CPU clocks plus parent PLL notifiers.

## Important APIs, types, and functions

- `struct exynos_cpuclk_regs` describes offsets for mux, mux status, DIV0/DIV1, divider status, and Exynos850-specific mux/div registers.
- `struct exynos_cpuclk_chip` binds a register layout to pre-rate and post-rate callbacks.
- `struct exynos_cpuclk` stores the CCF hardware object, alternate parent, register base, shared spinlock, copied config table, notifier block, flags, and chip layout.
- `wait_until_divider_stable()` and `wait_until_mux_stable()` poll hardware status bits with a 10 ms timeout and log on timeout.
- `exynos_set_safe_div()` writes temporary safe divider values to `div_cpu0`.
- `exynos_cpuclk_pre_rate_change()` and `exynos_cpuclk_post_rate_change()` handle Exynos 3/4/5 style transitions, including optional DIV1 and ATB/debug alternate divider handling.
- `exynos5433_cpuclk_pre_rate_change()` and `exynos5433_cpuclk_post_rate_change()` implement the Exynos5433 mux bit layout and always program DIV0/DIV1.
- `exynos850_alt_parent_set_max_rate()`, `exynos850_cpuclk_pre_rate_change()`, and `exynos850_cpuclk_post_rate_change()` implement the Exynos850 alternate-parent divider path through CMU_TOP.
- `exynos_cpuclk_determine_rate()` rounds CPU clock requests through the parent and requests a matching parent rate. `exynos_cpuclk_recalc_rate()` reports the CPU clock rate as the parent rate.
- `exynos_cpuclk_notifier_cb()` dispatches `PRE_RATE_CHANGE` and `POST_RATE_CHANGE` notifications from the primary parent to the layout-specific callbacks.
- `samsung_clk_register_cpu()` is the public registration loop called by Samsung CMU registration code.

## Control flow

Registration starts in `samsung_clk_register_cpu()`, which iterates a platform-provided list and calls `exynos_register_cpu_clock()` for each entry. The helper resolves primary and alternate parent `clk_hw` objects from the provider lookup table, allocates `struct exynos_cpuclk`, fills `clk_init_data` with one parent and `CLK_SET_RATE_PARENT`, installs the parent notifier, counts and copies the configuration table up to its zero-rate sentinel, registers the CPU `clk_hw`, and adds the lookup under the platform clock ID.

Rate changes are initiated by consumers changing the CPU clock. Because the CPU clock has `CLK_SET_RATE_PARENT`, the CCF propagates the request to the primary parent PLL. The parent PLL then emits notifier events. On `PRE_RATE_CHANGE`, this driver finds the divider configuration whose `prate * 1000` equals the new parent rate. If the alternate source is faster than the old parent or the transition lowers the PLL rate, it first applies a safe divider to prevent overspeed while running from the alternate source. It then switches the CPU mux to the alternate parent and writes the target auxiliary divider values while the PLL can be reprogrammed.

On `POST_RATE_CHANGE`, the driver switches the CPU mux back to the primary PLL parent and removes temporary safe divider settings. Exynos4210 optionally preserves HPM/COPY divider values when HPM is not sourced from APLL and can apply the ATB debug divider workaround. Exynos5433 uses a different mux bit and status field. Exynos850 skips all work when switching to or from the 26 MHz oscillator, otherwise constrains the alternate parent by setting an upstream divider rate, switches to the alternate mux parent, updates four divider registers, then returns the alternate parent to maximum rate after switching back to the PLL.

## State and persistence behavior

Per-CPU-clock state lives in allocated `struct exynos_cpuclk` instances and in the copied `cfg` arrays. The code registers a parent notifier and a CCF hardware clock but does not implement an unregister path, consistent with early SoC clock registration that persists for the life of the kernel. Hardware divider and mux register values persist until changed by future rate transitions, boot firmware, or power management code outside this file.

The transition functions use the Samsung provider's spinlock with IRQ save/restore around register updates to serialize CPU-domain mux/divider writes with other clock register accesses. Poll loops are timeout-based but do not fail the transition on timeout; they log errors and continue. Configuration lookup failures return `-EINVAL`, which is converted to a notifier error.

## Dependencies

This file depends on Samsung clock provider types and `struct samsung_cpu_clock` from `clk.h`, the public flags/layout/config definitions in `clk-cpu.h`, Linux CCF APIs, clock notifier APIs, MMIO accessors, spinlocks, jiffies timing, and parent clock implementations capable of notifiers and rate changes. It assumes platform code supplies valid parent IDs, alternate parent IDs, base offsets, layout enum values, and a zero-terminated `exynos_cpuclk_cfg_data` table whose `prate` values are in KHz.

## Risks and edge cases

- A config table missing the requested parent PLL rate causes the notifier to reject the transition. A table without a zero sentinel would read past the array while registering or searching.
- `WARN_ON(alt_div >= MAX_DIV)` only warns; the code still writes the computed value masked into hardware. Bad parent rates can therefore lead to unsafe or truncated divider programming.
- The wait helpers log timeouts but do not return errors. Hardware that fails to stabilize can leave the CPU domain on an unexpected mux/divider state while the CCF believes the transition completed.
- Exynos850 uses `clk_set_rate()` on the alternate parent during a parent PLL notifier path. Parent graph mistakes or locking inversions in platform topology could cause rate recursion or deadlocks.
- The CCF-visible CPU clock rate equals the primary parent rate, while hardware dividers exist and are temporarily used. Consumers must not interpret this clock as an arbitrary divider output.
- There is no cleanup path if `clk_hw_register()` succeeds but later system teardown wanted to unregister; this is normal for built-in SoC clocks but relevant for refactoring to loadable modules.

## Test signals

Relevant tests include booting platforms that use each layout, enabling CPU frequency transitions across every configured rate, and checking that transitions do not emit notifier errors, divider/mux timeout logs, or CPU instability. `clk_summary` should show CPU clock rates matching the selected parent PLL rates. Stress tests should include downclock and upclock transitions, alternate-parent faster-than-old-parent cases, Exynos4210 debug divider behavior, Exynos5433 DIV1 programming, and Exynos850 oscillator and alternate-parent divider paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-cpu.h -->
# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-cpu.h

## Purpose

`clk-cpu.h` is the small public header for Samsung Exynos CPU-clock support. It provides flag bits, layout identifiers, and the divider configuration data structure consumed by `clk-cpu.c` and by SoC-specific clock drivers that register CPU clocks through `samsung_clk_register_cpu()`.

## Important APIs and types

- `CLK_CPU_HAS_DIV1` indicates that the CPU clock register block includes a second divider configuration register and corresponding status register.
- `CLK_CPU_NEEDS_DEBUG_ALT_DIV` indicates that debug-related clocks require safe divider programming while the alternate parent is active.
- `enum exynos_cpuclk_layout` identifies the supported register-layout families: `CPUCLK_LAYOUT_E4210`, `CPUCLK_LAYOUT_E5433`, `CPUCLK_LAYOUT_E850_CL0`, and `CPUCLK_LAYOUT_E850_CL1`.
- `struct exynos_cpuclk_cfg_data` maps a primary parent rate in KHz to the `div0` and `div1` register values that should be programmed for that rate.

## Control flow and integration

The header has no runtime control flow. Its definitions are used by platform clock tables, usually embedded in `struct samsung_cpu_clock` descriptors from `clk.h`. During CPU clock registration, `clk-cpu.c` copies a zero-terminated array of `exynos_cpuclk_cfg_data`, selects behavior based on `reg_layout`, and checks the flags to decide whether to program DIV1 and debug-safe alternate dividers.

## State and persistence behavior

The header defines data contracts only. The `exynos_cpuclk_cfg_data` arrays authored by platform drivers are typically `__initconst` source data. `clk-cpu.c` copies them into persistent allocations during registration so rate transitions can continue after init memory is freed.

## Dependencies

The header uses `BIT()` in macro definitions, so it depends on inclusion context that provides Linux bit macros, usually through the Samsung clock headers or kernel headers included before it. It is tightly coupled to `clk-cpu.c` and the `samsung_cpu_clock` registration contract in `clk.h`.

## Risks and edge cases

- `prate` is documented in KHz, while clock notifier rates are in Hz. Platform tables must use KHz values exactly matching `new_rate / 1000`; otherwise lookup fails.
- `div0` and `div1` are full register values or packed field values interpreted by layout-specific code. Incorrect packing compiles but produces unsafe hardware frequencies.
- Adding a new enum value requires a matching `exynos_clkcpu_chips[]` entry in `clk-cpu.c`; otherwise a platform descriptor can index invalid or unintended chip data.

## Test signals

Compile coverage should catch missing enum references but not incorrect table values. Hardware CPU frequency transition tests are the real validation signal for any platform table using this header. Static review should verify descending or complete OPP tables where required by the platform, zero sentinels, correct KHz units, and correct flags for DIV1/debug-divider hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-cpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos-arm64.c -->
# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos-arm64.c

## Purpose

`clk-exynos-arm64.c` provides shared CMU registration, initialization, runtime PM setup, and suspend/resume helpers for newer arm64 Samsung/Exynos-style clock drivers. SoC-specific files supply `struct samsung_cmu_info` tables; this file handles common register initialization policy, bus-clock enablement, CCF provider registration, dynamic root clock gating enablement, and register save/restore around power management.

## Important APIs, types, and functions

- `struct exynos_arm64_cmu_data` is per-device state for PM-capable CMUs. It stores saved register dumps, optional sysreg dumps, suspend override dumps, the CMU bus clock, parent clocks that must be temporarily enabled for suspend/resume, and the Samsung provider context.
- `is_gate_reg()`, `is_pll_conx_reg()`, and `is_pll_con1_reg()` classify register offsets for initialization decisions.
- `exynos_arm64_init_clocks()` maps the CMU, optionally enables global automatic clock gating, sets PLL manual bits for PLL_CON1 registers when requested, and forces gate registers to manual mode when automatic mode is not active.
- `exynos_arm64_enable_bus_clk()` obtains and enables the CMU's parent/bus clock from a device or OF node based on `cmu->clk_name`.
- `exynos_arm64_cmu_prepare_pm()` allocates register-save arrays, records suspend override arrays from `samsung_cmu_info`, and obtains all parent clocks from the device-tree node for later suspend/resume sequencing.
- `exynos_arm64_register_cmu()` is the simple registration helper used by early and non-PM platform CMUs.
- `exynos_arm64_register_cmu_pm()` is the PM-aware registration helper for platform drivers. It prepares save state, enables the bus clock, optionally initializes registers, maps resources with devm APIs, initializes the Samsung provider, enables runtime PM around clock registration, registers clocks and OF provider, enables dynamic root clock gating, and releases the runtime PM usage count.
- `exynos_arm64_cmu_suspend()` and `exynos_arm64_cmu_resume()` save and restore CMU/sysreg registers and manage parent/bus clock enables during system/runtime power transitions.

## Control flow

For simple CMUs, a SoC driver calls `exynos_arm64_register_cmu(dev, np, cmu)`. The helper attempts to enable the named bus clock but only logs failure, because boot firmware may already have it enabled. It then initializes clock-control registers through `exynos_arm64_init_clocks()` and registers all clocks with `samsung_cmu_register_one()`.

The PM-capable path starts in a platform probe calling `exynos_arm64_register_cmu_pm(pdev, init_clk_regs)`. It obtains match data, allocates `exynos_arm64_cmu_data`, prepares register dump storage, enables the bus clock, optionally initializes clocks, maps the MMIO resource, initializes the Samsung provider context, makes the device runtime-PM active, registers the clocks, publishes the OF provider, enables dynamic root clock gating for sysreg-referenced clocks, and then allows runtime suspend.

Suspend first saves the CMU register list and sysreg register list, enables all parent clocks listed by the DT node, writes any `cmu->suspend_regs` override values needed for low power, disables those parent clocks, then disables the CMU bus clock. Resume reverses this by enabling the bus clock and parent clocks, restoring saved CMU registers, restoring sysreg registers if a sysreg mapping exists, then disabling the parent clocks.

## State and persistence behavior

PM-capable registration persists `exynos_arm64_cmu_data` as platform driver data. Register save buffers are allocated with `samsung_clk_alloc_reg_dump()` and freed only on early preparation failure; successful probes keep them for the device lifetime. The bus clock returned by `clk_get()` is retained in `data->clk`, and parent clocks returned by `of_clk_get()` are retained in `data->pclks`.

Hardware state initialization is explicit. If `cmu->auto_clock_gate` and `samsung_is_auto_capable(np)` are both true, the helper writes global auto-gating option bits to `cmu->option_offset`; otherwise every gate register in the CMU register list is forced to manual mode and hardware auto clock gating is disabled per gate. If `cmu->manual_plls` is set, PLL_CON1 registers get `PLL_CON1_MANUAL`.

## Dependencies

This file depends on Samsung clock provider internals from `clk.h`, OF address mapping, platform-device resource mapping, Linux CCF clock APIs, runtime PM, and optional Samsung sysreg/dynamic-root-gating helpers. It assumes SoC-specific `samsung_cmu_info` objects provide complete `clk_regs` lists, optional sysreg and suspend register lists, correct `clk_name` strings, and accurate auto/manual gating capability flags.

## Risks and edge cases

- `exynos_arm64_init_clocks()` panics if `of_iomap()` fails. That is appropriate for early clock init but makes bad DT register resources fatal.
- Gate-register classification is based on broad offset ranges (`0x2000..0x2fff`). A future CMU with different register layout would need updated classification or must avoid this helper.
- `exynos_arm64_cmu_prepare_pm()` returns success immediately when a node has zero parent clocks after allocating `clk_save` and optional sysreg save. That is intentional but means suspend/resume will still depend on `data->clk` bus-clock handling.
- Bus-clock enable failures are nonfatal. This supports bootloader-enabled hardware but can defer failures until register access if the clock is actually off.
- Suspend disables the CMU bus clock after applying suspend register overrides. If consumers or wakeup paths need registers accessible later, the SoC-specific PM policy must account for it.
- `exynos_arm64_register_cmu_pm()` enables runtime PM but does not show a local unwind path after successful runtime PM enablement if later registration helpers fail; current Samsung helpers are generally expected not to fail late, but refactors should revisit error handling.

## Test signals

Validation should include booting SoCs that use both simple and PM-capable paths, checking CMU registration logs, confirming global auto-gating versus manual-gate initialization through register inspection, and exercising runtime/system suspend/resume. `clk_summary` before and after suspend should preserve rates and parentage. Hardware tests should cover CMUs with sysreg-backed dynamic root gating and CMUs with parent clocks listed in DT, because suspend sequencing depends on both.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos-arm64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos-arm64.h -->
# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos-arm64.h

## Purpose

`clk-exynos-arm64.h` declares the shared arm64 Exynos CMU registration and PM helper API implemented by `clk-exynos-arm64.c`. SoC-specific Samsung clock drivers include this header when they want to register `samsung_cmu_info` domains through the common arm64 CMU setup path.

## Important APIs

- `exynos_arm64_register_cmu(struct device *dev, struct device_node *np, const struct samsung_cmu_info *cmu)` registers a CMU without installing the PM-specific provider context.
- `exynos_arm64_register_cmu_pm(struct platform_device *pdev, bool set_manual)` registers a platform CMU with runtime/system PM support and optional initial register setup.
- `exynos_arm64_cmu_suspend(struct device *dev)` saves CMU/sysreg registers, applies suspend register values, and disables the CMU bus clock.
- `exynos_arm64_cmu_resume(struct device *dev)` re-enables the bus clock and restores saved CMU/sysreg registers.

## Control flow and integration

The header has no control flow of its own. It exposes helpers for SoC files such as ARTPEC, Exynos850, Exynos7885, Exynos5433, and related arm64 Samsung drivers. Early `CLK_OF_DECLARE` users can call `exynos_arm64_register_cmu(NULL, np, cmu)`, while platform-driver probes pass a real `struct device` or `platform_device` to enable resource-managed mapping and runtime PM integration.

## State and persistence behavior

The header declares APIs that create persistent clock providers and, for the PM path, persistent per-device save/restore data. It does not define state itself.

## Dependencies

The header includes `clk.h` so that `struct samsung_cmu_info` is visible. It also references `struct device`, `struct device_node`, and `struct platform_device`; those are expected from kernel type declarations included through existing driver include order.

## Risks and edge cases

- The second parameter name in `exynos_arm64_register_cmu_pm()` is `set_manual` in the header but `init_clk_regs` in the C implementation. The type and position match, but the naming mismatch can confuse callers reviewing whether the boolean controls manual mode or all initial clock-register setup.
- Callers must select the simple versus PM helper correctly. Using the simple helper for a power-gated CMU can lose register state across suspend; using the PM helper requires a platform device and match data.

## Test signals

Compile coverage verifies signature consistency. Runtime validation comes from SoC drivers using the helper: successful CMU registration for simple users and successful suspend/resume for PM users. Review should check that new callers pass the intended boolean meaning to `exynos_arm64_register_cmu_pm()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos-arm64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos-audss.c -->
# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos-audss.c

## Purpose

`clk-exynos-audss.c` is a platform clock driver for the Exynos audio subsystem clock controller. It registers a small onecell clock provider containing audio muxes, dividers, and gates for Exynos4210/5250/5410/5420-style audio subsystem blocks, with variant flags for ADMA, MST, EPLL enablement, and clock count differences.

## Important APIs, types, and functions

- Global `lock`, `reg_base`, `clk_data`, and `epll` hold the register lock, mapped audio subsystem registers, onecell provider data, and optional EPLL input clock.
- `ASS_CLK_SRC`, `ASS_CLK_DIV`, and `ASS_CLK_GATE` are the three audio subsystem register offsets used by the driver.
- `reg_save` stores the source, divider, and gate register values across runtime/system PM.
- `struct exynos_audss_clk_drvdata` describes SoC variants with `has_adma_clk`, `has_mst_clk`, `enable_epll`, and `num_clks`. The current probe path uses `has_adma_clk`, `enable_epll`, and `num_clks`; `has_mst_clk` is variant metadata but is not otherwise consumed in this file.
- `exynos_audss_clk_suspend()` and `exynos_audss_clk_resume()` save and restore the three hardware registers.
- `exynos_audss_clk_teardown()` unregisters muxes, dividers, and gates from the onecell table in ID order.
- `exynos_audss_clk_probe()` maps registers, gets optional parent clocks, enables EPLL when requested, registers the clock hardware, adds the OF provider, and enables runtime PM around registration.
- `exynos_audss_clk_remove()` removes the provider, unregisters clocks, disables runtime PM, and disables EPLL if it was enabled.

## Control flow

Probe first selects variant data from the OF compatible. It maps the single MMIO resource and allocates a `clk_hw_onecell_data` table large enough for `EXYNOS_AUDSS_MAX_CLKS`, while exposing only `variant->num_clks` entries. Optional `pll_ref` and `pll_in` clocks override default parent names for `mout_audss`; if the variant requests EPLL enablement and `pll_in` exists, the driver prepares/enables it before touching audio clocks.

The driver enables runtime PM and holds a noresume usage count while registering clocks to prevent the clock core from suspending the device during provider setup. It registers two muxes (`mout_audss`, `mout_i2s`), three dividers (`dout_srp`, `dout_aud_bus`, `dout_i2s`), gates for SRP, I2S bus, I2S serial clock, PCM bus, PCM serial clock, and optionally ADMA. Optional external clocks (`cdclk`, `sclk_audio`, `sclk_pcm_in`) override parent names when present. After checking every exposed table entry for errors, it publishes the provider with `of_clk_add_hw_provider()` and drops the runtime PM usage count.

On remove or registration failure, `exynos_audss_clk_teardown()` unregisters successfully registered hardware clocks by ID range and type. Runtime PM callbacks save and restore the three audio subsystem registers. Late system sleep uses `pm_runtime_force_suspend` and `pm_runtime_force_resume`.

## State and persistence behavior

The driver keeps `reg_base`, `clk_data`, and `epll` as file-scope globals, which assumes only one audio subsystem instance is active. Registered clock hardware is stored in the onecell table allocated with devm memory, but hardware clocks are explicitly unregistered. The optional EPLL is prepared for variants that require it and is disabled on remove or probe failure.

Register state is persisted across runtime suspend by copying `ASS_CLK_SRC`, `ASS_CLK_DIV`, and `ASS_CLK_GATE` into `reg_save` and writing them back on resume. Clock topology state in CCF persists through `clk_hw` registrations and OF provider publication. Runtime PM usage is carefully held during registration and dropped afterwards.

## Dependencies

The driver depends on the Exynos AUDSS binding IDs from `dt-bindings/clock/exynos-audss-clk.h`, platform-device probing, OF match data, MMIO resource mapping, CCF registration helpers for mux/divider/gate clocks, runtime PM, and optional named parent clocks in DT (`pll_ref`, `pll_in`, `cdclk`, `sclk_audio`, `sclk_pcm_in`).

## Risks and edge cases

- File-scope globals make multiple instances unsafe. A second AUDSS node would overwrite `reg_base`, `clk_data`, and `epll`.
- `has_mst_clk` is set for Exynos5410 but not used in the registration logic; either the clock is no longer represented or support is incomplete/stale.
- `clk_data->num` is variant-specific, but allocation always uses `EXYNOS_AUDSS_MAX_CLKS`. Teardown loops rely on ID ordering (`mux` IDs first, then dividers, then gates).
- Optional parent clock lookup failures silently retain default string names. This is flexible but can hide DT naming mistakes until parent resolution or rate changes fail later.
- If EPLL enablement succeeds and a later registration step fails, the unwind disables it; any new exit path must preserve that balance.
- Runtime suspend reads/writes registers through a global `reg_base` without checking whether the optional EPLL/bus clock is enabled; PM ordering must ensure register access is valid.

## Test signals

Build and DT binding tests should cover all compatibles. Runtime validation includes probing each variant, checking `clk_summary` for the expected number of clocks and parent names, exercising I2S/PCM/SRP audio playback/capture, verifying ADMA clock presence on Exynos5420, and running runtime suspend/resume plus system suspend/resume while confirming `ASS_CLK_SRC`, `ASS_CLK_DIV`, and `ASS_CLK_GATE` are restored. Failure tests should cover missing optional parent clocks and provider registration unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos-audss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos-clkout.c -->
# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos-clkout.c

## Purpose

`clk-exynos-clkout.c` registers the Exynos PMU clock-output control as a single composite clock named `clkout`. The clock combines a mux selecting one of up to 32 PMU-provided `clkoutN` parents and a gate controlled by the PMU debug register. It supports Exynos4-style 4-bit mux fields and Exynos5-style 5-bit mux fields.

## Important APIs, types, and functions

- `struct exynos_clkout` embeds `struct clk_gate`, `struct clk_mux`, a spinlock, mapped PMU register base, provider node, saved PMU debug value, and onecell clock data.
- `struct exynos_clkout_variant` carries the SoC-specific mux mask.
- `exynos_clkout_ids` maps PMU parent compatible strings to Exynos4 or Exynos5 mux width variants.
- `exynos_clkout_match_parent_dev()` validates that the platform device was instantiated from an MFD parent and matches the parent device against `exynos_clkout_ids` to obtain the mux mask.
- `exynos_clkout_probe()` discovers parent clocks named `clkout0` through `clkout31`, maps the PMU register region, initializes embedded mux/gate structures, registers a composite clock, and publishes an OF onecell provider.
- `exynos_clkout_remove()` removes the provider, unregisters the composite clock, and unmaps the PMU register base.
- `exynos_clkout_suspend()` and `exynos_clkout_resume()` save and restore the PMU debug register.

## Control flow

The platform driver is intended to be instantiated as a child of an Exynos PMU MFD device. Probe allocates a variable-size `exynos_clkout`, matches the parent PMU compatible manually because the child device may not have its own OF match data, and chooses the mux mask. If the child has no own OF node, it uses the parent PMU node for clock parent lookup and provider registration.

Probe then scans `clkout0` through `clkout31` by name. Missing parents are represented as `"none"`, while found parents supply their real CCF names. `parent_count` is set to the highest found index plus one, so holes below the highest valid index remain selectable as `"none"`. If no parent exists, probe fails. The driver maps the PMU register region with `of_iomap()`, points both gate and mux at `EXYNOS_PMU_DEBUG_REG`, and registers `clkout` as a composite clock with mux ops, no rate ops, and gate ops. Flags `CLK_SET_RATE_PARENT | CLK_SET_RATE_NO_REPARENT` allow rate requests to propagate to the selected parent while preventing automatic reparenting.

On provider-add failure the composite clock is unregistered, the PMU mapping is unmapped, and all obtained parent clocks are released. On remove, the provider and composite clock are removed and the MMIO mapping is released. Suspend/resume preserves the PMU debug register so mux/gate state survives low-power transitions.

## State and persistence behavior

Per-instance state is stored in the devm-allocated `exynos_clkout` structure and attached to the platform device. The PMU debug register contains both gate and mux state; the driver saves the full register value in `pmu_debug_save` on suspend and writes it back on resume. The mux/gate operations share `slock` to serialize read-modify-write access to the same register.

One important lifetime detail is that parent clocks obtained during probe are released only on failure, not after successful registration and not in remove. This may be intentional to keep parent references alive for the composite clock name array, but it is also a leak-shaped pattern to review if this driver is refactored.

## Dependencies

The driver depends on platform-device/MFD instantiation by the Exynos PMU driver, parent PMU compatible strings, named parent clocks `clkout0` ... `clkout31` in the PMU node, CCF composite clock registration, OF MMIO mapping, and PM suspend/resume callbacks. It uses `of_clk_add_hw_provider()` on either the child node or parent PMU node.

## Risks and edge cases

- The driver must be a PMU child. Without a parent device or with an unsupported parent compatible, probe fails.
- Parent discovery allows holes. Selecting a mux index whose name is `"none"` will not provide a real parent, so DT parent definitions must match hardware-visible mux values carefully.
- `parent_count` is highest found index plus one, not count of valid parents. This preserves mux indices but can expose placeholder parents.
- `of_iomap()` is not devm-managed; failure and remove paths must keep `iounmap()` balanced.
- The full PMU debug register is restored on resume. If other PMU debug bits are owned by another driver and changed while suspended, restore could overwrite them.
- Parent `clk_put()` is missing on successful remove for the parent clocks acquired during probe; long-lived PMU child devices rarely unload, but module unload/reprobe testing should watch for leaks.

## Test signals

Useful validation includes probing under each supported PMU compatible, confirming `clkout` appears as a onecell provider, switching mux parents through CCF/debugfs where available, enabling/disabling the gate, and observing the physical clock output if the board exposes it. Suspend/resume should preserve the selected parent and gate state. Negative tests should cover missing parent device, unsupported parent compatible, no `clkoutN` parents, and provider-add failure unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos-clkout.c -->
