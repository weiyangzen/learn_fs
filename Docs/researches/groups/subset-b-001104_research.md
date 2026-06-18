# Research: subset-b-001104

This grouped report covers the requested MediaTek and Meson clock-controller source files. Each file section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mtk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mtk.c

Purpose: `clk-mtk.c` is the shared MediaTek common-clock registration helper. It allocates `clk_hw_onecell_data`, initializes empty clock slots to `ERR_PTR(-ENOENT)`, registers fixed-rate, fixed-factor, mux, composite, divider, gate, and optional reset-controller resources, and exposes simple platform probe/remove entry points used by many MediaTek SoC clock drivers.

Important APIs and functions: exported allocation helpers are `mtk_devm_alloc_clk_data()`, `mtk_alloc_clk_data()`, and `mtk_free_clk_data()`. Exported registration pairs include `mtk_clk_register_fixed_clks()`/`mtk_clk_unregister_fixed_clks()`, `mtk_clk_register_factors()`/`mtk_clk_unregister_factors()`, `mtk_clk_register_composites()`/`mtk_clk_unregister_composites()`, and `mtk_clk_register_dividers()`/`mtk_clk_unregister_dividers()`. `mtk_clk_pdev_probe()`, `mtk_clk_simple_probe()`, `mtk_clk_pdev_remove()`, and `mtk_clk_simple_remove()` wrap the internal simple probe/remove path. `mtk_clk_get_hwv_regmap()` resolves the optional `mediatek,hardware-voter` phandle.

Control flow: `__mtk_clk_simple_probe()` resolves `struct mtk_clk_desc` from OF match data or platform ID data, maps MMIO when composite or divider clocks need a base pointer, optionally enables runtime PM, calculates onecell capacity by summing all clock categories, and registers each category in dependency order: fixed clocks, fixed factors, muxes, composites, dividers, gates, notifier, provider, then reset controller. Every failure label unwinds the already registered categories in reverse order and resets slots to `ERR_PTR(-ENOENT)`. Removal unregisters the OF provider and tears down the same categories in reverse.

State and persistence: state is in kernel-managed clock registrations, the onecell `hws[]` table, optional platform driver data, MMIO mappings, and runtime PM reference counts. There is no persistent storage. Shared IO mappings created with `of_iomap()` are explicitly unmapped on error; non-shared resources are devm-managed.

Dependencies and integration points: the file depends on the Linux common clock framework, OF providers, platform devices, PM runtime, regmap syscon, and local MediaTek gate/mux/reset helpers. It integrates with device tree clock consumers through `of_clk_add_hw_provider(node, of_clk_hw_onecell_get, clk_data)`.

Risks: duplicate clock IDs are warned and skipped, so table mistakes may leave old entries active. The composite unwind loop checks `clk_data->hws[mcs->id]` instead of `clk_data->hws[mc->id]`, which looks like a latent cleanup bug if a later composite registration fails. Runtime PM and shared `of_iomap()` cleanup paths must stay balanced to avoid leaked mappings or suspended register access. Clock descriptor counts must match ID ranges because onecell slots are indexed directly by table IDs.

Test signals: useful checks include boot/probe logs for duplicate ID warnings and failed registration messages, `clk_summary` coverage for every descriptor ID, device tree clock consumer probing, runtime suspend/resume on `need_runtime_pm` controllers, and fault-injection or negative tests that force mid-registration failure and verify reverse unregister behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mtk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mtk.h -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mtk.h

Purpose: `clk-mtk.h` is the public local interface for MediaTek clock-controller data tables and common registration helpers. SoC clock drivers include it to describe fixed clocks, fixed factors, composite mux/div/gate clocks, simple dividers, reset descriptors, shared locks, runtime PM needs, and common probe/remove hooks.

Important APIs and types: it defines `struct mtk_fixed_clk`, `struct mtk_fixed_factor`, `struct mtk_composite`, `struct mtk_clk_divider`, and `struct mtk_clk_desc`. It declares the registration/unregistration APIs implemented in `clk-mtk.c`, plus `mtk_clk_get_hwv_regmap()`. Macros such as `FIXED_CLK`, `FACTOR`, `FACTOR_FLAGS`, `MUX_GATE`, `MUX_GATE_FLAGS`, `MUX`, `MUX_FLAGS`, `DIV_GATE`, `MUX_DIV_GATE`, and `DIV_ADJ` generate static table entries. `GATE_DUMMY`, `CLK_DUMMY`, `cg_regs_dummy`, and `mtk_clk_dummy_ops` support binding compatibility where hardware clock IDs do not start at zero.

Control flow: this header has no executable control flow. It shapes the control flow consumed by `clk-mtk.c`: `struct mtk_clk_desc` tells the simple probe which arrays to register, how many entries each array contains, whether MMIO is shared, whether runtime PM is needed, whether a reset controller is present, and whether a notifier must be installed for an MFG mux.

State and persistence: the header defines static descriptor state that SoC drivers compile into their modules. Runtime state lives in the common clock framework, the onecell clock array, and reset-controller structures allocated by the implementation.

Dependencies and integration points: it includes Linux clock-provider, IO, spinlock, and type headers, plus MediaTek `reset.h`. It is consumed by MediaTek SoC-specific drivers and by the local mux/gate/reset implementations. `struct mtk_clk_desc::rst_desc` integrates clock-controller probing with MediaTek reset controller registration.

Risks: most macros rely on positional initializer correctness; swapped register, shift, or width parameters produce valid C but wrong hardware behavior. `signed char` fields use `-1` as sentinel for absent mux/divider/gate parts, so table authors must avoid unsigned conversion mistakes. Count fields in `mtk_clk_desc` must match array lengths and ID ranges to avoid missing clocks or out-of-bounds onecell indexing.

Test signals: compile coverage across MediaTek SoC drivers catches initializer drift. Runtime signals include full `clk_summary` names, correct parent lists, expected rate propagation flags, reset controller registration when `rst_desc` is present, and absence of duplicate ID warnings during probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mtk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mux.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mux.c

Purpose: `clk-mux.c` implements MediaTek mux clocks that use set/clear/update registers, optional gate bits, optional fenc status polling, and optional hardware voter registers. It also provides a devm clock notifier that temporarily switches a mux to a bypass parent around PLL parent-rate changes.

Important APIs and functions: `struct mtk_clk_mux` wraps `clk_hw`, register maps, source descriptor, optional lock, and a `reparent` flag. Exported `clk_ops` are `mtk_mux_clr_set_upd_ops`, `mtk_mux_gate_clr_set_upd_ops`, `mtk_mux_gate_fenc_clr_set_upd_ops`, and `mtk_mux_gate_hwv_fenc_clr_set_upd_ops`. Exported registration functions are `mtk_clk_register_muxes()` and `mtk_clk_unregister_muxes()`. `devm_mtk_clk_mux_notifier_register()` installs the bypass notifier.

Control flow: enable paths clear the gate bit through `clr_ofs`; fenc enable additionally polls `fenc_sta_mon_ofs`; hardware-voter enable writes the HWV set register, waits for HWV status, then waits for fenc status. Disable paths either write normal set registers or hardware-voter clear registers. Parent reads mask and shift `mux_ofs`, translating through `parent_index` if present. Parent changes read/modify the mux value, write clear and set masks, and trigger `upd_ofs` when `upd_shift >= 0`; if the clock is gated, `reparent` causes the update bit to be rewritten when the gate is later enabled.

State and persistence: runtime state is only the hardware register values and the in-memory `reparent` boolean. Clock registration state is stored in the onecell `hws[]` table and released by `mtk_clk_unregister_muxes()`. No persistent storage is used.

Dependencies and integration points: the driver depends on Linux regmap, common clock framework mux helpers, spinlocks, syscon lookup from device tree, and `mtk_clk_get_hwv_regmap()`. It plugs into the common MediaTek descriptor path in `clk-mtk.c`; SoC tables from `clk-mux.h` select the appropriate ops.

Risks: `mtk_clk_register_mux()` returns early if HWV is required but no HWV regmap exists without freeing the just-allocated `clk_mux`, which appears to leak memory on that error path. Parent index tables must map every hardware value correctly; otherwise `get_parent()` can return an impossible index. Poll timeouts are short and atomic, so wrong fenc/HWV offsets can fail probe or enable under interrupt-disabled contexts. Lockless operation uses sparse annotations, so shared register users must provide a real spinlock when needed.

Test signals: validate parent selection through `clk_set_parent()` and `clk_get_parent()`, enable/disable state through fenc and non-fenc muxes, deferred probe/error behavior when hardware-voter phandles are missing, and PLL rate-change notifier behavior by observing temporary bypass selection during `PRE_RATE_CHANGE` and restoration on `POST_RATE_CHANGE` or `ABORT_RATE_CHANGE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mux.h -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mux.h

Purpose: `clk-mux.h` declares the descriptor format and construction macros for MediaTek mux clocks backed by set/clear/update registers, gate bits, fenc status monitoring, optional indexed parent values, and hardware voter support.

Important APIs and types: `struct mtk_mux` stores IDs, names, parent arrays, optional hardware parent index table, offsets for mux/set/clear/update/HWV/fenc registers, bit shifts and widths, selected `clk_ops`, and parent count. The header declares the four mux `clk_ops`, `mtk_clk_register_muxes()`, `mtk_clk_unregister_muxes()`, `struct mtk_mux_nb`, `to_mtk_mux_nb()`, and `devm_mtk_clk_mux_notifier_register()`.

Control flow: macros encode which runtime operations the implementation will use. `MUX_CLR_SET_UPD` creates a parent-only mux. `MUX_GATE_CLR_SET_UPD*` adds gate control. `MUX_GATE_FENC_CLR_SET_UPD*` adds fenc status polling. `MUX_GATE_HWV_FENC_CLR_SET_UPD*` routes enable/disable through hardware voter registers and fenc status. Indexed variants decouple logical parent indexes from hardware selector values.

State and persistence: the header contributes static, compile-time mux descriptors. Runtime state, such as the selected parent, gate state, fenc status, and `reparent` tracking, is maintained by hardware registers and the `struct mtk_clk_mux` allocated by `clk-mux.c`.

Dependencies and integration points: it depends on Linux notifier, spinlock, and type declarations. It is included by MediaTek SoC clock table files and the implementation. `struct mtk_mux_nb` links common clock rate-change notifiers with mux ops so a SoC can switch away from a PLL while the PLL is being retuned.

Risks: the macros are dense and parameter order is register-sensitive, so a shift or offset typo silently targets the wrong bit. `GATE_CLR_SET_UPD_FLAGS_INDEXED()` uses `ARRAY_SIZE(_paridx)` as `num_parents`, which assumes the index table length matches the parent-name array. Hardware voter descriptors require valid HWV offsets and a `mediatek,hardware-voter` phandle at runtime.

Test signals: build coverage catches missing ops symbols; runtime tests should check all descriptor-created clocks appear in `clk_summary`, parent indexes match hardware selectors, gate bits and fenc bits reflect enable state, and notifier users restore the original parent after successful and aborted PLL rate changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-pll.c

Purpose: `clk-pll.c` implements MediaTek PLL common-clock operations: power sequencing, prepare/unprepare, PCW/post-divider rate calculation, rate programming, optional tuner handling, optional fenc/set-clear enable operations, and bulk PLL registration.

Important APIs and functions: exported or externally declared operations include `mtk_pll_is_prepared()`, `mtk_pll_prepare()`, `mtk_pll_unprepare()`, `mtk_pll_recalc_rate()`, `mtk_pll_calc_values()`, `mtk_pll_set_rate()`, `mtk_pll_determine_rate()`, `mtk_clk_register_pll_ops()`, `mtk_clk_register_pll()`, `mtk_clk_unregister_pll()`, `mtk_clk_register_plls()`, `mtk_clk_unregister_plls()`, and `mtk_clk_pll_get_base()`. The main ops tables are `mtk_pll_ops` and exported `mtk_pll_fenc_clr_set_ops`.

Control flow: rate calculation clamps requested rates to `fmax`, picks a post divider from an optional divider table or from the default VCO minimum rule, and computes PCW using integer plus fractional PCW bits. `mtk_pll_set_rate_regs()` disables the tuner, writes postdiv and PCW, toggles the PCW change bit, updates the tuner register, re-enables tuning, and delays. Normal prepare powers on, deisolates, enables, optionally sets an enable mask and reset-bar bit, and waits. Unprepare reverses that sequence. Set/clear prepare variants only write enable set/clear registers and rely on fenc status for prepared state.

State and persistence: state is in PLL MMIO registers and allocated `struct mtk_clk_pll` instances. Bulk registration maps the provider base with `of_iomap()` and stores the base indirectly in each PLL object; unregister recovers one base pointer from registered clocks before `iounmap()`. There is no persistent storage.

Dependencies and integration points: the file integrates with Linux CCF `clk_hw_register()`, OF MMIO mapping, `clk_init_data`, and local PLL descriptors from `clk-pll.h`. `clk-pllfh.c` reuses most of these functions while replacing `.set_rate` with frequency-hopping control.

Risks: descriptor correctness is critical: bad register offsets, bit widths, `pcwbits`, `pd_shift`, or fmax/fmin constraints directly misprogram PLL hardware. Bulk registration does not check duplicate IDs before writing in the error unwind path, unlike some other helpers. Base unmapping relies on at least one registered clock to recover the mapping, which is fragile if descriptors or registration state are corrupted. Rate programming has no explicit locking in this file, so serialization relies on CCF and platform usage.

Test signals: boot logs should show no failed PLL registration. `clk_summary` should report expected PLL rates after `clk_set_rate()`. Tests should cover rates near `fmin`/`fmax`, fractional PCW rounding, divider-table entries, prepare/unprepare power bits, set/clear/fenc variants, and tuner enable state around rate changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-pll.h -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-pll.h

Purpose: `clk-pll.h` defines the descriptor and runtime structures for MediaTek PLL clocks and declares the common PLL operations implemented in `clk-pll.c`.

Important APIs and types: `struct mtk_pll_div_table` describes frequency thresholds for post-divider selection. Flags include `HAVE_RST_BAR`, `PLL_AO`, `PLL_PARENT_EN`, and `POSTDIV_MASK`. `struct mtk_pll_data` contains all hardware description fields: IDs, names, register offsets, enable masks, fenc status offset/bit, post-divider and PCW metadata, tuner metadata, optional init ops, PLL flags, fmin/fmax, divider table, parent name, set/clear registers, PLL enable bit, and PCW change bit. `struct mtk_clk_pll` stores resolved MMIO addresses, device pointer, `clk_hw`, and descriptor pointer.

Control flow: this header does not execute code except for `to_mtk_clk_pll()`. Its field layout drives the implementation: registration resolves offsets to MMIO pointers, prepare/unprepare consult flags and enable bits, rate calculation consults PCW fields and divider tables, and set/clear variants consult enable set/clear addresses and fenc fields.

State and persistence: descriptor instances are static SoC data. Runtime state is the allocated `struct mtk_clk_pll`, common clock registration state, and hardware PLL registers. No persistent storage exists.

Dependencies and integration points: it includes Linux clock-provider and type headers. It is used by normal PLL registration and by PLL frequency-hopping support, where `struct mtk_fh` embeds `struct mtk_clk_pll`.

Risks: many fields have default-by-zero semantics, such as `pll_en_bit`, `pcw_chg_bit`, `pcw_chg_reg`, and parent name. This is compact but makes descriptor review important because omission can be intentional or a bug. Register offsets are SoC-specific and untyped, so invalid offsets compile cleanly. Consumers must ensure ID values fit the onecell data array allocated by the parent clock driver.

Test signals: compile tests should cover all SoC descriptor initializers. Runtime checks should validate PLL parent names, rate rounding, lock/fenc status bits, always-on critical flags for `PLL_AO`, parent-enable behavior for `PLL_PARENT_EN`, and unregister cleanup under driver removal or probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-pll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-pllfh.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-pllfh.c

Purpose: `clk-pllfh.c` extends the MediaTek PLL framework with FHCTL frequency-hopping support. When a PLL has enabled FHCTL state from device tree, it registers the PLL with normal prepare/recalc/determine operations but routes rate changes through FHCTL hopping operations instead of direct PCW writes.

Important APIs and functions: `to_mtk_fh()` converts from PLL clock hardware to the enclosing `struct mtk_fh`. `fhctl_parse_dt()` parses a compatible FHCTL node and updates the caller-provided `mtk_pllfh_data` array. `mtk_clk_register_pllfhs()` bulk-registers a mixed set of FHCTL-backed PLLs and normal PLLs. `mtk_clk_unregister_pllfhs()` unregisters both variants and unmaps MMIO bases.

Control flow: `fhctl_parse_dt()` finds the FHCTL node, maps its registers, counts clock parents, reads paired `clocks` cells to find PLL IDs, reads `mediatek,hopping-ssc-percent`, and marks matching `mtk_pllfh_data` entries enabled with the FHCTL base and SSC rate. Registration maps the normal PLL provider base, walks each PLL descriptor, locates matching FH data, and either calls `mtk_clk_register_pllfh()` or falls back to `mtk_clk_register_pll()`. FH registration allocates `struct mtk_fh`, initializes register pointers from the FHCTL offset table, registers the embedded PLL with `mtk_pllfh_ops`, then calls `fhctl_hw_init()`.

State and persistence: state is held in the mutable `mtk_pllfh_data.state` entries, the FHCTL MMIO mapping, the normal PLL MMIO mapping, and allocated `struct mtk_fh` objects. No data survives reboot.

Dependencies and integration points: this file depends on `clk-pll.h`, `clk-pllfh.h`, and `clk-fhctl.h`. It integrates the common PLL CCF path with FHCTL operations returned by `fhctl_get_ops()` and offset tables returned by `fhctl_get_offset_table()`.

Risks: FHCTL enablement is parsed by matching PLL IDs from a DT `clocks` property; incorrect cell layout or missing SSC entries leaves PLLs using normal direct programming. `fhctl_parse_dt()` maps one FHCTL base and shares it across enabled PLL entries; unregister only unmaps a stored `fhctl_base` if at least one enabled FH PLL was registered. `mtk_clk_register_pllfhs()` does not check duplicate onecell IDs before assignment. Error unwind must choose the same FH-vs-normal path as registration, so descriptor/state drift can leak or unregister incorrectly.

Test signals: validate DT parsing with enabled and absent FHCTL nodes, check SSC rates appear in `pllfh_data.state`, confirm `clk_set_rate()` calls FH hopping through hardware behavior or tracepoints, verify fallback normal PLLs still change rate, and exercise probe-failure unwind with mixed FH and non-FH PLLs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-pllfh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-pllfh.h -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-pllfh.h

Purpose: `clk-pllfh.h` defines the data structures and external interface for MediaTek PLL frequency-hopping support layered over the normal PLL clock implementation.

Important APIs and types: `struct fh_pll_state` stores FHCTL base, enable state, and SSC rate. `struct fh_pll_data` describes per-PLL FHCTL identity, version, register offset, DDS mask, slopes, enable bits, trigger bits, delta fields, and update limit shift. `struct mtk_pllfh_data` combines mutable state with constant descriptor data. `struct fh_pll_regs` stores resolved FHCTL register pointers. `struct mtk_fh` embeds `struct mtk_clk_pll` and adds FH registers, descriptor pointer, operation table, and lock. `struct fh_operation` defines `hopping()` and `ssc_enable()` callbacks.

Control flow: the header itself only declares interfaces. Runtime flow is implemented by `clk-pllfh.c`: parse FHCTL DT state, initialize `struct mtk_fh` register pointers from FHCTL offset tables, register clocks with PLL operations that call FH hopping for rate changes, and unregister mixed FH/non-FH PLLs.

State and persistence: FH state is transient and lives in `mtk_pllfh_data.state`, FHCTL registers, and `struct mtk_fh`. The constant `fh_pll_data` descriptors are compiled into SoC drivers.

Dependencies and integration points: the header includes `clk-pll.h` because FH PLLs embed the normal MediaTek PLL object and reuse PLL prepare/recalc/rate-calculation helpers. It is consumed by SoC drivers that provide FH descriptor arrays and by FHCTL helper code.

Risks: descriptor values are highly hardware-specific; a bad `fh_ver`, `fhx_offset`, mask, slope, or trigger bit may cause rate changes to hang or program an unintended PLL. `fh_enable` is mutable and set by DT parsing, so initialization order matters. The API assumes callers pass arrays whose PLL IDs correspond to the normal PLL descriptor IDs.

Test signals: test by building FH-enabled SoC drivers, booting with and without FHCTL DT nodes, checking FH-enabled PLLs use hopping on rate changes, confirming SSC configuration is applied when requested, and validating unregister cleanup does not leave FHCTL mappings or registered clocks behind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-pllfh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/reset.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/reset.c

Purpose: `reset.c` registers reset-controller support for MediaTek clock-controller blocks. It supports two hardware styles: simple read/modify/write reset bits and set/clear register pairs.

Important APIs and functions: the exported entry point is `mtk_register_reset_controller_with_dev()`. Internal operations include `mtk_reset_assert()`, `mtk_reset_deassert()`, `mtk_reset()`, set/clear variants, and `reset_xlate()` for optional DT reset-index remapping.

Control flow: registration validates the descriptor, selects `reset_control_ops` based on `desc->version`, resolves the clock-controller regmap from the device node, allocates `struct mtk_clk_rst_data` with devm, fills `reset_controller_dev`, and registers it with `devm_reset_controller_register()`. Runtime assert/deassert calculates the bank offset from `id / RST_NR_PER_BANK` and bit from `id % RST_NR_PER_BANK`. Simple mode uses `regmap_update_bits()` with either all ones for assert or zero for deassert. Set/clear mode writes the bit to the bank offset, adding `0x4` for deassert.

State and persistence: reset state is entirely in hardware registers. The in-memory controller data and registration are devm-scoped to the device. No persistent data is stored.

Dependencies and integration points: the code depends on Linux reset-controller APIs, regmap syscon lookup, platform device infrastructure, and `reset.h`. `clk-mtk.c` invokes it when a clock descriptor includes `rst_desc`, allowing one clock-controller node to provide both clocks and resets.

Risks: the simple mode uses `regmap_update_bits()` with `val = ~0` for assert, relying on the mask to constrain the write. Descriptor bank offsets and optional `rst_idx_map` must be correct or reset consumers will manipulate the wrong lines. `reset_xlate()` validates against both `nr_resets` and `rst_idx_map_nr`, but only when a map is present; direct mode exposes `rst_bank_nr * 32` linear resets.

Test signals: DT reset consumers should acquire, assert, deassert, and pulse expected reset lines. Probe logs should show no unknown reset version or regmap lookup failures. Hardware validation can read reset registers before and after reset operations and verify mapped reset indexes match binding definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/reset.h -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/reset.h

Purpose: `reset.h` declares the MediaTek clock-reset descriptor format and the registration API used by MediaTek clock-controller drivers.

Important APIs and types: it defines `RST_NR_PER_BANK` as 32 and exposes INFRA reset set-register offsets used by SoC descriptors. `enum mtk_reset_version` distinguishes `MTK_RST_SIMPLE` from `MTK_RST_SET_CLR`. `struct mtk_clk_rst_desc` describes hardware version, reset bank offsets, bank count, optional reset index map, and map length. `struct mtk_clk_rst_data` is the runtime container for regmap, `reset_controller_dev`, and descriptor. The exported function is `mtk_register_reset_controller_with_dev()`.

Control flow: the header has no executable flow. Its descriptors drive `reset.c`, where the selected version chooses reset ops and optional `rst_idx_map` changes DT phandle translation from direct IDs to mapped reset bits.

State and persistence: descriptor arrays are static SoC data. Runtime state is allocated by the reset registration implementation and hardware reset state lives in the controller registers.

Dependencies and integration points: it depends on Linux reset-controller and type headers. It is included by `clk-mtk.h` so `struct mtk_clk_desc` can carry an optional reset descriptor, tying clock and reset provider setup together.

Risks: `rst_bank_ofs` and `rst_idx_map` are mutable pointer types even though they describe static tables; accidental modification would affect all reset users. The comment for `mtk_register_reset_controller_with_dev()` refers to `np` while the parameter is `dev`, a documentation drift but not a behavior issue. Incorrect map lengths or offsets can expose invalid resets to device tree consumers.

Test signals: compile-test SoC descriptors, inspect `/sys/kernel/debug/reset` where available, verify reset phandle translation for mapped controllers, and check that clock-controller probe registers resets only when a descriptor is provided.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/meson/Kconfig

Purpose: this Kconfig menu defines build-time configuration for Amlogic Meson common clock helpers and SoC-specific clock controller drivers. It gates the Meson clock driver family behind `ARCH_MESON || COMPILE_TEST`.

Important symbols: helper symbols include `COMMON_CLK_MESON_REGMAP`, `DUALDIV`, `MPLL`, `PHASE`, `PLL`, `SCLK_DIV`, `VID_PLL_DIV`, `VCLK`, `CLKC_UTILS`, `AO_CLKC`, and `CPU_DYNDIV`. SoC/controller symbols include `COMMON_CLK_MESON8B`, `COMMON_CLK_GXBB`, `COMMON_CLK_AXG`, `COMMON_CLK_AXG_AUDIO`, `COMMON_CLK_A1_PLL`, `COMMON_CLK_A1_PERIPHERALS`, `COMMON_CLK_C3_PLL`, `COMMON_CLK_C3_PERIPHERALS`, `COMMON_CLK_G12A`, `COMMON_CLK_S4_PLL`, `COMMON_CLK_S4_PERIPHERALS`, `COMMON_CLK_T7_PLL`, and `COMMON_CLK_T7_PERIPHERALS`.

Control flow: Kconfig selection controls which objects the Makefile builds. Helper symbols are mostly tristate and selected by SoC drivers. SoC entries select the common helper implementations they need, such as regmap, PLL, MPLL, dualdiv, AO clock controller, CPU dynamic divider, video clock helpers, reset controller, and syscon support.

State and persistence: this file affects kernel configuration state, not runtime state. Selected options are persisted in `.config` and determine which modules or built-ins are compiled.

Dependencies and integration points: the menu integrates with the kernel build system, architecture symbols, reset-controller support, regmap/syscon, auxiliary bus support for AXG audio, and optional SCMI clock support through `imply` on newer platforms.

Risks: missing `select` entries cause link failures or runtime missing helpers; overly broad `select` entries build unnecessary code. Some SoC configs default to `ARCH_MESON`, so dependency drift can change default kernel size. `COMMON_CLK_AXG_AUDIO` implies but does not hard-select `RESET_MESON_AUX`, so reset functionality may depend on broader config resolution.

Test signals: run `make olddefconfig` and compile for `ARCH_MESON`, ARM64 `COMPILE_TEST`, and module builds. Verify selected object lists match expected helpers and that all SoC clock drivers link when enabled independently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/meson/Makefile

Purpose: this Makefile maps Meson Kconfig symbols to the common helper and SoC-specific clock-controller objects built by Kbuild.

Important entries: common helper objects include `meson-clkc-utils.o`, `meson-aoclk.o`, `clk-cpu-dyndiv.o`, `clk-dualdiv.o`, `clk-mpll.o`, `clk-phase.o`, `clk-pll.o`, `clk-regmap.o`, `sclk-div.o`, `vid-pll-div.o`, and `vclk.o`. Controller objects include `axg.o`, `axg-aoclk.o`, `axg-audio.o`, `a1-pll.o`, `a1-peripherals.o`, C3, GXBB, G12A, Meson8, S4, and T7 objects.

Control flow: Kbuild expands each `obj-$(CONFIG_...)` assignment based on configuration. For `COMMON_CLK_AXG`, both `axg.o` and `axg-aoclk.o` are built together. Other controllers map one symbol to one object.

State and persistence: this file has no runtime state. It contributes build graph state during kernel compilation.

Dependencies and integration points: it relies on Kconfig to select helper symbols before SoC objects that reference them. It integrates with module or built-in builds through standard Kbuild `obj-*` semantics.

Risks: object lists must stay synchronized with Kconfig and source files. Missing helper objects surface as unresolved symbols, while stale object entries break builds when files are removed. Bundling `axg.o axg-aoclk.o` under one symbol means AXG main and AO clock support are compiled together.

Test signals: compile all Meson clock configs as built-in and modules under `ARCH_MESON`/ARM64 and `COMPILE_TEST`. Confirm `modules.order` and built object lists include the expected files for each selected symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/a1-peripherals.c -->
# sources/distributed-fs/ceph-client/drivers/clk/meson/a1-peripherals.c

Purpose: `a1-peripherals.c` is the Amlogic A1 peripherals clock-controller driver. It declares a large static clock tree for system, DSP, RTC, CEC, PWM, SPI, USB, SD/eMMC, PSRAM, DMC, and many peripheral bus gates, then registers it through the Meson MMIO clock-controller helper.

Important APIs and types: the file uses `struct clk_regmap`, `struct clk_fixed_factor`, `struct meson_clk_dualdiv_data`, `struct clk_regmap_mux_data`, `struct clk_regmap_div_data`, and `struct clk_regmap_gate_data`. It exports no public functions; its platform driver is registered with `module_platform_driver(a1_peripherals_clkc_driver)`. The clock provider data is `a1_peripherals_clkc_data` and the onecell array is `a1_peripherals_hw_clks[]`.

Control flow: there is little imperative logic. Probe is delegated to `meson_clkc_mmio_probe`, which uses the OF match data for `"amlogic,a1-peripherals-clkc"`. Static descriptors model the tree: oscillator input gates feed PLL input names; RTC and CEC 32 kHz clocks use dual-divider tables; system A/B clock branches are read-only boot-owned mux/div/gate chains and feed the critical `sys` mux; DSP A/B clocks have selectable mux/div/gate branches; device clocks are expressed as mux/div/gate chains; peripheral PCLK gates are generated through the `A1_PCLK` macro.

State and persistence: all runtime state is common clock framework registration state and the hardware register fields described by offsets such as `SYS_CLK_CTRL0`, `SYS_CLK_EN0`, and device-specific clock control registers. Boot firmware state is preserved for read-only system clocks and critical clocks. There is no persistent storage.

Dependencies and integration points: it depends on Meson `clk-regmap`, `clk-dualdiv`, and `meson-clkc-utils`, plus DT bindings from `amlogic,a1-peripherals-clkc.h`. It consumes external parent clocks by firmware names such as `xtal`, `fclk_div2`, `fclk_div3`, `fclk_div5`, `fclk_div7`, and `hifi_pll`, which are supplied by the A1 PLL controller or fixed firmware clocks.

Risks: the provider array is sparse and indexed by binding IDs; wrong indexes break DT consumers. Several gates use `CLK_IGNORE_UNUSED` for historical reasons, which can hide missing consumers and keep unused hardware active. Read-only system clocks assume boot firmware set safe values. Parent value tables skip unsupported hardware selector values; adding support requires careful binding and mux table updates.

Test signals: boot A1 with both PLL and peripherals controllers and inspect `clk_summary` for all binding IDs. Exercise consumers for UART, I2C, PWM, SPI, USB, SD/eMMC, SARADC, CEC, DSP, PSRAM, and DMC. Check that critical `sys` and fclk-derived clocks are never disabled, and verify rate setting for PWM/SPI/SD/USB mux-div-gate paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/a1-peripherals.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/a1-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/meson/a1-pll.c

Purpose: `a1-pll.c` is the Amlogic A1 PLL clock-controller driver. It exposes fixed PLL, hifi PLL, and fixed-factor fclk divider outputs used as parents by the A1 peripheral clock controller.

Important APIs and types: the file uses Meson `struct clk_regmap` PLL and gate descriptors, `struct clk_fixed_factor` for fclk divisions, `struct meson_clk_pll_data`, and `struct meson_clkc_data`. It registers a platform driver named `a1-pll-clkc` and delegates probe to `meson_clkc_mmio_probe`.

Control flow: static descriptors define `fixed_pll_dco` as a read-only PLL from `fixpll_in`, gate it as `fixed_pll`, derive fclk div2/div3/div5/div7 fixed factors from it, and gate each output. `hifi_pll` is a programmable PLL from `hifipll_in` with init register sequences and an M range of 32 to 64. The OF match table for `"amlogic,a1-pll-clkc"` passes `a1_pll_clkc_data` to the common MMIO probe.

State and persistence: runtime state lives in ANACTRL PLL registers and CCF registration structures. `fclk_div2`, `fclk_div3`, and `fclk_div5` are marked `CLK_IS_CRITICAL` because boot firmware or platform buses depend on them. No storage persists beyond hardware state.

Dependencies and integration points: it depends on Meson `clk-pll`, `clk-regmap`, and `meson-clkc-utils`, plus binding IDs from `amlogic,a1-pll-clkc.h`. It supplies firmware-name parents such as `fclk_div2` and `hifi_pll` consumed by `a1-peripherals.c`.

Risks: PLL init sequences and bit fields must match the A1 analog controller. Critical flags keep important clocks enabled but can mask missing ownership handoff. `fixed_pll_dco` is read-only, so attempts to change derived rates must resolve through allowed dividers or hifi PLL paths.

Test signals: `clk_summary` should show fixed PLL DCO, fixed PLL, fclk dividers, and hifi PLL at expected rates. Rate-change tests should cover hifi PLL programming and lock status. Boot tests should confirm DDR/APB/AXI dependent fclk outputs remain enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/a1-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/axg-aoclk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/meson/axg-aoclk.c

Purpose: `axg-aoclk.c` implements the Amlogic AXG always-on clock controller. It provides AO peripheral gates, 32 kHz clock generation/selection, RTC oscillator selection, SARADC clocking, and AO reset mappings.

Important APIs and types: the driver uses `MESON_PCLK`-based gates, `struct clk_regmap` mux/div/gate descriptors, `struct meson_clk_dualdiv_data`, `struct meson_aoclk_data`, and reset binding arrays. The platform driver `axg-ao-clkc` delegates probe to `meson_aoclkc_probe`.

Control flow: AO pclk gates are created from `AO_RTI_GEN_CNTL_REG0` with `CLK_IGNORE_UNUSED`. The 32 kHz path gates `cts_oscin`, enables `axg_ao_32k_pre`, runs a dual-divider table that approximates 32 kHz from xtal, selects between divided and pre clocks, and gates `axg_ao_32k`. RTC oscillator input can select internal 32 kHz or external `ext_32k-0`. SARADC uses mux, divider, and gate descriptors. The `meson_aoclk_data` bundles clock data with reset register and reset line map.

State and persistence: runtime state is in AO register bits and reset bits. AO domain clocks may remain active across low-power states, but the driver stores no persistent data. Registration state is owned by CCF and AO clock helper code.

Dependencies and integration points: it depends on `meson-aoclk`, `clk-regmap`, `clk-dualdiv`, reset controller support, and DT bindings from `axg-aoclkc.h`. Parent firmware names include `mpeg-clk`, `xtal`, and optional external 32 kHz input.

Risks: AO clocks often service wakeup or low-power peripherals; disabling the wrong gate can break remote, UART, I2C, IR, or SARADC behavior. The old PWM binding note on `axg_ao_clk81` means global clock-name compatibility still matters. Reset map indexes must match the reset binding exactly.

Test signals: validate AO consumers for remote, I2C, UART, IR, SARADC, and RTC. Check 32 kHz output accuracy, external 32 kHz selection, reset assert/deassert for AO devices, and suspend/resume wake capability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/axg-aoclk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/axg-audio.c -->
# sources/distributed-fs/ceph-client/drivers/clk/meson/axg-audio.c

Purpose: `axg-audio.c` implements the Amlogic AXG/G12A/SM1 audio clock controller. It declares audio bus gates, master clocks, sample clocks, TDM input/output clocks, SPDIF/PDM clocks, pad clock selectors, and newer SM1 eARC/sysclk additions, then registers the selected SoC variant through a custom platform probe.

Important APIs and types: macro families `AUD_GATE`, `AUD_MUX`, `AUD_DIV`, `AUD_PCLK_GATE`, `AUD_SCLK_DIV`, `AUD_TRIPHASE`, `AUD_PHASE`, `AUD_SCLK_WS`, and `AUD_TDM_PAD_CTRL` generate `struct clk_regmap` descriptors. `struct audioclk_data` holds the variant `meson_clk_hw_data`, optional auxiliary reset driver name, and max register. The probe is `axg_audio_clkc_probe()`.

Control flow: the driver selects variant data from OF compatible strings `amlogic,axg-audio-clkc`, `amlogic,g12a-audio-clkc`, and `amlogic,sm1-audio-clkc`. Probe maps MMIO, initializes regmap, enables mandatory `pclk`, resets the device, registers all non-input clock hardware from the variant array, adds the OF clock provider, and optionally creates an auxiliary reset device (`rst-g12a` or `rst-sm1`). Static clock arrays are variant-specific: AXG has the base set, G12A adds SPDIFOUT_B and pad controls, and SM1 changes register offsets, adds `aud_top` sysclk selection, more gates, and eARC clocks.

State and persistence: state is in audio clock registers and registered CCF objects. Input clocks are intentionally skipped at runtime by starting registration at `AUD_CLKID_DDR_ARB`; those input slots are expected from DT parent clocks. Reset side effects happen through `device_reset()` and optional auxiliary reset device creation.

Dependencies and integration points: the driver depends on auxiliary bus, regmap MMIO, reset APIs, Meson clock helpers, phase and sclk divider helpers, and DT binding IDs from `axg-audio-clkc.h`. It integrates with audio subsystem consumers that request TDM, SPDIF, PDM, FRDDR/TODDR, resample, loopback, eARC, and pad clocks.

Risks: this file has many generated descriptors with repeated names and SoC-specific register offsets, so variant arrays must point to the correct descriptor set. Probe requires `pclk`; missing clock or reset resources fail the whole controller. The arrays are sparse and input clocks are populated externally, so binding ID drift or missing parents can break audio graph setup. `CLK_SET_RATE_NO_REPARENT`, phase controls, and duty-cycle flags are important for audio signal integrity.

Test signals: compile all three variants, boot with representative AXG/G12A/SM1 DTs, inspect `clk_summary` for audio IDs, and run audio playback/capture through TDM, SPDIF, and PDM. Verify master clock rates, LRCLK/SCLK phase controls, pad muxes, reset auxiliary device creation, and SM1 eARC clocks where hardware is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/axg-audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/axg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/meson/axg.c

Purpose: `axg.c` is the main Amlogic AXG clock-controller driver for the HHI domain. It exposes PLLs, MPLLs, fixed-clock dividers, PCIe reference clocks, clk81, SD/eMMC clocks, VPU/VAPB clocks, video clocks, measurement clocks, a general-purpose clock, and many EE/AO peripheral gates.

Important APIs and types: the file is almost entirely static descriptors using `struct clk_regmap`, `struct clk_fixed_factor`, Meson PLL data, MPLL data, mux/divider/gate data, and `MESON_PCLK` gates. It provides `axg_clkc_data` and a platform driver named `axg-clkc` that uses `meson_clkc_syscon_probe`.

Control flow: probe is delegated through the OF match for `"amlogic,axg-clkc"`. The clock tree starts with fixed, sys, gp0, hifi, and PCIe PLL descriptors; derives fclk div2/div3/div4/div5/div7; creates MPLL0-3 from an MPLL predivider; builds PCIe mux/ref/CML gates; creates the critical `clk81` tree; defines SD/eMMC mux/div/gates; creates dual VPU and VAPB branches with mux selection; builds video clock and video2 paths with fixed post-dividers and ENCL selection; defines VDIN measurement and generic clock paths; and finally registers large groups of pclk gates for EE and AO domains.

State and persistence: runtime state is in HHI syscon registers and CCF registrations. Some clocks are marked critical or ignore-unused to preserve firmware or display state, especially fclk dividers, clk81, VPU/VAPB, and video gates. No persistent storage is used.

Dependencies and integration points: the file depends on Meson `clk-regmap`, `clk-pll`, `clk-mpll`, and `meson-clkc-utils`, with IDs from `axg-clkc.h`. It consumes firmware parent `xtal` and provides core clocks used by AXG peripheral, storage, PCIe, display, audio, and AO subsystems.

Risks: clock IDs in `axg_hw_clks[]` must match the binding exactly. PLL init tables are hardware-sensitive. Several parent value tables skip reserved hardware values, so selector programming must preserve those assumptions. `CLK_IGNORE_UNUSED` can hide ownership bugs but protects bootloader-enabled display paths. Shared syscon registers mean mux/div/gate definitions must not overlap incorrectly.

Test signals: boot on AXG and inspect `clk_summary`, especially PLL lock/rates, clk81, fclk divisors, SD/eMMC rates, PCIe ref, VPU/VAPB, and video clocks. Exercise MMC, PCIe, display, VDIN, audio parent clocks, USB, Ethernet, UART, SPI, and AO consumers. Test module removal or probe failure if built as a module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/meson/axg.c -->
