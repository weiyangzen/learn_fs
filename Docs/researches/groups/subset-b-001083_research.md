# Research: subset-b-001083

Grouped research for clock framework sources under `sources/distributed-fs/ceph-client/drivers/clk`. Each section is delimited for reconciliation into one source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/Kconfig

Purpose: this is the top-level Kconfig switchboard for the Linux common clock framework and its clock-provider drivers. It defines the base API symbols `HAVE_CLK`, `HAVE_CLK_PREPARE`, `HAVE_LEGACY_CLK`, and `COMMON_CLK`, then exposes many provider-specific options and sources vendor subdirectories.

Important symbols and integration points: `COMMON_CLK` selects `HAVE_CLK`, `HAVE_CLK_PREPARE`, and `RATIONAL`, and is mutually exclusive with legacy architecture clock implementations. Driver symbols such as `COMMON_CLK_SCMI`, `COMMON_CLK_SCPI`, `COMMON_CLK_SI5341`, `COMMON_CLK_RK808`, `COMMON_CLK_RPMI`, and many others describe dependencies on buses, MFD parents, firmware protocols, OF, architecture families, or `COMPILE_TEST`. The file sources vendor Kconfig fragments including `actions`, `analogbits`, `aspeed`, `bcm`, `qcom`, `renesas`, `rockchip`, `ti`, and `xilinx`.

Control flow/state: Kconfig has no runtime state, but it gates which object files are compiled and which symbols become visible to dependent drivers. `default` clauses mostly follow architecture or parent-device selections. The final KUnit options select clock tests and device-tree overlays.

Dependencies and risks: incorrect dependencies can silently build unsupported drivers, hide required clocks, or break compile-test coverage. The top-level `source` list is an integration dependency for every vendor subtree. Test signals are `make olddefconfig`, per-architecture defconfigs, `COMPILE_TEST`, and the clock KUnit symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/Makefile

Purpose: this Makefile maps clock Kconfig symbols to common framework objects, KUnit objects, standalone clock providers, and vendor subdirectories. It is the build integration point for `drivers/clk`.

Important build APIs: `obj-$(CONFIG_HAVE_CLK)` builds legacy/common API support helpers (`clk-devres.o`, `clk-bulk.o`, `clkdev.o`). `obj-$(CONFIG_COMMON_CLK)` builds core common clock objects such as `clk.o`, `clk-divider.o`, `clk-fixed-factor.o`, `clk-fixed-rate.o`, `clk-gate.o`, `clk-mux.o`, `clk-composite.o`, `clk-fractional-divider.o`, and `clk-gpio.o`. KUnit targets compose their test object plus DT overlay objects. Standalone provider objects are listed by Kconfig symbol, while vendor directories are enabled with `obj-y` or architecture-specific symbols.

Control flow/state: no runtime state; build order controls which drivers are linked. The comments request lexicographic ordering for file-path and directory sections.

Dependencies and risks: the file depends on names matching Kconfig symbols and object filenames. Several directories are always visited (`actions`, `analogbits`, `aspeed`, many vendor folders), letting their local Makefiles decide whether objects build. Misordered or missing entries create link gaps, unbuilt drivers, or stale Kconfig options. Test signals include allmodconfig, allyesconfig, vendor defconfigs, and KUnit target builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/actions/Kconfig

Purpose: this fragment exposes clock controller support for Actions Semi OWL SoCs. `CLK_ACTIONS` is the family-wide switch, and `CLK_OWL_S500`, `CLK_OWL_S700`, and `CLK_OWL_S900` enable individual SoC clock descriptors.

Important symbols: `CLK_ACTIONS` depends on `ARCH_ACTIONS || COMPILE_TEST`, selects `REGMAP_MMIO` and `RESET_CONTROLLER`, and defaults to `ARCH_ACTIONS`. The S500 option supports 32-bit Actions platforms, while S700 and S900 additionally depend on `ARM64 && ARCH_ACTIONS` unless `COMPILE_TEST` is used.

Control flow/state: Kconfig only controls compilation of the common `clk-owl` library and the SoC-specific drivers. Runtime binding is handled by each SoC driver's OF compatible string.

Dependencies and risks: the family option must select reset and MMIO regmap support because the SoC probes register reset controllers and use a regmap over CMU registers. SoC symbol dependencies protect against invalid platform builds while retaining compile coverage. Test signals are `COMPILE_TEST`, Actions defconfigs, and DT binding compatibility for `actions,s500-cmu`, `actions,s700-cmu`, and `actions,s900-cmu`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/actions/Makefile

Purpose: this Makefile builds the Actions OWL common clock support and the per-SoC clock controller objects.

Important build structure: `obj-$(CONFIG_CLK_ACTIONS) += clk-owl.o` produces a composite object from `owl-common.o`, `owl-gate.o`, `owl-mux.o`, `owl-divider.o`, `owl-factor.o`, `owl-composite.o`, `owl-pll.o`, and `owl-reset.o`. The SoC files `owl-s500.o`, `owl-s700.o`, and `owl-s900.o` are built independently by their SoC Kconfig symbols.

Control flow/state: the common object contains reusable `clk_ops` and reset ops used by every SoC descriptor file. The SoC objects register platform drivers at `core_initcall` time.

Dependencies and risks: all helper object names must stay synchronized with the headers used by the SoC files. If `CLK_ACTIONS` is disabled but a SoC object is enabled, unresolved helper symbols would result; the Kconfig `if CLK_ACTIONS` nesting prevents that. Test signals are build coverage for each SoC option and link verification for `clk-owl.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-common.c -->
# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-common.c

Purpose: this is the shared OWL clock registration and regmap setup layer. It maps the platform CMU MMIO resource into a 32-bit regmap, installs that regmap into every `owl_clk_common`, and registers clocks as a onecell provider.

Important functions: `owl_clk_regmap_init()` calls `devm_platform_ioremap_resource()`, initializes `devm_regmap_init_mmio()` with 32-bit registers/stride and `max_register = 0x00cc`, then stores the regmap in the descriptor. `owl_clk_set_regmap()` iterates `desc->clks` and assigns each non-null common clock. `owl_clk_probe()` iterates `clk_hw_onecell_data`, skips null/error entries, calls `devm_clk_hw_register()`, and finally registers `devm_of_clk_add_hw_provider()`.

Control flow/state: regmap and registered clocks are device-managed. The persistent runtime state is hardware register content plus pointers stored in static descriptor structures. The provider exposes DT clock IDs through `of_clk_hw_onecell_get`.

Risks and tests: `owl_clk_regmap_init()` return value is ignored by the SoC probes, so a failed ioremap/regmap could lead to later invalid access. The fixed `max_register` must cover every SoC register used, including S900 offsets up to `0x00cc`; larger future SoCs would need adjustment. Test signals include probe success, `clk_summary`, OF clock lookup, and fault injection around regmap initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-common.h -->
# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-common.h

Purpose: this header defines the common embedding contract used by all OWL clock types and SoC descriptors.

Important types: `struct owl_clk_common` embeds a `struct clk_hw` plus the shared `struct regmap *`. Every concrete OWL clock type places this member at the end and uses `container_of` conversion helpers. `struct owl_clk_desc` groups the array of common clocks, `clk_hw_onecell_data`, reset map, reset count, and initialized regmap for a SoC.

Important APIs: `hw_to_owl_clk_common()` converts framework callbacks back to the common object. `owl_clk_regmap_init()` and `owl_clk_probe()` are exported within the local driver family.

Control flow/state: the header does not own state, but its layout enables callback dispatch from generic `clk_ops` into OWL-specific register descriptions. The descriptor couples clock and reset registration by sharing the same regmap.

Risks and tests: all concrete structures rely on the embedded `common` field and conversion helpers being correct. Type mismatch or non-OWL `clk_hw` use would corrupt callback state. Test signals are successful registration of each clock class, `container_of` coverage through enable/disable/rate changes, and sparse/compiler checking for forward declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-composite.c -->
# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-composite.c

Purpose: this file implements composite OWL clocks that combine mux, gate, and one rate component. The rate component can be a divider, factor table, fixed factor, or pass-through mux/gate-only clock.

Important functions/APIs: mux callbacks delegate to `owl_mux_helper_get_parent()` and `owl_mux_helper_set_parent()`. Gate callbacks delegate to `owl_gate_set()` and `owl_gate_clk_is_enabled()`. Divider callbacks wrap `divider_determine_rate()`, `owl_divider_helper_recalc_rate()`, and `owl_divider_helper_set_rate()`. Factor callbacks wrap `owl_factor_helper_round_rate()`, `owl_factor_helper_recalc_rate()`, and `owl_factor_helper_set_rate()`. Fixed-factor callbacks invoke the core `clk_fixed_factor_ops` for determine/recalc and return success for set-rate because the rounded rate is already constrained.

Control flow/state: all state lives in CMU registers addressed by the embedded mux/gate/rate descriptors. Calls are synchronous regmap read/modify/write operations and do not persist extra software state.

Integration points: the exported `owl_comp_div_ops`, `owl_comp_fact_ops`, `owl_comp_fix_fact_ops`, and `owl_comp_pass_ops` are wired by macros in `owl-composite.h` and used heavily in S500/S700/S900 descriptor files.

Risks and tests: helper operations are not internally locked, so correctness relies on regmap serialization and clock framework call ordering. Shared registers containing mux, gate, and divider fields are vulnerable to bad masks. Test signals include parent switching, gate toggling, rate rounding/set/recalc, and DT consumers for SD, UART, display, and peripheral clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-composite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-composite.h -->
# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-composite.h

Purpose: this header declares the composite OWL clock type and the macros used by SoC files to instantiate composite clocks declaratively.

Important types/macros: `union owl_rate` holds either `owl_divider_hw`, `owl_factor_hw`, or `clk_fixed_factor`. `struct owl_composite` embeds mux and gate descriptors, the rate union, optional fixed-factor ops, and `owl_clk_common`. `OWL_COMP_DIV`, `OWL_COMP_DIV_FIXED`, `OWL_COMP_FACTOR`, `OWL_COMP_FIXED_FACTOR`, and `OWL_COMP_PASS` create initialized static objects with the correct `CLK_HW_INIT*` form and ops table.

Control flow/state: the macros hard-code parent names or parent arrays, the register fields, and clock flags. Runtime callbacks use `hw_to_owl_comp()` to recover the surrounding composite object and then operate on the relevant register fields.

Dependencies and integration: depends on `owl-common`, `owl-mux`, `owl-gate`, `owl-factor`, `owl-fixed-factor`, and `owl-divider`. SoC descriptor files use these macros as their primary clock declaration language.

Risks and tests: macro arguments are not type-safe and shared register fields can be misdeclared. `OWL_COMP_DIV_FIXED` uses the divider ops without mux parents, so any accidental parent manipulation would be invalid. Test signals are compile errors for bad macro use, clock tree inspection, and exercising each composite flavor through common clock framework APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-composite.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-divider.c -->
# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-divider.c

Purpose: this file implements OWL divider clocks and divider helper routines used by standalone and composite clocks.

Important functions: `owl_divider_determine_rate()` calls the common `divider_determine_rate()` with the table, width, and flags. `owl_divider_helper_recalc_rate()` reads the register, extracts the configured value, and calls `divider_recalc_rate()`. `owl_divider_helper_set_rate()` computes a hardware value with `divider_get_val()`, clears the target bitfield with `GENMASK`, writes the new field, and returns success. `owl_divider_ops` exposes recalc, determine, and set-rate callbacks.

Control flow/state: each callback reads or writes a field in the clock controller regmap. There is no separate cached divider state. The clock framework passes parent rates and requested rates to these callbacks.

Dependencies and risks: depends on common clock divider helpers, `regmap_read`, and `regmap_write`. A notable risk is that `owl_divider_helper_set_rate()` passes `0` rather than `div_hw->div_flags` to `divider_get_val()`, so flags used for determine/recalc may not affect programming. Register read-modify-write is unprotected at this layer. Test signals are rate set/recalc consistency, table-backed divider coverage, and hardware register field validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-divider.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-divider.h -->
# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-divider.h

Purpose: this header declares OWL divider clock data structures, instantiation macros, and helper prototypes.

Important types/macros: `struct owl_divider_hw` stores register offset, shift, width, divider flags, and optional `clk_div_table`. `struct owl_divider` embeds that hardware descriptor plus `owl_clk_common`. `OWL_DIVIDER_HW` is the reusable field descriptor used by composites; `OWL_DIVIDER` creates a standalone clock with `owl_divider_ops`.

Control flow/state: runtime callbacks use `hw_to_owl_divider()` to retrieve the descriptor and common regmap. The only durable state is the hardware bitfield described by the macro arguments.

Dependencies and integration: the header depends on `owl-common.h` and exposes helper APIs consumed by `owl-composite.c`. SoC descriptors use `OWL_DIVIDER_HW` inside composite declarations and `OWL_DIVIDER` for bus clocks.

Risks and tests: `width` is used in shifts and masks, so invalid widths can overflow or clear wrong bits. Table pointers must outlive the clock objects; in this driver they are static. Test signals are compile-time macro use, divider table sentinel correctness, and `clk_set_rate()` results observed through `clk_summary`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-divider.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-factor.c -->
# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-factor.c

Purpose: this file implements OWL factor-table clocks, where a register value maps to arbitrary multiplier/divider pairs rather than a simple linear divider.

Important functions: `_get_table_maxval()`, `_get_table_div_mul()`, and `_get_table_val()` search sentinel-terminated `clk_factor_table` arrays. `owl_clk_val_best()` chooses the best table value for a target rate and optionally asks the parent to round to a better rate when `CLK_SET_RATE_PARENT` is set. `owl_factor_helper_round_rate()` returns the selected rate. `owl_factor_helper_recalc_rate()` reads the hardware value, maps it to `mul/div`, warns on zero divisor unless allowed, and calculates the output. `owl_factor_helper_set_rate()` programs the selected table value into the bitfield.

Control flow/state: calculations are table-driven and state is persisted only in the regmap bitfield. Parent-rate negotiation is done through `clk_hw_round_rate(clk_hw_get_parent(hw), ...)`.

Risks and tests: `_get_table_val()` assumes tables are sorted from faster to slower acceptable rates because it picks the first calculated rate less than or equal to the request. `owl_clk_val_best()` calls `_get_table_maxval(clkt)` after iterating `clkt` to the sentinel when no best value was found, which means it will see only the sentinel rather than the original table; that path deserves focused review. Test signals include factor table ordering, impossible low-rate requests, `CLK_SET_RATE_PARENT` paths, and recalc/set round trips for SD/display/video clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-factor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-factor.h -->
# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-factor.h

Purpose: this header defines the OWL factor clock model and helper API.

Important types/macros: `struct clk_factor_table` maps a register `val` to `mul` and `div`. `struct owl_factor_hw` stores register location, bitfield width/shift, flags, and the table. `struct owl_factor` combines the descriptor with `owl_clk_common`. `OWL_FACTOR_HW` creates a reusable descriptor and `OWL_FACTOR` creates a standalone factor clock. `div_mask(d)` derives the maximum encodable value from width.

Control flow/state: factor clocks use the table to translate between framework rates and hardware values. State is persisted in the register field; software state is static descriptor data.

Dependencies and integration: used directly by `owl-factor.c`, by composite clocks, and by SoC files for SD, display, video, GPU, and bus factors.

Risks and tests: table sentinel entries must have `div == 0`. The `div_mask` macro uses `1 << width`, so width must be valid for the integer type. The declared `fct_flags` are only used for zero-divisor warning behavior. Test signals are sentinel validation, mask boundary coverage, and comparing hardware register values against expected `mul/div` tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-factor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-fixed-factor.h -->
# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-fixed-factor.h

Purpose: this header provides a small OWL-local macro wrapper around the common clock fixed-factor implementation.

Important API: `OWL_FIX_FACT()` declares a `struct clk_fixed_factor` with `mult`, `div`, and a `CLK_HW_INIT()` using `clk_fixed_factor_ops`. The header also declares `extern const struct clk_ops clk_fixed_factor_ops`.

Control flow/state: fixed-factor clocks have no mutable hardware state. Runtime behavior is delegated entirely to the core fixed-factor clock ops, which calculate child rate from parent rate.

Dependencies and integration: standalone use is minimal in the listed SoC files because composite fixed-factor clocks are usually declared through `OWL_COMP_FIXED_FACTOR`. The header is included by composite and SoC descriptors for consistent naming and availability.

Risks and tests: division by zero would be a macro caller bug. The macro instantiates a concrete object, so duplicate `_struct` names or wrong parent names are compile or DT clock-tree issues. Test signals are clock registration and rate propagation in `clk_summary`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-fixed-factor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-gate.c -->
# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-gate.c

Purpose: this file implements OWL gate clocks and a helper used by composite clocks.

Important functions: `owl_gate_set()` reads a gate register, computes whether the target bit should be set or cleared based on `CLK_GATE_SET_TO_DISABLE` and the requested enable state, and writes the register back. `owl_gate_enable()`, `owl_gate_disable()`, and `owl_gate_is_enabled()` adapt that helper to `clk_ops`. `owl_gate_clk_is_enabled()` reads the register and inverts the bit interpretation for set-to-disable gates.

Control flow/state: enable state is persisted in hardware gate bits. The code uses full regmap read/modify/write cycles and no local cache.

Dependencies and integration: composite clocks use `owl_gate_set()` and `owl_gate_clk_is_enabled()` directly. Standalone gate clocks are declared by `OWL_GATE` or `OWL_GATE_NO_PARENT`.

Risks and tests: there is no explicit locking in the helper, so multi-field shared registers rely on regmap and framework serialization. Set-to-disable polarity must be correct for each gate. Test signals are gate enable/disable/is_enabled symmetry, clocks marked `CLK_IGNORE_UNUSED`, and checking that unrelated bits survive read/modify/write cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-gate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-gate.h -->
# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-gate.h

Purpose: this header defines OWL gate clock descriptors, standalone gate macros, and helper prototypes.

Important types/macros: `struct owl_gate_hw` stores register offset, bit index, and gate flags. `struct owl_gate` embeds that descriptor and `owl_clk_common`. `OWL_GATE_HW` is used in composites; `OWL_GATE` and `OWL_GATE_NO_PARENT` create standalone `clk_hw` objects with or without a named parent.

Control flow/state: callbacks recover the outer `owl_gate` through `hw_to_owl_gate()` and operate on the described bit. Persistent state is the hardware gate bit.

Dependencies and integration: included by composites and SoC descriptors. It exposes `owl_gate_set()` and `owl_gate_clk_is_enabled()` for composite code.

Risks and tests: macro definitions include trailing backslashes and caller-provided initializer fragments; bad gate flags or bit indices can invert or touch the wrong clock. Gates without parents should only be used for hardware clocks whose parent relationship is unknown or irrelevant to the framework. Test signals are clock tree registration, enable-count behavior, and unused-clock disabling behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-gate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-mux.c -->
# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-mux.c

Purpose: this file implements OWL mux clocks and mux helper routines used by composites.

Important functions: `owl_mux_helper_get_parent()` reads the mux register, shifts and masks the parent index, and returns it. `owl_mux_helper_set_parent()` clears the mux bitfield and writes the requested parent index. `owl_mux_ops` exposes get/set parent plus `__clk_mux_determine_rate`.

Control flow/state: parent selection is stored in a hardware register field. There is no software cache or validation of index range inside the helper; the common clock framework supplies the selected index from registered parents.

Dependencies and integration: depends on regmap and common clock mux helpers. Used by standalone `OWL_MUX` declarations and by all mux-capable composite clocks.

Risks and tests: the mask expression `BIT(width) - 1` assumes `width` is the number of bits and must be nonzero and sensible. Set-parent does not preserve invalid-index protection at this layer. Test signals are parent switching under `clk_set_parent()`, rate determination with parent changes, and register field inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-mux.h -->
# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-mux.h

Purpose: this header declares the OWL mux descriptor model and standalone mux macro.

Important types/macros: `struct owl_mux_hw` stores register offset, shift, and width. `struct owl_mux` embeds the descriptor and `owl_clk_common`. `OWL_MUX_HW` creates reusable descriptors for composites; `OWL_MUX` creates a standalone parent-array clock initialized with `CLK_HW_INIT_PARENTS`.

Control flow/state: mux callbacks convert `clk_hw` back to `owl_mux` and operate on the descriptor's register field. State is the parent index persisted in hardware.

Dependencies and integration: consumed by `owl-mux.c`, `owl-composite.h`, and SoC files for CPU, bus, and device source selection.

Risks and tests: parent arrays must stay in the same order as the hardware mux encoding. A width mismatch will expose wrong parents or overwrite neighboring bits. Test signals are DT-visible clock parent names, parent index reads after bootloader configuration, and explicit parent switching tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-mux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-pll.c

Purpose: this file implements OWL PLL clocks, including fixed-rate PLLs, multiplier-based PLLs, and PLLs with explicit value/rate tables.

Important functions: `owl_pll_calculate_mul()` rounds a requested rate by base frequency and clamps it to min/max multiplier. `_get_table_rate()` and `_get_pll_table()` translate table values and choose the closest not-above table rate. `owl_pll_determine_rate()` returns a table rate, fixed base frequency, or base-frequency multiplied result. `owl_pll_recalc_rate()` reads the register and calculates current output. `owl_pll_is_enabled()`, `owl_pll_enable()`, and `owl_pll_disable()` control the enable bit. `owl_pll_set_rate()` writes multiplier/table value and delays for PLL lock.

Control flow/state: hardware registers store enable bits and multiplier/table fields. `udelay(pll_hw->delay)` models post-programming stabilization.

Risks and tests: in `owl_pll_set_rate()`, `reg &= ~mul_mask(pll_hw)` does not shift the mask before clearing, while values are written at `shift`; shifted fields may leave old bits behind. Fixed-frequency PLLs are represented by `width == 0`. Test signals include PLL table selection, recalc after set-rate, enable state, and hardware bring-up for audio/display/EDP PLLs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-pll.h -->
# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-pll.h

Purpose: this header defines the OWL PLL descriptor, table model, and instantiation macros.

Important types/macros: `struct clk_pll_table` maps register values to fixed rates and is sentinel-terminated by `rate == 0`. `struct owl_pll_hw` stores register, base frequency, enable bit, multiplier shift/width, min/max multiplier, delay, and optional table. `OWL_PLL`, `OWL_PLL_NO_PARENT`, and `OWL_PLL_NO_PARENT_DELAY` create PLL clocks with named parent, no parent, or custom lock delay. `mul_mask()` derives the field mask from width.

Control flow/state: runtime PLL state is in hardware bits; the static descriptor supplies constraints. A width of zero means fixed-frequency behavior.

Dependencies and integration: SoC files use these macros for core, dev, DDR, NAND, display, audio, Ethernet, assist, CVBS, and EDP PLLs. `owl-pll.c` provides `owl_pll_ops`.

Risks and tests: invalid width can break `mul_mask()`. Table-backed PLLs need sorted rates for closest-rate behavior. No-parent PLLs assume firmware or external naming is enough for the clock tree. Test signals are rate constraints, lock delays, and parented EDP PLL registration on S900.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-pll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-reset.c -->
# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-reset.c

Purpose: this file implements reset-controller operations for Actions OWL CMU reset bits.

Important functions: `owl_reset_assert()` clears the mapped bit with `regmap_update_bits()`. `owl_reset_deassert()` sets the mapped bit. `owl_reset_reset()` asserts, waits 1 microsecond, then deasserts. `owl_reset_status()` reads the register and returns the logical reset API status, explicitly inverting the hardware convention because set means not asserted.

Control flow/state: reset state is stored in CMU reset registers. The controller uses an ID-indexed `owl_reset_map` supplied by the SoC descriptor.

Dependencies and integration: SoC probes allocate `struct owl_reset`, point it at the shared regmap and static reset map, then register `owl_reset_ops` through `devm_reset_controller_register()`.

Risks and tests: there is no bounds check in the callbacks; the reset core must pass valid IDs less than `nr_resets`. Sparse reset arrays can leave zero-initialized map entries if IDs are missing. Test signals are reset assert/deassert/status for each DT reset ID and verifying hardware active-low semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-reset.h -->
# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-reset.h

Purpose: this header declares the OWL reset controller data model.

Important types: `struct owl_reset_map` maps a reset ID to a register and bit mask. `struct owl_reset` embeds `reset_controller_dev`, the reset map pointer, and the regmap. `to_owl_reset()` converts reset core callbacks back to this structure. `owl_reset_ops` is exported from `owl-reset.c`.

Control flow/state: the header itself has no logic. Runtime reset state remains in hardware, while `owl_reset` stores the static map and shared regmap needed by callbacks.

Dependencies and integration: included by SoC clock descriptor files and by `owl-common.h` through forward-declared descriptor references. DT binding reset IDs index the SoC reset map arrays.

Risks and tests: map array size and DT binding IDs must remain aligned. Since the map stores a full bit mask rather than a bit index, callers must pass `BIT(n)` values. Test signals are reset-controller registration, reset ID coverage, and invalid-ID protection at the reset core boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-s500.c -->
# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-s500.c

Purpose: this is the Actions OWL S500 CMU driver. It declares all S500 PLLs, muxes, gates, dividers, factor clocks, composites, DT clock IDs, reset IDs, and the platform driver for `actions,s500-cmu`.

Important structures: register offset macros describe CMU layout through `0x00fc`, though the shared regmap max covers clock fields through `0x00cc`. PLLs include Ethernet, core, DDR, NAND, display, dev, and audio; audio uses a two-entry table for 45.1584/49.152 MHz. Tables define SD, display engine, HDE, RMII, I2S, standard, and NAND divisors. `s500_clks[]` lists every `owl_clk_common`, `s500_hw_clks` maps DT `CLK_*` IDs to `clk_hw`, and `s500_resets[]` maps reset binding IDs to CMU reset bits.

Control flow/state: `s500_clk_probe()` initializes the regmap, allocates/registers a reset controller, and calls `owl_clk_probe()`. Static descriptors persist for the lifetime of the kernel; hardware registers hold clock state.

Dependencies/integration: depends on OWL helper macros, Actions S500 clock/reset DT bindings, platform driver matching, and common clock/reset frameworks.

Risks and tests: the probe ignores the return from `owl_clk_regmap_init()`. Several clocks are `CLK_IGNORE_UNUSED` to protect firmware-enabled UART/SPI/PLL state. Shared gates are reused for related clocks such as NAND/ECC and sensors. Test signals are boot on S500, DT clock/reset consumer lookup, peripheral bring-up for UART/I2C/SD/NAND/display/audio, and reset status polarity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-s500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-s700.c -->
# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-s700.c

Purpose: this file is the Actions S700 CMU provider and reset controller for `actions,s700-cmu`.

Important structures: the file declares CMU offsets, audio/CVBS PLL tables, core/dev/DDR/NAND/display/CVBS/audio/Ethernet PLLs, parent arrays, divider/factor tables, standalone mux/divider/gate clocks, many composite clocks, `s700_clks[]`, `s700_hw_clks`, and `s700_resets[]`. S700 adds CPU/NOC/HP bus muxing, USB2/USB3 gates, LCD/GPU/thermal sensor clocks, PCM1 fixed-factor clock, and I3C-like `irc_switch` gate relative to S500.

Control flow/state: `s700_clk_probe()` follows the same pattern as S500: initialize regmap, allocate an `owl_reset`, register reset ops, and register the onecell clock provider. A FIXME notes reset controller registration should move to common code once all OWL SoCs support it.

Dependencies/integration: depends on `dt-bindings/clock/actions,s700-cmu.h` and `dt-bindings/reset/actions,s700-reset.h`. Uses common OWL helpers for every register-level operation.

Risks and tests: return from regmap initialization is ignored. There are minor spelling/format anomalies such as `CLK_SENOR_SRC` and `clk_cvbs_pll .common`, so binding names and compiler coverage matter. Test signals include S700 boot, CPU/NOC rate reporting, USB/Ethernet/LCD/GPU devices, reset operations, and unused-clock handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-s700.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-s900.c -->
# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-s900.c

Purpose: this is the Actions S900 CMU driver for `actions,s900-cmu`, covering a larger clock tree with display, GPU, DDR, USB, EDP, NAND, SD, I2C, UART, and sensor clocks plus resets.

Important structures: the file defines register offsets through `CMU_PWM5CLK`, audio and EDP PLL tables, PLLs for core/dev/DDR/NAND/display/assist/audio/EDP, parent arrays, divider tables for NAND/APB/Ethernet/USB/I2S/HDMI audio, factor tables for SD/DMM/NOC/BISP, static clock instances, `s900_clks[]`, `s900_hw_clks`, and `s900_resets[]`. S900 includes EDP fixed and PLL clocks, multiple GPU clocks, dual NAND clocks, six I2C clocks, four SD clocks, DDR gates marked `CLK_IGNORE_UNUSED`, and a PWM2 backlight protection comment.

Control flow/state: `s900_clk_probe()` initializes regmap, registers the reset controller, then registers all clocks as a onecell provider. State is static descriptor data plus CMU hardware register contents.

Dependencies/integration: integrates with Actions S900 DT clock/reset bindings and common OWL helpers. It exposes clock IDs consumed by peripheral DT nodes.

Risks and tests: regmap init return is ignored. Several clocks intentionally preserve boot state with `CLK_IGNORE_UNUSED`; removing those flags may blank displays or break serial/DDR. UART1 uses shift `1` while other UARTs use `0`, which deserves hardware validation. Test signals include S900 board boot, EDP/display/GPU/USB/NAND/SD/UART devices, reset lines, and `clk_summary` parent/rate sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/actions/owl-s900.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/analogbits/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/analogbits/Kconfig

Purpose: this fragment declares the hidden tristate build symbol for the Analog Bits CLN28HPC wide-range PLL helper library.

Important symbol: `CLK_ANALOGBITS_WRPLL_CLN28HPC` has no prompt and no dependencies in this file, so it is selected by SoC/IP drivers that need the reusable PLL math library.

Control flow/state: Kconfig only controls whether `wrpll-cln28hpc.o` is built. The library itself exports GPL symbols for other drivers.

Dependencies and risks: because the symbol is hidden, missing `select CLK_ANALOGBITS_WRPLL_CLN28HPC` in a consumer will produce unresolved symbols or unavailable helper routines. Overly broad selection increases kernel size only modestly but exposes unused module code. Test signals are consumer driver builds and module/allmodconfig coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/analogbits/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/analogbits/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/analogbits/Makefile

Purpose: this Makefile maps the hidden Analog Bits WRPLL Kconfig symbol to its implementation object.

Important build rule: `obj-$(CONFIG_CLK_ANALOGBITS_WRPLL_CLN28HPC) += wrpll-cln28hpc.o`.

Control flow/state: no runtime state; the file only participates in kernel object selection.

Dependencies and risks: the object must remain synchronized with the public header `<linux/clk/analogbits-wrpll-cln28hpc.h>` and any drivers selecting the Kconfig symbol. Test signals are allmodconfig builds and link coverage for consumers of `wrpll_configure_for_rate()`, `wrpll_calc_output_rate()`, and `wrpll_calc_max_lock_us()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/analogbits/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/analogbits/wrpll-cln28hpc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/analogbits/wrpll-cln28hpc.c

Purpose: this is a reusable math/configuration library for the Analog Bits CLN28HPC wide-range PLL. It calculates PLL register fields and output rates but does not own hardware registers.

Important exported APIs: `wrpll_configure_for_rate()` fills `struct wrpll_cfg` for a target output rate and parent reference rate. `wrpll_calc_output_rate()` calculates output from an existing config. `wrpll_calc_max_lock_us()` returns the maximum lock delay. Private helpers compute filter range, feedback divisor, Q divider, and parent-rate-dependent R divider limits.

Control flow/state: callers pass a mutable `wrpll_cfg`; the function caches `parent_rate`, `max_r`, and `init_r` in that struct. It validates reference frequency ranges, handles parent-rate bypass, chooses `divq`, scans valid R values for the best `divf`, computes filter `range`, and clears reset/bypass flags as needed. The code exports GPL symbols for integration by platform-specific PLL drivers.

Dependencies and risks: depends on constants from the public WRPLL header and Linux math helpers. External feedback calculation is explicitly unsupported in `wrpll_calc_output_rate()`. The algorithm assumes initialized feedback flags and caller-side serialization. Test signals are unit tests over datasheet bounds, parent rates near min/max, bypass behavior, exact and inexact rates, and comparing computed fields to hardware manuals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/analogbits/wrpll-cln28hpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/aspeed/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/aspeed/Kconfig

Purpose: this Kconfig fragment exposes Aspeed BMC clock controller support.

Important symbols: `COMMON_CLK_ASPEED` covers older Aspeed G4/G5 SoCs such as AST2400/AST2500, depends on `ARCH_ASPEED || COMPILE_TEST`, defaults to `ARCH_ASPEED`, and selects `MFD_SYSCON` plus `RESET_CONTROLLER`. `COMMON_CLK_AST2700` enables AST2700 clock support and depends on the same architecture/compile-test condition. AST2600 is controlled by `CONFIG_MACH_ASPEED_G6` in the Makefile rather than a symbol here.

Control flow/state: Kconfig selects which platform drivers are compiled. Runtime matching is by SCU compatible strings.

Dependencies and risks: older drivers use syscon/regmap and register reset controllers from the clock driver, so missing selects would break builds. AST2700 uses auxiliary reset device creation rather than selecting reset here, likely relying on broader platform dependencies. Test signals include Aspeed defconfigs, compile-test, and DT compatible coverage for AST2400/2500/2600/2700.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/aspeed/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/aspeed/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/aspeed/Makefile

Purpose: this Makefile builds Aspeed clock controller objects for supported SoC generations.

Important build rules: `clk-aspeed.o` is built for `COMMON_CLK_ASPEED`, `clk-ast2600.o` for `MACH_ASPEED_G6`, and `clk-ast2700.o` for `COMMON_CLK_AST2700`.

Control flow/state: no runtime state; object selection determines which platform/OF clock providers are linked.

Dependencies and risks: AST2600 build is tied to the machine symbol, not a local Kconfig option. The common header `clk-aspeed.h` is shared by the older and AST2600 drivers. Test signals are defconfig builds for each generation, compile-test builds, and ensuring no unused generation object is required by another.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/aspeed/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/aspeed/clk-aspeed.c -->
# sources/distributed-fs/ceph-client/drivers/clk/aspeed/clk-aspeed.c

Purpose: this driver supports AST2400/AST2500 SCU clocks and resets. It registers early core clocks through `CLK_OF_DECLARE_DRIVER` and later registers gates/resets through a built-in platform driver.

Important functions/types: PLL helpers `aspeed_ast2400_calc_pll()` and `aspeed_ast2500_calc_pll()` translate HPLL/MPLL register values to fixed-factor clocks. Gate callbacks implement reset-before-enable sequencing for IPs with reset bits. Reset callbacks map reset IDs to SCU04 or SCUD4 bits. `aspeed_clk_probe()` registers the reset controller, UART/MPLL/SD/MAC/LHCLK/BCLK/ECLK clocks, AST2500 RMII gates, and every `aspeed_gates` entry. `aspeed_cc_init()` maps the SCU, initializes `aspeed_clk_data` with `-EPROBE_DEFER`, registers early `clkin`, `hpll`, `ahb`, and `apb`, then exposes a onecell provider.

Control flow/state: global `aspeed_clk_data` and `scu_base` bridge early OF initialization to platform probe. Hardware state is in SCU reset, stop, strap, selection, and PLL registers.

Risks and tests: several registered clocks are not device-managed in early init. Integer PLL calculation for AST2500 uses `(m + 1) / (n + 1)` before applying `p`, losing fractional precision. Gate enable intentionally toggles reset with delays; incorrect reset index can disrupt devices. Test signals include AST2400/2500 boot, deferred consumers resolving after platform probe, reset sequencing for USB/MAC/video, and clock-rate validation from straps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/aspeed/clk-aspeed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/aspeed/clk-aspeed.h -->
# sources/distributed-fs/ceph-client/drivers/clk/aspeed/clk-aspeed.h

Purpose: this shared header defines data structures used by the older Aspeed and AST2600 clock drivers.

Important types: `struct aspeed_gate_data` describes a gate bit, optional reset bit, name, parent, and flags. `struct aspeed_clk_gate` is a custom gate object with regmap, clock/reset indices, flags, and spinlock. `struct aspeed_reset` wraps a regmap-backed reset controller. `struct aspeed_clk_soc_data` provides per-SoC divider tables and a PLL calculation callback for AST2400/AST2500.

Control flow/state: callback code converts `clk_hw` or `reset_controller_dev` back to these structures with container macros. Runtime state is mostly hardware; software objects store the regmap and metadata needed by callbacks.

Dependencies and integration: included by `clk-aspeed.c` and `clk-ast2600.c`. It depends on common clock, reset controller, regmap, and spinlock declarations.

Risks and tests: the comment says `calc_pll` "maculate" rather than calculate, but behavior is clear. `reset_idx` is signed in data but stored as `s8`; generation-specific code must handle negative values before bit operations. Test signals are gate/reset callbacks across both old and G6 drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/aspeed/clk-aspeed.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/aspeed/clk-ast2600.c -->
# sources/distributed-fs/ceph-client/drivers/clk/aspeed/clk-ast2600.c

Purpose: this driver supports AST2600/G6 SCU clocks and resets. It follows the older Aspeed split between early clock provider setup and platform-probed gates, but adapts for two stop/reset registers, more gates, and silicon revision differences.

Important functions: `ast2600_calc_pll()` and `ast2600_calc_apll()` decode PLL registers, with APLL behavior depending on `soc_rev`. `get_bit()`, `get_reset_reg()`, and `get_clock_reg()` handle indices across two 32-bit registers. Gate ops use write-to-set and set-to-clear register semantics plus reset sequencing. Reset ops expose 64 reset IDs. `aspeed_g6_clk_probe()` registers UART/UARTX fixed rates, eMMC/SD/MAC/LHCLK/D1/BCLK/VCLK/ECLK clocks and all gate descriptors. `aspeed_g6_cc_init()` maps SCU, reads revision, initializes onecell data with `-EPROBE_DEFER`, registers early PLL/AHB/APB/USB/I3C/FSI clocks, and adds the provider.

Control flow/state: global `aspeed_g6_clk_data`, `scu_g6_base`, and `soc_rev` persist across early and platform phases. Hardware state is in strap, PLL, selection, stop, and reset registers.

Risks and tests: many clocks are deferred until platform probe, so consumers must tolerate `-EPROBE_DEFER`. The code writes clock selection registers for D1 and I3C, changing bootloader configuration. PLL math uses integer division in fixed-factor registration. Test signals include AST2600 revisions A0/A1/A2, I3C/FSI clocks, MAC1-4, eMMC/SD, reset sequencing, and `clk_summary` after probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/aspeed/clk-ast2600.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/aspeed/clk-ast2700.c -->
# sources/distributed-fs/ceph-client/drivers/clk/aspeed/clk-ast2700.c

Purpose: this module implements AST2700 clock providers for two SCU blocks, `aspeed,ast2700-scu0` and `aspeed,ast2700-scu1`. It is descriptor-driven and also creates an auxiliary reset device for each SCU.

Important types/functions: `enum ast2700_clk_type` selects registration behavior. `struct ast2700_clk_info` describes fixed, fixed-factor, display-fixed, PLL, HPLL, UART PLL, mux, divider, gate, and misc clocks. Static descriptor arrays `ast2700_scu0_clk_info` and `ast2700_scu1_clk_info` define the whole clock tree. Register helpers calculate display clocks, HPLL strap-selected rates, PLL fixed factors, UART PLL factors, MPHY/U2PHY misc divisors, and clear-to-enable gates. `ast2700_soc_clk_probe()` maps registers, allocates onecell data, optionally configures SCU1 I3C clock, iterates descriptors in dependency order, registers each clock, adds the OF provider, and creates `reset0` or `reset1` auxiliary devices.

Control flow/state: all clocks are device-managed except the small custom gate allocation path, which frees on registration failure. Parent hardware arrays are filled during probe from previously registered IDs. Hardware state is in SCU clock selection, PLL, stop, and display parameter registers.

Risks and tests: descriptor order is critical because parent IDs must already be registered. Several calculations use integer division before fixed-factor registration, so non-integral PLL ratios may be truncated. `devm_kasprintf()` result is not checked before auxiliary device creation. Test signals are both SCU nodes probing, UART/I3C/SD/MAC/display clocks, auxiliary reset device binding, and invalid descriptor ID detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/aspeed/clk-ast2700.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/Makefile

Purpose: this Makefile builds Microchip/Atmel AT91 clock controller support.

Important build rules: common PMC and clock class objects (`pmc.o`, `sckc.o`, `clk-slow.o`, `clk-main.o`, `clk-pll.o`, `clk-plldiv.o`, `clk-master.o`, `clk-system.o`, `clk-peripheral.o`, `clk-programmable.o`) are always built when the directory is selected. Feature objects build for symbols such as `HAVE_AT91_AUDIO_PLL`, `HAVE_AT91_UTMI`, `HAVE_AT91_USB_CLK`, and `HAVE_AT91_GENERATED_CLK`. SoC descriptor objects are selected by SoC symbols, often with `dt-compat.o`.

Control flow/state: no runtime state; this file controls which reusable clock classes and SoC setup files are linked.

Dependencies and risks: some SoC lines include shared descriptor files multiple times under the same symbol family; object duplication is avoided by kbuild object semantics but should be reviewed when changing SoC coverage. Test signals are AT91 defconfig builds, allmodconfig, and ensuring selected SoC objects have their needed feature helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/at91rm9200.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/at91rm9200.c

Purpose: this file declares the legacy AT91RM9200 PMC clock tree and registers it through early OF clock initialization.

Important data/functions: static master and PLL characteristics describe valid master output, divisors, PLL input ranges, output ranges, and PLL `out` values. `at91rm9200_systemck` maps system clocks such as `udpck`, `uhpck`, and programmable clocks to IDs. `at91rm9200_periphck` maps peripheral clock names to IDs. `at91rm9200_pmc_setup()` reads `slow_xtal` and `main_xtal` parent names, gets the syscon regmap, allocates `pmc_data`, registers main oscillator/main clock, PLLA/PLLB, master prescaler/divider, USB clock, four programmable clocks, system clocks, peripheral clocks, and finally adds the PMC clock provider.

Control flow/state: setup runs via `CLK_OF_DECLARE` for `atmel,at91rm9200-pmc`, before normal platform probing because timer/pinctrl dependencies need early clocks. State is kept in allocated `pmc_data` and PMC hardware registers.

Risks and tests: error cleanup only frees `pmc_data`, while clocks registered before failure may remain. Parent lookup failure silently aborts setup. Test signals are AT91RM9200 DT boot, clock provider lookups by ID, USB/system/peripheral clocks, and programmable clock parent/rate changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/at91rm9200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/at91sam9260.c -->
# sources/distributed-fs/ceph-client/drivers/clk/at91/at91sam9260.c

Purpose: this file provides PMC clock setup for AT91SAM9260, AT91SAM9G20, AT91SAM9261, and AT91SAM9263 families using a shared descriptor-driven setup function.

Important types/data: `struct at91sam926x_data` groups PLL layouts/characteristics, master clock characteristics, system clock arrays, peripheral clock arrays, programmable clock count, and whether the SoC has a selectable slow clock. The file defines SoC-specific PLL ranges, `out` and `icpll` tables, master divisors, system clocks, peripheral clocks, and descriptor instances for each supported compatible.

Important control flow: `at91sam926x_pmc_setup()` reads `slow_xtal` and `main_xtal`, obtains the PMC regmap, allocates `pmc_data`, registers main oscillator/main clock, optionally registers `slow_rc_osc` and `slck`, registers PLLA/PLLB, master prescaler/divider, USB clock, programmable clocks, all system clocks, all peripheral clocks, and adds the OF provider. Thin compatible-specific setup functions pass the right descriptor and are registered with `CLK_OF_DECLARE`.

State/dependencies: state lives in `pmc_data` arrays and PMC registers. Dependencies include `pmc.h` registration helpers, AT91 DT clock IDs, syscon regmap, and early OF clock setup.

Risks and tests: descriptor IDs must match hardware and DT binding expectations. Error cleanup is partial after successful clock registrations. Slow-clock handling differs by SoC and is a key integration risk. Test signals are boot on each compatible, clocksource/timer availability, USB clock divisors, programmable clock counts, and peripheral clocks for USART/MCI/SPI/SSC/MAC/LCD.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/at91/at91sam9260.c -->
