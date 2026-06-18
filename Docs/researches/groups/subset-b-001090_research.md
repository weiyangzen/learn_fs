# Research: subset-b-001090

Grouped research for Linux Common Clock Framework drivers under `sources/distributed-fs/ceph-client/drivers/clk`. Each section is keyed by exact source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-si5341.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-si5341.c

Purpose: I2C Common Clock Framework driver for Silicon Labs Si5340/Si5341/Si5342/Si5344/Si5345 jitter attenuator clock generators. It exposes the root PLL, N synthesizers, and output clocks, optionally reprogramming the chip from a driver-side default register table when the device is not already programmed or DT requests `silabs,reprogram`.

Important APIs/types/functions: `struct clk_si5341` owns regmap, I2C client, input clocks, synthesizer/output `clk_hw` objects, output register maps, VCO cache, chip model, and DT flags. `struct clk_si5341_synth` and `struct clk_si5341_output` model child clocks. `si5341_decode_44_32()`/`si5341_encode_44_32()` handle the chip's 44-bit numerator plus 32-bit denominator format. Root PLL ops are `si5341_clk_ops`; synthesizer ops are `si5341_synth_clk_ops`; output ops are `si5341_output_clk_ops`. Probe-time helpers include `si5341_wait_device_ready()`, `si5341_probe_chip_id()`, `si5341_dt_parse_dt()`, `si5341_initialize_pll()`, `si5341_send_preamble()`, `si5341_finalize_defaults()`, and `of_clk_si5341_get()`. Sysfs status files expose input/PLL alarm state and sticky-bit clearing.

Control flow: `si5341_probe()` waits for `DEVICE_READY` using raw SMBus before regmap paging can run, obtains up to four parent input clocks (`in0`, `in1`, `in2`, `xtal`), enables optional `vddoN` regulators, parses per-output DT electrical settings, creates a paged regmap, identifies the exact chip model, decides whether initialization is required, and records XAXB/IOVDD policy. If reprogramming, it reads current settings into cache, sends a datasheet preamble, switches regmap to cache-only, writes the static defaults, selects/enables an active input, programs the PLL multiplier, registers root/synth/output clocks, registers the OF provider, syncs the cache, finalizes with reset/postamble, waits for LOS/LOL to clear, clears sticky alarms, then creates sysfs files. Runtime CCF callbacks reparent inputs, recalculate/store the high VCO rate, program synthesizer fractions, mux outputs to synthesizers, manage R dividers, and power/enable outputs.

State and persistence: persistent state lives in chip registers, regmap cache, enabled input clocks, enabled VDDO regulators, CCF registrations, and sysfs attributes. `data->freq_vco` caches the true 13.5-14.256 GHz VCO frequency because the CCF rate return path cannot represent it directly, so the root clock reports kHz. Reprogramming uses `regcache_cache_only()` to accumulate final values and push them in one sync. `always-on` outputs are prepared at probe. Removal tears down sysfs files and disables output regulators; CCF/device-managed allocations handle clock object lifetime.

Dependencies and integration: depends on I2C/SMBus, regmap with paging, regulator framework, DT bindings for input clocks and output child nodes, CCF provider APIs, sysfs, unaligned helpers, `gcd()`, and 64-bit math helpers. It integrates with consumers through an OF clock provider with two-cell selectors: group 0 outputs, group 1 synthesizers, group 2 root PLL. Electrical output settings depend on optional regulator voltages.

Risks: hardware access before `DEVICE_READY` can corrupt device contents, so the raw wait path is critical. The static default table contains undocumented ClockBuilder values and is sensitive to chip revision/model. Error handling during reprogramming can leave regmap in cache-only mode before cleanup because many failures jump directly to cleanup. `si5341_synth_program()` overwrites the return from `si5341_encode_44_32()` before checking it, which can hide fraction-write failures. VCO rate caching means synthesizer calculations depend on root recalc having run. Optional regulators are enabled for all possible outputs before model detection. `clk_prepare()` for always-on outputs does not enable the output and its return is ignored. Sysfs creation failure is logged but probe continues.

Test signals: useful checks are probe on each supported model, DT validation for input clocks/output electrical options/regulators, reprogram and preprogrammed paths, regcache sync failure paths, root/synth/output rate round trips, OF two-cell lookup bounds, PLL lock timeout behavior, sysfs sticky clear behavior, and regulator cleanup on probe/remove errors. There are no direct in-tree tests in this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-si5341.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-si5351.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-si5351.c

Purpose: I2C Common Clock Framework driver for Skyworks/Silicon Labs Si5351A/B/C clock generators. It builds a CCF hierarchy of gated input clocks, PLL/VXCO nodes, multisynth dividers, and clkout dividers, applying DT or platform-data configuration for parent selection, drive strength, disable state, PLL reset behavior, and initial output rates.

Important APIs/types/functions: `struct si5351_driver_data` owns variant, regmap, input gates, two PLL hardware nodes, dynamically allocated multisynth and clkout arrays, and output count. `struct si5351_hw_data` wraps each PLL/multisynth/clkout `clk_hw` plus cached parameter registers. Regmap helpers wrap read/write/update and raw bulk writes. `si5351_read_parameters()`/`si5351_write_parameters()` encode PLL/multisynth parameter blocks. CCF ops are split across `si5351_xtal_ops`, `si5351_clkin_ops`, `si5351_vxco_ops`, `si5351_pll_ops`, `si5351_msynth_ops`, and `si5351_clkout_ops`. DT parsing is in `si5351_dt_parse()`, and OF output lookup is `si53351_of_clk_get()`.

Control flow: `si5351_i2c_probe()` resolves the chip variant, parses DT into platform data, obtains `xtal` and `clkin` parents, initializes regmap, disables interrupts, forces XTAL PLL source on non-C variants, applies configured PLL/multisynth/clkout parent and electrical policy, then registers the XTAL gate, optional CLKIN gate, PLLA, PLLB or placeholder VXCO, each multisynth, and each clkout. Initial output rates from DT are applied after the clkout is registered. Finally it registers the OF clock provider. Runtime callbacks enable input fanout, divide CLKIN into the 10-40 MHz PLL input range, compute PLL feedback parameters, reset PLLs when requested, compute multisynth dividers including DIVBY4 and integer-only MS6/MS7 cases, and set output R dividers/power state.

State and persistence: mutable state is primarily device registers and regmap cache. PLL/multisynth parameter fields are cached per `si5351_hw_data` after calculation or first register read. Platform data generated from DT persists through `client->dev.platform_data`. Clock tree state persists in parent mux bits, PLL reset mode, output power bits, output enable register, disable-state registers, drive-strength bits, and initial rate programming.

Dependencies and integration: depends on I2C, regmap, CCF, `rational_best_approximation()`, DT or legacy platform data from `linux/platform_data/si5351.h`, parent clocks named `xtal` and optional `clkin`, and the register constants from `clk-si5351.h`. Consumers obtain only output clocks through the OF provider with index argument. Variant handling supports 3-output A3, normal A/B/C with eight outputs, and Si5351C CLKIN-specific routing.

Risks: VXCO support for Si5351B is a stub that warns and returns zero-rate behavior. Many regmap writes ignore return values in callbacks, so hardware I/O failures can be invisible to CCF. `si5351_reg_read()` returns zero on read failure, which can mislead rate and parent calculations. Several bounds checks use `num > 8` even valid indices are 0-7. Probe requires `platform_data` after DT parsing; non-DT systems must supply complete platform data. Initial rate setting logs but does not fail probe. Cached parameters can become stale if firmware or another driver mutates registers.

Test signals: validate DT parsing for malformed paired arrays and child nodes, all variants including A3/C/B, rate round-trip for PLLs/multisynths/clkouts, CLKIN divider programming, PLL reset polling, OF output lookup bounds, and behavior when parent clocks defer. No direct tests are present in the source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-si5351.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-si5351.h -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-si5351.h

Purpose: private register and limit header for `clk-si5351.c`. It centralizes Si5351 address constants, frequency/divider bounds, bit masks, parameter block offsets, output controls, and chip-variant identifiers.

Important APIs/types/functions: the file exports no functions. It defines frequency constraints such as PLL VCO range, multisynth and clkout minimum/maximum rates, divider parameter bounds (`SI5351_PLL_A_MIN`, `SI5351_MULTISYNTH_P*_MAX`), register addresses for status, output enable, PLL input source, clkout control, parameter blocks, phase offsets, PLL reset, crystal load, and fanout enable. `enum si5351_variant` identifies A, A3, B, and C variants used by probe matching and DT validation.

Control flow: no executable control flow. The C driver uses these constants to validate requested rates, choose parameter registers, mask/update bitfields, and expose variant-specific behavior.

State and persistence: no runtime state. The definitions describe persistent hardware register layout and encoded values that the C driver writes through regmap.

Dependencies and integration: included only by the Si5351 driver. It depends on the external platform-data enums for some semantic values in the C file, but this header itself is self-contained. Constants must match the Skyworks/Silicon Labs datasheet and AN619 equations used by the implementation.

Risks: incorrect bounds or bit masks directly corrupt rate calculations and register writes. The naming typo "MULTISYNTH" versus comments saying "multisync" is harmless but can complicate review. Variant enum values are ABI-like inside the driver because I2C/OF match data casts them through integer pointer fields.

Test signals: build coverage plus driver-level rate/variant tests are the only meaningful validation. Golden register-map tests would catch mistakes in offsets, masks, and parameter limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-si5351.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-si544.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-si544.c

Purpose: I2C CCF driver for Silicon Labs Si544 programmable oscillators. It exposes the oscillator as a zero-parent programmable clock with output enable control and rate programming across Si544A/B/C speed grades.

Important APIs/types/functions: `struct clk_si544` stores `clk_hw`, regmap, I2C client, and max frequency. `struct clk_si544_muldiv` stores feedback divider, high-speed divider, low-speed divider, and delta adjustment. Key helpers are `si544_get_muldiv()`, `si544_set_delta_m()`, `si544_set_muldiv()`, `si544_calc_muldiv()`, `si544_calc_center_rate()`, `si544_calc_rate()`, `si544_max_delta()`, `si544_calc_delta()`, and `si544_enable_output()`. CCF ops are `si544_prepare`, `si544_unprepare`, `si544_is_prepared`, `si544_recalc_rate`, `si544_determine_rate`, and `si544_set_rate`.

Control flow: probe chooses the max frequency from I2C/OF match data, names the clock from `clock-output-names` or the DT node, creates an 8-bit cached regmap, selects page 0, registers the clock, and adds a simple OF provider. Runtime rate changes first validate range. If the requested rate is within the Si544 delta-M fine-adjustment range of the current center frequency, only ADPLL delta registers are changed. Larger changes compute new dividers, read output-enable state, disable the output, allow FCAL, reset delta, write divider registers with feedback MSB last to trigger the change, start calibration, wait 10-12 ms, and restore output state if it was enabled.

State and persistence: hardware registers hold dividers, fine frequency offset, calibration state, page selection, and output enable. Regmap uses MAPLE cache with volatile control/FCAL registers. The driver persists no software rate cache beyond max frequency; recalc reads hardware each time.

Dependencies and integration: depends on I2C, regmap, CCF, 64-bit division helpers, DT compatible strings `silabs,si544a/b/c`, and optional `clock-output-names`. Consumers obtain the single clock through `of_clk_hw_simple_get`.

Risks: many writes after disabling output return immediately on error and can leave output disabled or hardware partially programmed. Fine-adjustment arithmetic relies on signed 24-bit delta decoding and ppm constants. `determine_rate()` accepts any valid rate because expected accuracy is sub-Hz, so hardware behavior is only proven at set-time. No locking protects concurrent set_rate/prepare operations beyond CCF serialization assumptions.

Test signals: validate each speed grade max range, small delta-M-only changes, large divider/calibration changes, output enable preservation on success/failure, recalc against known register values, page selection, and OF provider registration. No direct unit tests are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-si544.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-si570.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-si570.c

Purpose: I2C CCF driver for Silicon Labs Si570/Si571 programmable XO/VCXO and Si598/Si599 devices. It computes factory crystal frequency from DT-supplied factory output and programs RFREQ/N1/HSDIV for requested output rates.

Important APIs/types/functions: `struct clk_si570_info` records max frequency and whether temperature-stability variants need a divider-register offset. `struct clk_si570` holds regmap, divider offset, factory crystal frequency, cached divider values, current frequency, and I2C client. Core helpers include `si570_get_divs()`, `si570_get_defaults()`, `si570_update_rfreq()`, `si570_calc_divs()`, `si570_set_frequency()`, and `si570_set_frequency_small()`. CCF ops are `si570_recalc_rate`, `si570_determine_rate`, and `si570_set_rate`.

Control flow: probe allocates state, selects device info from match data, optionally reads `temperature-stability` and applies the 7 ppm register offset, names the clock, requires `factory-fout`, reads optional `silabs,skip-recall`, initializes regmap, recalls NVM unless skipped, computes factory `fxtal`, registers the clock/provider, optionally applies DT `clock-frequency`, then logs the current frequency. Runtime set_rate rejects out-of-range requests; changes below 3500 ppm update RFREQ under freeze-M, while larger changes recalculate dividers, freeze DCO, update HSDIV/N1/RFREQ, unfreeze, assert NEWFREQ, and wait.

State and persistence: cached `fxtal`, `n1`, `hs_div`, `rfreq`, and `frequency` mirror hardware after defaults and set_rate. Hardware state persists in divider/RFREQ/control registers; regmap marks control volatile and limits writable ranges. Optional NVM recall changes RAM register contents at probe.

Dependencies and integration: depends on I2C, regmap, CCF, DT properties `factory-fout`, optional `temperature-stability`, optional `silabs,skip-recall`, and optional `clock-frequency`. Uses fixed compatible data for Si570/571 and Si598/599 max-frequency differences.

Risks: `si570_determine_rate()` computes candidate dividers but never writes `req->rate` to the rounded achievable value on success, so callers may not see rounding information. Missing required DT properties fail probe. Recalc returns cached frequency after read failure, potentially masking hardware errors. Probe may modify hardware by recalling NVM and applying `clock-frequency`. Large rate changes are timing-sensitive and assume fixed wait ranges.

Test signals: cover factory-fout parsing, 7 ppm offset, skip-recall behavior, small versus large frequency changes, divider search boundaries, max-frequency variants, recalc from raw registers, and initial `clock-frequency` programming. No direct tests are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-si570.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-sp7021.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-sp7021.c

Purpose: platform CCF driver for the Sunplus SP7021 clock controller. It registers PLLs, derived PLL outputs, and a table of gate clocks backed by memory-mapped clock/pll/system registers.

Important APIs/types/functions: `struct sp_pll` wraps a PLL `clk_hw`, register pointer, lock, divider layout, power/bypass bits, base rate, and saved special PLL parameters. `sp_pll_ops` supports enable/disable/is_enabled/determine_rate/recalc_rate/set_rate for bypass-capable PLLs, while `sp_pll_sub_ops` exposes fixed derived PLL outputs. PLL-specific helpers include `plltv_integer_div()`, `plltv_fractional_div()`, `plltv_set_rate()`, `plla_round_rate()`, `plla_set_rate()`, `sp_pll_calc_div()`, and `sp_pll_register()`. Gate metadata is in `sp_clk_gates`.

Control flow: `sp7021_clk_probe()` maps three MMIO resources, writes a default enable mask table to clock-gate registers, allocates onecell clock data, registers PLLA/PLLE/PLLF/PLLTV/PLLSYS and PLLE subclocks, registers PLLTV_A divider, then iterates `sp_clk_gates` to register hiword-mask gates with either external clock or system PLL parents. It registers an OF onecell provider. Runtime PLL callbacks compute bypass, integer/fractional PLLTV settings, lookup PLLA table rates, write hiword-mask fields under spinlock, and read back rates from registers.

State and persistence: state lives in MMIO registers and saved PLL parameter arrays used after determine_rate for special PLL set_rate paths. The driver writes default gate-enable values during probe, which mutates hardware before consumers request clocks. Per-PLL spinlocks protect local register writes, but gate writes use CCF gate helper behavior.

Dependencies and integration: depends on platform resources, `dt-bindings/clock/sunplus,sp7021-clkc.h`, MMIO, bitfield/hiword-mask helpers, CCF onecell provider, and compatible `sunplus,sp7021-clkc`. Consumers use numeric binding IDs up to `CLK_MAX`.

Risks: special PLLA/PLLTV set_rate depends on previous determine_rate storing parameters in `clk->p`; direct set_rate without a matching determine call can use stale state. PLLTV fractional search is complex and has TODO FVCO range comments. Default gate enabling may conflict with low-power expectations. `sp_pll_calc_div()` can produce zero only if unusual base/rate inputs occur, but hardware divider encoding assumes `fbdiv - 1`. Gate names are generated positional strings, making diagnostics less semantic.

Test signals: boot-time provider registration, all DT clock indices, PLL bypass and non-bypass rate round trips, PLLTV integer/fractional rates, PLLA table rates, default gate masks, and consumer probes for peripherals. No direct tests exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-sp7021.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-sparx5.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-sparx5.c

Purpose: built-in platform CCF driver for Microchip Sparx5 DPLL clocks. It exposes nine PLL outputs named by binding order and supports exact integer or fractional divisor programming.

Important APIs/types/functions: `struct s5_clk_data` owns MMIO base and an array of `struct s5_hw_clk`; `struct s5_pll_conf` captures divider and fractional rotation fields. Key helpers are `s5_calc_freq()`, `s5_search_fractional()`, `s5_calc_params()`, `s5_pll_enable()`, `s5_pll_disable()`, `s5_pll_set_rate()`, `s5_pll_recalc_rate()`, `s5_pll_determine_rate()`, and `s5_clk_hw_get()`. `s5_pll_ops` is the shared CCF operation table.

Control flow: `s5_clk_probe()` maps one MMIO resource, creates one `clk_hw` per binding clock, points each at a 4-byte register slot, and registers an OF provider. Runtime determine_rate searches for a divider/fractional rotation configuration matching the requested rate against the best parent rate. set_rate requires the effective computed rate to exactly equal the requested rate, preserves the enable bit, writes divider and optional fractional fields, and returns `-EOPNOTSUPP` when only an approximate match exists. recalc returns zero when disabled.

State and persistence: all hardware state is in one register per clock. No software cache is retained. The enable bit is preserved across set_rate. The driver is built-in via `builtin_platform_driver()`, so it is expected to be available early and is not unloadable as a module.

Dependencies and integration: depends on MMIO, platform driver, CCF, bitfield helpers, `dt-bindings/clock/microchip,sparx5.h`, and compatible `microchip,sparx5-dpll`. Consumers use a single phandle index into `N_CLOCKS`.

Risks: `s5_calc_params()` can leave the selected configuration underinitialized when the rounded and truncated divider are equal but the fractional search is not exact, because only the alternate path assigns in that case. Fractional search stores `best` only after an improvement, so impossible searches would be fragile. set_rate rejects approximate rates even though determine_rate can return the nearest rate. No register locking is used. recalc divides by the encoded divider and assumes it is nonzero.

Test signals: verify all nine IDs and names, exact integer rates, exact fractional rates, unsupported approximate rates, enable/disable bit behavior, disabled recalc, and invalid phandle index. No direct tests are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-sparx5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-stm32f4.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-stm32f4.c

Purpose: early OF clock provider for STM32F4/F7 RCC blocks. It registers system, bus, PLL, post-divider, RTC/LSE/LSI, peripheral gate, and auxiliary mux/gate clocks for several compatible SoC families.

Important APIs/types/functions: data tables `stm32f429_gates`, `stm32f469_gates`, `stm32f746_gates`, `stm32f769_gates`, gate maps, PLL data, post-div data, and aux clock arrays define variant-specific topology. Custom clock types include APB timer multiplier (`clk_apb_mul_*`), PLL gate/rate logic (`stm32f4_pll_*`), PLL post dividers (`stm32f4_pll_div_*`), ready gates (`rgclk_*`), backup-domain composite clock gates/muxes (`cclk_*`), and auxiliary composites. `stm32f4_rcc_lookup_clk_idx()` maps DT primary/secondary binding cells to `clks[]` indices. Initialization is `stm32f4_rcc_init()` registered by `CLK_OF_DECLARE_DRIVER()`.

Control flow: the init function maps RCC MMIO, optionally obtains the syscfg regmap for backup-domain write protection, selects variant data by compatible, allocates the global clock array, resolves external HSE/I2S parents from DT, registers fixed HSI, PLL source mux, VCO input, PLL VCOs and dividers, post dividers, system/AHB/APB clocks, systick/fclk, table-driven peripheral gates, LSI/LSE ready gates, HSE RTC divider, RTC composite, and variant aux clocks. It registers the OF provider and optionally parses/programs spread-spectrum PLL settings.

State and persistence: global `base`, `clks`, `pdrm`, `stm32f4_gate_map`, and `stm32fx_end_primary_clk` persist for the lifetime of the clock provider. MMIO RCC registers persist gate, mux, divider, PLL, backup-domain, and SSCG state. Ready gates temporarily disable backup-domain write protection and poll ready bits. PLL set_rate disables and re-enables PLLs around register changes. Error cleanup frees `clks` and unmaps base only on early failure; successful init is permanent.

Dependencies and integration: depends on early OF clock initialization, DT binding `stm32fx-clock.h`, MMIO, syscon/regmap for `st,syscfg`, CCF fixed/mux/divider/gate/composite APIs, spinlocks, and compatible strings `st,stm32f42xx-rcc`, `st,stm32f469-rcc`, `st,stm32f746-rcc`, and `st,stm32f769-rcc`. It serves reset/peripheral drivers through two-cell clock specifiers.

Risks: global singleton state means multiple RCC instances are not supported. Several allocations use non-devm lifetime because this is early init; partial failures after many registrations do not unregister prior clocks. Backup-domain write protection handling is delicate and the misspelled `sofware_reset_backup_domain()` intentionally resets the backup domain when changing RTC parent. PLL enable polling returns the remaining bit status rather than a conventional errno, so timeout behavior is not richly reported. Gate-map/index math must exactly match DT bindings. Missing syscfg only warns but can affect LSE/RTC writes.

Test signals: boot each compatible SoC, verify DT clock lookup for primary and gate cells, PLL rate changes with ready polling, SSCG DT parsing, LSE/LSI/RTC enable and backup-domain writes, aux mux/gate clocks, and peripheral consumer probes. No direct unit tests are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-stm32f4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-stm32h7.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-stm32h7.c

Purpose: early OF clock provider for STM32H7 RCC. It registers fixed oscillators, ready-gated oscillators, core and bus dividers, fractional PLLs, PLL output dividers, peripheral gates, muxed kernel clocks, RTC clock, and MCO outputs.

Important APIs/types/functions: global `base` and `hws` hold MMIO and onecell clock data. Ready-gate support is implemented by `struct stm32_ready_gate` and `ready_gate_clk_ops`. Composite construction uses `struct composite_clk_cfg`, `struct composite_clk_gcfg`, `_get_cmux()`, `_get_cdiv()`, `_get_cgate()`, and `get_cfg_composite_div()`. PLLs are modeled by `struct stm32_pll_obj` with a ready gate and fractional divider; `pll_ops` handles enable/disable/recalc. ODF dividers/gates use `odf_divider_ops` and `odf_gate_ops` to disable parent PLLs while mutating outputs. Tables `pclk`, `kclk`, `stm32_mclk`, `stm32_oclk`, `stm32_odf`, `rtc_clk`, and `mco_clk` define the topology. Initialization is `stm32h7_rcc_init()`.

Control flow: `stm32h7_rcc_init()` allocates a onecell array initialized to `ERR_PTR(-ENOENT)`, maps RCC MMIO, disables backup-domain write protection through optional syscfg regmap, resolves HSE/LSE/I2S parent names from DT, patches SAI/SPI parent arrays, registers internal fixed clocks and DSI PHY placeholder, registers HSI/HSE dividers, system muxes, bus/core dividers, ready-gated oscillators, HSE/LSE gates, fixed CSI divisor, PLL VCOs and their three ODF composites, peripheral gates, kernel composites, fixed off clock, RTC composite, MCO composites, then publishes the onecell provider.

State and persistence: state is permanent early-init state: global MMIO base, global onecell array, registered clocks, and RCC register contents. Backup-domain write protection is disabled and intentionally left disabled when syscfg is available. PLL output divider and gate changes temporarily disable and re-enable the parent PLL. Ready gates poll ready bits using `udelay()` because jiffies may be unavailable during early clocksource setup.

Dependencies and integration: depends on OF early clock declarations, `dt-bindings/clock/stm32h7-clks.h`, MMIO, syscon/regmap, CCF registration helpers, spinlock-protected register access, and compatible `st,stm32h743-rcc`. Peripheral and reset drivers consume clocks through the onecell provider.

Risks: early-init allocations and registrations are not unwound except for very early MMIO failure. Disabling backup-domain write protection permanently is a platform policy with security/power implications. Fractional PLL code is recalc-only; rate programming for PLL VCOs is not implemented here. Several helper allocations can fail and leave NULL component pointers that flow into composite registration. Fixed internal rates must match hardware; `clk-rc48` is registered as 48000 rather than 48 MHz, which is notable. Ready-gate timeout returns a boolean status rather than errno.

Test signals: boot on STM32H743, validate onecell indices and `ERR_PTR` holes, oscillator ready polling, PLL recalc with fractional enabled/disabled, ODF changes while parent PLL is enabled, RTC/LSE with backup-domain access, kernel mux parents for SPI/SAI/I2C/UART, and peripheral consumer probes. No direct unit tests are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-stm32h7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-tps68470.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-tps68470.c

Purpose: platform CCF driver for the TPS68470 PMIC clock output used by camera sensor stacks. It exposes a single PLL-derived clock with three supported output rates: 19.2 MHz, 20 MHz, and 24 MHz.

Important APIs/types/functions: `struct tps68470_clkdata` holds the clock hardware, parent PMIC regmap, and cached rate. `clk_freqs[]` maps supported rates to XTALDIV/PLLDIV/POSTDIV/BUCKDIV/BOOSTDIV register values. CCF ops are `tps68470_clk_is_prepared`, `tps68470_clk_prepare`, `tps68470_clk_unprepare`, `tps68470_clk_recalc_rate`, `tps68470_clk_determine_rate`, and `tps68470_clk_set_rate`. Probe registers both a generic clkdev name and platform-data consumer aliases.

Control flow: probe obtains the parent MFD regmap, initializes the clock with `CLK_SET_RATE_GATE`, programs the default 19.2 MHz rate, registers the hardware clock, registers clkdev aliases, and optionally registers aliases for ACPI/platform-data consumers. determine_rate chooses the nearest supported table entry; set_rate requires exact support and writes boost/buck/PLL/divider/drive/source registers; prepare enables outputs A and B, enables the PLL, and waits 4-5 ms; unprepare disables PLL and tri-states outputs.

State and persistence: PMIC registers persist PLL configuration, output enable/tri-state, dividers, and drive strength. Software caches only the selected rate. Init uses `subsys_initcall()` so built-in ordering precedes camera sensor drivers.

Dependencies and integration: depends on the TPS68470 MFD regmap, platform data consumer list, CCF, clkdev, and ACPI/platform-device ordering. It integrates with camera sensors that request named clock aliases.

Risks: regmap write/update return values are ignored in prepare/unprepare/set_rate, so I/O failures are silent. Parent crystal is assumed to match the hard-coded 20 MHz-derived table. determine_rate rounds to a supported rate but set_rate rejects non-exact requests. PLL lock bit is not trusted; fixed sleep is used. Consumer alias registration loops overwrite `ret` and return only the final alias result.

Test signals: probe ordering with ACPI camera devices, exact supported set_rate values, rejected unsupported rates, clkdev alias lookup, prepare/unprepare register sequencing, and recalc after set_rate. No direct tests are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-tps68470.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-twl.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-twl.c

Purpose: platform CCF driver for TWL6030/TWL6032 32 kHz clocks. It registers `clk32kg` and `clk32kaudio` as onecell clocks and controls their PM receiver state through TWL I2C register helpers.

Important APIs/types/functions: `struct twl_clock_info` stores device pointer, TWL type, base register, and clock hardware. `twlclk_read()`/`twlclk_write()` wrap `twl_i2c_read_u8()` and `twl_i2c_write_u8()`. `twl6032_clks_ops` implements prepare/unprepare/recalc_rate. `twl_clks_probe()` allocates `clk_hw_onecell_data`, registers both clocks, and adds the OF provider. `twl_clks_id` distinguishes `twl6030-clk` and `twl6032-clk`.

Control flow: probe counts the static clock table, allocates onecell data and per-clock state, fills each `twl_clock_info` with base address and type from platform ID, registers each clock, then publishes a onecell provider. prepare writes PM receiver state: TWL6030 reads the clock's group register and writes group-shifted ON state, while TWL6032 writes ON directly. unprepare writes OFF, using all groups for TWL6030. recalc_rate always returns 32768.

State and persistence: persistent state is in TWL PM receiver VREG_STATE/VREG_GRP registers. Software state is devm-managed per-clock data and onecell provider. Clocks are flagged `CLK_IGNORE_UNUSED` to avoid common clock cleanup disabling them.

Dependencies and integration: depends on TWL MFD/platform devices, TWL I2C helper APIs, CCF onecell provider, and platform IDs. Consumers use the provider's clock indices rather than named clkdev aliases.

Risks: unprepare logs but cannot propagate write failure. TWL6030 prepare uses the current group register, so bad firmware/group setup affects enable behavior. Both clocks share identical ops and fixed rate with no parent. Platform ID must be present; otherwise dereferencing `platform_get_device_id(pdev)` would fail.

Test signals: probe for both platform IDs, prepare/unprepare register writes on TWL6030 versus TWL6032, onecell index lookup, fixed 32768 rate, and behavior on TWL I2C read/write errors. No direct tests are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-twl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-twl6040.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-twl6040.c

Purpose: platform CCF driver exposing the TWL6040 McPDM functional clock `pdmclk`. It powers the audio IC while prepared and reports the TWL6040 system-clock rate.

Important APIs/types/functions: `struct twl6040_pdmclk` stores parent MFD pointer, device pointer, `clk_hw`, and a software enabled flag. Clock ops are `twl6040_pdmclk_is_prepared`, `twl6040_pdmclk_prepare`, `twl6040_pdmclk_unprepare`, and `twl6040_pdmclk_recalc_rate`. Erratum support is in `twl6040_pdmclk_reset_one_clock()` and `twl6040_pdmclk_quirk_reset_clocks()`.

Control flow: probe obtains the parent `struct twl6040` from the parent device's driver data, allocates state, registers the `pdmclk` hardware clock, stores drvdata, and adds a simple OF provider. prepare powers the TWL6040, resets HPPLL and LPPLL to work around Phoenix Audio IC erratum #6, marks enabled, and powers down again if reset fails. unprepare powers off and clears enabled on success. recalc_rate delegates to `twl6040_get_sysclk()`.

State and persistence: hardware power state and PLL reset bits live in the TWL6040 MFD. Software tracks prepared state with `enabled`; `CLK_GET_RATE_NOCACHE` forces rate reads rather than cached CCF rates.

Dependencies and integration: depends on TWL6040 MFD APIs, platform-device binding `twl6040-pdmclk`, CCF, and OF simple provider. Audio/McPDM consumers request this clock from the TWL6040 child device.

Risks: `enabled` is not protected by a lock, relying on CCF prepare serialization. unprepare ignores power-off failure except for leaving `enabled` set. The erratum workaround always resets both PLLs during prepare, which may affect other TWL6040 users if sequencing assumptions change. Missing parent drvdata would lead to invalid MFD access.

Test signals: probe with TWL6040 MFD parent, prepare power-on plus HPPLL/LPPLL reset sequence, failure rollback, unprepare power-off, rate reporting for different sysclk selections, and OF clock lookup. No direct tests are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-twl6040.c -->
