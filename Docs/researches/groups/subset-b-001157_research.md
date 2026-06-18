# Research: subset-b-001157

This grouped report covers 17 clock-driver source files in `sources/distributed-fs/ceph-client/drivers/clk/renesas` and `sources/distributed-fs/ceph-client/drivers/clk/rockchip`. Each file section is bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-usb2-clock-sel.c -->
## sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-usb2-clock-sel.c

### Purpose
Implements the R-Car Gen3 USB2.0 clock selector as a small common-clock provider. Although the hardware resembles a mux between `usb_extal` and `usb_xtal`, the driver exposes a gate-like clock named `rcar_usb2_clock_sel` because the EHCI/OHCI platform drivers do not switch parents. It coordinates USB module resets, the required bus/interface clocks, runtime PM, and the `USB20_CLKSET0` register bits needed for extal-only operation.

### Important APIs, Types, and Functions
`struct usb2_clock_sel_priv` stores the MMIO base, registered `clk_hw`, two bulk clocks (`ehci_ohci` and `hs-usb-if`), a shared reset-control array, and booleans indicating whether `usb_extal` and `usb_xtal` are present and have rates. `usb2_clock_sel_enable()` deasserts resets, enables the bulk clocks, then programs extal-only mode if needed. `usb2_clock_sel_disable()` reverses that sequence. `rcar_usb2_clock_sel_probe()` maps the resource, acquires clocks and resets, probes optional input oscillator rates, enables runtime PM, registers the clock, and publishes it through `of_clk_add_hw_provider()`.

### Control Flow, State, and Persistence
Probe initializes persistent device state in devm-managed storage and stores it as driver data. Enable state is controlled by CCF callbacks and not stored beyond hardware register state. If `usb_extal` exists and `usb_xtal` does not, `usb2_clock_sel_enable_extal_only()` writes `CLKSET0_EXTAL_ONLY`; suspend clears this to `CLKSET0_PRIVATE`, and resume reapplies it after a runtime-PM get. Error handling in enable asserts resets again if bulk clock enable fails.

### Dependencies and Integration Points
The driver depends on the platform device resource, reset controller API, runtime PM, CCF, DT compatible `renesas,rcar-gen3-usb2-clock-sel`, and clocks named `ehci_ohci`, `hs-usb-if`, `usb_extal`, and `usb_xtal`. Consumers obtain the single provided clock from the node. It is built in through `builtin_platform_driver()`.

### Risks and Test Signals
The important runtime risks are missing oscillator definitions, incorrect reset sharing, and CLKSET0 writes racing with USB controller use during suspend/resume. Good test signals are successful probe with exactly one oscillator present, EHCI/OHCI operation across enable/disable, suspend/resume with extal-only boards, and failure injection for bulk-clock enable to verify reset reassertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rcar-usb2-clock-sel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/renesas-cpg-mssr.c -->
## sources/distributed-fs/ceph-client/drivers/clk/renesas/renesas-cpg-mssr.c

### Purpose
Provides the common Renesas CPG/MSSR backend for R-Car, RZ/G1, RZ/A, R-Car Gen4, and RZ/T2H-style SoCs. It registers core clocks, module-stop gates, reset controllers, and an always-on PM domain that automatically attaches module clocks to device runtime PM. It also handles early clock registration, reserved devices, critical clocks, and system suspend/resume save-restore for module-stop state.

### Important APIs, Types, and Functions
`struct cpg_mssr_priv` extends the public `cpg_mssr_pub` data with reset controller state, register-layout selection, arrays of clock pointers, register offset tables, saved SMSTPCR values, and reserved-module IDs. `struct mstp_clock` is the CCF hardware wrapper for module-stop gates. `cpg_mssr_register_core_clk()` handles generic inputs, fixed factors, fixed rates, DIV6 clocks, and SoC-specific custom clocks through `info->cpg_clk_register()`. `cpg_mssr_register_mod_clk()` registers module gates and marks critical or reserved clocks with `CLK_IS_CRITICAL` or `CLK_IGNORE_UNUSED`. `cpg_mssr_clk_src_twocell_get()` implements the DT two-cell clock provider. Reset APIs are split between SRCR/SRSTCLR style (`cpg_mssr_reset_ops`) and RZ/T2H MRCR style (`cpg_mrcr_reset_ops`).

### Control Flow, State, and Persistence
Initialization flows through `cpg_mssr_common_init()`, which maps one or two MMIO bases, selects register arrays for the configured layout, allocates the clock array, scans `/soc` reserved children for CPG_MOD clocks, and registers the OF clock provider. `cpg_mssr_early_init()` registers early clocks before the platform driver probe, while `cpg_mssr_probe()` completes the core and module clock registration, adds the PM domain, and registers resets when supported. Module gate enable/disable updates the relevant stop-control bit under `rmw_lock`, then polls status registers on layouts that provide them. Suspend stores module stop registers under the driver mask and calls DIV6/core notifiers; resume restores core clocks, writes module stop bits back, and polls enabled modules.

### Dependencies and Integration Points
This file integrates with CCF, reset-controller, generic PM domains, `pm_clk`, PSCI-aware suspend, OF clock providers, and per-SoC `cpg_mssr_info` tables compiled under SoC Kconfig symbols. It depends on `dt-bindings/clock/renesas-cpg-mssr.h`, local `clk-div6`, and layout-specific offset tables. Reserved-device handling uses OF reserved child nodes to keep clocks assigned to non-Linux firmware from being disabled by `clk_disable_unused()`.

### Risks and Test Signals
Register layout mismatches can write the wrong stop or reset registers. RZ/T2H is especially sensitive because MSTPCR access can target two MMIO blocks and requires read-back plus delay. The global `cpg_mssr_priv` supports the early-init path but assumes one active CPG/MSSR instance. Test signals include DT clock lookup for core and module clocks, module gate polling, reset assert/deassert/status, reserved node preservation, critical clock behavior during `clk_disable_unused`, and suspend/resume under PSCI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/renesas-cpg-mssr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/renesas-cpg-mssr.h -->
## sources/distributed-fs/ceph-client/drivers/clk/renesas/renesas-cpg-mssr.h

### Purpose
Defines the common data model used by Renesas CPG/MSSR SoC clock-description files and the common backend. It captures core clock descriptors, module clock descriptors, register-layout variants, public runtime state shared with custom clock registration, and the top-level `cpg_mssr_info` contract consumed by `renesas-cpg-mssr.c`.

### Important APIs, Types, and Functions
`struct cpg_core_clk` describes input, fixed-factor, DIV6, fixed-rate, and custom core clocks with parent IDs, factors, offsets, divider tables, parent names, and mux metadata. `struct cpg_mssr_pub` exposes MMIO bases, notifier chain, RMW spinlock, and clock pointer array to SoC-specific custom registration code. `struct mssr_mod_clk` describes module clocks using packed `MOD_CLK_BASE` IDs. `enum clk_reg_layout` distinguishes Gen2/Gen3, RZ/A, Gen4, and RZ/T2H register maps. `struct cpg_mssr_info` is the central SoC descriptor with early clocks, normal clocks, module clocks, critical module IDs, PM-capable core clock IDs, and optional callbacks.

### Control Flow, State, and Persistence
The header itself stores no runtime state. Its macros such as `DEF_INPUT`, `DEF_FIXED`, `DEF_DIV6P1`, `DEF_MOD`, and `DEF_MOD_STB` create static descriptor arrays in SoC files. Packing macros translate sparse hardware numbering into dense array indexes used by the common backend and DT provider.

### Dependencies and Integration Points
The interface depends on the Linux notifier type and CCF divider-table declarations. It exports many external `cpg_mssr_info` symbols that are selected by compatible strings in the common driver. It also declares `cpg_mssr_early_init()` for early boot integration and `mssr_mod_nullify()` for SoC-revision-specific table fixups.

### Risks and Test Signals
The highest risk is descriptor/index mismatch: an incorrect `last_dt_core_clk`, `num_total_core_clks`, packed module ID, or register layout causes bad lookup or wrong register access in the backend. Test signals are compile coverage for all SoC descriptor tables, DT clock lookup by two-cell specifier, and boot logs showing no unsupported clock types or invalid indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/renesas-cpg-mssr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rzg2l-cpg.c -->
## sources/distributed-fs/ceph-client/drivers/clk/renesas/rzg2l-cpg.c

### Purpose
Implements the common CPG backend for Renesas RZ/G2L-family and related RZ/G3S SoCs. It registers core PLL, divider, mux, SD-mux, DSI/PLL5, and module clocks; handles module MSTOP control; exposes resets; and creates an always-on PM domain that attaches eligible module clocks to device PM.

### Important APIs, Types, and Functions
`struct rzg2l_cpg_priv` stores MMIO base, lock, clock array, reset controller, SoC info, PM domain, and cached PLL5/DSI divider choices. `rzg2l_cpg_register_core_clk()` dispatches descriptor types to fixed-factor, SAM PLL, G3S PLL, SIPLL5, standard divider, G3S dynamic divider, mux, SD mux, PLL5_4 mux, and DSI divider registration paths. `rzg2l_cpg_sd_clk_mux_notifier()` safely switches SD muxes through a 266 MHz intermediate parent before 533/400 MHz transitions. `rzg3s_cpg_div_clk_notifier()` avoids invalid divider/parent combinations before rate changes. Module clocks are represented by `struct mod_clock` and optional shared `struct mstop` counters.

### Control Flow, State, and Persistence
Probe maps the register block, allocates the clock array, registers all core and module clocks, initializes MSTOP state after all modules are visible, installs the OF provider, adds the PM domain, registers resets, deasserts critical resets, and exposes debugfs `mstop`. Core dynamic divider and SD mux updates write hiword-style fields under `rmw_lock` and poll status bits. SIPLL5/DSI rate changes compute PLL5 parameters, program PLL standby and clock registers, wait for lock, and program DSI divider fields. Module enable/disable sequences update CLK_ON and MSTOP state in a lock; coupled clocks share a soft `enabled` state so one hardware bit is not disabled while its sibling is still active.

### Dependencies and Integration Points
The driver integrates with CCF, OF two-cell clock providers, reset-controller, generic PM domains, `pm_clk`, debugfs, and SoC descriptor tables from `rzg2l-cpg.h`. It exports `rzg2l_cpg_dsi_div_set_divider()` for DSI users to communicate required divider and target mode. Compatible strings select R9A07G043, R9A07G044, R9A07G054, R9A08G045, R9A08G046, and R9A09G011 descriptor data.

### Risks and Test Signals
Key risks are static global DSI divider state shared across instances, PLL5 parameter search failures for unsupported pixel clocks, incorrect MSTOP sharing counts, and monitor polling timeouts. Test signals include rate-change tests for SDHI and G3S constrained dividers, DSI pixel-clock negotiation, debugfs MSTOP state consistency, coupled-clock enable/disable behavior, reset monitor polling, and suspend/resume re-enabling critical clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rzg2l-cpg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rzg2l-cpg.h -->
## sources/distributed-fs/ceph-client/drivers/clk/renesas/rzg2l-cpg.h

### Purpose
Defines RZ/G2L-family CPG descriptor formats and register encoding helpers. SoC-specific clock tables use this header to describe PLLs, dynamic dividers, muxes, SD muxes, DSI clocks, module gates, MSTOP associations, resets, critical resources, and PM exclusions.

### Important APIs, Types, and Functions
`struct cpg_core_clk` is the core descriptor with type, parent, factors, packed register configuration, optional status configuration, divider/mux tables, rate limits, and notifier hooks. `enum clk_types` includes `CLK_TYPE_SAM_PLL`, `CLK_TYPE_G3S_PLL`, `CLK_TYPE_DIV`, `CLK_TYPE_G3S_DIV`, `CLK_TYPE_MUX`, `CLK_TYPE_SD_MUX`, `CLK_TYPE_SIPLL5`, `CLK_TYPE_PLL5_4_MUX`, and `CLK_TYPE_DSI_DIV`. `struct rzg2l_mod_clk` carries module ID, parent, CLK_ON offset/bit, MSTOP configuration, and coupled-clock flag. `struct rzg2l_reset` maps reset bits to optional monitor bits. `struct rzg2l_cpg_info` is the full SoC contract.

### Control Flow, State, and Persistence
The header does not execute code. Its macros pack offsets, shifts, widths, and status bits into compact constants consumed by `rzg2l-cpg.c`. `DEF_MOD` and `DEF_COUPLED` generate module descriptors, while `DEF_RST` and `DEF_RST_MON` generate sparse reset arrays.

### Dependencies and Integration Points
The file depends on notifier declarations and CCF divider tables. It declares external SoC information symbols and notifier functions used from SoC-specific tables. It also defines register constants for PLL5, divider, selector, clock-status, reset monitor, and MSTOP blocks.

### Risks and Test Signals
Descriptor packing is compact but brittle: wrong shift/width/status encodings can make the backend poll or update the wrong bits. Coupled-clock and MSTOP descriptors must match hardware sharing. Test signals are compile-time table coverage, boot-time registration without invalid IDs, SDHI and DSI clock rate changes, reset assertions with monitor bits, and PM-domain filtering for `no_pm_mod_clks`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rzg2l-cpg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rzv2h-cpg.c -->
## sources/distributed-fs/ceph-client/drivers/clk/renesas/rzv2h-cpg.c

### Purpose
Implements the Renesas RZ/V2H(P) and related RZ/G3E CPG backend. It registers PLLs, PLLDSI clocks, PLLDSI dividers, dynamic dividers, static muxes, fixed-factor clocks with module-status reporting, module clocks with MSTOP reference tracking, reset controls, and an always-on PM domain.

### Important APIs, Types, and Functions
`struct rzv2h_cpg_priv` stores MMIO base, lock, clock array, copied reset descriptors, MSTOP counters, reset controller, fixed-factor status ops, and two PLLDSI calculation caches. `rzv2h_get_pll_pars()` and `rzv2h_get_pll_divs_pars()` are exported in namespace `RZV2H_CPG` and search PLL M/K/P/S and divider combinations using millihertz precision. `rzv2h_cpg_register_core_clk()` dispatches input, fixed-factor, fixed-factor-with-status, PLL, DDIV, SMUX, PLLDSI, and PLLDSI divider types. Module clocks use `struct mod_clock`, `rzv2h_mod_clock_endisable()`, and MSTOP helpers to coordinate ON bits, monitor bits, optional external parent muxes, and reference counts.

### Control Flow, State, and Persistence
Probe maps MMIO, allocates clocks and MSTOP counters, copies reset descriptors, registers core clocks then module clocks, installs the clock provider, adds PM domains, and registers resets. PLLDSI rate determination may be driven by the divider first; the selected PLL and divider parameters are cached in `priv->pll_dsi_info[instance]` and consumed by later set-rate callbacks. DDIV updates wait for idle monitor bits before and after writing. Module enable writes CLK_ON, updates MSTOP counts, then polls monitor bits when available; disable decrements MSTOP counts and writes the off state. Reset assert/deassert writes reset bits and polls reset-monitor registers.

### Dependencies and Integration Points
The driver integrates with CCF, reset-controller, generic PM domains, `pm_clk`, OF two-cell providers, and SoC data selected by compatible strings for R9A09G047, R9A09G056, and R9A09G057. It uses descriptor structures from `rzv2h-cpg.h` and CPG/MSSR DT binding constants. External users may call the exported PLL search helpers from the `RZV2H_CPG` namespace.

### Risks and Test Signals
Risks include expensive or incomplete PLL parameter searches, cached PLLDSI state shared by clock instances in the same CPG, the intentional pointer adjustment `priv->mstop_count -= 16`, and module status behavior when an external parent mux bypasses a monitor bit. Test signals include PLLDSI requested-rate round trips, DDIV monitor timeout handling, fixed-factor status reads, MSTOP reference count balance for shared bits, reset xlate from packed DT IDs, and PM-domain exclusion of `no_pm` module clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rzv2h-cpg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rzv2h-cpg.h -->
## sources/distributed-fs/ceph-client/drivers/clk/renesas/rzv2h-cpg.h

### Purpose
Defines packed descriptors and SoC-info contracts for the RZ/V2H-family CPG backend. It captures PLL, dynamic divider, static mux, fixed module-status, module-clock, MSTOP, and reset metadata used by `rzv2h-cpg.c`.

### Important APIs, Types, and Functions
`struct pll` packs PLL register offset, `has_clkn`, instance number, and optional limits pointer. `struct ddiv` packs dynamic-divider register offset, shift, width, monitor bit, and no-RMW flag. `struct smuxed` and `struct fixed_mod_conf` describe static muxes and fixed-factor clocks that can report module status. `struct cpg_core_clk` uses a union of these descriptor types. `struct rzv2h_mod_clk` records parent, critical/no-PM flags, ON and monitor indexes, MSTOP data, and optional external-clock mux index. `struct rzv2h_cpg_info` collects core clocks, module clocks, resets, and MSTOP capacity.

### Control Flow, State, and Persistence
The header is declarative. Macros such as `DEF_PLL`, `DEF_DDIV`, `DEF_SMUX`, `DEF_PLLDSI`, `DEF_MOD`, `DEF_MOD_CRITICAL`, `DEF_MOD_NO_PM`, and `DEF_RST` build static SoC tables. `BUS_MSTOP()` packs a register index and bit mask into one value consumed by MSTOP reference-counting code.

### Dependencies and Integration Points
It depends on bitfield and integer types, and on PLL limit/parameter structures declared elsewhere in the Renesas clock subsystem. External `rzv2h_cpg_info` symbols are consumed by OF match entries in the implementation file.

### Risks and Test Signals
The descriptor model relies on dense module IDs computed from ON register indexes and bits; wrong `num_hw_mod_clks`, ON indexes, or MSTOP bits can corrupt clock lookup or MSTOP accounting. Test signals include validating all exported DT clock IDs, checking static mux/divider writes, reset xlate coverage, critical clock behavior, and PM-domain filtering for `DEF_MOD_NO_PM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/renesas/rzv2h-cpg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/clk/rockchip/Kconfig

### Purpose
Declares Rockchip common clock controller configuration symbols. `COMMON_CLK_ROCKCHIP` enables shared Rockchip clock infrastructure when `ARCH_ROCKCHIP` is selected. Inside that block, per-SoC booleans select individual CRU drivers for PX30, RV110x/RV1126 variants, and RK30xx/RK35xx/RK3588 families.

### Important APIs, Types, and Functions
This is Kconfig metadata rather than C code. The symbols are `CLK_PX30`, `CLK_RV1103B`, `CLK_RV110X`, `CLK_RV1126`, `CLK_RV1126B`, `CLK_RK3036`, `CLK_RK312X`, `CLK_RK3188`, `CLK_RK322X`, `CLK_RK3288`, `CLK_RK3308`, `CLK_RK3328`, `CLK_RK3368`, `CLK_RK3399`, `CLK_RK3506`, `CLK_RK3528`, `CLK_RK3562`, `CLK_RK3568`, `CLK_RK3576`, and `CLK_RK3588`.

### Control Flow, State, and Persistence
No runtime state exists. The configuration controls which object files are built and which compatible strings can probe at runtime. Most SoC options default to `y` under the common Rockchip clock option and constrain architecture to ARM, ARM64, or `COMPILE_TEST`.

### Dependencies and Integration Points
The file integrates with the kernel Kconfig system and the local `Makefile`. It gates SoC-specific C files and reset companion files where applicable.

### Risks and Test Signals
The primary risk is enabling an SoC file on an unsupported architecture or forgetting to add a new SoC symbol to the Makefile. Test signals are `allyesconfig`, `COMPILE_TEST`, and per-architecture build coverage confirming expected objects are linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/Makefile -->
## sources/distributed-fs/ceph-client/drivers/clk/rockchip/Makefile

### Purpose
Defines how Rockchip clock controller objects are linked. It builds a common `clk-rockchip.o` aggregate from shared helper files and adds SoC-specific CRU/reset objects according to Kconfig symbols.

### Important APIs, Types, and Functions
The aggregate `clk-rockchip-y` includes `clk.o`, `clk-pll.o`, `clk-cpu.o`, `clk-gate-grf.o`, `clk-half-divider.o`, `clk-inverter.o`, `clk-mmc-phase.o`, `clk-muxgrf.o`, `clk-ddr.o`, `gate-link.o`, and optionally `softrst.o` under `CONFIG_RESET_CONTROLLER`.

### Control Flow, State, and Persistence
No runtime control flow exists. Build selection controls whether shared helper functions are available and which platform driver objects are linked.

### Dependencies and Integration Points
The Makefile depends on the Kconfig symbols in the same directory. Several newer SoCs build reset companion files, such as `rst-rv1126b.o`, `rst-rk3506.o`, `rst-rk3528.o`, `rst-rk3562.o`, `rst-rk3576.o`, and `rst-rk3588.o`.

### Risks and Test Signals
The main risks are missing a helper from the common aggregate or mismatching a Kconfig symbol and object name. Test signals are incremental builds for each `CONFIG_CLK_*` symbol and link checks for helper symbols referenced by SoC files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-cpu.c -->
## sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-cpu.c

### Purpose
Implements Rockchip CPU clock helpers that coordinate CPU-domain muxes, dividers, and parent PLL rate changes. The standard CPU clock path temporarily switches to an alternate safe parent while the primary PLL changes, then restores dividers and muxes. A multi-PLL variant registers a composite mux/divider clock and adjusts dividers around rate changes.

### Important APIs, Types, and Functions
`struct rockchip_cpuclk` stores the CCF hardware, alternate parent, register base, notifier, rate table, register layout data, and shared lock. `rockchip_clk_register_cpuclk()` registers the classic CPU clock and a notifier on the main parent. `rockchip_cpuclk_pre_rate_change()` validates the new rate, limits alternate-parent speed by applying temporary core dividers if needed, applies pre-mux settings, and selects the alternate parent. `rockchip_cpuclk_post_rate_change()` returns to the main parent, applies post-mux settings, removes temporary dividers, and programs final dividers in the correct order for up/down transitions. `rockchip_clk_register_cpuclk_multi_pll()` builds a composite mux/divider and attaches a simpler notifier.

### Control Flow, State, and Persistence
The persistent state is the allocated CPU clock object and a copied rate table. The notifier is called by CCF when the parent clock changes. Standard pre-rate flow moves the CPU domain to the alternate parent before the PLL changes; post-rate flow moves back and finalizes dividers. The multi-PLL flow only adjusts dividers before increasing and after decreasing.

### Dependencies and Integration Points
The helper depends on Rockchip `struct rockchip_cpuclk_reg_data` and rate-table definitions from `clk.h`, CCF notifier APIs, MMIO register writes, and the shared CRU lock supplied by SoC drivers. It uses `HIWORD_UPDATE()` for masked register writes.

### Risks and Test Signals
Risks include rate-table gaps, missing alternate parent lookup, incorrect divider ordering causing transient CPU overclock, and no cleanup path for successful registrations. Test signals are cpufreq transitions across all OPPs, parent PLL set-rate failures, boot with alternate parent enabled, and checking that old-rate to new-rate transitions do not exceed documented CPU-domain limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-ddr.c -->
## sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-ddr.c

### Purpose
Registers Rockchip DDR clocks whose rate control is delegated to firmware through ARM SMCCC SIP calls. The CCF clock exposes set, recalc, determine-rate, and get-parent operations while firmware owns DRAM frequency programming.

### Important APIs, Types, and Functions
`struct rockchip_ddrclk` stores the CCF hardware, CRU base, mux/divider field positions, DDR clock type flag, and lock. `rockchip_ddrclk_sip_set_rate()` calls `ROCKCHIP_SIP_DRAM_FREQ` with `ROCKCHIP_SIP_CONFIG_DRAM_SET_RATE`. `rockchip_ddrclk_sip_recalc_rate()` asks firmware for the active rate. `rockchip_ddrclk_sip_determine_rate()` asks firmware to round the requested rate. `rockchip_clk_register_ddrclk()` creates the clock and selects SIP ops for `ROCKCHIP_DDRCLK_SIP`.

### Control Flow, State, and Persistence
After registration, persistent state is the allocated `rockchip_ddrclk`. Rate changes are serialized by the supplied spinlock around the SMC set-rate call. Parent selection is read directly from the mux register, but rate programming itself is not reflected in local registers by this driver.

### Dependencies and Integration Points
The file depends on ARM SMCCC, Rockchip SIP firmware IDs, CCF, MMIO reads, and SoC tables that specify mux/divider positions. It exports `rockchip_clk_register_ddrclk()` for SoC CRU drivers.

### Risks and Test Signals
Risks are firmware absence or incompatible SIP ABI, SMC return errors, and stale parent/mux data if firmware changes hardware behind Linux. Test signals include firmware round-rate responses, successful DRAM frequency transitions under memory stress, get-parent accuracy, and rejection of unsupported `ddr_flag` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-ddr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-gate-grf.c -->
## sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-gate-grf.c

### Purpose
Implements Rockchip gate clocks controlled through GRF regmap bits instead of the main CRU gate registers. It supports normal and inverted gate polarity plus optional hiword-mask writes.

### Important APIs, Types, and Functions
`struct rockchip_gate_grf` holds the CCF hardware, GRF regmap, register offset, bit shift, and gate flags. `rockchip_gate_grf_enable()` and `rockchip_gate_grf_disable()` compute the correct data and hiword mask and use `regmap_update_bits()`. `rockchip_gate_grf_is_enabled()` uses `regmap_test_bits()` and applies `CLK_GATE_SET_TO_DISABLE` inversion. `rockchip_clk_register_gate_grf()` validates the regmap and registers the clock.

### Control Flow, State, and Persistence
The only persistent state is the allocated gate object. Hardware state lives in the GRF register bit. Enable/disable are direct regmap updates without extra polling.

### Dependencies and Integration Points
This helper depends on CCF, regmap, and Rockchip SoC descriptions that identify GRF-controlled gate bits. It is part of the common `clk-rockchip.o` aggregate.

### Risks and Test Signals
Risks include invalid GRF regmap, incorrect polarity flags, and silent disable failure because the disable callback cannot return regmap errors. Test signals are enable/disable/is_enabled cycles for GRF-gated clocks, hiword-mask writes on hardware that requires them, and probe behavior when the GRF regmap is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-gate-grf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-half-divider.c -->
## sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-half-divider.c

### Purpose
Provides a Rockchip composite clock helper for divider formulas of `rate = parent * 2 / (2 * val + 3)`, optionally combined with mux and gate components. This supports hardware branches whose divisors are half-step encoded rather than standard integer dividers.

### Important APIs, Types, and Functions
`clk_half_divider_recalc_rate()` reads the divider field and applies the half-divider formula. `clk_half_divider_bestdiv()` searches for the best divider, optionally asking the parent to round rates when `CLK_SET_RATE_PARENT` is set. `clk_half_divider_determine_rate()` updates the requested rate and parent rate. `clk_half_divider_set_rate()` writes the field using either hiword-mask or read-modify-write semantics. `rockchip_clk_register_halfdiv()` constructs a composite mux/divider/gate clock.

### Control Flow, State, and Persistence
Persistent state is allocated CCF mux, divider, and gate objects owned by the registered composite clock. Runtime state is the hardware mux/divider/gate register fields. The set-rate path locks the supplied spinlock if present.

### Dependencies and Integration Points
The helper depends on CCF composite clock APIs, MMIO access, `HIWORD_UPDATE()`, and SoC branch tables that pass register offsets and flags. It can include any subset of mux, half-divider, and gate components.

### Risks and Test Signals
Risks include overflow in rate search, invalid width values, non-monotonic parent rounding choices, and leaks if a later allocation fails after an earlier component is allocated. Test signals include round-rate/set-rate/recalc consistency, behavior with and without parent rate propagation, hiword and RMW writes, and gate-only or mux-only branch registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-half-divider.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-inverter.c -->
## sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-inverter.c

### Purpose
Implements a simple Rockchip phase inverter clock. It exposes CCF phase operations for clocks whose hardware phase is either 0 or 180 degrees.

### Important APIs, Types, and Functions
`struct rockchip_inv_clock` stores the CCF hardware, register pointer, bit shift, flags, and lock. `rockchip_inv_get_phase()` reads the bit and returns 0 or 180. `rockchip_inv_set_phase()` accepts degrees divisible by 180, maps them to a single bit, and writes either with `HIWORD_UPDATE()` or an RMW sequence under lock. `rockchip_clk_register_inverter()` registers the clock.

### Control Flow, State, and Persistence
Hardware phase is the single inverter register bit. The driver keeps no cached phase. `CLK_SET_RATE_PARENT` is set so rate operations can propagate through this phase-only node.

### Dependencies and Integration Points
The helper depends on CCF phase APIs, MMIO access, and Rockchip branch descriptors that pass `ROCKCHIP_INVERTER_HIWORD_MASK` when applicable.

### Risks and Test Signals
Risks include accepting degrees like 360 and mapping them to enabled inversion because `!!degrees` is used after modulo validation, incorrect hiword flags, and missing lock on RMW mode. Test signals are phase get/set at 0 and 180, rejection of non-180 multiples such as 90, and register write verification for hiword and RMW variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-inverter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-mmc-phase.c -->
## sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-mmc-phase.c

### Purpose
Implements Rockchip MMC sample/drive phase clocks. It models a fixed divide-by-2 rate plus phase controls built from 90-degree coarse steps and optional fine delay elements, with register access through either CRU MMIO or GRF regmap.

### Important APIs, Types, and Functions
`struct rockchip_mmc_clock` stores hardware state, register or GRF location, shift, cached phase, and a rate-change notifier. `rockchip_mmc_recalc()` returns parent/2. `rockchip_mmc_get_phase()` decodes coarse degrees and fine delay count into an approximate phase. `rockchip_mmc_set_phase()` computes coarse/fine fields from requested degrees and writes them with hiword mask. `rockchip_mmc_clk_rate_notify()` caches phase before rate decreases and restores it after the rate change. `rockchip_clk_register_mmc()` registers the clock and notifier.

### Control Flow, State, and Persistence
The phase is stored in hardware fields and may be cached transiently during rate-change notifications. On rate decreases, PRE_RATE_CHANGE stores the old phase and POST_RATE_CHANGE restores it, avoiding stale tuning after parent rate changes. The initial `cached_phase` is not explicitly initialized, so notifier behavior depends on allocated memory contents until the first PRE event.

### Dependencies and Integration Points
The helper depends on CCF phase and notifier APIs, regmap for GRF-backed controls, MMIO access, and MMC host tuning flows that call `clk_set_phase()`. SoC tables choose CRU or GRF register access.

### Risks and Test Signals
Risks include approximate fine-delay math, phase restoration only on downward rate transitions, possible uninitialized `cached_phase`, and invalid parent/rate setup returning 0 rate. Test signals are MMC tuning across rates, get/set phase round trips, CRU and GRF-backed register writes, notifier behavior during parent changes, and high-speed modes that are sensitive to sample timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-mmc-phase.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-muxgrf.c -->
## sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-muxgrf.c

### Purpose
Implements Rockchip mux clocks controlled through GRF regmap fields instead of CRU mux registers. It supports normal regmap bit updates and hiword-mask writes.

### Important APIs, Types, and Functions
`struct rockchip_muxgrf_clock` holds CCF hardware, regmap, register, shift, width, and mux flags. `rockchip_muxgrf_get_parent()` reads the field and returns the raw parent index. `rockchip_muxgrf_set_parent()` writes the parent index using either `regmap_write()` with hiword mask or `regmap_update_bits()`. `rockchip_clk_register_muxgrf()` validates the regmap and registers the mux.

### Control Flow, State, and Persistence
Persistent state is the allocated mux object. Parent state lives in the GRF field. There is no polling or cached parent state.

### Dependencies and Integration Points
The helper depends on CCF mux APIs, regmap, and SoC branch tables for GRF muxes. It uses `__clk_mux_determine_rate()` for rate selection through parents.

### Risks and Test Signals
Risks include unavailable regmap, raw parent indexes without a translation table, wrong width/shift producing bad masks, and hiword writes to registers that do not support them. Test signals are parent switching, get-parent after set-parent, invalid regmap handling, and rate determination through all parents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-muxgrf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-pll.c -->
## sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-pll.c

### Purpose
Implements Rockchip PLL clock registration and operations for several hardware layouts: RK3036/RK3328-style, RK3066/RK3188/RK3288-style, RK3399-style, and RK3588-style PLLs. Each registered PLL appears behind a mux that can select slow input, normal PLL output, or deep/32 kHz input while the underlying PLL object owns rate calculation, set-rate, enable, disable, and optional init-time sync.

### Important APIs, Types, and Functions
`struct rockchip_clk_pll` stores the real PLL `clk_hw`, its public mux, notifier field, register base, lock status location, PLL type, flags, copied rate table, shared CRU lock, and provider context. `rockchip_pll_determine_rate()` chooses the nearest supported table rate at or below the request. Layout-specific helpers read parameters, recalculate rates, set parameters, wait for lock, and expose `clk_ops`: `rockchip_rk3036_*`, `rockchip_rk3066_*`, `rockchip_rk3399_*`, and `rockchip_rk3588_*`. `rockchip_clk_register_pll()` creates the mux clock, copies the rate table, selects ops by `enum rockchip_pll_type`, registers the actual PLL, and returns the mux clock to consumers.

### Control Flow, State, and Persistence
Rate changes are table-driven. For PLLs that can safely remux, set-params reads current settings, switches the mux from normal to slow mode if needed, writes new divider/fraction fields, waits for lock, attempts restoration on failure, and returns the mux to normal mode. RK3066 lock polling uses the GRF lock bit through provider regmap; RK3036, RK3399, and RK3588 poll PLL-local lock bits. Enable clears powerdown and waits for lock; disable sets powerdown. Init callbacks for several types compare hardware settings against the rate table and optionally resynchronize them when `ROCKCHIP_PLL_SYNC_RATE` is set.

### Dependencies and Integration Points
The file depends on CCF, regmap, MMIO, polling helpers, `HIWORD_UPDATE()`, and Rockchip provider/type/rate-table definitions from `clk.h`. It is used by SoC-specific CRU drivers that supply parent names, register offsets, lock offsets, mode mux locations, rate tables, and flags.

### Risks and Test Signals
Risks include incomplete rate tables, failed lock polling, recursive restore attempts if old settings also fail, incorrect mux parent counts for RK3328 versus other PLLs, and different behavior for RK3588 core/DDR PLLs where remuxing is skipped or rate is doubled. Test signals are rate determine/set/recalc consistency for every table entry, lock timeout handling, init sync on bootloader-programmed PLLs, enable/disable powerdown bits, and mux parent switching during rate changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-pll.c -->
