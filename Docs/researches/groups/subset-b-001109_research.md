# Research: subset-b-001109

Grouped research for clock-controller source files under `sources/distributed-fs/ceph-client/drivers/clk`. Each section preserves the source path and is delimited for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/kirkwood.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mvebu/kirkwood.c

Purpose: Implements early common-clock support for Marvell Kirkwood-family core clocks, including `marvell,kirkwood-core-clock`, `marvell,mv88f6180-core-clock`, and `marvell,mv98dx1135-core-clock`. It decodes sample-at-reset registers to expose CPU, TCLK, L2, and DDR clocks, then optionally registers SoC clock gates and the Kirkwood power-save mux.

Important APIs, types, and functions: `kirkwood_get_tclk_freq()`, `kirkwood_get_cpu_freq()`, `kirkwood_get_clk_ratio()`, `mv88f6180_get_cpu_freq()`, `mv88f6180_get_clk_ratio()`, and `mv98dx1135_get_tclk_freq()` fill `struct coreclk_soc_desc` callbacks consumed by `mvebu_coreclk_setup()`. `kirkwood_gating_desc` supplies gate names and bit positions to `mvebu_clk_gating_setup()`. Local `struct clk_muxing_soc_desc` and `struct clk_muxing_ctrl` describe and own mux clocks; `clk_muxing_get_src()` maps OF clock specifier argument 0 to the mux shift.

Control flow: `CLK_OF_DECLARE()` invokes `kirkwood_clk_init()` during early OF clock init. The init selects the right `coreclk_soc_desc` from the compatible string, calls the common MVEbu core clock helper, finds the separate `"marvell,kirkwood-gating-clock"` node, registers gates, registers muxes with `clk_register_mux()`, and installs an OF provider for mux lookup.

State and persistence: Runtime state is MMIO-backed clock state plus allocated mux control storage. Core-clock frequencies are derived from immutable boot strap bits. Muxes and gates persist through CCF registrations; allocation is not devm-managed because this is early init.

Dependencies and integration points: Depends on `drivers/clk/mvebu/common.h` helpers, Linux CCF, OF early clock declaration, `of_iomap()`, `readl()`, and the shared `ctrl_gating_lock`. Device tree must provide the correct core-clock and gating-clock compatibles and use the mux shift as the clock specifier.

Risks: Unsupported strap encodings return zero multipliers or rates, which can propagate invalid clock rates. The mux provider uses the same flags value for mux registration and mux flags, so descriptor flags must stay valid for both roles. Error paths warn and return but may leave some clocks registered if later mux registration fails. The gating node lookup is global by compatible, so malformed DT with multiple matching nodes can bind an unexpected one.

Test signals: Boot logs should show no `WARN_ON()` from mapping/allocation or mux registration. `/sys/kernel/debug/clk/clk_summary` should expose `cpuclk`, `l2clk`, `ddrclk`, Kirkwood gates, and `powersave`; rates should match strap combinations in the comments. DT clock consumers using the gating node should be able to resolve the mux by shift 11.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/kirkwood.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/mv98dx3236.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mvebu/mv98dx3236.c

Purpose: Provides early clock support for Marvell MV98DX3236 and related 98DX4251 variants. It decodes the combined CPU/DDR/MPLL sample-at-reset option and registers core clocks plus a small set of peripheral gates.

Important APIs, types, and functions: `mv98dx3236_get_tclk_freq()` returns a fixed 200 MHz TCLK. `mv98dx3236_get_cpu_freq()` selects either `mv98dx4251_cpu_frequencies` or `mv98dx3236_cpu_frequencies` based on `of_machine_is_compatible()`. `mv98dx3236_get_clk_ratio()` exposes `ddrclk` and `mpll` through `struct coreclk_ratio` entries. `mv98dx3236_gating_desc` describes `ge0`, `ge1`, `pex00`, `sdio`, `usb0`, and `xor0` gates.

Control flow: The `CLK_OF_DECLARE()` hook for `"marvell,mv98dx3236-core-clock"` calls `mv98dx3236_clk_init()`. Init finds a separate `"marvell,mv98dx3236-gating-clock"` node, registers core clocks through `mvebu_coreclk_setup()`, and, when present, registers gates through `mvebu_clk_gating_setup()`.

State and persistence: All rate state is derived from SAR1 bits at boot and exposed as CCF clocks. Gate state persists in the clock-gating MMIO register. No private mutable state is kept after init beyond common MVEbu CCF allocations.

Dependencies and integration points: Relies on the MVEbu common core/gating helpers and device-tree root machine compatibles to distinguish 98DX4251 from 98DX3236. Consumers use clock names `ddrclk`, `mpll`, and the gate names registered from `mv98dx3236_gating_desc`.

Risks: If the machine compatible is absent or mismatched, CPU and ratio callbacks can leave rates or multipliers unset. Unsupported SAR options print an error for CPU frequency but ratio callbacks silently leave previous output values untouched for unknown SoC compatibility. The gate lookup is compatible-based rather than child-node-local.

Test signals: Boot on each supported compatible should report no "CPU freq select unsupported" message for valid straps. `clk_summary` should show fixed TCLK 200 MHz, CPU/DDR/MPLL values matching SAR1, and gate clocks with the expected bit positions. DT binding tests should ensure root compatible and core-clock compatible agree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/mv98dx3236.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/orion.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mvebu/orion.c

Purpose: Implements early core-clock providers for legacy Marvell Orion SoCs MV88F5181, MV88F5182, MV88F5281, and MV88F6183. It exposes TCLK, CPU, and a single CPU-to-DDR ratio clock through the shared MVEbu core-clock framework.

Important APIs, types, and functions: Four SoC-specific callback groups decode SAR fields: `mv88f5181_get_tclk_freq()`, `mv88f5181_get_cpu_freq()`, `mv88f5181_get_clk_ratio()`, equivalent 5182 and 5281 functions, and `mv88f6183_*()` callbacks. Each group is packaged in a `struct coreclk_soc_desc` with one `orion_coreclk_ratios` entry named `ddrclk`.

Control flow: Each compatible has a dedicated `CLK_OF_DECLARE()` callback. The callback simply calls `mvebu_coreclk_setup(np, &soc_desc)`, allowing the common MVEbu code to map the SAR register and publish the clocks.

State and persistence: The file maintains no dynamic state of its own. Rates are pure functions of the boot strap register, and the resulting CCF registrations persist for the lifetime of the kernel.

Dependencies and integration points: Depends on `drivers/clk/mvebu/common.h`, Linux OF clock early init, and the device-tree compatible string for the core-clock node. Clock consumers depend on the common MVEbu provider naming for CPU, TCLK, and `ddrclk`.

Risks: Unsupported or reserved SAR encodings return zero rates or ratio multiplier zero, which can surface as unusable child clocks. The callback `id` is ignored because there is only one ratio; expanding ratios without adjusting switch logic would be error-prone. These old SoCs have subtly different SAR layouts, so accidental compatible reuse would produce wrong rates.

Test signals: Boot each compatible with known strap values and verify `clk_summary` CPU/TCLK/DDR rates. Invalid strap emulation should produce zero-rate behavior in a controlled way. DT should bind exactly one Orion compatible and no clock-gating behavior is expected from this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/orion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mxs/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/mxs/Makefile

Purpose: Builds the Freescale/NXP MXS clock support. The common helper objects are always linked for this directory, while SoC-specific clock-topology files are conditional on i.MX23 and i.MX28 configuration.

Important APIs, types, and functions: The make targets include `clk.o`, `clk-pll.o`, `clk-ref.o`, `clk-div.o`, `clk-frac.o`, and `clk-ssp.o` unconditionally. `clk-imx23.o` is selected by `CONFIG_SOC_IMX23`; `clk-imx28.o` is selected by `CONFIG_SOC_IMX28`.

Control flow: Kbuild composes the MXS clock directory into the kernel. The object split matches the code design: reusable CCF primitives and SSP helper support are separated from SoC-specific OF early clock declarations.

State and persistence: No runtime state. The file controls which object files are present in the final kernel image.

Dependencies and integration points: Depends on parent Kbuild entering this directory only when MXS clock support is required. The conditional SoC objects must match the symbols that provide their `CLK_OF_DECLARE()` hooks and exported SoC helper APIs.

Risks: Because helpers are `obj-y`, they are built whenever the directory is included; stale helper dependencies would affect both i.MX23 and i.MX28. Missing SoC config prevents the matching one-cell provider from being present even if the DT node exists.

Test signals: Build coverage should include `CONFIG_SOC_IMX23`, `CONFIG_SOC_IMX28`, and both enabled. Link errors around `mxs_clk_*` helpers or missing `mxs_saif_clkmux_select()` would indicate Makefile coverage issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mxs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-div.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-div.c

Purpose: Defines an MXS integer divider clock wrapper around the generic `clk_divider` implementation, adding hardware busy-bit polling after rate changes.

Important APIs, types, and functions: `struct clk_div` embeds `struct clk_divider`, stores the generic divider ops pointer, the divider register, and the busy bit. `mxs_clk_div()` allocates and registers the clock with `CLK_DIVIDER_ONE_BASED` and `CLK_SET_RATE_PARENT`. `clk_div_recalc_rate()`, `clk_div_determine_rate()`, and `clk_div_set_rate()` delegate to generic divider ops, then call `mxs_clk_wait()` on successful writes.

Control flow: SoC topology files call `mxs_clk_div(name, parent, reg, shift, width, busy)`. CCF invokes wrapper ops. On `set_rate`, the generic divider updates the register under `mxs_lock`; the wrapper waits until the provided busy bit clears.

State and persistence: One allocated `struct clk_div` persists per clock. The actual divider state is MMIO-backed. The shared `mxs_lock` serializes register updates.

Dependencies and integration points: Depends on `clk.h` for `mxs_clk_wait()` and `mxs_lock`, the generic CCF divider ops, and SoC files passing correct register and busy-bit metadata.

Risks: Incorrect busy-bit metadata can cause false success, timeout, or indefinite hardware instability. Width/shift combinations are not validated beyond generic helpers. Allocation is not devm-managed because these clocks are early platform clocks.

Test signals: Rate-change tests should confirm the register field changes, the busy bit clears within 10 ms, and callers receive `-ETIMEDOUT` on stuck hardware. `clk_summary` should show derived divider rates for CPU, HBUS, XBUS, SSP, GPMI, EMI, LCDIF, and ETM paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-div.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-frac.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-frac.c

Purpose: Implements an adjustable MXS fractional divider with a busy bit. It is used for clocks such as SAIF where the output is `parent_rate * div / 2^width`.

Important APIs, types, and functions: `struct clk_frac` stores `clk_hw`, register, shift, width, and busy bit. `mxs_clk_frac()` registers the clock with `clk_frac_ops`. `clk_frac_recalc_rate()` reads the fractional field and computes the scaled rate. `clk_frac_determine_rate()` and `clk_frac_set_rate()` calculate a divider from requested and parent rates, reject rates above the parent or zero divisors, and update the register under `mxs_lock`.

Control flow: Consumers request a rate through CCF. The determine path adjusts `req->rate` to the rounded achievable value. The set path writes the fraction field and waits for the busy bit via `mxs_clk_wait()`.

State and persistence: Fractional divider state is stored in MMIO. The allocated `struct clk_frac` persists after registration. Register writes are serialized by the global MXS spinlock.

Dependencies and integration points: Used by `clk-imx23.c` and `clk-imx28.c` for SAIF divider clocks. Depends on `do_div()` arithmetic, relaxed IO accessors, CCF rate request semantics, and `mxs_clk_wait()`.

Risks: `(1 << width)` assumes width values small enough for 32-bit shifts. Very low requested rates can compute zero and fail with `-EINVAL`. Rounding behavior increments `req->rate` if the computed result truncates, so rate expectations should account for upward rounding.

Test signals: SAIF rate tests should exercise valid rates below the parent, rate-above-parent rejection, zero-divider rejection, and timeout behavior when the busy bit remains set. Debugfs should show the rounded rate after `set_rate`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-frac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-imx23.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-imx23.c

Purpose: Provides the i.MX23 clock tree as an early OF one-cell provider for `"fsl,imx23-clkctrl"`. It registers fixed clocks, PLL/reference clocks, muxes, integer and fractional dividers, gates, and initial always-on clocks.

Important APIs, types, and functions: `mx23_clocks_init()` is the `CLK_OF_DECLARE()` entry. `clk_misc_init()` programs WFI clock gating, clears SAIF/SSP bypasses, enables SAIF fractional divider mode, and programs the IO fractional reference to 288 MHz. The `enum imx23_clk` indexes the `clks[]` provider array. Helper calls include `mxs_clk_fixed()`, `mxs_clk_pll()`, `mxs_clk_ref()`, `mxs_clk_mux()`, `mxs_clk_div()`, `mxs_clk_frac()`, `mxs_clk_gate()`, and fixed-factor registration.

Control flow: Init maps the DIGCTL node and the CLKCTRL node, applies misc clock programming, registers every clock in enum order, checks for `IS_ERR()`, publishes `clk_data` through `of_clk_add_provider()`, and prepares/enables core clocks `cpu`, `hbus`, `xbus`, `emi`, and `uart`.

State and persistence: `clkctrl` and `digctrl` are static MMIO bases. The registered clock tree persists globally. Hardware registers hold mux, divider, PLL, and gate state; early init also mutates power/performance defaults.

Dependencies and integration points: Depends on the `"fsl,imx23-digctl"` node, MXS helper files, DT clock indexes matching `enum imx23_clk`, and CCF one-cell lookup. Consumers such as SSP, SAIF, LCDIF, GPMI, USB, and UART rely on these names and indexes.

Risks: Missing DIGCTL mapping only warns but later USB gate registration uses `DIGCTRL`, so NULL mapping can become unsafe. The init returns on the first registration error, potentially leaving a partially registered clock tree without provider registration. Register offsets and busy bits are hard-coded and must match the SoC reference manual.

Test signals: Boot should show no i.MX23 registration errors. `clk_summary` should expose all enum clocks and show the init-on clocks prepared. SSP parent should be `ref_io` rather than `ref_xtal`, SAIF should use fractional mode, and USB gate should resolve through DIGCTL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-imx23.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-imx28.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-imx28.c

Purpose: Provides the i.MX28 clock tree as an early OF one-cell provider for `"fsl,imx28-clkctrl"`. It extends the i.MX23 pattern with multiple PLLs, four SSP channels, Ethernet/PTP, FlexCAN, dual USB PHY gates, and SAIF clock-mux selection support.

Important APIs, types, and functions: `mx28_clocks_init()` is the early init entry. `mxs_saif_clkmux_select()` is an exported SoC helper that programs the SAIF input clock mux in DIGCTL. `clk_misc_init()` sets WFI behavior, fixes a bad ENET divider default, clears SAIF and SSP bypasses, enables SAIF fractional mode, clears ENET sleep, and sets IO fractional references. `enum imx28_clk` defines one-cell indexes.

Control flow: Init maps `"fsl,imx28-digctl"` and CLKCTRL, applies misc programming, registers fixed, PLL, reference, mux, divider, fractional, fixed-factor, and gate clocks, validates no `IS_ERR()` entries, adds the provider, registers the `enet_out` clkdev alias, and enables `cpu`, `hbus`, `xbus`, `emi`, and `uart`.

State and persistence: Static `clkctrl` and `digctrl` hold MMIO bases. Clock state is persisted in hardware registers and CCF registrations. `mxs_saif_clkmux_select()` can later mutate DIGCTL mux state.

Dependencies and integration points: Depends on MXS common helpers, DT indexes matching `enum imx28_clk`, and the DIGCTL node. Ethernet users can use the `enet_out` clkdev registration. SAIF users depend on the exported clkmux selector.

Risks: The helper accepts only mux values 0..3 but has no locking around the DIGCTL write pair. Missing DIGCTL mapping warns but later USB/SAIF accesses depend on it. The ENET divider quirk and IO fractional defaults are policy decisions that can affect board-specific expectations.

Test signals: Boot with i.MX28 DT should register all clocks without errors. Validate SSP0-3 can derive from ref_io0/ref_io1, SAIF clocks use fractional divisors, `enet_out` exists as a clkdev lookup, and `mxs_saif_clkmux_select()` returns `-EINVAL` for values above 3.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-imx28.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-pll.c

Purpose: Implements the MXS PLL clock primitive as a fixed-rate CCF clock with prepare/unprepare power control and enable/disable output gating.

Important APIs, types, and functions: `struct clk_pll` stores `clk_hw`, base address, power bit, and fixed rate. `mxs_clk_pll()` registers a PLL with `clk_pll_ops`. The ops set and clear the power bit at `base + SET/CLR`, clear or set bit 31 for output gating, and return the fixed `rate` in `clk_pll_recalc_rate()`.

Control flow: SoC files create PLLs by passing the PLL control base, power bit, and known rate. CCF prepare powers up the PLL and waits 10 microseconds. Enable clears the gate bit; disable sets it.

State and persistence: The allocated PLL object persists after registration. PLL power/gate state is hardware-backed. The rate is fixed in memory rather than recalculated from programmable fields.

Dependencies and integration points: Used by i.MX23 and i.MX28 clock trees. Depends on MXS SET/CLR register semantics and CCF prepare/enable separation.

Risks: There is no lock-status polling, only a fixed delay on prepare. If the hardware requires longer lock time or has board-specific PLL rates, consumers can see incorrect readiness or rates. Bit 31 is assumed to be the gate for every MXS PLL instance.

Test signals: Prepare/enable sequencing should set the power bit, clear bit 31, and produce the configured fixed rate in `clk_summary`. Suspend/resume or disable tests should verify unprepare clears the power bit and disable gates the output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-ref.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-ref.c

Purpose: Implements MXS PLL reference clocks. Four reference clocks share one register, each with an 8-bit lane containing a gate bit and a 6-bit fractional divisor.

Important APIs, types, and functions: `struct clk_ref` stores `clk_hw`, register, and lane index. `mxs_clk_ref()` registers the clock. `clk_ref_enable()` and `clk_ref_disable()` clear/set the lane gate bit. `clk_ref_recalc_rate()` computes `parent * 18 / FRAC`. `clk_ref_determine_rate()` and `clk_ref_set_rate()` clamp FRAC to 18..35 and update the lane under `mxs_lock`.

Control flow: SoC init creates references such as `ref_cpu`, `ref_emi`, `ref_pix`, and `ref_io`. Consumers request rates; the driver picks the closest valid FRAC and writes it to the lane.

State and persistence: Each `struct clk_ref` persists after registration. The divisor and gate state live in MMIO. Register updates are serialized with the shared MXS spinlock.

Dependencies and integration points: Used by both i.MX23 and i.MX28 topology files as parents for CPU, EMI, PIX, IO, HSADC, and GPMI paths. Depends on lane layout and CCF gate/rate ops.

Risks: A zero FRAC value in hardware would cause divide-by-zero in `recalc_rate()`. The implementation relies on init code programming sane fractional values. Clamping means requested rates outside the supported range silently become edge rates.

Test signals: Validate each reference lane rate follows `pll * 18 / frac`, gate bits clear/set on enable/disable, and set-rate clamps to FRAC 18 or 35 for out-of-range requests. Boot defaults should avoid zero FRAC fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-ref.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-ssp.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-ssp.c

Purpose: Provides the exported helper `mxs_ssp_set_clk_rate()` for programming the SSP block serial clock divider fields, used by MXS SPI/MMC-style SSP consumers.

Important APIs, types, and functions: `mxs_ssp_set_clk_rate(struct mxs_ssp *ssp, unsigned int rate)` reads the parent clock rate with `clk_get_rate(ssp->clk)`, searches even `clock_divide` values from 2 to 254, computes an 8-bit `clock_rate`, writes `HW_SSP_TIMING` fields, stores the actual SCK rate in `ssp->clk_rate`, and exports the symbol GPL-only.

Control flow: A consumer passes its SSP device context and requested bit clock. The helper picks the first divider pair where `clock_rate <= 255`; if none exists it logs an error and leaves the register unchanged. Otherwise it rewrites timing fields and logs the actual result at debug level.

State and persistence: Hardware timing register fields hold the active SSP clocking. The helper also updates `ssp->clk_rate` in the caller-owned structure.

Dependencies and integration points: Depends on `<linux/spi/mxs-spi.h>` register macros, `struct mxs_ssp`, and a valid prepared parent clock. It is not a CCF clock provider itself.

Risks: No locking is performed, so callers must serialize access against active transfers or other timing updates. A zero requested `rate` would divide by zero. The algorithm chooses the first valid divider pair, not necessarily the closest or least-jitter solution.

Test signals: SSP users should verify actual `ssp->clk_rate` is at or below the requested rate and the hardware timing fields match. Error-path tests should cover too-low requested rates and invalid zero-rate inputs at the caller boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-ssp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mxs/clk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mxs/clk.c

Purpose: Holds shared MXS clock infrastructure: the global spinlock and a busy-bit wait helper used by divider and fractional clocks.

Important APIs, types, and functions: `DEFINE_SPINLOCK(mxs_lock)` provides the shared serialization lock. `mxs_clk_wait(void __iomem *reg, u8 shift)` polls a bit in a register until it clears or 10 ms elapse.

Control flow: Clock set-rate paths write hardware fields, then call `mxs_clk_wait()` with the associated busy bit. The helper loops on `readl_relaxed(reg) & BIT(shift)` and returns `-ETIMEDOUT` if `time_after(jiffies, timeout)` becomes true.

State and persistence: The spinlock is global state shared by all MXS helper clocks. The wait helper does not persist state; it observes MMIO busy bits.

Dependencies and integration points: Included by all MXS helper files through `clk.h`. Depends on `jiffies`, `msecs_to_jiffies()`, relaxed IO reads, and Linux spinlock semantics.

Risks: Busy polling has no CPU relaxation call and can spin for up to 10 ms. If called while jiffies are not advancing, timeout behavior may be affected. Incorrect shift values can make rate changes appear stuck or complete prematurely.

Test signals: Inject or emulate stuck busy bits to confirm `-ETIMEDOUT`. Rate-change tests for `mxs_clk_div()` and `mxs_clk_frac()` should verify they propagate this error. Lockdep should not report issues around `mxs_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mxs/clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mxs/clk.h -->
# sources/distributed-fs/ceph-client/drivers/clk/mxs/clk.h

Purpose: Declares the shared MXS clock helper API and small inline wrappers around common CCF clock types.

Important APIs, types, and functions: Exposes `mxs_lock`, `mxs_clk_wait()`, `mxs_clk_pll()`, `mxs_clk_ref()`, `mxs_clk_div()`, and `mxs_clk_frac()`. Inline helpers register fixed-rate, gate, mux, and fixed-factor clocks. Defines MXS SET/CLR register offsets.

Control flow: SoC topology files include this header and compose clock trees by calling helper constructors. Inline gate and mux helpers consistently apply `CLK_SET_RATE_PARENT`; muxes also use `CLK_SET_RATE_NO_REPARENT`.

State and persistence: The header declares shared state but owns none directly. Registered clocks and MMIO state persist through the implementation files.

Dependencies and integration points: Depends on Linux CCF and spinlock definitions. It is the integration contract between generic MXS helper implementations and `clk-imx23.c`/`clk-imx28.c`.

Risks: Inline helpers bake in flags and lock choices for all SoC users. The gate helper uses `CLK_GATE_SET_TO_DISABLE`, so users must only pass gates with inverted set-to-disable semantics. The mux helper prevents reparenting during rate changes, which is correct for these trees but would surprise new users if reused elsewhere.

Test signals: Build tests should catch signature drift between declarations and implementations. Runtime checks should verify inline gate and mux semantics match hardware for every caller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mxs/clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/nuvoton/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/nuvoton/Kconfig

Purpose: Defines Kconfig selection for Nuvoton common clock support and the MA35D1 clock controller.

Important APIs, types, and functions: `COMMON_CLK_NUVOTON` is a bool gated by `ARCH_MA35 || COMPILE_TEST` and defaults to `ARCH_MA35`. Inside it, `CLK_MA35D1` enables the MA35D1 clock controller and also defaults to `ARCH_MA35`.

Control flow: Kconfig controls whether the Nuvoton clock directory builds the MA35D1 objects. The nested `if COMMON_CLK_NUVOTON` prevents selecting the SoC driver without the common family gate.

State and persistence: No runtime state; this file affects kernel configuration and object inclusion.

Dependencies and integration points: Integrates with architecture selection for MA35 and compile-test coverage for broader build validation.

Risks: Since both symbols are bool, the MA35D1 clock driver is built-in when enabled, matching its `postcore_initcall()` registration. Configurations that need modular clock support are not supported by this file.

Test signals: `ARCH_MA35=y` should default-enable both symbols. `COMPILE_TEST=y` should allow build coverage on other architectures. Disabling `CLK_MA35D1` should omit all MA35D1 clock objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/nuvoton/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/nuvoton/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/nuvoton/Makefile

Purpose: Builds the Nuvoton MA35D1 clock controller implementation when `CONFIG_CLK_MA35D1` is enabled.

Important APIs, types, and functions: Adds `clk-ma35d1.o`, `clk-ma35d1-divider.o`, and `clk-ma35d1-pll.o` to `obj-$(CONFIG_CLK_MA35D1)`.

Control flow: Kbuild links the main platform driver, custom ADC divider helper, and custom PLL helper together under the same config symbol.

State and persistence: No runtime state; build composition only.

Dependencies and integration points: Must stay aligned with declarations in `clk-ma35d1.h` and calls from `clk-ma35d1.c`.

Risks: Omitting one helper object would create unresolved symbols for `ma35d1_reg_adc_clkdiv()` or `ma35d1_reg_clk_pll()`. Adding new MA35D1 helper files requires updating this Makefile.

Test signals: Build `CONFIG_CLK_MA35D1=y` with `W=1` and `COMPILE_TEST` to ensure all three objects compile and link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/nuvoton/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/nuvoton/clk-ma35d1-divider.c -->
# sources/distributed-fs/ceph-client/drivers/clk/nuvoton/clk-ma35d1-divider.c

Purpose: Implements a MA35D1-specific ADC divider clock where the encoded field maps to even divisors and an optional update/mask bit must be written with the divider.

Important APIs, types, and functions: `struct ma35d1_adc_clk_div` stores `clk_hw`, MMIO register, shift/width, mask bit, generated divider table, and lock. `ma35d1_reg_adc_clkdiv()` allocates the object and an even-divisor table, then registers it with `devm_clk_hw_register()`. The ops implement recalc, determine, and set-rate using generic divider helpers.

Control flow: The main MA35D1 driver calls `ma35d1_reg_adc_clkdiv()` for `adc_div`. Determine uses `divider_determine_rate()` with `CLK_DIVIDER_ROUND_CLOSEST`. Set-rate computes the table value, writes `(value - 1)` into the field, ORs the optional mask bit, and unlocks.

State and persistence: Per-clock state is devm-managed. The divider value persists in hardware. The generated table persists for the device lifetime.

Dependencies and integration points: Depends on the MA35D1 platform driver's spinlock and parent clock hardware pointer. Exports `ma35d1_reg_adc_clkdiv()` for use by the main driver object.

Risks: `mask_bit` is tested as a boolean then passed to `BIT(mask_bit)`, so passing 0 means no mask bit can be set even if bit 0 is intended. The caller in this tree passes `0x1ffff`, which is too large for `BIT(mask_bit)` if interpreted as a bit index; because it is nonzero this expression is risky and suggests a semantic mismatch between mask and mask bit. Divider value handling also assumes generic `divider_get_val()` returns a value compatible with storing `value - 1`.

Test signals: ADC clock rate tests should verify register writes for several requested rates and confirm the update/mask behavior matches the hardware manual. Static review should check the `mask_bit` argument in `clk-ma35d1.c` against the helper's expected bit-index semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/nuvoton/clk-ma35d1-divider.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/nuvoton/clk-ma35d1-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/nuvoton/clk-ma35d1-pll.c

Purpose: Implements MA35D1 PLL clock hardware, including the special CAPLL SMIC format and generic integer, fractional, and spread-spectrum PLL formats for DDRPLL, APLL, EPLL, and VPLL.

Important APIs, types, and functions: `struct ma35d1_clk_pll` stores CCF hardware, clock id, mode, and CTL0/1/2 bases. `ma35d1_reg_clk_pll()` registers a PLL. `ma35d1_calc_smic_pll_freq()` and `ma35d1_calc_pll_freq()` recalculate rates from registers. `ma35d1_pll_find_closest()` searches valid input divider, feedback divider, and output divider combinations. `ma35d1_clk_pll_set_rate()`, `_recalc_rate()`, `_determine_rate()`, `_prepare()`, and `_unprepare()` implement CCF ops.

Control flow: The main driver registers CAPLL, DDRPLL, APLL, EPLL, and VPLL with modes parsed from DT. CAPLL and DDRPLL get fixed ops without set-rate; other PLLs can search, program CTL registers, and power up/down. Recalc dispatches by id and bypass bits return the parent rate.

State and persistence: PLL configuration persists in CTL registers. The in-memory object stores mode and register bases. Power-down state is tracked in CTL1 `PD` for generic PLLs; CAPLL has a different CTL0 layout for recalc.

Dependencies and integration points: Depends on dt-binding clock IDs, `<linux/bitfield.h>`, CCF, and MA35D1 register layout. The main driver supplies the parent `hxt` clock and base offsets.

Risks: `ma35d1_clk_pll_determine_rate()` calls the search but then overwrites `req->rate` with the current hardware rate instead of the found closest rate, which may make rate negotiation misleading. The set-rate path writes `PLL_CTL1_PD`, leaving the PLL powered down until prepare. CAPLL uses a different PD/BP layout but `ma35d1_clk_pll_is_prepared()` always reads CTL1, which is not valid for CAPLL; CAPLL avoids prepare ops via fixed ops. Search loops are large for fractional mode and can be expensive.

Test signals: Validate recalc against known register encodings for all PLL IDs and modes. For adjustable PLLs, test determine/set/prepare sequences and confirm requested rates converge. Confirm CAPLL/DDRPLL expose no set-rate ops. DT tests should cover valid `nuvoton,pll-mode` strings for all five PLLs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/nuvoton/clk-ma35d1-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/nuvoton/clk-ma35d1.c -->
# sources/distributed-fs/ceph-client/drivers/clk/nuvoton/clk-ma35d1.c

Purpose: Main platform clock driver for the Nuvoton MA35D1 SoC. It registers a one-cell hardware clock provider with fixed oscillators, PLLs, muxes, dividers, fixed factors, and gates for CPU, system, bus, storage, USB, graphics, timers, UARTs, I2C, SPI, watchdogs, audio, ADC, and other peripherals.

Important APIs, types, and functions: `ma35d1_clocks_probe()` maps the clock controller, parses five `nuvoton,pll-mode` entries with `ma35d1_get_pll_setting()`, allocates `struct clk_hw_onecell_data`, and fills the `hws[]` array up to `CLK_MAX_IDX`. Local helper wrappers register fixed, mux, divider, table divider, pow2 divider, fixed-factor, and gate clocks. The driver registers via `platform_driver_register()` at `postcore_initcall()`.

Control flow: Probe allocates provider storage, maps resource 0, validates PLL modes, registers oscillators and PLLs first, then derived CPU/system/bus clocks, then large groups of peripheral mux/div/gate clocks. It ends by calling `devm_of_clk_add_hw_provider()`.

State and persistence: Clock topology is devm-managed and tied to the platform device. The shared `ma35d1_lock` serializes mux, divider, and gate register accesses. Hardware registers retain rate, parent, and gate state.

Dependencies and integration points: Depends on `dt-bindings/clock/nuvoton,ma35d1-clk.h`, device-tree parent clock names such as `hxt`, register resource mapping, and helper files for PLL and ADC divider registration. Consumers use clock IDs from the binding through the one-cell provider.

Risks: The file is highly table/offset driven, so wrong shifts, widths, parent arrays, or clock IDs produce silent topology bugs. The probe does not check most individual `hws[]` results before publishing the provider. Some parent data entries use `.index = -1` placeholders, so mux widths must not allow invalid selections to leak to consumers. The ADC divider mask argument appears suspicious relative to the helper API.

Test signals: Boot should bind `"nuvoton,ma35d1-clk"` before device consumers probe and publish `CLK_MAX_IDX` clocks. `clk_summary` should show all named gates and parents. DT schema tests should require five valid `nuvoton,pll-mode` strings. Runtime tests should cover representative UART, timer, CAN, SDH, ADC, and PLL rate changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/nuvoton/clk-ma35d1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/nuvoton/clk-ma35d1.h -->
# sources/distributed-fs/ceph-client/drivers/clk/nuvoton/clk-ma35d1.h

Purpose: Declares the MA35D1 private helper interface shared between the main clock driver, PLL helper, and ADC divider helper.

Important APIs, types, and functions: Declares `ma35d1_reg_clk_pll()` for registering PLL clocks and `ma35d1_reg_adc_clkdiv()` for registering the special ADC divider. Both return `struct clk_hw *` for insertion into the main one-cell provider array.

Control flow: `clk-ma35d1.c` includes this header and calls the helpers while populating `hws[]`. The helper implementation files export the symbols GPL-only.

State and persistence: No state is owned by the header. It defines function signatures that pass device lifetime, parent clock hardware, MMIO base/register, locking, and encoding metadata into helper objects.

Dependencies and integration points: Depends on forward declarations from Linux CCF and device headers included by consumers. It is private to the Nuvoton clock directory.

Risks: The `ma35d1_reg_adc_clkdiv()` parameter name `mask_bit` implies a bit index, while call sites may pass masks; the header does not clarify semantics. Signature drift would break all MA35D1 object integration.

Test signals: Build tests should catch helper signature mismatches. Code review should verify every helper caller passes register and mask/bit parameters with the expected semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/nuvoton/clk-ma35d1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/nxp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/nxp/Makefile

Purpose: Builds NXP LPC clock drivers for LPC18xx/LPC43xx and LPC32xx families.

Important APIs, types, and functions: `CONFIG_ARCH_LPC18XX` selects `clk-lpc18xx-cgu.o`, `clk-lpc18xx-ccu.o`, and `clk-lpc18xx-creg.o`. `CONFIG_ARCH_LPC32XX` selects `clk-lpc32xx.o`.

Control flow: Kbuild links the correct clock provider set for the selected architecture. LPC18xx needs separate CGU, CCU, and CREG providers; LPC32xx is a single large provider plus a USB sub-provider inside one object.

State and persistence: No runtime state; object inclusion only.

Dependencies and integration points: Must align with the architecture Kconfig symbols and OF compatibles implemented by each source file.

Risks: No `COMPILE_TEST` conditions appear here, so broad build coverage depends on architecture config. Splitting LPC18xx across three objects means missing one object can leave DT clock providers unresolved.

Test signals: Build `ARCH_LPC18XX` and `ARCH_LPC32XX` configs and verify all selected objects link. Boot DTs should find matching providers for CGU, CCU, CREG, and LPC32xx USB clock nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/nxp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/nxp/clk-lpc18xx-ccu.c -->
# sources/distributed-fs/ceph-client/drivers/clk/nxp/clk-lpc18xx-ccu.c

Purpose: Implements the LPC18xx/LPC43xx Clock Control Unit branch clocks. It registers gates and optional read-only divide-by-two stages for branch clocks sourced from CGU base clocks.

Important APIs, types, and functions: `struct lpc18xx_clk_branch` describes each branch base parent, output name, register offset, flags, stored clk, and gate. `lpc18xx_ccu_branch_clk_get()` resolves OF clock specifier offset to a registered branch clock. `lpc18xx_ccu_gate_endisable()` implements hardware-specific enable/disable. `lpc18xx_ccu_register_branch_gate_div()` creates composite clocks.

Control flow: `lpc18xx_ccu_init()` maps the CCU, reads the node's `clock-names`, registers branch clocks for each named base clock, and adds a custom OF provider. For bus branches, registration updates the parent name so later branches in that group use the bus branch as parent. Essential CPU/SDRAM-related branches are prepared and enabled immediately.

State and persistence: Branch descriptors are static and store returned `struct clk *` pointers. Gate/divider state persists in CCU MMIO registers. Allocated divider objects persist after registration.

Dependencies and integration points: Depends on CGU base clock names such as `base_cpu_clk`, DT binding offsets from `lpc18xx-ccu.h`, and CCF composite clocks.

Risks: Branch registers hang if read while the base parent clock is disabled, so `is_enabled()` carefully checks parent state first. Disable requires a two-write AUTO then clear-RUN sequence; changing it can destabilize hardware. The provider returns clocks only if both offset and base-name membership match the DT `clock-names` list.

Test signals: Boot should register all branch clocks listed in DT `clock-names`. Read `clk_summary` without hangs when base clocks are disabled. Verify essential branches `CLK_CPU_EMC`, `CLK_CPU_CORE`, `CLK_CPU_CREG`, and `CLK_CPU_EMCDIV` are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/nxp/clk-lpc18xx-ccu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/nxp/clk-lpc18xx-cgu.c -->
# sources/distributed-fs/ceph-client/drivers/clk/nxp/clk-lpc18xx-cgu.c

Purpose: Implements the LPC18xx/LPC43xx Clock Generation Unit. It registers source clocks, PLLs, intermediate dividers, and base clocks used by CCU branch clocks and other consumers.

Important APIs, types, and functions: Source and base clock names are indexed by dt-binding IDs. `struct lpc18xx_cgu_src_clk_div`, `struct lpc18xx_cgu_base_clk`, and `struct lpc18xx_cgu_pll_clk` describe composite clocks. PLL0 helper functions encode/decode the special MDEC multiplier and bandwidth fields. `lpc18xx_pll0_set_rate()`, `lpc18xx_pll0_recalc_rate()`, and `lpc18xx_pll1_recalc_rate()` implement PLL rate behavior.

Control flow: `lpc18xx_cgu_init()` maps CGU registers, registers fixed IRC and external oscillator gate, registers PLL0USB/PLL0AUDIO/PLL1, registers IDIVA-E dividers, registers all base clocks, and exposes a one-cell provider for base clocks.

State and persistence: Static arrays store descriptors and base clock pointers. MMIO registers hold mux, divider, gate, and PLL state. PLL0 set-rate powers down the PLL, writes multiplier and pre/post dividers, powers up, polls lock with retries, then enables output.

Dependencies and integration points: Depends on `dt-bindings/clock/lpc18xx-cgu.h`, external oscillator parent from DT, CCF mux/divider/gate/composite ops, and CCU branch clocks consuming base clock names.

Risks: `lpc18xx_pll0_determine_rate()` and `set_rate()` appear to reject `parent_rate < rate`, which is unusual for a multiplying PLL and should be verified against hardware intent. PLL0 supports only pre/post divider values of 1. Gate `is_enabled()` recursively checks parents to avoid reporting enabled clocks whose source is off. Base clock table contains reserved holes returning `-ENOENT`.

Test signals: Verify one-cell base clocks for all non-reserved IDs. Test PLL0 rate changes on USB/audio PLLs, including lock timeout paths. Ensure CCU can consume registered base names and `clk_summary` traversal does not access disabled clock domains unsafely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/nxp/clk-lpc18xx-cgu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/nxp/clk-lpc18xx-creg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/nxp/clk-lpc18xx-creg.c

Purpose: Provides LPC18xx/LPC43xx CREG-derived 32 kHz and 1 kHz clocks. The 32 kHz clock must be available early, while the 1 kHz divided clock is registered later by a platform driver.

Important APIs, types, and functions: `struct clk_creg_data` stores clock hardware, name, syscon regmap, enable mask, and ops. `clk_creg_32k_prepare()` powers up and releases reset for the 32 kHz oscillator, then sleeps 2500 ms. `clk_creg_1k_recalc_rate()` returns `parent / 32`. `clk_register_creg_clk()` registers a CREG clock.

Control flow: `CLK_OF_DECLARE_DRIVER()` runs `lpc18xx_creg_clk_init()` early, looks up the parent syscon, registers only the 32 kHz clock, and leaves the 1 kHz slot as `-EPROBE_DEFER`. `builtin_platform_driver()` later runs `lpc18xx_creg_clk_probe()`, reuses the early 32 kHz clock, registers the 1 kHz clock with 32 kHz as parent, and replaces the OF provider data.

State and persistence: Static arrays hold early and final clock pointers. Enable and prepare state persist in the parent syscon register `CREG0`.

Dependencies and integration points: Depends on a syscon parent node, a DT parent for the 32 kHz source, CCF, and regmap. Consumers may request the 32 kHz clock before platform driver probe.

Risks: Preparing the 32 kHz oscillator blocks for 2.5 seconds because there is no status bit. `lpc18xx_creg_clk_probe()` uses `clk_register_creg_clk(NULL, ...)` rather than devm despite being in a platform probe, so clocks persist globally. Provider replacement must not break early consumers.

Test signals: Early consumers should resolve the 32 kHz clock; 1 kHz consumers should defer until platform probe. Enable/disable should update `EN32KHZ` and `EN1KHZ`. Prepare should clear `PD32KHZ` and `RESET32KHZ`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/nxp/clk-lpc18xx-creg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/nxp/clk-lpc32xx.c -->
# sources/distributed-fs/ceph-client/drivers/clk/nxp/clk-lpc32xx.c

Purpose: Implements the LPC32xx clock tree, including system clocks, PLLs, bus muxes/dividers, many peripheral gates, composite UART/PWM/SD/LCD clocks, DDRAM clock handling, and a separate USB clock provider.

Important APIs, types, and functions: `clk_proto[]` defines CCF-visible names, parents, and flags. `clk_hw_proto[]` defines fixed, mux, divider, gate, PLL, USB, and composite hardware descriptors. Custom ops include `clk_mask_ops`, PLL ops for `pll_397x`, `hclk_pll`, and `usb_pll`, DDRAM ops, UART divider recalc, USB enable/disable ops, and local mux/divider/gate ops over regmap. `lpc32xx_clk_register()` materializes a descriptor into a CCF clock.

Control flow: `lpc32xx_clk_init()` validates external `xtal_32k` and `xtal`, maps the system control block, creates a regmap, applies divider quirks to avoid zero values for PWM/MS clocks, registers clocks 1 through `LPC32XX_CLK_MAX - 1`, adds the main one-cell provider, sets USB PLL to 48 MHz, enables ARM/HCLK/VFP, and disables default NAND flash clocks. `lpc32xx_usb_clk_init()` maps USB clock registers, registers USB subclocks from offset IDs, and adds the USB provider.

State and persistence: Global `clk_regmap`, `usb_clk_vbase`, `clk[]`, and `usb_clk[]` persist after early init. Hardware registers hold clock state. PLL objects store most recently calculated divider mode parameters for subsequent `set_rate()`.

Dependencies and integration points: Depends on `dt-bindings/clock/lpc32xx-clock.h`, external oscillator DT clocks, regmap MMIO, and CCF one-cell providers for both main and USB clock nodes. USB clocks mix system-control and USB-controller register apertures.

Risks: PLL `set_rate()` depends on `determine_rate()` having populated in-memory `m_div`, `n_div`, `p_div`, and `mode`; direct set-rate without prior negotiation can fail. USB PLL only supports 48 MHz. Several muxes share one control bit but are registered as separate read-only muxes, so parent interpretations must stay synchronized. `lpc32xx_clk_register()` composite paths reuse union members carefully; changes to descriptor layout are high-risk.

Test signals: Boot should validate oscillator rates, register providers without errors, and show ARM/HCLK/VFP enabled. Rate tests should cover HCLK PLL closest-rate search and USB PLL 48 MHz setup. USB device/host enable paths should report `-EBUSY` when the opposite busy bit is set and should restore control state on timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/nxp/clk-lpc32xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/pistachio/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/pistachio/Kconfig

Purpose: Defines the config symbol for IMG Pistachio SoC clock-controller support.

Important APIs, types, and functions: `COMMON_CLK_PISTACHIO` is a bool depending on `MIPS || COMPILE_TEST`. Help text says to enable clock support for the IMG Pistachio SoC.

Control flow: Kconfig enables building the Pistachio clock support objects through parent Makefile logic.

State and persistence: No runtime state; this is configuration-only.

Dependencies and integration points: Allows native MIPS builds and compile-test coverage elsewhere.

Risks: As a bool, the driver is built-in when selected, matching the early `CLK_OF_DECLARE()` style used by the implementation. There is no per-subcontroller config split.

Test signals: `COMPILE_TEST=y` should allow building on non-MIPS architectures. Pistachio platform configs should select or enable this symbol so early clock providers exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/pistachio/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/pistachio/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/pistachio/Makefile

Purpose: Builds the Pistachio clock support objects.

Important APIs, types, and functions: Always adds `clk.o`, `clk-pll.o`, and `clk-pistachio.o` when the directory is entered.

Control flow: Kbuild links the provider helper, PLL implementation, and SoC descriptor/topology file together.

State and persistence: Build composition only.

Dependencies and integration points: Depends on parent Kbuild selecting this directory under `COMMON_CLK_PISTACHIO`. All three objects are required because the SoC topology calls helper and PLL registration functions.

Risks: There is no conditional split for subcontrollers; any build issue in one object affects the whole Pistachio clock driver.

Test signals: Build with `COMMON_CLK_PISTACHIO=y` and verify no unresolved symbols around `pistachio_clk_register_*`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/pistachio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/pistachio/clk-pistachio.c -->
# sources/distributed-fs/ceph-client/drivers/clk/pistachio/clk-pistachio.c

Purpose: Describes and registers the IMG Pistachio clock topology across the main clock controller, peripheral clock controller, CR peripheral gates, and CR top external gates.

Important APIs, types, and functions: Descriptor arrays define main gates, fixed factors, dividers, muxes, fixed PLLs, peripheral gates/dividers, system gates, and external gates. Init functions `pistachio_clk_init()`, `pistachio_clk_periph_init()`, `pistachio_cr_periph_init()`, and `pistachio_cr_top_init()` are bound with `CLK_OF_DECLARE()` compatibles. `pistachio_clk_force_enable()` keeps critical clocks on.

Control flow: Each init allocates a provider for its clock count, registers the relevant descriptor arrays through helper functions, registers the OF provider, and optionally force-enables critical clocks. The main controller also registers a debug mux with an explicit mux table.

State and persistence: Descriptor arrays are `__initdata`; registered CCF clocks and provider storage persist. Hardware state resides in MMIO registers. Critical clock enable counts persist after init.

Dependencies and integration points: Depends on `dt-bindings/clock/pistachio-clk.h`, helper functions from `clk.c` and `clk-pll.c`, and DT nodes with compatible strings `"img,pistachio-clk"`, `"img,pistachio-clk-periph"`, `"img,pistachio-cr-periph"`, and `"img,pistachio-cr-top"`.

Risks: The topology is table-driven; wrong IDs, offsets, shifts, or parent names create silent miswiring. Main PLLs are registered as fixed-parameter PLLs with no rate tables, so they expose current hardware rates but cannot be changed. Critical clocks must be force-enabled or the system can lose CPU/peripheral/DDR/ROM clocks.

Test signals: Boot should expose all four providers. `clk_summary` should show `mips`, core system clocks, peripheral gates, and external input gates. Critical clocks should be enabled even with no consumers. Debug mux parent selection should match the `mux_debug_idx` table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/pistachio/clk-pistachio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/pistachio/clk-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/pistachio/clk-pll.c

Purpose: Implements Pistachio PLL clocks for GF40LP fractional and low-area integer PLL types, with optional table-driven rate programming and fixed-rate recalc-only variants.

Important APIs, types, and functions: `struct pistachio_clk_pll` stores `clk_hw`, base, rate table, and rate count. `pll_register()` selects ops based on `enum pistachio_pll_type` and whether a rate table exists. Fractional ops manage `PLL_CTRL3/4`, mode selection, fractional fields, and recalc. Low-area integer ops manage `PLL_CTRL1/2` integer fields. `pistachio_clk_register_pll()` registers descriptor arrays into a provider.

Control flow: Enable clears power-down and bypass bits, then spins in `pll_lock()` until lock. Set-rate looks up exact table parameters, validates/warns for VCO and PFD constraints, writes divider fields, switches fractional/int mode where applicable, and relocks if already enabled. Determine-rate picks a table entry not exceeding the requested rate, defaulting to the first entry.

State and persistence: Per-PLL objects persist after registration. Rate configuration and power state persist in MMIO. Fixed PLL descriptors with no rate table expose enable/disable/recalc but no set-rate.

Dependencies and integration points: Used by `clk-pistachio.c`. Depends on table definitions in `struct pistachio_pll`, CCF, and hardware lock bit behavior.

Risks: `pll_lock()` has no timeout and can spin forever if the PLL never locks. Set-rate requires an exact rate-table match and warns, rather than fails, on several hardware constraint violations. Changing postdiv values while enabled is only warned about, not prevented.

Test signals: Recalc should match register encodings for both PLL types. Fault injection or hardware tests should verify lock behavior. Rate-table PLLs should reject missing parameters with `-EINVAL`; fixed PLLs should not expose set-rate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/pistachio/clk-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/pistachio/clk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/pistachio/clk.c

Purpose: Provides shared Pistachio clock-provider allocation and descriptor registration helpers for gates, muxes, dividers, fixed factors, PLLs, and critical clock enabling.

Important APIs, types, and functions: `pistachio_clk_alloc_provider()` allocates provider state, one-cell array, and maps the DT node. `pistachio_clk_register_provider()` warns about failed entries and adds an OF one-cell provider. `pistachio_clk_register_gate()`, `_mux()`, `_div()`, `_fixed_factor()`, and `_force_enable()` perform CCF registrations from descriptor arrays.

Control flow: SoC init files allocate a provider, register descriptor arrays, publish the provider, and optionally force-enable critical clocks. Mux width is computed from number of parents using `get_count_order()`.

State and persistence: Provider memory and clock array are allocated with `kzalloc()` and intentionally persist for early clock providers. The MMIO mapping persists in `p->base`. Clock state is hardware-backed.

Dependencies and integration points: Consumed by `clk-pistachio.c` and `clk-pll.c`. Depends on OF address mapping and CCF registration functions.

Risks: No cleanup path exists after partial registration failures, which is common for early clock providers but means failed entries remain in the provider array. Gate/mux/div registrations use no lock. `pistachio_clk_register_provider()` warns on `IS_ERR()` entries but still publishes the provider.

Test signals: Provider allocation failure should prevent registration cleanly. Boot logs should warn for failed individual clocks. Consumers should resolve clock IDs through `of_clk_src_onecell_get`. Critical force-enable errors should be logged with clock names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/pistachio/clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/pistachio/clk.h -->
# sources/distributed-fs/ceph-client/drivers/clk/pistachio/clk.h

Purpose: Defines Pistachio clock descriptor structures, construction macros, provider state, and shared registration function declarations.

Important APIs, types, and functions: Structures include `pistachio_gate`, `pistachio_mux`, `pistachio_div`, `pistachio_fixed_factor`, `pistachio_pll_rate_table`, `pistachio_pll`, and `pistachio_clk_provider`. Macros `GATE`, `MUX`, `DIV`, `DIV_F`, `FIXED_FACTOR`, `PLL`, and `PLL_FIXED` build descriptor arrays. Function declarations expose provider allocation, registration, PLL registration, and critical force-enable helpers.

Control flow: Descriptor macros are used by `clk-pistachio.c` to build static topology tables. Helper declarations are implemented in `clk.c` and `clk-pll.c`.

State and persistence: The header owns no runtime state but defines `pistachio_clk_provider`, whose instances hold the mapped base and one-cell data.

Dependencies and integration points: Depends on Linux CCF types and binding IDs supplied by includers. It is private to the Pistachio clock directory.

Risks: Macros hide field ordering and default flags; mistakes in macro arguments can create wrong clock IDs or parents with little compile-time protection. `MUX` calculates parent count from the array, so arrays must remain in scope as `__initconst` until registration.

Test signals: Build tests should catch structure signature drift. Runtime provider inspection should verify descriptor IDs map to expected binding IDs and parent names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/pistachio/clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/pxa/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/pxa/Makefile

Purpose: Builds Marvell PXA clock support objects.

Important APIs, types, and functions: Always builds `clk-pxa.o`. Adds `clk-pxa25x.o` for `CONFIG_PXA25x`, `clk-pxa27x.o` for `CONFIG_PXA27x`, and `clk-pxa3xx.o` for `CONFIG_PXA3xx`.

Control flow: Kbuild links the common CKEN/DT/frequency-change helpers plus the selected SoC-specific topology file.

State and persistence: No runtime state; controls object inclusion.

Dependencies and integration points: Common `clk-pxa.o` is required by all PXA SoC files. The listed config symbols must match architecture support.

Risks: `clk-pxa3xx.o` is referenced but outside this work item; build coverage should ensure the common interfaces remain compatible across all PXA variants.

Test signals: Build PXA25x, PXA27x, and PXA3xx configs. Link errors around `clk_pxa_cken_init()` or `pxa2xx_*` helpers indicate Makefile/interface drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/pxa/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/pxa/clk-pxa.c -->
# sources/distributed-fs/ceph-client/drivers/clk/pxa/clk-pxa.c

Purpose: Provides common PXA clock infrastructure for CKEN peripheral clocks, DT one-cell publishing, turbo switching, core PLL changes, and frequency selection.

Important APIs, types, and functions: `struct pxa_clk` combines low-power and high-power fixed factors with a gate. `clk_pxa_cken_init()` registers CKEN composite clocks. `clkdev_pxa_register()` populates the global one-cell array and clkdev aliases. `pxa2xx_core_turbo_switch()` toggles CLKCFG turbo state through ARM coprocessor p14. `pxa2xx_cpll_change()` safely updates CCCR and SDRAM refresh timing. `pxa2xx_determine_rate()` selects exact or closest supported frequency entries.

Control flow: SoC files define CKEN descriptors and call `clk_pxa_cken_init()`. Rate recalc chooses low-power or high-power fixed factor based on `is_in_low_power()`. Core PLL changes disable IRQs, preset MDREFR for safe SDRAM refresh, write CCCR, execute aligned coprocessor FCS sequence, post-update MDREFR, and restore IRQs.

State and persistence: Global `pxa_clocks[]` backs the DT one-cell provider. `pxa_clk_lock` protects CKEN gates. Frequency state persists in CCCR, CLKCFG, and MDREFR hardware registers.

Dependencies and integration points: Depends on PXA SMEMC helpers, ARM-specific p14 instructions, CCF, clkdev, and dt-binding clock IDs. SoC-specific files provide frequency tables and MDREFR DRI calculators.

Risks: The inline assembly is architecture-specific and timing-sensitive. Incorrect MDREFR preset/postset handling can corrupt SDRAM timing during frequency changes. CKEN composite clocks pass the same `struct clk_hw` as mux and rate hardware, requiring care if CCF internals change.

Test signals: Frequency transition tests should validate SDRAM remains stable and rates update in `clk_summary`. CKEN enable/disable should toggle expected bits under lock. DT consumers should resolve IDs through `clk_pxa_dt_common_init()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/pxa/clk-pxa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/pxa/clk-pxa.h -->
# sources/distributed-fs/ceph-client/drivers/clk/pxa/clk-pxa.h

Purpose: Defines common PXA clock macros, CKEN descriptors, PXA2xx frequency data, and shared function prototypes.

Important APIs, types, and functions: Provides CLKCFG bit definitions, helper macros for registering read-only rate clocks, mux clocks, and settable rate clocks, `struct desc_clk_cken`, `PXA_CKEN` and `PXA_CKEN_1RATE`, `struct pxa2xx_freq`, `dummy_clk_set_parent()`, and prototypes for common PXA registration and frequency-change helpers.

Control flow: PXA25x/PXA27x files use these macros to generate CCF registration functions and CKEN descriptor arrays. Common `clk-pxa.c` consumes `struct desc_clk_cken` and `struct pxa2xx_freq`.

State and persistence: Header owns no runtime state. It defines descriptor structures containing embedded CCF hardware that are copied or consumed during init.

Dependencies and integration points: Private contract between PXA common and SoC-specific clock files, plus dt-binding IDs from includers.

Risks: The macros generate static symbols and CCF ops; naming collisions or misuse are easy if new SoC code reuses macro names poorly. `PXA_CKEN` assumes two parents even for one-rate clocks by duplicating parent arrays.

Test signals: Build all PXA variants to catch macro-generated symbol errors. Review generated parent arrays and flags for each CKEN descriptor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/pxa/clk-pxa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/pxa/clk-pxa25x.c -->
# sources/distributed-fs/ceph-client/drivers/clk/pxa/clk-pxa25x.c

Purpose: Implements PXA25x clock topology, frequency reporting, CKEN peripheral clocks, PLL/core clocks, dummy legacy aliases, and DT early provider registration.

Important APIs, types, and functions: `pxa25x_get_clk_frequency_khz()` reports core/run/CPLL/memory rates. `clk_pxa25x_memory_get_rate()`, `clk_pxa25x_run_get_rate()`, `clk_pxa25x_cpll_get_rate()`, and `clk_pxa25x_core_get_parent()` decode CCCR/CLKCFG state. `clk_pxa25x_cpll_set_rate()` applies supported `pxa25x_freqs` entries through `pxa2xx_cpll_change()`. `pxa25x_clocks_init()` registers base, dummy, and CKEN clocks.

Control flow: Init stores the clock register base, registers fixed oscillators and peripheral PLL fixed factors, registers CPLL/run/core/memory clocks, registers dummy clkdev aliases for legacy devices, then registers CKEN gates. DT init ioremaps the fixed clock register address and publishes the common one-cell provider.

State and persistence: Static `clk_regs` holds MMIO base. CPLL and core state persists in CCCR/CLKCFG; memory refresh state is in SMEMC MDREFR. CKEN gate bits persist in CKEN.

Dependencies and integration points: Depends on PXA common helpers, PXA SMEMC row-count helpers, `clk-pxa2xx.h` register definitions, legacy clkdev device IDs, and DT binding IDs.

Risks: Only four frequency table entries are supported. `clk_pxa25x_memory_get_rate()` divides by M multiplier from CCCR; invalid encodings could divide by zero. DT init uses a hard-coded physical register address. Dummy clocks preserve legacy API behavior but can mask missing real pin clock control.

Test signals: `pxa25x_get_clk_frequency_khz(1)` should print expected run/turbo/memory rates. Test CPLL changes across supported table entries and validate MDREFR DRI updates. CKEN bits should match peripherals such as MMC, I2C, UARTs, USB, SSP, LCD, and MEMC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/pxa/clk-pxa25x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/pxa/clk-pxa27x.c -->
# sources/distributed-fs/ceph-client/drivers/clk/pxa/clk-pxa27x.c

Purpose: Implements PXA27x clock topology, including richer core/run/system-bus/memory/LCD-base clock derivation, PXA27x CKEN peripherals, supported CPLL frequency changes, dummy aliases, and DT early provider setup.

Important APIs, types, and functions: `pxa27x_get_clk_frequency_khz()` reports core/run/CPLL/memory/system-bus rates. `pxa27x_is_ppll_disabled()` selects low-power peripheral parent. Rate callbacks include `clk_pxa27x_cpll_get_rate()`, `_run_get_rate()`, `_system_bus_get_rate()`, `_memory_get_rate()`, and `_lcd_base_get_rate()`. Parent callbacks interpret oscillator-forced, fast-bus, turbo, A-bit, and LCD divider state. `clk_pxa27x_cpll_set_rate()` applies entries from `pxa27x_freqs`.

Control flow: Init registers fixed oscillators and PPLL, core CPLL/run/core clocks, system bus, memory, LCD base, dummy legacy aliases, and CKEN clocks. DT init maps the clock registers at the fixed physical address and publishes the common provider.

State and persistence: Static `clk_regs` points to PXA clock registers. Frequency state persists in CCSR/CCCR/CLKCFG and SMEMC MDREFR. CKEN bits persist per peripheral.

Dependencies and integration points: Depends on common PXA code, `clk-pxa2xx.h`, PXA SMEMC helpers, clkdev aliases for legacy platform devices, and dt-binding IDs.

Risks: The file supports only selected frequency combinations from the manual. Parent/rate callbacks rely on CCSR and CCCR fields being coherent after FCS. `pxa27x_register_plls()` registers `osc_32_768khz` as `32768 * KHz`, which should be scrutinized because the name implies 32.768 kHz but the value is 32.768 MHz. Hard-coded DT ioremap address limits portability.

Test signals: Validate reported frequencies for each `pxa27x_freqs` entry. Test oscillator-forced and PPLL-disabled states for correct parent selection. Check CKEN clocks for UARTs, I2C, USB, SSP, keypad, LCD, camera, and memory controller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/pxa/clk-pxa27x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/pxa/clk-pxa2xx.h -->
# sources/distributed-fs/ceph-client/drivers/clk/pxa/clk-pxa2xx.h

Purpose: Defines PXA2xx clock-register offsets and bit masks shared by PXA25x and PXA27x clock drivers.

Important APIs, types, and functions: Provides offsets for `CCCR`, `CCSR`, `CKEN`, and `OSCC`; masks and bit positions for CCCR/CCSR frequency fields; CKEN bit assignments for peripherals; and OSCC 32.768 kHz oscillator bits.

Control flow: SoC-specific PXA clock files include this header to decode frequency registers and build CKEN descriptors with `CKEN_*` bit constants.

State and persistence: No state. It describes hardware register layout.

Dependencies and integration points: Private to PXA2xx clock support. Must match the processor reference manuals and the PXA dt-binding clock IDs used by higher-level code.

Risks: Several CKEN bit numbers are aliases across SoC variants, for example USB host/NSSP and SSP/SSP2. Callers must use the correct symbol for their SoC. Wrong masks here directly break rate computation or peripheral gating.

Test signals: Register readback tests for CCCR/CCSR fields should match computed rates. Peripheral enable tests should confirm the expected CKEN bits toggle for each PXA25x/PXA27x device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/pxa/clk-pxa2xx.h -->
