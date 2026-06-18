# subset-b-001186 Research

Grouped research for TI and UniPhier clock driver sources. Each section is source-tree aligned and bounded by reconciler markers for per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clk-7xx.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/clk-7xx.c

Purpose: DRA7/DRA72/DRA74/DRA76 clock initialization data for the OMAP/TI common clock framework. The file is almost entirely `__initconst` metadata that maps PRCM clkctrl register blocks to module clocks and their subclocks, plus `dra7xx_dt_clk_init()` for early clock alias registration and fixed boot-time DPLL programming.

Important APIs/types/functions: it exports `dra7_clkctrl_data[]` for `clkctrl.c` lookup and defines `dra7xx_dt_clk_init()`. It uses `struct omap_clkctrl_data`, `struct omap_clkctrl_reg_data`, `struct omap_clkctrl_bit_data`, and `struct omap_clkctrl_div_data` from `clock.h`; `DT_CLK()` entries form legacy clkdev aliases for generated clkctrl names such as `l4per-clkctrl:0118:24`.

Control flow: `clkctrl.c` selects `dra7_clkctrl_data[]` by machine compatible and clkctrl base address, then iterates register entries. Register entries create a main module clock and optional gate/mux/divider subclocks for timers, UARTs, McASP, MMC, DSS, GMAC, QSPI, PCIe, ATL, GPIO debounce clocks, and other DRA7 domains. `dra7xx_dt_clk_init()` registers aliases, disables autoidle globally, adds fixed/simple aliases, sets GMAC and USB DPLL rates, sets USB M2 to half rate, and enables `dss_deshdcp_clk`.

State and persistence: static tables disappear after init; persistent state is in registered CCF clocks and hardware PRCM/DPLL registers. The initializer programs live DPLL rates and enables one DSS-related clock without releasing it.

Dependencies/integration: depends on `dt-bindings/clock/dra7.h`, CCF, clkdev aliases, TI clkctrl registration, and parent clock names created by DTS/other TI clock files. SoC flags (`CLKF_SOC_DRA72`, `CLKF_SOC_DRA74`, `CLKF_SOC_DRA76`, `CLKF_SOC_NONSEC`) gate entries for SKU/security variants.

Risks: correctness is table driven, so wrong offsets, bit positions, parent names, or SoC masks silently create broken clocks. Boot-time `clk_get_sys()` results are not checked with `IS_ERR()` before `clk_set_rate()`/`clk_prepare_enable()`, relying on complete clock data. DPLL rate programming failures are logged but initialization returns only the last `rc`.

Test signals: boot DRA7-family kernels with clk debug enabled, verify no "failed to lookup clock node" or DPLL setup errors, inspect `/sys/kernel/debug/clk/clk_summary`, exercise MMC/UART/timer/USB/GMAC/DSS/ATL peripherals, and validate DT bindings produce matching clkctrl node names and two-argument clkctrl phandles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clk-7xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clk-814x.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/clk-814x.c

Purpose: DM814x/TI81xx clock-control metadata and early ADPLL initialization glue. It defines clkctrl register tables for default, always-on, and Ethernet clock blocks, a small legacy alias table, and initcall sequencing for PLL subsystem population.

Important APIs/types/functions: exports `dm814_clkctrl_data[]`; defines `dm814x_dt_clk_init()`, `dm814x_adpll_early_init()` as `core_initcall`, and `dm814x_adpll_enable_init_clocks()` as `postcore_initcall`. Uses `omap_clkctrl_reg_data`, `ti_dt_clk`, `of_platform_populate()`, and `omap2_clk_enable_init_clocks()`.

Control flow: `dm814x_dt_clk_init()` registers `timer_sys_ck`, disables autoidle, adds aliases, enables no named init clocks, and sets `timer_clocks_initialized`. Later initcalls are gated on that boolean: the core initcall locates the `pllss` node and populates ADPLL platform devices; the postcore initcall obtains and enables `pll040clkout` and `pll290clkout`.

State and persistence: tables are init-only. Persistent state consists of clkctrl registrations, populated ADPLL child devices, and enabled MPU/DDR ADPLL output clocks. `timer_clocks_initialized` is a static sequencing guard.

Dependencies/integration: selected by TI81xx machine support and `dt-bindings/clock/dm814.h`; integrated with `clkctrl.c` through the exported data table. Requires DTS to provide a `pllss` node and clock names matching `pll040clkout` and `pll290clkout`.

Risks: ADPLL population is skipped if the main init did not run, and missing `pllss` or init clocks only logs warnings/errors. The Ethernet clkctrl entry uses offset `0` at a base address, so the base address must be exact.

Test signals: boot DM814x with DT clock debug, confirm `pllss` child devices probe after timers are ready, verify UART/GPIO/I2C/MMC/GPMC clocks can enable, and check warning logs for missing init clocks or clkctrl aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clk-814x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clk-816x.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/clk-816x.c

Purpose: DM816x/TI81xx clkctrl metadata and boot-time legacy alias setup. The file maps default and always-on PRCM clock-control registers to parent clocks and declares a few clock aliases expected by timer and legacy platform code.

Important APIs/types/functions: exports `dm816_clkctrl_data[]`; defines `dm816x_dt_clk_init()`. Uses `omap_clkctrl_reg_data`, `ti_dt_clk`, `DT_CLK()`, and `omap2_clk_enable_init_clocks()`.

Control flow: clkctrl metadata is consumed by `clkctrl.c` when the machine compatible is `ti,dm816`. `dm816x_dt_clk_init()` registers aliases for system and timer clocks, disables autoidle, adds simple aliases, and enables DDR PLL outputs plus `sysclk6_ck`.

State and persistence: source tables are init-only; enabled init clocks and PRCM module state persist. No private runtime structure is allocated here.

Dependencies/integration: depends on `dt-bindings/clock/dm816.h`, CCF, TI clkctrl common code, and clock providers for `ddr_pll_clk1/2/3`, `sysclk6_ck`, and sysclk/timer parents.

Risks: all module access relies on correct parent clock names and register offsets. `CLKF_NO_IDLEST` on watchdog, RTC, MDIO, and EMAC avoids waiting for idle status; incorrect use would hide readiness failures or cause timeouts if removed.

Test signals: boot DM816x, inspect clk summary for sysclk aliases, verify USB/UART/GPIO/I2C/timer/MMC/GPMC/EMAC module clock enable paths, and watch for init-clock warnings during boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clk-816x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clk-dra7-atl.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/clk-dra7-atl.c

Purpose: DRA7 Audio Tracking Logic clock driver. It registers four ATL clock outputs early as CCF clocks and later binds them to the ATL hardware platform device, programming ATL mux/divider registers and runtime PM when clocks are enabled.

Important APIs/types/functions: `of_dra7_atl_clock_setup()` handles `ti,dra7-atl-clock` clock nodes; `of_dra7_atl_clk_probe()` handles the `ti,dra7-atl` platform device. `dra7_atl_desc` stores per-output clock state (`probed`, `valid`, `enabled`, BWS/AWS/divider), and `dra7_atl_clock_info` stores device and MMIO base. `atl_clk_ops` implements enable, disable, is_enabled, recalc, determine_rate, and set_rate.

Control flow: early DT clock setup allocates a descriptor, validates one parent, registers the clock with `CLK_IGNORE_UNUSED`, and provides it to consumers. Platform probe maps MMIO, enables PM, configures PCLKMUX, resolves each `ti,provided-clocks` phandle back to its descriptor, optionally reads child `atl0`..`atl3` BWS/AWS properties, writes mux configuration, marks descriptors probed, and replays enable if a consumer enabled the clock before the hardware driver loaded.

State and persistence: per-clock descriptors persist for the life of the built-in driver. Divider values are cached until enable, and `enabled` is software state used before and after probe. BWS/AWS and SWEN/ATLCR are programmed into hardware registers; runtime PM references are acquired while enabled.

Dependencies/integration: uses OF clock providers, platform bus, runtime PM, raw MMIO, and TI clock registration helpers. Consumers obtain clocks from the early `ti,dra7-atl-clock` nodes while the hardware node provides register access and phandle binding.

Risks: `divider - 1` is written on enable; the default divider is one, but bad rate paths must not leave zero. Probe assumes exactly four `ti,provided-clocks`; missing phandles fail the whole probe. Runtime PM return values are not checked. Unconfigured ATL instances still enable with only a warning.

Test signals: validate DT with four provided clocks and optional `atlN` children, request rates from audio drivers, enable before and after platform probe, inspect ATL registers, and test runtime PM balance across enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clk-dra7-atl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/clk.c

Purpose: shared TI clock infrastructure. It provides low-level register access indirection, DT clock alias registration, retry initialization, provider memory-map indexing, feature setup, common alias helpers, and tracking for registered `clk_hw_omap` clocks.

Important APIs/types/functions: `ti_clk_setup_ll_ops()`, `ti_dt_clocks_register()`, `ti_clk_retry_init()`, `ti_clk_get_reg_addr()`, `ti_clk_latch()`, `omap2_clk_provider_init()`, `omap2_clk_legacy_provider_init()`, `ti_dt_clk_init_retry_clks()`, `ti_clk_add_aliases()`, `ti_clk_setup_features()`, `omap2_clk_enable_init_clocks()`, `of_ti_clk_register()`, `of_ti_clk_register_omap_hw()`, `omap2_clk_for_each()`, and `omap2_clk_is_hw_omap()`.

Control flow: platform code first installs `ti_clk_ll_ops`, which is augmented with this file's read/write/rmw callbacks. Provider init maps clock DT parent nodes to `clk_memmaps[]`. Individual clock setup code then calls `ti_clk_get_reg_addr()` to encode provider index, offset, and bit. Alias registration resolves legacy `DT_CLK` names by `clock-output-names`, node names, or clkctrl phandle arguments and adds `clkdev` lookups.

State and persistence: persistent globals include `ti_clk_ll_ops`, `ti_clk_features`, `clocks_node_ptr[]`, `clk_memmaps[]`, `clk_hw_omap_clocks`, and `retry_list`. Legacy provider data may be allocated from memblock. Retry entries are consumed and freed by `ti_dt_clk_init_retry_clks()`.

Dependencies/integration: integrates Linux CCF, clkdev, OF, regmap/syscon or MMIO, and platform-specific low-level clockdomain/CM callbacks. It is the hub used by TI gate/divider/mux/DPLL/composite/clkctrl files.

Risks: memory-map indexes must match provider setup or register access goes to the wrong region. `ti_dt_clocks_register()` has compatibility behavior for old clkctrl layouts and can suppress repeated warnings after missing clkctrl nodes. Retry processing has a bounded retry count but does not verify that callbacks succeeded.

Test signals: unit-style coverage is mostly boot-time: verify provider init order, alias lookup for old and new DT naming, regmap and MMIO access paths, retry list draining, and `clk_summary` consistency after clock registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clkctrl.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/clkctrl.c

Purpose: OMAP4-style clkctrl provider implementation. It turns SoC-specific `omap_clkctrl_data[]` tables into CCF module clocks and optional subclocks, handles MODULEMODE enable/disable, waits for IDLEST transitions, and exposes two-cell clkctrl phandle translation.

Important APIs/types/functions: `CLK_OF_DECLARE(... "ti,clkctrl", _ti_omap4_clkctrl_setup)`, `_omap4_clkctrl_clk_enable()`, `_omap4_clkctrl_clk_disable()`, `_ti_omap4_clkctrl_xlate()`, `_ti_clkctrl_setup_gate/mux/div/subclks()`, `_ti_clkctrl_clk_register()`, and exported `ti_clk_is_in_standby()`. Internal state lives in `omap_clkctrl_provider` and `omap_clkctrl_clk`.

Control flow: setup maps node address, selects SoC data by machine compatible, applies SoC/security masks, derives a clockdomain name, maps MMIO, and iterates matching register entries. Each entry can create gate/mux/divider subclocks from bit data, then creates a primary module clock with SW or HW supervisor mode. The OF provider later resolves `<offset bit>` phandle arguments by scanning the provider list.

State and persistence: provider lists and allocated clocks persist. Runtime state is in PRCM MODULEMODE, IDLEST, and STBYST bits. `_early_timeout` switches from udelay loop counting to ktime-based timeout at `arch_initcall`, but timekeeping-suspended paths continue using delay loops.

Dependencies/integration: consumes SoC clkctrl tables from DRA7, OMAP, AM3/AM4, DM814, and DM816 files. Depends on `ti_clk_ll_ops`, clockdomain callbacks, CCF, OF address resources, and generated parent clock names.

Risks: offset/name generation must match DTS and alias tables. Incorrect `CLKF_NO_IDLEST` or supervisor flags cause hangs, false readiness, or modules left unmanaged. Timeout logic differs during early boot and suspend, which matters for clocks used by timers or PM.

Test signals: boot each supported SoC family, resolve clkctrl phandles, enable/disable modules, verify timeout logs are absent, test suspend/resume with clkctrl users, and inspect `ti_clk_is_in_standby()` behavior for OMAP clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clkctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clkt_dflt.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/clkt_dflt.c

Purpose: default OMAP module clock operations for legacy non-clkctrl clocks. It enables/disables module clocks, coordinates clockdomain use counts, and waits for modules to leave idle through default companion/IDLEST register discovery.

Important APIs/types/functions: `omap2_dflt_clk_enable()`, `omap2_dflt_clk_disable()`, `omap2_dflt_clk_is_enabled()`, `omap2_clk_dflt_find_companion()`, `omap2_clk_dflt_find_idlest()`, and exported `clkhwops_wait`. Internal helpers `_omap2_module_wait_ready()` and `_wait_idlest_generic()` implement readiness waits.

Control flow: enable optionally enables the clockdomain, sets or clears the enable bit depending on `INVERT_ENABLE`, performs an OCP barrier read, and calls the clock's `find_idlest` path. Readiness checks optionally require a companion functional/interface clock before waiting on CM IDLEST or a generic external IDLEST register. Disable clears the hardware enable bit and decrements the clockdomain if enabled.

State and persistence: no private allocations. State is held in hardware enable/IDLEST registers and in low-level clockdomain use counts. `clkhwops_wait` plugs default `find_idlest`/`find_companion` behavior into `clk_hw_omap` instances.

Dependencies/integration: depends on `ti_clk_ll_ops` for CM register access, `ti_clk_features` for IDLEST polarity, and clockdomain callbacks. Used by gate and interface clock setup.

Risks: register offset derivation assumes old CM register layouts (`FCLKEN`, `ICLKEN`, `IDLEST`). Generic wait has a large busy-wait timeout. Incorrect feature IDLEST polarity or companion offsets can skip waits or report false failures.

Test signals: enable legacy OMAP interface/function clocks, confirm modules become ready without timeout logs, test inverted enables, and validate clockdomain use count transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clkt_dflt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clkt_dpll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/clkt_dpll.c

Purpose: common OMAP2/3/4 DPLL rate math. It calculates current DPLL rates, initial parent selection, valid M/N settings, and rounded rates for later hardware programming by SoC-specific DPLL code.

Important APIs/types/functions: `omap2_init_dpll_parent()`, `omap2_get_dpll_rate()`, and `omap2_dpll_determine_rate()`. Helpers `_dpll_test_fint()`, `_dpll_test_mult()`, `_dpll_compute_new_rate()`, and `_omap2_dpll_is_in_bypass()` enforce hardware limits and bypass behavior.

Control flow: `omap2_init_dpll_parent()` reads enable bits and returns bypass parent index when needed. `omap2_get_dpll_rate()` returns bypass parent rate if the enable mode is a bypass value, otherwise computes `ref * M / (N + 1)` from hardware registers. `omap2_dpll_determine_rate()` iterates divider N, validates Fint ranges, computes a scaled multiplier, rejects rates above target, and stores `last_rounded_m`, `last_rounded_n`, and `last_rounded_rate` in `dpll_data`.

State and persistence: this file mutates `dpll_data` rounding caches and min/max divider fields. It does not write hardware registers directly except reads through `ti_clk_ll_ops`.

Dependencies/integration: used by `dpll.c`, `dpll3xxx.c`, and `dpll44xx.c`; depends on `ti_clk_features` for Fint limits and bypass value masks.

Risks: rounding deliberately chooses the closest rate not greater than target, which may surprise consumers expecting nearest rate. `_dpll_test_fint()` updates divider bounds while searching. J-type Fint constants are selected but some comparisons still use feature limits, so platform features must be correct.

Test signals: rate-rounding tests across parent rates and DPLL variants, current-rate checks in bypass and locked modes, and validation that cached M/N values match hardware programming performed later.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clkt_dpll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clkt_iclk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/clkt_iclk.c

Purpose: OMAP2/3 interface-clock helper operations. It provides AUTOIDLE allow/deny helpers and special IDLEST lookup behavior for OMAP2430 I2CHS clocks.

Important APIs/types/functions: `omap2_clkt_iclk_allow_idle()`, `omap2_clkt_iclk_deny_idle()`, `clkhwops_iclk`, `clkhwops_iclk_wait`, and `clkhwops_omap2430_i2chs_wait`. The special `omap2430_clk_i2chs_find_idlest()` maps I2CHS CM clock enable offsets to the correct IDLEST register.

Control flow: allow/deny functions copy the enable register, transform the offset from `CM_ICLKEN` to `CM_AUTOIDLE`, then set or clear the enable bit. The ops structures are selected by interface clock registration and later invoked by clock management paths.

State and persistence: no allocated state. Persistent effects are AUTOIDLE bits in CM registers.

Dependencies/integration: uses `ti_clk_ll_ops`; integrates with interface and composite interface clock setup in `interface.c` and `gate.c`; reuses default IDLEST/companion helpers from `clkt_dflt.c`.

Risks: offset XOR assumptions are specific to legacy CM layout. Wrong ops on OMAP2430 I2CHS would wait on the wrong IDLEST register.

Test signals: toggle AUTOIDLE through clock framework idle paths, verify I2CHS readiness on OMAP2430, and confirm no regressions for generic OMAP3 interface clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clkt_iclk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clock.h -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/clock.h

Purpose: internal header for TI clock drivers. It defines shared clock wrapper structures, table schemas, flag bits, macros, extern data declarations, and cross-file helper prototypes.

Important APIs/types/functions: structures include `clk_omap_divider`, `clk_omap_mux`, `ti_clk`, `ti_clk_mux`, `ti_clk_divider`, `ti_clk_gate`, `ti_dt_clk`, `omap_clkctrl_div_data`, `omap_clkctrl_bit_data`, `omap_clkctrl_reg_data`, and `omap_clkctrl_data`. It declares ops such as `ti_clk_divider_ops`, `ti_clk_mux_ops`, `omap_gate_clk_ops`, and helpers across registration, clockdomain, DPLL, divider, mux, gate, and clkctrl paths.

Control flow: no executable code, but the flag definitions determine behavior in setup and runtime paths. Global flags describe legacy index schemes and rate-parent behavior; gate flags select waits, inverted enables, and clockdomain handling; DPLL flags select modes; clkctrl flags select module supervision and SoC masks.

State and persistence: wrapper structs hold runtime context such as divider register context, mux saved parent, DPLL cached values through referenced public TI structures, and clkctrl table metadata. The header also exposes global `ti_clk_features` and `ti_clk_ll_ops`.

Dependencies/integration: this header is the internal contract among all files in `drivers/clk/ti`. Public pieces from `<linux/clk/ti.h>` and CCF types are assumed.

Risks: bit values are reused across flag domains, so callers must pass the right flag namespace. Structure layout is relied on by `container_of()` macros. Any signature change affects many clock setup files.

Test signals: compile coverage across enabled SoC configs is the primary signal; runtime coverage comes from exercising each declared ops structure and table type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clockdomain.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/clockdomain.c

Purpose: bridges TI clock framework clocks to OMAP clockdomains. It looks up clockdomain names, stores pointers in `clk_hw_omap`, exposes enable/disable helpers for clocks that do not use default gate ops, and supports DT `ti,clockdomain` nodes.

Important APIs/types/functions: `omap2_clkops_enable_clkdm()`, `omap2_clkops_disable_clkdm()`, `omap2_init_clk_clkdm()`, and `ti_dt_clockdomains_setup()`. `of_ti_clockdomain_setup()` applies one clockdomain name to all parent clocks of a `ti,clockdomain` node.

Control flow: during clock registration, `.init = omap2_init_clk_clkdm` resolves `clkdm_name` through `ti_clk_ll_ops->clkdm_lookup()`. Runtime enable/disable helpers increment/decrement clockdomain use counts. DT setup walks matching nodes after clock registration and retrofits `clkdm_name` onto listed OMAP clocks.

State and persistence: clockdomain pointer and name live in each `clk_hw_omap`. Actual use counts are maintained by platform clockdomain code behind low-level callbacks.

Dependencies/integration: depends on `ti_clk_ll_ops` clockdomain callbacks and on `omap2_clk_is_hw_omap()` to reject basic CCF clocks. Used by gate, interface, DPLL, and clkctrl operations.

Risks: missing clockdomain names are nonfatal but can leave power-domain control incomplete. DT clockdomain setup warns and skips basic clocks, so mixed lists need review. Feature flag `TI_CLK_DISABLE_CLKDM_CONTROL` changes runtime semantics.

Test signals: verify clockdomain lookup logs, enable/disable clocks while checking clockdomain use counts, parse DT `ti,clockdomain` nodes, and test platforms with framework clockdomain control disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clockdomain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/composite.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/composite.c

Purpose: TI composite clock assembly. It collects separately declared mux/divider/gate component clocks and registers one CCF composite clock when all referenced components are available.

Important APIs/types/functions: `of_ti_composite_clk_setup()` for `ti,composite-clock`, `ti_clk_add_component()`, `_register_composite()`, and internal `component_clk`/`clk_hw_omap_comp`. Composite divider ops delegate recalc to `ti_clk_divider_ops` but reject rate changes in this wrapper; composite gate ops use default OMAP gate enable/disable.

Control flow: component setup files call `ti_clk_add_component()` to store component `clk_hw`, parent names, node pointer, and type. Composite setup records component phandle nodes and calls `_register_composite()`. If a component is missing, registration enters the TI retry list. Once all components are present, it chooses parent names from the highest-priority available component, calls `clk_register_composite()`, adds an alias/provider, and frees component list entries.

State and persistence: pending component list entries persist until consumed. The final composite clock persists in CCF; temporary assembly structs are freed after registration.

Dependencies/integration: integrates with `divider.c`, `mux.c`, and `gate.c` composite component declarations, OF phandles, TI retry init, and CCF composite registration.

Risks: duplicate component types or missing parents abort registration. Component entries are removed and freed when consumed, so a component node cannot safely be shared by multiple composites. Rate changes for composite dividers are intentionally disabled.

Test signals: DT composite-clock nodes with delayed component registration, duplicate/missing component negative tests, provider lookup by composite node, and parent/rate behavior through mux/divider/gate subcomponents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/composite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/divider.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/divider.c

Purpose: TI divider clock implementation for standalone and composite component divider clocks. It parses DT divider properties, calculates masks/rates, programs divider registers, latches changes, and saves/restores context.

Important APIs/types/functions: exported `ti_clk_divider_ops`, `ti_clk_parse_divider_data()`, `of_ti_divider_clk_setup()`, and `of_ti_composite_divider_clk_setup()`. Key helpers include `_get_div()`, `_get_val()`, `ti_clk_divider_bestdiv()`, `ti_clk_divider_determine_rate()`, `ti_clk_divider_set_rate()`, and context save/restore callbacks.

Control flow: setup obtains the register address and bit shift, optional latch bit, index scheme flags, optional set-rate-parent flag, optional divider table, and min/max values. Runtime recalc reads the register field and converts it to a divisor. Determine-rate selects the best divisor, optionally asking the parent to round. Set-rate clamps the divisor, writes the encoded value, and pulses the latch bit if present.

State and persistence: each divider holds register location, shift, mask, min/max, optional table, latch, flags, and saved context. Hardware register fields persist across runtime; context callbacks preserve values across suspend/resume.

Dependencies/integration: uses `ti_clk_get_reg_addr()`, `ti_clk_latch()`, CCF rate APIs, DT properties `ti,dividers`, `ti,min-div`, `ti,max-div`, and component assembly through `ti_clk_add_component()`.

Risks: table allocation is permanent for registered clocks. Zero divisors return parent rate unless explicitly allowed, potentially masking bad hardware state. Best-divider search can alter parent rates when `CLK_SET_RATE_PARENT` is set, so parent capabilities matter.

Test signals: fixed divisor tables, one-based and power-of-two encodings, latch behavior, set-rate-parent cases, suspend/resume context restore, and invalid DT without `ti,max-div`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/divider.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/dpll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/dpll.c

Purpose: device-tree registration layer for TI/OMAP DPLL clocks. It binds compatible strings to appropriate `clk_ops` and `dpll_data` templates, parses DPLL register resources and optional spread-spectrum data, and registers DPLL or DPLLx2 clocks with CCF.

Important APIs/types/functions: `_register_dpll()`, `_register_dpll_x2()`, `of_ti_dpll_setup()`, and many `CLK_OF_DECLARE()` setup functions for OMAP2, OMAP3, OMAP4, OMAP5, AM3, AM4, DRA7, J-type, M4XEN, no-gate, and x2 variants. It wires ops from `clkt_dpll.c`, `dpll3xxx.c`, and `dpll44xx.c`.

Control flow: setup duplicates a DPLL data template, allocates `clk_hw_omap` and `clk_init_data`, fills parent names, parses control/idlest/mult-div/autoidle/SSC registers, reads mode properties, adjusts min divider, then calls `_register_dpll()`. `_register_dpll()` obtains clk-ref and clk-bypass parents; if unavailable, it schedules retry. Successful registration adds a simple OF clock provider and frees init-time parent arrays.

State and persistence: registered DPLL clocks keep `dpll_data` with register descriptors, masks, mode flags, parent `clk_hw` pointers, and cached rounded values. Init allocations become CCF clock state; failed registrations free them.

Dependencies/integration: depends on `clock.h`, CCF, OF, TI register mapping, SoC config guards, and DPLL runtime ops from other TI files.

Risks: compatible strings must select the exact mask template. Parent ordering is fixed: reference parent first, bypass parent second. Retry list hides order dependencies but only if callbacks eventually succeed. SSC fields are optional but must be complete to program spread spectrum.

Test signals: boot each compatible family, verify DPLL providers appear, test missing-parent retry, set rates for normal/J-type/M4XEN/no-gate variants, validate x2 recalc, and suspend/resume through save/restore ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/dpll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/dpll3xxx.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/dpll3xxx.c

Purpose: OMAP3/OMAP4-style non-core DPLL runtime control. It handles DPLL lock/bypass/stop transitions, M/N programming, FREQSEL/DCO/SD divider calculation, spread-spectrum programming, errata workarounds, x2 output rates, and DPLL context save/restore.

Important APIs/types/functions: `omap3_dpll_recalc()`, `omap3_noncore_dpll_enable()`, `omap3_noncore_dpll_disable()`, `omap3_noncore_dpll_determine_rate()`, `omap3_noncore_dpll_set_parent()`, `omap3_noncore_dpll_set_rate()`, `omap3_noncore_dpll_set_rate_and_parent()`, `omap3_clkoutx2_recalc()`, `omap3_core_dpll_save_context()/restore_context()`, `omap3_noncore_dpll_save_context()/restore_context()`, `omap3_dpll4_set_rate()`, and `omap3_dpll5_set_rate()`.

Control flow: enable chooses bypass if current rate equals bypass parent, otherwise locks on reference parent. Set-rate requires the reference parent and a previous successful determine-rate cache, optionally computes FREQSEL, then bypasses the DPLL, writes M/N and optional DCC/DCO/SDDIV/M4XEN/low-power/SSC fields, and locks. Context restore compares saved state with hardware and either reprograms or writes enable mode directly.

State and persistence: DPLL hardware registers hold mode, M/N, autoidle, SSC, and lock state. `dpll_data` caches rounded M/N/rate and restore values; `clk_hw_omap.context` stores enable mode. Autoidle may be temporarily denied during programming and restored afterward.

Dependencies/integration: depends on rate caches from `clkt_dpll.c`, low-level register callbacks, CCF parent rates, feature flags for FREQSEL and errata i810, and DPLL templates from `dpll.c`.

Risks: transition waits busy-loop up to one million microseconds. Hardware programming assumes `last_rounded_*` are valid. Errata-specific paths are critical for DPLL4 and DPLL5 USB host operation. SSC arithmetic can produce warnings for out-of-range modulation.

Test signals: DPLL lock/bypass/stop transitions, rate changes on supported variants, errata paths for OMAP36xx DPLL5 and OMAP3430ES1 DPLL4 denial, SSC programming, x2 output rates, and suspend/resume register-loss restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/dpll3xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/dpll44xx.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/dpll44xx.c

Purpose: OMAP4-specific DPLL helpers for DPLL M4XEN and DPLL output gate-control behavior. It adjusts rate calculations for the 4x multiplier and computes low-power mode eligibility.

Important APIs/types/functions: exported `clkhwops_omap4_dpllmx`, `omap4_dpll_regm4xen_recalc()`, and `omap4_dpll_regm4xen_determine_rate()`. Internal helpers `omap4_dpllmx_allow_gatectrl()`, `omap4_dpllmx_deny_gatectrl()`, and `omap4_dpll_lpmode_recalc()` operate on control fields.

Control flow: Mx output idle ops clear or set the DPLL CLKOUT/CLKOUTX2 gate-control mask in `clksel_reg`. Rate recalc calls common `omap2_get_dpll_rate()` and multiplies by four if REGM4XEN is set. Determine-rate first tries normal DPLL rounding; if that fails, it retries with target divided by four and marks `last_rounded_m4xen`. It also computes whether low-power mode can be used from Fint/Fout thresholds.

State and persistence: state is stored in DPLL control/clksel registers and in `dpll_data` fields `last_rounded_m4xen` and `last_rounded_lpmode`.

Dependencies/integration: used by `dpll.c` for OMAP4/DRA7 M4XEN and x2 clocks; depends on common DPLL rounding and low-level register callbacks.

Risks: the low-power Fint calculation uses cached N semantics, so it must match the rounding/programming convention. Missing clksel register data causes x2 registration to drop hw-ops, changing gate-control behavior.

Test signals: rate requests that require and do not require REGM4XEN, gatectrl allow/deny on CLKOUT and CLKOUTX2, and low-power bit programming through subsequent DPLL set-rate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/dpll44xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/fapll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/fapll.c

Purpose: DM816 Flying Adder PLL and synthesizer clock driver. It registers a parent FAPLL with two parents and up to seven output clocks, including fractional synthesizers and fixed/hardwired special cases.

Important APIs/types/functions: `ti_fapll_setup()` for `ti,dm816-fapll-clock`, `ti_fapll_ops`, `ti_fapll_synt_ops`, `ti_fapll_synth_setup()`, and structures `fapll_data` and `fapll_synth`.

Control flow: setup maps the FAPLL base, obtains reference and bypass parents, detects inverted bypass behavior for DDR PLL, registers the main PLL, then iterates `clock-output-names` and optional `clock-indices` to register synthesizer outputs. Runtime main PLL ops enable/disable PLLEN, calculate bypass or `parent / P * N`, choose parent by bypass bit, and set rate by entering bypass, writing P/N, waiting for lock, and clearing bypass. Synth ops power outputs via PWD bits, compute fractional/post-divider rates, and program frequency/divider load bits.

State and persistence: `fapll_data` owns base MMIO, parent clocks, onecell output array, and bypass polarity. `fapll_synth` owns per-output register pointers and index. Hardware PLL, PWD, synth frequency, and divider registers persist.

Dependencies/integration: uses raw MMIO, CCF onecell providers, clkdev for synthesizer names, OF address/clock properties, and DM816 TRM-specific register layouts.

Risks: address-based special cases (`fapll_is_ddr_pll`, `is_audio_pll_clk1`) depend on mapped virtual address low bits matching hardware offsets, which is fragile. `ti_fapll_determine_rate()` stores an error code in `req->rate` but returns success. Main divider rates below parent are unsupported.

Test signals: DM816 boot with FAPLL nodes, lock timeout behavior, main PLL set-rate and bypass parent changes, fixed audio 32.768 kHz output, fractional synth rate programming, and onecell index holes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/fapll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/fixed-factor.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/fixed-factor.c

Purpose: TI-specific DT wrapper for fixed-factor clocks. It reads TI property names and registers a standard CCF fixed-factor clock with alias and optional autoidle setup.

Important APIs/types/functions: `of_ti_fixed_factor_clk_setup()` for `ti,fixed-factor-clock`. It uses `clk_register_fixed_factor()`, `ti_dt_clk_name()`, `ti_clk_add_alias()`, and `of_ti_clk_autoidle_setup()`.

Control flow: setup requires `ti,clock-div` and `ti,clock-mult`, optionally sets `CLK_SET_RATE_PARENT`, obtains the first parent name, registers the fixed-factor clock, adds an OF provider, configures autoidle, and creates a clkdev alias.

State and persistence: no private state beyond the CCF fixed-factor clock and optional autoidle side effects.

Dependencies/integration: depends on DT properties, one parent clock, CCF fixed-factor ops, and TI alias/autoidle helpers.

Risks: missing div/mult properties abort registration. The code does not validate zero divisors directly; behavior depends on CCF fixed-factor validation. Parent absence still passes a NULL parent name.

Test signals: DT nodes with valid and missing mult/div, set-rate-parent propagation, provider lookup, and alias lookup by output name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/fixed-factor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/gate.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/gate.c

Purpose: OMAP/TI gate clock registration and operations. It registers standalone gates, wait gates, clockdomain-only gates, HSDIV gates, and composite gate components.

Important APIs/types/functions: exported `omap_gate_clk_ops`, internal `omap_gate_clkdm_clk_ops`, `omap_gate_clk_hsdiv_restore_ops`, `_register_gate()`, `_of_ti_gate_clk_setup()`, `_of_ti_composite_gate_clk_setup()`, and multiple `CLK_OF_DECLARE()` setup functions. `omap36xx_gate_clk_enable_with_hsdiv_restore()` implements errata i556.

Control flow: standalone setup parses register/bit unless the gate only controls a clockdomain, validates one parent, handles `ti,set-rate-parent` and inverted enable, registers a `clk_hw_omap`, and adds an OF provider. Composite setup builds a `clk_hw_omap` gate component for later assembly. Runtime ops use default OMAP enable/disable or clockdomain-only enable/disable. HSDIV restore first enables the gate, then toggles the parent divider register to reload divider values after PWRDN.

State and persistence: each gate stores enable register, bit, flags, optional hardware ops, and clockdomain pointer after init. Context restore delegates to generic `clk_gate_restore_context`.

Dependencies/integration: depends on `clkt_dflt.c`, `clockdomain.c`, `clkt_iclk.c` ops for variants, `ti_clk_get_reg_addr()`, and composite assembly.

Risks: HSDIV workaround assumes a specific parent hierarchy. Clockdomain-only gates skip register parsing and rely entirely on clockdomain callbacks. Inverted enable flags must match hardware polarity.

Test signals: enable/disable each compatible gate type, composite gate assembly, inverted gate behavior, HSDIV errata reload, and context restore after suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/gate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/interface.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/interface.c

Purpose: OMAP interface clock registration. It wraps interface clocks in `clk_hw_omap` and selects the proper idle/wait ops for generic, no-wait, OMAP3 special, AM35xx, and OMAP2430 variants.

Important APIs/types/functions: `_register_interface()`, `_of_ti_interface_clk_setup()`, and `CLK_OF_DECLARE()` handlers for `ti,omap3-interface-clock`, `ti,omap3-no-wait-interface-clock`, `ti,omap3-hsotgusb-interface-clock`, `ti,omap3-dss-interface-clock`, `ti,omap3-ssi-interface-clock`, `ti,am35xx-interface-clock`, and `ti,omap2430-interface-clock`.

Control flow: setup parses the register bit, requires one parent, names the clock, registers it with `ti_interface_clk_ops`, and publishes an OF provider. Runtime operations use default enable/disable/is_enabled with clockdomain initialization, while chosen `clk_hw_omap_ops` determine idle allowance and IDLEST wait behavior.

State and persistence: each interface clock stores enable register and bit plus optional ops. Hardware CM enable/idle bits persist.

Dependencies/integration: uses `ti_clk_get_reg_addr()`, `of_ti_clk_register_omap_hw()`, default OMAP clock ops, and special ops from `clkt_iclk.c` and SoC-specific files.

Risks: wrong compatible string changes wait behavior and can cause boot hangs or skipped readiness waits. Parent is mandatory and missing parent aborts registration.

Test signals: DT registration for each compatible variant, module enable waits, no-wait behavior for clocks without reliable IDLEST, and SoC-specific interface clocks under suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/interface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/mux.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/mux.c

Purpose: TI mux clock implementation for standalone mux clocks and composite mux components. It reads/writes mux selector fields, supports legacy index encodings, latches updates, and saves/restores selected parents.

Important APIs/types/functions: exported `ti_clk_mux_ops`, `of_mux_clk_setup()`, `ti_clk_build_component_mux()`, and `of_ti_composite_mux_clk_setup()`. Runtime ops are `ti_clk_mux_get_parent()`, `ti_clk_mux_set_parent()`, context save, and context restore.

Control flow: standalone setup requires at least two parents, fills parent names, parses register/shift and optional latch bit, handles one-based indices and set-rate-parent, computes a selector mask from parent count, registers the mux, and adds an OF provider. Runtime get reads and decodes the selector through an optional table, bit index, or one-based index. Set encodes the parent index, writes with optional hiword mask support, and pulses latch.

State and persistence: mux structures hold register location, mask, shift, latch, flags, optional table, and saved parent. Hardware selector fields persist; context callbacks restore them.

Dependencies/integration: uses `ti_clk_get_reg_addr()`, `ti_clk_latch()`, CCF mux rate determination, and composite registration through `ti_clk_add_component()`.

Risks: the code comments note ambiguity between bitwise and numeric selector encodings. `CLK_MUX_INDEX_BIT` encoding uses `ffs(index)`, which is sensitive to zero-based assumptions. Parent count determines mask width, so holes require tables.

Test signals: parent switching for zero-based, one-based, table, and bit encodings; latch behavior; save/restore selected parent; and composite mux registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/uniphier/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/uniphier/Kconfig

Purpose: Kconfig option for the UniPhier clock controller driver.

Important APIs/types/functions: defines `CONFIG_CLK_UNIPHIER` as a boolean prompt "Clock driver for UniPhier SoCs". It depends on `ARCH_UNIPHIER || COMPILE_TEST`, and also on `OF && MFD_SYSCON`; it defaults to `ARCH_UNIPHIER`.

Control flow: build-time only. Enabling the option compiles the UniPhier clock driver objects listed by the local Makefile.

State and persistence: no runtime state. The config gates whether built-in platform clock drivers are present.

Dependencies/integration: captures required OF and syscon/regmap infrastructure for the table-driven clock provider.

Risks: disabling the option on UniPhier prevents system, media I/O, peripheral, and SoC-glue clocks from registering. The option is bool rather than tristate, matching builtin platform driver usage.

Test signals: Kconfig dependency resolution for UniPhier and COMPILE_TEST builds, and build coverage with OF/syscon disabled to confirm the option is hidden.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/uniphier/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/uniphier/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/uniphier/Makefile

Purpose: object list for UniPhier clock support.

Important APIs/types/functions: includes `clk-uniphier-core.o`, primitive helpers (`cpugear`, fixed-factor, fixed-rate, gate, mux), and SoC data objects (`sys`, `mio`, `peri`) in `obj-y`.

Control flow: build-time only. Once `CONFIG_CLK_UNIPHIER` causes this directory to build, all local objects are built in and the core builtin platform driver can reference data arrays and helper registration functions.

State and persistence: no runtime state, but the object ordering ensures core and helper/data code are linked together.

Dependencies/integration: integrates with the parent drivers/clk build. The use of `obj-y` aligns with builtin platform driver declarations.

Risks: adding a new UniPhier data/helper file requires updating this Makefile; otherwise compatible entries or helper symbols will be missing at link time.

Test signals: compile/link with `CONFIG_CLK_UNIPHIER=y`, verify all helper symbols resolve, and add build coverage when new UniPhier clock data files are introduced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/uniphier/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-core.c -->
# sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-core.c

Purpose: common UniPhier platform clock provider. It selects a SoC clock-data array by compatible string, gets the parent syscon regmap, registers each described clock, and publishes a onecell OF clock provider.

Important APIs/types/functions: `uniphier_clk_probe()`, `uniphier_clk_register()`, `uniphier_clk_match[]`, and builtin platform driver `uniphier_clk_driver`. It dispatches to `uniphier_clk_register_cpugear()`, fixed-factor, fixed-rate, gate, and mux helpers according to `uniphier_clk_data.type`.

Control flow: probe retrieves match data, obtains the parent node's syscon regmap, scans data to size `clk_hw_onecell_data` by maximum nonnegative index, initializes unused entries to `ERR_PTR(-EINVAL)`, registers every named clock, stores indexed clocks in `hws[idx]`, and calls `devm_of_clk_add_hw_provider()`.

State and persistence: all allocations are device-managed. The provider stores an array of `clk_hw` pointers for indexed outputs; unindexed internal clocks can serve as parents by name but are not exposed by cell index.

Dependencies/integration: requires DT clock nodes under a syscon parent, MFD syscon/regmap, CCF onecell provider support, and data arrays from `clk-uniphier-sys.c`, `mio.c`, and `peri.c`.

Risks: `idx` values must be dense enough for consumers but may intentionally leave holes. Helper registration failures warn and continue, possibly leaving an indexed output invalid. The parent must be a syscon node or probe fails.

Test signals: probe all compatible strings, inspect onecell indices, verify internal unindexed parents resolve by name, and test missing syscon parent or bad data entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-cpugear.c -->
# sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-cpugear.c

Purpose: UniPhier CPU gear clock implementation. It is a mux-like clock that changes CPU gear selection through a set register and update handshake.

Important APIs/types/functions: `uniphier_clk_register_cpugear()`, `uniphier_clk_cpugear_set_parent()`, `uniphier_clk_cpugear_get_parent()`, and `uniphier_clk_cpugear_ops`. Runtime state is in `struct uniphier_clk_cpugear`.

Control flow: registration allocates device-managed state, fills CCF init data with parent names and `CLK_SET_RATE_PARENT`, stores regmap/regbase/mask, and registers the hw. Set-parent writes the requested index to `SET`, asserts the `UPD` bit, then polls until hardware clears it. Get-parent reads `STAT`, masks the selector, and validates it against parent count.

State and persistence: regmap-backed hardware registers hold selected gear. Driver state stores regbase and selector mask only.

Dependencies/integration: used by system clock data for LD11/LD20/PXS3/NX1 CPU clocks; depends on regmap polling and parent factor clocks.

Risks: poll timeout is one microsecond total as written, so slow hardware update could fail. The selector value is assumed to be directly represented by `mask` without shifting.

Test signals: switch CPU gear parents, confirm `UPD` clears, validate reported parent against `STAT`, and test parent-rate propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-cpugear.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-fixed-factor.c -->
# sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-fixed-factor.c

Purpose: UniPhier helper for registering table-described fixed-factor clocks.

Important APIs/types/functions: `uniphier_clk_register_fixed_factor()` allocates a `clk_fixed_factor`, sets standard `clk_fixed_factor_ops`, optional parent, multiplier, and divisor, then registers via `devm_clk_hw_register()`.

Control flow: called by the core dispatcher for `UNIPHIER_CLK_TYPE_FIXED_FACTOR`. If the data has a parent name, the clock sets `CLK_SET_RATE_PARENT`; otherwise it is parentless. On allocation or registration failure it returns `ERR_PTR`.

State and persistence: device-managed `clk_fixed_factor` stores mult/div and CCF state. There is no MMIO.

Dependencies/integration: consumes `uniphier_clk_fixed_factor_data` from SoC data macros such as `UNIPHIER_CLK_FACTOR` and divider convenience macros.

Risks: data must not provide zero divisors. Parentless fixed factors are allowed by code but must make sense in the clock tree.

Test signals: rates for PLL-derived factor clocks, parentless entries, and compile coverage of all SoC tables using `UNIPHIER_CLK_FACTOR`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-fixed-factor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-fixed-rate.c -->
# sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-fixed-rate.c

Purpose: UniPhier helper for registering table-described fixed-rate clocks.

Important APIs/types/functions: `uniphier_clk_register_fixed_rate()` allocates `clk_fixed_rate`, sets `clk_fixed_rate_ops`, assigns `fixed_rate`, and registers device-managed CCF hw.

Control flow: called by core dispatcher for `UNIPHIER_CLK_TYPE_FIXED_RATE`. It creates a parentless clock with no flags and returns `ERR_PTR` on allocation or registration failure.

State and persistence: fixed rate value and CCF state persist as device-managed data. No hardware registers are touched.

Dependencies/integration: depends on SoC data using fixed-rate type and CCF fixed-rate ops.

Risks: fixed-rate data must match board/SoC reference clocks; incorrect values skew all descendants. There are no runtime validation hooks.

Test signals: clock summary rates for fixed-rate entries and consumers using those clocks as roots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-fixed-rate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-gate.c -->
# sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-gate.c

Purpose: UniPhier regmap-backed gate clock implementation.

Important APIs/types/functions: `uniphier_clk_register_gate()`, `uniphier_clk_gate_enable()`, `uniphier_clk_gate_disable()`, `uniphier_clk_gate_is_enabled()`, and `uniphier_clk_gate_ops`. State is `struct uniphier_clk_gate`.

Control flow: registration allocates state, sets parent and `CLK_SET_RATE_PARENT` when present, stores regmap/register/bit from data, and registers CCF hw. Enable/disable update one bit via `regmap_write_bits()`. `is_enabled()` reads the register and tests the bit.

State and persistence: hardware gate bits persist in syscon registers; driver state stores location metadata.

Dependencies/integration: used by UniPhier system, MIO, peripheral, and SoC-glue data. Depends on syscon regmap from the parent device.

Risks: disable and is_enabled cannot return regmap errors through void/u8 CCF interfaces, so they warn and continue. Parentless gates are allowed for root-controlled blocks.

Test signals: enable/disable every exposed gate index, check register bits, validate warning paths with regmap failure injection, and verify parent rate propagation when a parent exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-gate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-mio.c -->
# sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-mio.c

Purpose: UniPhier Media I/O and SD clock data. It describes SD rate parents, per-channel SD mux/gate clocks, MIO DMA, USB2 link, and USB2 PHY gates.

Important APIs/types/functions: exports `uniphier_ld4_mio_clk_data[]` and `uniphier_pro5_sd_clk_data[]`. Macros `UNIPHIER_MIO_CLK_SD_FIXED`, `UNIPHIER_MIO_CLK_SD()`, `UNIPHIER_MIO_CLK_USB2()`, and `UNIPHIER_MIO_CLK_USB2_PHY()` expand to fixed-factor, mux, and gate data.

Control flow: the core driver selects these arrays for MIO/SD compatible strings. Fixed SD rates are internal parents; each SD channel has an unindexed mux selecting among eight SD rates and an indexed gate exposing `sdN`. LD4-style data includes three SD channels, MIO DMA, and USB2/PHY gates; Pro5-style SD data exposes two SD channels.

State and persistence: no executable state; table entries drive helper allocations and syscon register bit usage at probe.

Dependencies/integration: depends on parent system clocks such as `sd-133m`, `sd-200m`, and `usb2`; integrated through `clk-uniphier-core.c`.

Risks: SD mux masks/values are nonuniform across parent groups and must match hardware. Channel register offsets scale by `0x200`, so wrong channel numbers affect unrelated registers.

Test signals: SD rate switching for each channel, gate enable bits at `0x20 + 0x200 * ch`, USB2/PHY gate toggles, and compatible mapping to the right data array.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-mio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-mux.c -->
# sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-mux.c

Purpose: UniPhier regmap-backed mux clock implementation using per-parent masks and values.

Important APIs/types/functions: `uniphier_clk_register_mux()`, `uniphier_clk_mux_set_parent()`, `uniphier_clk_mux_get_parent()`, and `uniphier_clk_mux_ops`. State is `struct uniphier_clk_mux`.

Control flow: registration stores parent names, register offset, mask array, and value array, then registers a `CLK_SET_RATE_PARENT` mux. Set-parent writes the selected parent's value under its mask. Get-parent reads the register and returns the first parent whose masked value matches.

State and persistence: hardware selector fields persist in syscon registers. Driver state references static mask/value arrays embedded in clock data.

Dependencies/integration: used by SD and SoC-glue clock data; depends on regmap and CCF mux determine-rate.

Risks: overlapping masks or values can make `get_parent()` return the first matching parent, so table order matters. Set-parent trusts index bounds from CCF. Regmap read errors are returned through a `u8` callback, which can truncate negative errors.

Test signals: parent switching for SD and SATA reference muxes, readback matching after writes, and validation of overlapping mask/value tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-peri.c -->
# sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-peri.c

Purpose: UniPhier peripheral clock data for UART, I2C/FI2C, SCSSI, and MCSSI gates.

Important APIs/types/functions: exports `uniphier_ld4_peri_clk_data[]` and `uniphier_pro4_peri_clk_data[]`. Macros define gate entries for UART channels, common/individual I2C, fast I2C, SCSSI, and MCSSI.

Control flow: core selects the array by peripheral compatible. LD4-style data gates UART0-3, an internal `i2c-common` gate, I2C0-4 derived from it, and SCSSI0. Pro4-style data gates UART0-3, FI2C0-6, SCSSI0-3, and MCSSI.

State and persistence: static table only. Runtime state is generated gate clocks and syscon register bits at `0x20`/`0x24`.

Dependencies/integration: parent clocks are expected from system clock data (`uart`, `i2c`, `spi`). Gate helper writes the described syscon bits.

Risks: index assignments are ABI-visible to DT consumers. Shared parent/common gates mean disabling a common parent can affect multiple children if consumer usage is wrong.

Test signals: peripheral driver clock gets by index/name, gate bit toggles for UART/I2C/SPI channels, and correct parent rate inheritance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-peri.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-sys.c -->
# sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-sys.c

Purpose: UniPhier system and SoC-glue clock data. It describes PLL-derived fixed factors, gates for NAND/eMMC/Ethernet/USB/SATA/PCIe/AIO/EVEA/EXIV/VOC/HDMI, SD parent rates, CPU gear parents, and a SATA reference mux.

Important APIs/types/functions: exports `uniphier_ld4_sys_clk_data[]`, `uniphier_pro4_sys_clk_data[]`, `uniphier_sld8_sys_clk_data[]`, `uniphier_pro5_sys_clk_data[]`, `uniphier_pxs2_sys_clk_data[]`, `uniphier_ld11_sys_clk_data[]`, `uniphier_ld20_sys_clk_data[]`, `uniphier_pxs3_sys_clk_data[]`, `uniphier_nx1_sys_clk_data[]`, and `uniphier_pro4_sg_clk_data[]`. It uses table macros from `clk-uniphier.h`.

Control flow: the core driver registers the selected array in order. Internal PLL/factor clocks form parents for indexed output gates and muxes. Later SoCs add CPU gear clocks backed by `UNIPHIER_CLK_CPUGEAR()` and intermediate divider parents. The SoC-glue array creates a `gpll/4` factor and a `sata-ref` mux.

State and persistence: no code state; data controls generated fixed-factor, gate, mux, and CPU gear clock state. Syscon register offsets such as `0x2104`, `0x2108`, `0x210c`, `0x2110`, and `0x2260` are the persistent hardware interface.

Dependencies/integration: selected by system and SoC-glue compatible strings in `clk-uniphier-core.c`. Depends on external root `ref` clock and parent names created earlier in the same array.

Risks: table order and parent names matter because internal parents are referenced by string. Comments document hardware quirks such as always-enabled GIO and USB link OR logic; changing those gates could break hardware. ABI indices must remain stable.

Test signals: boot every listed UniPhier SoC compatible, inspect clock summary for expected PLL rates, enable each indexed gate, switch CPU gears where present, validate SD/NAND/eMMC rates, and test SATA reference mux on Pro4 SG.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-sys.c -->
