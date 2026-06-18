# subset-b-001105 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/c3-peripherals.c -->
## sources/distributed-fs/ceph-client/drivers/clk/meson/c3-peripherals.c

### Purpose
`c3-peripherals.c` describes the Amlogic C3 peripheral clock controller. It is mostly declarative clock-tree data: RTC, system/APB gates, AXI gates, 12/24 MHz output, general-purpose clocks, PWM, SPI, eMMC/SD, transport stream, Ethernet, display, video codec, ISP, NNA, GE2D, and VAPB clocks. The controller is exposed as a platform driver for `amlogic,c3-peripherals-clkc`.

### Important APIs, Types, And Functions
The file defines register offsets for the C3 peripheral clock block and uses `struct clk_regmap`, `struct clk_fixed_factor`, `struct clk_parent_data`, `struct meson_clk_dualdiv_param`, and `struct meson_clkc_data`. `C3_SYS_PCLK()` and `C3_AXI_PCLK()` wrap `MESON_PCLK()` gate declarations, while `C3_COMP_SEL()`, `C3_COMP_DIV()`, and `C3_COMP_GATE()` build the common mux/divider/gate triplets. The final `c3_peripherals_hw_clks[]` array maps dt-binding `CLKID_*` indices to `clk_hw` objects, and `c3_peripherals_clkc_driver` delegates probe to `meson_clkc_mmio_probe()`.

### Control Flow
There is no custom runtime algorithm. At platform probe, `meson_clkc_mmio_probe()` ioremaps the clock controller register resource, creates a regmap, registers each non-null hardware clock from `c3_peripherals_clkc_data`, and installs the OF clock provider. Later common clock framework calls operate through the generic regmap gate, mux, divider, fixed-factor, and dual-divider ops selected in each initializer.

### State, Persistence, And Dependencies
State persists in the C3 clock controller registers and in kernel `clk_hw` registrations. Gate clocks mutate individual enable bits in `SYS_CLK_EN0_REG*`, `AXI_CLK_EN0`, and per-block clock-control registers. Muxes and dividers mutate parent-select and divisor bitfields. The RTC 32 kHz path uses `meson_clk_dualdiv_ops` with a table entry designed to synthesize 32.768 kHz from the oscillator. Dependencies include `clk-regmap.h`, `clk-dualdiv.h`, `meson-clkc-utils.h`, Linux common clock framework APIs, platform-device probing, and `dt-bindings/clock/amlogic,c3-peripherals-clkc.h`.

### Integration Points
The dt-binding IDs are the public contract for device-tree consumers. Parent clocks are resolved by firmware names such as `oscin`, `xtal_24m`, `sysclk`, `axiclk`, `fix`, `gp0`, `gp1`, `hifi`, and fixed PLL divider names. Several clocks are marked `CLK_IS_CRITICAL` because disabling them would break CPU control, interrupt routing, GIC, system NIC, or CPU-to-DDR access. Media and peripheral drivers consume the registered clocks through normal `clocks = <&clkc CLKID_...>` phandles.

### Risks And Edge Cases
The file is data-heavy, so the main risks are wrong register offsets, parent order, bit shifts, or dt-binding indices. Critical-clock annotations are part of platform safety; missing one can allow Linux unused-clock cleanup to disable essential interconnects. Some comments describe hardware quirks: DDR-related `sys_mmc_pclk` is read-only because firmware initializes DDR, and some divider encodings have non-obvious zero behavior. Since this source snapshot has several historically suspicious duplicated lines in adjacent C3 clock files, compile and dt-binding validation are especially useful for catching initializer mistakes in this area. Sparse `c3_peripherals_hw_clks[]` entries also need to stay aligned with the binding header.

### Test Signals
Useful signals include kernel build coverage with C3 clock configs enabled, probe success for `amlogic,c3-peripherals-clkc`, `clk_summary` inspection for all expected IDs, parent/rate changes for PWM/SPI/eMMC/Ethernet/display/video clocks, RTC 32 kHz rate checks, and boot tests verifying critical clocks remain enabled. Device-tree validation should confirm all provider references use valid C3 peripheral IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/c3-peripherals.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/c3-pll.c -->
## sources/distributed-fs/ceph-client/drivers/clk/meson/c3-pll.c

### Purpose
`c3-pll.c` describes the Amlogic C3 PLL clock controller. It exposes fixed PLL-derived outputs, GP0 PLL, HIFI PLL, and MCLK PLL paths, plus two MCLK output chains. The driver registers the `amlogic,c3-pll-clkc` provider and maps C3 PLL dt-binding IDs to clock hardware.

### Important APIs, Types, And Functions
The source uses `struct clk_regmap`, `struct clk_fixed_factor`, `struct clk_div_table`, `struct pll_mult_range`, and `struct reg_sequence`. PLL DCO nodes use `meson_clk_pll_ops`; output dividers use `clk_regmap_divider_ops`; fixed PLL dividers use fixed-factor clocks and read-only gates; MCLK selectors and gates use generic regmap mux/gate ops. `c3_pll_hw_clks[]` is the dt-binding ID map, `c3_pll_clkc_data` is the common registration payload, and `c3_pll_clkc_driver` probes through `meson_clkc_mmio_probe()`.

### Control Flow
Probe is generic: map the MMIO resource, create a regmap, register every clock in the C3 PLL array, and add an OF provider. Runtime PLL enable, disable, recalc, determine-rate, and set-rate behavior is delegated to `clk-pll.c`. GP0 and HIFI PLLs have initialization register sequences and multiplier ranges; MCLK PLL has an init sequence, an OD divider, a special one-based/allow-zero post divider, and MCLK0/MCLK1 mux/divider/gate chains.

### State, Persistence, And Dependencies
Persistent hardware state is in ANACTRL registers such as `ANACTRL_FIXPLL_CTRL4`, `ANACTRL_GP0PLL_CTRL*`, `ANACTRL_HIFIPLL_CTRL*`, and `ANACTRL_MPLL_CTRL*`. Linux state is the registered `clk_hw` graph. Dependencies include `clk-regmap.h`, `clk-pll.h`, `meson-clkc-utils.h`, platform probing, fixed-factor clock ops, and `dt-bindings/clock/amlogic,c3-pll-clkc.h`.

### Integration Points
Other C3 clock controllers and device-tree consumers refer to parent names such as `fix`, `top`, `mclk`, `fdiv2`, `fdiv2p5`, `fdiv3`, `fdiv4`, `fdiv5`, `fdiv7`, `gp0`, and `hifi`. The output table makes PLL-generated clocks available to peripheral controllers and audio/MCLK users. The implementation relies on the common Meson PLL helper for lock polling and rate programming.

### Risks And Edge Cases
PLL init sequences are tightly coupled to silicon programming manuals; wrong constants can prevent lock or produce unstable rates. OD tables intentionally limit supported encodings below the raw bitfield maximum. The source should be compiled as part of validation because initializer syntax and duplicated initializer fields in this kind of declarative table are easy to miss in review. Rate changes inherit `clk-pll.c` behavior, including temporary disable/re-enable and fallback attempts if the PLL does not lock.

### Test Signals
Build coverage with C3 PLL enabled, probe of `amlogic,c3-pll-clkc`, `clk_summary` inspection of fixed and programmable PLL outputs, rate-set tests for GP0/HIFI/MCLK PLLs, lock-failure logging checks, and audio MCLK consumer tests are high-value. Device-tree tests should confirm all named parent clocks are provided and every `CLKID_*` entry matches the binding header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/c3-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/clk-cpu-dyndiv.c -->
## sources/distributed-fs/ceph-client/drivers/clk/meson/clk-cpu-dyndiv.c

### Purpose
`clk-cpu-dyndiv.c` implements the Meson CPU dynamic divider clock type. It is a small common-clock helper used by CPU frequency paths where hardware requires a dynamic-enable bit to be asserted before divider changes and cleared as part of the divider update.

### Important APIs, Types, And Functions
The exported API is `meson_clk_cpu_dyndiv_ops`. Internally, `meson_clk_cpu_dyndiv_data()` casts `clk_regmap->data`, `meson_clk_cpu_dyndiv_recalc_rate()` reads the divider field and calls `divider_recalc_rate()`, `meson_clk_cpu_dyndiv_determine_rate()` delegates to `divider_determine_rate()`, and `meson_clk_cpu_dyndiv_set_rate()` computes a divider encoding with `divider_get_val()`.

### Control Flow
For a rate change, the helper computes the divider value from the requested and parent rates. It writes the dynamic-enable parameter to `1`, then performs one `regmap_update_bits()` that writes the divider bits while clearing the dynamic-enable bits by including both masks and only setting the shifted divider value. Recalc and determine paths are read-only calculations through the Linux divider helpers.

### State, Persistence, And Dependencies
The only persistent state is the hardware register bitfields described by `struct meson_clk_cpu_dyndiv_data`: `div` and `dyn`. The helper depends on `clk-regmap.h`, `clk-cpu-dyndiv.h`, `parm.h` accessors, regmap update semantics, and common clock divider helpers. It exports its ops under the `CLK_MESON` namespace.

### Integration Points
SoC clock-tree files instantiate `struct clk_regmap` objects with `.ops = &meson_clk_cpu_dyndiv_ops` for CPU dynamic divider nodes. CPU DVFS notifiers in SoC drivers rely on this divider being safely reprogrammed while the CPU clock is parked on a safe alternate path.

### Risks And Edge Cases
`divider_get_val()` failures propagate directly. The set-rate sequence assumes hardware expects the dynamic bit asserted before changing the divider and that clearing it in the same masked update as the divider write is correct. There is no local locking beyond regmap serialization; higher-level CPU clock notifiers must protect against unsafe live CPU clock changes.

### Test Signals
Tests should cover recalc/determine math for the configured divider width, set-rate register updates that first set `dyn` and then update `div`, invalid requested rates, and CPU DVFS transitions that verify no lockups or unstable intermediate frequencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/clk-cpu-dyndiv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/clk-cpu-dyndiv.h -->
## sources/distributed-fs/ceph-client/drivers/clk/meson/clk-cpu-dyndiv.h

### Purpose
`clk-cpu-dyndiv.h` declares the data contract for the Meson CPU dynamic divider helper and exposes its common-clock operations to SoC clock-controller files.

### Important APIs, Types, And Functions
`struct meson_clk_cpu_dyndiv_data` contains two `struct parm` fields: `div` for the divider bitfield and `dyn` for the dynamic-enable bitfield. The header declares `extern const struct clk_ops meson_clk_cpu_dyndiv_ops`.

### Control Flow
The header contains no executable control flow. Consumers fill the parameter descriptors in static clock initializers and assign the exported ops to a `struct clk_regmap`.

### State, Persistence, And Dependencies
State is not stored by the header itself. It depends on Linux `clk-provider.h` for `struct clk_ops` and on local `parm.h` for register-field descriptors. The described state persists in SoC clock registers when the implementation writes those parameters.

### Integration Points
Included by CPU clock implementation files that need the special dynamic divider update sequence. The type is consumed by `clk-cpu-dyndiv.c` through `clk_regmap->data`.

### Risks And Edge Cases
Incorrect `parm` widths or shifts in SoC data will cause the implementation to update the wrong register bits. Because the header only declares the contract, compile-time type checks are limited to the structure shape.

### Test Signals
Build tests for SoC clock files using this header and runtime register-update tests for every instantiated CPU dynamic divider are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/clk-cpu-dyndiv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/clk-dualdiv.c -->
## sources/distributed-fs/ceph-client/drivers/clk/meson/clk-dualdiv.c

### Purpose
`clk-dualdiv.c` implements the Meson dual-divider clock type, originally used in always-on domains to derive precise low-frequency clocks such as 32.768 kHz for suspend, RTC, and CEC. The hardware can run either a single divider or alternate between two divider/counter pairs.

### Important APIs, Types, And Functions
The exported APIs are `meson_clk_dualdiv_ops` and `meson_clk_dualdiv_ro_ops`. `__dualdiv_param_to_rate()` computes the effective rate from table parameters. `meson_clk_dualdiv_recalc_rate()` reads the `dual`, `n1`, `m1`, `n2`, and `m2` fields from hardware. `__dualdiv_get_setting()` searches the static table for exact or closest settings. `determine_rate` reports the achievable rate, and `set_rate` writes the chosen table values minus one into the hardware fields.

### Control Flow
Rate selection is table-driven. Determine-rate and set-rate both call `__dualdiv_get_setting()`. Exact matches return immediately; otherwise the table entry with the smallest absolute rate error is selected. Set-rate rejects controllers without a table, then writes all five parameter fields. The read-only ops omit `set_rate` and only expose initialization and recalculation.

### State, Persistence, And Dependencies
State persists in the dual-divider register fields described by `struct meson_clk_dualdiv_data`. The implementation depends on `clk-regmap.h`, `clk-dualdiv.h`, `parm.h`, regmap-backed field helpers, Linux common clock registration, and rate rounding helpers. Table entries are expected to end with a sentinel where `n1 == 0`.

### Integration Points
C3 peripheral RTC clocks and G12A AO RTC/CEC clocks instantiate this helper. Consumers see it as a normal common-clock divider-like node whose exact behavior is constrained by the provided hardware-valid table.

### Risks And Edge Cases
If no table is provided, `determine_rate()` falls back to the current hardware rate but `set_rate()` fails with `-EINVAL`. The closest-rate calculation initializes `best` to zero; for very low target rates the absolute-difference comparison still converges, but table quality determines the result. All written values subtract one, so table entries must use human divider/count values, not raw bit encodings.

### Test Signals
Tests should verify exact and closest matches for the 32 kHz tables, recalc from programmed raw fields, set-rate writes for single and dual modes, missing-table behavior, and sentinel handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/clk-dualdiv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/clk-dualdiv.h -->
## sources/distributed-fs/ceph-client/drivers/clk/meson/clk-dualdiv.h

### Purpose
`clk-dualdiv.h` defines the table and register-field contract for Meson dual-divider clocks and declares the mutable/read-only ops exported by the implementation.

### Important APIs, Types, And Functions
`struct meson_clk_dualdiv_param` stores one table setting: `n1`, `n2`, `m1`, `m2`, and `dual`. `struct meson_clk_dualdiv_data` describes the five hardware fields as `struct parm` values plus a pointer to the settings table. The header declares `meson_clk_dualdiv_ops` and `meson_clk_dualdiv_ro_ops`.

### Control Flow
There is no runtime logic in the header. SoC files provide static table data and field descriptors; `clk-dualdiv.c` interprets them during recalc, determine-rate, and set-rate calls.

### State, Persistence, And Dependencies
The header itself is stateless. It depends on `clk-provider.h` and `parm.h`. Persistent state is the hardware register state represented by consumers' `parm` descriptors and the static table lifetime of the parameter arrays.

### Integration Points
Included by AO/peripheral clock-controller files that need precise low-frequency generation. The read-only ops let SoC files expose firmware-programmed dual dividers without allowing Linux to modify them.

### Risks And Edge Cases
The table sentinel convention is implicit in the C implementation. If a consumer omits the terminating zero entry or uses raw encodings instead of natural values, rate calculations and register writes will be wrong.

### Test Signals
Compile coverage for all users, table-sentinel checks in review, and runtime rate checks for every dual-divider consumer validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/clk-dualdiv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/clk-mpll.c -->
## sources/distributed-fs/ceph-client/drivers/clk/meson/clk-mpll.c

### Purpose
`clk-mpll.c` implements Meson MPLL clocks. MPLLs are PLL-derived outputs with fractional scaling, modeled as `parent_rate / (N2 + SDM/16384)`. They provide audio and fixed-rate derived clocks with optional spread-spectrum and initialization register programming.

### Important APIs, Types, And Functions
The exported ops are `meson_clk_mpll_ops` and `meson_clk_mpll_ro_ops`. `rate_from_params()` converts SDM/N2 fields to a rate. `params_from_rate()` computes SDM/N2 for a requested rate, respecting `CLK_MESON_MPLL_ROUND_CLOSEST`. `mpll_recalc_rate()`, `mpll_determine_rate()`, and `mpll_set_rate()` implement common clock callbacks. `mpll_init()` runs optional init sequences, enables fractional SDM, optionally sets spread spectrum, and sets a misc bit when provided.

### Control Flow
Initialization first calls `clk_regmap_init()`, then optionally writes the init register sequence. It always enables the SDM fractional part and conditionally programs spread-spectrum and misc fields. Determine-rate computes bounded N2/SDM parameters and returns the achievable rate. Set-rate writes SDM first and then N2.

### State, Persistence, And Dependencies
Persistent state is the MPLL register fields described by `struct meson_clk_mpll_data`: `sdm`, `sdm_en`, `n2`, `ssen`, `misc`, optional init regs, and flags. Dependencies include `clk-regmap.h`, `clk-mpll.h`, `parm.h`, `regmap_multi_reg_write()`, Linux common clock helpers, `do_div()`, and module namespace exports.

### Integration Points
SoC clock files instantiate MPLL divider nodes for audio and fixed-frequency trees, commonly with init sequences. Read-only ops expose firmware-owned MPLLs while still allowing recalc/determine. The helper relies on parent PLL rates supplied by the surrounding clock tree.

### Risks And Edge Cases
`N2_MIN` and `N2_MAX` clamp impossible rates; callers may receive a rounded/clamped rate rather than the request. `rate_from_params()` rejects `n2 < 4` and recalc reports zero on invalid hardware state. Spread-spectrum and misc fields are optional via `MESON_PARM_APPLICABLE()`, so SoC descriptors must use null parameters correctly. Init sequences alter hardware immediately on registration.

### Test Signals
Tests should cover rate-to-parameter conversion at min/max N2, round-up versus round-closest behavior, recalc from raw SDM/N2 values, init register writes, SDM enablement, spread-spectrum flag behavior, and read-only consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/clk-mpll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/clk-mpll.h -->
## sources/distributed-fs/ceph-client/drivers/clk/meson/clk-mpll.h

### Purpose
`clk-mpll.h` declares the data structure and flags used by Meson MPLL common-clock operations.

### Important APIs, Types, And Functions
`struct meson_clk_mpll_data` describes SDM, SDM enable, integer divider N2, spread-spectrum enable, misc bit, optional init sequence, init count, and flags. The flags are `CLK_MESON_MPLL_ROUND_CLOSEST` and `CLK_MESON_MPLL_SPREAD_SPECTRUM`. The header declares read-only and mutable `clk_ops` exports.

### Control Flow
The header has no executable logic. SoC files fill the descriptors and choose either `meson_clk_mpll_ops` or `meson_clk_mpll_ro_ops`.

### State, Persistence, And Dependencies
It is stateless by itself and depends on `clk-provider.h`, `spinlock.h`, and `parm.h`. Runtime state persists in the hardware registers addressed by the `parm` fields.

### Integration Points
Included by Meson SoC clock-controller files with MPLL outputs. The optional `reg_sequence` pointer links SoC-specific magic init values to the shared implementation.

### Risks And Edge Cases
Omitting optional fields is valid only when the implementation checks `MESON_PARM_APPLICABLE()`. Incorrect init counts or flag choices can change spread-spectrum behavior or rate rounding across all consumers of an MPLL.

### Test Signals
Build coverage plus SoC-specific clock-rate checks around MPLL consumers are the useful validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/clk-mpll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/clk-phase.c -->
## sources/distributed-fs/ceph-client/drivers/clk/meson/clk-phase.c

### Purpose
`clk-phase.c` implements Meson phase-control clock ops. It supports a simple single phase bitfield, an audio triphase clock where three phase fields must stay synchronized, and a special serial-clock word-select inverter where the word-select bit is the inverse of the phase bit.

### Important APIs, Types, And Functions
The exports are `meson_clk_phase_ops`, `meson_clk_triphase_ops`, and `meson_sclk_ws_inv_ops`. Helpers convert between register values and degrees using `phase_step(width)`. Single-phase callbacks read/write `ph`. Triphase callbacks synchronize `ph1` and `ph2` to `ph0` during init and update all three on set. SCLK word-select callbacks synchronize/write `ws` to the inverse of the phase value.

### Control Flow
Single phase get/set is direct field read/write. Triphase init calls `clk_regmap_init()`, reads phase 0, writes that value to phases 1 and 2, and later reports phase 0 as authoritative. SCLK WS inverter init calls `clk_regmap_init()`, reads `ph`, and writes `ws` as `!ph`; set-phase repeats that paired update.

### State, Persistence, And Dependencies
State persists in the phase and word-select register fields described by the corresponding header structs. Dependencies include `clk-regmap.h`, `clk-phase.h`, `parm.h`, common-clock phase callbacks, and `DIV_ROUND_CLOSEST()`.

### Integration Points
Audio clock-controller descriptions use these ops to expose I2S/TDM phase controls through the common clock framework. The triphase abstraction intentionally presents one phase knob even though hardware has multiple output/input phase fields.

### Risks And Edge Cases
`phase_step(width)` uses integer division of 360 by `2^width`, so unsupported widths that do not evenly divide 360 would lose precision. `degrees_to_val()` wraps a rounded 360-degree request back to zero. The SCLK WS helper assumes a binary phase field; wider fields would make `val ? 0 : 1` too coarse unless hardware semantics match.

### Test Signals
Tests should verify degree/value conversion for supported widths, 360-degree wraparound, triphase init synchronization, triphase set writing all fields, and word-select inversion on init and set-phase.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/clk-phase.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/clk-phase.h -->
## sources/distributed-fs/ceph-client/drivers/clk/meson/clk-phase.h

### Purpose
`clk-phase.h` declares the register-field descriptors and ops for Meson phase-control clocks.

### Important APIs, Types, And Functions
`struct meson_clk_phase_data` contains one phase `parm`. `struct meson_clk_triphase_data` contains `ph0`, `ph1`, and `ph2`. `struct meson_sclk_ws_inv_data` contains a phase field and a word-select field. The header declares `meson_clk_phase_ops`, `meson_clk_triphase_ops`, and `meson_sclk_ws_inv_ops`.

### Control Flow
No executable logic lives in the header. SoC clock descriptions attach these data structs to `clk_regmap` instances and pick the desired ops.

### State, Persistence, And Dependencies
The header is stateless and depends on `clk-provider.h` and `parm.h`. Persistent state is the hardware phase/word-select register state managed by the implementation.

### Integration Points
Included by audio-focused Meson clock-controller files that need phase controls surfaced through common clock phase APIs.

### Risks And Edge Cases
The structures encode semantic contracts that are not type-enforced: triphase fields must be equivalent-width compatible fields, and the SCLK word-select field must represent the inverse phase relation expected by the implementation.

### Test Signals
Compile coverage of users and runtime clock phase get/set tests for each instantiated phase type validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/clk-phase.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/clk-pll.c -->
## sources/distributed-fs/ceph-client/drivers/clk/meson/clk-pll.c

### Purpose
`clk-pll.c` implements shared Meson PLL common-clock operations. It models PLL DCO rates as `parent * (m + frac/frac_max) / n`, supports table-driven or range-driven settings, handles lock polling, initialization sequences, enable/disable, PCIe-specific enable retry, and mutable/read-only ops.

### Important APIs, Types, And Functions
Exports are `meson_clk_pll_ops`, `meson_clk_pll_ro_ops`, and `meson_clk_pcie_pll_ops`. Key helpers include `__pll_params_to_rate()`, `__pll_params_with_frac()`, `meson_clk_get_pll_settings()`, `meson_clk_pll_determine_rate()`, `meson_clk_pll_wait_lock()`, `meson_clk_pll_is_enabled()`, `meson_clk_pll_init()`, `meson_clk_pll_enable()`, `meson_clk_pll_disable()`, and `meson_clk_pll_set_rate()`.

### Control Flow
Rate determination searches either a multiplier range or a parameter table. It chooses the best integer M/N pair, then optionally improves the result with a fractional field. Initialization obtains a regmap, optionally skips reinitializing a bootloader-enabled PLL when `CLK_MESON_PLL_NOINIT_ENABLED` is set, otherwise asserts reset, writes init registers, and deasserts reset. Enable asserts reset if available, enables the PLL, releases reset, optionally follows newer self-adaption current and lock-detect sequences, then polls lock. Set-rate disables an enabled PLL, writes N/M/fractional settings, re-enables it, and attempts to restore the old rate if relock fails.

### State, Persistence, And Dependencies
Persistent state is entirely in PLL control registers described by `struct meson_clk_pll_data`: enable, M, N, fractional, lock, reset, optional current/lock-detect fields, init sequences, range/table data, fractional max, and flags. Dependencies include `clk-regmap.h`, `clk-pll.h`, `parm.h`, regmap multi-write, Linux delay helpers, 64-bit math helpers, and common clock callbacks.

### Integration Points
SoC clock-controller files use this helper for system, GP, HIFI, HDMI, PCIe, and other PLLs. The PCIe ops intentionally reuse init/enable sequencing for a fixed precise 100 MHz reference clock and omit `set_rate`. Downstream dividers and muxes rely on accurate PLL recalc and set-rate propagation through `CLK_SET_RATE_PARENT`.

### Risks And Edge Cases
PLL lock polling waits up to about 100 ms and returns `-ETIMEDOUT`; enable maps that to `-EIO`. The set-rate failure path recursively calls `meson_clk_pll_set_rate()` to restore the old rate, and the source comment notes this could be unsafe if the old rate also cannot lock. Fractional calculations use round-up or round-closest flags and clamp to `frac_max - 1`, so exactness depends on descriptor fields. A zero hardware N returns rate zero to avoid division by zero. Init sequences can perturb bootloader-programmed PLLs unless the no-init-enabled flag is correctly applied.

### Test Signals
High-value tests include recalc for integer and fractional PLLs, table and range selection, round-down versus round-closest behavior, zero-N handling, enable/disable bit sequences, lock timeout behavior, PCIe retry behavior, no-init-enabled boot handoff, and set-rate failure recovery. Hardware boot tests should monitor PLL lock status and downstream clock stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/clk-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/clk-pll.h -->
## sources/distributed-fs/ceph-client/drivers/clk/meson/clk-pll.h

### Purpose
`clk-pll.h` defines the shared Meson PLL data model used by PLL clock-controller declarations and exposes the PLL common-clock ops.

### Important APIs, Types, And Functions
`struct pll_params_table` stores one M/N pair and is usually populated through `PLL_PARAMS(_m, _n)`. `struct pll_mult_range` declares a legal multiplier range. `struct meson_clk_pll_data` describes all PLL bitfields, optional init sequences, parameter tables or ranges, fractional maximum, and flags. Flags are `CLK_MESON_PLL_ROUND_CLOSEST` and `CLK_MESON_PLL_NOINIT_ENABLED`. The header declares read-only, mutable, and PCIe PLL ops.

### Control Flow
The header contains no runtime logic. It establishes the structure consumed by `clk-pll.c`; SoC files choose either table-driven or range-driven settings and supply any required init sequence.

### State, Persistence, And Dependencies
The header is stateless and depends on `clk-provider.h`, `regmap.h`, and `parm.h`. Runtime persistence is in hardware registers pointed to by the `parm` descriptors and in static parameter/init tables.

### Integration Points
Included by Meson SoC PLL description files. The exported ops connect static SoC descriptors to Linux common clock framework behavior.

### Risks And Edge Cases
Descriptors must not provide inconsistent tables/ranges, invalid bit widths, or init counts. Missing optional `rst`, `frac`, `current_en`, or `l_detect` fields are supported only because the implementation checks applicability. Table arrays require a sentinel entry with `n == 0`.

### Test Signals
Build coverage of every PLL descriptor, review of table sentinels and bit widths, and runtime PLL rate/lock tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/clk-pll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/clk-regmap.c -->
## sources/distributed-fs/ceph-client/drivers/clk/meson/clk-regmap.c

### Purpose
`clk-regmap.c` provides generic regmap-backed Meson clock ops for gates, dividers, and muxes, plus initialization logic that discovers and caches the relevant regmap for a `struct clk_regmap`.

### Important APIs, Types, And Functions
The exported initialization function is `clk_regmap_init()`. Exported ops are `clk_regmap_gate_ops`, `clk_regmap_gate_ro_ops`, `clk_regmap_divider_ops`, `clk_regmap_divider_ro_ops`, `clk_regmap_mux_ops`, and `clk_regmap_mux_ro_ops`. Internal helpers implement gate enable/disable/is_enabled, divider recalc/determine/set_rate, and mux get_parent/set_parent/determine_rate.

### Control Flow
Initialization returns early if `clk->map` is already preset. Otherwise it first asks the clock's device for a regmap, then falls back to the parent DT node via `syscon_node_to_regmap()`. Gate enable/disable performs masked `regmap_update_bits()` and honors `CLK_GATE_SET_TO_DISABLE`. Divider callbacks read, mask, and pass encodings through Linux divider helpers; read-only dividers use `divider_ro_determine_rate()` with the current value. Mux callbacks convert between register values and framework parent indices.

### State, Persistence, And Dependencies
The cached `struct regmap *` in `struct clk_regmap` is persistent kernel state after init. Hardware state persists in the target registers. Dependencies include Linux device/regmap/syscon/OF APIs, `clk-provider.h` helpers for dividers and muxes, and local `clk-regmap.h`.

### Integration Points
Almost every Meson SoC clock file uses these ops for simple gates, muxes, and dividers. The implementation bridges SoC-specific static descriptors to both syscon-backed legacy controllers and newer platform-device MMIO controllers.

### Risks And Edge Cases
`clk_regmap_init()` couples clock type initialization to controller topology and contains a FIXME noting this is a temporary design. If neither device nor parent syscon provides a regmap, registration fails with `-EINVAL`. `clk_regmap_mux_get_parent()` returns an `int` error through a `u8` callback type, which can collapse negative errors into large unsigned values; this mirrors common clock callback constraints but makes read failures hard to report cleanly. HIWORD mask flags are documented as ignored.

### Test Signals
Tests should cover init with preset, device, and parent-syscon regmaps; gate polarity with and without `CLK_GATE_SET_TO_DISABLE`; divider recalc/set/determine including read-only mode; mux parent value/index conversion with tables; and probe failure when no regmap is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/clk-regmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/clk-regmap.h -->
## sources/distributed-fs/ceph-client/drivers/clk/meson/clk-regmap.h

### Purpose
`clk-regmap.h` defines the common data structures for Meson regmap-backed clocks and declares the generic gate, divider, and mux ops.

### Important APIs, Types, And Functions
`struct clk_regmap` embeds `struct clk_hw`, caches a `struct regmap *`, and stores type-specific `data`. `to_clk_regmap()` converts from `clk_hw`. `struct clk_regmap_gate_data`, `struct clk_regmap_div_data`, and `struct clk_regmap_mux_data` describe register offsets, bit positions, widths/masks, flags, tables, and mux value tables. Inline helpers cast `clk->data` to the specific data type.

### Control Flow
The header contains no complex control flow. It provides declarations and inline casts used by `clk-regmap.c` and SoC clock declaration files.

### State, Persistence, And Dependencies
Runtime state is the cached regmap pointer and the hardware register state described by each data struct. The header depends on Linux device, common clock, and regmap types.

### Integration Points
This is the central contract for Meson clock-controller data files. Higher-level helper headers such as PLL, MPLL, dual-divider, and phase still rely on `struct clk_regmap` to carry their data and regmap.

### Risks And Edge Cases
The `void *data` member makes the selected ops and data type a manual contract. Pairing mux ops with divider data, wrong bit widths, or stale regmap pointers will not be caught by the type system. Comments note that HIWORD mask variants of generic flags are ignored.

### Test Signals
Compile coverage catches structure availability; runtime tests must verify each instantiated clock uses matching ops/data and correct register fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/clk-regmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/g12a-aoclk.c -->
## sources/distributed-fs/ceph-client/drivers/clk/meson/g12a-aoclk.c

### Purpose
`g12a-aoclk.c` describes the Amlogic G12A always-on clock controller. It registers AO peripheral gates, 32 kHz oscillator-derived clocks, CEC clocks, RTC oscillator selection, AO clk81 selection, SAR ADC clocking, and AO reset lines for `amlogic,meson-g12a-aoclkc`.

### Important APIs, Types, And Functions
The file uses `MESON_PCLK()` through `G12A_AO_PCLK()` to define AO gates, `meson_clk_dualdiv_ops` for 32 kHz RTC/CEC dividers, regmap mux/divider/gate ops for AO clock paths, and `struct meson_aoclk_data` to combine clock and reset-controller data. `g12a_ao_reset[]` maps reset IDs to AO reset bits. `g12a_ao_hw_clks[]` maps clock binding IDs. The platform driver probes through `meson_aoclkc_probe()`.

### Control Flow
Probe is handled by the shared AO clock controller code, using `g12a_ao_clkc_data` to register clocks and resets. Runtime operations are generic common-clock callbacks: gate toggles, mux selection, divider programming, and dual-divider table selection. The reset controller uses `AO_RTI_GEN_CNTL_REG0` and the reset bit map supplied in the data structure.

### State, Persistence, And Dependencies
Persistent state lives in AO registers such as `AO_CLK_GATE0`, `AO_CLK_GATE0_SP`, `AO_RTI_PWR_CNTL_REG0`, `AO_RTC_ALT_CLK_CNTL*`, `AO_CEC_CLK_CNTL_REG*`, `AO_SAR_CLK`, and `AO_RTI_GEN_CNTL_REG0`. Dependencies include `meson-aoclk.h`, `clk-regmap.h`, `clk-dualdiv.h`, syscon/regmap access through the parent node, reset-controller support, and G12A AO clock/reset dt-bindings.

### Integration Points
AO peripherals such as IR, I2C, UART, SAR ADC, mailbox, RTI, M3/M4, RTC, and CEC consume these clocks. Many AO gates are marked `CLK_IGNORE_UNUSED` for historical compatibility, with comments encouraging future replacement by narrower flags where possible. The `g12a_ao_clk81` global name is retained for legacy PWM binding behavior.

### Risks And Edge Cases
The file intentionally keeps many AO gates from being disabled, which can hide missing consumers and wastes power, but removing the flag risks regressions. The 32 kHz and CEC clocks depend on the dual-divider table matching the oscillator rate. Reset bit mappings must stay aligned with `dt-bindings/reset/g12a-aoclkc.h`. Legacy global-name use by PWM constrains cleanup.

### Test Signals
Probe tests for `amlogic,meson-g12a-aoclkc`, reset-controller assertions/deassertions, RTC/CEC 32 kHz rate checks, SAR ADC rate programming, suspend/resume tests, and boot tests without unexpected AO gate disabling are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/g12a-aoclk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/g12a.c -->
## sources/distributed-fs/ceph-client/drivers/clk/meson/g12a.c

### Purpose
`g12a.c` is the main clock-controller description for Amlogic G12A, G12B, and SM1 SoCs. It defines PLLs, fixed-factor PLL outputs, CPU/DSU dynamic clock paths, MPLLs, clk81, peripheral gates, SD/eMMC, video/display, VPU/VAPB, HDMI, Mali, TS, SPI, NNA, MIPI DSI, SoC-specific clock ID arrays, and DVFS notifiers.

### Important APIs, Types, And Functions
The file uses almost every Meson helper in this subset: `meson_clk_pll_ops`, `meson_clk_pcie_pll_ops`, `meson_clk_mpll_ops`, `meson_clk_cpu_dyndiv_ops`, regmap mux/divider/gate ops, fixed-factor clocks, and `MESON_PCLK()`. Notable functions are `g12a_cpu_clk_mux_notifier_cb()`, `g12a_cpu_clk_dyn_notifier_cb()`, `g12a_sys_pll_notifier_cb()`, `g12a_dvfs_setup_common()`, `g12b_dvfs_setup()`, `g12a_dvfs_setup()`, and `g12a_clkc_probe()`. `g12a_hw_clks[]`, `g12b_hw_clks[]`, and `sm1_hw_clks[]` map dt-binding clock IDs for the three compatible variants.

### Control Flow
Most runtime behavior is delegated to common clock ops attached to static descriptors. Probe fetches match data, calls `meson_clkc_syscon_probe()` to register the clock tree from the parent syscon regmap, then runs the variant-specific DVFS notifier setup if present. For G12A, the setup registers notifiers on the CPU dynamic path, CPU mux, and system PLL. For G12B, it additionally registers notifiers for the second CPU cluster and sys1/sys PLL split.

CPU rate-change control is notifier-driven. Before changing a dynamic divider path, `g12a_cpu_clk_dyn_notifier_cb()` parks the CPU dynamic mux on an alternate path sourced from the xtal and waits for propagation. After the change, it switches the dynamic mux back. Before changing the system PLL that directly feeds a CPU clock, `g12a_sys_pll_notifier_cb()` moves the CPU clock to the dynamic path; after the PLL rate change, it switches back. A separate mux notifier adds pre/post propagation delays around mux changes.

### State, Persistence, And Dependencies
Persistent state is spread across HHI clock registers such as PLL control blocks, MPEG gates, CPU clock control registers, media/video clock controls, SD/eMMC controls, and peripheral gate registers. Linux state includes registered `clk_hw` objects, devm-managed notifier registrations, and static notifier data structures whose `xtal` pointers are filled at probe. Dependencies include generated G12A clock dt-bindings, local Meson PLL/MPLL/dynamic-divider/regmap helpers, `meson-clkc-utils`, Linux common clock notifier APIs, syscon regmap access, and platform-device probing.

### Integration Points
The compatible strings are `amlogic,g12a-clkc`, `amlogic,g12b-clkc`, and `amlogic,sm1-clkc`. Device drivers consume the exported clock IDs for CPU, DDR, VPU, HDMI, Mali, SD/eMMC, Ethernet, PCIe, audio, SPI, NNA, and video pipelines. The CPU DVFS integration is the most behaviorally sensitive point because cpufreq operations depend on safe temporary parent switching and PLL relock. Some clocks are present only for G12B or SM1 and are exposed through variant-specific arrays.

### Risks And Edge Cases
The file is a large declarative hardware map, so ID-array alignment with binding headers is a core risk. CPU notifiers assume fixed parent topology and successful `clk_hw_set_parent()` calls; the callbacks do not check those return values, so failures could leave CPU clocks on an unexpected path. The temporary 24 MHz parking path protects rate changes but can hurt if propagation delays are insufficient for hardware. PLL descriptors inherit lock-timeout and set-rate fallback risks from `clk-pll.c`. Variant arrays share many clock objects, so a change for one SoC can affect the others. Sparse arrays and SoC-specific clocks need device-tree coverage to prevent invalid phandle IDs.

### Test Signals
Important signals include boot on G12A/G12B/SM1 boards, `clk_summary` comparison against expected clock trees, cpufreq/DVFS stress tests across PLL and dynamic-divider transitions, PLL lock monitoring, video/HDMI/VPU/Mali rate programming, SD/eMMC timing mode tests, PCIe reference-clock tests, and device-tree binding validation for every exported `CLKID_*`. Build coverage should include all three compatibles and modular/static clock-controller configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/g12a.c -->
