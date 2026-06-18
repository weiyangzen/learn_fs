# subset-b-001183 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-sdmmc-mux.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-sdmmc-mux.c

Purpose: implements the Tegra SDMMC mux/divider composite used by newer Tegra SD/MMC clocks that have two different hardware parent selector encodings depending on whether the fractional divider is zero. It wraps parent muxing, an 8-bit fractional divider, and a Tegra peripheral gate into one Common Clock Framework clock.

Important APIs, types, and functions: `tegra_clk_register_sdmmc_mux_div()` is the exported constructor declared in `clk.h` and used by Tegra210 for SDMMC instances. The implementation stores state in `struct tegra_sdmmc_mux`: `reg`, optional `lock`, `div_flags`, embedded `tegra_clk_periph_gate`, and delegated `gate_ops`. Core callbacks are `clk_sdmmc_mux_get_parent()`, `set_parent()`, `determine_rate()`, `recalc_rate()`, `set_rate()`, gate passthrough callbacks, and `restore_context()`.

Control flow: parent lookup reads `reg`, extracts bits 31:29, and maps the raw selector through `mux_lj_idx` when divider bits are zero or `mux_non_lj_idx` when nonzero. Rate calculation uses `rate = parent_rate * 2 / (div + 2)` with rounding behavior selected by `TEGRA_DIVIDER_ROUND_UP`. `set_rate()` computes the fractional divider with `div_frac_get()`, locks if provided, translates the current logical parent to the matching raw low-jitter or non-low-jitter selector, writes selector plus divider as one register value, and fences with `fence_udelay(2, reg)`. Gate operations call the normal Tegra peripheral gate ops after binding the embedded gate hw to the composite clock.

State and persistence: persistent state is hardware register contents plus the global `periph_clk_enb_refcnt` array. The C object is allocated for the lifetime of the clock and freed only on registration failure. Suspend/resume context is restored by replaying parent and rate from CCF state, which is important because raw parent encoding changes with divider mode.

Dependencies and integration: depends on `clk.h` helpers, `get_reg_bank()`, `tegra_clk_periph_gate_ops`, `periph_clk_enb_refcnt`, and `div_frac_get()`. The fixed parent list is `"pll_p", "pll_c4_out2", "pll_c4_out0", "pll_c4_out1", "clk_m"` and must match hardware selector tables.

Risks and test signals: risks are off-by-one selector table errors, changing divider without translating selector encoding, missing locking with shared CAR registers, and invalid `clk_num` bank lookup. Test by switching all parents with divider zero and nonzero, verifying SDMMC rates against register values, checking gate enable/disable/reset behavior, and running suspend/resume while an SDMMC clock uses both low-jitter and divided modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-sdmmc-mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-super.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-super.c

Purpose: provides generic Tegra "super clock" muxes used for CPU and system clock burst-policy registers. A super clock has state-specific parent selector fields for idle/run/IRQ/FIQ states and, in the full composite form, a fractional divider in the adjacent register.

Important APIs, types, and functions: exported `tegra_clk_super_ops`, `tegra_clk_register_super_mux()`, and `tegra_clk_register_super_clk()` are the integration surface. The main data carrier is `struct tegra_clk_super_mux` with register address, selector width, lock, PLLX/div2 indexes, embedded `tegra_clk_frac_div`, and optional flags such as `TEGRA_DIVIDER_2` and `TEGRA210_CPU_CLK`. Key callbacks are `clk_super_get_parent()`, `clk_super_set_parent()`, `clk_super_restore_context()`, and the composite divider wrappers.

Control flow: parent get/set reads the burst-policy register, requires hardware state to be RUN or IDLE, chooses the field offset for that state, and masks by configured selector width. For low-power CPU clocks with `TEGRA_DIVIDER_2`, PLLX and PLLX/2 are represented as separate logical parents even though hardware uses a bypass bit plus PLLX selector. `set_parent()` refuses direct PLLX-to-PLLX/2 changes, toggles `SUPER_LP_DIV2_BYPASS` only from another parent, and delays for hardware settling. Tegra210 CPU clocks enable PLLP CPU branches before selecting PLLP out0/out4 and disable those branches after moving away.

State and persistence: persistent state is in the CAR burst-policy register and optional divider register at `reg + 4`. The restore path replays divider state first for full super clocks and then restores the selected parent. Registration allocates a permanent `tegra_clk_super_mux` and uses `clk_register()` or `tegra_clk_dev_register()`.

Dependencies and integration: uses CCF mux/divider callbacks, Tegra fractional divider ops, Tegra CPU PLLP branch control, and `clk.h` flag definitions. Gen4/gen5 SoC code registers `sclk`, `cclk_g`, and `cclk_lp` through these APIs; CPU-specific wrappers in `clk-tegra-super-cclk.c` reuse `tegra_clk_super_ops`.

Risks and test signals: important risks are `BUG_ON()` if used while hardware reports IRQ/FIQ state, unsafe LP PLLX/div2 transitions, stale PLLP CPU branch gates, and wrong selector width or parent ordering. Test parent transitions in RUN and IDLE, LP PLLX/div2 negative paths, suspend/resume restore, and Tegra210 CPU parent moves to and from PLLP outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-audio.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-audio.c

Purpose: registers shared Tegra audio clocks: audio PLLs supplied by SoC data, `pll_a_out0`, sync-source clocks for I2S/SPDIF/VIMCLK, per-audio mux/gate pairs, DMIC sync clocks, and 2x audio doubler/divider/gate chains.

Important APIs, types, and functions: `tegra_audio_clk_init()` is the public init hook. `tegra_audio_sync_clk_init()` registers mux and gate pairs for both audio and DMIC sync clocks. Local init-data types describe sync sources, audio mux/gates, and audio2x chains. Parent arrays are `mux_audio_sync_clk` and `mux_dmic_sync_clk`.

Control flow: initialization validates `audio_info` and `num_plls`, registers each supplied PLL through `tegra_clk_register_pll()`, constructs `pll_a_out0_div` and `pll_a_out0`, registers fixed-rate sync source clocks with the supplied maximum rate, then registers audio mux/gate pairs. Before DMIC mux registration it writes selector value `1` to each DMIC sync register so the DMIC clocks do not default to the invalid `"unused"` parent. Audio 2x clocks are a fixed factor doubler, a one-bit divider in `AUDIO_SYNC_DOUBLER`, and a Tegra peripheral gate.

State and persistence: persistent hardware state includes mux selector and gate bits in the audio sync registers, the PLLA_OUT divider/output bits, and doubler divider bits. `clk_doubler_lock` serializes doubler register updates. There is no local suspend callback; it relies on CCF/underlying clock restore behavior.

Dependencies and integration: called from Tegra30/114/124/210 SoC clock init after PLL and peripheral infrastructure exists. It uses `tegra_lookup_dt_id()` to skip clocks not present in a given SoC clock table and stores successful clocks in the `tegra_clks` lookup array. It depends on `tegra_clk_register_sync_source()`, `tegra_clk_register_pll_out()`, `tegra_clk_register_divider()`, and `tegra_clk_register_periph_gate()`.

Risks and test signals: risks include missing `audio_info`, wrong mux parent ordering, invalid DMIC default parent, and unhandled registration errors because many return values are assigned without `IS_ERR()` checks. Test by booting audio-capable SoCs, checking DT clock IDs, verifying I2S/SPDIF parent selection and 2x rate propagation, confirming DMIC muxes start on valid parents, and exercising suspend/resume with audio clocks active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-fixed.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-fixed.c

Purpose: initializes fixed root clocks common to Tegra SoCs: oscillator-derived roots (`osc`, `osc_div2`, `osc_div4`, `clk_m`, `pll_ref`) and the always-32768 Hz `clk_32k`. It also snapshots oscillator control bits for resume.

Important APIs, types, and functions: `tegra_osc_clk_init()` reads `OSC_CTRL`, maps the hardware oscillator index to a supplied frequency table, registers fixed-rate/fixed-factor roots into the SoC `struct tegra_clk` table, and optionally returns oscillator and PLL reference rates. `tegra_fixed_clk_init()` registers `clk_32k`. `tegra_clk_osc_resume()` restores saved oscillator control fields.

Control flow: `tegra_osc_clk_init()` saves `OSC_CTRL_MASK` bits in `osc_ctrl_ctx`, extracts `OSC_FREQ`, validates the index against `input_freqs`, registers `osc`, optional divided oscillator clocks, `clk_m` using the caller-provided divider, and `pll_ref` using `OSC_CTRL_PLL_REF_DIV_SHIFT`. Early returns are used when a clock ID is absent from the SoC table.

State and persistence: `osc_ctrl_ctx` is module-global saved state used by resume. Hardware state lives in `OSC_CTRL`; restored fields include oscillator frequency selection and PLL reference divider bits while preserving unrelated register bits. Registered fixed clocks are static roots with no rate changes.

Dependencies and integration: SoC init files call this before PLL registration so PLLs can parent to `pll_ref` and peripheral clocks can parent to `clk_m`. It relies on `tegra_lookup_dt_id()` and standard CCF fixed-rate/fixed-factor constructors.

Risks and test signals: risks are wrong oscillator frequency table indexing, returning success when a required root ID is absent, and restoring stale oscillator bits across suspend if firmware changed them. Test with each supported oscillator strap, verify `osc_freq` and `pll_ref_freq`, inspect `/sys/kernel/debug/clk/clk_summary`, and suspend/resume while checking PLL lock behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-fixed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-periph.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-periph.c

Purpose: centralizes Tegra peripheral clock registration data shared across multiple SoCs. It defines mux parent tables, per-peripheral composite init rows, simple gate rows, PLLP and PLLP-out branches, and the exported `tegra_periph_clk_init()` that SoC files call after root PLLs exist.

Important APIs, types, and functions: the public API is `tegra_periph_clk_init()`. Internal helpers are `init_pllp()`, `periph_clk_init()`, `gate_clk_init()`, and `div_clk_init()`. Tables include `periph_clks[]`, `gate_clks[]`, `div_clks[]`, and `pllp_out_clks[]`. Macros such as `MUX`, `MUX8`, `INT`, `UART`, `I2C`, `XUSB`, `AUDIO`, `NODIV`, `GATE`, and `DIV8` produce `struct tegra_periph_init_data` using `TEGRA_INIT_DATA_TABLE()`.

Control flow: `tegra_periph_clk_init()` registers PLLP and PLLP outputs first, then iterates data tables. For each composite peripheral clock it checks the DT clock ID, finds the proper enable/reset bank with `get_reg_bank()`, installs the bank into the embedded gate, and calls `tegra_clk_register_periph_data()`. Gate-only and divider-only rows use specialized Tegra gate and divider constructors. `init_pllp()` registers `pll_p`, divider plus `pll_out` pairs, Tegra210's `pll_p_out_cpu`-based CPU branch topology, and HSIO/XUSB gates.

State and persistence: most state is encoded in static init data and hardware CAR source, enable, and reset registers. Gate refcounts use the global `periph_clk_enb_refcnt`. Spinlocks protect shared PLLP_OUT registers. The function writes no long-lived software state beyond registered CCF clock objects.

Dependencies and integration: called by Tegra20/30/114/124/210 SoC init paths with a SoC clock presence table and PLLP params. It integrates with `clk-periph.c`, `clk-periph-gate.c`, `clk-divider`, `clk-pll`, `clk-id.h`, and DT clock IDs. The mux tables encode SoC-specific parent selector holes, so table order and `_idx` maps are part of the ABI.

Risks and test signals: risks include duplicate or wrong clock IDs, wrong parent selector maps, gate flags such as `TEGRA_PERIPH_ON_APB` or `TEGRA_PERIPH_NO_RESET` on the wrong device, and the apparent `iqc2` row using `tegra_clk_iqc1`. Test by validating all present DT IDs resolve, checking parent/rate/gate operations for representative UART/I2C/SDMMC/XUSB/audio/display clocks, inspecting reset behavior, and booting SoCs that select different variants of the same clock name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-periph.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-super-cclk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-super-cclk.c

Purpose: implements CPU CCLK-specific behavior on top of generic Tegra super clocks. It chooses PLLP for low CPU rates, PLLX for high rates, accounts for thermal div2 slowdown, disables unused clock-skipper hardware, and provides pre/post hooks for PLLX rate changes.

Important APIs, types, and functions: exported `tegra_clk_register_super_cclk()`, `tegra_cclk_pre_pllx_rate_change()`, and `tegra_cclk_post_pllx_rate_change()` are the integration surface. Static state is `cclk_super` and `cclk_on_pllx`. CCF ops are `tegra_cclk_super_ops` for Tegra30+ style composite clocks and `tegra_cclk_super_mux_ops` for Tegra20-style mux-only clocks.

Control flow: registration allocates a `tegra_clk_super_mux`, selects ops based on `TEGRA20_SUPER_CLK`, initializes the optional fractional divider at `reg + 4`, clears `SUPER_CDIV_ENB` to disable the clock skipper, registers the clock, and records the singleton pointer. `determine_rate()` compares requested CPU rate with PLLP rate: requests at or below PLLP use PLLP, while higher requests round PLLX and select it. `recalc_rate()` halves the result when the thermal `TSENSOR_SLOWDOWN` bit is active, and bypasses divider math when parent is direct PLLX.

State and persistence: the singleton keeps the registered CPU clock state and whether it was on PLLX during a PLLX rate-change transaction. Hardware state is in CCLK burst/divider registers. Pre-change reparenting temporarily moves CPU to PLLP before PLLX is altered; post-change restores PLLX only if it was previously selected.

Dependencies and integration: relies on `tegra_clk_super_ops`, parent index constants `PLLP_INDEX` and `PLLX_INDEX`, and PLL code calling the pre/post hooks around PLLX rate changes. Tegra20/30 SoC files register CPU super clocks through this API.

Risks and test signals: risks are singleton misuse, missing pre/post PLLX notifications, incorrect parent indexes for a SoC parent array, and rate calculations that hide thermal throttling. Test CPUfreq transitions below and above PLLP, PLLX rate changes while CPU is and is not parented to PLLX, thermal slowdown reporting, and registration rejection on a second CCLK.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-super-cclk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-super-gen4.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-super-gen4.c

Purpose: registers generation 4 and 5 Tegra super-clock trees: system clock (`sclk`), AHB/APB dividers and gates (`hclk`, `pclk`), CPU cluster super muxes (`cclk_g`, `cclk_lp`), PLLX, and `pll_x_out0`.

Important APIs, types, and functions: exported `tegra_super_clk_gen4_init()` and `tegra_super_clk_gen5_init()` call `tegra_super_clk_init()` with `tegra_super_gen_info` describing parent arrays and counts. Internal helpers are `tegra_sclk_init()` and `tegra_super_clk_init()`. Parent arrays differ between gen4 and gen5, especially use of PLLC4 and DFLL CPU output.

Control flow: `tegra_super_clk_init()` optionally registers `cclk_g` and `cclk_lp` with `tegra_clk_register_super_mux()`, using Tegra210-specific CPU branch handling for gen5 `cclk_g` and LP div2 semantics for gen4 `cclk_lp`. It then registers SCLK: either as `sclk_mux` plus divider `sclk`, or as a mux-only critical `sclk` when no separate mux ID exists. HCLK and PCLK are dividers plus gates in `SYSTEM_CLK_RATE`, protected by `sysrate_lock`. When enabled by build config, it registers PLLX and fixed-factor `pll_x_out0`.

State and persistence: state lives in CAR burst-policy, system-rate, and PLLX registers. `sclk`, `hclk`, and `pclk` are marked critical where required to avoid disabling system buses. There is no local suspend storage; registered super-clock/divider ops handle restore where supported.

Dependencies and integration: used by Tegra20/30/114/124/210 SoC init after oscillator and PLLP infrastructure are present. It relies on clock table presence checks to decide which variants to register and on `CONFIG_ARCH_TEGRA_*` to compile PLLX registration paths.

Risks and test signals: risks include parent array/index mismatches, missing critical flags on bus clocks, gen5 CPU PLLP branch handling only being attached to `cclk_g`, and build-config-specific PLLX registration differences. Test `sclk`/`hclk`/`pclk` rates, CPU parent switches, debug clock summaries for gen4 and gen5 SoCs, and suspend/resume of bus clock hierarchy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra-super-gen4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra114.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra114.c

Purpose: top-level CAR clock driver for Tegra114. It maps CAR/PMC registers, declares PLL parameter tables, maps Tegra internal clock IDs to DT IDs, registers fixed/root/PLL/peripheral/audio/super clocks, initializes clock defaults, and exposes DFLL DVCO reset plus CPU clock trim controls.

Important APIs, types, and functions: entry point is `tegra114_clock_init()` through `CLK_OF_DECLARE("nvidia,tegra114-car")`. Major helpers are `tegra114_pll_init()`, `tegra114_periph_clk_init()`, `tegra114_clock_apply_init_table()`, CPU CAR ops, DFLL reset assert/deassert, and exported `tegra114_clock_tune_cpu_trimmers_*()` functions. Static data includes PLL params for PLLC/C2/C3/M/P/A/D/D2/U/X/E/RE, `tegra114_clks[]`, `devclks[]`, and `init_table[]`.

Control flow: init maps CAR and PMC, allocates the Tegra clock table for five peripheral banks, initializes oscillator roots and `clk_32k`, registers PLLs and derived outputs, installs Tegra114-specific peripherals such as DSI muxes/gates, EMC mux/MC, MIPI-CAL, and VI sensor, then calls shared peripheral/audio/super-clock init. It registers one special reset for `TEGRA114_RST_DFLL_DVCO`, publishes the OF clock provider, registers legacy clkdev aliases, stores the init-table callback, and installs CPU CAR ops.

State and persistence: global `clk_base`, `pmc_base`, `clks`, `osc_freq`, and `pll_ref_freq` hold runtime clock-controller state. CPU suspend context saves CSITE and CCLKG burst/divider registers and restores them on resume. CPU trimmer functions program finetrim registers and fence through a CAR readback. Hardware PLL state is mostly owned by shared PLL implementations using the static params here.

Dependencies and integration: depends on Tegra DT bindings, `clk.h`, shared fixed/peripheral/audio/super-clock files, PMC node `"nvidia,tegra114-pmc"`, and reset framework hooks from Tegra clock code. DFLL reset is used by the DFLL driver; CPU trimmer symbols are exported for voltage/CPU frequency code.

Risks and test signals: risks are PLL table/reg offset errors, unchecked registration failures, missing PMC mapping, incorrect initial enable bits for DFLL ref/soc needed by I2C5, and CPU trim assumptions noted in comments. Test full boot clock summary, init-table rates, DSI/EMC/MC clocks, DFLL reset control, CPU suspend/resume, and audio/XUSB defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra114.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra124-dfll-fcpu.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra124-dfll-fcpu.c

Purpose: platform driver that supplies CPU DFLL operating-point data for Tegra114, Tegra124, and Tegra210. It turns fuse speedo/process information plus CVB voltage tables into CPU OPPs and registers the generic Tegra DFLL clock driver.

Important APIs, types, and functions: `struct dfll_fcpu_data` groups max-frequency and CVB table arrays per SoC. `tegra124_dfll_fcpu_probe()` is the core runtime path; `tegra124_dfll_fcpu_remove()` tears down DFLL and OPP state. Matching is through `"nvidia,tegra114-dfll"`, `"nvidia,tegra124-dfll"`, and `"nvidia,tegra210-dfll"`. Helpers `get_alignment_from_dt()` and `get_alignment_from_regulator()` define voltage rail alignment.

Control flow: probe gets SoC-specific data from the OF match, reads `tegra_sku_info` CPU process/speedo IDs and speedo value, bounds-checks the max-frequency table, allocates `tegra_dfll_soc_data`, binds it to CPU0's device, obtains rail alignment either from PWM DT properties or the `vdd-cpu` regulator, chooses `max_freq`, builds an OPP table with `tegra_cvb_add_opp_table()`, and calls `tegra_dfll_register()`. On DFLL registration failure it removes the OPP table. Remove unregisters DFLL first and then removes OPPs.

State and persistence: persistent runtime state is devm-allocated `tegra_dfll_soc_data`, the selected CVB table pointer, CPU OPP table entries, rail alignment, and DFLL driver state. Tables are static and encode fuse-dependent voltage/frequency policy. Runtime/system PM delegates to generic DFLL suspend/resume callbacks.

Dependencies and integration: depends on fuse data (`soc/tegra/fuse.h`), regulator APIs, CPU device discovery, CVB helpers, and `clk-dfll.c`. The SoC CAR drivers provide DFLL reset and reference clocks; DT properties decide PWM-to-PMIC alignment handling.

Risks and test signals: risks include unsupported speedo IDs causing probe failure, missing CPU0 device, regulator providers not ready, mismatched rail alignment creating unsafe voltages, and stale CVB table limits. Test probe on representative speedo/process bins, validate generated OPP voltages, exercise regulator and PWM paths, CPUfreq transitions through DFLL, runtime PM, system suspend/resume, and remove/error unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra124-dfll-fcpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra124-emc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra124-emc.c

Purpose: Common Clock Framework clock for Tegra124 external memory controller frequency switching. It loads EMC timing tables from DT, coordinates timing transitions with the external EMC driver, and programs the CAR EMC source/divider register safely.

Important APIs, types, and functions: exported `tegra124_clk_register_emc()`, `tegra124_clk_set_emc_callbacks()`, and `tegra124_clk_emc_driver_available()` are the integration surface. Internal types are `struct emc_timing` and `struct tegra_clk_emc`. CCF callbacks are `emc_recalc_rate()`, `emc_determine_rate()`, `emc_get_parent()`, and `emc_set_rate()`.

Control flow: registration scans CAR DT child nodes with `nvidia,ram-code`, loads timing children via `load_timings_from_dt()`, sorts each RAM-code group by rate, stores a phandle to `nvidia,external-memory-controller`, registers critical clock `"emc"`, records the current parent, and registers a debug clkdev alias. Rate determination selects the lowest timing for the current RAM code that satisfies the request, preferring upward rounding unless constrained by max rate. `emc_set_rate()` finds an exact timing; if the new timing uses the same underlying clock source but requires a different parent rate, it first switches to a backup timing with a different source. `emc_set_timing()` gets the external EMC driver and callbacks, sets/enables the parent, calls prepare, writes mux/divider under lock, calls complete, reparents CCF state, disables the old parent, and updates `prev_parent`.

State and persistence: state includes DT-loaded timing table, `prev_parent`, `changing_timing` recursion guard, callback pointers, retained EMC device node until first use, and cached external `tegra_emc`. Hardware state is `CLK_SOURCE_EMC`. The clock is critical because disabling memory clocking would break the system.

Dependencies and integration: called by Tegra124/132 CAR init; the custom OF clock provider defers consumers until `tegra124_clk_emc_driver_available()` is true. Depends on `tegra_read_ram_code()`, DT timing schema, external EMC driver callbacks, CCF parent/rate APIs, and CAR lock.

Risks and test signals: risks are missing or malformed DT timings, no backup timing for same-source parent-rate changes, callbacks not registered, parent rate mismatch, leaked parent clk refs on partial failures, and integer divider truncation. Test every RAM-code timing, exact and rounded rate requests, callback defer behavior, backup timing path, suspend/resume memory stability, and clock summary parent/rate after transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra124-emc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra124.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra124.c

Purpose: top-level CAR clock driver for Tegra124 and Tegra132. It shares most registration for both SoCs, declares PLL/root/peripheral data, registers Tegra124-specific EMC clocking, exposes DFLL DVCO reset, and handles Tegra132 differences where CPU clocks live outside CAR.

Important APIs, types, and functions: `tegra124_clock_init()` and `tegra132_clock_init()` are declared with `CLK_OF_DECLARE`. Shared phases are `tegra124_132_clock_init_pre()` and `_post()`. Major helpers are `tegra124_pll_init()`, `tegra124_periph_clk_init()`, `tegra124_clock_apply_init_table()`, `tegra132_clock_apply_init_table()`, `tegra124_clk_src_onecell_get()`, CPU CAR ops, and DFLL reset assert/deassert. Static data includes PLL params for PLLX/C/C2/C3/C4/M/E/RE/P/A/D/D2/DP/U, `tegra124_clks[]`, `devclks[]`, SOR parent data, and init tables.

Control flow: pre-init maps CAR/PMC, allocates a six-bank clock table, initializes oscillator and fixed roots, registers all PLLs and derived outputs, registers custom peripherals such as xusb_ss_div2, DPAUX, DSI gates, MC, CML0/1, SOR0, and shared peripherals/audio. It forces PLLD as the DSI source for Tegra124/132. Post-init registers gen4 super clocks, special DFLL reset, a custom OF provider, the EMC clock, clkdev aliases, and CPU CAR ops. Tegra124 sets the full init table; Tegra132 marks CAR CPU/PLLX clocks absent before post-init and uses a smaller init table.

State and persistence: global mapped bases and `clks` hold runtime controller state. CPU suspend context saves/restores CSITE and CCLKG burst/divider registers. The custom onecell provider returns `-EPROBE_DEFER` for EMC until the EMC timing callbacks are present. Hardware PLL and peripheral state is programmed through shared clock implementations.

Dependencies and integration: depends on Tegra124 DT clock/reset bindings, PMC node, shared fixed/peripheral/audio/super-clock files, `tegra124_clk_register_emc()`, and reset framework glue. Consumer-visible DT IDs are selected by `tegra124_clks[]`; legacy clkdev aliases support non-DT users and debug tooling.

Risks and test signals: risks include unchecked registration errors, Tegra132 mutation of the shared `tegra124_clks[]` table after pre-init, PLLSS parameter mistakes for display/storage PLLs, EMC provider ordering, and init-table differences between Tegra124 and Tegra132. Test both compatibles, EMC probe deferral, reset ID behavior, CPU suspend/resume, SOR/DSI/display clocks, XUSB/SATA defaults, and complete clock summary against DT IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra124.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra20-emc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra20-emc.c

Purpose: CCF implementation of the Tegra20/Tegra30-style EMC clock. It provides parent selection, fractional divider programming, low-jitter PLLM_UD selection, MC/EMC same-frequency preparation, and a callback-based rate rounding hook supplied by the external EMC driver.

Important APIs, types, and functions: exported `tegra20_clk_register_emc()`, `tegra20_clk_set_emc_round_callback()`, `tegra20_clk_emc_driver_available()`, and `tegra20_clk_prepare_emc_mc_same_freq()` are the integration points. State is held in local `struct tegra_clk_emc` with `reg`, `mc_same_freq`, `want_low_jitter`, `round_cb`, and `cb_arg`. CCF ops are `emc_recalc_rate()`, `emc_get_parent()`, `emc_set_parent()`, `emc_set_rate()`, `emc_set_rate_and_parent()`, and `emc_determine_rate()`.

Control flow: registration creates a critical `"emc"` clock with parents `"pll_m", "pll_c", "pll_p", "clk_m"`. Recalc and set-rate use Tegra fractional divider math where EMC rate is `parent * 2 / (div + 2)`. Parent/rate writes update source and divider fields, set `USE_PLLM_UD` only for PLLM with divider zero when low jitter is requested, set or clear `MC_EMC_SAME_FREQ`, write the register, and fence for one microsecond. Rate determination first asks `round_cb` to choose a supported EMC rate, then searches parents for an exact representable divider and fills `best_parent_*`.

State and persistence: persistent state is the CAR EMC source register plus software booleans for desired low-jitter and MC same-frequency modes. The callback is installed later by the EMC driver through a global clock lookup. The clock is critical to prevent accidental memory-clock disable.

Dependencies and integration: Tegra20 registers this with `low_jitter=false`; Tegra30 uses `low_jitter=true`. External EMC drivers install the rounding callback and may call same-frequency preparation before clock changes. Depends on `div_frac_get()`, `fence_udelay()`, and public callback typedefs in `include/linux/clk/tegra.h`.

Risks and test signals: risks include `determine_rate()` dereferencing a missing `round_cb` if consumers request rates before the EMC driver registers, no locking around register writes, exact-divider search failure for valid board timings, and stale `mc_same_freq` state. Test callback availability deferral in SoC users, parent/divider combinations, PLLM low-jitter bit behavior, MC same-frequency toggling, and memory stability across rate changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-tegra20-emc.c -->
