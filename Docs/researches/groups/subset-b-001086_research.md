# subset-b-001086 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-iproc-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-iproc-pll.c

## Purpose
Implements the reusable Broadcom iProc PLL and PLL-derived channel clock provider. It programs PLL VCO parameters, reset and power sequencing, lock polling, optional ASIU top-level gating, optional software override, and leaf clock dividers, then exposes the PLL and its channels through the Linux common clock framework and a device-tree onecell provider.

## Important APIs, Types, And Functions
Core private types are `struct iproc_pll` for mapped status/control/power/ASIU bases and PLL metadata, and `struct iproc_clk` for a `clk_hw` tied to either the PLL root or one leaf channel. `iproc_pll_clk_setup` is the exported setup entry used by SoC files. PLL operations include `pll_calc_param`, `pll_set_rate`, `iproc_pll_recalc_rate`, `iproc_pll_determine_rate`, and `iproc_pll_set_rate`. Channel operations include `iproc_clk_enable`, `iproc_clk_disable`, `iproc_clk_recalc_rate`, `iproc_clk_determine_rate`, and `iproc_clk_set_rate`.

## Control Flow
Setup allocates the PLL, onecell data, and an array of iProc clocks, maps control plus optional power, ASIU, and split status resources, registers output 0 as the PLL root, then registers remaining outputs as channel clocks parented by the PLL. Rate changes either compute VCO parameters at runtime or select an exact table entry, enable power/ASIU paths, skip disruptive reset when only fractional NDIV changes, otherwise assert reset, program user mode, VCO band bits, NDIV, fractional NDIV, PDIV, release reset with Ki/Kp/Ka values, and poll lock.

## State And Persistence
Persistent runtime state is the registered `clk_hw` graph, mapped MMIO bases, optional VCO parameter table pointer, and hardware register contents for power, reset, NDIV, PDIV, channel enable/hold, and MDIV. The driver keeps little mutable software state after setup; hardware is the source for recalc and enable checks.

## Dependencies And Integration Points
Depends on iProc control descriptors from `clk-iproc.h`, SoC-specific data in files such as `clk-ns2.c`, `clk-nsp.c`, and `clk-sr.c`, common clock framework registration, DT `clock-output-names`, `of_iomap`, and onecell clock lookup. It integrates with consumers through normal `clk_ops`.

## Risks And Edge Cases
PLL lock timeout returns `-EIO`; bad target rates, parent rates, or VCO table misses return `-EINVAL`. `bit_mask(width)` assumes safe widths. Resource mapping cleanup is multi-stage and must match optional bases. `IPROC_CLK_AON` disables runtime power-down. Fractional-only fast path is valid only when the PLL is locked and integer NDIV/PDIV match the target.

## Test Signals
Useful tests include DT nodes with split and unified status/control mappings, fractional and integer-only PLLs, calculated VCO mode, exact table mode, lock failure injection, `MCLK_DIV_BY_2` leaf rates, disable requests on always-on clocks, and provider lookup of every `clock-output-names` index.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-iproc-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-iproc.h -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-iproc.h

## Purpose
Defines the Broadcom iProc clock descriptor contract shared by generic PLL/ASIU helpers and SoC-specific clock table files. The header describes register bitfields, feature flags, VCO parameter tables, PLL power/reset/filter controls, channel enables, and exported setup functions.

## Important APIs, Types, And Functions
Important flags include `IPROC_CLK_AON`, `IPROC_CLK_PLL_ASIU`, `IPROC_CLK_PLL_HAS_NDIV_FRAC`, `IPROC_CLK_NEEDS_READ_BACK`, `IPROC_CLK_PLL_NEEDS_SW_CFG`, `IPROC_CLK_EMBED_PWRCTRL`, `IPROC_CLK_PLL_SPLIT_STAT_CTRL`, `IPROC_CLK_MCLK_DIV_BY_2`, `IPROC_CLK_PLL_USER_MODE_ON`, `IPROC_CLK_PLL_RESET_ACTIVE_LOW`, and `IPROC_CLK_PLL_CALC_PARAM`. Key structures are `iproc_pll_vco_param`, `iproc_clk_reg_op`, `iproc_asiu_gate`, `iproc_pll_aon_pwr_ctrl`, `iproc_pll_reset_ctrl`, `iproc_pll_dig_filter_ctrl`, `iproc_pll_sw_ctrl`, `iproc_pll_vco_ctrl`, `iproc_pll_ctrl`, `iproc_clk_enable_ctrl`, `iproc_clk_ctrl`, and `iproc_asiu_div`.

## Control Flow
The header has no runtime flow, but its descriptors drive the generic helpers. SoC files instantiate `iproc_pll_ctrl` and `iproc_clk_ctrl` arrays, then call `iproc_pll_clk_setup`, `iproc_armpll_setup`, or `iproc_asiu_setup`; the generic code interprets offsets, shifts, widths, and flags to map resources, program registers, and expose clocks.

## State And Persistence
State is declarative and usually `static const` in SoC files. The descriptor values persist for the lifetime of the registered clock provider and point the runtime code at hardware state rather than storing rates in software.

## Dependencies And Integration Points
Includes Linux common clock, OF, device, spinlock, slab, and kernel headers. It is consumed by Broadcom iProc SoC drivers and by the common `clk-iproc-pll.c` implementation.

## Risks And Edge Cases
Descriptor errors are hazardous because the generic driver trusts offsets, shifts, and widths. Missing optional fields must be paired with the right flags. `bit_mask(width)` is a simple shift expression, so widths must remain below the word size.

## Test Signals
Compile coverage across all iProc SoC table files, successful registration for each compatible string, and rate/enable behavior that matches hardware manuals are the main signals. Static review should verify every flagged feature has the corresponding descriptor fields populated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-iproc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-kona-setup.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-kona-setup.c

## Purpose
Validates and registers Broadcom Kona CCU clock data. It checks CCU and peripheral-clock descriptors for sane register ranges, bit positions, divider math, parent selector mappings, and trigger requirements before adding clocks and the OF onecell provider.

## Important APIs, Types, And Functions
The exported entry is `kona_dt_ccu_setup`. Validation helpers include `ccu_data_offsets_valid`, `peri_clk_data_offsets_valid`, `bit_posn_valid`, `bitfield_valid`, `policy_valid`, `gate_valid`, `hyst_valid`, `sel_valid`, `div_valid`, `kona_dividers_valid`, `trig_valid`, `peri_clk_data_valid`, and `kona_clk_valid`. Registration and cleanup helpers include `parent_process`, `clk_sel_setup`, `kona_clk_setup`, `kona_clk_teardown`, `ccu_clks_teardown`, `kona_ccu_teardown`, and `of_clk_kona_onecell_get`.

## Control Flow
`kona_dt_ccu_setup` converts the DT resource to a bounded register range, validates CCU-wide data, maps the CCU registers, records the node, then loops over predefined `kona_clks` and registers each populated clock. Parent processing compacts parent-name arrays by dropping `BAD_CLK_NAME` placeholders and creates a selector-value map that preserves original hardware selector positions. After adding the provider, `kona_ccu_init` programs initial hardware state.

## State And Persistence
Setup fills mutable fields in clock descriptors: allocated parent name arrays, selector value arrays, `clk_hw.init`, CCU base address, node reference, range, and provider state. Teardown frees selector arrays, unregisters clocks, deletes the provider, drops the node, and unmaps MMIO.

## Dependencies And Integration Points
Depends on `clk-kona.h` descriptor macros, OF address translation, common clock registration, and the runtime initializer in `clk-kona.c`. SoC-specific CCU definitions call this function from their `CLK_OF_DECLARE` paths.

## Risks And Edge Cases
The registration loop ignores individual `kona_clk_setup` return values and relies on later error checks imperfectly, so malformed individual clocks can leave partial providers. Parent arrays use dynamically allocated copies that must be freed on failures. Missing triggers are fatal when selectors or variable dividers require hardware commit. Fractional pre-divider plus divider widths must not overflow scaled arithmetic.

## Test Signals
Exercise invalid offsets outside the DT resource, bit positions above 31, zero-width selectors, unsupported parent placeholders, multiple parents without selectors, pre-trigger without trigger, variable divider without trigger, provider lookup bounds, and teardown after mid-registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-kona-setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-kona.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-kona.c

## Purpose
Implements Broadcom Kona CCU runtime clock operations: protected register access, policy engine control, gate management, hysteresis initialization, trigger commits, divider rate math, selector parent switching, and common-clock callbacks for peripheral clocks.

## Important APIs, Types, And Functions
Externally visible symbols are `scaled_div_max`, `kona_peri_clk_ops`, and `kona_ccu_init`. Important internals include `__ccu_write_enable`, `__ccu_wait_bit`, `__ccu_policy_engine_start`, `__ccu_policy_engine_stop`, `policy_init`, `__gate_commit`, `clk_gate`, `hyst_init`, `__clk_trigger`, `divider_read_scaled`, `__div_commit`, `divider_write`, `clk_recalc_rate`, `round_rate`, `selector_read_index`, `__sel_commit`, `selector_write`, and the `kona_peri_clk_*` callbacks.

## Control Flow
All hardware writes occur under the CCU spinlock with the write-access password enabled. Initialization walks CCU clocks and applies policy masks, gates, hysteresis, dividers, pre-dividers, and selectors. Runtime enable/disable toggles software-managed gates. Rate changes compute a scaled divisor, enable the clock if needed, write divider bits, pulse the trigger, then restore the previous gate state. Parent changes follow the same enable, write selector, trigger, restore pattern.

## State And Persistence
The CCU tracks `write_enabled` and serializes accesses with `lock`. Clock descriptors cache intended gate enabled state, selector index, and scaled divider value. Hardware registers persist actual gate status, policy masks, divider fields, selector fields, and trigger completion state.

## Dependencies And Integration Points
Integrates with descriptors from `clk-kona.h`, validation/setup in `clk-kona-setup.c`, Linux common clock callbacks, and DT onecell providers. Consumers invoke it through `clk_prepare_enable`, `clk_set_rate`, and parent-selection APIs.

## Risks And Edge Cases
Polling failures on gate or trigger commits return `-EIO`. Cached software state is reverted after failed divider/selector commits, but hardware may already be partially changed. The code uses `BUG_ON` for impossible descriptor states. `determine_rate` intentionally ignores `CLK_SET_RATE_NO_REPARENT` and does not propagate rate changes to parents.

## Test Signals
Signals include successful policy stop/start, gate status polling, no-disable gate behavior, selector readback with sparse hardware values, variable and fixed divider rounding, rate changes while initially disabled, trigger timeouts, and parent search selecting the closest achievable rate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-kona.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-kona.h -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-kona.h

## Purpose
Defines the Broadcom Kona CCU descriptor model used by setup and runtime code. It captures policy masks, gate variants, hysteresis bits, fixed and variable dividers, parent selectors, triggers, peripheral clock data, CCU data, and macros for static SoC clock tables.

## Important APIs, Types, And Functions
Core types are `bcm_clk_policy`, `bcm_clk_gate`, `bcm_clk_hyst`, `bcm_clk_div`, `bcm_clk_sel`, `bcm_clk_trig`, `peri_clk_data`, `kona_clk`, `bcm_lvm_en`, `bcm_policy_ctl`, `ccu_policy`, and `ccu_data`. Macros such as `POLICY`, `HW_SW_GATE`, `HW_SW_GATE_AUTO`, `HW_ENABLE_GATE`, `SW_ONLY_GATE`, `HW_ONLY_GATE`, `HYST`, `FIXED_DIVIDER`, `DIVIDER`, `FRAC_DIVIDER`, `SELECTOR`, `TRIGGER`, `CLOCKS`, `KONA_CLK`, and `KONA_CCU_COMMON` build static descriptors.

## Control Flow
The header itself is declarative. Setup code validates these descriptors and registers clocks; runtime code uses the same fields to decide which registers to read/write, how to map common-clock parent indexes to hardware selector values, and how to compute scaled divider rates.

## State And Persistence
Some descriptor fields are mutable runtime state, notably gate flags for software-managed enabled state, `bcm_clk_div.u.s.scaled_div`, `bcm_clk_sel.parent_sel`, `bcm_clk_sel.parent_count`, and `bcm_clk_sel.clk_index`. `ccu_data` persists the mapped base, lock, write-enable state, node, range, and flexible `kona_clks` array.

## Dependencies And Integration Points
Includes common clock and OF headers and exports `kona_peri_clk_ops`, `scaled_div_max`, `kona_dt_ccu_setup`, and `kona_ccu_init` for SoC files and setup/runtime split compilation.

## Risks And Edge Cases
Descriptors use flag macros and sentinel values such as `BAD_CLK_INDEX`, `BAD_CLK_NAME`, and `BAD_SCALED_DIV_VALUE`; misuse can silently change setup behavior. Because `kona_clk` embeds `clk_init_data`, parent arrays allocated during setup must remain valid until teardown.

## Test Signals
Static table validation, sparse parent selector mappings, fractional divider scale bounds, gate variants, CCU policy descriptors, and compile coverage of all macros are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-kona.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-ns2.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-ns2.c

## Purpose
Provides Northstar 2 iProc PLL descriptor tables and DT initialization hooks for genpll SCR, genpll SW, LCPLL DDR, and LCPLL ports clock blocks.

## Important APIs, Types, And Functions
This file defines register helper macros (`REG_VAL`, `AON_VAL`, `RESET_VAL`, `DF_VAL`, `VCO_CTRL_VAL`, `ENABLE_VAL`), `iproc_pll_ctrl` instances `genpll_scr`, `genpll_sw`, `lcpll_ddr`, and `lcpll_ports`, plus matching `iproc_clk_ctrl` channel arrays. Init functions `ns2_genpll_scr_clk_init`, `ns2_genpll_sw_clk_init`, `ns2_lcpll_ddr_clk_init`, and `ns2_lcpll_ports_clk_init` call `iproc_pll_clk_setup`.

## Control Flow
Each `CLK_OF_DECLARE` compatible invokes a small init wrapper at boot. The wrapper passes the appropriate PLL descriptor and channel array to the generic iProc PLL setup code, which maps resources, registers output clocks, and handles runtime PLL/channel operations.

## State And Persistence
All state in this file is static descriptor data. Runtime state is created by `clk-iproc-pll.c` and hardware registers. Most clocks are marked `IPROC_CLK_AON`, so the generic disable path will leave them running.

## Dependencies And Integration Points
Depends on `dt-bindings/clock/bcm-ns2.h` indexes, `clk-iproc.h`, OF `CLK_OF_DECLARE`, and the shared iProc PLL provider. Device-tree `clock-output-names` must align with the array indexes.

## Risks And Edge Cases
The NS2 comments note that `bypass_shift` is not defined and is set to 0 because the shared code does not use it. Split status/control flag requires the DT resource layout expected by `iproc_pll_clk_setup`. Index holes for unused channels still need stable binding alignment.

## Test Signals
Boot-time provider registration for all four compatible strings, correct onecell indexes for used and unused channels, recalc rates from MDIV fields, and no disable effect on always-on outputs are useful checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-ns2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-nsp.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-nsp.c

## Purpose
Defines Broadcom Northstar Plus iProc clock descriptors for ARM PLL, GENPLL, and LCPLL0 blocks and binds them to early DT clock setup.

## Important APIs, Types, And Functions
`nsp_armpll_init` delegates to `iproc_armpll_setup`. Descriptor macros initialize `genpll`, `genpll_clk`, `lcpll0`, and `lcpll0_clk`. `nsp_genpll_clk_init` and `nsp_lcpll0_clk_init` call `iproc_pll_clk_setup`, and `CLK_OF_DECLARE` binds compatible strings `brcm,nsp-armpll`, `brcm,nsp-genpll`, and `brcm,nsp-lcpll0`.

## Control Flow
At OF clock initialization, the matching wrapper invokes the common iProc implementation with fractional NDIV and embedded power-control descriptors. The common code registers the PLL root and channel outputs with channel-specific enable and MDIV fields.

## State And Persistence
The file contributes static register descriptors only. Hardware register state and allocated `clk_hw` structures are owned by the shared iProc implementation. Several outputs are always-on and therefore persist through disable attempts.

## Dependencies And Integration Points
Uses `dt-bindings/clock/bcm-nsp.h`, `clk-iproc.h`, and OF clock declaration infrastructure. The DT resource and `clock-output-names` ordering must match the binding enum indexes.

## Risks And Edge Cases
Incorrect fractional NDIV, PDIV, reset, or status offsets can make PLL rate changes fail or hang waiting for lock. The ARM PLL path is external to this file, so platform support depends on that helper being linked.

## Test Signals
Probe-time registration under all three compatible strings, PLL recalc with fractional NDIV, lock behavior after rate changes, stable output indexes, and always-on disable protection are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-nsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-raspberrypi.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-raspberrypi.c

## Purpose
Implements Raspberry Pi firmware-controlled clocks as common-clock providers. It uses firmware mailbox properties instead of direct register access so firmware can continue managing thermal and undervoltage constraints, especially for PLLB/ARM and shared display/media clocks.

## Important APIs, Types, And Functions
Key types are `raspberrypi_clk`, `raspberrypi_clk_data`, `raspberrypi_clk_variant`, `raspberrypi_firmware_prop`, and `rpi_firmware_get_clocks_response`. Important routines include `raspberrypi_clock_property`, `raspberrypi_fw_is_prepared`, `raspberrypi_fw_get_rate`, `raspberrypi_fw_set_rate`, `raspberrypi_fw_dumb_determine_rate`, `raspberrypi_fw_prepare`, `raspberrypi_fw_unprepare`, `raspberrypi_clk_register`, `raspberrypi_discover_clocks`, `raspberrypi_clk_probe`, and `raspberrypi_clk_remove`.

## Control Flow
Probe locates the firmware node, obtains an `rpi_firmware` handle, allocates onecell data, discovers available firmware clocks, filters for exported variants, queries min/max rates, registers each `clk_hw`, optionally registers clkdev aliases, enforces variant minimum rates, adds the OF provider, and spawns the Raspberry Pi cpufreq platform device. Clock operations translate prepare, unprepare, rate get, and rate set into firmware tags.

## State And Persistence
Persistent state includes the firmware handle, one `clk_hw` per exported firmware clock, variant policy flags (`minimize`, `maximize`, `min_rate`, `CLK_IS_CRITICAL`, `CLK_IGNORE_UNUSED`), rate ranges stored in CCF, and the child cpufreq platform device. Actual clock state persists in firmware.

## Dependencies And Integration Points
Depends on `soc/bcm2835/raspberrypi-firmware.h`, platform devices, OF provider APIs, clkdev aliases for CPU clock consumers, and firmware property tags such as `GET_CLOCKS`, `GET/SET_CLOCK_RATE`, `GET_MIN/MAX_CLOCK_RATE`, and `GET/SET_CLOCK_STATE`.

## Risks And Edge Cases
Firmware discovery can report unknown IDs. `determine_rate` cannot know firmware rounding. `unprepare` deliberately sets rate to minimum before disabling because firmware may not fully power off clocks. Shared clocks use minimize/maximize policies that can surprise consumers expecting exact requested rates. Missing firmware node defers or fails probe.

## Test Signals
Mock firmware responses for discovery, min/max, state, and rate changes; exported-only clocks in the onecell provider; cpufreq child creation/removal; minimum-rate enforcement for M2MC; critical clocks staying enabled; and rate restoration for maximize variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-raspberrypi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-sr.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-sr.c

## Purpose
Provides Broadcom Stingray iProc PLL descriptor tables and platform-driver dispatch for multiple GENPLL and LCPLL blocks, plus an early OF declaration for GENPLL3.

## Important APIs, Types, And Functions
The file defines descriptor helper macros and static `iproc_pll_ctrl`/`iproc_clk_ctrl` arrays for `sr_genpll0`, `sr_genpll2`, `sr_genpll3`, `sr_genpll4`, `sr_genpll5`, `sr_lcpll0`, `sr_lcpll1`, and `sr_lcpll_pcie`. Per-block init functions call `iproc_pll_clk_setup`. `sr_clk_dt_ids`, `sr_clk_probe`, and `sr_clk_driver` dispatch platform probes using `of_device_get_match_data`.

## Control Flow
For most Stingray PLL nodes, the built-in platform driver probes, extracts the function pointer from the match table, and runs the matching init function. `sr_genpll3_clk_init` is instead registered through `CLK_OF_DECLARE`. The common iProc provider handles resource mapping, PLL programming, channel registration, and runtime callbacks.

## State And Persistence
This file is static SoC metadata. Runtime state is allocated by `iproc_pll_clk_setup`; hardware retains PLL and channel divider state. Many outputs are flagged `IPROC_CLK_AON`, and several PLLs require `IPROC_CLK_PLL_NEEDS_SW_CFG` before programming.

## Dependencies And Integration Points
Depends on `dt-bindings/clock/bcm-sr.h`, `clk-iproc.h`, OF match data, and built-in platform driver registration. It integrates with the shared iProc PLL engine and common clock consumers.

## Risks And Edge Cases
The mixed early-declare and platform-driver model means init ordering differs between GENPLL3 and other PLLs. Descriptor copy-paste errors in shifts or channel indexes directly affect hardware programming. Missing match data returns `-ENODEV`.

## Test Signals
Probe each compatible string, verify channel indexes match binding enums, confirm software override bits are written for flagged PLLs, ensure always-on channels ignore disable, and check rate recalc/set behavior for fractional and integer-only PLLs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-sr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/berlin/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/berlin/Makefile

## Purpose
Builds the Marvell Berlin clock support objects. Common AVPLL, PLL, and divider helpers are always built for the directory, while SoC provider files are selected by machine configuration.

## Important APIs, Types, And Functions
The make rules add `berlin2-avpll.o`, `berlin2-pll.o`, and `berlin2-div.o` unconditionally. `bg2.o` is selected for `CONFIG_MACH_BERLIN_BG2` and `CONFIG_MACH_BERLIN_BG2CD`; `bg2q.o` is selected for `CONFIG_MACH_BERLIN_BG2Q`.

## Control Flow
Kbuild compiles the common helper objects and conditionally links the SoC-specific provider object that contains the `CLK_OF_DECLARE` setup function for the configured machine.

## State And Persistence
No runtime state exists in the Makefile. It controls which object files are available in the kernel image.

## Dependencies And Integration Points
Integrates with Kbuild and the Berlin machine configuration symbols. The SoC files depend on the common helper objects being linked.

## Risks And Edge Cases
Because common objects are `obj-y`, they may be built even when no Berlin SoC provider is selected by this local file. Missing config coverage would omit the `CLK_OF_DECLARE` provider and leave DT clock nodes unresolved.

## Test Signals
Build tests for BG2, BG2CD, and BG2Q configurations should show the expected provider object linked with the three common helper objects and no unresolved helper symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/berlin/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/berlin/berlin2-avpll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/berlin/berlin2-avpll.c

## Purpose
Implements Berlin2 audio/video PLL VCO and channel clock providers. It models each AVPLL as a VCO plus eight channel clocks, handling production SoC bit-shift and channel-scramble quirks while calculating channel rates from sync and divider registers.

## Important APIs, Types, And Functions
Private types are `berlin2_avpll_vco` and `berlin2_avpll_channel`. Exported registration functions are `berlin2_avpll_vco_register` and `berlin2_avpll_channel_register`. Clock operations include VCO enable/disable/is_enabled/recalc and channel enable/disable/is_enabled/recalc. Quirk handling uses `BERLIN2_AVPLL_BIT_QUIRK`, `BERLIN2_AVPLL_SCRAMBLE_QUIRK`, and `quirk_index`.

## Control Flow
SoC setup registers a VCO clock parented by the reference clock, then registers channel clocks parented by that VCO. VCO recalc reads `VCO_CTRL1` refdiv/fbdiv. Channel recalc checks whether the channel DPLL divider is enabled, reads sync1/sync2, applies optional HDMI, AV1, AV2, and AV3 divisors, accounts for fractional AV2/AV3 behavior, and divides the parent-derived frequency.

## State And Persistence
Each registered clock stores a base address, flags, and channel index. Actual power, sync, divider, and DPLL state resides in AVPLL MMIO registers. Allocation is permanent after early boot registration and has no explicit unregister path in this file.

## Dependencies And Integration Points
Used by `bg2.c` for AVPLL A/B registration. Depends on common clock framework, MMIO accessors, and constants declared in `berlin2-avpll.h`.

## Risks And Edge Cases
Channel 8 is special and lacks normal dividers. BG2/BG2CD quirks shift some fields and scramble channel indexes. Zero sync/divider values can produce invalid or misleading rates if hardware is not initialized. Registration leaks allocations if `clk_hw_register` fails after allocation.

## Test Signals
Validate VCO rates from known refdiv/fbdiv values, channel rates for enabled and bypassed DPLL paths, quirked AVPLL_B channel 1 sync shift, scrambled channel mappings, and enable bits for channels 1 through 7 with channel 8 always enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/berlin/berlin2-avpll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/berlin/berlin2-avpll.h -->
# sources/distributed-fs/ceph-client/drivers/clk/berlin/berlin2-avpll.h

## Purpose
Declares the Berlin2 AVPLL helper interface and quirk flags used by SoC provider files.

## Important APIs, Types, And Functions
Defines `BERLIN2_AVPLL_BIT_QUIRK` for shifted register fields and `BERLIN2_AVPLL_SCRAMBLE_QUIRK` for channel index translation. Declares `berlin2_avpll_vco_register` and `berlin2_avpll_channel_register`.

## Control Flow
No runtime logic exists here. SoC setup code passes MMIO base, names, parent names, indexes, quirk flags, and CCF flags to the implementation in `berlin2-avpll.c`.

## State And Persistence
The header holds only constants and prototypes. Registered clock state is allocated by the implementation.

## Dependencies And Integration Points
Consumed by `bg2.c` and implemented by `berlin2-avpll.c`. It assumes inclusion context provides `BIT`, `u8`, and `void __iomem` definitions through kernel headers.

## Risks And Edge Cases
Incorrect quirk flag choice changes register interpretation for all AVPLL channels. Since the prototypes are `__init` implementations, callers should only use them during early clock setup.

## Test Signals
Compile/link coverage and BG2/BG2CD setup using both quirk flags are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/berlin/berlin2-avpll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/berlin/berlin2-div.c -->
# sources/distributed-fs/ceph-client/drivers/clk/berlin/berlin2-div.c

## Purpose
Implements Berlin2 composite divider cells that may include an input PLL mux, programmable divider, divide-by-3 bypass path, and gate. It wraps this hardware in CCF composite clock registration.

## Important APIs, Types, And Functions
Private `struct berlin2_div` stores `clk_hw`, base, copied `berlin2_div_map`, and optional lock. The exported `berlin2_div_register` creates a composite clock. Operations include `berlin2_div_is_enabled`, `berlin2_div_enable`, `berlin2_div_disable`, `berlin2_div_set_parent`, `berlin2_div_get_parent`, and `berlin2_div_recalc_rate`.

## Control Flow
Registration copies the map, chooses mux/rate/gate ops based on flags, and calls `clk_hw_register_composite`. Parent selection toggles `PLL_SWITCH`, then programs `PLL_SELECT` for nonzero parent indexes. Rate recalc checks divide-by-3 switch first, then divider bypass, otherwise maps `DIV_SELECT` through the fixed divider table `{1,2,4,6,8,12,1,1}`.

## State And Persistence
Per-clock software state is the copied map and base pointer. Hardware registers persist selected parent, divider selection, divide-by-3 switch, divider bypass, and gate enable. The optional spinlock serializes shared register updates across Berlin clock cells.

## Dependencies And Integration Points
Used by `bg2.c` and `bg2q.c` with maps from `berlin2-div.h`. Integrates with common clock composite helpers and shared SoC register locks.

## Risks And Edge Cases
Only recalc is implemented for rate; `determine_rate` is no-reparent and there is no divider programming path. Parent indexes assume the hardware encoding where index 0 means bypass and index >0 maps to `PLL_SELECT=index-1`. Missing locks around shared registers would race with mux/gate changes.

## Test Signals
Check parent get/set encodings, divide-by-3 dominance, divider bypass, all divider table values, optional gate/mux flag combinations, and concurrent register access under the shared spinlock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/berlin/berlin2-div.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/berlin/berlin2-div.h -->
# sources/distributed-fs/ceph-client/drivers/clk/berlin/berlin2-div.h

## Purpose
Defines Berlin2 divider-cell descriptor structures and macros for mapping logical mux/divider/gate controls onto scattered SoC registers.

## Important APIs, Types, And Functions
Flags `BERLIN2_DIV_HAS_GATE` and `BERLIN2_DIV_HAS_MUX` select composite sub-ops. Mapping macros include `BERLIN2_PLL_SELECT`, `BERLIN2_PLL_SWITCH`, `BERLIN2_DIV_SELECT`, `BERLIN2_DIV_SWITCH`, `BERLIN2_DIV_D3SWITCH`, `BERLIN2_DIV_GATE`, and `BERLIN2_SINGLE_DIV`. Structures are `berlin2_div_map` and `berlin2_div_data`. The exported constructor is `berlin2_div_register`.

## Control Flow
No code executes in the header. SoC files populate `berlin2_div_data` arrays; `berlin2_div_register` consumes each map to register a composite CCF clock.

## State And Persistence
Maps are typically `__initconst`; the implementation copies them into permanent per-clock state so early init data can be discarded.

## Dependencies And Integration Points
Consumed by Berlin SoC provider files and implemented by `berlin2-div.c`. Parent IDs in `berlin2_div_data` are translated by SoC files into parent name arrays.

## Risks And Edge Cases
The macros only describe offsets and shifts; they do not validate that fields fit in registers or do not overlap. Shared-register maps must use the same lock at registration.

## Test Signals
Build coverage for single-register and scattered-register maps, gate-less and mux-less cells, and parent-name generation from `parent_ids` arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/berlin/berlin2-div.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/berlin/berlin2-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/berlin/berlin2-pll.c

## Purpose
Implements simple Berlin2 system PLL rate reporting. It reads feedback, reference, and VCO divider fields and exposes the result as a CCF clock.

## Important APIs, Types, And Functions
Private `struct berlin2_pll` stores `clk_hw`, base, and a copied `berlin2_pll_map`. `berlin2_pll_recalc_rate` implements the rate formula, and `berlin2_pll_register` allocates/registers a PLL clock.

## Control Flow
Registration copies the map, attaches one parent, and calls `clk_hw_register`. Recalc reads `SPLL_CTRL0` for feedback and reference divisors, reads `SPLL_CTRL1` for the VCO divider select, maps that selector through `map->vcodiv`, multiplies by `map->mult`, and divides by refdiv and vcodiv.

## State And Persistence
Per-clock software state is static after registration. Hardware registers persist PLL configuration. The driver only reports rates; it does not enable, disable, or reprogram PLL settings.

## Dependencies And Integration Points
Used by `bg2.c` and `bg2q.c` with maps from `berlin2-pll.h`. Integrates with common clock framework parent/rate propagation.

## Risks And Edge Cases
Zero refdiv or vcodiv values are warned and treated as one to avoid divide-by-zero, which can hide bad hardware state. Failed registration leaks the allocated PLL object. No locking is used because this driver only reads PLL registers.

## Test Signals
Known register images should produce expected rates, zero divisor warnings should not crash, and BG2/BG2Q maps should select the correct shifts and VCO divider tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/berlin/berlin2-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/berlin/berlin2-pll.h -->
# sources/distributed-fs/ceph-client/drivers/clk/berlin/berlin2-pll.h

## Purpose
Declares the Berlin2 PLL descriptor map and registration API used by SoC clock setup code.

## Important APIs, Types, And Functions
`struct berlin2_pll_map` contains the VCO divider lookup table, multiplier, and bit shifts for feedback, reference, and divider-select fields. `berlin2_pll_register` registers a simple PLL clock from a map, base, name, parent name, and flags.

## Control Flow
The header is declarative. SoC files create `__initconst` maps and pass them to the implementation.

## State And Persistence
Map data is copied by the implementation into the permanent clock object at registration time.

## Dependencies And Integration Points
Consumed by `bg2.c`, `bg2q.c`, and `berlin2-pll.c`.

## Risks And Edge Cases
The 16-entry `vcodiv` table may contain zero holes, so the implementation must defend against selected invalid entries. Incorrect shift values produce wrong clock tree rates.

## Test Signals
Compile/link coverage and rate-recalc tests for BG2 and BG2Q maps are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/berlin/berlin2-pll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/berlin/bg2.c -->
# sources/distributed-fs/ceph-client/drivers/clk/berlin/bg2.c

## Purpose
Registers the Berlin2/Berlin2CD global clock tree: reference inputs, simple PLLs, AVPLL VCOs/channels, bypass muxes, audio/video muxes, composite divider cells, leaf gates, and fixed-factor TWD clock.

## Important APIs, Types, And Functions
The main entry is `berlin2_clock_setup`, declared with `CLK_OF_DECLARE` for `marvell,berlin2-clk`. Static data includes register offsets, `clk_names`, `bg2_pll_map`, `default_parent_ids`, `bg2_divs`, and `bg2_gates`. It calls `berlin2_pll_register`, `berlin2_avpll_vco_register`, `berlin2_avpll_channel_register`, `clk_hw_register_mux`, `berlin2_div_register`, `clk_hw_register_gate`, and `clk_hw_register_fixed_factor`.

## Control Flow
Setup allocates onecell data, maps the parent global-register node, optionally replaces default reference names from DT, registers SYS/MEM/CPU PLLs, selects AVPLL scramble quirks for Berlin2, registers AVPLL A and B VCO/channel trees, creates PLL bypass muxes and audio/video muxes, registers all divider and gate cells into binding-indexed onecell slots, adds the fixed TWD clock, checks leaf clock errors, and adds the OF provider.

## State And Persistence
Global static `clk_data`, `gbase`, and `lock` persist after early setup. The onecell array stores only public leaf clocks by binding index; intermediate PLLs/muxes are registered by name for parent resolution.

## Dependencies And Integration Points
Depends on Berlin clock bindings, common Berlin helper files, OF parent/global register mapping, CCF registration, and DT-compatible selection. Consumers use the dt-binding indexes.

## Risks And Edge Cases
Failure cleanup only unmaps `gbase`; registered earlier clocks and allocated onecell data are not fully unwound. Some audio/video parent PLLs are documented as assumptions or unknown. Error checks only inspect onecell leaf slots, not every intermediate registration result beyond immediate `IS_ERR` checks.

## Test Signals
Boot with Berlin2 and Berlin2CD compatibles, verify AVPLL quirk selection, provider indexes for all `CLKID_*` leaves, bypass mux parent names, gate bits under `REG_CLKENABLE`, and TWD fixed factor from CPU/3.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/berlin/bg2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/berlin/bg2q.c -->
# sources/distributed-fs/ceph-client/drivers/clk/berlin/bg2q.c

## Purpose
Registers the Berlin2Q global clock tree, including system and CPU PLLs, composite divider cells, peripheral gates, CPU fixed-factor clock, and TWD fixed-factor clock.

## Important APIs, Types, And Functions
The main entry is `berlin2q_clock_setup`, declared with `CLK_OF_DECLARE` for `marvell,berlin2q-clk`. Static data includes `clk_names`, `bg2q_pll_map`, `default_parent_ids`, `bg2q_divs`, and `bg2q_gates`. It uses `berlin2_pll_register`, `berlin2_div_register`, `clk_hw_register_gate`, and `clk_hw_register_fixed_factor`.

## Control Flow
Setup allocates onecell data, maps the global register resource and the separate CPU PLL resource, optionally replaces `refclk` from DT, registers SYSPLL and CPUPLL, registers all divider cells with parent names resolved from parent IDs, registers gates, adds fixed CPU and TWD clocks, checks leaf slots for registration errors, then adds the OF provider.

## State And Persistence
Static globals `clk_data`, `gbase`, `cpupll_base`, and `lock` persist after init. Registered clocks and MMIO mappings remain for the lifetime of the system.

## Dependencies And Integration Points
Depends on `dt-bindings/clock/berlin2q.h`, common Berlin divider and PLL helpers, OF address resources from the parent node, and CCF provider APIs.

## Risks And Edge Cases
The file explicitly lacks BG2Q AVPLL and PLL bypass switch support. Failure cleanup unmaps bases but does not unregister clocks already registered. Parent IDs for AVPLL names are present even though AVPLL registration is TODO, so related rates may depend on external or absent parent clocks.

## Test Signals
Boot registration on BG2Q DT, correct mapping of separate CPU PLL base, provider slots for all dividers/gates, fixed CPU and TWD rates, graceful handling of missing AVPLL parents, and error paths for missing resources are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/berlin/bg2q.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/berlin/common.h -->
# sources/distributed-fs/ceph-client/drivers/clk/berlin/common.h

## Purpose
Provides a small shared Berlin descriptor for simple gate clocks used by SoC provider files.

## Important APIs, Types, And Functions
Defines `struct berlin2_gate_data` with `name`, `parent_name`, `bit_idx`, and CCF `flags`.

## Control Flow
No code executes here. `bg2.c` and `bg2q.c` iterate arrays of `berlin2_gate_data` and call `clk_hw_register_gate` for each entry.

## State And Persistence
Gate descriptors are static init-time data. Runtime gate state is stored in SoC clock-enable registers and CCF gate objects.

## Dependencies And Integration Points
Included by Berlin SoC provider files. It complements the divider and PLL helper headers.

## Risks And Edge Cases
The descriptor does not carry a register offset, so users assume all gates in a given array share the SoC file's `REG_CLKENABLE` base. Wrong bit indexes affect unrelated hardware clocks.

## Test Signals
Compile coverage and provider tests verifying each gate name, parent, bit, and ignore-unused flag are sufficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/berlin/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-apple-nco.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-apple-nco.c

## Purpose
Implements Apple SoC numerically controlled oscillator channels as programmable CCF clocks. The driver translates desired rates into NCO divisor and accumulator increment registers, including the LFSR encoding used for coarse divisors.

## Important APIs, Types, And Functions
Important types are `applnco_tables` and `applnco_channel`. Core helpers include `applnco_compute_tables`, `applnco_div_out_of_range`, `applnco_div_translate`, `applnco_div_translate_inv`, `applnco_set_rate`, `applnco_recalc_rate`, `applnco_determine_rate`, enable/disable/is_enabled callbacks, and `applnco_probe`.

## Control Flow
Probe maps the register resource, derives the number of channels from resource size and channel stride, allocates onecell data and shared translation tables, initializes each channel with its own lock and base offset, registers one clock per channel with parent index 0, then adds an OF onecell provider. Rate set computes a base divisor and two accumulator increments, validates/encodes the divisor, disables the channel under lock, writes divider/increment/accumulator initial registers, and restores enable state.

## State And Persistence
Each channel stores base, shared LFSR tables, `clk_hw`, and a spinlock. Hardware registers persist enable, encoded divisor, increments, and accumulator initial value. CCF provider state persists through devm lifetime.

## Dependencies And Integration Points
Depends on platform resources, OF compatibles `apple,t8103-nco` and `apple,nco`, CCF onecell providers, bitfield helpers, math64 division, and spinlocks.

## Risks And Edge Cases
The operation theory is partly inferred. Unsupported accumulator wraparound or zero increments make recalc return zero. Very low or high requested rates can put the coarse divisor out of range. Rate programming temporarily disables the channel, which may glitch consumers.

## Test Signals
Check LFSR forward/inverse table round trips, min/max determine-rate clamping, set/recalc consistency for representative parent rates, enable preservation across set_rate, multi-channel resource sizing, and rejection of out-of-range divisors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-apple-nco.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-asm9260.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-asm9260.c

## Purpose
Registers the AlphaScale ASM9260 clock controller at early OF init. It builds a clock tree from a fixed PLL rate register, muxes, mux update gates, one-based dividers, and AHB peripheral gates.

## Important APIs, Types, And Functions
Descriptor types are `asm9260_div_clk`, `asm9260_gate_data`, and `asm9260_mux_clock`. Static tables define divider clocks, mux gates, AHB gates, parent data, mux tables, and mux clocks. The entry is `asm9260_acc_init`, declared with `CLK_OF_DECLARE`.

## Control Flow
Initialization allocates onecell data, maps the controller with `of_io_request_and_map`, reads the SYSPLL rate from register bits times 1 MHz, registers a fixed-rate PLL, registers muxes with table encodings, registers mux update gates, registers dividers into binding-indexed slots, registers AHB gates into binding-indexed slots, checks leaf slots for `ERR_PTR`, and adds the OF provider.

## State And Persistence
Static globals hold `clk_data`, MMIO `base`, and a spinlock. Hardware registers persist mux selection, update gate bits, divider values, and AHB gates. Registered clocks are permanent early-boot objects.

## Dependencies And Integration Points
Depends on `dt-bindings/clock/alphascale,asm9260.h`, CCF mux/gate/divider helpers, OF early init, and parent clocks from DT index 0 plus named PLL/RTC parents.

## Risks And Edge Cases
Several registration calls are not individually checked before later leaf-slot validation, and intermediate mux/gate failures may be missed. Failure paths use `panic` for mapping or PLL registration failures. The fixed PLL rate assumes register bits encode MHz directly.

## Test Signals
Boot with ASM9260 DT, verify PLL rate from `HW_SYSPLLCTRL`, all binding indexes resolve, mux table values `{0,1,3}` select expected parents, one-based divider rates are correct, and `CLK_IGNORE_UNUSED` gates stay enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-asm9260.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-axi-clkgen.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-axi-clkgen.c

## Purpose
Implements the Analog Devices AXI clkgen pcore clock generator. It programs Xilinx MMCM dynamic reconfiguration registers to synthesize requested output rates, supports parent selection, and adapts operating limits to FPGA family, speed grade, voltage, and pcore version.

## Important APIs, Types, And Functions
Types include `axi_clkgen_limits`, `axi_clkgen`, and `axi_clkgen_div_params`. Important helpers are `axi_clkgen_calc_params`, `axi_clkgen_calc_clk_params`, `axi_clkgen_wait_non_busy`, `axi_clkgen_mmcm_read`, `axi_clkgen_mmcm_write`, `axi_clkgen_mmcm_enable`, `axi_clkgen_set_div`, `axi_clkgen_set_rate`, `axi_clkgen_determine_rate`, `axi_clkgen_get_div`, `axi_clkgen_recalc_rate`, `axi_clkgen_setup_limits`, and `axi_clkgen_probe`.

## Control Flow
Probe maps registers, handles optional `s_axi_aclk`, validates parent count, reads parent names, selects default or discovered FPGA limits, names the output clock, disables the MMCM, registers the clock, and adds a simple OF provider. Rate determination searches integer and fractional MMCM divider combinations within PFD/VCO limits. Set-rate writes power, output divider, input divider, feedback divider, lock, and filter registers through the DRP interface.

## State And Persistence
The driver stores base, `clk_hw`, and selected limits. Hardware persists reset/MMCM enable, parent select, and DRP-programmed MMCM registers. It does not cache the programmed rate; recalc reads MMCM dividers back.

## Dependencies And Integration Points
Depends on ADI AXI version/info registers, Xilinx MMCM DRP semantics, CCF APIs, optional AXI bus clock, OF compatibles `adi,axi-clkgen-2.00.a` and `adi,zynqmp-axi-clkgen-2.00.a`, and module platform-driver binding.

## Risks And Edge Cases
DRP busy timeouts return `-EIO`; some write paths do not propagate read-modify-write failures. Parameter search uses kHz scaling and may lose precision. Parent count differs between legacy and named AXI-clock DTs. Unknown speed grades fail probe for newer pcores.

## Test Signals
Mock register tests for DRP busy handling, set/recalc consistency across integer and fractional rates, parent get/set, pcore-version limit selection, voltage-limited speed grade behavior, invalid parent counts, and zero parent/requested rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-axi-clkgen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-axm5516.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-axm5516.c

## Purpose
Provides the LSI Axxia AXM5516 clock controller, registering PLL, divider, and mux clocks backed by a shared MMIO regmap and exposing them through DT binding indexes.

## Important APIs, Types, And Functions
Common type `axxia_clk` embeds `clk_hw` and regmap. Specialized types are `axxia_pllclk`, `axxia_divclk`, and `axxia_clkmux`. Important callbacks are `axxia_pllclk_recalc`, `axxia_divclk_recalc_rate`, and `axxia_clkmux_get_parent`. Static objects define all PLLs, dividers, muxes, and `axmclk_clocks`. Provider/probe functions are `of_clk_axmclk_get`, `axmclk_probe`, `axmclk_init`, and `axmclk_exit`.

## Control Flow
The core initcall registers a platform driver. Probe maps the resource, creates a regmap, assigns that regmap to each static clock object, registers each `clk_hw`, and adds an OF provider. Recalc callbacks read control registers to compute PLL or divider rates; mux callback reads parent selector fields.

## State And Persistence
Clock objects are static globals; probe fills their regmap pointer. Hardware registers persist PLL dividers, postdividers, reference dividers, clock dividers, and mux selections. The provider returns clocks by binding enum index.

## Dependencies And Integration Points
Depends on `dt-bindings/clock/lsi,axm5516-clks.h`, platform resources, regmap MMIO, CCF, and OF provider APIs. Parent clocks such as `clk_ref0`, `clk_ref1`, and `clk_ref2` must be provided elsewhere.

## Risks And Edge Cases
The driver is read-only for rates and mux parents; it cannot change rates or parents. Static clock objects complicate multiple-instance support. Integer arithmetic calculates `(parent / divisors) * fbdiv`, which may lose precision. Provider lookup assumes every binding index maps to a non-null static object.

## Test Signals
Probe registration count, provider bounds checking, PLL rate formulas, divider one-plus field behavior, mux parent indexes, required external reference clocks, and single-instance assumptions should be covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-axm5516.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-bd718x7.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-bd718x7.c

## Purpose
Registers the 32 kHz output clock exposed by ROHM BD718xx and BD72720 PMIC MFD devices, using the parent PMIC regmap to gate or ungate the output bit.

## Important APIs, Types, And Functions
`struct bd718xx_clk` stores `clk_hw`, register, mask, platform device, and regmap. Important functions are `bd71837_clk_set`, `bd71837_clk_enable`, `bd71837_clk_disable`, `bd71837_clk_is_enabled`, and `bd71837_clk_probe`. Platform IDs map chip variants to register addresses.

## Control Flow
Probe gets the parent device regmap, reads the parent clock name from the parent DT node, chooses the output-control register based on `rohm_chip_type`, optionally overrides the output name from `clock-output-names`, registers a simple `clk_hw`, and adds an OF simple provider. Prepare writes the enable mask; unprepare clears it; is_prepared reads the bit.

## State And Persistence
Driver state is devm-allocated per platform device. The PMIC register persists the actual output enable state. The clock has one parent supplied by the parent node.

## Dependencies And Integration Points
Depends on ROHM MFD platform IDs, parent regmap, CCF prepare/unprepare APIs, OF parent clock naming, and platform-driver module binding.

## Risks And Edge Cases
Missing parent regmap or parent clock name fails probe. `bd71837_clk_enable` passes all ones to `regmap_update_bits`, relying on the mask to select the enable bit. `is_prepared` returns a negative regmap error directly if read fails, which CCF callers must tolerate.

## Test Signals
Probe all supported platform IDs, verify selected register addresses, parent clock name requirement, output-name override, prepare/unprepare bit updates, regmap read error behavior, and provider lookup via parent DT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-bd718x7.c -->
