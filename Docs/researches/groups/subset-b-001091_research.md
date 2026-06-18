# subset-b-001091 research

This grouped report covers six Linux common-clock drivers under `sources/distributed-fs/ceph-client/drivers/clk`. Each section is wrapped with the required source-path markers so the reconciliation lane can split it into the mapped source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-versaclock3.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-versaclock3.c

## Purpose
`clk-versaclock3.c` is an I2C common-clock-framework driver for Renesas VersaClock 3 timing devices, specifically the `renesas,5p35023` and `renesas,5l35023` compatibles. It models the chip as a tree of reference input, PFD muxes, PFD predividers, PLLs, divider muxes, output dividers, output muxes, and six exported output clocks (`ref`, `se1`, `se2`, `se3`, `diff1`, `diff2`). It also supports programming a raw `renesas,settings` register image from device tree before clock registration.

## Important APIs, Types, And Functions
The driver defines register offsets and bit fields for PLL input routing, predivider state, PLL feedback dividers, output divider controls, and output source muxes. The core data carriers are `struct vc3_clk_data` for one-bit mux register fields, `struct vc3_pfd_data` for PFD/predivider layout, `struct vc3_vco` and `struct vc3_pll_data` for PLL limits and divider registers, `struct vc3_div_data` for divider table metadata, `struct vc3_hw_data` for each CCF clock instance plus cached divider programming, and `struct vc3_hw_cfg` for per-compatible PLL2 VCO range and SE2 mux mask differences.

Important CCF operations include `vc3_pfd_mux_get_parent()` and `vc3_pfd_mux_set_parent()`, `vc3_pfd_recalc_rate()`, `vc3_pfd_determine_rate()`, `vc3_pfd_set_rate()`, `vc3_pll_recalc_rate()`, `vc3_pll_determine_rate()`, `vc3_pll_set_rate()`, `vc3_div_recalc_rate()`, `vc3_div_determine_rate()`, `vc3_div_set_rate()`, and the output clock mux helpers `vc3_clk_mux_determine_rate()`, `vc3_clk_mux_get_parent()`, and `vc3_clk_mux_set_parent()`. Static clock objects `clk_pfd_mux`, `clk_pfd`, `clk_pll`, `clk_div_mux`, `clk_div`, `clk_mux`, and `clk_out` describe the full hardware graph.

## Control Flow
Probe starts by creating an 8-bit I2C regmap with maple caching and optional bulk programming of the 37-byte `renesas,settings` array. It then registers clocks in dependency order: PFD muxes, PFDs, PLLs, divider muxes, dividers, output muxes, and finally fixed-factor output nodes. PLL2 and the SE2 mux are adjusted from the match data because the supported 5P and 5L variants use different VCO ranges and SE2 select bits. `vc3_of_clk_get()` exports clocks by the phandle argument index and rejects indexes outside the six-element output array.

Rate control flows through CCF parent propagation. PFDs cap PLL input at 50 MHz and either bypass the predivider or select integer/divide-by-2 predivision. PLL1 and PLL3 are integer-N PLLs with fixed VCO limits; PLL2 supports a 16-bit fractional feedback divider and receives variant-specific VCO limits. Output dividers use fixed `clk_div_table` mappings and are marked read-only for the existing programmed divider values, while muxes select between internal PLL/divider branches and propagate rate changes to parents.

## State And Persistence
Persistent state is the chip register map written over I2C: optional initial settings, PFD source and predivider bits, PLL feedback integer/fraction fields, divider select fields, mux source bits, and output configuration registers. The driver also keeps transient CCF registration state in static `vc3_hw_data` arrays and stores computed `div_int`/`div_frc` in the clock object between `determine_rate` and `set_rate`. There is no remove callback because all registered resources are device-managed; the module-level I2C driver owns lifetime.

## Dependencies And Integration Points
The driver integrates with the Linux CCF via `struct clk_hw`, `clk_ops`, `devm_clk_hw_register()`, fixed-factor output registration, and `devm_of_clk_add_hw_provider()`. It depends on I2C regmap, OF match data, device-tree clock specifiers, and generic divider/mux CCF helpers. External consumers reference the output indexes from device tree; board firmware or DT can preconfigure raw device registers through `renesas,settings`.

## Risks
The static arrays are global, so the implementation assumes a single device instance; registering multiple VC3 chips would share mutable `regmap`, cached divider, and output pointers. The optional raw settings array can overwrite all modeled registers, so invalid DT data can produce unusable clocks before CCF validation. Several divider clocks are read-only, which means requests may be rounded to existing hardware state rather than reprogramming outputs. The fractional PLL calculation uses cached fields from `determine_rate`, so callers must follow the CCF determine/set flow. Rate arithmetic uses `unsigned long` in places where high VCO rates can be architecture-sensitive on 32-bit builds. Regmap read errors in recalc/get-parent helpers are mostly ignored, which can collapse failures to parent 0 or rate 0.

## Test Signals
Useful validation signals are successful probe against both compatible strings, successful raw settings programming including `-EOVERFLOW` rejection, `clk_summary` topology matching the hardware graph, output phandle indexes returning the expected clocks, and rate requests that exercise direct PFD bypass, divide-by-2 predivision, integer PLLs, fractional PLL2, and each output mux branch. Regression tests should include invalid clock indexes, missing/oversized `renesas,settings`, and hardware-backed rate measurements or tracepoints showing that requested output rates match computed PLL/divider programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-versaclock3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-versaclock5.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-versaclock5.c

## Purpose
`clk-versaclock5.c` is an I2C CCF driver for IDT/Renesas VersaClock 5 and VersaClock 6 clock-generator families. It exposes one selectable input path, optional frequency doubler, PFD, fractional PLL, up to four fractional output dividers (FODs), and up to five output buffers. It supports multiple models with different output counts, internal crystal availability, PFD doubler support, FOD sync-bypass capability, and maximum VCO frequencies.

## Important APIs, Types, And Functions
`struct vc5_chip_info` captures model-specific hardware capacity and flags. `struct vc5_driver_data` owns the I2C client, regmap, input clocks, clock mux/doubler/PFD/PLL nodes, FOD array, and output array. `struct vc5_hw_data` stores PLL/FOD CCF state and cached integer/fractional divider fields. `struct vc5_out_data` stores output CCF state plus pending DT-derived electrical configuration masks.

The major operations are `vc5_mux_*` for selecting `xin` versus `clkin`, `vc5_dbl_*` for optional reference doubling, `vc5_pfd_*` for PLL input predivision, `vc5_pll_*` for the 12-bit integer plus 24-bit fractional feedback divider, `vc5_fod_*` for the output divider's 12-bit integer plus fractional divider, and `vc5_clk_out_*` for output muxing and buffer enable. Device-tree parsing helpers include `vc5_update_mode()`, `vc5_update_power()`, `vc5_update_slew()`, `vc5_map_cap_value()`, `vc5_update_cap_load()`, and `vc5_get_output_config()`.

## Control Flow
Probe allocates per-device state, reads optional `xin` and `clkin` parent clocks, initializes a protected regmap that blocks writes to factory-reserved registers, applies optional shutdown/output-enable polarity bits, and builds the CCF graph in dependency order. If no external `xin` exists but the model has `VC5_HAS_INTERNAL_XTAL`, it registers a fixed 25 MHz internal crystal. For external crystals, it optionally programs load capacitance from `idt,xtal-load-femtofarads`.

The registered tree is input mux, optional doubler, PFD, PLL, FODs, a special OUT0 path, and FOD-connected outputs. `vc5_map_index_to_output()` handles package-specific output numbering, notably the 5P49V5933 sparse mapping. Output registration also reads child nodes named `OUTn` for mode, voltage, and slew settings, but those settings are applied lazily in `vc5_clk_out_prepare()` when the output buffer is enabled. The OF clock provider returns only output clocks, not internal PLL/FOD nodes.

## State And Persistence
Persistent state lives in the chip's I2C registers: source enable bits, predivider configuration, PLL feedback fields, FOD divider blocks, FOD enable/source bits, output electrical configuration, output enable bits, and the global reset/sync trigger. Runtime state includes the regmap cache, optional fixed-rate internal crystal, CCF nodes, cached divider values staged by `determine_rate`, and per-output pending config masks. Suspend switches the regmap to cache-only and marks it dirty; resume turns bus access back on and syncs cached writes to hardware.

## Dependencies And Integration Points
The driver uses the Linux CCF, I2C, regmap, OF/property APIs, PM ops, and `dt-bindings/clock/versaclock.h` values for output modes. Board descriptions provide parent clocks named `xin` and/or `clkin`, optional top-level control properties (`idt,shutdown`, `idt,output-enable-active`, `idt,xtal-load-femtofarads`), and child output electrical properties. Clock consumers bind through the OF provider and output indexes.

## Risks
FOD and PLL rate calculations rely on integer arithmetic, shifted fractional fields, and cached `determine_rate` results, so changes can easily introduce off-by-one rate errors. `vc5_fod_determine_rate()` warns that one divider combination silences the output and clamps to avoid it; relaxing that logic is risky. `vc5_clk_out_prepare()` may write reserved sync-bypass registers on supported VC6E devices and toggles global reset after FOD updates, both of which are hardware-sensitive sequences. The driver mixes devm-managed clocks with manually registered fixed-rate internal crystal and manual provider removal, so error paths must keep ownership balanced. Output child-node lookup by `OUT%d` uses hardware output numbering; mismatches in DT naming silently skip electrical configuration. Rate and divider arithmetic uses `unsigned long` and `u32` near multi-GHz VCO values, which is safer on 64-bit targets than 32-bit ones.

## Test Signals
Key tests include probe for all listed I2C/OF compatibles, input mux behavior with only `xin`, only `clkin`, both inputs, and internal crystal fallback, and clock-rate requests spanning PFD bypass/division, optional doubler, PLL fractional feedback, and FOD fractional output division. DT validation should cover legal and illegal output modes, voltages, slew percentages, load-capacitance bounds, and 5P49V5933 index mapping. Runtime validation should verify suspend/resume restores register state, output prepare/unprepare toggles buffer enable, FOD sync bypass prevents unrelated output glitches on VC6E variants, and unsupported factory-reserved register writes remain blocked by regmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-versaclock5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-versaclock7.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-versaclock7.c

## Purpose
`clk-versaclock7.c` is a CCF I2C driver for Renesas VersaClock7-family timing devices, currently represented by the `renesas,rc21008a` compatible. It exposes a fixed APLL rate derived from the current device state, three fractional output dividers (FODs), four integer output dividers (IODs), and eight exported output clocks mapped from the RC21008A package's physical outputs.

## Important APIs, Types, And Functions
The driver defines 16-bit paged register access through regmap range configuration and field definitions for XO/APLL configuration, FOD/IOD divider blocks, output-bank source selection, and output driver enable bits. `struct vc7_chip_info` describes model output mapping. `struct vc7_apll_data`, `struct vc7_fod_data`, `struct vc7_iod_data`, and `struct vc7_out_data` hold the CCF-visible state for each clock block. `struct vc7_driver_data` ties the client, regmap, parent input, APLL, FODs, IODs, and outputs together.

Important helpers include the local 128-bit math routines `vc7_64_mul_64_to_128()` and `vc7_128_div_64_to_64()`, bank routing resolver `vc7_get_bank_clk()`, register accessors `vc7_read_apll()`, `vc7_read_fod()`, `vc7_write_fod()`, `vc7_read_iod()`, `vc7_write_iod()`, `vc7_read_output()`, and `vc7_write_output()`, and rate calculators `vc7_get_apll_rate()`, `vc7_calc_iod_divider()`, `vc7_calc_fod_1st_stage()`, `vc7_calc_fod_1st_stage_rate()`, `vc7_calc_fod_2nd_stage_rate()`, and `vc7_calc_fod_divider()`.

## Control Flow
Probe allocates state, requires a parent clock named `xin`, creates a paged I2C regmap, selects a node name from `clock-output-names` or the OF node, reads the current APLL configuration, computes the APLL rate, and registers the APLL as a fixed-rate clock. It then registers all FOD and IOD internal clocks as children of APLL. For each exported output, it maps the logical provider index to a physical output, derives the output bank, reads the bank's current source selection, resolves that source to a supported FOD or IOD, and registers the output clock with that existing parent. The driver explicitly does not remap output banks; it mirrors the chip's programmed routing.

FOD rate determination computes a first-stage integer/fractional divider and optionally searches the second-stage integer divider when the first-stage rate would be below 33 MHz. It prefers integer solutions before fractional ones and enforces output range checks in `set_rate`. IOD rate handling is simpler: it computes and writes a bounded integer divisor. Output prepare/unprepare toggles the output disable bit; `is_enabled` reads the same register and reports inverted state.

## State And Persistence
Persistent state is the VC7 register file: APLL registers are read but not changed, FOD/IOD divider registers are updated, bank source mapping is read but not changed, and output driver disable bits are written during prepare/unprepare. In memory, the driver stores the most recent divider values in FOD/IOD structs and the current output disable state in each output struct. The fixed-rate APLL clock persists as a manually registered clock and is unregistered in remove; FOD/IOD/output clocks are devm-managed.

## Dependencies And Integration Points
The driver integrates with I2C, CCF, OF clock providers, regmap range windows, and kernel math helpers. Consumers receive only exported output clocks from `vc7_of_clk_get()`. The driver depends on board or firmware initialization to configure APLL and output bank routing before Linux probes, because APLL changes and FOD/IOD-to-bank remapping are outside the supported runtime surface.

## Risks
The largest risk is arithmetic correctness: FOD rates combine 10 GHz parent rates, 34-bit fractional denominators, and 128-bit intermediate math. The local division routine returns all-ones on overflow or divide-by-zero, so caller-side validation matters. `vc7_get_apll_rate()` returns an `unsigned long` but may return a negative error value cast through that type if APLL reads fail. Several regmap bulk reads cast stack scalar addresses to `u32 *`, `u16 *`, or `u64 *`; the regmap endian configuration is intended to make this work, but alignment and endian changes would be delicate. The driver does not validate APLL rate against the documented 9.5-10.7 GHz range after reading hardware. Unsupported bank source values abort output registration, so firmware routing outside the driver's supported map prevents probe. There is no PM regcache restore path.

## Test Signals
Validation should probe RC21008A hardware or emulation with expected output mapping `{1,2,3,6,7,8,10,11}` and known bank routing. `clk_summary` should show APLL, FODs, IODs, and eight outputs with parents matching existing bank source registers. Rate tests should cover FOD outputs below and above the 33 MHz first-stage threshold, integer and fractional FOD solutions, IOD min/max bounds, and out-of-range rate rejection. Output enable tests should verify prepare/unprepare toggles `VC7_REG_OUT_DIS`. Firmware-routed unsupported bank sources should be tested as probe failures so board integration catches invalid preconfiguration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-versaclock7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-vt8500.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-vt8500.c

## Purpose
`clk-vt8500.c` provides early OF-declared clock registration for VIA/Wondermedia SoC clock controllers. It supports memory-mapped PMC-backed gated clocks, divisor clocks, combined gated-divisor clocks, and several PLL encoding families (`VT8500`, `WM8650`, `WM8750`, and `WM8850`). The driver is intended for platform clock setup during boot rather than as a normal platform device.

## Important APIs, Types, And Functions
`struct clk_device` models a device clock with optional divisor and enable registers, enable bit, divisor mask, and shared lock. `struct clk_pll` models a PLL register plus PLL type. `vtwm_set_pmc_base()` maps the PMC either from the `via,vt8500-pmc` node or the legacy physical base `0xD8130000`. Device clock operations are `vt8500_dclk_enable()`, `vt8500_dclk_disable()`, `vt8500_dclk_is_enabled()`, `vt8500_dclk_recalc_rate()`, `vt8500_dclk_determine_rate()`, and `vt8500_dclk_set_rate()`.

PLL support is split into bit-calculation helpers for each hardware family: `vt8500_find_pll_bits()`, `wm8650_find_pll_bits()`, `wm8750_find_pll_bits()`, `wm8850_find_pll_bits()`, and `wm8750_get_filter()`. CCF-facing PLL operations are `vtwm_pll_set_rate()`, `vtwm_pll_determine_rate()`, and `vtwm_pll_recalc_rate()`. OF init functions are registered through `CLK_OF_DECLARE()` for `via,vt8500-device-clock`, `via,vt8500-pll-clock`, `wm,wm8650-pll-clock`, `wm,wm8750-pll-clock`, and `wm,wm8850-pll-clock`.

## Control Flow
For a device clock node, `vtwm_device_clk_init()` ensures the PMC base is mapped, allocates a `clk_device`, reads optional `enable-reg`/`enable-bit` and `divisor-reg`/`divisor-mask` properties, selects the correct operation set based on whether the clock is gated, divided, or both, registers the clock, adds an OF provider, and registers a clkdev lookup. For rate changes, the divisor path computes a ceiling divisor, handles SDMMC's special bit-5 `/64` predivider encoding when the divisor mask is `0x3f`, waits for PMC busy bits before and after writing, and serializes register updates with a global spinlock.

For PLL nodes, `vtwm_pll_clk_init()` maps the register offset from `reg`, assigns the PLL type from the compatible wrapper, registers a PLL clock with one parent, adds an OF provider, and registers clkdev lookup. PLL `determine_rate` and `set_rate` dispatch to type-specific search functions and then encode the chosen multiplier/divisor/filter fields into the memory-mapped register while waiting for PMC busy state.

## State And Persistence
Persistent state is the memory-mapped PMC register contents controlling clock gates, device divisors, and PLL multiplier/divider fields. In-memory state consists of allocated `clk_device` and `clk_pll` structures retained for the life of the system, the global `pmc_base`, and the shared spinlock. There is no remove path because `CLK_OF_DECLARE` clocks are boot-time infrastructure. Register writes are immediately persistent in hardware, guarded by busy polling but not mirrored through regmap or a suspend cache.

## Dependencies And Integration Points
The driver integrates with early device-tree clock initialization, `of_iomap()`, `ioremap()`, CCF `clk_hw_register()`, `of_clk_add_hw_provider()`, and legacy clkdev lookups. It depends on board DTS nodes to provide PMC offsets, parent clocks, optional output names, and compatible strings selecting the correct PLL formula. Consumers use the registered OF clock providers and clkdev aliases.

## Risks
Busy waiting on `pmc_base` can spin forever if hardware never clears `VT8500_PMC_BUSY_MASK`. Some error paths after allocation or missing properties return without freeing already allocated state. PLL search loops are brute force for WM8750/WM8850 and intentionally choose the closest lower-or-equal rate, which can surprise consumers expecting exact rates. In `vtwm_pll_determine_rate()`, failures assign the negative errno into `req->rate` and still return 0, which is an unusual CCF contract. The SDMMC divisor encoding is inferred from mask value `0x3f`, so another clock with the same mask but different semantics would be misdetected. The fallback legacy PMC base can map hardware even without a proper DT PMC node.

## Test Signals
Tests should verify OF-declared clocks register from representative DTS nodes for gated-only, divisor-only, and gated-divisor clocks. Rate tests should cover zero-rate no-ops, divisor rounding, divisor overflow rejection, SDMMC `/64` encoding, and PMC busy wait sequencing. PLL tests should exercise all four compatibles, exact and inexact rate requests, out-of-range rejection, and recalc from known register encodings. Boot logs and `clk_summary` should confirm expected parentage, output names, enable states, and clkdev aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-vt8500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-wm831x.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-wm831x.c

## Purpose
`clk-wm831x.c` is a platform CCF driver for the Wolfson WM831x PMIC clock block. It exposes three clocks from the parent MFD device: a 32.768 kHz crystal clock, an FLL clock that is supported only in AUTO frequency mode, and a `clkout` output buffer that can select either FLL or crystal as parent.

## Important APIs, Types, And Functions
`struct wm831x_clk` stores the parent `struct wm831x *`, three `clk_hw` objects, and a cached `xtal_ena` flag read once at probe. `wm831x_xtal_is_prepared()` and `wm831x_xtal_recalc_rate()` expose the OTP/InstantConfig-controlled crystal state. FLL support is implemented by `wm831x_fll_is_prepared()`, `wm831x_fll_prepare()`, `wm831x_fll_unprepare()`, `wm831x_fll_recalc_rate()`, `wm831x_fll_determine_rate()`, `wm831x_fll_set_rate()`, and `wm831x_fll_get_parent()`. Output support is implemented by `wm831x_clkout_is_prepared()`, `wm831x_clkout_prepare()`, `wm831x_clkout_unprepare()`, `wm831x_clkout_get_parent()`, and `wm831x_clkout_set_parent()`.

## Control Flow
Probe retrieves the PMIC core from the parent device, allocates driver state, reads `WM831X_CLOCK_CONTROL_2` to cache whether the crystal is enabled, then registers `xtal`, `fll`, and `clkout` as device-managed `clk_hw` objects. The FLL has two possible parents by name (`xtal`, `clkin`) but AUTO mode always reports the crystal parent. FLL rate determination selects the nearest value from eight predefined AUTO rates. `set_rate` accepts only exact table entries and refuses changes while the FLL is enabled because the CCF init data marks the clock `CLK_SET_RATE_GATE`.

`fll_prepare` sets `WM831X_FLL_ENA` and sleeps 2-3 ms for the new frequency to take effect; `fll_unprepare` clears the same bit. `clkout_prepare` and `clkout_unprepare` unlock protected PMIC registers, update `WM831X_CLKOUT_ENA`, and relock. `clkout_set_parent` updates the `WM831X_CLKOUT_SRC` bit to select between FLL and crystal.

## State And Persistence
Persistent state lives in WM831x PMIC registers accessed through the MFD register API: `FLL_CONTROL_1`, `CLOCK_CONTROL_1`, `CLOCK_CONTROL_2`, and `FLL_CONTROL_5`. The crystal enable state is not writable here and is cached once because it is controlled by OTP/InstantConfig. The FLL enable bit, FLL AUTO frequency index, clkout enable bit, and clkout parent bit are mutable hardware state. The driver has no explicit remove callback; devm clock registrations are released with the platform device.

## Dependencies And Integration Points
The driver depends on the WM831x MFD core for register reads, writes, bit updates, and protected register locking. It integrates with CCF as a platform driver named `wm831x-clk` and publishes clocks named `xtal`, `fll`, and `clkout`. It expects any external `clkin` parent to be registered elsewhere by name and relies on MFD platform-device creation for probe.

## Risks
The FLL implementation only supports AUTO mode; manual FLL configurations recalc to 0 and log an error. `wm831x_fll_is_prepared()` returns true on register-read failure, which prevents rate changes but can hide hardware access problems as a conservative enabled state. `clkout_set_parent()` writes protected clock control bits without unlocking, unlike prepare/unprepare, so whether it works depends on MFD/register policy for that field. FLL rate selection uses `abs()` on differences involving unsigned long request values coerced through integer arithmetic, which is acceptable for the small table but fragile if expanded. Names are fixed and not OF-provider based, so multiple WM831x instances could collide in the global clock namespace.

## Test Signals
Useful tests include platform probe from the WM831x MFD, xtal rate reporting based on `WM831X_XTAL_ENA`, FLL nearest-rate selection for all eight AUTO frequencies, exact-match rejection in `set_rate`, `-EPERM` when changing FLL rate while enabled, and the 2-3 ms enable delay. Register-level tests should verify clkout enable/disable performs unlock/update/lock and parent selection toggles `WM831X_CLKOUT_SRC`. Integration tests should check consumers can resolve `xtal`, `fll`, and `clkout` by name and that manual FLL mode is reported as unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-wm831x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-xgene.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-xgene.c

## Purpose
`clk-xgene.c` provides boot-time CCF support for AppliedMicro X-Gene SoC clocks. It covers SOC and PCP PLL clocks, PMD fractional scale clocks, and IP/device clocks with optional enable/reset CSR control and optional divider registers. All clocks are registered from device tree using `CLK_OF_DECLARE()`.

## Important APIs, Types, And Functions
PLL support centers on `struct xgene_clk_pll`, `xgene_clk_pll_is_enabled()`, `xgene_clk_pll_recalc_rate()`, `xgene_register_clk_pll()`, `xgene_pllclk_version()`, and `xgene_pllclk_init()`. PMD scaling uses `struct xgene_clk_pmd`, `xgene_clk_pmd_recalc_rate()`, `xgene_clk_pmd_determine_rate()`, `xgene_clk_pmd_set_rate()`, `xgene_register_clk_pmd()`, and `xgene_pmdclk_init()`. Device clocks use `struct xgene_dev_parameters`, `struct xgene_clk`, `xgene_clk_enable()`, `xgene_clk_disable()`, `xgene_clk_is_enabled()`, `xgene_clk_recalc_rate()`, `xgene_clk_set_rate()`, `xgene_clk_determine_rate()`, `xgene_register_clk()`, and `xgene_devclk_init()`.

Register field macros decode old and v2 PLL formats (`N_DIV_RD`, `SC_N_DIV_RD`, `SC_OUTDIV2`, `CLKR_RD`, `CLKOD_RD`, `CLKF_RD`, `REGSPEC_RESET_F1_MASK`). Device-tree compatibles bind SOC PLL, PCP PLL, v2 PLL variants, PMD clocks, and generic device clocks.

## Control Flow
PLL OF init maps the register resource, determines whether the compatible uses version 1 or version 2 layout, registers a read-only PLL clock with one parent, adds an OF clock provider, and registers a clkdev alias. PLL recalc reads hardware fields and computes PCP or SOC output frequency; version 2 uses a different feedback and output divider encoding.

PMD init skips disabled nodes, maps its CSR, sets an inverted 3-bit scale with denominator 8, registers a clock, and adds provider/clkdev entries. Its rate operations compute `parent_rate * scale / denom`; `determine_rate` rounds up scale, and `set_rate` writes the encoded scale field under the shared lock.

Device clock init maps up to two register resources, distinguishing `div-reg` from CSR registers by resource name, loads optional properties for enable/reset offsets and masks plus divider offset/width/shift, registers the CCF clock, and adds an OF provider. Enable first sets the clock-enable mask then clears CSR reset; disable asserts reset before clearing the enable mask. Rate operations divide by a register field when a divider resource is present, otherwise pass through the parent rate.

## State And Persistence
Persistent state is memory-mapped SoC register content for PLL status/configuration, PMD scale fields, device clock enable masks, CSR reset masks, and device dividers. In memory, each registered clock stores mapped register pointers and property-derived offsets/masks. There is no dynamic remove path; mappings and allocated clock structures persist for the system lifetime. A global `clk_lock` serializes register updates for PLL/PMD/device paths that pass it.

## Dependencies And Integration Points
The driver uses early OF clock declaration, `of_iomap()`, `of_address_to_resource()`, CCF registration, clkdev lookup registration, and relaxed MMIO accessors. It depends on DTS resource names and properties to distinguish CSR and divider resources and to provide parent clocks. Consumers obtain clocks through OF providers or clkdev names from `clock-output-names`.

## Risks
Several registration helpers return `NULL` instead of an `ERR_PTR` on `clk_register()` failure, while callers check only `IS_ERR()`, so failures may be treated as success and passed to provider registration. Device clock divider recalc divides by the raw field without guarding against zero. `xgene_clk_set_rate()` returns the achieved rate despite the CCF `.set_rate` contract expecting 0 or a negative errno. Divider calculation rounds down and masks without validating overflow against field width, which can silently program an unintended divisor. OF resource-name assumptions are fragile: anything not named `div-reg` is treated as CSR. MMIO mappings are generally not unmapped after successful boot-time registration, by design, but error cleanup must keep both mapped resources balanced.

## Test Signals
Tests should instantiate DT nodes for each compatible and verify `clk_summary` rates against known register snapshots for v1 SOC PLL, v1 PCP PLL, v2 SOC/PCP PLL, PMD inverted scaling, pass-through device clocks, and divided device clocks. Enable/disable tests should inspect CSR order: enable mask set before reset deassertion, reset assertion before enable clear. Negative tests should cover zero divider fields, missing or misnamed resources, disabled PMD/device nodes, divider field overflow, and simulated `clk_register()` failure so the NULL-versus-ERR_PTR path is caught.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-xgene.c -->
