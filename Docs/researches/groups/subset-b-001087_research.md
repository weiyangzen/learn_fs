# subset-b-001087 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-bm1880.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-bm1880.c

### Purpose
`clk-bm1880.c` is the Common Clock Framework provider for the Bitmain BM1880 SoC. It models the SoC's PLL block, system muxes, fixed gate clocks, divider clocks, and gate-plus-divider or gate-plus-mux composites, then exports a onecell provider indexed by `dt-bindings/clock/bm1880-clock.h`.

### Important APIs, Types, And Functions
The main state is `struct bm1880_clock_data`, carrying PLL and SYS MMIO bases plus `clk_hw_onecell_data`. Clock descriptions are split into `bm1880_pll_hw_clock`, `bm1880_div_hw_clock`, `bm1880_mux_clock`, `bm1880_gate_clock`, and `bm1880_composite_clock`, with static tables describing each SoC clock. Important callbacks are `bm1880_pll_recalc_rate()`, `bm1880_clk_div_recalc_rate()`, `bm1880_clk_div_determine_rate()`, and `bm1880_clk_div_set_rate()`. Registration helpers create PLLs, muxes, dividers, gates, and composites before `bm1880_clk_probe()` installs the OF provider.

### Control Flow, State, And Persistence
Probe maps two platform resources, allocates a flexible onecell array, initializes all slots to `ERR_PTR(-ENOENT)`, and registers clocks in dependency order: PLLs, standalone dividers, muxes, composites, then gates. PLL rates are read-only calculations from hardware register fields. Divider clocks use a shared spinlock and BM1880-specific behavior where an unprogrammed divider register can fall back to an `initval` before delegating math to generic divider helpers. Persistent state is the registered clock graph plus hardware register contents; managed allocation covers the provider data, but many clock objects are static or manually registered.

### Dependencies, Integration Points, Risks, And Test Signals
This driver depends on platform resources, OF compatible `bitmain,bm1880-clk`, CCF gate/mux/composite/divider helpers, BM1880 clock IDs, MMIO ordering, and consumers using onecell indices. Risks include unhandled return values in `bm1880_clk_probe()` for intermediate registration batches, incomplete unwind if a later batch fails after earlier batches succeed, critical/ignore-unused flags masking ownership bugs, and table/register mismatches for divider reset defaults. In this source snapshot there are duplicated initializer tokens in the BM1880 tables/macros, which is a build signal to verify before relying on the file. Test signals are provider registration, all DT clock IDs resolving, expected PLL rates from boot registers, rate changes updating divider fields under lock, no gating of CPU/DDR-critical clocks, and peripheral probe success for UART, eMMC/SD, USB, Ethernet, GPIO, and AXI clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-bm1880.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-bulk.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-bulk.c

### Purpose
`clk-bulk.c` implements bulk clock acquisition and bulk prepare/enable/disable/put helpers. It lets device drivers handle arrays of `struct clk_bulk_data` with consistent forward setup and reverse-order unwind.

### Important APIs, Types, And Functions
Exported APIs include `clk_bulk_get()`, `clk_bulk_get_optional()`, `clk_bulk_get_all()`, `clk_bulk_put()`, `clk_bulk_put_all()`, `clk_bulk_prepare()`, `clk_bulk_unprepare()`, `clk_bulk_enable()`, and `clk_bulk_disable()`. OF internals `of_clk_bulk_get()` and `of_clk_bulk_get_all()` populate clock IDs from `clock-names` and retrieve indexed DT clocks.

### Control Flow, State, And Persistence
Bulk get initializes each array entry to a null clock, then obtains clocks left to right. If any required clock fails, it calls `clk_bulk_put()` on the successfully acquired prefix. Optional acquisition suppresses `-ENOENT` per entry and leaves the entry null. Prepare and enable also proceed left to right and unwind the already prepared or enabled prefix in reverse order on failure; disable/unprepare/put always walk backward. The only persistent state is held by the caller's `clk_bulk_data` array and references returned by CCF.

### Dependencies, Integration Points, Risks, And Test Signals
The file integrates with OF clock providers, `clk_get()` lookup by con_id, optional clock semantics, `CONFIG_HAVE_CLK_PREPARE`, and exported symbols consumed by drivers. Risks include callers using mismatched counts, expecting optional missing clocks to be real handles, or failing to follow disable-before-unprepare ordering. Test signals include injected failure at each index, optional `-ENOENT` handling, DT `clock-names` population, reverse unwind ordering, null-safe `clk_bulk_put_all()`, and successful bulk prepare-enable/disable-unprepare cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-bulk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-cdce706.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-cdce706.c

### Purpose
`clk-cdce706.c` drives the TI CDCE706 programmable clock synthesizer over I2C. It exposes the input selector, three PLLs, six dividers, and six output clocks as a CCF hierarchy.

### Important APIs, Types, And Functions
`struct cdce706_dev_data` stores the I2C client, regmap, optional input clocks, and arrays of `cdce706_hw_data` for clkin, PLLs, dividers, and outputs. Register helpers wrap `regmap_read/write/update_bits()` with the device's command bit. Clock ops are `cdce706_clkin_ops`, `cdce706_pll_ops`, `cdce706_divider_ops`, and `cdce706_clkout_ops`; probe registers each layer through `cdce706_register_clkin()`, `cdce706_register_plls()`, `cdce706_register_dividers()`, and `cdce706_register_clkouts()`.

### Control Flow, State, And Persistence
Probe requires SMBus byte-data support, initializes regmap, reads the chip's existing mux/divider/multiplier state, registers clock hardware with device-managed lifetime, then installs `of_clk_cdce_get()` for output indices. PLL and divider determine-rate callbacks cache selected `mul`/`div` values in `cdce706_hw_data`, and set-rate callbacks persist those values into CDCE706 registers. Output prepare/unprepare toggles output enable bits; parent changes update mux fields.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include I2C, regmap, rational approximation, DT compatible `ti,cdce706`, optional `clk_in0` and `clk_in1` parent clocks, and CCF rate propagation via `CLK_SET_RATE_PARENT`. Risks include cached rate-selection state being shared between determine and set calls, invalid divider parent encodings, rate requests outside PLL VCO limits, and output parent mask handling. This snapshot shows duplicated source tokens around a register write/init initializer, so build coverage is a key signal. Tests should cover I2C read/write errors, OF clock index validation, input-source selection, PLL multiplier programming, divider reparenting, output enable/disable, and rate propagation from output to PLL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-cdce706.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-cdce925.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-cdce925.c

### Purpose
`clk-cdce925.c` supports the TI CDCE913/925/937/949 multi-PLL clock synthesizer family. It exposes chip-specific PLL and Y-output clocks and can configure output frequencies and spread-spectrum properties from device tree.

### Important APIs, Types, And Functions
`struct clk_cdce925_chip_info` records model-specific PLL/output counts. `struct clk_cdce925_chip` owns regmap and arrays of `clk_cdce925_pll` and `clk_cdce925_output`. PLL callbacks calculate and program N/M state with `cdce925_pll_find_rate()`, `cdce925_pll_prepare()`, and `cdce925_pll_unprepare()`. Output callbacks calculate p-dividers, program Y output divider registers, and activate or disable outputs. Custom `regmap_cdce925_bus` implements the device's I2C command protocol.

### Control Flow, State, And Persistence
Probe enables `vdd` and `vddout`, initializes a regcache-backed regmap, reads the parent crystal clock, applies optional `xtal-load-pf`, clears powerdown, registers PLL clocks, optionally applies child-node `clock-frequency` and spread-spectrum settings, registers Y1 as an input-clock child, registers other Y outputs as PLL children with `CLK_SET_RATE_PARENT`, and adds an OF provider. Runtime state is cached in each PLL's `m/n` and each output's `pdiv`; actual hardware programming happens mostly in prepare/unprepare because I2C operations can sleep.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include I2C transfers, regulator framework, regmap, DT compatibles for all four chip variants, a parent clock, and child node naming such as `PLL1`. Risks include first-come PLL rate allocation, cached `pdiv` not being persisted until prepare, no explicit provider removal in this file, register encoding edge cases for Q/R/P values, and different divider width for Y1 versus other outputs. This snapshot includes duplicated declarations/braces in visible source, so all variant build tests matter. Test signals include regulator failure paths, parent-clock absence, model-specific output counts, PLL bypass mode, PLL range rejection, output enable programming, OF output index lookup, spread-spectrum property writes, and I2C short-transfer handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-cdce925.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-clps711x.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-clps711x.c

### Purpose
`clk-clps711x.c` is an early OF clock provider for Cirrus CLPS711X/EP7209 systems. It derives fixed CPU, bus, PLL, timer, PWM, SPI, UART, and tick clocks from boot registers and exposes them through a onecell provider.

### Important APIs, Types, And Functions
The main entry point is `clps711x_clk_init_dt()`, registered via `CLK_OF_DECLARE()`. `struct clps711x_clk` holds a spinlock and flexible `clk_hw_onecell_data`. The file uses generic fixed-rate, fixed-factor, and divider-table helpers with `spi_div_table` and `timer_div_table`.

### Control Flow, State, And Persistence
Early init reads `startup-frequency`, maps the syscon region, computes PLL/CPU/bus/timer/SPI/PWM rates from `PLLR`, `SYSFLG2`, and `SYSCON` bits, programs timer mode bits in `SYSCON1`, registers all clocks, logs per-clock registration failures, and adds the onecell provider. State persists in hardware timer-mode bits and the registered static clock graph; there is no remove path because this is early boot infrastructure.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include OF address mapping, CLPS711X syscon bit definitions, fixed-rate/fixed-factor/divider CCF helpers, and clock IDs from `clps711x-clock.h`. Risks are `BUG_ON()` for mapping/allocation failure, limited recovery if individual clock registration fails, hard-coded oscillator frequencies, and early register mutation of timer modes. Test signals include EP7209 DT provider registration, correct CPU/bus rates in external-clock and PLL modes, timer1/timer2 divider behavior, SPI divider table selection, and no boot failure when optional startup frequency is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-clps711x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-composite.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-composite.c

### Purpose
`clk-composite.c` implements the reusable CCF composite clock wrapper that combines optional mux, rate, and gate subclocks into one logical clock.

### Important APIs, Types, And Functions
Public registration APIs are `clk_hw_register_composite()`, `clk_hw_register_composite_pdata()`, `clk_register_composite()`, `clk_register_composite_pdata()`, `clk_hw_unregister_composite()`, and `devm_clk_hw_register_composite_pdata()`. Internal callbacks forward parent selection, rate calculation, rate setting, gate state, and enable/disable to the subclock ops after setting each sub-HW's `clk` context.

### Control Flow, State, And Persistence
Registration allocates `struct clk_composite`, validates required sub-ops, builds a synthetic `clk_ops` table based on supplied subcomponents, registers the composite hardware, then points each child `clk_hw` at the composite's `struct clk`. `determine_rate()` either evaluates all mux parents and picks the closest rate through the rate component, honors `CLK_SET_RATE_NO_REPARENT`, or delegates to the rate or mux component alone. `set_rate_and_parent()` orders parent and rate changes based on temporary rate to reduce overshoot.

### Dependencies, Integration Points, Risks, And Test Signals
The file is a central integration point for SoC drivers that compose generic mux/divider/gate blocks. Risks include accepting inconsistent sub-op sets, ownership ambiguity because unregistering the composite only frees the wrapper and not caller-owned sub-HW allocations, and subtle rate-selection behavior when parents return errors. Test signals include mux-only, rate-only, gate-only, and full composite clocks; `CLK_SET_RATE_NO_REPARENT`; exact and closest parent selection; invalid ops rejection; devm release; and unregister paths not freeing caller-owned subcomponents unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-composite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-conf.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-conf.c

### Purpose
`clk-conf.c` applies standard device-tree assigned-clock defaults. It parses assigned clock parents and rates and programs them through the CCF during device/provider setup.

### Important APIs, Types, And Functions
The exported API is `of_clk_set_defaults(struct device_node *node, bool clk_supplier)`. Internals `__set_clk_parents()` and `__set_clk_rates()` parse `assigned-clock-parents`, `assigned-clocks`, `assigned-clock-rates`, and `assigned-clock-rates-u64`.

### Control Flow, State, And Persistence
`of_clk_set_defaults()` first reparents assigned clocks, then applies assigned rates. Each index resolves phandle arguments with `of_parse_phandle_with_args()`, skips empty phandles, obtains `struct clk` from providers, performs `clk_set_parent()` or `clk_set_rate()`, and drops clock references. If the node supplies one of the clocks and `clk_supplier` is false, the function exits early to avoid configuring a provider before it is ready. Persistent effects are the clock parent/rate changes in CCF and hardware provider state.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include OF phandle parsing, provider lookup, `clk_set_parent()`, `clk_set_rate()`, and the assigned-clock DT binding. Risks include mismatched array lengths, self-supplier deferral semantics, 32-bit versus 64-bit rate property precedence, and partial application if a later entry fails. Test signals include null phandle holes, `-EPROBE_DEFER` propagation, self-supplier behavior for both `clk_supplier` values, `assigned-clock-rates-u64`, and logs for failed reparent/rate programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-conf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-cs2000-cp.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-cs2000-cp.c

### Purpose
`clk-cs2000-cp.c` drives the Cirrus Logic CS2000-CP fractional-N clock synthesizer and clock multiplier. It exposes one programmable output clock sourced from either dynamic `clk_in` or static `ref_clk` mode.

### Important APIs, Types, And Functions
`struct cs2000_priv` stores CCF hardware, I2C client, `clk_in`, `ref_clk`, regmap, mode flags, ratio format, clock-skip setting, and suspend/resume rate state. Important helpers include `cs2000_rate_to_ratio()`, `cs2000_ratio_to_rate()`, `cs2000_ratio_set()`, `cs2000_ratio_select()`, `cs2000_select_ratio_mode()`, `cs2000_enable_dev_config()`, and `cs2000_wait_pll_lock()`. `cs2000_ops` implements parent reporting, recalc/determine/set rate, prepare, and unprepare.

### Control Flow, State, And Persistence
Probe allocates state, initializes regmap, obtains both parent clocks, registers the clock, checks chip revision, and unwinds provider/clock registration on revision failure. Registration parses `clock-output-names`, `cirrus,dynamic-mode`, `cirrus,aux-output-source`, and `cirrus,clock-skip`, bounds the reference clock divider, initializes static mode to 1:1, and adds an OF provider. Set-rate freezes global config, chooses 12.20 or 20.12 ratio mode, writes four ratio bytes for channel 0, selects ratio channel/mode, unfreezes, and saves rate state for late resume. Prepare enables device config and outputs, then polls PLL lock.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include I2C/regmap, two parent clocks, OF properties, CCF `CLK_SET_RATE_GATE`, and late system sleep resume. Risks include `dev_get_drvdata()` in resume relying on drvdata being set through I2C client data conventions, channel 0-only implementation, ratio format boundary mistakes, static/dynamic parent semantics, and timeout sensitivity while polling lock. Test signals include dynamic and static mode parent choice, ref-clock range validation, ratio round-trip math, PLL lock timeout, output disable on unprepare, revision rejection, resume reprogramming of saved ratio, and `-EPROBE_DEFER` for missing parents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-cs2000-cp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-devres.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-devres.c

### Purpose
`clk-devres.c` provides device-managed wrappers for clock get, prepare, enable, bulk get, bulk enable, and child-node clock lookup. It makes clock references unwind automatically on driver detach or probe failure.

### Important APIs, Types, And Functions
Core state is `struct devm_clk_state` with a `struct clk *` and optional exit callback, plus `struct clk_bulk_devres` for bulk arrays. Exported APIs include `devm_clk_get()`, prepared/enabled/optional variants, `devm_clk_get_optional_enabled_with_rate()`, `devm_clk_bulk_get()`, `devm_clk_bulk_get_optional()`, `devm_clk_bulk_get_optional_enable()`, `devm_clk_bulk_get_all()`, `devm_clk_bulk_get_all_enabled()`, `devm_clk_put()`, and `devm_get_clk_from_child()`.

### Control Flow, State, And Persistence
`__devm_clk_get()` allocates a devres record, obtains a clock with the supplied getter, optionally runs an init callback such as `clk_prepare()` or `clk_prepare_enable()`, then registers devres. Release invokes the stored exit callback and `clk_put()`. Bulk wrappers register release callbacks that put or disable-unprepare-put arrays. The optional-enabled-with-rate helper sets rate before prepare-enable and calls `devm_clk_put()` on failure. Persistence is only the devres list state associated with the device.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on driver-core devres, clock core references, bulk clock helpers, and OF child clock lookup. Risks include match/release mismatch in `devm_clk_put()` if resource layout differs, optional null clocks flowing into init/exit callbacks, set-rate-before-enable assumptions, and callers using bulk arrays after automatic release. Test signals include probe failure unwind, manual `devm_clk_put()`, optional missing clocks, enabled-with-rate failure at set-rate and prepare-enable stages, all-clock bulk allocation/free, and child-node named clock lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-devres.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-divider.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-divider.c

### Purpose
`clk-divider.c` implements generic adjustable divider clocks for CCF. It handles multiple hardware encodings, divider tables, rate rounding, read-only dividers, endian variants, shared-register locking, and managed registration.

### Important APIs, Types, And Functions
Exported helpers include `divider_recalc_rate()`, `divider_determine_rate()`, `divider_ro_determine_rate()`, `divider_get_val()`, `clk_divider_ops`, `clk_divider_ro_ops`, `__clk_hw_register_divider()`, `clk_register_divider_table()`, `clk_hw_unregister_divider()`, and `__devm_clk_hw_register_divider()`. Internal helpers translate between register values and dividers for one-based, power-of-two, max-at-zero, even-integer, and table-driven encodings.

### Control Flow, State, And Persistence
Recalc reads the register, extracts the field, converts it to a divider, and returns rounded-up parent/divider rate. Determine-rate chooses the best divider, optionally asking the parent to round to `target * divider` when `CLK_SET_RATE_PARENT` is set; read-only clocks use the current hardware divider. Set-rate converts the requested rate to a hardware value, takes the optional spinlock, updates the field or HIWORD mask, writes it back, and releases the lock. Persistent state is the hardware divider field and allocated `struct clk_divider`.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include MMIO accessors, CCF parent-rate negotiation, spinlocks, `clk_div_table`, and numerous `CLK_DIVIDER_*` flags used by SoC drivers. Risks include zero-divisor handling, invalid table entries, overflow in `rate * divider`, HIWORD mask field limits, read-only clocks still propagating parent-rate changes, and races when callers omit a lock for shared registers. Test signals include each divider encoding, closest versus up rounding, table min/max, `CLK_SET_RATE_PARENT`, big-endian MMIO, HIWORD mask writes, read-only determine-rate, unregister/devm release, and `CLK_DIVIDER_ALLOW_ZERO` warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-divider.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-en7523.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-en7523.c

### Purpose
`clk-en7523.c` provides clock and reset-controller support for Airoha/EcoNet EN7523, EN7581, and EN751221 SCU blocks. It exposes fixed-rate clocks computed from SCU strap/divider registers plus a PCIe reference clock gate and SoC-specific reset mappings.

### Important APIs, Types, And Functions
Clock descriptions use `struct en_clk_desc`, PCIe gates use `struct en_clk_gate`, reset state uses `struct en_rst_data`, and variant behavior is described by `struct en_clk_soc_data`. Important functions are `en7523_get_base_rate()`, `en7523_get_div()`, `en7523_register_clocks()`, `en7581_register_clocks()`, `en751221_register_clocks()`, `en7523_register_pcie_clk()`, PCIe prepare/enable callbacks, reset assert/deassert/status/xlate helpers, and `en7523_clk_probe()`.

### Control Flow, State, And Persistence
Probe selects variant match data, allocates onecell clock data, runs the variant `hw_init()`, then adds an OF provider. EN7523 maps two MMIO resources; EN7581 and EN751221 also lookup syscon regmaps. Base clocks are registered as fixed-rate clocks by reading base selectors and divider fields. PCIe clock registration may first disable/unprepare hardware, then later prepare/enable toggles refclk, PERST, and reset bits with documented delays. Reset registration maps DT reset IDs through per-SoC tables into bank/bit offsets and writes SCU reset registers.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include platform MMIO resources, syscon regmaps, reset-controller framework, DT clock/reset bindings for all variants, and early `arch_initcall()` registration. Risks include fixed-rate snapshots not tracking later SCU changes, direct PCIe reset sequencing in clock callbacks, sparse reset maps returning raw mapped IDs without sentinel validation, no provider cleanup path, and table/register drift across variants. This snapshot contains duplicated statements in a few helper/table areas, making compile tests important. Test signals include OF provider resolution, correct rates from straps/dividers, PCIe refclk/perst sequencing, reset assert/deassert/status for all banks, syscon lookup failure handling, EN751221 hardware-ID-dependent SPI rate, and boot ordering before PCIe consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-en7523.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-ep93xx.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-ep93xx.c

### Purpose
`clk-ep93xx.c` implements clock control for Cirrus EP93xx SoCs using an auxiliary device supplied by the EP93xx syscon/regmap layer. It registers fixed PLL-derived clocks, UART/DMA/USB gates, SPI/PWM clocks, touchscreen/keypad dividers, and video/I2S mux-divider chains.

### Important APIs, Types, And Functions
`struct ep93xx_clk_priv` owns the syscon map, base, auxiliary write hook, spinlock, fixed clock array, and flexible array of register-backed clocks. `struct ep93xx_clk` stores register, enable bit, divider/mux fields, and divisor tables. Important functions include `calc_pll_rate()`, `ep93xx_plls_init()`, gate ops, mux/double-divider ops, generic small-divider ops, `ep93xx_uart_clock_init()`, `ep93xx_dma_clock_init()`, `of_clk_ep93xx_get()`, and `ep93xx_clk_probe()`.

### Control Flow, State, And Persistence
Probe allocates private state, initializes PLL1/PLL2 fixed rates from bootloader-programmed registers, registers derived FCLK/HCLK/PCLK, USB, UART, DMA, SPI, and PWM clocks, enables sane video/I2S divider defaults, registers video and I2S MCLK/SCLK/LRCLK clocks, then adds an OF provider. Register writes are serialized through a local spinlock and the auxiliary syscon write callback. Persistent state is hardware enable/divider/mux bits and registered clock hardware; devm manages most clock registrations.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include auxiliary bus IDs, EP93xx syscon regmap/write-lock API, DT clock IDs, fixed-factor/gate/divider CCF helpers, and external 14.7456 MHz/32.768 kHz assumptions. Risks include missed error handling after several registration calls in probe, video/I2S register mutation during probe, mux-rate search edge cases, DMA gates using direct generic gate helpers while other gates use syscon writes, and source snapshot duplicated declarations/returns. Test signals include auxiliary ID variants with different SPI dividers, PLL bypass/enabled states, UART baud divisor selection, DMA gate toggling, USB gate enable, video/I2S rate changes and parent selection, OF index validation, and syscon write locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-ep93xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-eyeq.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-eyeq.c

### Purpose
`clk-eyeq.c` is the Mobileye EyeQ5/EyeQ6 clock provider for OLB regions. It exposes read-only PLLs as fixed-factor clocks, divider clocks, fixed-factor child clocks, and optional auxiliary reset/pinctrl/PHY devices, with special early providers for clocks required before normal platform probing.

### Important APIs, Types, And Functions
Data tables use `struct eqc_pll`, `struct eqc_div`, `struct eqc_fixed_factor`, `struct eqc_match_data`, and `struct eqc_early_match_data`. Important logic includes `eqc_pll_parse_registers()` for PLL register decoding and spread-spectrum accuracy, `eqc_pll_downshift_factors()` for fixed-factor width limits, `eqc_probe_init_plls()`, `eqc_probe_init_divs()`, `eqc_probe_init_fixed_factors()`, `eqc_auxdev_create_optional()`, `eqc_probe()`, and `eqc_early_init()`.

### Control Flow, State, And Persistence
Late probe ioremaps the OLB resource, creates optional auxiliary devices, allocates onecell data, marks early-owned clocks as errors, registers late PLLs/dividers/fixed factors, and adds an OF provider. Early init allocates a larger onecell array, marks not-yet-late clocks as `-EPROBE_DEFER`, maps OLB, registers boot-critical PLLs and child fixed factors, and installs a provider through `CLK_OF_DECLARE_DRIVER()`. PLLs are read-only snapshots of hardware state; dividers read hardware fields through generic divider registration. State persists as registered clock providers and auxiliary devices using the mapped OLB base.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include OF address mapping, 64-bit non-atomic register reads, CCF fixed-factor/divider helpers, auxiliary bus creation, EyeQ DT bindings, and ordering between early and late providers. Risks include no unmap/free path for late `ioremap()` and `kzalloc_flex()` allocations, early-provider precedence subtleties, failure to parse unlocked PLLs, precision loss while downshifting large fractional factors, and source snapshot syntax anomalies near one EyeQ6H match table. Test signals include early boot clocks for timer/UART, late provider override behavior, PLL bypass/locked/fractional/spread-spectrum decoding, deferred lookup for late clocks, divider parent fallback to early provider, auxiliary device creation, and all compatible variants building.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-eyeq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-fixed-factor.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-fixed-factor.c

### Purpose
`clk-fixed-factor.c` implements fixed multiplier/divider clocks. These clocks cannot gate or reparent, but derive their rate from one parent using `parent_rate / div * mult`, optionally reporting fixed accuracy.

### Important APIs, Types, And Functions
The exported `clk_fixed_factor_ops` implements recalc, determine, set-rate no-op, and accuracy. Registration APIs include parent-name, parent-HW, firmware-name, parent-index, accuracy, and devm variants such as `clk_hw_register_fixed_factor()`, `clk_hw_register_fixed_factor_index()`, `clk_hw_register_fixed_factor_fwname()`, `devm_clk_hw_register_fixed_factor()`, and unregister helpers. OF support is provided by `_of_fixed_factor_clk_setup()`, `of_fixed_factor_clk_setup()`, and a builtin platform driver for `fixed-factor-clock`.

### Control Flow, State, And Persistence
Registration allocates `struct clk_fixed_factor`, fills `clk_init_data` with exactly one parent, stores `mult`, `div`, `acc`, and flags, then registers with either device or OF clock registration. Determine-rate optionally asks the parent to round when `CLK_SET_RATE_PARENT` is set, then computes the resulting fixed-factor output. OF setup reads `clock-div`, `clock-mult`, and `clock-output-names`, registers a provider, and clears `OF_POPULATED` if early registration fails so platform probe can retry.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include CCF parent data, OF fixed-factor binding, devres, and integer arithmetic with `do_div()`. Risks include division by zero if invalid DT or caller data passes `div=0`, fixed-factor `set_rate()` reporting success as a no-op, parent lookup ambiguity across name/HW/fw_name/index variants, and double-free avoidance in devm release paths. This source snapshot shows a duplicated brace around `clk_register_fixed_factor()`, so compile coverage is a signal. Tests should cover OF retry, devm and unmanaged unregister, `CLK_SET_RATE_PARENT`, fixed accuracy versus parent accuracy, parent-data variants, and invalid DT properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-fixed-factor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-fixed-mmio.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-fixed-mmio.c

### Purpose
`clk-fixed-mmio.c` provides a simple fixed-rate clock whose frequency is read from a memory-mapped register at registration time.

### Important APIs, Types, And Functions
The main helper is `fixed_mmio_clk_setup()`. It is used by early `of_fixed_mmio_clk_setup()` registered with `CLK_OF_DECLARE()` and by the fallback platform driver probe for compatible `fixed-mmio-clock`.

### Control Flow, State, And Persistence
Setup maps the first OF resource with `of_iomap()`, reads a 32-bit frequency, immediately unmaps the resource, optionally reads `clock-output-names`, registers a fixed-rate clock, and adds an OF provider. Platform probe runs only if early setup did not succeed and stores the `clk_hw` for remove. Remove deletes the provider and unregisters the fixed-rate clock. The clock is a snapshot of the register value; later MMIO changes are not tracked.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include OF address mapping, fixed-rate CCF registration, platform-driver fallback, and `fixed-mmio-clock` binding. Risks include assuming a 32-bit little-endian register, no cleanup if fixed-rate registration fails after mapping is already unmapped but before provider install, early setup lacking remove, and snapshot staleness. Test signals include early and platform probe paths, mapping failure, output-name override, provider lookup, register-frequency correctness, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-fixed-mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-fixed-rate.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-fixed-rate.c

### Purpose
`clk-fixed-rate.c` implements the basic fixed-rate CCF clock. It exposes clocks whose rate is constant and independent of parent rate, with optional fixed or parent-derived accuracy.

### Important APIs, Types, And Functions
`clk_fixed_rate_ops` provides `recalc_rate` and `recalc_accuracy`. The core API is `__clk_hw_register_fixed_rate()`, with wrappers such as `clk_register_fixed_rate()`, `clk_hw_register_fixed_rate_with_accuracy()` through header macros, `clk_unregister_fixed_rate()`, and `clk_hw_unregister_fixed_rate()`. OF setup uses `_of_fixed_clk_setup()`, `of_fixed_clk_setup()`, and a builtin platform driver for `fixed-clock`.

### Control Flow, State, And Persistence
Registration allocates `struct clk_fixed_rate`, configures optional parent by name, HW, or parent data, stores fixed rate/accuracy/flags, and registers through device or OF APIs. Devm registration stores the object as devres and releases by unregistering only the HW, leaving devres to free memory. OF setup reads `clock-frequency`, optional `clock-accuracy`, and `clock-output-names`, registers the clock, and adds a simple OF provider. The only persistent behavior is the registered fixed value and optional accuracy mode.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include OF fixed-clock binding, CCF registration, devres, and optional parent data. Risks include `clock-frequency` being limited to u32 in OF setup, parent accuracy behavior depending on `CLK_FIXED_RATE_PARENT_ACCURACY`, provider duplication between early setup and platform probe, and unregister path ownership differences between devm and unmanaged clocks. Test signals include fixed rate retrieval, fixed accuracy retrieval, parent ignored for rate, parent-derived accuracy mode, OF overlay provider registration, missing `clock-frequency`, and platform fallback/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-fixed-rate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-fixed-rate_test.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-fixed-rate_test.c

### Purpose
`clk-fixed-rate_test.c` is a KUnit test module for the fixed-rate clock implementation and its OF registration path.

### Important APIs, Types, And Functions
The test helper `struct clk_hw_fixed_rate_kunit_params` mirrors `__clk_hw_register_fixed_rate()` arguments. Resource helpers `clk_hw_register_fixed_rate_kunit()` and `clk_hw_unregister_fixed_rate_kunit()` manage test clock lifetime. Test cases cover basic rate, fixed accuracy, parent lookup, parent-rate independence, parent-accuracy independence, and OF fixed-clock overlay behavior.

### Control Flow, State, And Persistence
KUnit tests allocate/register clocks as test resources, get temporary `struct clk` handles through KUnit CCF helpers, assert rates/accuracy/parent relationships, and automatically unregister on test cleanup. The OF suite applies `kunit_clk_fixed_rate_test`, registers a temporary consumer platform driver, waits for probe completion, then obtains the fixed clock from that consumer device.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include KUnit, KUnit clock helpers, KUnit OF overlay support, KUnit platform-driver helpers, `clk-fixed-rate_test.h`, and the fixed-clock implementation under test. Risks are test isolation across global clock names, overlay/provider cleanup correctness, timeout sensitivity waiting for probe, and helper correctness masking lifecycle bugs. Direct test signals are suites named `clk_fixed_rate`, `clk_fixed_rate_parent`, and `clk_fixed_rate_of`, including assertions for `TEST_FIXED_FREQUENCY` and `TEST_FIXED_ACCURACY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-fixed-rate_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-fixed-rate_test.h -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-fixed-rate_test.h

### Purpose
`clk-fixed-rate_test.h` provides shared constants for the fixed-rate KUnit overlay tests.

### Important APIs, Types, And Functions
It defines `TEST_FIXED_FREQUENCY` as `50000000` and `TEST_FIXED_ACCURACY` as `300`. There are no functions or data structures.

### Control Flow, State, And Persistence
The header has no runtime control flow or persistent state. Its values are compiled into the KUnit test and must match the test device-tree overlay referenced by `clk-fixed-rate_test.c`.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends on inclusion by `clk-fixed-rate_test.c` and the overlay generated for `kunit_clk_fixed_rate_test`. Risks are simple drift between constants and overlay data or accidental include-guard mismatch. Test signals are the OF fixed-rate KUnit assertions that compare `clk_get_rate()` and `clk_get_accuracy()` to these constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-fixed-rate_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-fractional-divider.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-fractional-divider.c

### Purpose
`clk-fractional-divider.c` implements generic adjustable fractional divider clocks where output rate is `(m / n) * parent_rate`. It supports rational approximation, zero-based fields, big-endian registers, optional power-of-two prescaler adjustment, debugfs inspection, and unmanaged registration.

### Important APIs, Types, And Functions
The main exported symbols are `clk_fractional_divider_general_approximation()`, `clk_fractional_divider_ops`, `clk_hw_register_fractional_divider()`, `clk_register_fractional_divider()`, and `clk_hw_unregister_fractional_divider()`. Internal helpers `clk_fd_get_div()`, `clk_fd_recalc_rate()`, `clk_fd_determine_rate()`, and `clk_fd_set_rate()` perform register extraction, rational approximation, and field updates.

### Control Flow, State, And Persistence
Recalc reads the register under the optional lock, extracts numerator and denominator fields, adjusts zero-based encodings, and returns parent rate when either field is zero. Determine-rate returns the parent rate for zero or above-parent requests when the parent cannot change; otherwise it calls a custom approximation hook or the generic rational approximation and writes the approximated output into the request. Set-rate computes `m/n`, adjusts zero-based hardware values, masks both fields, updates the register under lock, and persists the new ratio in hardware.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include CCF `struct clk_fractional_divider`, `linux/rational.h`, MMIO, spinlocks, debugfs, and flags such as `CLK_FRAC_DIVIDER_ZERO_BASED`, `BIG_ENDIAN`, and `POWER_OF_TWO_PS`. Risks include division by zero if requested rate is zero inside prescaler scaling paths, overflow/precision limits in rational approximation, unsupported managed registration, and debugfs exposing stale values during concurrent writes. This snapshot has a duplicated `.determine_rate` initializer, a compile-style signal. Tests should cover max numerator/denominator, zero-based fields, big-endian MMIO, locked and unlocked shared registers, power-of-two prescaler scaling, debugfs numerator/denominator, and unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-fractional-divider.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-fractional-divider.h -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-fractional-divider.h

### Purpose
`clk-fractional-divider.h` is the local interface for the fractional-divider implementation and its KUnit tests.

### Important APIs, Types, And Functions
It forward-declares `struct clk_hw`, declares `extern const struct clk_ops clk_fractional_divider_ops`, and declares `clk_fractional_divider_general_approximation()`.

### Control Flow, State, And Persistence
The header has no runtime behavior or state. It exposes the approximation function so tests can validate the helper directly without registering a real clock.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies are CCF type declarations from including C files and consistency with `clk-fractional-divider.c`. Risks are prototype drift and exposing only the approximation helper, leaving register set/recalc paths to require integration tests. Test signals are successful build of both implementation and `clk-fractional-divider_test.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-fractional-divider.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-fractional-divider_test.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-fractional-divider_test.c

### Purpose
`clk-fractional-divider_test.c` contains KUnit tests for the fractional divider's generic rational approximation helper.

### Important APIs, Types, And Functions
The suite `clk-fd-approximation` includes `clk_fd_test_approximation_max_denominator()`, `clk_fd_test_approximation_max_numerator()`, `clk_fd_test_approximation_max_denominator_zero_based()`, and `clk_fd_test_approximation_max_numerator_zero_based()`. Each allocates a `struct clk_fractional_divider`, sets field widths and flags, invokes `clk_fractional_divider_general_approximation()`, and checks selected `m/n` values.

### Control Flow, State, And Persistence
Each test uses `kunit_kzalloc()` for isolated clock state, sets 3-bit numerator/denominator fields, chooses parent/request rates that exceed one side of the representable ratio, and verifies the helper saturates to the expected maximum numerator or denominator. There is no persistent state outside KUnit-managed allocations.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include KUnit, CCF fractional divider types, and the local header. Risks are narrow coverage: tests validate approximation limits but not register read/write, locking, debugfs, big-endian access, or power-of-two prescaler behavior. Test signals are the four expectation pairs: non-zero-based max denominator `n=7`, non-zero-based max numerator `m=7`, zero-based max denominator `n=8`, and zero-based max numerator `m=8`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-fractional-divider_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-fsl-flexspi.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-fsl-flexspi.c

### Purpose
`clk-fsl-flexspi.c` provides a divider-table clock for Layerscape FlexSPI controllers. It exposes the FlexSPI clock divider register as a CCF clock provider for LS1028A and LX2160A variants.

### Important APIs, Types, And Functions
Variant tables `ls1028a_flexspi_divs` and `lx2160a_flexspi_divs` map hardware field values to supported dividers. The only probe path is `fsl_flexspi_clk_probe()`, which registers a `devm_clk_hw_register_divider_table()` clock and `devm_of_clk_add_hw_provider()`.

### Control Flow, State, And Persistence
Probe obtains the variant table from OF match data, maps the first resource with `devm_ioremap()` rather than claiming it, obtains parent clock name from DT index 0, applies optional `clock-output-names`, registers a 5-bit divider at shift 0, and installs a simple provider. Persistent state is the hardware divider field and the devm-managed clock registration.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include platform resources that may be shared with a parent device, OF parent clock, divider-table CCF helper, and compatible strings `fsl,ls1028a-flexspi-clk` and `fsl,lx2160a-flexspi-clk`. Risks include shared MMIO lifetime with parent devices, no explicit spinlock for shared register protection, parent-clock absence, and table differences where LS1028A accepts divider 1 but LX2160A starts at divider 2. Test signals include probe on both compatibles, divider table round/set behavior, shared-resource mapping, provider lookup by FlexSPI consumers, and failure paths for missing resource/parent/table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-fsl-flexspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-fsl-sai.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-fsl-sai.c

### Purpose
`clk-fsl-sai.c` exposes Freescale/NXP SAI bit clock, and on i.MX8MQ also MCLK, as generic CCF composite clocks backed by SAI divider and gate registers.

### Important APIs, Types, And Functions
`struct fsl_sai_data` records the register offset and whether MCLK exists. `struct fsl_sai_clk` stores divider/gate subcomponents, registered clock HW pointers, and a shared spinlock. Important functions are `fsl_sai_of_clk_get()`, `fsl_sai_clk_register()`, and `fsl_sai_clk_probe()`. Variant data supports `fsl,vf610-sai-clock` and `fsl,imx8mq-sai-clock`.

### Control Flow, State, And Persistence
Probe allocates state, maps the SAI resource, optionally enables a `bus` clock with devm, initializes the spinlock, registers BCLK as a composite of divider and gate, conditionally registers MCLK, then installs a custom OF provider that returns BCLK for no args or arg 0 and MCLK for arg 1 when supported. Registration writes a direction bit to the divider/control register, builds a full OF-node-derived clock name, and registers a rate-gated composite using `clk_divider_ops` and `clk_gate_ops`. Persistent state is SAI gate/divider/direction register state.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include SAI MMIO layout, optional bus clock, CCF composite/divider/gate helpers, OF clock specifier conventions, and variant-specific offset differences. Risks include writing `dir_bit` as a whole register value rather than read-modify-write, no validation of parent clock existence beyond parent-data index, shared register races if external SAI driver manipulates the same registers, and MCLK access on variants without MCLK. Test signals include BCLK-only VF610 behavior, BCLK/MCLK i.MX8MQ behavior, OF arg validation, divider rate changes under `CLK_SET_RATE_GATE`, gate enable/disable, optional bus-clock failure, and register direction programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-fsl-sai.c -->
