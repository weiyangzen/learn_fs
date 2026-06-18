# subset-b-001182 research

This grouped report covers the requested Sunxi and Tegra clock-provider files. Each section preserves the source path and is wrapped for downstream reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun4i-tcon-ch1.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun4i-tcon-ch1.c

## Purpose

Implements the Allwinner sun4i TCON channel 1 clock as a custom Common Clock Framework provider. The hardware uses one register to gate two serial clock paths, select one of four SCLK2 parents, and divide/halve the selected rate for LCD/TV timing.

## APIs, Types, And Control Flow

The private `struct tcon_ch1_clk` embeds `struct clk_hw`, a per-clock spinlock, and the mapped register. `tcon_ch1_ops` provides gate operations, parent mux operations, `determine_rate`, `recalc_rate`, and `set_rate`. `tcon_ch1_calc_divider()` searches divider `m` 1..15 and a 1x/2x half divider for the closest rate not above the request. `tcon_ch1_determine_rate()` evaluates every parent, records `best_parent_hw` and `best_parent_rate`, and writes the rounded request rate. `tcon_ch1_setup()` maps the DT resource, reads four parents and optional `clock-output-names`, allocates/registers the clock, and publishes it through `of_clk_add_provider()`.

## State And Persistence

Persistent state is the hardware register contents and the registered clock provider. Register writes are protected by the instance spinlock. The driver has no remove path because it is installed by `CLK_OF_DECLARE()` during early boot.

## Dependencies And Integration Points

Depends on OF address mapping, `clk_register()`, parent names from DT, `CLK_SET_RATE_PARENT`, and the CCF `clk_hw` API. Consumers see a single OF clock provider for compatible `allwinner,sun4i-a10-tcon-ch1-clk`.

## Risks And Test Signals

Parent selection and divider bitfields are the main risk. `tcon_ch1_get_parent()` uses `reg &= reg >> TCON_CH1_SCLK2_MUX_MASK`, which looks suspicious because mux extraction normally masks with `TCON_CH1_SCLK2_MUX_MASK`; this is a high-value review/test target. Enable state returns any gate bit rather than requiring both, so mixed hardware state may appear enabled. Test signals include DT clock lookup, parent switching, display mode rate changes, register readback, and boot logs for mapping/provider failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun4i-tcon-ch1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun6i-apb0-gates.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun6i-apb0-gates.c

## Purpose

Registers APB0 gate clocks for Allwinner A31 and A23 style PRCM clock blocks. It exposes onecell clock outputs at sparse bit positions selected by SoC-specific masks.

## APIs, Types, And Control Flow

`struct gates_data` stores a 32-bit bitmap of valid gate bits. The OF match table binds A31 to mask `0x7f` and A23 to `0x5d`. `sun6i_a31_apb0_gates_clk_probe()` validates OF data, maps the register, gets the single parent name, allocates `clk_onecell_data`, sizes the clock array to the last set bit, then iterates `for_each_set_bit()` to read each `clock-output-names` entry and call `clk_register_gate()`.

## State And Persistence

State lives in the APB0 gate register and in devm-managed provider allocations. Registered clocks are indexed by hardware bit number, leaving holes for unsupported bits. There is no explicit remove path for the built-in platform driver.

## Dependencies And Integration Points

Depends on platform-device probing, OF match data, `devm_platform_ioremap_resource()`, `clk_register_gate()`, and `of_clk_src_onecell_get`. Consumers rely on DT clock specifier indices matching gate bit positions.

## Risks And Test Signals

The driver warns but continues if an individual gate registration fails, so consumers may later receive error pointers or NULL holes. Missing `clock-output-names` entries are not checked per gate. Test signals are provider registration success, correct `clk_num`, expected gate bits toggling in PRCM registers, and peripheral probe success for APB0 consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun6i-apb0-gates.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun6i-apb0.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun6i-apb0.c

## Purpose

Provides the Allwinner A31 APB0 divider clock. APB0 has a two-bit divider field whose first two encodings both mean divide-by-2, so it cannot use a plain power-of-two divider.

## APIs, Types, And Control Flow

`sun6i_a31_apb0_divs` maps register values 0 and 1 to divisor 2, value 2 to 4, and value 3 to 8. `sun6i_a31_apb0_clk_probe()` maps the register, obtains the first parent name, reads an optional output name, registers a divider-table clock with `clk_register_divider_table()`, and adds a simple OF provider.

## State And Persistence

Persistent state is the two-bit divider field in the mapped APB0 register. Allocations and mappings are devm-managed, while the registered CCF clock persists for the built-in platform driver's lifetime.

## Dependencies And Integration Points

Uses platform-device probing, OF clock parent naming, CCF divider-table helpers, and compatible `allwinner,sun6i-a31-apb0-clk`. APB0 gate drivers and low-power peripherals consume this clock as their parent.

## Risks And Test Signals

The DT node must have a parent and valid resource. The non-linear divider table is the important correctness contract. Test signals include reading the rounded APB0 rate for each encoding, peripheral bus stability after rate changes, and absence of `-EINVAL`/`PTR_ERR` probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun6i-apb0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun6i-ar100.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun6i-ar100.c

## Purpose

Registers the Allwinner A31 AR100 clock through the shared Sunxi factors framework. AR100 is a divide-only clock with parent muxing and two factors: preshift `p` and divider `m`.

## APIs, Types, And Control Flow

`sun6i_get_ar100_factors()` clamps requests above the parent, computes a total divisor, chooses `p` so the remaining `m + 1` divider fits in five bits, clamps maximum divisor to 32, and returns the achieved rate. `sun6i_ar100_config` maps `m` to bits 12:8 and `p` to bits 5:4. `sun6i_ar100_data` adds a mux at bit 16 with two-bit mask. Probe maps the resource, calls `sunxi_factors_register()`, and stores the resulting clock in platform data.

## State And Persistence

State is contained in the AR100 clock register and protected by a static spinlock shared for this clock. There is no dynamic teardown because this is a built-in clock driver.

## Dependencies And Integration Points

Depends on `clk-factors.h`, platform resources, OF compatible `allwinner,sun6i-a31-ar100-clk`, and the Sunxi factors registration helper. Consumers are firmware/PRCM-side AR100 users.

## Risks And Test Signals

Divider selection must respect the hardware field widths and divide-only semantics. Very low requested rates collapse to the maximum divisor. Test signals include `clk_round_rate()`/`clk_set_rate()` for boundary rates, parent mux selection, and boot-time probe on A31 DTs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun6i-ar100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun8i-apb0.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun8i-apb0.c

## Purpose

Provides the Allwinner A23 APB0 divider clock for both early OF clock declaration and platform-device probing. Unlike A31, the A23 APB0 clock is a standard two-bit divider.

## APIs, Types, And Control Flow

`sun8i_a23_apb0_register()` reads the first parent and optional output name, registers `clk_register_divider()` over bits 1:0, and adds a simple OF provider. `sun8i_a23_apb0_setup()` maps early resources with `of_io_request_and_map()` for `CLK_OF_DECLARE_DRIVER()`, while `sun8i_a23_apb0_clk_probe()` uses devm platform mapping and reuses the same registration helper.

## State And Persistence

The hardware divider field persists in the PRCM register. The early setup path manually releases mappings on error; the platform path uses devm mapping but still registers a non-devm CCF divider.

## Dependencies And Integration Points

Integrates with OF early clock init, platform-device fallback, `of_clk_add_provider()`, and compatible `allwinner,sun8i-a23-apb0-clk`.

## Risks And Test Signals

The dual init path can duplicate provider registration if DT/platform population is wrong. The early path intentionally suppresses the common `-EINVAL` mapping error for MFD-instantiated nodes. Test signals include successful APB0 clock resolution in both early and MFD paths and correct divider readback for all two-bit values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun8i-apb0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun8i-bus-gates.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun8i-bus-gates.c

## Purpose

Registers Sun8i H3/A83T bus gate clocks whose parent depends on the clock index range. It maps DT `clock-indices` into sparse onecell outputs and chooses AHB1, AHB2, APB1, or APB2 parents.

## APIs, Types, And Control Flow

`sun8i_h3_bus_gates_init()` maps the gate register block, resolves the four named parents from `clock-names`, allocates a `clk_onecell_data` sized to the largest listed index, iterates each `clock-indices` value, reads the corresponding output name, selects the parent by index ranges/special cases, computes register word and bit, and registers each gate with a shared spinlock. Two `CLK_OF_DECLARE()` entries bind H3 and A83T compatibles to the same setup.

## State And Persistence

Gate state persists in the bus gate registers. Provider arrays are sparse and indexed by DT clock IDs. There is no teardown for early OF registration.

## Dependencies And Integration Points

Depends on DT properties `clock-names`, `clock-indices`, and `clock-output-names`; CCF gate helpers; and OF onecell lookup. Downstream bus/peripheral clocks rely on the index-to-parent routing policy.

## Risks And Test Signals

Several early returns after mapping do not release the mapping, which is tolerable during boot but risky for error hygiene. Wrong index ranges silently assign the wrong bus parent. Test signals include each gate's parent name, enable bit toggling in the correct 32-bit bank, and peripheral probes across AHB/APB domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun8i-bus-gates.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun8i-mbus.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun8i-mbus.c

## Purpose

Builds the Allwinner A23 MBUS composite clock, combining mux, divider, and gate components into one critical memory-bus clock.

## APIs, Types, And Control Flow

`sun8i_a23_mbus_setup()` counts parents, allocates a parent-name array, maps the register, allocates `clk_divider`, `clk_mux`, and `clk_gate`, fills component bitfields, and calls `clk_register_composite()` with `CLK_IS_CRITICAL`. The mux uses bits 25:24, the divider uses bits 2:0, and the gate uses bit 31. It then registers a simple OF provider.

## State And Persistence

The selected parent, divider, and gate bit persist in one hardware register. The clock is critical, so the CCF should not disable it as unused. The parent-name array is freed after registration because CCF deep-copies it.

## Dependencies And Integration Points

Uses CCF composite helpers, OF parent fill, early `CLK_OF_DECLARE`, and shared spinlock protection. It supplies the MBUS clock to memory/display/DMA consumers that cannot tolerate accidental gating.

## Risks And Test Signals

The error path notes that composite registration may leak subcomponents after unregister. Parent count is not capped against the unused `SUN8I_MBUS_MAX_PARENTS` define. Test signals include boot survival with unused-clock disabling enabled, parent/divider readback, and memory/display traffic stability under rate changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun8i-mbus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun9i-core.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun9i-core.c

## Purpose

Provides factor-clock definitions for Allwinner A80 core clocks: PLL4, GT bus, AHB0/1/2, APB0, and APB1. Each is registered through the shared Sunxi factors framework.

## APIs, Types, And Control Flow

`sun9i_a80_get_pll4_factors()` normalizes PLL4 to 6/12/24 MHz steps and selects `n`, `m`, and `p`. `sun9i_a80_get_gt_factors()` implements a simple divide-by-1..4 path. `sun9i_a80_get_ahb_factors()` selects a power-of-two `p` divider. `sun9i_a80_get_apb1_factors()` attempts an `m,p` divider for APB1. Each clock has a `clk_factors_config`, `factors_data`, spinlock, setup function, and `CLK_OF_DECLARE()` compatible.

## State And Persistence

Each clock's mux/factor/enable state persists in its mapped register. The GT bus clock is registered as critical through `sunxi_factors_register_critical()` so it remains enabled.

## Dependencies And Integration Points

Depends on `clk-factors.h`, `order_base_2()`, OF early registration, and A80 DT compatibles such as `allwinner,sun9i-a80-pll4-clk` and `allwinner,sun9i-a80-apb1-clk`.

## Risks And Test Signals

Factor math is the primary risk because invalid `m/p/n` values directly corrupt bus rates. The APB1 helper's `req->m = (req->parent_rate >> req->p) - 1` is worth targeted review because it appears to omit division by the requested divisor and can exceed the five-bit field. Test signals include rate-rounding for low/high boundaries, boot-critical bus stability, and CCF summaries matching the A80 manual.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun9i-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun9i-cpus.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun9i-cpus.c

## Purpose

Implements the Allwinner A80 CPUS composite clock. It combines a parent mux with a custom divider block that has an additional PLL4 predivider when PLL4 is selected.

## APIs, Types, And Control Flow

`struct sun9i_a80_cpus_clk` stores `clk_hw` and the mapped register. `sun9i_a80_cpus_clk_recalc_rate()` reads the mux, applies the PLL4 predivider if parent index 3 is selected, and then applies the main divider. `sun9i_a80_cpus_clk_round()` chooses main divider and optional PLL4 predivider. `determine_rate` evaluates each parent, optionally asking parents to round if `CLK_SET_RATE_PARENT` is present, and picks the fastest child rate not exceeding the request. `set_rate` writes divider fields under a static spinlock. Setup creates a composite clock with standard mux ops and custom rate ops.

## State And Persistence

Mux and divider fields persist in the CPUS register. The global spinlock serializes mux/divider updates because the mux and divider share a register.

## Dependencies And Integration Points

Uses OF early registration, `clk_register_composite()`, `clk_mux_ops`, and the CCF rate-request API. It is exposed for compatible `allwinner,sun9i-a80-cpus-clk`.

## Risks And Test Signals

The PLL4 predivider path is sensitive to parent index ordering in DT. `sun9i_a80_cpus_clk_round()` initializes `pre_div` as 1 but returns `pre_div - 1` for programming, so tests should cover non-PLL4 and PLL4 parents. Test signals include parent switching, requested rates across divider thresholds, and CPUS consumers retaining stable operation after set-rate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun9i-cpus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun9i-mmc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun9i-mmc.c

## Purpose

Registers Allwinner A80 MMC configuration clocks and a matching reset controller. The hardware exposes one 32-bit word per MMC channel, with a gate bit and reset bit in each word.

## APIs, Types, And Control Flow

`struct sun9i_mmc_clk_data` owns the mapped base, parent clock, upstream reset, onecell clock data, reset controller, and spinlock. Reset ops assert/deassert bit 18 for each ID while temporarily enabling the parent clock. `sun9i_a80_mmc_config_clk_probe()` maps the resource, derives channel count from resource size divided by four, gets and deasserts the parent reset, registers one gate clock per word at bit 16, publishes an OF onecell provider, then registers reset-controller ops.

## State And Persistence

Per-channel gate and reset bits persist in MMIO. The parent reset is deasserted during probe and reasserted only on probe error. The reset controller and clock provider persist for the built-in driver's lifetime.

## Dependencies And Integration Points

Depends on platform resources, reset framework, CCF gates, `devm_clk_get()`, and OF reset-controller registration. MMC host drivers consume both the clock outputs and reset IDs.

## Risks And Test Signals

Error cleanup unregisters `count` entries even if only a prefix was successfully registered, so sparse failure handling should be tested. Reset ops ignore `clk_prepare_enable()` failures. Test signals include MMC probe/reset behavior, gate bit toggling per channel, reset pulse timing, and provider/reset-controller registration in DT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sun9i-mmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sunxi.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sunxi.c

## Purpose

Central legacy Sunxi clock-registration file for many Allwinner SoCs. It defines factor calculators, mux/divider setup helpers, and multi-output PLL divider registration used by older DT compatibles.

## APIs, Types, And Control Flow

The file groups several patterns. Factor calculators derive `n/k/m/p` for PLL1, PLL5/6, AHB, APB1, CLK_OUT, and display clocks, then pass `factors_data` to `sunxi_factors_register()`. `sunxi_mux_clk_setup()` registers simple mux clocks with optional critical flag. `sunxi_divider_clk_setup()` registers divider-table clocks and adds clkdev aliases. `sunxi_divs_clk_setup()` first registers a base factor PLL, derives or reads its name, then registers up to four leaf outputs as fixed-factor or divider composite clocks, optionally with gates and critical flags. Many setup functions are connected with `CLK_OF_DECLARE()`.

## State And Persistence

State persists in clock control registers mapped by OF. A single global `clk_lock` serializes shared register updates. Early-boot registrations have no remove path; some helper-allocated subcomponents are intentionally long-lived.

## Dependencies And Integration Points

Depends on `clk-factors.h`, CCF mux/divider/fixed-factor/composite/gate helpers, OF clock providers, clkdev aliases, and many Allwinner compatible strings. It supplies root PLLs and bus clocks used by the rest of the Sunxi clock tree.

## Risks And Test Signals

The file is dense with SoC-specific arithmetic, so boundary rates and field widths are the main risk. Error paths sometimes leak mappings or helper allocations after partial registration, typical for early boot but still relevant for static analysis. `sunxi_divs_clk_setup()` has complex name derivation and parent propagation rules; PLL5 DDR is intentionally protected from automatic reparenting. Test signals include CCF rate summaries across supported SoCs, boot with unused-clock disabling, DT compatible coverage, and set/round/recalc consistency for each factor table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-sunxi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-usb.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-usb.c

## Purpose

Registers Sunxi USB gate clocks and optional reset controllers for several Allwinner SoCs. It handles register layouts where USB clock enable bits and reset bits share one clock/reset register.

## APIs, Types, And Control Flow

`struct usb_clk_data` defines a `clk_mask`, `reset_mask`, and whether reset operations need the module clock enabled. `sunxi_usb_clk_setup()` maps the register, gets the parent clock name, allocates a sparse onecell clock array sized to the highest clock bit, registers gates for set bits, publishes an OF clock provider, then optionally allocates `usb_reset_data` and registers reset ops. Reset assert/deassert clears/sets reset bit `id` while holding the shared lock and optionally enabling the parent clock.

## State And Persistence

Gate and reset state persists in the USB clock register. Static spinlocks are used per compatible group. Reset data persists after registration and has no early-boot teardown.

## Dependencies And Integration Points

Uses OF early declarations for sun4i/sun5i/sun6i/sun8i/sun9i USB compatibles, CCF gate helpers, and the reset-controller framework. USB PHY, host, and OTG drivers consume these clocks and reset lines.

## Risks And Test Signals

Several error paths return without unmapping or freeing after partial setup. Reset `nr_resets` is derived from the highest reset bit, so unsupported holes can still be addressed by consumers if DT is wrong. Test signals include USB PHY/host probe, reset deassert sequencing, clock gate register readback, and A80 reset behavior where the reset controller first enables the associated clock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi/clk-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/Kconfig

## Purpose

Defines build-time configuration symbols for selected Tegra clock features: BPMP-managed clocks, DFLL support, and Tegra124 EMC clock support.

## APIs, Types, And Control Flow

`CLK_TEGRA_BPMP` defaults to yes when `TEGRA_BPMP` is enabled. `TEGRA_CLK_DFLL` defaults to yes for Tegra114/124/210 SoCs and selects `PM_OPP`, reflecting DFLL's dependence on OPP voltage/frequency tables. `TEGRA124_CLK_EMC` is a plain bool selected elsewhere.

## State And Persistence

No runtime state. These symbols shape which object files are compiled and which runtime drivers can exist.

## Dependencies And Integration Points

Feeds the Tegra clock Makefile and Kbuild dependency graph. It also ensures DFLL builds with OPP support.

## Risks And Test Signals

Wrong dependencies either omit required clock drivers or build unsupported code for SoCs. Test signals are kernel config diffs, object inclusion in build logs, and successful link with/without BPMP and DFLL SoC configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/Makefile

## Purpose

Lists Tegra clock driver objects and maps SoC/config symbols to the appropriate implementation files.

## APIs, Types, And Control Flow

Common clock primitives such as `clk.o`, audio sync, device, DFLL core, dividers, peripheral wrappers, PLLs, super clocks, fixed clocks, and utilities are always built into this directory. SoC-specific files are gated by `CONFIG_ARCH_TEGRA_*`, `CONFIG_TEGRA_CLK_DFLL`, `CONFIG_TEGRA124_CLK_EMC`, and `CONFIG_CLK_TEGRA_BPMP`.

## State And Persistence

No runtime state. The file determines object composition and therefore the available registration functions and platform drivers.

## Dependencies And Integration Points

Integrates Kbuild, Kconfig symbols, and source modules under `drivers/clk/tegra`. It ensures common helpers are present before SoC clock initialization code references them.

## Risks And Test Signals

Missing object entries cause unresolved symbols or absent clocks; overbroad `obj-y` entries can build dead code for unsupported SoCs. Test signals are allmodconfig/SoC defconfig builds and link coverage for BPMP, DFLL, EMC, and legacy Tegra generations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-audio-sync.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-audio-sync.c

## Purpose

Implements a simple software-controlled Tegra audio sync source clock. It has no hardware register; it stores the selected rate in memory and enforces a maximum.

## APIs, Types, And Control Flow

`tegra_clk_sync_source_ops` implements `determine_rate`, `set_rate`, and `recalc_rate`. `determine_rate` rejects requests above `sync->max_rate`; `set_rate` stores `sync->rate`; `recalc_rate` returns that stored value. `tegra_clk_register_sync_source()` allocates `struct tegra_clk_sync_source`, fills `clk_init_data`, and calls `clk_register()`.

## State And Persistence

State is in the allocated clock object: `rate` and `max_rate`. It persists until the clock is unregistered, with no hardware side effects.

## Dependencies And Integration Points

Depends on CCF registration and `struct tegra_clk_sync_source` declarations from `clk.h`. It is used by Tegra audio clock setup code as a programmable sync source.

## Risks And Test Signals

Because rate is memory-only, suspend/resume has no hardware context to restore. Consumers must not expect parent propagation or hardware validation. Test signals include `clk_set_rate()` rejecting over-max requests and audio path clock summaries reflecting the stored rate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-audio-sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-bpmp.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-bpmp.c

## Purpose

Exposes firmware-managed Tegra BPMP clocks through the Linux CCF. It discovers clock metadata from BPMP firmware, registers parent-aware clocks, and translates CCF operations into MRQ clock commands.

## APIs, Types, And Control Flow

`tegra_bpmp_clk_transfer()` constructs `MRQ_CLK` requests with command and clock ID encoded in `cmd_and_id`. Clock ops implement prepare/unprepare/is_prepared, recalc, determine/round, set_rate, and parent get/set using BPMP commands. Multiple `clk_ops` tables are selected based on firmware flags: gate-only, mux, rate, mux+rate, and read-only variants when BPMP denies state or rate/parent changes. Probe flow calls `CMD_CLK_GET_MAX_CLK_ID`, iterates IDs with `CMD_CLK_GET_ALL_INFO`, filters holes, recursively registers parents before children, and adds an OF hw provider with clock ID xlate.

## State And Persistence

State is split between firmware and the Linux-side `struct tegra_bpmp_clk` records. Parent ID arrays map CCF parent indices to BPMP IDs. Registered clocks are devm-managed, while actual enable/rate/parent state persists in BPMP firmware/hardware.

## Dependencies And Integration Points

Depends on `soc/tegra/bpmp.h`, BPMP ABI structures, OF providers, and CCF hw registration. Device tree consumers request clocks by BPMP firmware ID. Firmware permission bits directly determine which operations Linux exposes.

## Risks And Test Signals

ABI packing is fragile because command payloads are copied into an anonymous union by offset. `tegra_bpmp_unregister_clocks()` assumes all `bpmp->clocks[i]` entries are valid, but registration may store error pointers. Parent discovery can leave NULL parent names if firmware references a missing parent. Test signals include BPMP clock enumeration logs, OF clock lookup by ID, rate/parent operation errors, and permission-bit behavior for read-only clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-bpmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-device.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-device.c

## Purpose

Provides a virtual platform driver that ties selected Tegra clocks to core power-domain performance states. It lets independent PLLs and system clocks raise/lower GENPD performance state as their rates change.

## APIs, Types, And Control Flow

`struct tegra_clk_device` stores the device, target `clk_hw`, notifier block, and mutex. `tegra_clock_set_pd_state()` finds a ceiling OPP for a rate, falls back to floor for unused overly high clocks, obtains required pstate, and calls `dev_pm_genpd_set_performance_state()`. The clock notifier raises pstate before rate increases, restores old pstate on abort, and lowers pstate after rate decreases. Probe gets the clock, initializes OPPs, registers the notifier, and syncs initial pstate. Suspend resumes runtime PM to keep these clocks available during system suspend.

## State And Persistence

State is the registered notifier and current power-domain performance state. Runtime PM is expected to already be enabled by parent clock infrastructure. The driver stores no persistent rate; it derives it from the clock.

## Dependencies And Integration Points

Depends on PM domains, PM OPP, runtime PM, Tegra core OPP helpers, and clock notifiers. OF matches include Tegra sclk/pllc/plle/pllm compatibles.

## Risks And Test Signals

OPP table gaps or missing PM domains fail probe or rate transitions. Notifier error propagation can abort clock changes if pstate cannot be set. Test signals include pstate changes during `clk_set_rate()`, suspend behavior, and boards with unused high-rate clocks taking the floor fallback path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-dfll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-dfll.c

## Purpose

Implements common Tegra DFLL/DVCO support for CPU dynamic voltage/frequency scaling. The DFLL is a root clock source that can run open-loop or closed-loop, using either an integrated I2C controller or PWM output to request PMIC voltage changes while targeting CPU frequency.

## APIs, Types, And Control Flow

`struct tegra_dfll` holds device resources, MMIO bases, clocks, resets, regulator/PWM data, SoC characterization, LUTs, mode/tuning state, and the registered output `clk_hw`. Runtime PM callbacks enable/disable ref, soc, and i2c clocks. Initialization fetches common DT parameters, interface-specific I2C/PWM parameters, builds voltage LUTs from OPP/regulator data, maps four MMIO regions, prepares clocks, resets hardware, programs default integrator/droop/monitor parameters, initializes output interface, registers the CCF clock, and optional debugfs.

Rate control flows through `dfll_calculate_rate_request()`, which chooses scale/mult bits and a voltage LUT index, `dfll_request_rate()`, which saves the last request, and `dfll_set_frequency_request()`, which writes `DFLL_FREQ_REQ` in closed-loop mode. `dfll_clk_enable()` transitions disabled -> open-loop -> closed-loop; disable reverses closed-loop -> open-loop -> disabled. Suspend requires the DFLL to be stopped, asserts resets, and resume reinitializes the block.

## State And Persistence

Important software state includes `mode`, `tune_range`, `last_req`, `last_unrounded_rate`, LUT contents, and debugfs directory. Hardware state spans DFLL control registers, output/I2C registers, LUT RAM, resets, and PMIC interface state. Runtime PM gates the backing clocks around active hardware access.

## Dependencies And Integration Points

Depends on OPP tables, `cvb` voltage tables, regulator APIs, regmap/I2C for PMIC mode, pinctrl for PWM mode, reset controls, runtime PM, CCF, OF properties, and SoC callbacks in `tegra_dfll_soc_data`. CPUFreq is expected to set a rate before enabling and to disable the DFLL before suspend/remove.

## Risks And Test Signals

This file is high risk because it coordinates clock, voltage, reset, and PM state. LUT construction depends on exact regulator selectors and OPP voltages; bad tables can over/under-voltage the CPU. Mode transitions return errors if called from the wrong state, while debugfs can manually force transitions. `BUG_ON()` appears in divisor programming and mode sanity paths. Test signals include OPP/LUT build success, CPUFreq transitions, closed-loop lock, monitor-rate debugfs output, suspend refusal when still running, and regulator/PWM activity on rate changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-dfll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-dfll.h -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-dfll.h

## Purpose

Declares the public interface and SoC data contract for the Tegra DFLL common driver.

## APIs, Types, And Control Flow

`struct tegra_dfll_soc_data` supplies the OPP-owning device, maximum frequency, CVB table, regulator rail alignment, and optional clock-trimmer callbacks for initialization and voltage ranges. Exported prototypes cover registration/unregistration and runtime/system PM callbacks: `tegra_dfll_register()`, `tegra_dfll_unregister()`, `tegra_dfll_runtime_suspend/resume()`, and `tegra_dfll_suspend/resume()`.

## State And Persistence

The header owns no state, but its struct fields define the persistent SoC characterization used by `clk-dfll.c`.

## Dependencies And Integration Points

Depends on platform devices, reset types, and `cvb.h`. SoC-specific DFLL shim drivers include this header and pass initialized `tegra_dfll_soc_data` into the common driver.

## Risks And Test Signals

Incorrect SoC data can make the common DFLL driver program unsafe voltages or rates. Test signals are compile coverage for all Tegra DFLL SoCs and runtime registration using valid CVB/alignment/trimmer data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-dfll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-divider.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-divider.c

## Purpose

Implements Tegra fractional divider clocks and a special memory-controller divider helper.

## APIs, Types, And Control Flow

`tegra_clk_frac_div_ops` recalculates, determines, sets, and restores divider rates. Recalc reads the divider field, optionally bypasses UART division when `PERIPH_CLK_UART_DIV_ENB` is clear, then computes `parent * frac_base / (div + frac_base)`. Set-rate calculates the encoded divisor with `div_frac_get()`, updates the field under an optional spinlock, toggles UART divider enable, and sets fixed PLL output override when requested. `tegra_clk_register_divider()` allocates and registers a `tegra_clk_frac_div`. `tegra_clk_register_mc()` registers a critical read-only divider-table clock for MC.

## State And Persistence

Divider state persists in MMIO fields; optional UART enable and fixed override bits are coupled to divider programming. Restore context reprograms the current rate after suspend.

## Dependencies And Integration Points

Depends on CCF divider math helpers, Tegra-specific flags from `clk.h`, MMIO access, and optional shared spinlocks. Peripheral clock wrappers embed this divider implementation.

## Risks And Test Signals

Fractional rounding and UART bypass semantics are the main risks. `determine_rate` relies on `best_parent_rate` already being populated by CCF. Test signals include serial baud stability, `clk_round_rate()` accuracy for fractional dividers, context restore after suspend, and MC divider remaining critical/read-only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-divider.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-id.h -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-id.h

## Purpose

Defines a shared `enum clk_id` for Tegra clocks used across multiple SoC clock initialization files.

## APIs, Types, And Control Flow

The enum lists root clocks, PLLs, PLL outputs, bus clocks, peripheral clocks, audio sync clocks, display/XUSB/SATA clocks, and newer Tegra210-era IDs, ending with `tegra_clk_max`. It has no functions; its ordering is the API.

## State And Persistence

No runtime state. The enum values are compile-time indexes into Tegra clock arrays and registration tables.

## Dependencies And Integration Points

Included by Tegra clock setup code that stores `struct clk *` or `clk_hw` by ID. The values must remain consistent across files that share clock arrays.

## Risks And Test Signals

Changing enum order can break clock registration silently by indexing the wrong slot. Additions should appear before `tegra_clk_max` and be coordinated with all SoC tables. Test signals are build coverage and boot-time clock lookup for every ID referenced by SoC code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-id.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-periph-fixed.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-periph-fixed.c

## Purpose

Registers fixed-factor Tegra peripheral clocks that still have peripheral enable/reset bits in the CAR register banks.

## APIs, Types, And Control Flow

`tegra_clk_periph_fixed_ops` implements is_enabled, enable, disable, and recalc_rate. Enable writes the bank's enable-set register; disable writes enable-clear; is_enabled requires the enable bit set and reset bit deasserted. Recalc applies `parent_rate * mul / div`. `tegra_clk_register_periph_fixed()` resolves the register bank from the peripheral number, allocates the clock, fills init data, and registers it.

## State And Persistence

Enable/reset state persists in CAR bank registers. The fixed multiplier/divider are immutable software parameters.

## Dependencies And Integration Points

Depends on `get_reg_bank()` and Tegra periph register metadata from `clk.h`, CCF registration, and MMIO write-one-to-set/clear registers.

## Risks And Test Signals

Wrong peripheral number maps to the wrong enable/reset bank. The driver does not deassert reset on enable; it only reports reset as part of enabled state. Test signals include gate bit writes, reset-state readback, and fixed-factor rate visible in `clk_summary`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-periph-fixed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-periph-gate.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-periph-gate.c

## Purpose

Implements shared gate operations for Tegra peripheral clocks, including duplicate-clock reference counting, APB flush handling, reset-state enabled checks, and a hardware workaround.

## APIs, Types, And Control Flow

`clk_periph_is_enabled()` checks enable bits and, unless `TEGRA_PERIPH_NO_RESET`, reset bits. Enable/disable paths hold a global spinlock and update an `enable_refcnt[clk_num]` array so duplicated clock definitions do not fight over one gate. First enable writes the enable-set register and optionally executes workaround `TEGRA_PERIPH_WAR_1005168`; final disable may read chip ID first for APB peripherals, then writes enable-clear. `disable_unused` disables only when the shared refcount is zero. `tegra_clk_register_periph_gate()` allocates a gate clock and stores bank metadata.

## State And Persistence

Hardware state persists in CAR enable/reset registers. Software state persists in the shared enable-refcount array supplied by the caller.

## Dependencies And Integration Points

Depends on Tegra register-bank metadata, `tegra_read_chipid()` for APB flush, CCF gate ops, and SoC peripheral tables that share `periph_clk_enb_refcnt`.

## Risks And Test Signals

Refcount mismatches can leave clocks stuck on or off; the code warns on disabling an unenabled clock. Duplicated critical clocks rely on `disable_unused` behavior. Test signals include duplicate gate users, APB peripheral disable safety, reset-aware enable state, and workaround execution on affected clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-periph-gate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-periph.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-periph.c

## Purpose

Composes Tegra peripheral clocks from mux, divider, and gate subcomponents while presenting them as one CCF clock.

## APIs, Types, And Control Flow

Wrapper ops delegate parent operations to embedded mux ops, rate operations to embedded fractional divider ops, and enable operations to embedded peripheral gate ops after binding each sub-hw to the top-level clock. Three operation tables cover full mux/div/gate clocks, no-divider clocks, and no-gate clocks. `_tegra_clk_register_periph()` selects the right ops from flags, initializes register pointers, gate bank metadata, and shared refcount storage, registers the top-level clock, then backfills subcomponent `hw.clk` pointers. Public helpers register normal, no-divider, or data-table-driven periph clocks.

## State And Persistence

State is distributed across a mux/divider register, CAR gate registers, and the shared gate refcount array. Restore context reprograms divider and parent after suspend when applicable.

## Dependencies And Integration Points

Depends on `tegra_clk_frac_div_ops`, Tegra mux ops, `tegra_clk_periph_gate_ops`, global `periph_clk_enb_refcnt`, and SoC initialization tables.

## Risks And Test Signals

Subcomponent `__clk_hw_set_clk()`/`hw.clk` binding is essential for CCF parent/rate helpers. Flag combinations such as no-div/no-gate change operation exposure. Test signals include parent switching, fractional rate programming, gate reference counting, and context restore after suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-periph.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-pll-out.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-pll-out.c

## Purpose

Implements Tegra PLL output gate/reset clocks. These are child outputs of PLLs controlled by enable and reset bits in a shared register.

## APIs, Types, And Control Flow

`tegra_clk_pll_out_ops` implements is_enabled, enable, disable, and restore_context. Enable sets both output enable and reset bits under an optional spinlock and delays briefly. Disable clears both bits. Restore context uses the CCF enable count to decide whether to re-enable or disable after context loss. `tegra_clk_register_pll_out()` allocates and registers the output clock.

## State And Persistence

Output enable/reset state persists in the PLL output register. Software stores the bit indices, flags, and optional lock.

## Dependencies And Integration Points

Depends on CCF registration, MMIO, and Tegra PLL setup code that creates named PLL outputs for consumers.

## Risks And Test Signals

The meaning of reset bit polarity is encoded in `is_enabled()` and enable/disable; wrong bit indices break child outputs. Test signals include output enable counts after suspend/resume, register bit readback, and downstream consumers receiving expected PLL-derived rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-pll-out.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-pll.c

## Purpose

Implements Tegra PLL clock operations and registration helpers for generic PLLs and many special PLL variants: PLLE, PLLU, PLLX/C dynamic-ramp PLLs, PLLRE, PLLM/PLLMB, PLLC, PLLSS, and Tegra114/Tegra210-specific PLLE/PLLU handling.

## APIs, Types, And Control Flow

Generic PLL flow uses `_get_table_rate()` for table matches or `_calc_rate()`/variant calculators for computed rates, `_update_pll_mnp()` to program M/N/P fields, optional `clk_pll_set_sdm_data()` for SDM divisors, `_update_pll_cpcon()` for loop parameters, and `_program_pll()` to stop spread spectrum, disable if running, program defaults/dividers, re-enable, wait for lock, and restart spread spectrum. `tegra_clk_pll_ops` exposes CCF enable/disable/recalc/determine/set/restore.

Special paths add hardware-specific sequencing. PLLE performs training, setup/lock programming, spread-spectrum setup, and XUSB/SATA hardware sequencer handoff. PLLU programs UTMI delay/stable counts based on oscillator rate. Dynamic-ramp PLLs compute fixed M divisors, VCO clipping, ramp steps, and variant-specific enable/set-rate flows. PLLC has shadow-register initialization and strobe handling. PLLRE ignores P for output rate. PLLSS initializes SDM/SSC defaults and lock override. Registration helpers initialize `tegra_clk_pll`, default div field maps, operation tables, VCO limits, IDDQ, parent assumptions, and SoC-specific flags before calling `tegra_clk_dev_register()`.

## State And Persistence

PLL state spans base/misc/ext registers, PMC override registers for PLLM, IDDQ/reset bits, spread-spectrum/SDM registers, lock detector state, and dynamic ramp settings. Software parameters in `tegra_clk_pll_params` are partly mutated during registration, including flags, clipped VCO minimums, default divider map, and default calc function.

## Dependencies And Integration Points

Depends on CCF, Tegra `clk.h` data structures, register maps from SoC clock files, PMC base access, parent clocks registered by name, spinlocks, delay/timeout APIs, and optional SoC config guards. It is a central dependency for Tegra root and peripheral clock trees.

## Risks And Test Signals

This is high-risk hardware code: wrong M/N/P/SDM programming can destabilize the SoC, and enable sequences include IDDQ, reset, lock, spread-spectrum, hardware sequencer, and PMC override ordering. `BUG()` is used on unexpected reference rates. Registration mutates shared parameter structs, so reuse must be intentional. Test signals include `clk_summary` rates, lock timeout absence, suspend/resume restore, USB/XUSB/SATA operation for PLLE/PLLU, memory PLL behavior under PMC override, and set-rate coverage for table and calculated rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-pll.c -->
