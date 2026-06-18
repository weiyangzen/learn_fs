# Research: subset-b-001093

Grouped research for common clkdev lookup support, TI DaVinci clock providers, ESWIN EIC7700 clock providers, and selected HiSilicon clock provider files.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clkdev.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clkdev.c

Purpose: implements the legacy `clkdev` lookup table used by the Linux common clock framework to map device/connection names to `struct clk_hw` and create consumer-facing `struct clk` handles.

Important APIs/types/functions: global `clocks` stores `struct clk_lookup` entries under `clocks_mutex`. `clk_find()` does fuzzy lookup with specificity order device+connection, device-only, then connection-only. Public entry points include `clk_get_sys()`, `clk_get()`, `clk_put()`, `clkdev_add()`, `clkdev_add_table()`, `clkdev_create()`, `clkdev_hw_create()`, `clk_add_alias()`, `clkdev_drop()`, `clk_register_clkdev()`, `clk_hw_register_clkdev()`, and `devm_clk_hw_register_clkdev()`. `struct clk_lookup_alloc` embeds bounded storage for formatted `dev_id` and copied `con_id`.

Control flow: consumers call `clk_get()`, which first tries device-tree lookup through `of_clk_get_hw()` when `dev->of_node` exists and falls back to `__clk_get_sys()`. Providers add lookup entries through static tables or dynamic allocation. Dynamic helpers allocate a lookup, copy or format IDs, attach the `clk_hw`, and insert into the list. Managed registration adds a devres cleanup action that drops the lookup.

State and persistence: all state is in-memory kernel global list state. Entries persist until explicitly dropped, devres cleanup runs, or the provider module unloads.

Dependencies and integration points: integrates with `linux/clk.h`, `clk-provider.h`, OF clock providers, device names, module exports, and the internal `"clk.h"` helpers `clk_hw_create_clk()`, `__clk_get_hw()`, and `__clk_put()`.

Risks: lookup semantics depend on short fixed ID buffers (`MAX_DEV_ID` 24, `MAX_CON_ID` 16); too-long IDs log an error but create an intentionally nonmatching entry. `clk_find()` is list-order sensitive among equally specific entries. `clk_get()` only treats `-EPROBE_DEFER` from OF as terminal; other OF errors fall back to clkdev, which can hide DT naming mistakes.

Test signals: there are no local unit tests in this file. Useful validation is boot/probe coverage where clock consumers resolve by dev_id/con_id, OF lookup fallback is exercised, aliases resolve correctly, and devres cleanup removes dynamically registered lookups without use-after-free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clkdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/davinci/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/davinci/Makefile

Purpose: builds TI DaVinci clock-controller objects only when the common clock framework is enabled.

Important APIs/types/functions: make variables add `da8xx-cfgchip.o`, `pll.o`, `pll-da850.o`, `psc.o`, and `psc-da850.o` according to `CONFIG_COMMON_CLK`, `CONFIG_ARCH_DAVINCI_DA8XX`, and `CONFIG_ARCH_DAVINCI_DA850`.

Control flow: when `CONFIG_COMMON_CLK=y`, generic PLL and PSC support are always built in this subdirectory, while DA8xx/DA850 platform descriptors are conditional. If common clk is disabled, no objects from this Makefile are selected.

State and persistence: no runtime state; it controls build composition.

Dependencies and integration points: couples SoC Kconfig selections to the DaVinci CFGCHIP, PLL, and PSC providers. PSC registration depends on PLL and async clock providers being available early, matching the `postcore_initcall()` ordering in the C files.

Risks: because `pll.o` and `psc.o` are unconditional under `CONFIG_COMMON_CLK`, missing platform descriptors can still compile generic code without registering useful SoC clocks. DA850-specific objects require `CONFIG_ARCH_DAVINCI_DA850`, so defconfig mistakes produce missing platform init data.

Test signals: build tests should confirm the DA8xx and DA850 configurations link all referenced init data and that non-DA850 DaVinci/common-clk builds do not pull unresolved descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/davinci/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/davinci/da8xx-cfgchip.c -->
# sources/distributed-fs/ceph-client/drivers/clk/davinci/da8xx-cfgchip.c

Purpose: exposes DA8xx/AM17xx/AM18xx CFGCHIP syscon bits as common-clock gates, muxes, special dividers, and USB PHY clocks.

Important APIs/types/functions: gate support uses `da8xx_cfgchip_gate_clk_info`, `da8xx_cfgchip_gate_clk`, and ops for enable/disable/is_enabled plus a `div4.5` recalc. Mux support uses `da8xx_cfgchip_mux_clk_info` and parent switching through `regmap_write_bits()`. USB-specific clocks are `da8xx_usb0_clk48` and `da8xx_usb1_clk48`, with USB0 prepare/enable sequencing, 48 MHz rate reporting, and PHY parent muxing. Platform dispatch uses `da8xx_cfgchip_of_match`, `da8xx_cfgchip_id_table`, and `da8xx_cfgchip_probe()`.

Control flow: probe obtains a CFGCHIP regmap from the parent syscon for DT or platform data for legacy devices, then calls a per-clock initializer. Initializers register tbclk, div4.5, async1, async3, or USB PHY clock providers. Legacy paths also install clkdev aliases and set default async3/USB parents to match existing boards.

State and persistence: hardware state is CFGCHIP register bits. Driver state is devm-managed `clk_hw` wrappers. USB0 enable temporarily enables its PSC functional clock while programming and waiting for PHY PLL lock.

Dependencies and integration points: depends on `mfd/da8xx-cfgchip.h`, syscon/regmap, `clkdev`, DT clock providers, platform data, and the DaVinci PSC/PLL clock names (`pll0_auxclk`, `pll1_sysclk2`, `async3`).

Risks: `da8xx_usb0_clk48_recalc_rate()` writes reference-frequency bits while recalculating rate, so a read-like clock operation mutates hardware. USB0 enable waits up to 500 ms for `PHYCLKGD`; failures propagate to consumers. Legacy default parent selection can fight board-specific assumptions if DT should have been used. Probe fails hard without regmap.

Test signals: validate probe on legacy and DT boards, async1/async3 parent selection, USB0 48 MHz lock behavior for all supported reference rates, USB1 parent muxing, and tbclk clkdev lookup for EHRPWM consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/davinci/da8xx-cfgchip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/davinci/pll-da850.c -->
# sources/distributed-fs/ceph-client/drivers/clk/davinci/pll-da850.c

Purpose: provides DA850/OMAP-L138/AM18xx-specific PLL descriptors, SYSCLK definitions, OBSCLK parent tables, and init routines consumed by the generic DaVinci PLL driver.

Important APIs/types/functions: `da850_pll0_info` and `da850_pll1_info` describe PLL masks, unlock registers, multiplier limits, output ranges, and quirks. `SYSCLK()` definitions create `pll0_sysclk1..7` and `pll1_sysclk1..3`. `da850_pll0_init()`, `of_da850_pll0_init()`, `da850_pll1_init()`, and `of_da850_pll1_init()` register clocks and clkdev aliases.

Control flow: PLL0 registration creates the PLL tree from `ref_clk`, registers seven sysclks, AUXCLK, an `async2` fixed-factor alias, and OBSCLK. PLL1 registration uses `oscin` as parent and registers three sysclks plus OBSCLK. OF init uses `of_davinci_pll_init()` with sysclk arrays and max IDs; platform init manually installs clkdev aliases for PSCs and legacy devices.

State and persistence: no independent mutable state; it programs hardware through generic PLL helpers and persists clock topology through registered `clk` objects and providers.

Dependencies and integration points: uses CFGCHIP unlock masks, DT bindings, `clkdev`, syscon lookup for `ti,da830-cfgchip`, and the generic declarations in `pll.h`. PSC and CFGCHIP providers consume names such as `pll0_sysclk2`, `pll0_sysclk4`, `async2`, and `pll1_sysclk2`.

Risks: init routines ignore some returned errors after registration, so missing clock nodes may surface later as consumer probe failures. Fixed-ratio SYSCLKs are treated read-only even though hardware may allow coordinated ratio changes. Legacy aliases encode specific device names and can break if platform device names drift.

Test signals: boot DA850 with DT and non-DT paths, inspect `/sys/kernel/debug/clk/clk_summary`, verify PSC parent lookups, test CPU/ARM SYSCLK rate changes, and confirm CFGCHIP unlock bits allow PLL programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/davinci/pll-da850.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/davinci/pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/davinci/pll.c

Purpose: implements the generic DaVinci PLL common-clock provider, including PLLOUT, optional pre/post dividers, PLLEN bypass control, AUXCLK, SYSCLKBP, OBSCLK, SYSCLKn, OF registration, platform probing, and debugfs register exposure.

Important APIs/types/functions: main types are `davinci_pll_clk` and `davinci_pllen_clk`. PLL ops include recalc, determine, and set-rate; DM365 has a 2x multiplier recalc variant. `davinci_pll_div_register()` builds gate+divider composites. Public registration functions include `davinci_pll_clk_register()`, `davinci_pll_auxclk_register()`, `davinci_pll_sysclkbp_clk_register()`, `davinci_pll_obsclk_register()`, `davinci_pll_sysclk_register()`, and `of_davinci_pll_init()`.

Control flow: `davinci_pll_clk_register()` optionally creates `oscin`, prediv, PLLOUT, postdiv, and PLLEN. A PLLEN notifier switches to bypass before parent/PLL rate changes, resets and relocks the PLL, then re-enables PLL mode. SYSCLK notifiers wait for pending GO operations and trigger `PLLCMD_GOSET` after divider changes. OF init registers child providers for `pllout`, `sysclk`, `auxclk`, and `obsclk`. The platform driver maps registers and dispatches DA850 init callbacks.

State and persistence: hardware register state lives in PLL MMIO; software state is allocated `clk_hw` wrappers and notifier blocks. There is no suspend persistence layer.

Dependencies and integration points: depends on clk composite/gate/divider/mux helpers, OF providers, regmap/syscon for CFGCHIP unlock, platform IDs, `postcore_initcall()`, and DA850 callbacks from `pll-da850.c`.

Risks: busy waits use unbounded `regmap_read_poll_timeout(..., 0, 0)` for SYSCLK/PSC-style waits in related paths, so stuck hardware can hang. Some allocations are not devm-managed and unregister paths are only partial error unwind. Rate setting writes PLLM directly and relies on notifier ordering for safe bypass. Debugfs regset allocation is not explicitly freed.

Test signals: exercise PLL rate changes, prediv/postdiv read-only flags, SYSCLK divider updates with GO synchronization, OF child providers, error unwinds on failed clock registration, and debugfs register visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/davinci/pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/davinci/pll.h -->
# sources/distributed-fs/ceph-client/drivers/clk/davinci/pll.h

Purpose: declares shared DaVinci PLL metadata structures, quirk flags, SYSCLK/OBSCLK descriptors, registration APIs, and DA850 platform callbacks.

Important APIs/types/functions: `davinci_pll_clk_info` captures PLL register masks, multiplier limits, output limits, CFGCHIP unlock information, and `PLL_*` flags. `davinci_pll_sysclk_info` describes SYSCLKn name, parent, ID, ratio width, and `SYSCLK_*` flags. `SYSCLK()` is the descriptor macro used by DA850. `davinci_pll_obsclk_info` describes OBSCLK mux parents and hardware selection table.

Control flow: no executable control flow. The header defines the contracts that platform data files pass into `pll.c` registration functions and OF initialization.

State and persistence: no runtime state. The structs are static descriptor data used to create persistent registered clocks at boot/probe time.

Dependencies and integration points: includes bitops, common clock provider interfaces, OF, regmap, and types. It links generic `pll.c` with DA850 descriptors and callbacks (`da850_pll1_init()`, `of_da850_pll0_init()`, `of_da850_pll1_init()`).

Risks: flag combinations encode hardware behavior; wrong flags can disable critical dividers, treat writable dividers as fixed, or compute PLL rates incorrectly. The `SYSCLK()` macro stringifies symbol names, so renaming descriptors changes clock names visible to consumers.

Test signals: compile-time coverage for descriptor users, boot-time verification that generated names match DT/clkdev consumers, and rate tests confirming flag combinations produce expected parent propagation and divider behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/davinci/pll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/davinci/psc-da850.c -->
# sources/distributed-fs/ceph-client/drivers/clk/davinci/psc-da850.c

Purpose: supplies DA850 PSC0/PSC1 LPSC clock tables, clkdev aliases, parent-clock dependencies, and init data for the generic DaVinci PSC driver.

Important APIs/types/functions: `da850_psc0_info` and `da850_psc1_info` define LPSC module IDs, power domains, names, parents, clkdev aliases, and flags. `LPSC_CLKDEV*()` arrays map legacy consumers such as MMC, UART, USB, EMAC, LCDC, SATA, GPIO, and DSP. Exports `da850_psc0_init_data`, `da850_psc1_init_data`, `of_da850_psc0_init_data`, and `of_da850_psc1_init_data`.

Control flow: PSC0 init registers 16 possible module slots; PSC1 init registers 32. Platform paths call `davinci_psc_register_clocks()` to also install clkdev aliases. OF paths call `of_davinci_psc_clk_init()` to publish onecell clock and genpd providers.

State and persistence: the file has static descriptor state only. Hardware enable/reset state is managed by `psc.c` based on these descriptors.

Dependencies and integration points: depends on PLL names (`pll0_sysclk*`), CFGCHIP async clocks (`async1`, `async3`), legacy platform device names, and PSC generic structures in `psc.h`.

Risks: missing or wrong parent clocks cause PSC probe deferral/failure. `LPSC_ALWAYS_ENABLED` is critical for DMA, interrupt controller, ARM, DDR, and transfer controller clocks; misclassification could break boot or suspend. Sparse module IDs require the `num_clks` bounds to exceed the highest LPSC ID.

Test signals: DA850 boot should show all always-enabled clocks on, legacy clkdev consumers should resolve, DT consumers should acquire clocks by onecell index, and DSP local reset should work for the `LPSC_LOCAL_RESET` entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/davinci/psc-da850.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/davinci/psc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/davinci/psc.c

Purpose: implements TI DaVinci Power and Sleep Controller clocks as common-clock gates, optional generic PM domains, and local reset controls.

Important APIs/types/functions: `davinci_lpsc_clk` wraps `clk_hw`, `generic_pm_domain`, a PSC regmap, module-domain ID, power-domain ID, and flags. `davinci_lpsc_config()` sequences MDCTL/PDCTL/PTCMD/EPCPR/PTSTAT/MDSTAT transitions. Registration APIs are `davinci_psc_register_clocks()` and `of_davinci_psc_clk_init()`. Reset ops map OF reset IDs back to LPSC module IDs.

Control flow: probe finds init data from OF match or platform ID, maps the PSC resource, obtains parent clocks in bulk, then calls the platform init callback. Registration creates sparse onecell clock and PM-domain arrays, initializes missing clock entries to `-ENOENT`, registers each LPSC, registers reset control for real devices, then publishes clkdev aliases or OF providers. Enable/disable drives PSC state transitions to ENABLE or DISABLE.

State and persistence: PSC hardware retains module/power states in registers. Software stores allocated clock data, PM domains, and reset controller structures. DT mode records each LPSC as a genpd domain whose attach path adds the LPSC clock to the consumer's pm-clk list.

Dependencies and integration points: depends on regmap-mmio, PM clock/domain frameworks, reset controller framework, clkdev, OF onecell providers, and DA850 init data from `psc-da850.c`.

Risks: `regmap_read_poll_timeout()` calls use zero timeout, so bad hardware state can hang. `clk_hw_register_clkdev()` return is not checked before PM domain setup. Reset xlate assumes the phandle also identifies a clock and casts returned `clk_hw` to an LPSC. Sparse arrays depend on descriptor IDs staying within `num_clks`.

Test signals: test enable/disable/is_enabled transitions, genpd attach/detach power-on behavior, reset assert/deassert for DSP, OF clock lookups for sparse IDs, and probe deferral when parent clocks are unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/davinci/psc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/davinci/psc.h -->
# sources/distributed-fs/ceph-client/drivers/clk/davinci/psc.h

Purpose: defines the descriptor contract for DaVinci LPSC clocks, clkdev alias arrays, quirk flags, registration APIs, and device-specific PSC init data.

Important APIs/types/functions: flags are `LPSC_ALWAYS_ENABLED`, `LPSC_SET_RATE_PARENT`, `LPSC_FORCE`, and `LPSC_LOCAL_RESET`. `davinci_lpsc_clkdev_info` plus `LPSC_CLKDEV*()` macros describe legacy lookup aliases. `davinci_lpsc_clk_info` describes each module clock. `LPSC()` builds table entries. `davinci_psc_init_data` carries parent bulk clock requirements and a `psc_init()` callback.

Control flow: no executable flow; macros expand static descriptor tables consumed by `psc.c`.

State and persistence: none directly. Descriptor tables created with this header determine hardware state transitions and registered clock topology at runtime.

Dependencies and integration points: depends on common clock provider types and is shared by generic PSC code and DA850 descriptors. External init data symbols are referenced by the platform driver match tables.

Risks: macro-generated names are stringified, so C identifier changes alter ABI-visible clock names. Incorrect `md`/`pd` IDs or flags can affect unrelated modules or power domains. Local-reset support is opt-in by flag and must match hardware capability.

Test signals: compile coverage of descriptor tables, boot-time clock summary inspection, reset-controller phandle tests for local-reset entries, and legacy clkdev resolution for generated alias arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/davinci/psc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/eswin/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/eswin/Kconfig

Purpose: declares ESWIN clock-controller Kconfig options.

Important APIs/types/functions: `COMMON_CLK_ESWIN` is an internal boolean selected by SoC drivers. `COMMON_CLK_EIC7700` is a tristate user-visible driver option depending on `ARCH_ESWIN || COMPILE_TEST`, selecting `COMMON_CLK_ESWIN` and defaulting to `ARCH_ESWIN`.

Control flow: configuration controls whether shared ESWIN clock helpers and the EIC7700 provider are compiled.

State and persistence: no runtime state.

Dependencies and integration points: ties ESWIN architecture selection and compile-test coverage to `drivers/clk/eswin/Makefile`, which builds `clk.o` for common helpers and `clk-eic7700.o` for the SoC provider.

Risks: `COMMON_CLK_ESWIN` has no prompt, so helper code is only built when selected. The EIC7700 driver is tristate, while its helper selection is bool; module/built-in combinations need link coverage.

Test signals: run `allyesconfig`/`allmodconfig`/`COMPILE_TEST` builds and an `ARCH_ESWIN` default build to ensure helper/provider symbols link in both built-in and module configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/eswin/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/eswin/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/eswin/Makefile

Purpose: maps ESWIN Kconfig symbols to build objects.

Important APIs/types/functions: `obj-$(CONFIG_COMMON_CLK_ESWIN) += clk.o` builds shared registration/PLL/divider helpers. `obj-$(CONFIG_COMMON_CLK_EIC7700) += clk-eic7700.o` builds the EIC7700 SoC provider.

Control flow: no runtime flow; kbuild includes object files based on selected symbols.

State and persistence: no runtime state.

Dependencies and integration points: the SoC provider depends on exported helper symbols from `clk.o`. Because `COMMON_CLK_EIC7700` selects `COMMON_CLK_ESWIN`, normal configurations include both.

Risks: if symbol visibility changes, `clk-eic7700.o` can be built without helper symbols. Module build combinations should ensure exported GPL helper symbols are visible to the provider.

Test signals: compile EIC7700 as built-in and module under `COMPILE_TEST`; verify no unresolved exports from `clk.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/eswin/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/eswin/clk-eic7700.c -->
# sources/distributed-fs/ceph-client/drivers/clk/eswin/clk-eic7700.c

Purpose: describes and registers the ESWIN EIC7700 clock tree, including fixed rates, programmable PLLs, fixed factors, dividers, gates, muxes, and CPU PLL rate-change protection.

Important APIs/types/functions: descriptor arrays are `eic7700_fixed_rate_clks`, `eic7700_pll_clks`, `eic7700_factor_clks`, `eic7700_div_clks`, `eic7700_gate_clks`, `eic7700_early_clks`, `eic7700_mux_clks`, and `eic7700_clks`. `eic7700_clk_pll_cpu_notifier_cb()` temporarily switches the CPU root mux to low-power fixed-factor input while `clk_pll_cpu` changes. `eic7700_clk_probe()` registers all descriptors and publishes an OF onecell provider.

Control flow: probe allocates `EIC7700_NR_CLKS`, registers fixed-rate roots, PLLs, the CPU PLL notifier, factors, simple dividers/gates, early composite descriptors needed as mux parents, muxes, then the remaining derived clocks. Consumers retrieve clocks by IDs from `dt-bindings/clock/eswin,eic7700-clock.h`.

State and persistence: register state lives in the SYS-CRG MMIO range. Runtime state includes `eswin_clock_data`, `clk_hw` arrays, and the saved CPU mux parent during PLL transitions.

Dependencies and integration points: depends on the shared ESWIN helpers in `clk.c`, common-clock APIs, OF platform probing, and DT binding IDs. Many gates use `CLK_IGNORE_UNUSED` where clocks must remain on for CPUs, UARTs, DDRT, and timer paths.

Risks: the file is table-heavy; ID/parent ordering mistakes can silently wire a clock to the wrong parent. Some fixed-rate entries are declared with rate 0 (`APLL_FOUT2`, `APLL_FOUT3`, `EXT_MCLK`), so consumers must not assume valid rates unless hardware/DT updates them elsewhere. The CPU notifier assumes `eic7700_mux_clks[0]` and `eic7700_early_clks[11]` remain specific clocks.

Test signals: probe with DT, enumerate all clock IDs, run CPU PLL rate changes under load, verify protected parent switch/restore, check critical/ignore-unused clocks survive late init, and compare clock summary rates with the SoC manual.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/eswin/clk-eic7700.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/eswin/clk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/eswin/clk.c

Purpose: provides shared ESWIN common-clock helper registration plus custom PLL and divider implementations.

Important APIs/types/functions: `eswin_clk_init()` allocates `eswin_clock_data` and maps the MMIO resource. PLL ops implement `clk_pll_set_rate()`, `clk_pll_recalc_rate()`, and `clk_pll_determine_rate()`. Helper exports register fixed-rate, PLL, fixed-factor, mux, divider, gate, and mixed `eswin_clk_info` descriptors. `eswin_register_clkdiv()` registers the custom private divider used when `ESWIN_PRIV_DIV_MIN_2` is required.

Control flow: PLL set-rate computes fbdiv/frac from requested rate and parent, disables the PLL, writes refdiv/fbdiv/frac/postdiv fields, re-enables it, and polls lock. Registration functions iterate descriptor arrays, create devm-managed `clk_hw` objects, and store them in the onecell `hws` array.

State and persistence: runtime state is devm-managed provider data and MMIO-backed register contents. A spinlock in `eswin_clock_data` serializes mux/divider/gate read-modify-write cycles.

Dependencies and integration points: uses `bitfield.h`, `iopoll.h`, common-clock devm helpers, platform resource mapping, and descriptor types from `common.h`. Exports GPL symbols used by the EIC7700 provider.

Risks: `eswin_clk_init()` converts any ioremap error to `-EINVAL`, losing the original reason. Custom divider math has a potential divide-by-zero path in `eswin_clk_bestdiv()` when `down` becomes zero for rates above parent. PLL set-rate hardcodes refdiv/postdiv values and polls only 100 microseconds total, so marginal hardware could fail. `eswin_clk_register_fixed_factor()` assumes `parent_data->index` rather than full parent data.

Test signals: unit-style rate tests for PLL and private divider math, lock-timeout error injection, concurrent gate/mux/divider operations, probe failure with missing resource, and module build/export checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/eswin/clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/eswin/common.h -->
# sources/distributed-fs/ceph-client/drivers/clk/eswin/common.h

Purpose: defines ESWIN clock descriptor structures, frequency limits, private divider flags, registration prototypes, and table-building macros.

Important APIs/types/functions: central types include `eswin_clock_data`, `eswin_divider_clock`, `eswin_fixed_rate_clock`, `eswin_fixed_factor_clock`, `eswin_gate_clock`, `eswin_mux_clock`, `eswin_pll_clock`, `eswin_clk_pll`, and generic `eswin_clk_info`. Macros such as `ESWIN_FIXED`, `ESWIN_PLL`, `ESWIN_DIV`, `ESWIN_GATE`, `ESWIN_MUX`, and `*_TYPE` forms initialize descriptor tables.

Control flow: no executable code; it defines the data contracts consumed by `clk.c` and SoC files.

State and persistence: no direct state. Struct fields point to MMIO offsets, parents, flags, and IDs that determine registered clock state.

Dependencies and integration points: used by all ESWIN clock providers and relies on common clock types, `clk_parent_data`, `clk_hw_onecell_data`, `notifier_block`, and spinlocks from included kernel headers via C files.

Risks: descriptor macros hide field ownership differences between direct arrays and typed `eswin_clk_info` arrays; `_pid` and `_pdata` usage must match the registration path. `ESWIN_PRIV_DIV_MIN_2` changes hardware divider interpretation and must only be used where the register encoding really forbids 0/1.

Test signals: compile descriptor arrays with sparse IDs, validate onecell lookups for all exported binding IDs, and check that macro-produced parent relationships match clock tree documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/eswin/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/hisilicon/Kconfig

Purpose: defines HiSilicon clock and reset controller configuration options for multiple SoCs and firmware-mediated stub clocks.

Important APIs/types/functions: options include `COMMON_CLK_HI3516CV300`, `COMMON_CLK_HI3519`, `COMMON_CLK_HI3559A`, `COMMON_CLK_HI3660`, `COMMON_CLK_HI3670`, `COMMON_CLK_HI3798CV200`, `COMMON_CLK_HI6220`, `RESET_HISI`, `STUB_CLK_HI6220`, and `STUB_CLK_HI3660`.

Control flow: SoC clock options depend on `ARCH_HISI || COMPILE_TEST`, many select `RESET_HISI`, and defaults follow `ARCH_HISI`. Stub clock options depend on mailbox support and default to their SoC clock driver.

State and persistence: no runtime state.

Dependencies and integration points: drives the Hisilicon Makefile and reset-controller availability. Stub clock selections integrate clock drivers with mailbox firmware channels.

Risks: some SoC drivers are bool while others are tristate, so link coverage must include both built-in and module paths. Reset support is selected only by CRG-style drivers; Hi3660 does not select `RESET_HISI` here.

Test signals: Kconfig build matrix for each SoC under `COMPILE_TEST`, mailbox-disabled configs for stub clocks, and reset-controller symbol availability for CRG drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/hisilicon/Makefile

Purpose: selects common and SoC-specific HiSilicon clock/reset objects for kbuild.

Important APIs/types/functions: always builds shared helpers `clk.o`, `clkgate-separated.o`, `clkdivider-hi6220.o`, and `clk-hisi-phase.o`. Conditional objects include `clk-hi3620.o`, `clk-hip04.o`, `clk-hix5hd2.o`, CRG drivers, Hi3660/Hi3670, Hi6220, reset support, and stub clock drivers.

Control flow: build inclusion follows architecture and Kconfig symbols.

State and persistence: no runtime state.

Dependencies and integration points: SoC files in this work item rely on shared Hisilicon helpers and reset code selected here.

Risks: unconditional helper objects increase compile surface for all Hisilicon clock builds. Architecture-specific `obj-$(CONFIG_ARCH_HI3xxx)` gates Hi3620 separately from the `COMMON_CLK_*` options.

Test signals: compile Hi3xxx, Hi3519, Hi3559A, Hi3660, and stub-clock configurations; verify module/built-in combinations do not leave unresolved common helper symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi3519.c -->
# sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi3519.c

Purpose: implements the Hi3519 CRG clock/reset platform driver with fixed-rate roots, one FMC mux, peripheral gates, OF clock provider registration, and reset controller setup.

Important APIs/types/functions: `hi3519_fixed_rate_clks` defines 24 MHz through 400 MHz roots. `hi3519_mux_clks` defines `fmc_mux` with an eight-entry hardware table. `hi3519_gate_clks` gates FMC, UART0-4, and SPI0-2. `hi3519_clk_register()` and `hi3519_clk_unregister()` manage clock provider lifecycle; `hi3519_clk_probe()` integrates reset initialization.

Control flow: probe allocates `hi3519_crg_data`, initializes reset controller, registers fixed rates, muxes, gates, adds an OF onecell provider, and stores drvdata. Remove tears down reset and unregisters clocks/provider.

State and persistence: state is in CRG registers mapped by shared Hisilicon helpers and in allocated clock/reset data. No durable state exists across reboot.

Dependencies and integration points: uses `dt-bindings/clock/hi3519-clock.h`, shared `clk.h` helpers, `reset.h`, OF platform matching on `hisilicon,hi3519-crg`, and `core_initcall()` for early availability.

Risks: unwind labels are ordered oddly: on mux registration failure the `unregister_fixed_rate` label is used correctly, but subsequent labels require care when edited. Probe treats reset init failure as `-ENOMEM` even if the underlying cause differs. Only a small set of peripherals is represented here.

Test signals: boot/probe with Hi3519 DT, verify clock IDs resolve, toggle FMC/UART/SPI gates, exercise reset controller consumers, and unload/remove in module builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi3519.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi3559a.c -->
# sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi3559a.c

Purpose: implements Hi3559AV100 CRG and sensor-hub clock providers, including fixed-rate roots, muxes, gates, custom PLLs, SHUB dividers, default SHUB programming, and reset-controller integration.

Important APIs/types/functions: CRG descriptors include `hi3559av100_fixed_rate_clks_crg`, mux tables for FMC/MMC/sysbus/UART/A73, `hi3559av100_gate_clks`, and custom PLL descriptors `hi3559av100_pll_clks`. PLL ops are `clk_pll_set_rate()` and `clk_pll_recalc_rate()`. SHUB descriptors include fixed-rate I2C/UART sources, `hi3559av100_shub_mux_clks`, divider tables, and SHUB gates. `hisi_crg_funcs` selects CRG versus SHUB registration.

Control flow: matched probe initializes reset, calls the selected registration function, and stores `hisi_crg_dev`. CRG registration allocates onecell data, registers fixed rates, custom PLLs, muxes, gates, and provider. SHUB registration first calls `hi3559av100_shub_default_clk_set()` to program SSP/UART defaults through an absolute `ioremap()`, then registers fixed rates, muxes, dividers, gates, and provider.

State and persistence: CRG/SHUB register state persists while powered. PLL state is custom `clk_hw` memory allocated with devm. Default SHUB setup directly mutates global CRG registers.

Dependencies and integration points: uses Hisilicon shared helpers, `crg.h`, `reset.h`, DT bindings, OF match compatibles `hisilicon,hi3559av100-clock` and `hisilicon,hi3559av100-shub-clock`.

Risks: fixed-rate `"148p5m"` is set to `1485000000`, likely 10x the name. PLL calculation ignores `parent_rate` and uses hardcoded 24 MHz in recalc. SHUB default setup uses physical `CRG_BASE_ADDR` instead of the platform resource and does not check `ioremap()` failure. Custom PLL registration logs failures but continues, leaving missing IDs.

Test signals: compare exported rates to hardware manual, especially PLL and 148.5 MHz paths; boot both CRG and SHUB providers; verify reset consumers; test SHUB SPI/UART divider defaults; and fault-inject failed PLL registration/provider setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi3559a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi3620.c -->
# sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi3620.c

Purpose: provides early OF clock initialization for Hi3620 system clocks and a separate MMC CIU clock provider with timing-programming behavior.

Important APIs/types/functions: top-level descriptor arrays define fixed rates, fixed factors, muxes, dividers, and separated gates for timers, UARTs, SPI, PWM, SD/MMC, display, video, GPIO, USB, and buses. `hi3620_clk_init()` registers the main provider via `CLK_OF_DECLARE`. MMC-specific types are `hisi_mmc_clock` and `clk_mmc`; ops include `mmc_clk_recalc_rate()`, `mmc_clk_determine_rate()`, `mmc_clk_set_timing()`, `mmc_clk_prepare()`, and `mmc_clk_set_rate()`.

Control flow: early clock init maps the clock controller through `hisi_clk_init()` and registers descriptor arrays. MMC init maps a pctrl node, allocates onecell data sized to the number of MMC descriptors, registers each MMC CIU clock, and adds an OF provider. MMC prepare sets a safe default timing; set-rate disables the clock, writes sample/drive/divider delay fields, then re-enables it under a spinlock.

State and persistence: MMIO registers hold mux/divider/gate and MMC timing state. Allocated `clk_mmc` objects persist for the life of the boot.

Dependencies and integration points: depends on shared Hisilicon helpers, OF early init, DT binding IDs, and pctrl-compatible MMC clock node.

Risks: `mmc_clk_determine_rate()` sets a rate but returns `-EINVAL`, which is unusual and may prevent normal rate negotiation. MMC provider allocates `clk_data->clks` with length equal to descriptor count while indexing by binding IDs, which is only safe if IDs are dense from zero. Missing cleanup on partial init is typical early-boot code but leaks on failure.

Test signals: boot Hi3620 DT, validate timer/UART/MMC/display clock IDs, run MMC at 13/25/50/100/180 MHz, confirm timing fields, and watch for determine-rate failures in MMC consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi3620.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi3660-stub.c -->
# sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi3660-stub.c

Purpose: implements Hi3660 firmware-mediated stub clocks for CPU clusters, GPU, and DDR using mailbox commands to LPM3 firmware and shared SRAM rate readback.

Important APIs/types/functions: `hi3660_stub_clk_chan` stores mailbox client/channel. `hi3660_stub_clk` stores ID, `clk_hw`, firmware command, message buffer, and cached rate. `DEFINE_CLK_STUB()` builds four clocks with `CLK_GET_RATE_NOCACHE`. Ops are `hi3660_stub_clk_recalc_rate()`, `hi3660_stub_clk_determine_rate()`, and `hi3660_stub_clk_set_rate()`.

Control flow: probe configures a nonblocking mailbox client, requests channel 0, maps the SRAM/resource region, offsets to `HI3660_STUB_CLOCK_DATA`, registers all stub `clk_hw`s, and publishes an OF provider that validates index arguments. Set-rate sends command plus MHz rate through mailbox and immediately marks tx done.

State and persistence: firmware owns the real clock programming. The driver reads rates from shared SRAM and stores a transient cached rate per stub clock. Global `freq_reg` and `stub_clk_chan` are singleton state.

Dependencies and integration points: depends on mailbox framework, DT binding IDs, `hisilicon,hi3660-stub-clk` compatible, and LPM3 firmware protocol command values.

Risks: mailbox send return value is ignored, so failed firmware requests appear successful. Probe leaks the mailbox channel on later failures because no remove/free path is defined. `devm_ioremap()` is used instead of resource-requesting helpers. Global singleton state makes multiple instances unsafe.

Test signals: verify mailbox traffic for each command, shared SRAM rate updates after set-rate, invalid phandle index handling, probe deferral/failure behavior when mailbox is absent, and CPU/GPU/DDR DVFS integration under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi3660-stub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi3660.c -->
# sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi3660.c

Purpose: registers Hi3660 clock providers across CRGCTRL, PCTRL, PMUCTRL, SCTRL, and IOMCU domains using shared HiSilicon clock helpers.

Important APIs/types/functions: descriptor arrays cover fixed rates, CRG fixed factors, separated gates, hiword gates, muxes, dividers, PMU/PCTRL gates, SCTRL gates/muxes/dividers, and IOMCU gates. `clk_crgctrl_data` is initialized early by `hi3660_clk_crgctrl_early_init()`. Domain init functions include `hi3660_clk_crgctrl_init()`, `hi3660_clk_pctrl_init()`, `hi3660_clk_pmuctrl_init()`, `hi3660_clk_sctrl_init()`, and `hi3660_clk_iomcu_init()`.

Control flow: CRGCTRL has an early `CLK_OF_DECLARE_DRIVER` path that registers fixed roots and fills all clock slots with `-EPROBE_DEFER`, allowing early consumers to defer until the platform driver registers the rest. Platform probe dispatches to the init function stored in the OF match table. Each domain maps/registers its own onecell provider via `hisi_clk_init()` and the relevant descriptor arrays.

State and persistence: each hardware block keeps register state in its own MMIO region. Software state is in `hisi_clock_data` objects and the global CRGCTRL pointer.

Dependencies and integration points: uses `dt-bindings/clock/hi3660-clock.h`, shared `clk.h`, OF early declaration, platform driver `core_initcall()`, and common-clock hiword mask semantics.

Risks: descriptor-only errors are hard to detect until consumers request clocks. Some gate entries use `CLK_DIVIDER_HIWORD_MASK` where gate flags might be expected, which deserves review against helper semantics. CRGCTRL global state is singleton and assumes one controller. Unregistered `-EPROBE_DEFER` slots are logged only after full registration.

Test signals: boot with early serial/storage consumers, verify deferral resolves after platform probe, inspect clock summary across all domains, test UFS critical clock suspend/resume, and check all binding IDs map to non-error clocks where hardware supports them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi3660.c -->
