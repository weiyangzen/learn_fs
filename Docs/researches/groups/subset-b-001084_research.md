# Research: subset-b-001084 AT91 PMC clock drivers

Grouped source-tree-aligned research for `sources/distributed-fs/ceph-client/drivers/clk/at91/*` clock setup and provider files. Each section is intentionally self-contained so the reconciliation lane can split it into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/at91sam9g45.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/at91sam9g45.c

Purpose: early common-clock setup for the AT91SAM9G45 PMC, selected by `CLK_OF_DECLARE(..., "atmel,at91sam9g45-pmc", ...)`. It builds the SoC clock tree and publishes it through `of_clk_add_hw_provider(np, of_clk_hw_pmc_get, at91sam9g45_pmc)`.

Important APIs and data: `at91sam9g45_pmc_setup()` is the only entry point. Static tables describe master-clock limits/divisors, PLLA output windows plus `out`/`icpll` programming, system clocks such as critical `ddrck`, and peripheral IDs. It uses provider helpers from `pmc.h`: main oscillator, RM9200 main clock, legacy PLL, PLLA divider, UTMI, master pres/div, USB, programmable, system, and basic peripheral clocks.

Control flow: it resolves `slow_clk` and `main_xtal`, maps the PMC regmap, allocates `pmc_data`, honors `atmel,osc-bypass`, registers the core clocks in dependency order, fills `chws`, `pchws`, `shws`, and `phws`, then registers the provider. Any registration failure jumps to `err_free`.

State and persistence: persistent state is the allocated `pmc_data` arrays and registered `clk_hw` objects. Runtime hardware state is owned by helper providers through PMC registers. `ddrck` is marked `CLK_IS_CRITICAL` because DDR is bootloader-enabled and must not be disabled by unused-clock cleanup.

Dependencies and integration: depends on DT `clock-names`, `dt-bindings/clock/at91.h`, syscon/regmap, and AT91 common-clock helpers. The TCB clocksource note explains why this is an early OF declaration rather than a platform driver.

Risks: missing parent names silently abort setup; failed mid-tree registration leaks already registered clocks because only `pmc_data` is freed; incorrect PLL ranges or peripheral IDs can over/under-clock hardware. Test signals include boot logs for invalid `clk_get`, `/sys/kernel/debug/clk/clk_summary`, USB/UTMI enumeration, DDR stability, and timer availability during early boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/at91sam9g45.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/at91sam9n12.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/at91sam9n12.c

Purpose: AT91SAM9N12 PMC clock-tree setup for `"atmel,at91sam9n12-pmc"`. It models a main RC/main crystal mux, PLLA, PLLB-backed USB, master clock, programmable clocks, system clocks, and PCR-based peripherals.

Important APIs and data: `at91sam9n12_pmc_setup()` is the setup entry. It defines master characteristics with `have_div3_pres`, PLLA high-frequency ranges, PLLB 30-100 MHz output, `at91sam9n12_pcr_layout`, system clocks including critical `ddrck`, and the peripheral ID/name table.

Control flow: the function resolves `slow_clk` and `main_xtal`, maps the PMC, allocates arrays sized by `PMC_PLLBCK + 1`, system count, 31 peripherals, and two PCKs. It registers `main_rc_osc`, optional-bypass `main_osc`, SAM9x5-style `mainck`, PLLA plus `plladivck`, PLLB, master pres/div, SAM9N12 USB from `pllbck`, two programmable clocks, system clocks, and PCR peripherals.

State and persistence: `pmc_data` stores exported core, system, peripheral, and programmable handles. The PCR peripheral provider persists per-clock divider/status state and writes PCR on enable/restore. `ddrck` is critical to preserve bootloader DDR enablement.

Dependencies and integration: shares the global `pmc_pcr_lock`; uses `at91sam9x5_master_layout`, legacy PLL registration, SAM9N12 USB ops, and OF provider lookup through `of_clk_hw_pmc_get`.

Risks: the setup assumes PLLB can satisfy USB consumers; missing `clock-names` aborts without diagnostics; no cleanup unregisters earlier clocks after later failure. Test signals include USB clock rate, master clock under `/sys/kernel/debug/clk/clk_summary`, peripheral gates toggling through drivers, and DDR continuing through unused-clock disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/at91sam9n12.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/at91sam9rl.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/at91sam9rl.c

Purpose: early PMC setup for AT91SAM9RL via `"atmel,at91sam9rl-pmc"`. It is a smaller legacy tree with main clock, PLLA, UTMI, master clock, two programmable clocks, two system PCKs, and basic peripheral gates.

Important APIs and data: `at91sam9rl_pmc_setup()` consumes static `sam9rl_mck_characteristics`, two PLLA output bands, `at91sam9rl_systemck`, and `at91sam9rl_periphck`. It registers clocks through the common helpers declared in `pmc.h`.

Control flow: setup fetches `slow_clk` and `main_xtal`, maps the PMC regmap, allocates `pmc_data`, registers an RM9200-style `mainck` directly from the crystal parent, PLLA, UTMI, master pres/div using `at91rm9200_master_layout`, two programmable clocks, system PCK gates, peripheral gates, and the OF provider.

State and persistence: persistent kernel state is only the clock graph and `pmc_data`. Hardware persistence and suspend context are handled by provider ops such as master, PLL, UTMI, programmable, and system where available. There is no local backup state in this file.

Dependencies and integration: depends on legacy AT91 PMC register layout, `at91rm9200_programmable_layout`, `at91_clk_register_peripheral()`, and the global clock provider contract using two phandle arguments.

Risks: PLLA range selection is narrow and table-driven; wrong DT parents can yield impossible master/UTMI rates. Registration failure frees only `pmc_data`. Test signals: PCK0/PCK1 readiness, USB/UTMI lock, peripheral driver clock enables, and clocksource operation if timer peripherals depend on the registered gates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/at91sam9rl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/at91sam9x5.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/at91sam9x5.c

Purpose: shared PMC setup for the AT91SAM9x5 family variants (`9g15`, `9g25`, `9g35`, `9x25`, `9x35`). Variant-specific `CLK_OF_DECLARE` wrappers pass extra peripheral tables and LCD clock presence into `at91sam9x5_pmc_setup()`.

Important APIs and data: common tables describe master limits with div3 prescaler, PLLA ranges, the PCR layout, shared system clocks, shared peripherals, and per-variant extras such as MACB, LCDC, CAN, ISI, and USART3. `at91sam9x5_pmc_setup()` is the central builder.

Control flow: setup resolves slow/main parents, maps the PMC, allocates `pmc_data`, registers `main_rc_osc`, bypassable `main_osc`, SAM9x5 `mainck`, PLLA, `plladivck`, UTMI, master pres/div, USB, SMD clock, two programmable clocks, system clocks, optional `lcdck`, shared PCR peripherals, extra variant peripherals, and the OF provider.

State and persistence: `pmc_data` exports core/system/peripheral/PCK handles. Critical `ddrck` keeps DDR enabled. Peripheral dividers are PCR-backed and can auto-divide according to declared range. No variant state is stored after setup beyond registered clocks.

Dependencies and integration: integrates SMD and USB helper providers and uses `pmc_pcr_lock`. The static variant wrappers expose distinct DT compatible strings without duplicating clock construction.

Risks: sentinel-driven `extra_pcks` requires `.id == 0` termination; family variants rely on correct boolean `has_lcdck`; setup failure does not unwind registered clocks. Test signals include each compatible binding producing expected clocks in clk_summary, SMD/USB rates, LCDC availability only on LCD variants, and CAN/MACB clocks only on matching variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/at91sam9x5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-audio-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-audio-pll.c

Purpose: common-clock providers for SAMA5D2 audio PLL outputs: fractional core (`FRAC`), PAD output, and PMC output. It converts requested audio rates into PLL multiplier/fraction and divider register fields.

Important APIs and data: exported registration helpers are `at91_clk_register_audio_pll_frac()`, `at91_clk_register_audio_pll_pad()`, and `at91_clk_register_audio_pll_pmc()`. Internal structs track `fracr`/`nd`, PAD `qdaudio`/`div`, and PMC `qdpmc`. Ops implement enable/disable, recalc, determine, and set-rate.

Control flow: FRAC enable resets the PLL, writes fractional register `AUDIO_PLL1`, then enables PLL and ND in `AUDIO_PLL0`. PAD/PMC enables write their divider fields and enable output bits. Determine-rate for FRAC clamps to 620-700 MHz and computes `nd`/`fracr`; PAD searches qd/div combinations and asks the parent PLL to round; PMC searches qd divisors against parent-rounded rates.

State and persistence: selected rate parameters are held in allocated clock structs until enable programs registers. This file does not implement save/restore ops; suspend correctness depends on normal clock framework re-enablement or parent PMC backup handling.

Dependencies and integration: used by SAMA5D2 SoC setup and legacy DT compat code. It depends on `AT91_PMC_AUDIO_PLL*` masks and common-clock parent rate propagation (`CLK_SET_RATE_PARENT` for PAD/PMC).

Risks: PAD set-rate does not independently verify exact divisibility or qd bounds after determine-rate; zero rate is rejected except PMC determine returns success for zero. Test signals include exact audio sample-clock derivation, parent rate lock behavior when multiple audio consumers share FRAC, and register dumps around enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-audio-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-generated.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-generated.c

Purpose: provider for AT91 generated clocks (`GCK`) controlled through the PMC PCR register. These are per-peripheral mux/divider clocks with optional rate-changing parent support for audio-capable generated clocks.

Important APIs and data: `at91_clk_register_generated()` creates a `struct clk_generated` with PCR layout, mux table, range, parent id, divider, and optional `chg_pid`. Ops cover enable/disable, is_enabled, recalc, determine, set_parent, set_rate, save/restore.

Control flow: registration initializes local `parent_id` and `gckdiv` from hardware via `clk_generated_startup()`. Enable writes PCR PID, parent selector, divider, command, and `GCKEN` under `pmc_pcr_lock`; disable clears `GCKEN`. Determine-rate first searches fixed parents and divider 1-256, then optionally forwards parent-rate requests to a changeable parent such as audio PLL.

State and persistence: parent and divider changes are staged in memory because `CLK_SET_RATE_GATE` and `CLK_SET_PARENT_GATE` ensure hardware is modified at enable time. Save/restore stores whether the clock was enabled and replays PCR setup only when previously active.

Dependencies and integration: used by SAMA5D2, SAM9X60, SAM9X7, and DT compat. It relies on `clk_pcr_layout`, `field_prep/get`, regmap, and caller-provided parent arrays/mux tables.

Risks: debug logging dereferences `req->best_parent_hw` after searches, so logic must ensure a valid best parent; mux-table correctness is critical for SAM9X7 non-linear parent values; range max/min silently clamps requests. Test signals include GCK rates under clk_summary, PCR register parent/div fields, audio PLL parent-rate changes for I2S/ClassD, and suspend/resume restore of enabled GCKs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-generated.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-h32mx.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-h32mx.c

Purpose: provider for SAMA5D4/SAMA5D2 H32MX clock divider, a master-clock derivative that can pass through the parent or divide by two to keep the H32 matrix clock within limits.

Important APIs and data: `at91_clk_register_h32mx()` registers a single-output clock with `h32mx_ops`. The private struct stores `clk_hw` and PMC regmap. `H32MX_MAX_FREQ` is 90 MHz.

Control flow: `recalc_rate` reads `AT91_PMC_MCKR`; if `AT91_PMC_H32MXDIV` is set, it returns parent/2, otherwise parent and warns when above max. `determine_rate` chooses the closer of parent or parent/2. `set_rate` validates exact parent or parent/2 and updates `H32MXDIV`.

State and persistence: no explicit save/restore state; the selected divider is only in `AT91_PMC_MCKR`. The registered clock object persists with its regmap pointer.

Dependencies and integration: used by SAMA5D2 setup for `h32mxck`, which then parents 32-bit peripheral clocks. It depends on regmap and common clock rate-gate behavior.

Risks: unsupported rates return `-EINVAL`; no automatic cap is enforced on recalc beyond a warning, so bootloader-provided overclocking can persist until consumers set a rate. Test signals include `h32mxck` at or below 90 MHz, peripheral32 clocks parented by `h32mxck`, and MCKR bit transitions during rate changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-h32mx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-i2s-mux.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-i2s-mux.c

Purpose: simple SFR-backed mux provider selecting I2S bus clock source between the peripheral clock and generated clock on SAMA5D2-style hardware.

Important APIs and data: `at91_clk_i2s_mux_register()` allocates `struct clk_i2s_mux`, storing the SFR regmap and bus id. `clk_i2s_mux_ops` implements get_parent, set_parent, and mux determine-rate.

Control flow: get reads `AT91_SFR_I2SCLKSEL` and extracts the bit for `bus_id`. set updates that bit to the requested parent index. Registration accepts parent names and bus id from SoC setup or DT compat and registers a normal mux-like `clk_hw`.

State and persistence: the parent selection is persisted solely in SFR hardware. There are no save/restore hooks here, so retention depends on SFR state across suspend or reconfiguration by consumers after resume.

Dependencies and integration: uses `syscon_regmap_lookup_by_compatible("atmel,sama5d2-sfr")` in callers and `soc/at91/atmel-sfr.h` offsets. SAMA5D2 publishes `PMC_I2S0_MUX` and `PMC_I2S1_MUX` when SFR is available.

Risks: `set_parent` trusts common-clock parent index validation; a bad bus id would address an unintended bit. Test signals include I2S mux parent in clk_summary, SFR bit changes per bus, and audio playback/recording with both peripheral and GCK parents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-i2s-mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-main.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-main.c

Purpose: providers for AT91 main clock sources: external main oscillator, internal main RC oscillator, legacy RM9200 main clock, and SAM9x5 muxable main clock.

Important APIs and data: exported helpers are `at91_clk_register_main_osc()`, `at91_clk_register_main_rc_osc()`, `at91_clk_register_rm9200_main()`, and `at91_clk_register_sam9x5_main()`. Private structs store regmap, cached RC frequency/accuracy, parent selection, and power-management status.

Control flow: oscillator prepare sets MOR key-protected enable/bypass bits and waits for `MOSCS`; unprepare clears enable. RC prepare enables `MOSCRCEN` and waits for `MOSCRCS`. RM9200/SAM9x5 main clocks probe frequency through `CKGR_MCFR`, using busy wait before boot and sleep later. SAM9x5 set_parent toggles `MOSCSEL` and waits for `MOSCSELS`.

State and persistence: RC frequency/accuracy are static properties; main mux parent is read from hardware at registration. Save/restore records enabled state and parent for backup suspend and replays preparation/parent selection when needed.

Dependencies and integration: heavily used by every SoC setup and DT compat path. It depends on key-protected MOR writes (`AT91_PMC_KEY`), PMC status bits, delay helpers, and common-clock parent data/name support.

Risks: several waits are unbounded except MCFR probing timeout; wrong parent rate can make main frequency fallback approximate; `clk_sam9x5_main_save_context()` calls RC helper on a SAM9x5 main struct layout, which is fragile but intentionally relies on shared first fields. Test signals include main clock parent switching, MCFR timeout logs, RC accuracy propagation, and suspend/resume restoring oscillator state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-master.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-master.c

Purpose: provider for AT91 master clocks, split into prescaler and divider stages for legacy PMC layouts plus an integrated SAMA7G5-style master clock. It enforces SoC-specific master output ranges and supports safe divider notifiers.

Important APIs and data: exported helpers include `at91_clk_register_master_pres()`, `at91_clk_register_master_div()`, `at91_clk_sama7g5_register_master()`, and layout constants `at91rm9200_master_layout` and `at91sam9x5_master_layout`. `struct clk_master` stores regmap, lock, layout, characteristics, cached parent/div, mux table, and PM state.

Control flow: prepare waits for `MCKRDY`/`MCKXRDY`. Legacy pres recalc decodes CSS and prescaler; legacy div recalc decodes MCKR divider. Changeable div mode can program hardware and registers a notifier to switch to a safe divider before parent changes and restore the highest safe rate afterward. SAMA7G5 ops search parent/div pairs, stage parent/div in memory, and program `MCR_V2` on enable.

State and persistence: save/restore records parent/rate expectations and warns if firmware did not preserve them, or reprograms changeable dividers. SAMA7G5 stores enable status and replays setup if enabled.

Dependencies and integration: called by all SoC setup files and shared with newer SAMA7 code. It depends on regmap, spinlocks, common-clock notifier API, layout masks, and characteristic divisor arrays.

Risks: `master_div` is a single global notifier target, so only one safe-div master is supported; unbounded ready waits can hang if hardware never signals; wrong divisors can overclock the CPU/matrix. Test signals include rate-change notifier behavior, MCKR/MCR register values, warnings about over/underclock, and suspend/resume messages about firmware clock preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-master.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-peripheral.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-peripheral.c

Purpose: providers for AT91 peripheral clocks: legacy PCER/PCDR gates and SAM9x5 PCR-based gates with optional divisors and parent-rate propagation.

Important APIs and data: `at91_clk_register_peripheral()` creates a legacy gate for IDs 2-31. `at91_clk_register_sam9x5_peripheral()` creates `struct clk_sam9x5_peripheral` with PCR layout, range, divider, `auto_div`, flags, and optional `chg_pid`. It also defines global `pmc_pcr_lock`.

Control flow: legacy enable/disable writes PCER/PCDR or PCER1/PCDR1 based on ID. PCR enable writes PID then PCR divider/cmd/enable under the lock; disable clears enable. Recalc reads active divider or computes an automatic shift that keeps the peripheral below range max. Determine-rate searches power-of-two shifts and optionally requests a changeable parent rate; set-rate stores the selected shift.

State and persistence: PCR divider state is cached in memory until enable. Save/restore records enable state and replays PCR setup if it was active. Legacy gates have no explicit PM callbacks.

Dependencies and integration: used by nearly every SoC setup file and DT compat. PCR users require a correct `clk_pcr_layout`, regmap, and lock; critical flags are passed for DDR-related peripherals.

Risks: legacy registration rejects IDs over 31 while PCR supports larger IDs; range zero disables rate management; auto-div depends on parent rate at registration/recalc. Test signals include peripheral enable bits, PCR divider fields, rate constraints for SAMA5D2/SAM9X60 high-speed peripherals, and DDR-critical clocks surviving unused-clock cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-peripheral.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-pll.c

Purpose: legacy AT91 PLL provider for PLLA/PLLB registers at `CKGR_PLLAR + id * 4`. It computes divider/multiplier pairs within input/output constraints and programs optional output/current-control fields.

Important APIs and data: `at91_clk_register_pll()` registers the clock. Layout constants describe RM9200, SAM9G45, SAM9G20 PLLB, and SAMA5D3 bit layouts. `struct clk_pll` stores id, div, mul, output range index, layout, characteristics, regmap, and PM state.

Control flow: prepare reads current PLL register, skips if already ready with matching div/mul, programs ICPR/out/count/mul/div, then waits for lock. Determine-rate calls `clk_pll_get_best_div_mul()` to scan valid dividers, choose closest multiplier, and verify output range. set-rate only updates cached div/mul/range; hardware changes occur when prepared.

State and persistence: cached div/mul/range are initialized from hardware and later set by rate changes. Save stores parent rate, calculated rate, and status; restore checks that firmware retained register values and warns if not.

Dependencies and integration: older SoC setup and DT compat paths use this provider. It depends on `clk_pll_characteristics`, `clk_pll_layout`, regmap, and PMC status lock bits.

Risks: lock wait is unbounded; restore passes `PLL_REG(id)` into a ready helper that expects an id, so warnings may be unreliable; arithmetic uses integer division and may select close but not exact rates. Test signals include PLL lock bits, chosen div/mul/out fields, invalid rate rejection, and restore warnings after backup suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-plldiv.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-plldiv.c

Purpose: small provider for the PLLA divide-by-two selector controlled by `AT91_PMC_PLLADIV2` in `MCKR`.

Important APIs and data: `at91_clk_register_plldiv()` registers a single-parent clock with `plldiv_ops`. The private struct stores `clk_hw` and PMC regmap.

Control flow: recalc reads `MCKR` and returns parent or parent/2. Determine-rate chooses whichever of parent and parent/2 is closer to the request. set-rate validates exact parent or half-parent and updates `PLLADIV2`.

State and persistence: hardware bit is the only persistent divider state; the clock object keeps the regmap pointer. No save/restore hooks are implemented.

Dependencies and integration: used by AT91SAM9G45, SAM9N12, SAM9x5, SAMA5D2, and DT compat setup before master/USB/programmable clocks consume `plladivck`.

Risks: exact-rate validation means callers must use determine/round before set; no explicit ready wait after MCKR update. Test signals include `plladivck` rate in clk_summary, MCKR bit changes, and downstream master/USB clocks selecting correct parent rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-plldiv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-programmable.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-programmable.c

Purpose: provider for AT91 programmable clocks (`PCK0..PCK7`) using PCKR CSS and prescaler fields.

Important APIs and data: `at91_clk_register_programmable()` registers a programmable clock with layout-specific CSS/prescaler behavior. Layout constants cover RM9200, SAM9G45, and SAM9x5. `struct clk_programmable` stores id, regmap, layout, optional mux table, and PM state.

Control flow: recalc reads `PCKR(id)` and divides parent by either direct divisor (`pres + 1`) or power-of-two shift. determine-rate searches all parents and legal prescalers for the closest rate not above the request. set_parent maps parent index to hardware CSS including the special RM9200 `CSSMCK_MCK` path. set_rate validates direct or power-of-two divisors and writes prescaler bits.

State and persistence: parent/rate are stored on save and restored by calling set_parent then set_rate. Hardware holds the live PCKR values.

Dependencies and integration: SoC setup files instantiate two or three PCKs; DT compat creates child node providers. It depends on regmap and common-clock rate/parent gates.

Risks: parent selection logic is layout-sensitive; direct prescaler layouts can accept many divisors while legacy layouts require powers of two; no ready wait is done here, system clocks for PCK IDs perform readiness waits. Test signals include PCK parent/rate selection, PCK system gate readiness, and suspend/resume restoration of parent plus prescaler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-programmable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-sam9x60-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-sam9x60-pll.c

Purpose: modern PLL provider for SAM9X60/SAM9X7/SAMA7-style fractional PLL cores and divider outputs using `PLL_UPDT`, `PLL_CTRL0`, `PLL_CTRL1`, `PLL_ACR`, and lock status registers.

Important APIs and data: `sam9x60_clk_register_frac_pll()` and `sam9x60_clk_register_div_pll()` register fractional and divider clocks. Shared `sam9x60_pll_core` stores id, layout, characteristics, regmap, and lock; `sam9x60_frac` stores mul/frac; `sam9x60_div` stores div/safe_div. Ops support gated or live-changing set_rate modes plus save/restore.

Control flow: fractional prepare selects PLL ID, loads ACR, writes mul/frac, enables optional UPLL bandgap/regulator sequencing, issues update, enables lock/PLL, and waits for lock. Fractional set-rate computes integer and 22-bit fractional multiplier. Divider prepare selects ID and enables programmed divider; changeable mode writes div while running. A notifier can switch one divider to a safe value before parent rate changes.

State and persistence: cached mul/frac/div initialize from hardware if already locked/enabled, otherwise from minimum valid rate. Save/restore records enable status and replays setup for active clocks.

Dependencies and integration: used by SAM9X60 and SAM9X7 SoC files and newer SAMA7 files. It depends on spinlocked regmap access, PLL characteristics including core/output ranges and ACR defaults, and common-clock notifier support.

Risks: one global notifier divider is supported; unbounded lock waits can hang on invalid PLL settings; `sam9x60_div_pll_compute_div()` iterates against `div_mask` rather than decoded max count, making layout masks important. Test signals include PLL lock bits, ACR UPLL sequencing, safe-divider behavior during CPU PLL changes, and exact rate propagation through generated/USB/master clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-sam9x60-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-slow.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-slow.c

Purpose: legacy SAM9260 slow-clock mux provider exposing which slow-clock parent hardware selected.

Important APIs and data: `at91_clk_register_sam9260_slow()` registers a clock with two parents and `sam9260_slow_ops`. The private struct stores regmap and `clk_hw`.

Control flow: get_parent reads `AT91_PMC_SR` and returns parent 1 when `AT91_PMC_OSCSEL` is set, otherwise parent 0. Registration validates name and parent array, then registers the clock.

State and persistence: no mutable software state beyond the regmap pointer; parent selection is hardware-owned. No set_parent or save/restore hooks are provided.

Dependencies and integration: used by legacy DT compat `"atmel,at91sam9260-clk-slow"` rather than the newer SCKC slow-clock provider. It depends on syscon/regmap access to PMC status.

Risks: read-only parent reporting means Linux cannot switch the source through this provider; invalid parent count aborts setup. Test signals include correct slow clock parent in clk_summary and matching `OSCSEL` hardware status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-slow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-smd.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-smd.c

Purpose: provider for the SAM9x5 SMD clock, a parent-selectable divided clock controlled by `AT91_PMC_SMD`.

Important APIs and data: `at91sam9x5_clk_register_smd()` registers the clock. `struct at91sam9x5_clk_smd` stores regmap and `clk_hw`; ops implement recalc, determine, get/set parent, and set_rate.

Control flow: recalc reads `SMD_DIV` and divides parent by `div + 1`. determine-rate clamps to parent or searches divisors 1-16 for the closest rate. set_parent toggles `AT91_PMC_SMDS` between two parents. set_rate requires exact integer division in range and writes `SMD_DIV`.

State and persistence: live state is entirely in `AT91_PMC_SMD`; no explicit PM save/restore exists.

Dependencies and integration: AT91SAM9x5 SoC setup registers `smdclk` and exposes system `smdck`; DT compat can register it when `CONFIG_HAVE_AT91_SMD` is enabled.

Risks: `get_parent` returns the raw `AT91_PMC_SMDS` bit value, which is suitable only if the bit encodes 0/1; no parent-count validation in set_parent beyond index > 1. Test signals include SMD rate and parent in clk_summary, SMD_DIV register values, and SMD consumers receiving exact supported rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-smd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-system.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-system.c

Purpose: provider for AT91 system clocks controlled by SCER/SCDR/SCSR bits, including programmable clock outputs and fixed system gates such as DDR, USB host/device, LCD, and ISI clocks.

Important APIs and data: `at91_clk_register_system()` creates `struct clk_system` with id, regmap, and PM status. Ops implement prepare/unprepare/is_prepared and save/restore. `is_pck()` identifies IDs 8-15, which need readiness polling.

Control flow: prepare writes `SCER` bit; for PCK IDs it waits until the corresponding status bit is ready. unprepare writes `SCDR`. is_prepared checks `SCSR`, then for PCK IDs also checks `PMC_SR`.

State and persistence: save records whether the system clock was prepared and restore re-prepares only previously active clocks. The hardware enable bits persist in PMC system-clock registers.

Dependencies and integration: SoC setup files register system clocks from static tables and pass critical flags for DDR where needed. It depends on parent clocks already being registered and can propagate rate setting to parents via `CLK_SET_RATE_PARENT`.

Risks: PCK readiness wait is unbounded; IDs above 31 are rejected; non-PCK clocks do not verify readiness beyond SCSR. Test signals include SCER/SCSR bit toggles, PCK ready bits, critical DDR clocks not being disabled, and resume restoring prepared system clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-system.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-usb.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-usb.c

Purpose: USB clock providers for SAM9x5/SAM9x60 mux+divider, SAM9N12 enable-only USB from one parent, and RM9200 divisor-table USB from PLLB.

Important APIs and data: exported helpers are `at91sam9x5_clk_register_usb()`, `sam9x60_clk_register_usb()`, `at91sam9n12_clk_register_usb()`, and `at91rm9200_clk_register_usb()`. Private structs store regmap, PM state, parent count, selector mask, and RM9200 divisor table.

Control flow: SAM9x5 recalc reads `AT91_PMC_USB` divider; determine-rate searches parents and divisors 1-16 while asking parents to round; set_parent writes USBS bits; set_rate writes OHCI divisor. SAM9N12 ops only enable/disable/check `USBS` and reuse divider rate logic. RM9200 uses `PLLBR.USBDIV` table entries.

State and persistence: SAM9x5 save/restore records parent, parent rate, and rate, then replays parent/rate. SAM9N12 and RM9200 variants lack explicit PM callbacks. Hardware registers hold selector/divider state.

Dependencies and integration: used by older SoC setup files, SAM9X60/SAM9X7 setup, and DT compat. It depends on common-clock parent rate propagation and `AT91_PMC_USB` or `CKGR_PLLBR` bit definitions.

Risks: SAM9N12 ops omit get/set parent even though the shared struct has fields; zero or unsupported divisors reject rate changes; SAM9X60 uses a wider selector mask than SAM9x5. Test signals include USB 48 MHz-derived clock accuracy, parent selection across PLL/UTMI/main oscillator, host/device enumeration, and suspend/resume preserving SAM9x5 USB settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-utmi.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-utmi.c

Purpose: UTMI clock provider generating a fixed 480 MHz USB PHY clock, with classic UCKR/SFR trim handling and a SAMA7G5-style XTAL frequency programming variant.

Important APIs and data: `at91_clk_register_utmi()` registers classic UTMI; `at91_clk_sama7g5_register_utmi()` registers the XTALF variant. `struct clk_utmi` stores PMC regmap, optional SFR regmap, and PM status.

Control flow: classic prepare reads parent `mainck` rate, maps 12/16/24/48 MHz to trim values, writes SFR trim when needed, enables UPLL/BIAS/count in `CKGR_UCKR`, and waits for `LOCKU`. unprepare clears `UPLLEN`. SAMA7G5 prepare maps 16/20/24/32 MHz to `PMC_XTALF` values and does not perform a lock wait.

State and persistence: UTMI rate is fixed. Save/restore records prepared state and re-runs prepare for active clocks; SAMA7G5 save checks whether `XTALF` matches current parent rate.

Dependencies and integration: used by legacy SAM9/SAMA5 setup, DT compat, and newer SAMA7 code. It depends on optional SFR syscon for non-12 MHz trims and `soc/at91/atmel-sfr.h`.

Risks: unsupported parent rates return `-EINVAL`; missing SFR regmap is fatal for nonzero classic trim; lock wait is unbounded. Test signals include `utmick` at 480 MHz, successful USB PHY lock, correct SFR trim or XTALF value, and restore after backup suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/clk-utmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/dt-compat.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/dt-compat.c

Purpose: legacy device-tree compatibility layer that registers individual AT91 clock nodes using older compatible strings, forwarding each node to the newer common provider helpers.

Important APIs and data: numerous `CLK_OF_DECLARE` setup functions cover audio PLL, generated clocks, H32MX, I2S mux, main oscillators, main clocks, master clocks, peripherals, PLLs, PLL dividers, programmable clocks, slow clock, SMD, system clocks, USB, and UTMI. Helper parsers allocate master and PLL characteristics from DT properties.

Control flow: each setup function obtains parent names/counts, parent syscon/regmap, optional `clock-output-names`, ranges/divisors/IDs, registers the corresponding `clk_hw`, and publishes it with `of_clk_add_hw_provider()`. Multi-child nodes iterate children and register one provider per child. Conditional blocks compile optional domains based on `CONFIG_HAVE_AT91_*`.

State and persistence: per-node setup allocates characteristics/range arrays for clocks that need them; registered providers own their runtime state. There is no central `pmc_data` array in this legacy path; each node is a simple provider.

Dependencies and integration: bridges old DT bindings to helpers in `pmc.h`. It relies on syscon parent nodes, child `reg` properties, Atmel range/divisor properties, and compatibility-specific constants such as generated audio parent index 5.

Risks: some error paths leak allocated characteristics when regmap lookup fails after allocation; `clock-output-names` is read from parent nodes in child loops, which may not match per-child naming expectations; invalid child IDs are skipped silently. Test signals include booting old DTBs, every legacy compatible producing a clock provider, optional feature configs gating expected bindings, and range/divisor parsing behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/dt-compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/pmc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/pmc.c

Purpose: shared PMC support for AT91 clock providers: DT clock lookup, `pmc_data` allocation, clock-range parsing, and backup-mode suspend/resume clock context integration.

Important APIs and data: `of_at91_get_clk_range()` reads two-u32 min/max properties. `of_clk_hw_pmc_get()` resolves two-cell clock specifiers by type (`CORE`, `SYSTEM`, `PERIPHERAL`, `GCK`, `PROGRAMMABLE`) and index. `pmc_data_allocate()` allocates one flexible array and partitions it into typed `clk_hw **` tables.

Control flow: range parsing returns errors from property reads. Provider lookup validates type/index and returns the matching `clk_hw` or `ERR_PTR(-EINVAL)`. Allocation computes total clocks, uses a flexible array allocation, and assigns contiguous slices. Under `CONFIG_PM`, `pmc_register_ops()` finds compatible PMC and SECURAM nodes, maps SECURAM, and registers syscore suspend/resume hooks.

State and persistence: `pmc_data` persists for each SoC provider. Backup suspend state is determined by a SECURAM word; if set, syscore suspend calls `clk_save_context()` and resume calls `clk_restore_context()`.

Dependencies and integration: every monolithic SoC setup uses `pmc_data_allocate()` and `of_clk_hw_pmc_get()`. PM support depends on DT compatibles, `atmel,sama5d2-securam`, `of_iomap`, and common-clock context callbacks implemented by individual providers.

Risks: `pmc_register_ops()` calls `of_node_put(np)` before `of_iomap(np, 0)`, making the local sequence fragile; lookup logs errors for invalid specifiers but cannot diagnose missing registered entries. Test signals include phandle clock resolution by type/index, allocation table sizing, backup suspend/resume invoking provider callbacks, and no invalid type/index errors in boot logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/pmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/pmc.h -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/pmc.h

Purpose: private interface for AT91 PMC clock drivers. It defines shared data structures, layout/characteristic descriptors, PM snapshot structure, table helpers, external layout constants, and registration prototypes.

Important APIs and data: key structs are `pmc_data`, `clk_range`, `clk_master_layout`, `clk_master_characteristics`, `clk_pll_layout`, `clk_pll_characteristics`, `clk_programmable_layout`, `clk_pcr_layout`, and `at91_clk_pms`. Macros `nck()` and `ndck()` size clock arrays from sorted ID tables, and `PMC_INIT_TABLE`/`PMC_FILL_TABLE` build mux tables.

Control flow: the header has no executable flow, but it establishes the construction contract used by SoC files: allocate `pmc_data`, register providers, store handles in typed arrays, then expose `of_clk_hw_pmc_get()`. It also declares all helper registration functions for oscillator, PLL, master, peripheral, generated, USB, UTMI, audio, and misc clocks.

State and persistence: `at91_clk_pms` standardizes saved rate, parent rate, enable status, and parent index for backup suspend. Layout structs describe hardware register masks that provider implementations persist in their allocated clock objects.

Dependencies and integration: included by every file in this subset. It depends on Linux regmap, spinlock, I/O, IRQ domain includes, and AT91 DT clock binding constants.

Risks: `nck()` assumes tables are sorted by ascending `id` and non-empty; wrong layout masks cause provider register corruption; prototypes allow both parent names and parent hardware pointers, so callers must pass consistent combinations. Test signals are compile-time: all providers agree on prototypes, layout constants link, and SoC setup tables allocate enough entries for their highest IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/pmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/sam9x60.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/sam9x60.c

Purpose: monolithic PMC setup for Microchip SAM9X60 using newer fractional/divider PLL providers, PCR peripherals, generated clocks, USB clock, programmable clocks, and master clock limits.

Important APIs and data: `sam9x60_pmc_setup()` is selected by `"microchip,sam9x60-pmc"`. Static data defines PLLA/UPLL characteristics and layouts, master layout at offset `0x28`, direct programmable layout, PCR layout at `0x88`, system clocks, peripheral clocks, and GCK tables with max-rate ranges.

Control flow: setup resolves `td_slck`, `md_slck`, and `main_xtal`, maps the PMC, allocates `pmc_data`, registers RC/main oscillators, main mux, PLLA frac/div as critical CPU clocks, UPLL frac/div as UTMI core, master pres/div, USB clock with three parents, two programmable clocks, system clocks, PCR peripherals, generated clocks, and the provider.

State and persistence: critical PLLA/div and DDR/MPDDR-related clocks prevent disabling CPU and memory domains. Fractional/divider PLL providers cache programming and restore active state; PCR generated/peripheral providers cache enable and divider state.

Dependencies and integration: depends on `clk-sam9x60-pll.c`, `clk-generated.c`, `clk-peripheral.c`, `clk-usb.c`, and `pmc_pcr_lock`. The setup is early because some clocks are clocksource dependencies.

Risks: parent arrays are reused across programmable and generated setup; all GCKs use linear parent IDs without mux table, so layout masks must match hardware encoding. Test signals include CPU/master rate, UPLL-derived USB clock, GCK max-rate enforcement for SDMMC/LCD/I2S/ClassD, and critical clocks surviving unused-clock cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/sam9x60.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/sam9x7.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/sam9x7.c

Purpose: SAM9X7 PMC setup for a richer clock tree with PLLA, UPLL, audio PLL, LVDS PLL, PLLA DIV2, master clock, generated clocks with non-linear mux IDs, peripherals, and system gates.

Important APIs and data: `sam9x7_pmc_setup()` is selected by `"microchip,sam9x7-pmc"`. It defines PLL ID/type enums, multiple PLL characteristic/range sets, fractional/divider layouts including DIVPMC and DIVIO, descriptor table `sam9x7_plls`, system/peripheral tables, and a large GCK descriptor table with per-clock PLL parents and mux hardware values.

Control flow: setup resolves three parent clocks, maps the PMC, allocates `pmc_data`, allocates a mux-table tracking buffer, registers RC/main oscillators and `mainck`, iterates PLL descriptors to register frac/div clocks and export selected outputs, registers master pres/div, USB, two programmable clocks, system clocks, PCR peripherals, then builds per-GCK mux tables and registers generated clocks.

State and persistence: allocated mux tables are intentionally retained after success because generated clocks keep pointers to them; the tracking buffer itself is freed. Critical PLLA/DIV2 and DDR/MPDDR clocks protect CPU/timer/memory domains. Provider-level PM callbacks handle active PLL/peripheral/generated state.

Dependencies and integration: uses SAM9X60 PLL provider, PCR generated/peripheral providers, and `PMC_INIT_TABLE`/`PMC_FILL_TABLE`. It sometimes obtains parent hardware with `of_clk_get_by_name()` for descriptor parents outside local handles.

Risks: `char pp_mux_table[8]` feeds `u32` mux tables; values must remain positive and small. Error paths free only mux tables tracked so far and `pmc_data`, not registered clocks. Test signals include all exported PLL indices (`PMC_PLLACK`, `PMC_AUDIOPMCPLL`, `PMC_AUDIOIOPLL`, `PMC_LVDSPLL`, `PMC_PLLADIV2`), GCK parent hardware IDs, USB parent selection, and LVDS/audio consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/sam9x7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/sama5d2.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/sama5d2.c

Purpose: SAMA5D2 PMC setup for main/PLL/master clocks, audio PLLs, UTMI trim, H32MX, USB, programmable clocks, system clocks, two classes of peripherals, generated clocks, and optional I2S mux outputs.

Important APIs and data: `sama5d2_pmc_setup()` is selected by `"atmel,sama5d2-pmc"`. Static tables define master limits, PLLA range, PCR layout, system clocks, normal and H32MX-parented peripherals, generated clocks with audio PLL changeable parent IDs, and direct programmable layout.

Control flow: setup resolves slow/main parents, maps PMC, allocates `pmc_data`, registers RC/main/mainck, PLLA and `plladivck`, audio FRAC/PAD/PMC outputs, optional SFR regmap, UTMI, master pres/div, H32MX, USB, three programmable clocks, system clocks, normal peripherals, 32-bit peripherals parented by H32MX, generated clocks, optional I2S mux clocks via SFR, and provider.

State and persistence: `ddrck` and `mpddr_clk` are critical. SFR regmap is optional for I2S mux but used by UTMI trim when present. Provider-level PM state covers main/master/peripheral/generated/USB/UTMI clocks; audio PLL lacks explicit save/restore.

Dependencies and integration: pulls together most providers in this subset. Generated clocks for I2S and ClassD can change parent audio PLL rate through `chg_pid = 5`, matching the sixth parent `"audiopll_pmcck"`.

Risks: without SFR, I2S mux clocks are skipped and UTMI supports only trims not requiring SFR; periph32 ranges rely on H32MX cap; audio PLL sharing can lock rates around first enabled consumer. Test signals include audio clocks, I2S mux availability, UTMI trim behavior at non-12 MHz main clocks, H32MX below 90 MHz, and GCK range enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/sama5d2.c -->
