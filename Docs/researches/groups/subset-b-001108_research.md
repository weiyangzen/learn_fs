# subset-b-001108 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-audio.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-audio.c

Purpose: platform driver for the MMP2 audio clock controller, exposing the audio PLL plus SYSCLK, SSPA0, and SSPA1 output clocks through a onecell OF provider.

Important APIs/functions: `audio_pll_recalc_rate`, `audio_pll_determine_rate`, and `audio_pll_set_rate` implement the custom PLL `clk_ops` from known pre-divider/post-divider tables. `register_clocks` wires the PLL, muxes, dividers, and gates with `devm_clk_hw_register`. `mmp2_audio_clk_probe`, `mmp2_audio_clk_remove`, and runtime PM callbacks manage resources and saved registers.

Control flow: probe allocates `struct mmp2_audio_clk`, maps MMIO, enables runtime PM and PM clock support, adds the external audio clock, then registers the internal clock tree and `of_clk_add_hw_provider`. Rate changes search the precomputed table for an exact VCO/post-divider match and write `SSPA_AUD_PLL_CTRL0/1`.

State and persistence: MMIO register state is live hardware state. Suspend stores `SSPA_AUD_CTRL` and PLL control registers in the driver private struct; resume restores them after `pm_clk_resume`.

Dependencies and integration: depends on CCF helpers, `pm_clock`, runtime PM, platform resources, and `dt-bindings/clock/marvell,mmp2-audio.h`. Consumers use the three exported clock IDs from device tree.

Risks: unsupported parent rates return zero or rounded rates; `audio_pll_set_rate` only accepts exact table-derived rates. Register restore ordering and PM clock failures can leave audio clocks unusable after suspend. There is a spinlock in the private struct, but the CCF subclocks are not configured to use it.

Test signals: boot on MMP2 audio DT, `clk_summary` showing audio PLL and SSPA clocks, rate round/set tests for 11.2896/12.288 MHz families, suspend/resume audio playback, and module bind/unbind error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-frac.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-frac.c

Purpose: implements the MMP fractional M/N clock type used for UART and I2S synthesizer clocks.

Important APIs/functions: `mmp_clk_register_factor` allocates and registers `struct mmp_clk_factor`. The `clk_factor_ops` callbacks are `clk_factor_recalc_rate`, `clk_factor_determine_rate`, `clk_factor_set_rate`, and `clk_factor_init`.

Control flow: `determine_rate` scans a caller-provided `u32_fract` table and picks the nearest output derived from `parent * denominator / (numerator * factor)`. `set_rate` chooses the nearest not-greater table entry, masks numerator/denominator fields, and writes the MMIO register under an optional spinlock. `init` validates the current hardware fraction against the table and enables or normalizes the synthesizer.

State and persistence: state is in the hardware register at `base`; the allocated `mmp_clk_factor` stores masks, table pointer, count, and lock. No suspend state is kept here.

Dependencies and integration: included by MMP SoC clock files through `clk.h`. It uses Linux CCF, `do_div`, `u32_fract`, relaxed MMIO access, and optional SoC-provided locks.

Risks: `determine_rate` assumes the table is ordered by increasing effective rate. A zero denominator in hardware returns zero rate. `set_rate` silently falls back to the first entry for very low rates and always returns success after programming an approximate value.

Test signals: unit-level checks of table ordering and rounding, UART/I2S baud/audio sample-rate validation, and boot logs for synthesized clocks after `clk_factor_init`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-frac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-gate.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-gate.c

Purpose: provides an MMP-specific CCF gate for registers where enable and disable values are multi-bit patterns rather than a single bit.

Important APIs/functions: `mmp_clk_gate_ops` supplies `enable`, `disable`, and `is_enabled`. `mmp_clk_register_gate` allocates `struct mmp_clk_gate` and registers it with the common clock framework.

Control flow: enable and disable read the target register, clear the configured mask, OR in `val_enable` or `val_disable`, and write back under an optional spinlock. When `MMP_CLK_GATE_NEED_DELAY` is set, enable waits about two clock cycles based on `clk_hw_get_rate`.

State and persistence: no software state beyond the allocated gate metadata; enable state is the masked MMIO value. Persistence across suspend is handled by SoC-level code if required.

Dependencies and integration: used by the MMP registration helpers and SoC tables for APBC/APMU gates. Depends on CCF, MMIO, delays, and locks supplied in table entries.

Risks: if the clock rate is zero, the delay calculation can divide by zero. Incorrect masks or enable values can overwrite adjacent control bits. `is_enabled` requires exact equality with `val_enable`, so partially enabled hardware encodings are treated as off.

Test signals: per-clock enable/disable smoke tests, `clk_summary` gate status, boot testing peripherals with reset-sensitive APBC clocks, and static review of mask/value pairs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-gate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-mix.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-mix.c

Purpose: implements MMP "mix" clocks that combine mux and divider fields which must be programmed together, often with a hardware frequency-change request bit.

Important APIs/functions: exported `mmp_clk_mix_ops` and `mmp_clk_register_mix`. Internal helpers translate divider/mux encodings (`_get_div`, `_get_div_val`, `_get_mux`, `_get_mux_val`), filter suggested tables, and `_set_rate` performs the atomic hardware update.

Control flow: initialization optionally filters a rate table based on actual parent rates. `determine_rate` either searches that table or brute-forces parents and divisors. `set_rate`, `set_parent`, and `set_rate_and_parent` convert selected parent/divider values to register encodings and call `_set_rate`. `_set_rate` handles V1 direct writes, V2 writes with a polling frequency-change bit, and V3 split control/select registers.

State and persistence: software state stores copied table and mux table data plus register descriptors and type. Persistent state is in hardware mux/divider fields.

Dependencies and integration: MMP SoC files use it for SDH, CCIC, GPU, and other clocks where mux and divider share registers. It depends on CCF composite-style semantics but registers as a single `clk_hw`.

Risks: division by zero is possible if a register encoding maps to divisor zero. V2 polling has a fixed 50-iteration timeout without delay. The table filter mutates the copied table at init and assumes parent rates are already available.

Test signals: requested-rate coverage for table and non-table clocks, parent switching, timeout/error path tests on emulated FC bits, and hardware boot checks for SDH/CCIC/GPU clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-mix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-of-mmp2.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-of-mmp2.c

Purpose: early OF clock initialization for Marvell MMP2 and MMP3, registering PLLs, fixed factors, APBC/APMU peripheral clocks, resets, and generic power domains.

Important APIs/functions: `mmp2_clk_init` is registered for `marvell,mmp2-clock` and `marvell,mmp3-clock`. `mmp2_main_clk_init`, `mmp2_apb_periph_clk_init`, `mmp2_axi_periph_clk_init`, `mmp2_clk_reset_init`, and `mmp2_pm_domain_init` split setup by controller area.

Control flow: init detects MMP2 versus MMP3 compatible, maps MPMU/APMU/APBC resources, registers PM domains, creates the onecell clock table, then registers root PLL/fixed-factor clocks, APB mux/gates, AXI/APMU mix/mux/div/gates, SoC-specific GPU/thermal/SDH additions, and APBC reset cells.

State and persistence: the allocated `mmp2_clk_unit` persists for the lifetime of the system. Clock and reset state is MMIO-backed; PM-domain state is represented by generic PM domains over APMU power island bits.

Dependencies and integration: uses `clk.h`, `reset.h`, MMP2/MMP3 clock and power DT bindings, CCF registration helpers, reset-controller integration, and genpd.

Risks: early-init allocations and MMIO mappings are mostly permanent; some failure paths unmap resources but not all intermediate registrations. A table entry in `mmp3_pll_clks` uses `MMP2_CLK_PLL2` for `"pll1"`, which deserves careful DT binding validation. Shared SDH mix clock setup uses the SDH0 register for all SDH clocks.

Test signals: boot on both MMP2 and MMP3 DTs, clock ID lookup for exported bindings, reset control for APBC devices, GPU/audio/camera genpd on/off, and `clk_summary` hierarchy comparison against expected PLL trees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-of-mmp2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-of-pxa168.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-of-pxa168.c

Purpose: early OF clock controller for Marvell PXA168, covering MPMU PLL/factor clocks, APBC low-speed peripheral clocks, APMU AXI peripheral clocks, and APBC resets.

Important APIs/functions: `pxa168_clk_init` is the `CLK_OF_DECLARE` entry. `pxa168_pll_init`, `pxa168_apb_periph_clk_init`, `pxa168_axi_periph_clk_init`, and `pxa168_clk_reset_init` register table-driven clocks and resets.

Control flow: init maps three register banks, initializes a 200-entry onecell provider, registers fixed roots (`clk32`, `vctcxo`, `pll1`, `usb_pll`), PLL1 fixed factors, a UART fractional PLL, APBC muxes/gates for TWSI/KPC/PWM/UART/SSP/timer, APMU mux/div/gates for DFC/USB/SDH/display/camera, then derives reset cells from APBC gate table offsets.

State and persistence: persistent state is hardware register contents plus the allocated `pxa168_clk_unit` and reset cell array. There is no explicit suspend state in this file.

Dependencies and integration: includes PXA168 DT clock IDs, MMP helper APIs, and reset-controller glue. Device-tree consumers resolve clocks through the onecell provider.

Risks: mapping failures after earlier successful `of_iomap` calls do not consistently unmap previous mappings. Clock IDs of zero are intentionally not inserted into the table, so table entries with id zero are name-only. Reset cells assume APBC reset bit `0x4` for every APBC gate.

Test signals: PXA168 boot with serial, I2C, SDH, USB, and display enabled; reset-controller phandle tests for APBC peripherals; `clk_summary` coverage of all nonzero binding IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-of-pxa168.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-of-pxa1928.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-of-pxa1928.c

Purpose: OF clock setup for PXA1928 split into separate MPMU, APMU, and APBC compatible nodes.

Important APIs/functions: `pxa1928_mpmu_clk_init`, `pxa1928_apmu_clk_init`, and `pxa1928_apbc_clk_init` are separate `CLK_OF_DECLARE` entries. Helpers register root/factor clocks, APBC mux/gates, APMU SDH/USB gates, and reset cells.

Control flow: MPMU init maps the PLL bank and registers fixed roots/factors plus `uart_pll`. APMU init creates an APMU onecell provider and registers one shared SDH mux/div plus gates for USB/HSIC/SDH0-4. APBC init creates an APBC onecell provider, registers UART/SSP muxes, APB gates for TWSI/GPIO/KPC/RTC/PWM/UART/SSP, and reset mappings.

State and persistence: each compatible node allocates its own `pxa1928_clk_unit`; MMIO registers hold clock state. Reset cells are derived from APBC gate table entries.

Dependencies and integration: uses PXA1928 DT clock bindings, MMP helper registration, and reset controller APIs. Root clocks are registered by name for cross-node parent references.

Risks: split providers mean parent names must be globally registered before consumers request derived clocks. Several fixed roots have id zero and are not exported by onecell ID. APMU uses the SDH0 register fields for the shared SDH mux/div while gates are per SDH register, so hardware assumptions are central.

Test signals: DT boot ordering across MPMU/APMU/APBC nodes, UART/SSP/SDH rate queries, reset phandle lookup by clock ID, and smoke tests for all exported PXA1928 clock IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-of-pxa1928.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-of-pxa910.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-of-pxa910.c

Purpose: early OF clock controller for PXA910, registering MPMU roots/factors, APBC and APBCP peripheral clocks, APMU clocks, and reset cells.

Important APIs/functions: `pxa910_clk_init` is the `CLK_OF_DECLARE` entry. `pxa910_pll_init`, `pxa910_apb_periph_clk_init`, `pxa910_axi_periph_clk_init`, and `pxa910_clk_reset_init` provide staged registration.

Control flow: init maps MPMU/APMU/APBC/APBCP resources, initializes a 200-entry onecell provider, registers fixed root and factor clocks plus UART fractional PLL, registers APBC and APBCP muxes/gates, registers APMU mux/div/gates for DFC/USB/SDH/display/camera, and creates reset cells from APBC plus APBCP gate arrays.

State and persistence: hardware MMIO holds clock/reset state. Allocated unit and reset cells are permanent after early init.

Dependencies and integration: uses PXA910 DT clock bindings, the shared MMP clock helpers, and reset-controller registration.

Risks: the APBCP reset loop indexes `apbc_gate_clks` and `apbc_base` instead of `apbcp_gate_clks` and `apbcp_base`, which looks like a real reset mapping bug. Failure paths correctly unmap resources before provider registration but not after partial clock registration.

Test signals: PXA910 boot with APBCP UART2/TWSI1 reset phandles, serial and SDH clocks, USB gates, and static validation of reset-cell register addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-of-pxa910.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-pll.c

Purpose: implements MMP PLL rate reporting for MMP2/MMP3-style PLL control registers.

Important APIs/functions: `mmp_register_pll_clks` registers arrays of `mmp_param_pll_clk`; internal `mmp_clk_register_pll` creates `struct mmp_clk_pll`; `mmp_clk_pll_is_enabled` and `mmp_clk_pll_recalc_rate` are the CCF operations.

Control flow: registration resolves optional rate and post-divider registers from offsets, then registers a no-parent clock. Rate recalculation returns `default_rate` when software enable bits are off. Otherwise it decodes feedback/reference dividers, and for MMP3 also decodes a post-divider table.

State and persistence: PLL configuration is read-only from hardware in this driver; no set-rate operation exists. Allocated `mmp_clk_pll` metadata persists.

Dependencies and integration: called from `clk-of-mmp2.c` through the parameter table in `clk.h`. Uses MMIO, CCF, and `do_div`.

Risks: `mmp_register_pll_clks` passes `base + postdiv_offset` even when `postdiv_offset` is zero, so MMP2 entries get a non-NULL base pointer and may enter the MMP3 calculation path unless the table relies on zero offset meaning valid base. Unsupported MMP2 `refdiv` values return zero and log an error.

Test signals: compare reported PLL rates against SAR/MPMU expected values on MMP2 and MMP3, verify disabled-default PLL behavior, and inspect `clk_summary` for PLL names and rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-pxa1908-apbc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-pxa1908-apbc.c

Purpose: platform driver for the PXA1908 APBC clock block, exposing APB peripheral muxes and gates.

Important APIs/functions: `pxa1908_apbc_probe` maps the APBC resource, initializes a 19-clock onecell provider, and calls `pxa1908_apb_periph_clk_init`. The helper registers shared PWM gates, SWJTAG through `mmp_clk_register_apbc`, muxes for UART/SSP, and APBC gate table entries.

Control flow: on bind, all clocks are registered from static tables. UART parents are `pll1_117` or `uart_pll`; SSP parents are PLL1 divided roots. PWM clocks share intermediate APB gates.

State and persistence: platform-device managed memory and MMIO mappings; actual enable/mux state is hardware-backed.

Dependencies and integration: PXA1908 DT clock IDs, shared MMP helper functions, and platform driver matching `marvell,pxa1908-apbc`.

Risks: some gate table entries have no locks while sharing registers, so concurrent CCF operations may race if consumers manipulate related APBC clocks. `APBC_NR_CLKS` must stay aligned with binding IDs. No remove path unregisters the provider.

Test signals: module/platform bind, UART0/1 console and SSP function, PWM shared-gate behavior, SWJTAG clock lookup, and `clk_summary` ID count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-pxa1908-apbc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-pxa1908-apbcp.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-pxa1908-apbcp.c

Purpose: platform driver for the PXA1908 APBCP clock block, covering UART2, TWSI2, and AICER/RIPC clocks.

Important APIs/functions: `pxa1908_apbcp_probe` maps the register resource, initializes a 4-clock onecell provider, and calls `pxa1908_apb_p_periph_clk_init`. Static tables define one UART2 mux and three gates.

Control flow: probe registers the UART2 mux first, then all gates, so `uart2_clk` can use `uart2_mux` as parent. The provider serves binding IDs from `dt-bindings/clock/marvell,pxa1908.h`.

State and persistence: device-managed allocation/MMIO; gate and mux state is persistent hardware state.

Dependencies and integration: depends on platform-device matching `marvell,pxa1908-apbcp`, CCF, MMP helper tables, and parent clocks from the MPMU provider.

Risks: small onecell size makes binding ID drift immediately harmful. The RIPC/AICER gate has no parent and custom enable value `0x2`, so consumer assumptions about parent rate may fail.

Test signals: UART2 and TWSI2 DT clock acquisition, APBCP provider registration, and register-level gate toggling checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-pxa1908-apbcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-pxa1908-apmu.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-pxa1908-apmu.c

Purpose: platform driver for the PXA1908 APMU clock block, including PLL1 branch gates, SDH mix clocks, USB/SDH gates, and creation of an auxiliary power controller device.

Important APIs/functions: `pxa1908_apmu_probe` maps MMIO, creates an auxiliary `"power"` device, initializes a 17-clock provider, and calls `pxa1908_axi_periph_clk_init`. That helper registers general PLL1 gates, three SDH mix clocks, and APMU gates.

Control flow: probe sets up power-controller integration before registering clocks. Each SDH controller has its own mix clock using parent choices `pll1_416` and `pll1_624`; gates use `CLK_SET_RATE_UNGATE` so rates can change while gated.

State and persistence: hardware registers hold clock state; the auxiliary device links the same platform device to the power-domain side.

Dependencies and integration: CCF, auxiliary bus, platform driver, PXA1908 bindings, and shared MMP mix/gate helpers.

Risks: reusing a single global `sdh_mix_config` while mutating its register address is safe only because `mmp_clk_register_mix` copies config fields. Missing remove cleanup leaves provider lifetime tied to device lifetime. Power auxiliary creation failure aborts clock registration.

Test signals: APMU bind, auxiliary power device appearance, SDH0-2 rate changes, USB clock enable, and PLL1 gate visibility in `clk_summary`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-pxa1908-apmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-pxa1908-mpmu.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-pxa1908-mpmu.c

Purpose: platform driver for the PXA1908 MPMU root clock provider, defining fixed PLL roots, fixed-factor PLL1 derivatives, and the UART fractional PLL.

Important APIs/functions: `pxa1908_mpmu_probe` maps the MPMU register block, creates a 39-clock onecell provider, and calls `pxa1908_pll_init`.

Control flow: registration creates fixed rates for clk32, vctcxo, and multiple PLL1 outputs; then it registers a tree of fixed factors such as `pll1_d2`, `pll1_d4`, `pll1_d96`, `pll1_32`, `pll1_208`, and `pll1_117`; finally it registers `uart_pll` from the MPMU UART PLL register.

State and persistence: fixed clocks are software constants; `uart_pll` is MMIO-backed by `clk-frac.c`. Device-managed resources are tied to the platform device.

Dependencies and integration: Linux units macros, PXA1908 DT bindings, platform CCF provider, and parent names consumed by APBC/APBCP/APMU drivers.

Risks: fixed PLL rates assume boot firmware configured expected frequencies. The UART fractional table exposes only one 14.745 MHz entry, limiting rate flexibility. Provider ID count must remain consistent with bindings.

Test signals: probe ordering before APB/APMU consumers, parent name resolution, UART baud-rate accuracy, and `clk_summary` root/factor hierarchy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-pxa1908-mpmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk.c

Purpose: shared table-driven registration utilities for MMP clock providers.

Important APIs/functions: `mmp_clk_init` creates an OF onecell clock table. `mmp_register_fixed_rate_clks`, `mmp_register_fixed_factor_clks`, `mmp_register_general_gate_clks`, `mmp_register_gate_clks`, `mmp_register_mux_clks`, and `mmp_register_div_clks` register arrays of parameter structs. `mmp_clk_add` inserts an arbitrary registered clock into a provider table.

Control flow: SoC files call `mmp_clk_init`, then invoke table helpers with base MMIO pointers. Each helper loops over its descriptor array, registers a CCF clock, logs failures, and stores successful nonzero IDs in `unit->clk_table`.

State and persistence: `mmp_clk_unit` owns the clock pointer table and onecell metadata; the clocks and providers persist after init. No unregister path is implemented here.

Dependencies and integration: CCF fixed-rate/fixed-factor/gate/mux/divider registration, OF onecell providers, `clk.h` descriptor types, and MMP custom gate APIs.

Risks: ID zero is never stored, so descriptor authors must reserve zero for non-exported internal clocks. Failed registrations only log and continue, which can produce partially populated providers. `mmp_clk_init` returns void, so callers may continue after allocation/provider failure.

Test signals: static table ID audits, `of_clk_get_by_name` and by index, boot log failure scans, and checking that provider `clk_num` matches binding maximums.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk.h -->
# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk.h

Purpose: shared private header for MMP clock drivers, defining custom clock data structures, parameter table formats, helper prototypes, and power-domain APIs.

Important APIs/types: defines `mmp_clk_factor`, `mmp_clk_mix`, `mmp_clk_gate`, `mmp_clk_unit`, parameter structs for fixed-rate/factor/gate/mux/div/PLL clocks, `mmp_clk_mix_config`, `mmp_clk_mix_reg_info`, `DEFINE_MIX_REG_INFO`, and `mmp_pm_domain_register`.

Control flow: the header itself has no runtime control flow, but its descriptor types drive the table loops in `clk.c`, custom registration in `clk-frac.c`, `clk-gate.c`, `clk-mix.c`, `clk-pll.c`, and power islands.

State and persistence: structs describe persistent CCF objects and MMIO-backed register metadata. `mmp_clk_unit` is the central provider state for onecell lookups.

Dependencies and integration: includes CCF provider APIs, math helpers, PM domains, and clkdev. It is the integration contract between generic MMP helper files and SoC-specific clock tables.

Risks: bit macros use `1 << width`, so invalid widths can overflow. Many fields are raw shifts/masks/offsets supplied by tables; no central validation prevents out-of-range IDs or register fields.

Test signals: build coverage for all MMP clock files, sparse/static analysis of table initializers, and binding/table consistency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/pwr-island.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mmp/pwr-island.c

Purpose: generic PM domain implementation for MMP APMU power islands.

Important APIs/functions: `mmp_pm_domain_register` creates a `generic_pm_domain` with `mmp_pm_domain_power_on` and `mmp_pm_domain_power_off` callbacks.

Control flow: power-on sets configured power bits, disables isolation via bit `0x100`, optionally toggles reset and clock-enable bits for blocks that need post-power reset sequencing, and restores the post-power-on value. Power-off clears power and isolation bits unless `MMP_PM_DOMAIN_NO_DISABLE` is set.

State and persistence: each allocated `mmp_pm_domain` stores MMIO address, masks, flags, lock, and embedded `generic_pm_domain`. Hardware register bits hold actual island state.

Dependencies and integration: used by `clk-of-mmp2.c` to expose GPU/audio/camera domains through genpd. Depends on PM domain core, MMIO, and optional spinlocks shared with clock gates.

Risks: isolation bit `0x100` is hard-coded for all users. Incorrect masks can reset or gate unrelated block bits. No unregister path or devm ownership exists for early-init allocations.

Test signals: genpd provider registration, runtime PM of GPU/audio/camera devices, power-on reset sequence validation on hardware, and suspend/resume checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/pwr-island.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/reset.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mmp/reset.c

Purpose: reset-controller bridge for MMP clock/reset bits, mapping reset specifier clock IDs to MMIO bit operations.

Important APIs/functions: `mmp_clk_reset_register` registers a `reset_controller_dev`. `mmp_of_reset_xlate` maps OF reset args to internal reset indexes. `mmp_clk_reset_assert` and `mmp_clk_reset_deassert` set or clear configured reset bits under optional locks.

Control flow: SoC files build `mmp_clk_reset_cell` arrays from APBC clock tables and call register. Consumers pass a clock ID in the reset specifier; xlate linearly searches cells for that ID, and reset ops operate on the matched register/mask.

State and persistence: `mmp_clk_reset_unit` and cell arrays persist after registration. Reset state is MMIO-backed.

Dependencies and integration: Linux reset-controller framework, OF phandles, MMP reset descriptors from `reset.h`, and shared APBC locks.

Risks: `flags` and `MMP_RESET_INVERT` are currently unused, so inverted reset support is declared but not implemented. Linear lookup is small but depends on unique clock IDs. No unregister path is provided.

Test signals: reset phandle resolution by binding IDs, assert/deassert register traces, device probe recovery after reset, and static checks for duplicate `clk_id` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/reset.h -->
# sources/distributed-fs/ceph-client/drivers/clk/mmp/reset.h

Purpose: private MMP reset-controller header.

Important APIs/types: defines `MMP_RESET_INVERT`, `struct mmp_clk_reset_cell`, `struct mmp_clk_reset_unit`, and the `mmp_clk_reset_register` prototype or stub depending on `CONFIG_RESET_CONTROLLER`.

Control flow: no runtime flow in the header. The stub makes SoC clock files build when reset-controller support is disabled.

State and persistence: cell descriptors carry clock ID, register address, reset bits, flags, and optional spinlock. The unit embeds a `reset_controller_dev`.

Dependencies and integration: includes Linux reset-controller types and is used by MMP SoC clock init files plus `reset.c`.

Risks: the invert flag is part of the interface but not honored by `reset.c`, which can mislead table authors. Header users need `struct device_node` visibility through other includes.

Test signals: build coverage with and without `CONFIG_RESET_CONTROLLER`, and reset phandle tests for SoC clock providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mmp/reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mstar/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/mstar/Kconfig

Purpose: declares configuration symbols for MStar/SigmaStar MSC313 clock drivers.

Important APIs/types: `MSTAR_MSC313_CPUPLL` controls the CPU PLL driver. `MSTAR_MSC313_MPLL` controls the MPLL/divider block and selects `REGMAP_MMIO`.

Control flow: Kconfig symbols are boolean, default to `ARCH_MSTARV7`, and allow `COMPILE_TEST` builds. The MPLL symbol ensures regmap-mmio support is present.

State and persistence: build-time only; it affects which object files are compiled into the kernel.

Dependencies and integration: tied to the mstar Makefile and platform drivers with `builtin_platform_driver`.

Risks: both drivers are bool-only and not modular. Missing `REGMAP_MMIO` selection for CPUPLL is fine because it uses raw MMIO, but any future refactor must revisit dependencies.

Test signals: `ARCH_MSTARV7` defconfig inclusion, `COMPILE_TEST` allmod/allnoconfig builds, and verifying selected objects in the build log.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mstar/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mstar/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/mstar/Makefile

Purpose: maps MStar clock Kconfig symbols to object files.

Important APIs/types: `obj-$(CONFIG_MSTAR_MSC313_CPUPLL)` builds `clk-msc313-cpupll.o`; `obj-$(CONFIG_MSTAR_MSC313_MPLL)` builds `clk-msc313-mpll.o`.

Control flow: Kbuild includes objects conditionally according to boolean Kconfig symbols.

State and persistence: build-system metadata only.

Dependencies and integration: paired with `drivers/clk/mstar/Kconfig` and included from the parent clock-driver build.

Risks: adding new MStar clock files requires both Kconfig and Makefile updates. Since drivers use builtin platform registration, object inclusion directly controls runtime availability.

Test signals: kernel build with each config enabled and disabled, and checking `drivers/clk/mstar/` object list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mstar/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mstar/clk-msc313-cpupll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mstar/clk-msc313-cpupll.c

Purpose: CPU PLL driver for MStar/SigmaStar MSC313-class SoCs, exposing a rate-changeable CPU PLL based on vendor-derived LPF registers.

Important APIs/functions: `msc313_cpupll_recalc_rate`, `msc313_cpupll_determine_rate`, and `msc313_cpupll_set_rate` implement CCF operations. `msc313_cpupll_reg_read32` and `_write32` combine/split 16-bit register pairs. `msc313_cpupll_setfreq` writes LPF transition registers and waits for lock.

Control flow: probe maps MMIO, seeds LPF low with current frequency, registers a single clock with parent index 0, and adds an OF simple provider. Set-rate converts desired frequency to the magic register divisor, writes the high target, configures transition controls, toggles LPF, polls lock, disables toggle, and stores the low value.

State and persistence: current PLL divisor is stored in hardware LPF/current registers; software holds only MMIO base and `clk_hw`.

Dependencies and integration: platform driver matching `mstar,msc313-cpupll`, CCF, OF provider, raw 16-bit MMIO, and boot parent clock from DT.

Risks: hardware is poorly documented; comments note low-frequency lockups. Poll timeout is 100 ms in a busy loop. `determine_rate` contains conservative rounding logic and a misspelled helper name but works locally.

Test signals: boot CPU frequency report, rate transition stress tests above 220 MHz, lock timeout logs, and comparing register values with vendor-known 400/600/800/1000 MHz examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mstar/clk-msc313-cpupll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mstar/clk-msc313-mpll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mstar/clk-msc313-mpll.c

Purpose: MStar MSC313 MPLL driver that reports one programmable MPLL rate and fixed-factor divided outputs.

Important APIs/functions: `msc313_mpll_recalc_rate` reads regmap fields for input, loop, and output divisors. `msc313_mpll_probe` sets up MMIO regmap, regmap fields, registers the MPLL clock, creates fixed-factor divider outputs, and publishes a onecell provider.

Control flow: probe maps resource, creates a 16-bit stride-4 regmap, allocates field handles, allocates `clk_hw_onecell_data`, registers the root MPLL, then registers output clocks named `<mpll>_div_N` for dividers 2,3,4,5,6,7,10.

State and persistence: root rate is hardware-backed by config registers; divider outputs are software fixed factors. Allocations are devm-managed.

Dependencies and integration: requires `REGMAP_MMIO`, CCF, platform driver matching `mstar,msc313-mpll`, and OF onecell consumers.

Risks: `clk_data` allocation uses `ARRAY_SIZE(output_dividers)` but `num` is `NUMOUTPUTS`, which is one larger, suggesting a possible under-allocation for `hws[0..NUMOUTPUTS-1]`. The output divider field value is used directly instead of mapped through `output_dividers`, so hardware encoding assumptions matter.

Test signals: KASAN boot for allocation bounds, rate readback tests, onecell indexes for all outputs, and compile testing with regmap-mmio.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mstar/clk-msc313-mpll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/mvebu/Kconfig

Purpose: defines build symbols for Marvell EBU/Armada clock controller support.

Important APIs/types: internal helper symbols include `MVEBU_CLK_COMMON`, `MVEBU_CLK_CPU`, `MVEBU_CLK_COREDIV`, and `ARMADA_AP_CP_HELPER`. SoC symbols select the helper subsets required by their clock files.

Control flow: Kconfig selection controls which early-init or platform clock drivers are compiled. Legacy Armada 370/XP/Dove/Kirkwood/Orion select common helpers; AP806/CP110 and AP CPU select AP/CP naming helpers.

State and persistence: build-time only.

Dependencies and integration: consumed by the mvebu Makefile and platform/`CLK_OF_DECLARE` code in the folder.

Risks: symbols are bool and mostly hidden, so top-level SoC config must select them correctly. Missing helper selection causes link failures or missing runtime providers.

Test signals: defconfig coverage for each Armada family, compile-test builds of individual symbols, and verifying dependent object inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/mvebu/Makefile

Purpose: Kbuild object mapping for MVEBU clock drivers.

Important APIs/types: maps helper symbols to `common.o`, `clk-cpu.o`, `clk-corediv.o`, and `armada_ap_cp_helper.o`, and maps SoC symbols to Armada 37xx, AP806, CP110, Dove, Kirkwood, Orion, and Armada XP/370/375/38x/39x objects.

Control flow: Kbuild includes object files based on boolean config symbols. Some SoCs build multiple files, such as Armada 37xx xtal/TBG/periph and Dove core/divider.

State and persistence: build metadata only.

Dependencies and integration: must match Kconfig symbols and source filenames in the same directory.

Risks: Armada XP also builds `mv98dx3236.o`; this implicit pairing can surprise maintainers. Adding new SoC files requires Kconfig and Makefile synchronization.

Test signals: object list review for defconfigs, compile tests for each symbol, and missing-object/link-error CI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/ap-cpu-clk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mvebu/ap-cpu-clk.c

Purpose: platform driver for Armada AP806/AP807 CPU cluster DFS clocks.

Important APIs/functions: `ap_cpu_clk_recalc_rate`, `ap_cpu_clk_determine_rate`, and `ap_cpu_clk_set_rate` implement per-cluster CCF operations. `ap_cpu_clock_probe` discovers active CPU clusters, creates cluster clocks, and registers a onecell provider. `ap806_dfs_regs` and `ap807_dfs_regs` encode SoC register layouts.

Control flow: probe obtains the parent syscon regmap, scans CPU nodes to determine whether cluster 1 exists, allocates clock data, creates one clock per cluster with a unique AP/CP name, and adds an OF provider. Set-rate writes divider fields, optionally writes AP807 secondary ratio, forces reload, requests ratio switch, polls stability, then clears the request bit.

State and persistence: cluster clock state is hardware divider/status registers; software stores cluster index, regmap, and layout descriptor.

Dependencies and integration: syscon parent node, CPU DT nodes, `ap_cp_unique_name`, CCF, regmap polling, and compatible data for `marvell,ap806-cpu-clock`/`ap807-cpu-clock`.

Risks: `recalc_rate` divides by the raw divider; invalid zero hardware state would fault. Cluster counting depends on CPU `reg` values and enabled nodes. Parent clocks are acquired by cluster index.

Test signals: cpufreq/DFS transitions, AP806 and AP807 boot, two-cluster and one-cluster DT variants, timeout handling, and `clk_summary` cluster names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/ap-cpu-clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/ap806-system-controller.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mvebu/ap806-system-controller.c

Purpose: AP806/AP807 system-controller clock provider for fixed root and derived AP clocks based on Sample At Reset frequency mode.

Important APIs/functions: `ap806_syscon_common_probe` reads the SAR register and registers six clocks. `ap806_get_sar_clocks` and `ap807_get_sar_clocks` decode frequency modes. Both legacy syscon and child clock platform drivers call the common probe.

Control flow: probe obtains the syscon regmap from either the node itself or its parent, decodes CPU and DDR clock MHz, registers fixed-rate cluster PLLs, a fixed 1.2 GHz clock, MSS and SDIO fixed-factor clocks, AP-DCLK, then publishes a onecell provider.

State and persistence: clocks are fixed after boot from SAR state. A static `ap806_clks` array backs the provider.

Dependencies and integration: CCF, regmap syscon, AP/CP unique names, platform drivers for legacy `marvell,ap806-system-controller` and modern `marvell,ap806-clock`/`ap807-clock`.

Risks: static clock storage means multiple instances would conflict. Error unwind labels unregister `ap806_clks[5]` with fixed-factor API even though AP-DCLK is fixed-rate. Unsupported SAR modes abort all provider registration.

Test signals: AP806/AP807 SAR mode matrix, legacy binding warnings, onecell clock indexes, and boot clock rate validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/ap806-system-controller.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-370.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-370.c

Purpose: Armada 370 early clock setup for SAR-derived core clocks and peripheral gate clocks.

Important APIs/functions: `a370_clk_init` calls `mvebu_coreclk_setup` and optionally `mvebu_clk_gating_setup`. Helpers decode TCLK, CPU frequency, CPU-to-NB/HCLK/DRAM ratios, and SSCG enable state.

Control flow: the core-clock descriptor reads SAR bits to register `tclk`, `cpuclk`, and fixed-factor `nbclk`, `hclk`, and `dramclk`. If a matching gating node exists, gate descriptors register clocks such as audio, PCIe, GE, SATA, SDIO, crypto, TDM, DDR.

State and persistence: clocks are fixed from boot SAR state; gate state is MMIO-backed and restored by common syscore code.

Dependencies and integration: MVEBU common helpers, `kirkwood_fix_sscg_deviation` for spread-spectrum correction, DT compatibles `marvell,armada-370-core-clock` and `marvell,armada-370-gating-clock`.

Risks: unsupported CPU frequency selector returns zero. Gate names and bit indexes are DT ABI-sensitive. Crypto and DDR use `CLK_IGNORE_UNUSED` to avoid unwanted disable.

Test signals: Armada 370 boot rate check, gating node discovery, SSCG-enabled system clock validation, and peripheral enable tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-370.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-375.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-375.c

Purpose: Armada 375 early clock setup for core clocks and clock-gating controller.

Important APIs/functions: `armada_375_coreclk_init` registers SAR-derived core clocks through `mvebu_coreclk_setup`. `armada_375_clk_gating_init` registers peripheral gates through `mvebu_clk_gating_setup`.

Control flow: CPU, DDR, and L2 frequencies are decoded from shared SAR1 bits; TCLK is decoded from a separate bit. Ratio tables map the selected mode to `l2clk` and `ddrclk`. The gating descriptor exposes MU, PP, PTP, PCIe, audio, NAND, SATA, USB, SDIO, GOP, XOR, crypto, and related gates.

State and persistence: fixed clocks reflect boot straps; gate state is in the gating register.

Dependencies and integration: MVEBU common helpers and DT compatibles `marvell,armada-375-core-clock` and `marvell,armada-375-gating-clock`.

Risks: sparse CPU frequency table returns zero for reserved modes without a separate zero check. Gate descriptors have three-field initializers relying on the fourth `flags` field being zero.

Test signals: SAR mode boot matrix, peripheral gate lookup by bit, SATA/USB/crypto functional tests, and `clk_summary` names from `clock-output-names`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-375.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-37xx-periph.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-37xx-periph.c

Purpose: Armada 37xx peripheral clock driver for northbridge/southbridge composite clocks, including mux/divider/gate combinations and a DVFS-aware CPU clock.

Important APIs/functions: `armada_3700_periph_clock_probe` registers all clocks described by match data. `armada_3700_add_composite_clk` adapts static mux/rate/gate templates to the mapped register base and calls `clk_hw_register_composite`. Custom ops include `clk_double_div_ops` and `clk_pm_cpu_ops`.

Control flow: match data selects NB or SB clock tables. Probe maps registers, initializes a lock, converts template register offsets to real MMIO addresses, handles special PM CPU mux/rate setup via the NB PM syscon, registers composites, and publishes a onecell provider. Suspend stores selector/divider/gate registers; resume writes them back in ATF-compatible order.

State and persistence: driver data stores hardware register snapshots for sleep. Runtime clock state is hardware-backed. `clk_pm_cpu` keeps an `l1_expiration` jiffies value for the high-frequency DVFS workaround.

Dependencies and integration: CCF composite clocks, syscon/regmap for NB PM, platform compatibles for NB/SB periph clocks, TBG parent clocks, and noirq system sleep PM.

Risks: `get_div` can return zero for invalid encodings, leading to division by zero in rate recalculation. Static template objects are mutated at probe, so multiple instances of the same data set would conflict. CPU DVFS set-rate returns `rate` instead of zero on success.

Test signals: NB and SB provider registration, all composite indexes, suspend/resume register restore, CPU DVFS level transitions including 20 ms L1 workaround, and invalid divider handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-37xx-periph.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-37xx-tbg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-37xx-tbg.c

Purpose: Armada 37xx Time Base Generator clock provider, exposing four fixed-factor TBG outputs.

Important APIs/functions: `armada_3700_tbg_clock_probe` registers `TBG-A-P`, `TBG-B-P`, `TBG-A-S`, and `TBG-B-S`. Helpers `tbg_get_mult` and `tbg_get_div` decode feedback, reference, and VCO divider fields.

Control flow: probe allocates onecell data for four clocks, gets the parent clock, maps registers, decodes each TBG multiplier/divider, registers fixed-factor clocks, and adds an OF provider. Remove unregisters provider and fixed factors.

State and persistence: TBG rates are derived from current hardware registers at probe and then represented as fixed-factor clocks.

Dependencies and integration: platform driver matching `marvell,armada-3700-tbg-clock`, parent XTAL clock, CCF fixed-factor registration, and periph clocks that consume TBG names.

Risks: TBG factors are not refreshed if firmware changes registers after probe. Error handling logs failed individual registrations but still publishes the provider. The error message for missing parent says "Could get" instead of "Couldn't get".

Test signals: XTAL/TBG clock tree in `clk_summary`, parent-rate variants at 25/40 MHz, remove path, and peripheral rate calculations downstream.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-37xx-tbg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-37xx-xtal.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-37xx-xtal.c

Purpose: Armada 37xx XTAL clock provider that chooses 25 MHz or 40 MHz from a latched strap bit.

Important APIs/functions: `armada_3700_xtal_clock_probe` reads `NB_GPIO1_LATCH` via parent syscon, registers a fixed-rate clock, and adds a simple OF provider. `armada_3700_xtal_clock_remove` deletes the provider.

Control flow: probe validates parent node, obtains regmap, reads latch bit `XTAL_MODE`, selects rate, optionally reads `clock-output-names`, registers fixed-rate `xtal`, and publishes it.

State and persistence: fixed rate is sampled once at probe from latch hardware; no software state beyond the `clk_hw` pointer is needed.

Dependencies and integration: syscon parent, platform driver matching `marvell,armada-3700-xtal-clock`, CCF fixed-rate provider, TBG parent linkage.

Risks: initial devm allocation of `clk_hw` is overwritten by `clk_hw_register_fixed_rate`, making the allocation unnecessary. Remove deletes provider but does not unregister the fixed-rate clock.

Test signals: strap variants for 25/40 MHz, TBG downstream rates, provider remove/reprobe checks, and DT `clock-output-names` handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-37xx-xtal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-38x.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-38x.c

Purpose: Armada 380/385 early clock setup for core SAR clocks and peripheral gates.

Important APIs/functions: `armada_38x_coreclk_init` registers `tclk`, `cpuclk`, `l2clk`, and `ddrclk`; `armada_38x_clk_gating_init` registers gate descriptors.

Control flow: SAR bits select TCLK and CPU frequency; ratio tables map CPU mode to L2 and DDR factors. Gate descriptors expose audio, Ethernet, PCIe, USB3/USB2, BM, crypto, SATA, SDIO, XOR, and TDM clocks.

State and persistence: boot strap values define fixed core rates; gate state is MMIO and saved/restored by common gating code.

Dependencies and integration: MVEBU common helpers and compatibles `marvell,armada-380-core-clock` and `marvell,armada-380-gating-clock`.

Risks: CPU frequency table contains reserved zero entries, so unsupported but in-range selectors produce zero rate silently. Gate bit names are ABI-visible to consumers.

Test signals: Armada 38x boot, TCLK 250/200 MHz strap variants, peripheral gate enable/disable, and static comparison to datasheet SAR encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-38x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-39x.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-39x.c

Purpose: Armada 39x early clock setup with SAR-derived core clocks, optional refclk, and peripheral gates.

Important APIs/functions: `armada_39x_coreclk_init` registers core clocks through `mvebu_coreclk_setup`; `armada_39x_clk_gating_init` registers gates. Helpers decode TCLK, CPU frequency, fixed ratios, and 25/40 MHz refclk.

Control flow: SARL selects CPU/TCLK modes and SARH selects reference clock. Core setup registers `tclk`, `cpuclk`, fixed-factor `nbclk`, `hclk`, `dclk`, and optional `refclk`. Gating registers PCIe, USB3, SATA, SDIO, and XOR gates.

State and persistence: fixed at boot from SAR registers; gates are hardware-backed.

Dependencies and integration: MVEBU common helpers and DT compatibles `marvell,armada-390-core-clock` and `marvell,armada-390-gating-clock`.

Risks: sparse CPU frequency table returns zero for unsupported in-range selectors. Ratios are hard-coded rather than mode-table derived, so future variants need care.

Test signals: refclk strap validation, core clock rate checks, PCIe/SATA/USB gate behavior, and SAR mode boot coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-39x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-xp.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-xp.c

Purpose: Armada XP early clock setup for SAR-derived core clocks and extensive peripheral gate clocks.

Important APIs/functions: `axp_clk_init` calls `mvebu_coreclk_setup` and optional `mvebu_clk_gating_setup`. Helpers decode split 64-bit SAR fields for CPU frequency and fabric ratios.

Control flow: TCLK is fixed at 250 MHz. CPU frequency selector combines low and high SAR bits; fabric ratio selector also combines non-contiguous bits. The common core helper registers `tclk`, `cpuclk`, `nbclk`, `hclk`, and `dramclk`; gating setup registers GE, PCIe lanes, SATA, LCD, SDIO, USB, XOR, crypto, TDM, and audio clocks.

State and persistence: core clocks are fixed after boot; gates are MMIO-backed.

Dependencies and integration: MVEBU common helper, DT compatibles `marvell,armada-xp-core-clock` and `marvell,armada-xp-gating-clock`, and CPU clock support from `clk-cpu.c` for per-CPU dividers.

Risks: some CPU frequency selectors map to zero. Non-contiguous SAR decoding is easy to regress. Gate hierarchy uses parent gate names for SATA links and ports.

Test signals: Armada XP boot on several strap modes, PCIe/SATA gate tests, CPU divisor provider interaction, and `clk_summary` comparison with board DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada-xp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada_ap_cp_helper.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada_ap_cp_helper.c

Purpose: helper for Armada AP/CP clock drivers to create unique clock names from syscon resource addresses.

Important APIs/functions: `ap_cp_unique_name` returns a devm-managed string formatted as `<resource-start>-<name>`.

Control flow: if `name` is NULL, returns NULL. Otherwise it converts the first address resource of `np` to `struct resource` and formats the start address plus requested base name.

State and persistence: returned strings are device-managed allocations owned by `dev`.

Dependencies and integration: used by AP806, AP CPU, and CP110 clock drivers to avoid duplicate names when multiple AP/CP instances exist.

Risks: return value of `of_address_to_resource` is ignored; malformed nodes may produce an uninitialized or stale resource. Names depend on physical address stability in DT.

Test signals: multiple CP110/AP instances producing distinct clock names, fault-injection for missing `reg`, and memory lifetime via devm teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada_ap_cp_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada_ap_cp_helper.h -->
# sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada_ap_cp_helper.h

Purpose: header declaring the AP/CP unique clock-name helper.

Important APIs/types: forward-declares `struct device` and `struct device_node`, and declares `ap_cp_unique_name`.

Control flow: no runtime flow.

State and persistence: no state in the header; the function returns devm-managed names from the C file.

Dependencies and integration: included by AP806/AP807, AP CPU, and CP110 system-controller clock drivers.

Risks: callers must include suitable kernel headers for allocation error handling and must tolerate NULL if the helper is passed NULL.

Test signals: build coverage of all helper users and duplicate-name checks when multiple syscon instances are described in DT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada_ap_cp_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/clk-corediv.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mvebu/clk-corediv.c

Purpose: MVEBU core-divider clock provider, currently focused on NAND/core divider clocks for Armada 370/375/380 and mv98dx3236.

Important APIs/functions: custom `clk_corediv_*` ops implement enable/disable/is_enabled, recalc, determine, and set_rate. `mvebu_corediv_clk_init` registers per-SoC divider clocks; `CLK_OF_DECLARE` wrappers bind specific compatibles.

Control flow: init maps the divider register block, allocates `clk_corediv` and clock arrays, reads parent name and output names, registers clocks with SoC-specific ops. Set-rate writes divider ratio, sets reload-force, triggers ratio reload, waits, then clears request bits.

State and persistence: each `clk_corediv` stores register base, descriptor, SoC descriptor, and lock. Hardware registers hold divider and enable state.

Dependencies and integration: CCF, OF early init, MMIO, udelay, and MVEBU SoC compatibles.

Risks: only `spin_lock_init(&corediv->lock)` initializes the first element if more descriptors are added. `recalc_rate` divides by raw divider without zero guard. Determine-rate clamps to 4,5,6,8 only.

Test signals: NAND clock rate set/get, enable bit behavior on SoCs with enable ops, zero-divider fault tests, and compatible-specific register offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/clk-corediv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/clk-cpu.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mvebu/clk-cpu.c

Purpose: Armada XP per-CPU clock provider with dynamic divider updates through clock-complex and PMU DFS registers.

Important APIs/functions: `clk_cpu_recalc_rate`, `clk_cpu_determine_rate`, `clk_cpu_set_rate`, `clk_cpu_off_set_rate`, and `clk_cpu_on_set_rate` implement CCF operations. `of_cpu_clk_setup` creates `cpuN` clocks. `of_mv98dx3236_cpu_clk_setup` supplies a simple provider for mv98dx3236.

Control flow: early setup maps clock-complex and optional PMU DFS registers, allocates per-CPU clock structs, registers one clock per possible CPU, and publishes a onecell provider. Rate changes while disabled update divider registers directly and trigger reload; while enabled they program PMU DFS ratios and call `mvebu_pmsu_dfs_request`.

State and persistence: CPU divider state is hardware-backed; software stores per-CPU register offsets, parent name, and optional PMU DFS address.

Dependencies and integration: CCF, OF early init, `num_possible_cpus`, Armada PMSU DFS API, and SMP CPU topology.

Risks: `recalc_rate` divides by raw divider with no zero guard. Dynamic scaling is unavailable without PMU DFS mapping. `clk_data.clk_num` is fixed to `MAX_CPU` even if fewer CPUs/clks were allocated, which can expose invalid entries.

Test signals: CPU clock lookup for all possible CPUs, cpufreq transitions on online/offline CPUs, missing PMU DFS warning path, and mv98dx3236 simple provider behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/clk-cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/common.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mvebu/common.c

Purpose: shared MVEBU clock infrastructure for SAR-derived core clocks, spread-spectrum correction, and common clock-gating controllers.

Important APIs/functions: `kirkwood_fix_sscg_deviation`, `mvebu_coreclk_setup`, and `mvebu_clk_gating_setup`. Internal gating helpers include `clk_gating_get_src` and syscore suspend/resume callbacks.

Control flow: core setup maps SAR registers, allocates a onecell table for TCLK, CPU clock, ratio clocks, and optional refclk, registers fixed-rate/fixed-factor clocks, unmaps SAR, and publishes provider. Gating setup maps the gate register, determines default parent from input clock, registers gates from a descriptor array, adds a custom provider that indexes by gate bit, and registers syscore save/restore.

State and persistence: core clock data is static onecell storage; gating control is a single global `ctrl` with saved register state for suspend. Gates are hardware-backed.

Dependencies and integration: OF, CCF, syscore ops, MMIO, and SoC descriptors from `common.h`.

Risks: only one gating controller can instantiate because `ctrl` is global. Several allocations are permanent early-init allocations. SSCG helper logs errors if the optional `sscg` node is missing and returns unadjusted clocks.

Test signals: core provider clock counts, gating provider bit-index lookup, suspend/resume restore of gate register, and SSCG-corrected CPU rate validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/common.h -->
# sources/distributed-fs/ceph-client/drivers/clk/mvebu/common.h

Purpose: shared MVEBU clock descriptor and helper declarations.

Important APIs/types: declares `ctrl_gating_lock`, `struct coreclk_ratio`, `struct coreclk_soc_desc`, `struct clk_gating_soc_desc`, `mvebu_coreclk_setup`, `mvebu_clk_gating_setup`, and `kirkwood_fix_sscg_deviation`.

Control flow: no runtime logic in the header; SoC files populate descriptors and pass them to common setup functions.

State and persistence: descriptors point to SoC-specific SAR decoding callbacks and static ratio/gate tables.

Dependencies and integration: included by all legacy MVEBU SoC clock files, core divider code, and common implementation.

Risks: callback contracts are informal; returning zero for unsupported SAR values is not centrally rejected. Gate descriptor arrays must be NULL-name terminated.

Test signals: compile coverage across all MVEBU SoC files and descriptor-array static checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/cp110-system-controller.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mvebu/cp110-system-controller.c

Purpose: CP110 system-controller clock provider for core clocks and 32 possible gateable peripheral clocks.

Important APIs/functions: `cp110_syscon_common_probe` registers core and gate clocks. `cp110_register_gate`, `cp110_gate_enable`, `cp110_gate_disable`, and `cp110_gate_is_enabled` implement custom regmap-backed gates. `cp110_of_clk_get` decodes two-cell clock specifiers.

Control flow: probe gets the syscon regmap, reads NAND clock selection, allocates onecell data, registers PLL0 and derived PPv2/x2core/core/NAND/SDIO clocks, creates unique gate names, chooses each gate parent, registers gates, and publishes a custom provider. Legacy and modern platform drivers call the same common probe.

State and persistence: fixed-factor core clocks are static after probe; gates are controlled by `CP110_PM_CLOCK_GATING_REG`. Platform data stores clock HW pointers for cleanup.

Dependencies and integration: syscon parent, AP/CP unique naming helper, CCF, regmap, two-cell DT binding with clock type and index.

Risks: PCIe gates use `CLK_IGNORE_UNUSED` to avoid breaking active links, so unused-clock cleanup will not disable them. `gate_base_names` has sparse NULL entries; indexing must stay aligned with binding bits. Manual cleanup paths are complex.

Test signals: legacy and modern binding probe, two-cell clock lookup for core/gate types, NAND 400/core selection, PCIe active-link boot, and gate enable register tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/cp110-system-controller.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/dove-divider.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mvebu/dove-divider.c

Purpose: Dove PMU core PLL divider provider for AXI, GPU, VMeta, and LCD clocks.

Important APIs/functions: `dove_divider_clk_init` maps registers, calls `dove_divider_init`, and publishes a onecell provider. Custom divider ops are `dove_recalc_rate`, `dove_determine_rate`, and `dove_set_clock`.

Control flow: init registers a fixed 2 GHz `core-pll`, then registers four custom divider clocks. Set-rate computes a divider or table encoding, builds mask/load bits, and calls `dove_load_divider`, which deasserts reset, writes divider value, pulses load, delays 250 ns, and clears load.

State and persistence: divider settings live in PMU `DIV_CTRL0/1`; static `dove_hw_clocks` carries per-clock bit fields and lock pointer.

Dependencies and integration: called from `dove.c`, CCF, MMIO, spinlock, and Dove DT divider node.

Risks: `axi_divider` starts with `(u32)-1` as a sentinel-like table entry, which can surprise rate calculations. Fixed 2 GHz core PLL is an assumption due to sparse documentation. No unregister path for early init.

Test signals: Dove boot `clk_summary`, AXI/GPU/VMeta/LCD rate changes, register load pulse timing, and divider table edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/dove-divider.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/dove-divider.h -->
# sources/distributed-fs/ceph-client/drivers/clk/mvebu/dove-divider.h

Purpose: header for Dove divider clock initialization.

Important APIs/types: declares `dove_divider_clk_init(struct device_node *np)`.

Control flow: no runtime flow in the header.

State and persistence: no header-local state; the C file registers static divider clocks.

Dependencies and integration: included by `dove.c` and implemented by `dove-divider.c`.

Risks: relies on other includes for `struct device_node` and `__init` visibility.

Test signals: build coverage of Dove clock support and link resolution for `dove_divider_clk_init`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/dove-divider.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/dove.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mvebu/dove.c

Purpose: Dove early clock setup for SAR-derived core clocks, optional PMU dividers, and peripheral gate clocks.

Important APIs/functions: `dove_clk_init` calls `mvebu_coreclk_setup`, optional `dove_divider_clk_init`, and optional `mvebu_clk_gating_setup`. Helpers decode TCLK, CPU frequency, and CPU-to-L2/DDR ratios from SAR bits.

Control flow: core setup registers `tclk`, `cpuclk`, `l2clk`, and `ddrclk`. The init function searches globally for compatible divider and gating nodes, initializes them if present, and drops node refs. Gate descriptors expose USB, GE/GE PHY, SATA, PCIe, SDIO, NAND, camera, I2S, crypto, AC97, PDMA, and XOR gates.

State and persistence: core rates are fixed from boot straps; divider and gate state are MMIO-backed and managed by their helper providers.

Dependencies and integration: MVEBU common helpers, Dove divider helper, and DT compatibles `marvell,dove-core-clock`, `marvell,dove-divider-clock`, and `marvell,dove-gating-clock`.

Risks: unsupported SAR encodings map to zero rates without central rejection. Global compatible-node search can initialize the first matching node rather than a strict child relation. Divider provider assumes a fixed core PLL rate.

Test signals: Dove board boot, SAR mode rate checks, divider output rates, GE/SATA/USB gate tests, and DT topology tests with multiple compatible nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mvebu/dove.c -->
