# Research: subset-b-005848

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk-provider.h -->
# sources/distributed-fs/ceph-client/include/linux/clk-provider.h

Purpose: This is the provider-side Common Clock Framework contract. It gives clock-controller drivers the shared data structures, framework flags, `clk_ops` callback table, simple clock building blocks, registration helpers, and OF provider hooks used to publish clocks to consumers.

Important APIs/types/functions: Core types are `struct clk_rate_request`, `struct clk_duty`, `struct clk_ops`, `struct clk_parent_data`, `struct clk_init_data`, `struct clk_hw`, `struct clk_onecell_data`, and `struct clk_hw_onecell_data`. Basic clock implementations are represented by `struct clk_fixed_rate`, `struct clk_gate`, `struct clk_divider`, `struct clk_mux`, `struct clk_fixed_factor`, `struct clk_fractional_divider`, `struct clk_multiplier`, and `struct clk_composite`. The header exports framework flags such as `CLK_SET_RATE_GATE`, `CLK_SET_PARENT_GATE`, `CLK_SET_RATE_PARENT`, `CLK_IGNORE_UNUSED`, `CLK_GET_RATE_NOCACHE`, `CLK_SET_RATE_NO_REPARENT`, `CLK_IS_CRITICAL`, and `CLK_OPS_PARENT_ENABLE`, plus type-specific flags for gates, dividers, muxes, fixed factors, fractional dividers, and multipliers. Registration families include `clk_register*`, `clk_hw_register*`, `devm_clk_hw_register*`, `of_clk_hw_register`, fixed-rate/gate/divider/mux/fixed-factor/fractional/composite helpers, and OF APIs `of_clk_add_provider`, `of_clk_add_hw_provider`, `devm_of_clk_add_hw_provider`, `of_clk_del_provider`, `of_clk_src_onecell_get`, `of_clk_hw_onecell_get`, `of_clk_parent_fill`, and `of_clk_detect_critical`.

Control flow: Runtime behavior is callback-driven. Consumers call generic `clk_*` APIs, which traverse `clk_core`/`clk_hw` and invoke provider callbacks such as `prepare`, `enable`, `recalc_rate`, `determine_rate`, `set_parent`, `set_rate`, `save_context`, and `restore_context`. Registration helpers construct init data and connect provider hardware blocks into the framework. Static init macros such as `CLK_OF_DECLARE`, `CLK_HW_INIT*`, and `CLK_FIXED_FACTOR*` create early-boot or compound-literal setup paths. With `CONFIG_OF` disabled, OF provider helpers degrade to inert success or `-ENOENT` stubs.

State and persistence behavior: The header defines state handles but stores no state itself. Provider state is held in registered clock objects, MMIO registers referenced by `reg`, cached parent/rate metadata inside the clock framework, per-type `spinlock_t` register locks, and devres-managed registrations. Persistent behavior is hardware and firmware facing: clock names, parent arrays, OF phandle indices, divider/mux encodings, and flags become ABI-like contracts between DT, drivers, and board code.

Dependencies and integration points: It includes `<linux/of.h>` and `<linux/of_clk.h>` and integrates with the CCF core in `drivers/clk/clk.c`, DT clock providers, platform clock-controller drivers, debugfs, devres, MMIO helpers, spinlocks, and consumer APIs in `clk.h`. Basic clock helpers are reused by SoC clock drivers that compose register gates, muxes, dividers, PLL-derived factors, and one-cell provider tables.

Risks: Misstating `clk_ops` sleep/atomic rules can deadlock or sleep in atomic context; wrong parent array type or count can select the wrong upstream clock; incorrect divider/mux flags can program bad bitfields; missing `CLK_IS_CRITICAL` or misuse of `CLK_IGNORE_UNUSED` can gate hardware needed for boot or suspend; mismatched devm/non-devm unregister paths cause leaks or double unregister. The source comment explicitly says changes to common flags must be mirrored in `clk_flags[]` in `drivers/clk/clk.c`.

Test signals: Build coverage with broad `CONFIG_COMMON_CLK`/`CONFIG_OF` combinations, `dtbs_check`/DT compile for clock phandles, boot logs for provider registration failures, debugfs clock tree inspection, rate-change notifier tests, suspend/resume context save/restore, unused-clock disable sweeps, and hardware tests for mux/divider/gate programming are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk-provider.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk.h -->
# sources/distributed-fs/ceph-client/include/linux/clk.h

Purpose: This is the consumer-side clock API. Device drivers use it to acquire clock handles, prepare/enable clocks, manage rates, parents, phases, duty cycles, notifiers, exclusive rate control, bulk clock sets, and OF clock lookup.

Important APIs/types/functions: The header defines notifier events `PRE_RATE_CHANGE`, `POST_RATE_CHANGE`, and `ABORT_RATE_CHANGE`, plus `struct clk_notifier`, `struct clk_notifier_data`, and `struct clk_bulk_data`. Main APIs include `clk_get`, `devm_clk_get*`, `clk_get_optional`, `clk_bulk_get*`, `devm_clk_bulk_get*`, `clk_prepare`, `clk_unprepare`, `clk_enable`, `clk_disable`, `clk_prepare_enable`, `clk_disable_unprepare`, `clk_bulk_prepare_enable`, `clk_bulk_disable_unprepare`, `clk_get_rate`, `clk_round_rate`, `clk_set_rate`, `clk_set_rate_exclusive`, `clk_set_rate_range`, `clk_set_min_rate`, `clk_set_max_rate`, `clk_drop_range`, `clk_set_parent`, `clk_get_parent`, `clk_has_parent`, `clk_set_phase`, `clk_get_phase`, `clk_set_duty_cycle`, `clk_get_scaled_duty_cycle`, `clk_notifier_register`, `devm_clk_notifier_register`, `clk_rate_exclusive_get`, `clk_rate_exclusive_put`, `clk_save_context`, `clk_restore_context`, `clk_put`, `clk_bulk_put*`, `devm_clk_put`, `of_clk_get`, `of_clk_get_by_name`, and `of_clk_get_from_provider`.

Control flow: Consumers first obtain references with get APIs, then prepare in sleepable context and enable in atomic-capable context. `clk_prepare_enable` rolls back prepare if enable fails; the bulk helper mirrors that pattern for multiple clocks. Rate and parent changes enter the CCF tree, notify registered callbacks, and may propagate to parents. Optional getters normalize missing clocks to `NULL`; managed getters bind cleanup to device lifetime. When `CONFIG_COMMON_CLK`, `CONFIG_HAVE_CLK_PREPARE`, or `CONFIG_HAVE_CLK` are off, inline stubs preserve buildability and usually return success, `NULL`, `0`, or `-ENOTSUPP` depending on the API.

State and persistence behavior: The header itself owns no storage. State lives in acquired `struct clk` handles, reference counts in the clock core, devres entries, notifier lists, rate range constraints, exclusive-rate locks, prepare/enable counts, and provider hardware. Correct behavior depends on strict balancing of get/put, prepare/unprepare, enable/disable, and exclusive get/put calls.

Dependencies and integration points: It includes `<linux/err.h>`, `<linux/kernel.h>`, and `<linux/notifier.h>`. It integrates with platform and DT clock providers, devres, SRCU notifier chains, PM suspend/resume paths, and nearly every device driver that needs clocks.

Risks: Calling `clk_prepare` or get/put APIs from interrupt context violates documented sleeping rules; forgetting to balance usage counts leaves clocks running or shuts them off while shared; relying on stub success when clock support is disabled can hide missing dependencies; optional clocks must be checked for `NULL`; rate notifiers must handle abort paths; exclusive-rate users must release exclusivity or block future changes.

Test signals: Driver probe/remove tests should check resource unwind, managed cleanup, and optional-clock behavior. Runtime tests should cover repeated prepare/enable/disable/unprepare cycles, failure injection for bulk acquisition and enable rollback, rate changes with notifiers, suspend/resume `clk_save_context` and `clk_restore_context`, and clock summary/debugfs inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/analogbits-wrpll-cln28hpc.h -->
# sources/distributed-fs/ceph-client/include/linux/clk/analogbits-wrpll-cln28hpc.h

Purpose: This header describes configuration helpers for Analog Bits WRPLL CLN28HPC PLLs, used by clock drivers that need to calculate PLL divisors and output rates.

Important APIs/types/functions: It defines `DIVQ_VALUES`, flag masks and shifts for bypass, reset, internal feedback, and external feedback, and `struct wrpll_cfg` with public PLL fields `divr`, `divq`, `range`, `flags`, and `divf`. Helper functions are `wrpll_configure_for_rate`, `wrpll_calc_max_lock_us`, and `wrpll_calc_output_rate`.

Control flow: Callers zero-initialize `struct wrpll_cfg`, set a feedback-mode flag, ask `wrpll_configure_for_rate` to search parameters for a target rate and parent rate, then program hardware with the resulting fields. Output-rate and lock-time helpers derive calculated behavior from an existing config.

State and persistence behavior: Public fields map to PLL signal values; private fields cache output rates across DIVQ values and remember parent-rate search bounds. No persistent state is stored by the header itself, but chosen divisor values become hardware state after driver programming.

Dependencies and integration points: It includes `<linux/types.h>` and is consumed by WRPLL-capable clock drivers, especially SoC PLL providers that bridge hardware-specific PLL math into CCF rate callbacks.

Risks: `divr` and `divf` are hardware values, not plain divisors, and `divq` is a power-of-two divider with `0` invalid. External feedback is documented as unsupported by this driver, so setting that flag without implementation support is risky. Stale cached parent-rate fields can be wrong if a config is reused without recalculation.

Test signals: Rate-rounding tests should verify target-rate search, output-rate reconstruction, lock-time bounds, invalid DIVQ handling, feedback-mode flags, and parent-rate changes. Hardware bring-up should confirm PLL lock and measured output frequencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/analogbits-wrpll-cln28hpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/at91_pmc.h -->
# sources/distributed-fs/ceph-client/include/linux/clk/at91_pmc.h

Purpose: This is the AT91/SAMA Power Management Controller register-map header. It provides offsets, masks, status bits, write-protect keys, PLL fields, programmable-clock fields, USB/audio clock controls, and wake-up bits used by AT91 clock and PM drivers.

Important APIs/types/functions: It exports register offsets such as `AT91_PMC_SCER`, `AT91_PMC_SCDR`, `AT91_PMC_SCSR`, `AT91_CKGR_MOR`, `AT91_CKGR_PLLAR`, `AT91_CKGR_PLLBR`, `AT91_PMC_MCKR`, `AT91_PMC_PCKR(n)`, `AT91_PMC_SR`, `AT91_PMC_PROT`, `AT91_PMC_WPSR`, `AT91_PMC_PCR`, and audio PLL registers. Important masks include oscillator enable/select bits, PLL multiplier/divider fields, master-clock source/prescaler/divider fields, status bits such as `AT91_PMC_MCKRDY` and `AT91_PMC_LOCK*`, `AT91_PMC_KEY`, write-protect fields, and helper macros such as `AT91_PMC_MUL_GET`, `AT91_PMC3_MUL_GET`, `AT91_PMC_SMDDIV`, and `AT91_PMC_MCR_V2_ID`.

Control flow: There is no executable control flow in the header. Drivers use these definitions to sequence oscillator and PLL setup, wait on status bits, enable peripheral/generated clocks, configure programmable clocks, manage write protection, and handle wake events. Several offsets are SoC-version-specific or reused for different registers on different families.

State and persistence behavior: The state is entirely in PMC hardware registers. Register writes persist until reset, power-state loss, or later driver reprogramming. Some fields such as write-protect state and wake-up masks can affect subsequent register access and low-power behavior.

Dependencies and integration points: It includes `<linux/bits.h>` and integrates with AT91 clocksource, CCF, PM, USB, audio, watchdog/wakeup, and SoC initialization code that maps PMC registers.

Risks: Register offsets overlap by SoC generation, so using a SAM9X60/SAMA7G5 definition on older hardware can program the wrong register. Missing the `AT91_PMC_KEY` or write-protect key causes silent write failures. PLL and master-clock prescaler fields differ across families, and readiness/status bits must be polled before consumers use the clock.

Test signals: Boot tests on each AT91/SAMA family, PLL lock and master-clock ready polling, peripheral clock enable/disable tests, suspend/resume wake-source validation, write-protect violation checks, and measured USB/audio/generated clock frequencies are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/at91_pmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/clk-conf.h -->
# sources/distributed-fs/ceph-client/include/linux/clk/clk-conf.h

Purpose: This header exposes the Devicetree clock-default application helper used to apply assigned-clock parents and rates from firmware nodes.

Important APIs/types/functions: The only API is `of_clk_set_defaults(struct device_node *node, bool clk_supplier)`, with a stub returning `0` when either OF or Common Clock Framework support is disabled.

Control flow: Clock providers or consumers call the helper during probe or early initialization. The real implementation reads clock default properties from the node and applies parent/rate assignments, while the stub is a no-op.

State and persistence behavior: The header stores no state. The real helper mutates clock framework state and hardware rates/parents based on DT configuration.

Dependencies and integration points: It includes `<linux/types.h>`, forward-declares `struct device_node`, and integrates with OF clock parsing, CCF rate/parent operations, and platform driver probe ordering.

Risks: Calling with the wrong `clk_supplier` role can apply defaults at the wrong time. Disabled configs returning success can hide absent default processing. DT defaults can conflict with consumer rate constraints or exclusive-rate users.

Test signals: DT boot tests with `assigned-clocks`, `assigned-clock-parents`, and `assigned-clock-rates`, probe-order tests for suppliers and consumers, and clock tree inspection after probe validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/clk-conf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/davinci.h -->
# sources/distributed-fs/ceph-client/include/linux/clk/davinci.h

Purpose: This compact header exposes early registration for TI DaVinci DA850 PLL0 clocks.

Important APIs/types/functions: It includes `<linux/device.h>` and `<linux/regmap.h>` and declares `da850_pll0_init(struct device *dev, void __iomem *base, struct regmap *cfgchip)`.

Control flow: Board or platform clock initialization passes a device, mapped PLL register base, and CFGCHIP regmap into `da850_pll0_init`, which registers the relevant clocks in the implementation.

State and persistence behavior: The header owns no state. The implementation will use MMIO and regmap-backed hardware state plus CCF registrations.

Dependencies and integration points: It integrates DaVinci PLL/PSC clock-controller code with platform device setup, CCF registration, and system configuration registers reachable through regmap.

Risks: Passing an unmapped or wrong base address or CFGCHIP regmap can corrupt unrelated clock configuration. Because this is early boot plumbing, probe ordering and availability of the regmap matter.

Test signals: DA850 boot logs, CCF clock tree contents, PLL0-derived clock rates, PSC consumer probe success, and suspend/resume behavior are the key checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/davinci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/imx.h -->
# sources/distributed-fs/ceph-client/include/linux/clk/imx.h

Purpose: This header exposes an i.MX6SL clock-control hook for wait-mode clock handling.

Important APIs/types/functions: The API is `imx6sl_set_wait_clk(bool enter)`, declared after including `<linux/types.h>`.

Control flow: i.MX platform PM code calls this hook when entering or leaving wait mode; the implementation adjusts the SoC wait clock selection or gating.

State and persistence behavior: State lives in SoC clock registers. The boolean indicates transition direction; the header stores no state.

Dependencies and integration points: It integrates i.MX clock code with low-power state entry/exit code and architecture-specific PM flows.

Risks: Calling it for the wrong SoC or wrong transition direction can leave wait-mode clocks misconfigured, affecting wakeup and low-power stability.

Test signals: i.MX6SL suspend/wait-mode entry and wake tests, clock register traces, and wake-source validation provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/imx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/mxs.h -->
# sources/distributed-fs/ceph-client/include/linux/clk/mxs.h

Purpose: This header exposes a Freescale/NXP MXS SAIF clock-mux selector.

Important APIs/types/functions: The only API is `mxs_saif_clkmux_select(unsigned int clkmux)`.

Control flow: Audio or clock setup code calls the helper with a mux selector to choose the SAIF clock source.

State and persistence behavior: State is the hardware mux selection. The header stores no state and has no fallback stub.

Dependencies and integration points: It integrates MXS clock code with SAIF audio clock consumers and SoC register programming.

Risks: Invalid mux values can route audio clocks incorrectly or break sample-rate generation. Callers need SoC-specific knowledge of valid selectors.

Test signals: Audio playback/capture clock-rate tests, mux register readback, and probe failures from SAIF consumers are useful validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/mxs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/pxa.h -->
# sources/distributed-fs/ceph-client/include/linux/clk/pxa.h

Purpose: This header declares PXA clock initialization and PXA3xx frequency/ACCR update helpers.

Important APIs/types/functions: APIs are `pxa25x_clocks_init`, `pxa27x_clocks_init`, `pxa3xx_clocks_init`, `pxa3xx_get_clk_frequency_khz`, and `pxa3xx_clk_update_accr`. For non-`CONFIG_PXA3xx`, the latter two are macros returning `0` or doing nothing.

Control flow: Early PXA platform code passes mapped clock-register bases to the init functions. PXA3xx-specific code can query clock frequency in kHz and update ACCR bits through disable/enable/xclkcfg/mask arguments.

State and persistence behavior: State is in PXA clock registers and the CCF registrations created by the implementation. Non-PXA3xx builds intentionally compile out dynamic PXA3xx operations.

Dependencies and integration points: It includes compiler and type headers and integrates with ARM PXA board init, CCF registration, and SoC-specific power/clock code.

Risks: These APIs take raw `void __iomem *` register bases, so incorrect mapping is high impact. Stubbed PXA3xx helpers can hide code paths that should be conditional on `CONFIG_PXA3xx`.

Test signals: PXA25x/PXA27x/PXA3xx boot tests, rate readouts, ACCR register readback, and peripheral probe coverage validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/pxa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/renesas.h -->
# sources/distributed-fs/ceph-client/include/linux/clk/renesas.h

Purpose: This header gathers Renesas CPG/MSTP/MSSR integration hooks and RZ/V2H PLL parameter-search structures for Renesas clock drivers.

Important APIs/types/functions: It declares `cpg_mstp_add_clk_domain`, optional `cpg_mstp_attach_dev`/`detach_dev`, optional `cpg_mssr_attach_dev`/`detach_dev`, `rzg2l_cpg_dsi_div_set_divider`, enum targets `PLL5_TARGET_DPI` and `PLL5_TARGET_DSI`, PLL limit/parameter structures `struct rzv2h_pll_limits`, `struct rzv2h_pll_pars`, and `struct rzv2h_pll_div_pars`, macro `RZV2H_CPG_PLL_DSI_LIMITS`, and helpers `rzv2h_get_pll_pars` and `rzv2h_get_pll_divs_pars`. Disabled configs provide `NULL`, no-op, or `false` fallbacks.

Control flow: CPG drivers add clock power domains and attach/detach devices through PM-domain callbacks when corresponding drivers are built. RZ/G2L DSI code can update PLL5 divider state. RZ/V2H code supplies frequency targets in millihertz and receives best PLL/divider parameters constrained by the limits structures.

State and persistence behavior: Runtime state is in Renesas CPG registers, PM domains, and calculated PLL parameter structs. The header includes parameter-cache fields such as best frequencies and signed error values but stores nothing globally itself.

Dependencies and integration points: It includes `<linux/clk-provider.h>`, `<linux/types.h>`, and `<linux/units.h>`. It integrates CPG clock providers, generic PM domains, display DSI/DPI consumers, and Renesas SoC-specific PLL search implementations.

Risks: Config-dependent `NULL` attach hooks must be handled by PM-domain users. Millihertz units in PLL helpers are easy to confuse with hertz. Wrong limits or divider tables can select unstable PLL settings. DSI/DPI target confusion can break display clocking.

Test signals: Renesas boot and PM-domain attach logs, display clock-rate validation, PLL parameter unit tests, DSI/DPI mode-setting tests, and suspend/resume coverage are meaningful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/renesas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/samsung.h -->
# sources/distributed-fs/ceph-client/include/linux/clk/samsung.h

Purpose: This header exposes Samsung S3C64xx common-clock initialization.

Important APIs/types/functions: The API is `s3c64xx_clk_init(struct device_node *np, unsigned long xtal_f, unsigned long xusbxti_f, bool s3c6400, void __iomem *base)`, with a no-op inline fallback when `CONFIG_S3C64XX_COMMON_CLK` is disabled.

Control flow: Platform or DT clock setup calls the function with the controller node, crystal frequencies, SoC variant boolean, and mapped base address. The real implementation registers the S3C64xx clocks.

State and persistence behavior: State lives in clock registers and CCF registrations. The disabled fallback stores nothing and silently skips setup.

Dependencies and integration points: It includes compiler type support, forward-declares `struct device_node`, and integrates Samsung ARM platform init with the CCF.

Risks: Wrong external oscillator frequency values propagate into incorrect derived rates. The `s3c6400` variant flag must match hardware. The no-op fallback can hide missing clock registration in incorrectly configured builds.

Test signals: S3C64xx DT boot, clock tree inspection, UART/timer/peripheral rates, and variant-specific board tests validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/samsung.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/spear.h -->
# sources/distributed-fs/ceph-client/include/linux/clk/spear.h

Purpose: This header declares early clock initialization entry points for ST SPEAr SoC families.

Important APIs/types/functions: APIs are `spear3xx_clk_init`, `spear6xx_clk_init`, `spear1310_clk_init`, and `spear1340_clk_init`, each guarded by the relevant `CONFIG_ARCH_*` or machine option with no-op fallback stubs.

Control flow: Architecture setup passes mapped miscellaneous, SoC config, or RAS register bases to the matching init function. The implementation registers clocks and programs family-specific setup.

State and persistence behavior: State is hardware register configuration and CCF registration. Disabled-family builds intentionally compile calls into no-ops.

Dependencies and integration points: The header integrates SPEAr platform init, early boot MMIO mapping, and CCF provider setup.

Risks: Passing the wrong base pointer or compiling with the wrong family option can leave required clocks unregistered. The `__init` lifecycle means pointers and functions are intended for boot-time only.

Test signals: Family-specific boot tests, clock tree inspection, peripheral probe success, and compile coverage for each guarded configuration are the useful checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/spear.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/sunxi-ng.h -->
# sources/distributed-fs/ceph-client/include/linux/clk/sunxi-ng.h

Purpose: This header exposes Allwinner sunxi-ng clock-control helpers for MMC timing mode and the sun6i RTC CCU probe.

Important APIs/types/functions: APIs are `sunxi_ccu_set_mmc_timing_mode(struct clk *clk, bool new_mode)`, `sunxi_ccu_get_mmc_timing_mode(struct clk *clk)`, and `sun6i_rtc_ccu_probe(struct device *dev, void __iomem *reg)`.

Control flow: MMC drivers or platform code call set/get timing mode on a `struct clk`; RTC CCU platform code probes with a device and mapped register base.

State and persistence behavior: State lives in CCU registers and clock-provider structures. The header itself stores none.

Dependencies and integration points: It relies on visible declarations for `struct clk`, `struct device`, and MMIO types from including contexts, and integrates sunxi-ng CCU providers with MMC and RTC subsystems.

Risks: Timing mode must match the MMC controller and card mode; a wrong setting can produce data corruption. The RTC CCU probe requires a valid MMIO base.

Test signals: MMC mode-switch tests, high-speed card I/O, CCU register readback, RTC clock availability, and Allwinner boot logs validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/sunxi-ng.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/tegra.h -->
# sources/distributed-fs/ceph-client/include/linux/clk/tegra.h

Purpose: This header exposes NVIDIA Tegra CPU clock/reset control wrappers, EMC clock callbacks and providers, and Tegra210 PLL/USB/SATA/EMC control hooks.

Important APIs/types/functions: Core type `struct tegra_cpu_car_ops` contains CPU reset, clock, and PM callbacks. Wrappers include `tegra_wait_cpu_in_reset`, `tegra_put_cpu_in_reset`, `tegra_cpu_out_of_reset`, `tegra_enable_cpu_clock`, `tegra_disable_cpu_clock`, `tegra_cpu_rail_off_ready`, `tegra_cpu_clock_suspend`, and `tegra_cpu_clock_resume`. EMC types include callback typedefs for Tegra20 and Tegra124, `struct tegra210_clk_emc_config`, and `struct tegra210_clk_emc_provider`. Tegra210 APIs cover PLLE hardware sequencing, XUSB/SATA PLL hardware control, UTMIPLL IDDQ, MBIST workaround handling, EMC DLL/source updates, and `tegra210_clk_emc_attach`/`detach`.

Control flow: On Tegra builds, inline CPU wrappers validate callback pointers with `WARN_ON` and dispatch through global `tegra_cpu_car_ops`; otherwise they become no-ops. PM wrappers exist only when sleep support is enabled. EMC callback registration lets memory-controller code coordinate timing changes with clock rate changes. Tegra210-specific helpers are compiled in only for Tegra210; other builds use stubs.

State and persistence behavior: State lives in the global ops pointer, clock/reset hardware registers, EMC provider config arrays, and PLL/IDDQ hardware state. The header stores no persistent data but exposes paths that alter CPU reset, CPU clock, memory clock, and PLL state.

Dependencies and integration points: It includes `<linux/types.h>` and `<linux/bug.h>`, and integrates with Tegra architecture CPU hotplug/reset code, PM sleep, memory controller timing, XUSB/SATA PHY clocking, and CCF providers.

Risks: Missing `tegra_cpu_car_ops` callbacks trigger warnings and skipped operations, which can break CPU bring-up or hotplug. EMC timing callbacks must be ordered around rate changes or memory instability can result. Tegra210 stubs returning success can hide missing platform support in generic builds.

Test signals: Tegra CPU hotplug, suspend/resume, rail-off readiness, EMC frequency switching, XUSB/SATA link bring-up, PLL sequence status, MBIST workaround paths, and compile coverage across Tegra generations are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/tegra.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/ti.h -->
# sources/distributed-fs/ceph-client/include/linux/clk/ti.h

Purpose: This header is the TI OMAP clock-driver support contract. It describes OMAP register references, DPLL data, OMAP-specific `clk_hw` state, low-level register/clockdomain operations, init hooks, feature flags, and context save/restore helpers.

Important APIs/types/functions: Main structures are `struct clk_omap_reg`, `struct dpll_data`, `struct clk_hw_omap_ops`, `struct clk_hw_omap`, `struct ti_clk_ll_ops`, and `struct ti_clk_features`. Flags include `ENABLE_REG_32BIT`, `CLOCK_IDLE_CONTROL`, `CLOCK_NO_IDLE_PARENT`, `ENABLE_ON_INIT`, `INVERT_ENABLE`, `CLOCK_CLKOUTX2`, DPLL mode constants, `DPLL_J_TYPE`, and feature bits such as `TI_CLK_DPLL_HAS_FREQSEL`, `TI_CLK_DPLL4_DENY_REPROGRAM`, `TI_CLK_DISABLE_CLKDM_CONTROL`, `TI_CLK_ERRATA_I810`, `TI_CLK_CLKCTRL_COMPAT`, and `TI_CLK_DEVICE_TYPE_GP`. APIs include autoidle controls, DPLL recalc/reprogram helpers, clockdomain setup, low-level ops setup, DT/legacy provider init for many OMAP/AM/DRA SoCs, feature setup/getters, standby checks, and DPLL context save/restore.

Control flow: TI clock init registers low-level ops, maps PRCM/CM regions, initializes DT or legacy providers, and exposes OMAP-specific hardware clocks through CCF. Clock operations use `clk_hw_omap` state and low-level ops for MMIO/regmap access and clockdomain coordination. DPLL helpers cache rounded parameters and reprogram PLL registers. Context save/restore functions preserve DPLL state across low-power transitions.

State and persistence behavior: The structures include persistent runtime state such as fixed rates, enable registers, DPLL rounded-rate caches, clockdomain pointers, autoidle counts, context fields, and global feature flags. Hardware state lives in PRCM/CM/DPLL registers.

Dependencies and integration points: It includes `<linux/clk-provider.h>` and `<linux/clkdev.h>`, and integrates with OMAP clockdomain code, DT clock providers, legacy board files, DPLL implementations, PM context handling, and CCF helpers.

Risks: Several `dpll_data` fields are runtime caches mixed with fixed data, and comments warn they should ideally be separated. Incorrect low-level ops or register indices can corrupt PRCM state. Autoidle and clockdomain control mistakes can cause hangs or power regressions. Legacy init stubs return `-ENXIO`, so callers must handle unavailable SoC support.

Test signals: OMAP/AM/DRA boot tests, DPLL rate-change and lock tests, clockdomain idle/active transitions, suspend/resume DPLL context validation, DT and legacy provider compile paths, and clock tree/rate inspection are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/ti.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/zynq.h -->
# sources/distributed-fs/ceph-client/include/linux/clk/zynq.h

Purpose: This header exposes Xilinx Zynq clock initialization and PLL registration.

Important APIs/types/functions: APIs are `zynq_clock_init(void)` and `clk_register_zynq_pll(const char *name, const char *parent, void __iomem *pll_ctrl, void __iomem *pll_status, u8 lock_index, spinlock_t *lock)`.

Control flow: Platform init calls `zynq_clock_init` to register the clock tree. PLL providers call `clk_register_zynq_pll` with names, parent, control/status MMIO addresses, lock-bit index, and a shared spinlock.

State and persistence behavior: State is in Zynq PLL control/status registers and CCF registration objects. The spinlock serializes register updates. The header stores no state.

Dependencies and integration points: It includes `<linux/spinlock.h>` and integrates Zynq platform clock setup with CCF and MMIO PLL control.

Risks: Wrong lock-bit index or status register can make PLL lock detection unreliable. Register operations must be serialized with the provided lock when shared. Name/parent strings form clock-tree lookup contracts.

Test signals: Zynq boot tests, PLL lock polling, rate measurement, clock tree inspection, and concurrent clock-rate update stress are useful checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clk/zynq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clkdev.h -->
# sources/distributed-fs/ceph-client/include/linux/clkdev.h

Purpose: This header provides the legacy clock lookup table helper layer used by the clock API to map device IDs and connection IDs to `struct clk` or `struct clk_hw`.

Important APIs/types/functions: It defines `struct clk_lookup` with list node, `dev_id`, `con_id`, `clk`, and `clk_hw`; macro `CLKDEV_INIT`; and APIs `clkdev_add`, `clkdev_drop`, `clkdev_create`, `clkdev_hw_create`, `clkdev_add_table`, `clk_add_alias`, `clk_register_clkdev`, `clk_hw_register_clkdev`, and `devm_clk_hw_register_clkdev`.

Control flow: Board or provider code creates lookup entries, adds them to the global clkdev list, and the consumer clock lookup path matches `dev_id`/`con_id` during `clk_get`-style calls. Devm registration binds lookup removal to device lifetime.

State and persistence behavior: Lookup entries persist in a global list until dropped or devres cleanup runs. Entries may point at either a consumer `struct clk` or provider `struct clk_hw`.

Dependencies and integration points: It includes `<linux/slab.h>` and integrates with the legacy non-DT clock lookup path, board files, CCF providers, and `clk_get_sys`.

Risks: Duplicate or overly broad `dev_id`/`con_id` entries can resolve the wrong clock. Lifetime must outlive consumers; dropping entries too early breaks lookup, while never dropping dynamically created entries leaks memory. Format-string creation must be used carefully.

Test signals: Legacy board boot, `clk_get` lookup success/failure tests, alias tests, module unload cleanup, and duplicate lookup audits validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clkdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clockchips.h -->
# sources/distributed-fs/ceph-client/include/linux/clockchips.h

Purpose: This header defines the clock-event device abstraction used by timer and tick code to program interrupts for periodic, oneshot, stopped, shutdown, and detached states.

Important APIs/types/functions: It defines `enum clock_event_state`, feature flags such as `CLOCK_EVT_FEAT_PERIODIC`, `CLOCK_EVT_FEAT_ONESHOT`, `CLOCK_EVT_FEAT_C3STOP`, `CLOCK_EVT_FEAT_DYNIRQ`, `CLOCK_EVT_FEAT_PERCPU`, and `CLOCK_EVT_FEAT_HRTIMER`, and `struct clock_event_device`. The struct contains event programming callbacks, state transition callbacks, suspend/resume hooks, conversion fields `mult`/`shift`, min/max delta values in ns and ticks, feature/rating/IRQ/CPU mask metadata, and list/module ownership. Helpers include `clockevent_state_*`, `div_sc`, `clockevent_delta2ns`, `clockevents_register_device`, `clockevents_unbind_device`, `clockevents_config_and_register`, `clockevents_update_freq`, `clockevents_calc_mult_shift`, `clockevents_suspend`, `clockevents_resume`, and broadcast helpers.

Control flow: A timer driver fills `struct clock_event_device`, configures conversion factors, registers it, and implements callbacks for mode transitions and next-event programming. Tick code selects devices by rating/features, calls state transition callbacks, programs deadlines, and handles broadcast when local timers stop in idle states. Disabled `CONFIG_GENERIC_CLOCKEVENTS` builds expose only empty suspend/resume and broadcast stubs.

State and persistence behavior: Runtime state includes current clockevent state, next event, retry counters, min/max deltas, CPU binding, feature flags, and list membership in clockevents core. Hardware state is represented by driver callbacks.

Dependencies and integration points: With generic clockevents enabled it includes clocksource, cpumask, ktime, and notifier headers. It integrates with tick, hrtimer broadcast, CPU idle, clocksource coupled mode, IRQ affinity, and architecture timer drivers.

Risks: Wrong min/max delta or multiplier/shift values cause missed or early timer interrupts. State transitions must match hardware power state. Broadcast feature flags are critical for timers that stop in idle. Callback sleepability and interrupt context assumptions must be respected.

Test signals: Timer interrupt smoke tests, high-resolution timer tests, CPU idle with broadcast, suspend/resume tick recovery, CPU hotplug, clockevent frequency updates, and latency/early-expiry tracing are key validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clockchips.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clocksource.h -->
# sources/distributed-fs/ceph-client/include/linux/clocksource.h

Purpose: This header defines the clocksource abstraction for free-running counters used by timekeeping, plus helper math and registration/probe hooks.

Important APIs/types/functions: It defines `struct clocksource`, flags such as `CLOCK_SOURCE_IS_CONTINUOUS`, `CLOCK_SOURCE_MUST_VERIFY`, `CLOCK_SOURCE_WATCHDOG`, `CLOCK_SOURCE_VALID_FOR_HRES`, `CLOCK_SOURCE_UNSTABLE`, `CLOCK_SOURCE_SUSPEND_NONSTOP`, `CLOCK_SOURCE_CAN_INLINE_READ`, and `CLOCK_SOURCE_HAS_COUPLED_CLOCK_EVENT`, macro `CLOCKSOURCE_MASK`, conversion helpers `clocksource_freq2mult`, `clocksource_khz2mult`, `clocksource_hz2mult`, and `clocksource_cyc2ns`, registration/update helpers `clocksource_register_hz`, `clocksource_register_khz`, `__clocksource_register`, `__clocksource_update_freq_hz`, `__clocksource_update_freq_khz`, watchdog and suspend helpers, MMIO helpers, `clocksource_mmio_init`, `clocksource_i8253_init`, timer declaration macros `TIMER_OF_DECLARE` and `TIMER_ACPI_DECLARE`, `timer_probe`, and `struct clocksource_base`.

Control flow: Clocksource drivers fill a `struct clocksource` with a `read` callback, mask, rating, frequency conversion values, flags, and optional enable/disable/suspend/resume/watchdog hooks, then register it. Timekeeping selects a suitable source by rating and validity, caches hot-path fields elsewhere, and uses watchdog validation to mark unstable sources. OF/ACPI timer declarations hook probe functions into early timer discovery.

State and persistence behavior: Runtime state includes registered list nodes, frequency, mask, conversion factors, watchdog last values, selected clocksource identity, suspend timing, and base-clock relationships. The source struct is not itself the timekeeping hot path but persists while registered.

Dependencies and integration points: It includes time, list, timer, init, OF, clocksource ID, architecture division/MMIO, optional architecture clocksource data, and VDSO clocksource mode. Integration points are timekeeping, sched_clock-adjacent counter drivers, watchdog validation, MMIO counter helpers, DT/ACPI timer probing, and VDSO mode selection.

Risks: Counter masks, mult/shift, and frequency units must be correct or system time drifts. Rating inflation can select an inferior source. Sources marked continuous or suspend-nonstop incorrectly can break idle or suspend accounting. Watchdog fields and unstable marking must be honored to avoid bad timekeeping.

Test signals: Timekeeping selftests, NTP/clock drift monitoring, watchdog instability logs, suspend/resume time continuity, high-resolution timer enablement, VDSO clock mode checks, and MMIO counter wrap tests validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clocksource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clocksource_ids.h -->
# sources/distributed-fs/ceph-client/include/linux/clocksource_ids.h

Purpose: This header defines stable IDs for known clocksource bases so snapshots and coupled clock-event logic can identify the underlying time source.

Important APIs/types/functions: It exports `enum clocksource_ids` with `CSID_GENERIC`, `CSID_ARM_ARCH_COUNTER`, `CSID_S390_TOD`, `CSID_X86_TSC_EARLY`, `CSID_X86_TSC`, `CSID_X86_KVM_CLK`, `CSID_X86_ART`, and `CSID_MAX`.

Control flow: There is no runtime control flow. Clocksource drivers set IDs in `struct clocksource` or `struct clocksource_base`; consumers compare IDs when validating snapshots.

State and persistence behavior: IDs are compile-time constants and become part of internal timekeeping contracts. Adding or changing values affects cross-subsystem identification.

Dependencies and integration points: It is included by `clocksource.h` and used by architecture clocksources, VDSO/time snapshot paths, and clockevent coupled-mode metadata.

Risks: Reordering or reusing enum values can make saved IDs ambiguous. New clocksources should choose a generic or specific ID intentionally.

Test signals: Compile coverage for architecture clocksources, time snapshot validation tests, VDSO mode checks, and coupled clockevent tests are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/clocksource_ids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/closure.h -->
# sources/distributed-fs/ceph-client/include/linux/closure.h

Purpose: This header defines the bcache-style closure abstraction: a reference-counted asynchronous control-flow and wait primitive for operations that need to wait on multiple in-flight tasks and then continue synchronously or on a workqueue.

Important APIs/types/functions: Types include `struct closure_waitlist`, `enum closure_state`, `struct closure`, `struct closure_syncer`, and `closure_fn`. APIs and macros include `closure_get`, `closure_get_not_zero`, `closure_put`, `closure_sub`, `closure_wait`, `closure_wake_up`, `closure_sync`, `closure_sync_timeout`, `closure_init`, `closure_init_stack`, `closure_init_stack_release`, `continue_at`, `continue_at_nobarrier`, `closure_return`, `closure_return_sync`, `closure_return_with_destructor`, `closure_call`, `closure_wait_event`, `closure_wait_event_timeout`, `CLOSURE_CALLBACK`, and `closure_type`. Debug support adds magic values, IP tracking, and create/destroy hooks under `CONFIG_DEBUG_CLOSURES`.

Control flow: A closure starts with a running reference. Users add references for in-flight work with `closure_get` and drop them with `closure_put`. `closure_sync` sleeps until only the running reference remains. `continue_at` sets the next function/workqueue and drops the running reference so the next closure function runs once outstanding references reach zero; callers are expected to return immediately. Wait-list helpers park closures until `closure_wake_up`.

State and persistence behavior: State is held in `atomic_t remaining`, state bits for destructor/waiting/running, parent pointer, next function/workqueue, linked-list node, optional work_struct overlay, debug metadata, and whether `closure_get` happened. Parent closures hold a lifetime reference until child completion. Stack closures use special initialization.

Dependencies and integration points: It includes llist, sched, task stack, and workqueue support and is used by bcache-style asynchronous storage code. It integrates with workqueues, wait lists, atomics, memory barriers, jiffies timeouts, and debugfs through `bcache_debug`.

Risks: The comments emphasize strict ownership: after `continue_at`, the caller no longer owns the closure and must return. Missing `closure_put`, transferring references incorrectly, reusing stack closures after return, or waiting without the required wakeup can deadlock or use-after-free. The 32-bit `remaining` bit layout mixes count and state bits, so arithmetic must use the provided helpers.

Test signals: Concurrency stress with multiple completions, debug closure assertions, timeout paths, parent/child closure completion, wait-list wakeups, workqueue vs direct callback execution, and KCSAN/KASAN/KMSAN runs are the best validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/closure.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cma.h -->
# sources/distributed-fs/ceph-client/include/linux/cma.h

Purpose: This header exposes the Contiguous Memory Allocator interface for declaring reserved CMA areas and allocating/releasing contiguous page ranges from them.

Important APIs/types/functions: It defines `MAX_CMA_AREAS` from `CONFIG_CMA_AREAS`, `CMA_MAX_NAME`, `CMA_MIN_ALIGNMENT_PAGES`, `CMA_MIN_ALIGNMENT_BYTES`, opaque `struct cma`, global `totalcma_pages`, getters `cma_get_base`, `cma_get_size`, `cma_get_name`, declaration helpers `cma_declare_contiguous_nid`, `cma_declare_contiguous`, `cma_declare_contiguous_multi`, `cma_init_reserved_mem`, allocation helpers `cma_alloc`, `cma_release`, frozen variants, iterator `cma_for_each_area`, intersection test `cma_intersects`, and `cma_reserve_pages_on_error`.

Control flow: Early boot or reserved-memory code declares or initializes CMA regions. Runtime users allocate contiguous pages from a selected area with count/alignment/no-warn arguments and later release them. Iterator and intersection helpers support diagnostics and memory-management decisions.

State and persistence behavior: CMA areas persist after early declaration and own pageblocks marked for migratable contiguous allocations. `totalcma_pages` records aggregate reserved pages. Allocations mutate page ownership and migration state until released.

Dependencies and integration points: It includes init, types, and NUMA support. It integrates with memblock/reserved memory setup, buddy allocator pageblocks, DMA subsystems, device drivers needing physically contiguous memory, and NUMA placement.

Risks: Alignment must respect pageblock constraints. Overlapping or wrongly sized regions can steal memory or break DMA. Failure to release CMA pages causes long-lived memory pressure. Frozen allocation paths need careful pairing with frozen releases.

Test signals: Boot logs for CMA reservation, DMA allocation tests, page migration/compaction stress, NUMA-specific area declarations, `/proc/meminfo` CMA counters, and driver allocation/release loops are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cmpxchg-emu.h -->
# sources/distributed-fs/ceph-client/include/linux/cmpxchg-emu.h

Purpose: This header declares an emulated byte-sized compare-exchange helper for architectures that lack direct 1-byte or 2-byte cmpxchg operations and implement them through wider atomics.

Important APIs/types/functions: The exported API is `uintptr_t cmpxchg_emu_u8(volatile u8 *p, uintptr_t old, uintptr_t new)`.

Control flow: Architecture or generic atomic code calls the helper when it needs cmpxchg semantics for an 8-bit target. The implementation performs the emulation, typically using a 32-bit cmpxchg around the containing word.

State and persistence behavior: No state is stored in the header. State mutation is the atomic update of the byte pointed to by `p`, returning the observed old value in cmpxchg style.

Dependencies and integration points: It relies on integer and `u8` types from including contexts and integrates with architecture atomic implementations and generic cmpxchg fallback code.

Risks: Emulation must preserve atomicity for the target byte without corrupting neighboring bytes. Alignment, endian layout, and volatile access rules are critical. Return type width must match generic cmpxchg expectations.

Test signals: Atomic cmpxchg selftests on architectures using the fallback, KCSAN stress, unaligned/neighbor-byte tests where allowed, and build coverage for small-width atomics validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cmpxchg-emu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cn_proc.h -->
# sources/distributed-fs/ceph-client/include/linux/cn_proc.h

Purpose: This header exposes process-event connector hooks used to publish fork, exec, id/session, ptrace, comm, coredump, and exit events to the connector subsystem.

Important APIs/types/functions: With `CONFIG_PROC_EVENTS`, it declares `proc_fork_connector`, `proc_exec_connector`, `proc_id_connector`, `proc_sid_connector`, `proc_ptrace_connector`, `proc_comm_connector`, `proc_coredump_connector`, and `proc_exit_connector`. Without the config, all helpers are inline no-ops. It includes the UAPI event definitions from `<uapi/linux/cn_proc.h>`.

Control flow: Process lifecycle code calls the relevant helper at event points. The implementation emits connector messages when proc events are enabled; otherwise calls compile away.

State and persistence behavior: The header stores no state. Runtime state belongs to task structs, connector sockets, and proc-event listener configuration.

Dependencies and integration points: It integrates scheduler/process lifecycle paths with the connector/netlink UAPI and userspace event listeners.

Risks: Event hooks must be placed where task identity fields are stable and locking is appropriate. No-op stubs mean code must not depend on side effects. Connector event ordering matters for monitoring tools.

Test signals: Userspace proc connector listener tests for fork/exec/exit and credential/session changes, config-off build coverage, and lifecycle stress tests are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cn_proc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cnt32_to_63.h -->
# sources/distributed-fs/ceph-client/include/linux/cnt32_to_63.h

Purpose: This header provides a lock-free macro to extend a frequently sampled 32-bit hardware counter into a 63-bit monotonic-ish value for uses such as `sched_clock`.

Important APIs/types/functions: It defines endian-aware `union cnt32_to_63` and macro `cnt32_to_63(cnt_lo)`. The macro uses a static high word, a read memory barrier, sign-bit comparison between high and low halves, and updates the high word when the 32-bit counter crosses half-period.

Control flow: Callers pass a direct hardware counter expression to `cnt32_to_63`. The macro reads cached high state, barriers, evaluates the low counter, conditionally updates the high word when top bits differ, and returns the combined 64-bit value with bit 63 considered garbage.

State and persistence behavior: Each macro expansion site owns a `static u32 __m_cnt_hi`, so state is per call site. Correctness requires calls at least once per half period and no preemption longer than the half-period margin described in the comment.

Dependencies and integration points: It includes compiler/types and byteorder headers. It integrates with clocksource/sched_clock-style code using 32-bit free-running counters.

Risks: Passing a pre-read variable rather than a globally increasing counter expression violates the macro’s ordering requirement. Missing the half-period call frequency can lose wraps. Call-site-local static state means multiple call sites do not share extension history.

Test signals: Counter wrap simulation, high-frequency sampling, preemption stress, endian build coverage, sched_clock monotonicity tests, and explicit clearing/masking of bit 63 when callers need a true nonnegative value validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cnt32_to_63.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/coda.h -->
# sources/distributed-fs/ceph-client/include/linux/coda.h

Purpose: This kernel header bridges the Coda distributed filesystem definitions by setting up a legacy `u_quad_t` typedef and including the UAPI Coda header.

Important APIs/types/functions: It defines include guard `_CODA_HEADER_`, typedefs `u_quad_t` as `unsigned long long`, and includes `<uapi/linux/coda.h>`.

Control flow: There is no runtime control flow; inclusion exposes UAPI Coda structures and constants to kernel code.

State and persistence behavior: It owns no state. The persistent contract is the Coda kernel/userspace ABI included from UAPI.

Dependencies and integration points: It integrates Coda filesystem kernel code with UAPI request/response structures shared with userspace Venus/Coda tools.

Risks: The typedef is legacy compatibility glue; changing it can break ABI assumptions. Most substantive structure changes must happen in the UAPI header with compatibility care.

Test signals: Coda filesystem build coverage, mount/client smoke tests, ioctl/message ABI tests, and userspace Coda tool compatibility validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/coda.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/codetag.h -->
# sources/distributed-fs/ceph-client/include/linux/codetag.h

Purpose: This header defines the code tagging framework: metadata records emitted into special ELF sections so runtime code can iterate tagged source locations, format them, and manage module-provided tag sections.

Important APIs/types/functions: It defines section prefix macros `CODETAG_SECTION_START_PREFIX` and `CODETAG_SECTION_STOP_PREFIX`, flag `CODETAG_FLAG_INACCURATE`, `struct codetag`, `union codetag_ref`, `struct codetag_type_desc`, `struct codetag_iterator`, `CODE_TAG_INIT`, and module-name macro `CT_MODULE_NAME`. APIs include `codetag_register_type`, `codetag_lock_module_list`, `codetag_trylock_module_list`, `codetag_get_ct_iter`, `codetag_next_ct`, `codetag_to_text`, and, with code tagging plus modules, section allocation/loading helpers such as `codetag_needs_module_section`, `codetag_alloc_module_section`, `codetag_free_module_sections`, `codetag_module_replaced`, `codetag_load_module`, and `codetag_unload_module`.

Control flow: Tag users define records in named sections initialized with source metadata. A codetag type registers a section descriptor and optional module load/unload callbacks. Iterators walk core and module tag ranges under module-list locking. Module helpers allocate, load, replace, and unload tag sections when supported; otherwise stubs return false, `NULL`, or success no-ops.

State and persistence behavior: Tag records persist in ELF sections for built-in code and loaded modules. Iterators carry module sequence/id state to traverse safely. Module section memory may be dynamically allocated and freed around module lifecycle.

Dependencies and integration points: It includes `<linux/types.h>` and integrates with module loading, linker sections, seq_buf formatting, diagnostics/accounting frameworks that tag code sites, and Kbuild module names.

Risks: Section names, sizes, and alignment must match descriptors or iteration corrupts metadata. Module lifecycle locking is essential. Disabled stubs mean callers must tolerate absent module tagging. Source metadata may become inaccurate after transformations and uses `CODETAG_FLAG_INACCURATE`.

Test signals: Build/link checks for start/stop section symbols, module load/unload and livepatch replacement tests, iterator concurrency tests, seq_buf output validation, and config-off build coverage validate the framework.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/codetag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/comedi/comedi_8254.h -->
# sources/distributed-fs/ceph-client/include/linux/comedi/comedi_8254.h

Purpose: This header provides generic Comedi support for Intel 8254-style timer/counter devices, including register definitions, oscillator constants, state storage, access callbacks, timer programming helpers, and allocation helpers for I/O-port or MMIO-backed counters.

Important APIs/types/functions: It defines oscillator base constants from 10 MHz through 1 kHz, access sizes `I8254_IO8/16/32`, counter/control register offsets and control word helpers, `I8254_MAX_COUNT`, callback typedef `comedi_8254_iocb_fn`, and `struct comedi_8254` containing access callback/context, oscillator base, divisors, next divisors, clock/gate sources, busy flags, and optional instruction config callback. APIs include status/read/write, mode/load, pacer enable, divisor update, ns-to-timer conversion for single and cascaded timers, busy marking, subdevice init, `comedi_8254_io_alloc`, and `comedi_8254_mm_alloc`.

Control flow: Drivers allocate an 8254 object for I/O or MMIO, initialize a Comedi subdevice with it, convert desired nanosecond periods to divisors, load modes/counts, and enable/disable cascaded pacers. Register access flows through the callback so bus-specific access is abstracted.

State and persistence behavior: The struct caches current and next divisors, source selections, and busy state, while hardware counters hold programmed mode/count. I/O allocation returns `-ENXIO` when `CONFIG_HAS_IOPORT` is unavailable.

Dependencies and integration points: It includes types, errno, and err helpers and integrates with Comedi subdevices, instruction config paths, pacer timing for acquisition, I/O port access, and MMIO access.

Risks: Timer divisor zero maps to `0x10000`, which must be handled intentionally. Wrong oscillator base or access size produces incorrect sample timing. Cascaded counter ordering matters. Busy flags must prevent conflicting ownership of counters.

Test signals: Comedi driver tests for pacer frequency, mode programming, I/O-port-disabled builds, MMIO-backed devices, divisor conversion edge cases, and acquisition timing validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/comedi/comedi_8254.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/comedi/comedi_8255.h -->
# sources/distributed-fs/ceph-client/include/linux/comedi/comedi_8255.h

Purpose: This header provides generic Comedi support for 8255 digital I/O subdevices.

Important APIs/types/functions: It defines register offsets `I8255_DATA_A_REG`, `I8255_DATA_B_REG`, `I8255_DATA_C_REG`, `I8255_CTRL_REG`, size `I8255_SIZE`, control bits for port directions/modes, and helper `I8255_CTRL_A_MODE(x)`. APIs are `subdev_8255_io_init`, `subdev_8255_mm_init`, `subdev_8255_cb_init`, and `subdev_8255_regbase`. `subdev_8255_io_init` returns `-ENXIO` when I/O ports are unavailable.

Control flow: A low-level driver initializes a Comedi subdevice for I/O-port, MMIO, or callback-based access. The generic implementation then handles digital input/output instruction operations through the configured access path.

State and persistence behavior: Hardware state is the 8255 control word and port data registers; Comedi subdevice private state records register base/context. The header itself stores none.

Dependencies and integration points: It includes errno support and integrates with Comedi DIO subdevices, legacy I/O-port boards, MMIO boards, and custom bus access callbacks.

Risks: Port direction bits are split across A/B/C high/C low fields, and wrong control words can invert intended input/output behavior. I/O-port stubs require callers to handle `-ENXIO`.

Test signals: DIO read/write/config tests, callback and MMIO access tests, I/O-port-disabled builds, and port direction readback validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/comedi/comedi_8255.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/comedi/comedi_isadma.h -->
# sources/distributed-fs/ceph-client/include/linux/comedi/comedi_isadma.h

Purpose: This header defines ISA DMA helper state and APIs for Comedi drivers that use legacy ISA DMA channels.

Important APIs/types/functions: It defines direction constants `COMEDI_ISADMA_READ` and `COMEDI_ISADMA_WRITE`, `struct comedi_isadma_desc` with virtual address, bus address, channel, sizes, and mode, and `struct comedi_isadma` with device, descriptor count, current descriptor, primary/secondary channels, and flexible descriptor array. APIs include `comedi_isadma_program`, `comedi_isadma_disable`, `comedi_isadma_disable_on_sample`, `comedi_isadma_poll`, `comedi_isadma_set_mode`, `comedi_isadma_alloc`, and `comedi_isadma_free`; disabled `CONFIG_ISA_DMA_API` stubs do nothing or return `0`/`NULL`.

Control flow: Drivers allocate DMA descriptors, set transfer mode, program a descriptor, poll progress or disable on sample boundaries, and free descriptors at detach. The helpers abstract unavailable `<asm/dma.h>` constants.

State and persistence behavior: DMA state is tracked in descriptor buffers, hardware DMA channel programming, current descriptor index, and transfer sizes. Disabled builds allocate nothing and perform no DMA operations.

Dependencies and integration points: It includes `<linux/types.h>` and integrates Comedi drivers with legacy ISA DMA API, non-coherent memory allocation, and acquisition buffer movement.

Risks: ISA DMA has strict channel, size, and addressability constraints. Direction mistakes can corrupt memory or miss samples. Stubbed builds require graceful fallback. Descriptor lifetime must outlive active DMA.

Test signals: ISA-capable hardware tests, DMA residue/poll validation, disable-on-sample behavior, allocation failure paths, config-off builds, and buffer integrity checks are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/comedi/comedi_isadma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/comedi/comedi_pci.h -->
# sources/distributed-fs/ceph-client/include/linux/comedi/comedi_pci.h

Purpose: This header provides Comedi helper APIs for PCI-backed Comedi drivers.

Important APIs/types/functions: It defines several PCI vendor IDs not present in `pci_ids.h`, declares `comedi_to_pci_dev`, `comedi_pci_enable`, `comedi_pci_disable`, `comedi_pci_detach`, `comedi_pci_auto_config`, `comedi_pci_auto_unconfig`, `comedi_pci_driver_register`, `comedi_pci_driver_unregister`, and macro `module_comedi_pci_driver`.

Control flow: A PCI probe path calls Comedi PCI auto-config with the matched `pci_dev`, Comedi driver, and context. Register/unregister helpers pair a Comedi driver with a PCI driver, while enable/disable/detach manage PCI device resources.

State and persistence behavior: State lives in `struct comedi_device`, its `hw_dev`, PCI enable/resource state, and Comedi attachment state. The macro wires module init/exit to paired register/unregister calls.

Dependencies and integration points: It includes `<linux/pci.h>` and `comedidev.h`, integrating PCI bus probe/remove with Comedi core auto-configuration and low-level board drivers.

Risks: Resource enable/disable must be balanced. Auto-unconfig must run on remove to detach Comedi devices. Vendor IDs duplicated here should not conflict with future central definitions.

Test signals: PCI probe/remove, module load/unload, BAR/IRQ resource cleanup, Comedi minor creation, and hot-unplug or driver unbind tests are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/comedi/comedi_pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/comedi/comedi_pcmcia.h -->
# sources/distributed-fs/ceph-client/include/linux/comedi/comedi_pcmcia.h

Purpose: This header provides Comedi helper APIs for PCMCIA-backed Comedi drivers.

Important APIs/types/functions: It declares `comedi_to_pcmcia_dev`, `comedi_pcmcia_enable`, `comedi_pcmcia_disable`, `comedi_pcmcia_auto_config`, `comedi_pcmcia_auto_unconfig`, `comedi_pcmcia_driver_register`, `comedi_pcmcia_driver_unregister`, and macro `module_comedi_pcmcia_driver`.

Control flow: A PCMCIA probe path auto-configures a Comedi device for the card. Enable calls may receive a `conf_check` callback for socket/resource validation. The module macro binds Comedi and PCMCIA driver registration lifetimes.

State and persistence behavior: State lives in PCMCIA socket/device resources and the attached Comedi device. Disable/unconfig releases configuration and Comedi attachment.

Dependencies and integration points: It includes PCMCIA CIS/driver headers and `comedidev.h`, integrating PCMCIA card services with Comedi core.

Risks: PCMCIA resource windows and configuration checks are hardware-sensitive. Failing to auto-unconfig on removal can leave stale Comedi devices. Probe ordering and card eject races need care.

Test signals: PCMCIA insertion/removal, configuration callback failure paths, module unload, Comedi minor cleanup, and I/O resource release validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/comedi/comedi_pcmcia.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/comedi/comedi_usb.h -->
# sources/distributed-fs/ceph-client/include/linux/comedi/comedi_usb.h

Purpose: This header provides Comedi helper APIs for USB-backed Comedi drivers.

Important APIs/types/functions: It declares `comedi_to_usb_interface`, `comedi_to_usb_dev`, `comedi_usb_auto_config`, `comedi_usb_auto_unconfig`, `comedi_usb_driver_register`, `comedi_usb_driver_unregister`, and macro `module_comedi_usb_driver`.

Control flow: USB probe calls auto-config with the interface, Comedi driver, and context. Disconnect calls auto-unconfig. Register/unregister helpers bind Comedi driver lifecycle to the USB driver lifecycle.

State and persistence behavior: State lives in USB interface/device references and the attached Comedi device. Auto-unconfig detaches Comedi state during disconnect.

Dependencies and integration points: It includes `<linux/usb.h>` and `comedidev.h`, integrating USB core probe/disconnect with Comedi low-level drivers.

Risks: USB disconnect can race with open Comedi users and async commands. Drivers must stop URBs and detach cleanly. Device/interface conversion helpers depend on correct `hw_dev` association.

Test signals: USB plug/unplug, active acquisition disconnect, module unload, URB cleanup, Comedi minor removal, and runtime PM tests are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/comedi/comedi_usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/comedi/comedidev.h -->
# sources/distributed-fs/ceph-client/include/linux/comedi/comedidev.h

Purpose: This is the kernel-only Comedi core contract. It defines Comedi device/subdevice/async-buffer/driver structures, callback event bits, range helpers, command validation helpers, buffer APIs, resource helpers, firmware loading, and driver registration.

Important APIs/types/functions: Main structures are `struct comedi_subdevice`, `struct comedi_buf_page`, `struct comedi_buf_map`, `struct comedi_async`, `struct comedi_driver`, `struct comedi_device`, and `struct comedi_lrange`. Important constants/macros include `COMEDI_VERSION`, `COMEDI_VERSION_CODE`, `COMEDI_RELEASE`, `COMEDI_NUM_BOARD_MINORS`, range constructors `RANGE*`, `BIP_RANGE`, `UNI_RANGE`, `range_digital`, `COMEDI_TIMEOUT_MS`, and `module_comedi_driver`. Event enum `comedi_cb` defines EOS, EOA, BLOCK, EOBUF, ERROR, OVERFLOW, error mask, and cancel mask. APIs cover events, device refs, subdevice running refs, private allocation, chanlist checks, range predicates, sample-size conversion, trigger validation, hardware-device association, async buffer read/write allocation/free/sample helpers, timeout handling, DIO helpers, scan accounting, device/subdevice/readback allocation, firmware loading, I/O region checks/requests, legacy detach, auto config/unconfig, and driver register/unregister.

Control flow: Low-level drivers register `struct comedi_driver`, attach or auto-attach devices, allocate subdevices, fill operation callbacks, and optionally set async command callbacks. The core dispatches instructions, validates commands through `do_cmdtest`, manages async buffer producer/consumer counters, emits events through `comedi_event`/`comedi_handle_events`, and detaches devices through driver callbacks. Module macro wires simple module init/exit.

State and persistence behavior: `struct comedi_device` persists while the minor is active and tracks use count, attached state, hardware resources, subdevices, default read/write subdevices, locks, refcount, and async queue. `struct comedi_subdevice` tracks capabilities, callbacks, locks/busy state, digital state, range/maxdata metadata, and optional readback. `struct comedi_async` maintains modulo-32-bit buffer counters and pointers with strict ordering invariants, wait queues, completion, command, callback mask, and software trigger. `struct comedi_buf_map` uses `kref` to delay freeing mmapped buffers.

Dependencies and integration points: It includes DMA mapping, mutex, spinlock, rwsem, kref, completion, and public `<linux/comedi.h>`. It integrates with char devices/minors, sysfs subdevice class devices, fasync, DMA, firmware loader, I/O port resource management, bus-specific Comedi helpers, and userspace Comedi ioctls.

Risks: Async buffer count invariants are central; violating them causes data corruption or overflow/underflow. Attach failure paths rely on detach handling partially initialized resources. Locks and busy/run-active refs must prevent command races. Range helpers assume valid indices and correct table type. `comedi_request_region` requires nonzero base. DMA users must set `hw_dev`.

Test signals: Comedi core ioctl tests, async acquisition/read/write stress, buffer mmap lifetime tests, command validation step tests, attach failure injection, detach/unbind while open, DIO/range helper tests, firmware loading errors, and lockdep/KASAN coverage are primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/comedi/comedidev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/comedi/comedilib.h -->
# sources/distributed-fs/ceph-client/include/linux/comedi/comedilib.h

Purpose: This header exposes a small in-kernel Comedi library API for opening Comedi devices and performing simple digital I/O operations.

Important APIs/types/functions: APIs are `comedi_open_from`, inline `comedi_open`, `comedi_close_from`, inline `comedi_close`, `comedi_dio_get_config`, `comedi_dio_config`, `comedi_dio_bitfield2`, `comedi_find_subdevice_by_type`, and `comedi_get_n_channels`.

Control flow: Kernel users open a fake `/dev/comediN` path, use the returned `struct comedi_device` for DIO config/bitfield operations or subdevice discovery, then close it. Inline wrappers pass `-1` as the caller source to the `_from` variants.

State and persistence behavior: Open/close manipulate Comedi device references/use counts in the implementation. DIO calls mutate subdevice channel direction or state. The header itself stores no state.

Dependencies and integration points: It forward-declares `struct comedi_device` and integrates in-kernel consumers with Comedi core without going through userspace file descriptors.

Risks: The path parser expects `/dev/comediN`-style names. Callers must close opened devices. DIO operations require valid subdevice and channel numbers and an attached device.

Test signals: In-kernel Comedi users, open/close refcount tests, invalid path tests, DIO config/bitfield tests, and subdevice discovery checks validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/comedi/comedilib.h -->
