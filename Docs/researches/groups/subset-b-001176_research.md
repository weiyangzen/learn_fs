# subset-b-001176 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/ums512-clk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sprd/ums512-clk.c

## Purpose
This file is the Unisoc UMS512 clock provider. It describes the SoC clock tree for many independent register regions: PMU PLL gates, analog PHY PLL blocks, AP AHB/AP APB gates, AP composite clocks, AON APB clocks and gates, AUDCP gates, GPU clocks, multimedia clocks, and multimedia gates. It is mostly declarative: the implementation binds Unisoc clock helper macros to register offsets, bitfields, parent data, fixed factors, and dt-binding clock IDs.

## Important APIs, Types, And Functions
The primary exported behavior is through the platform driver `ums512_clk_driver`. `ums512_clk_probe()` uses `device_get_match_data()`, `sprd_clk_regmap_init()`, and `sprd_clk_probe()` to register the `clk_hw_onecell_data` for the matched register block. Each `sprd_clk_desc` contains the common clocks that need regmap-backed registration plus the hardware onecell table exposed to consumers. The file uses Unisoc helpers from `common.h`, `composite.h`, `div.h`, `gate.h`, `mux.h`, and `pll.h`: `SPRD_PLL_*`, `SPRD_SC_GATE_CLK_*`, `SPRD_MUX_CLK_DATA`, `SPRD_COMP_CLK_DATA`, `SPRD_DIV_CLK_HW`, and Linux `CLK_FIXED_FACTOR_*`.

## Control Flow
Device tree compatible strings select one descriptor from `sprd_ums512_clk_ids`. Probe initializes the regmap for that register resource, then publishes the corresponding onecell clock provider. There is no custom rate algorithm in this file; runtime operations are supplied by the shared Unisoc PLL/gate/mux/div/composite implementations selected by the macros.

## State And Persistence
Persistent state is hardware register state in the matched clock block. The static descriptor tables are immutable driver metadata. Some clocks use `CLK_IGNORE_UNUSED` because firmware, hardware DVFS, or co-processors may control them outside the Linux clock API. AUDCP gates also use `SPRD_GATE_NON_AON` because their register behavior differs from always-on gate blocks.

## Dependencies And Integration Points
The file depends on `dt-bindings/clock/sprd,ums512-clk.h` for numeric IDs and on matching DTS nodes such as `sprd,ums512-pmu-gate`, `sprd,ums512-ap-clk`, and `sprd,ums512-mm-gate-clk`. Parent clocks are mixed: some are firmware-named external clocks like `ext-26m`, `ext-32k`, `rco-100m`, and others are `clk_hw` links to PLL-derived clocks defined earlier in the file. Consumers use the onecell provider by binding ID.

## Risks
The largest risk is table drift: a wrong register offset, bit index, parent order, or dt-binding ID silently produces incorrect rates or failed peripheral bring-up. `CLK_IGNORE_UNUSED` prevents Linux from disabling shared or firmware-controlled clocks, but overuse can hide missing consumer enables and wastes power. Cross-block parent references assume all relevant provider nodes probe successfully and in a usable order.

## Test Signals
Useful validation is boot probing for every compatible, `/sys/kernel/debug/clk/clk_summary` parent/rate/enabled state, MMC/UART/I2C/SPI/display/GPU/MM functional smoke tests, and suspend/resume checks for clocks marked ignore-unused or shared with AUDCP/DVFS. Binding tests should catch missing compatible strings and clock ID mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/ums512-clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/st/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/st/Makefile

## Purpose
This Makefile unconditionally builds the ST clock generator support objects for the `drivers/clk/st` directory: mux, PLL, frequency synthesizer, and flexgen support.

## Important APIs, Types, And Functions
The only build rule is `obj-y += clkgen-mux.o clkgen-pll.o clkgen-fsyn.o clk-flexgen.o`. It does not define code APIs itself, but it determines that all four legacy OF-declared ST providers are linked into the kernel whenever this directory is selected by the parent build.

## Control Flow
There is no runtime control flow. At build time, Kbuild adds the listed objects to built-in objects.

## State And Persistence
No persistent state is held here. The operational state lives in the compiled C files and their hardware registers.

## Dependencies And Integration Points
The rule integrates with the parent clock Kbuild. Because the objects are `obj-y`, availability is controlled by directory inclusion rather than per-object Kconfig symbols in this file.

## Risks
Since all objects build together, compile failures in any one ST clockgen file can break the whole directory. There is no fine-grained module gating here.

## Test Signals
Build coverage for ST clock support should compile all four objects and verify that the corresponding `CLK_OF_DECLARE` providers are present in the final image.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/st/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/st/clk-flexgen.c -->
# sources/distributed-fs/ceph-client/drivers/clk/st/clk-flexgen.c

## Purpose
This file implements ST flexgen clocks, which combine a parent crossbar mux, pre-divider gate, pre-divider, final divider gate, final divider, and optional asynchronous-mode control into one Linux clock. It supports generic DT-provided output names and several STiH-specific static output lists with critical clock annotations.

## Important APIs, Types, And Functions
`struct flexgen` embeds `clk_mux`, two `clk_gate`s, and two `clk_divider`s. `flexgen_ops` implements enable, disable, is_enabled, parent switching, rate determination, rate recalculation, and rate setting. `clk_register_flexgen()` wires one logical flexgen output to register offsets derived from the output index. `st_of_flexgen_setup()` is the OF entry point registered by `CLK_OF_DECLARE(flexgen, "st,flexgen", ...)`.

## Control Flow
The OF setup maps the parent node registers, gathers parent names, chooses compatible-specific `struct clkgen_data`, allocates `clk_onecell_data`, and registers each non-empty output. Enable turns on both pre and final gates. Disable only turns off the final gate. Rate setting computes a best divider, optionally clears the sync/control bit, then places the division either in the final divider for `div <= 64` or in the pre-divider for larger divisors to avoid duty-cycle problems.

## State And Persistence
Runtime state is held in hardware registers for mux selection, gates, dividers, and sync. The allocated `flexgen`, lock, parent-name array, and onecell data persist after early clock registration. Some outputs are marked `CLK_IS_CRITICAL` because they keep memory, bus interconnect, or CPU paths alive.

## Dependencies And Integration Points
The code depends on the common clock framework primitive ops (`clk_mux_ops`, `clk_gate_ops`, `clk_divider_ops`), OF address mapping, `clock-output-names`, and ST compatible strings such as `st,flexgen-stih410-c0`, `st,flexgen-stih418-d2`, and `st,flexgen-video`. Consumers get clocks through the onecell provider.

## Risks
Index-derived offsets mean output order must match hardware layout exactly. Empty static names skip unused channels, so array position remains semantically important. Error paths do not fully unregister previously registered clocks, which is typical for early clock setup but makes partial failures hard to recover. The control-mode path clears the sync bit but does not restore it in the local function.

## Test Signals
Expected tests include boot-time provider registration, clock summary checks for parent/rate propagation, rate-setting tests above and below divider 64, critical-clock retention, and functional tests of display/audio/peripheral blocks that consume flexgen outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/st/clk-flexgen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/st/clkgen-fsyn.c -->
# sources/distributed-fs/ceph-client/drivers/clk/st/clkgen-fsyn.c

## Purpose
This file implements ST quad frequency synthesizer clock blocks. Each block has a PLL-like parent clock and up to four digital synthesizer channels with programmable `mdiv`, `pe`, `sdiv`, and optional `nsdiv` fields.

## Important APIs, Types, And Functions
`struct clkgen_quadfs_data` describes register fields and hardware polarity for a quadfs variant. `struct st_clk_quadfs_pll` models the block PLL, while `struct st_clk_quadfs_fsynth` models one output channel and caches the last programmed values. PLL ops are in `st_quadfs_pll_c32_ops`; channel ops are in `st_quadfs_ops`. Key math functions are `clk_fs660c32_vco_get_params()`, `clk_fs660c32_vco_get_rate()`, `clk_fs660c32_dig_get_params()`, and `clk_fs660c32_dig_get_rate()`. OF entries register variants `st,quadfs-pll`, `st,quadfs`, `st,quadfs-d0`, `st,quadfs-d2`, and `st,quadfs-d3`.

## Control Flow
`st_of_quadfs_setup()` maps the clock block registers, obtains the parent clock name, creates a private spinlock, registers a hidden PLL clock named from the node, then registers up to four channel clocks. PLL enable handles reset, bandwidth filter, ndiv programming, power-up polarity, and optional lock polling. Channel enable writes cached rate fields, exits standby, handles per-channel reset, and pulses the program-enable bit. `set_rate` computes best parameters and immediately programs them.

## State And Persistence
Hardware registers persist ndiv, standby, reset, enable, mdiv, pe, sdiv, and nsdiv state. The driver caches channel parameters so an enable after suspend or parent enable can reprogram hardware. The lock serializes selected field changes.

## Dependencies And Integration Points
It depends on `clkgen.h` register-field helpers, the common clock framework, OF address mapping, `clock-output-names` fallback for legacy bindings, and static names for known STiH D/C quadfs instances. Downstream display/audio/peripheral clocks consume the onecell channel provider.

## Risks
Frequency synthesis math is sensitive to overflow and rounding, though 64-bit arithmetic is used for the fractional path. Lock polling uses a jiffies timeout with busy wait. Some failures after partial registration leak early clocks. If hardware loses state and cached values were never initialized from a successful set or recalc, enable can restore zero parameters and produce a stopped output.

## Test Signals
Tests should cover valid and invalid PLL ranges, channel rate requests with expected rounded rates, enable/disable standby behavior, suspend/resume restoration, timeout handling when lock status never asserts, and functional consumers such as audio or display clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/st/clkgen-fsyn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/st/clkgen-mux.c -->
# sources/distributed-fs/ceph-client/drivers/clk/st/clkgen-mux.c

## Purpose
This file registers a small ST clock-generator mux provider, currently for the STiH407 A9 mux compatible.

## Important APIs, Types, And Functions
`struct clkgen_mux_data` describes offset, shift, width, lock, clock flags, and mux flags. `clkgen_mux_get_parents()` reads OF parents into an allocated name array. `st_of_clkgen_mux_setup()` maps registers and calls `clk_register_mux()`. `st_of_clkgen_a9_mux_setup()` supplies `stih407_a9_mux_data` and is bound by `CLK_OF_DECLARE(clkgen_a9mux, "st,stih407-clkgen-a9-mux", ...)`.

## Control Flow
Setup first maps a `reg` property on the mux node. For backward compatibility it falls back to the parent node register resource. It registers a mux clock named after the OF node with `CLK_SET_RATE_PARENT`, then publishes it as a simple OF clock provider.

## State And Persistence
The parent selection persists in the mapped hardware mux register. The provider keeps allocated parent-name storage for the registered clock. Shared A9 access uses `clkgen_a9_lock` from `clkgen-pll.c`.

## Dependencies And Integration Points
It depends on OF clock parents, OF address mapping, `clk_register_mux()`, and `clkgen.h` for the external A9 lock declaration. Consumers obtain the mux clock directly from the node.

## Risks
The fallback parent-node mapping must match legacy DT layout or the mux will access the wrong register base. The clock name is `np->name`, so DT node naming changes can affect debug visibility. Error handling unmaps on setup failure but early-registered clocks are not dynamically removed.

## Test Signals
Boot logs should show provider registration. Debugfs/clk summary should show the mux parent, and CPU/A9 rate-change paths should verify parent switching under the shared lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/st/clkgen-mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/st/clkgen-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/st/clkgen-pll.c

## Purpose
This file implements ST PLL providers for PLL3200 C32 and PLL4600 C28 clock generator blocks, including A9 PLL variants and output divider clocks.

## Important APIs, Types, And Functions
`struct clkgen_pll_data` defines field locations for powerdown, lock, ndiv/idf/cp, output dividers, gates, and optional switch-to-PLL control. `struct clkgen_pll` is the registered PLL clock state. `struct stm_pll` carries computed parameters. Core ops include `clkgen_pll_enable()`, `clkgen_pll_disable()`, `recalc_stm_pll3200c32()`, `set_rate_stm_pll3200c32()`, `recalc_stm_pll4600c28()`, and `set_rate_stm_pll4600c28()`. `clkgen_c32_pll_setup()` registers a PLL and its ODF composite outputs for several `CLK_OF_DECLARE` compatibles.

## Control Flow
Setup obtains the parent clock, maps the parent register base, detects critical flags, registers the PLL clock, then registers one or more ODF composite clocks made from divider plus gate primitives. Enable powers the PLL, polls the lock bit with `readl_relaxed_poll_timeout()`, and optionally switches a mux to PLL. Disable optionally switches away then powers down. Rate setting computes valid ndiv/idf and charge-pump values, disables the PLL, writes fields under the lock when present, then re-enables.

## State And Persistence
PLL configuration persists in hardware registers. The driver caches ndiv/idf/cp in `struct clkgen_pll` during set-rate. Global spinlocks protect A9 PLL/mux and C32 ODF updates. Non-A9 C32 ops expose fixed-rate behavior with recalc but no set-rate.

## Dependencies And Integration Points
The file depends on `clkgen.h` field helpers, common clock APIs, OF early registration, and the A9 mux lock shared with `clkgen-mux.c`. Compatible strings include `st,clkgen-pll0`, `st,clkgen-pll1`, `st,stih407-clkgen-plla9`, and `st,stih418-clkgen-plla9`.

## Risks
PLL math has narrow legal ranges and may return zero rates on invalid requests. A missing lock bit or bad field definition can stall enable until timeout. Error paths after PLL registration do not fully unwind. The `err:` path attempts to free `pll_name`, which is a clock-owned name pointer and not an allocation from this function.

## Test Signals
Tests should verify rate calculations for known parent rates, A9 PLL rate transitions, lock timeout failure, ODF gate/divider behavior, critical flag propagation, and boot operation on DTs using both legacy and named-output compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/st/clkgen-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/st/clkgen.h -->
# sources/distributed-fs/ceph-client/drivers/clk/st/clkgen.h

## Purpose
This header provides small register-field helpers shared by the ST clockgen mux, PLL, and frequency-synthesizer drivers.

## Important APIs, Types, And Functions
`struct clkgen_field` holds an offset, mask, and shift. `clkgen_read()` extracts a field from `base + offset`; `clkgen_write()` updates the field using read-modify-write. `CLKGEN_FIELD()` initializes field metadata. `CLKGEN_READ(pll, field)` and `CLKGEN_WRITE(pll, field, val)` assume the caller object has `regs_base` and `data` members.

## Control Flow
There is no standalone runtime flow. Consumers call the inline helpers in their clock ops while holding any required locks.

## State And Persistence
No state is stored in the header. The helpers read and write hardware register state.

## Dependencies And Integration Points
It declares `extern spinlock_t clkgen_a9_lock`, which is defined in `clkgen-pll.c` and used by A9-related mux/PLL paths. It depends on `readl()` and `writel()` being available via including C files.

## Risks
The write helper does not apply `field->mask` to `val` before shifting, so callers must provide an in-range value. The helpers do not lock; correctness depends on callers using the right spinlock around shared registers.

## Test Signals
Coverage comes indirectly from all ST clockgen drivers. Register field tests should focus on preserving unrelated bits and writing expected shifted field values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/st/clkgen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/starfive/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/starfive/Kconfig

## Purpose
This Kconfig file exposes build options for StarFive JH7100 and JH7110 clock drivers and their shared JH71x0 clock core.

## Important APIs, Types, And Functions
It defines `CLK_STARFIVE_JH71X0` as an internal bool, `CLK_STARFIVE_JH7100`, `CLK_STARFIVE_JH7100_AUDIO`, and JH7110 domain options for PLL, SYS, AON, STG, ISP, and VOUT. The SYS option selects `AUXILIARY_BUS`, the shared clock core, the JH7110 reset driver when reset controller support is enabled, and the PLL provider.

## Control Flow
There is no runtime flow. Kconfig dependency resolution controls which C files build and whether domain drivers are built-in or modules.

## State And Persistence
No runtime state. Defaults are tied to `ARCH_STARFIVE`, with `COMPILE_TEST` support for several built-in options.

## Dependencies And Integration Points
JH7100 audio depends on JH7100 core support. JH7110 AON/STG/ISP/VOUT depend on JH7110 SYS, and ISP/VOUT also require `JH71XX_PMU`. These dependencies mirror parent-clock and power-domain dependencies in the driver code.

## Risks
Incorrect dependency selection can build a domain driver without the parent clocks or reset infrastructure it needs. Module-capable child domains depend on built-in SYS support, so boot ordering and module autoloading matter.

## Test Signals
Kconfig tests should cover `ARCH_STARFIVE`, `COMPILE_TEST`, module builds for child domains, and reset-controller enabled/disabled combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/starfive/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/starfive/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/starfive/Makefile

## Purpose
This Makefile maps StarFive clock Kconfig symbols to object files.

## Important APIs, Types, And Functions
It builds `clk-starfive-jh71x0.o` for the shared core, JH7100 system and audio providers, and JH7110 PLL, SYS, AON, STG, ISP, and VOUT providers according to their config symbols.

## Control Flow
No runtime control flow. Kbuild includes the objects selected by configuration.

## State And Persistence
No state. It affects which driver registration code is linked or built as a module.

## Dependencies And Integration Points
The object mapping follows the dependencies in `Kconfig`. Child domain objects rely on exported symbols from the shared JH71x0 core and, for JH7110 resets, the SYS/header helper.

## Risks
If config dependencies and object rules diverge, undefined symbols or missing providers can result. The shared core must be built whenever any table-driven domain uses `starfive_jh71x0_clk_ops()` or `jh71x0_clk_get()`.

## Test Signals
All StarFive configs should be build-tested in built-in and module combinations allowed by Kconfig.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/starfive/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7100-audio.c -->
# sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7100-audio.c

## Purpose
This driver registers the JH7100 audio clock controller, covering ADC/DAC/I2S/PDM/SPDIF/PWMDAC/USB audio-domain clocks.

## Important APIs, Types, And Functions
The clock table `jh7100_audclk_data[]` uses shared `JH71X0_*` macros to encode gate, divider, mux-divider, and inverter clocks. `jh7100_audclk_probe()` allocates `jh71x0_clk_priv`, maps registers, converts internal and external parent IDs into `clk_parent_data`, registers each `clk_hw`, and publishes `jh71x0_clk_get()` as the OF provider. The platform driver is module-capable.

## Control Flow
Probe iterates from `0` to `JH7100_AUDCLK_END`, derives ops from each entry's encoded `max` field via `starfive_jh71x0_clk_ops()`, resolves parents to either local `priv->reg[]` hardware or firmware names such as `audio_src`, `audio_12288`, and `dom7ahb_bus`, then registers the clock.

## State And Persistence
State is in the audio clock control registers, accessed by the shared JH71x0 read-modify-write helpers. The driver-private allocation persists for the module lifetime and stores the base pointer, lock, and per-clock structs.

## Dependencies And Integration Points
It depends on `CLK_STARFIVE_JH7100`, the shared JH71x0 core, and `dt-bindings/clock/starfive-jh7100-audio.h`. External parent clocks come from the main JH7100 clock generator or board inputs.

## Risks
Parent mapping only handles three external IDs even though several external constants are declared for iopad clocks; table entries that use unsupported IDs would register with empty parent data. Audio bit-clock and LR-clock mux/divider setup is sensitive to parent order.

## Test Signals
Probe success, clock summary parent/rate checks, I2S ADC/DAC playback/capture, PDM/SPDIF operation, and module load/unload coverage are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7100-audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7100.c -->
# sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7100.c

## Purpose
This built-in driver registers the main StarFive JH7100 clock generator, including root muxes, PLL fixed-factor outputs, CPU/bus clocks, DDR, video, audio source, GMAC, USB, security, and peripheral clocks.

## Important APIs, Types, And Functions
`jh7100_clk_data[]` is the main clock topology table. `jh7100_clk_get()` customizes provider lookup so IDs below `JH7100_CLK_PLL0_OUT` return register-backed clocks while PLL output IDs return the fixed-factor `priv->pll[]` clocks. `clk_starfive_jh7100_probe()` performs allocation, register mapping, fixed-factor PLL registration, table iteration, and OF provider registration.

## Control Flow
Probe creates three fixed-factor PLL outputs from `osc_sys` or `pll2_refclk`, then registers all register-backed clocks before the first PLL ID. Parent resolution handles local clocks, PLL outputs, and firmware names for `osc_sys`, `osc_aud`, `gmac_rmii_ref`, and `gmac_gr_mii_rxclk`.

## State And Persistence
Clock state persists in one register per clock index under the shared JH71x0 register format. PLLs are modeled as fixed factors instead of programmable PLLs in this driver. Several CPU, DDR, and interconnect clocks are marked `CLK_IS_CRITICAL` to prevent accidental disable.

## Dependencies And Integration Points
It depends on `dt-bindings/clock/starfive-jh7100.h`, the shared JH71x0 core, and board-provided external clocks. Consumers use the onecell provider exposed by compatible `starfive,jh7100-clkgen`.

## Risks
The loop only registers clocks below `JH7100_CLK_PLL0_OUT`; binding ID ordering is therefore a hard contract. Fixed-factor PLL modeling assumes boot firmware configured PLLs as expected. GMAC mux/inverter paths are parent-order sensitive.

## Test Signals
Boot on JH7100 should show all critical roots enabled. Useful tests include CPU/bus rate summaries, DDR stability, SDIO, USB, GMAC RGMII/RMII modes, display/video, and audio-source consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110-aon.c -->
# sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110-aon.c

## Purpose
This module registers the JH7110 always-on clock controller for GMAC0, OTPC, RTC, and AON APB functional clocks.

## Important APIs, Types, And Functions
`jh7110_aonclk_data[]` encodes the AON clock topology. `jh7110_aoncrg_probe()` registers each clock through the shared JH71x0 core and then calls `jh7110_reset_controller_register(priv, "rst-aon", 1)` to expose the associated reset controller.

## Control Flow
Probe maps registers, registers local clocks with parent data resolved to either local hardware or firmware names (`osc`, `gmac0_rmii_refin`, `gmac0_rgmii_rxin`, `stg_axiahb`, `apb_bus`, `gmac0_gtxclk`, `rtc_osc`), adds the OF clock provider, then registers reset auxiliary device `rst-aon`.

## State And Persistence
Hardware register state controls gates, muxes, divider values, and inversion for GMAC and RTC paths. The module retains `jh71x0_clk_priv` state and the shared read-modify-write lock.

## Dependencies And Integration Points
It depends on JH7110 SYS clocks for several firmware-named parents and on the reset helper exported by the SYS driver. It integrates with `dt-bindings/clock/starfive,jh7110-crg.h` and compatible `starfive,jh7110-aoncrg`.

## Risks
Because it is a module depending on SYS, loading before parent clocks or reset helper availability would fail. GMAC0 TX/RX inversion and RMII/RGMII parent selection are hardware-mode sensitive.

## Test Signals
GMAC0 operation in RGMII and RMII modes, RTC 32k selection, reset-controller registration, and module probe/remove tests are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110-aon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110-isp.c -->
# sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110-isp.c

## Purpose
This module registers the JH7110 ISP clock controller for VIN/MIPI/ISP wrapper clocks and coordinates required top-domain clocks, resets, and runtime PM.

## Important APIs, Types, And Functions
`jh7110_ispclk_data[]` describes local clocks. `jh7110_isp_top_clks[]` names required top SYS clocks `isp_top_core` and `isp_top_axi`. `jh7110_isp_top_rst_init()` obtains shared reset controls and deasserts them. Runtime PM callbacks disable and enable the top clocks. `jh7110_ispcrg_probe()` performs all registration and reset setup.

## Control Flow
Probe allocates clock and top-clock state, maps registers, gets top clocks, enables runtime PM and powers the domain, deasserts shared top resets, registers local clocks with local or firmware parents, adds the OF provider, and registers reset auxiliary device `rst-isp`. Error handling unwinds runtime PM.

## State And Persistence
State includes hardware clock registers, runtime PM state, prepared/enabled top clocks, reset deassertion state, and driver-private top-clock metadata stored with `dev_set_drvdata()`.

## Dependencies And Integration Points
It depends on JH7110 SYS and PMU/power-domain support. Parent firmware names include `isp_top_core`, `isp_top_axi`, `noc_bus_isp_axi`, and `dvp_clk`. It uses shared JH71x0 operations and the JH7110 reset auxiliary-device helper.

## Risks
`pm_runtime_get_sync()` failure returns without disabling runtime PM, which can leave PM enabled on probe failure. Parent-clock and power-domain availability are mandatory. Pixel-path muxes and inversion depend on correct external DVP/MIPI wiring.

## Test Signals
Probe under active power domain, runtime suspend/resume, reset deassertion, VIN/MIPI capture, ISP wrapper clocks, and error-injection around missing top clocks or resets are important validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110-isp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110-pll.c

## Purpose
This built-in driver registers the programmable PLL outputs for JH7110 PLL0, PLL1, and PLL2 using syscon/regmap registers. It supports a fixed set of legal preset frequencies.

## Important APIs, Types, And Functions
`struct jh7110_pll_preset` holds frequency, fractional value, fbdiv, prediv, postdiv1, and integer/fraction mode. `struct jh7110_pll_info` describes each PLL's offsets, masks, and shifts. `jh7110_pll_recalc_rate()`, `jh7110_pll_determine_rate()`, and `jh7110_pll_set_rate()` implement `jh7110_pll_ops`. `jh7110_pll_probe()` obtains the parent syscon regmap, registers three `clk_hw`s, and adds a custom OF provider.

## Control Flow
Rate recalculation reads all relevant fields, interprets integer mode when both DACPD and DSMPD are set, fraction mode when both are clear, and computes `parent * (fbdiv + frac / 2^24) / prediv / 2^postdiv1`. Determine-rate chooses the highest preset not exceeding the request, but only when the parent is the expected 24 MHz oscillator. Set-rate requires an exact preset frequency and writes mode, prediv, fbdiv, optional frac, and postdiv fields.

## State And Persistence
PLL configuration persists in syscon registers shared with the broader system controller. The driver keeps only static metadata and `regmap` access state. Debugfs can expose decoded register fields per PLL.

## Dependencies And Integration Points
It depends on `dt-bindings/clock/starfive,jh7110-crg.h`, an OF parent syscon node, and a 24 MHz input clock. The SYS clock driver consumes these PLL outputs by firmware name when available.

## Risks
Only preset rates are supported; arbitrary clock framework requests fail. Parent rates other than 24 MHz make determine-rate fall back to current hardware rate and make set-rate invalid. There is no explicit PLL lock wait after programming in this file. Division by zero is possible if hardware reports prediv zero, though valid presets avoid it.

## Test Signals
Validate each preset rate, rejected non-preset rates, debugfs decoded fields, SYS CPU-root notifier behavior during PLL0 changes, and boot operation when SYS uses these PLL outputs instead of fixed-factor fallbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110-stg.c -->
# sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110-stg.c

## Purpose
This module registers JH7110 System-Top-Group clocks for HIFI4, USB, PCIe, security, matrix/interconnect, E24, and DMA-related domains.

## Important APIs, Types, And Functions
`jh7110_stgclk_data[]` encodes all local STG gates/dividers. `jh7110_stgcrg_probe()` maps registers, registers each clock through the shared JH71x0 core, adds the OF provider, and registers reset auxiliary device `rst-stg`.

## Control Flow
Probe resolves local parents or firmware-named external parents from a compact `fw_name[]` array (`osc`, `hifi4_core`, `stg_axiahb`, `usb_125m`, `cpu_bus`, `hifi4_axi`, `nocstg_bus`, `apb_bus`). After successful clock provider registration it exposes reset ID 2.

## State And Persistence
State lives in STG clock registers and the allocated `jh71x0_clk_priv`. Several matrix clocks are `CLK_IS_CRITICAL` to keep interconnect paths running.

## Dependencies And Integration Points
It depends on the SYS clock controller for most top-level parents and reset helper export. Consumers include USB, PCIe, security, HIFI4, E24, and DMA drivers.

## Risks
Wrong external parent names break probe deferral or produce orphan clocks. Critical matrix clocks must remain enabled; changing their flags can hang bus access. Module ordering depends on SYS being available.

## Test Signals
USB and PCIe bring-up, security DMA clocks, reset-controller registration, critical clock retention, and module probe with all firmware parents available are primary checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110-stg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110-sys.c -->
# sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110-sys.c

## Purpose
This built-in driver registers the main JH7110 system clock controller and reset auxiliary device. It covers CPU, bus, DDR, GPU, ISP top, audio, VOUT top, codec, QSPI, SDIO, USB/STG roots, GMAC, APB peripherals, and audio serial clocks.

## Important APIs, Types, And Functions
`jh7110_sysclk_data[]` is the main topology table. `jh7110_reset_controller_register()` creates an auxiliary reset device backed by the same register base and is exported for child clock domains. `jh7110_pll0_clk_notifier_cb()` temporarily switches `cpu_root` to `osc` during PLL0 rate changes. `jh7110_syscrg_probe()` registers clocks, optional fixed-factor PLL fallbacks, OF provider, and reset device `rst-sys`.

## Control Flow
Probe maps registers, tries to get real `pll*_out` clocks, and falls back to fixed factors if absent. If PLL0 exists it registers a notifier. It iterates through all SYS clock IDs, resolving parents to local clocks, external firmware names, real PLL names, or fallback PLL hardware. After registration it adds the OF provider and registers reset ID 0.

## State And Persistence
Clock state is in one register per clock index. Driver state tracks the register base, read-modify-write lock, fallback PLLs, original CPU-root parent during PLL0 transitions, and notifier block. Reset auxiliary devices share the same base.

## Dependencies And Integration Points
It depends on the shared JH71x0 core, the JH7110 PLL provider when enabled, auxiliary bus, reset framework, and board-provided external clocks. Child domains AON/STG/ISP/VOUT depend on its parent clocks and exported reset helper.

## Risks
PLL0 notifier obtains `osc` with `clk_get()` but does not check for an error before `clk_set_parent()`. A registered PLL0 notifier is not explicitly unregistered, relying on built-in lifetime. Parent mapping is large and table-driven, so binding ID drift is high impact. Fallback fixed-factor PLLs may hide missing PLL provider configuration.

## Test Signals
Boot with real PLL provider and fallback PLLs, CPU frequency changes involving PLL0, child-domain probes, reset auxiliary-device binding, GMAC modes, audio serial clocks, SDIO/QSPI, and critical interconnect clocks should be validated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110-sys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110-vout.c -->
# sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110-vout.c

## Purpose
This module registers the JH7110 video-output clock controller for display controller, DSI, MIPI TX DPHY, HDMI, and APB clocks, with runtime PM and top reset handling.

## Important APIs, Types, And Functions
`jh7110_voutclk_data[]` encodes local clocks. `jh7110_vout_top_clks[]` names required top clocks `vout_src` and `vout_top_ahb`. `jh7110_vout_top_rst_init()` deasserts the shared top reset. Runtime PM callbacks gate and ungate top clocks. `jh7110_voutcrg_probe()` registers clocks and reset auxiliary device `rst-vo`.

## Control Flow
Probe allocates private and top-clock state, maps registers, gets top clocks, enables runtime PM using `pm_runtime_resume_and_get()`, deasserts top reset, registers each local clock with local or firmware parent data, adds the OF provider, and registers reset ID 4. Remove drops runtime PM usage and disables PM.

## State And Persistence
State includes display clock registers, runtime PM power state, enabled top clocks, shared reset state, and `jh7110_top_sysclk` metadata.

## Dependencies And Integration Points
It depends on SYS top clocks, PMU/power-domain support, resets, and external firmware parents including `vout_top_axi`, `vout_top_hdmitx0_mclk`, `i2stx0_bclk`, and `hdmitx0_pixelclk`. Consumers are DRM/display, DSI, HDMI, and DPHY drivers.

## Risks
Display pixel clock parent order is mode-sensitive. Missing top clocks or power-domain support prevents probe. Error unwinding handles PM state, but reset deassertion is not reasserted on later failure. HDMI pixel clock is an external dependency not produced locally.

## Test Signals
Runtime suspend/resume, display modes through DC8200, DSI and HDMI output, top reset behavior, and missing-parent probe deferral are important tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110-vout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110.h -->
# sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110.h

## Purpose
This header shares JH7110-specific helpers and data structures between SYS, AON, STG, ISP, and VOUT clock drivers.

## Important APIs, Types, And Functions
`struct jh7110_top_sysclk` stores a bulk-clock array and count for ISP/VOUT top clocks. `jh7110_reset_controller_register()` is declared for child domains to create reset-controller auxiliary devices.

## Control Flow
There is no standalone flow. Implementations call the reset helper after clock provider registration, and ISP/VOUT use the top-clock struct from runtime PM callbacks.

## State And Persistence
The header defines only types and declarations. Persistent state is allocated by the individual domain drivers.

## Dependencies And Integration Points
It includes `clk-starfive-jh71x0.h`, so all users share the common register-backed clock structures. The reset helper implementation lives in `clk-starfive-jh7110-sys.c` and is exported for module users.

## Risks
Because child modules call a helper implemented in SYS, Kconfig and module dependencies must ensure symbol availability. Changes to `jh7110_top_sysclk` affect ISP and VOUT PM callbacks together.

## Test Signals
Build tests with AON/STG/ISP/VOUT as modules and SYS built-in should verify exported symbol linkage and PM callback data layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh7110.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh71x0.c -->
# sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh71x0.c

## Purpose
This file is the shared implementation for StarFive JH71x0 register-backed clocks. It provides common ops for gates, dividers, fractional dividers, muxes, mux-dividers, gate-mux-dividers, and inverters.

## Important APIs, Types, And Functions
`starfive_jh71x0_clk_ops(max)` selects a `clk_ops` table based on encoded capability bits in the per-clock `max` field. `jh71x0_clk_get()` is the generic OF onecell lookup. Internal helpers include `jh71x0_clk_reg_get()`, `jh71x0_clk_reg_rmw()`, enable/disable/is_enabled, integer and fractional rate operations, parent get/set, phase get/set, and debugfs register export.

## Control Flow
Domain drivers allocate `struct jh71x0_clk_priv` with a flexible `reg[]` array, fill each `jh71x0_clk`, and register it with ops selected by `max`. At runtime, clock framework callbacks read or update `base + 4 * idx`. Read-modify-write operations are serialized by `priv->rmw_lock`.

## State And Persistence
Persistent state is one 32-bit hardware register per clock. The register format uses bit 31 enable, bit 30 invert, bits 27:24 mux, and bits 23:0 divider or fractional divider data. Driver state stores the mapped base, lock, optional PLL fallback pointers, notifier state, and per-clock max divider.

## Dependencies And Integration Points
It depends on Linux common clock APIs, debugfs, MMIO access, and the macros/types in `clk-starfive-jh71x0.h`. It exports symbols for all StarFive JH7100/JH7110 domain drivers.

## Risks
`starfive_jh71x0_clk_ops()` infers behavior from `max`; a wrong macro in a table can select the wrong ops. Divider recalc returns zero for a register divider of zero, so reset-default hardware must be initialized by firmware or set before use. Fractional arithmetic multiplies parent rates by 100 and should be checked for overflow on future higher-rate parents.

## Test Signals
Unit-level signals include ops selection for every macro family, enable/rate/parent/phase callbacks, concurrent RMW safety, debugfs register visibility, and full-domain boot tests for JH7100 and JH7110.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh71x0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh71x0.h -->
# sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh71x0.h

## Purpose
This header defines the shared JH71x0 clock register format, declarative table macros, and common private structures used by StarFive clock domain drivers.

## Important APIs, Types, And Functions
It defines register masks for enable, invert, mux, integer divider, and fractional divider fields. `struct jh71x0_clk_data` is the compact table entry used by SoC files. Macros such as `JH71X0_GATE`, `JH71X0__DIV`, `JH71X0_GDIV`, `JH71X0_FDIV`, `JH71X0__MUX`, `JH71X0_GMUX`, `JH71X0_MDIV`, `JH71X0__GMD`, and `JH71X0__INV` encode clock capabilities into `max`. `struct jh71x0_clk_priv` stores shared runtime state.

## Control Flow
The header itself has no flow. Its macro output drives `starfive_jh71x0_clk_ops()` in the implementation file and parent resolution loops in each SoC/domain driver.

## State And Persistence
No state is stored by the header, but it defines the state layout used by all domain drivers: MMIO base, RMW lock, optional original CPU-root clock, PLL notifier, fallback PLL hardware, and one `jh71x0_clk` per register.

## Dependencies And Integration Points
It integrates all StarFive JH71x0 clock drivers with the Linux common clock framework. The flexible array uses `__counted_by(num_reg)`.

## Risks
The encoded `max` field has dual meaning: capability bits and maximum divider. Mistakes in macros or table values can select incorrect ops or divider limits. Parent arrays are fixed at four entries, so hardware with more parents would need structural changes.

## Test Signals
Build-time coverage should compile all macro users. Runtime tests should check that each macro family maps to expected operations and that max divider limits are enforced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/starfive/clk-starfive-jh71x0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/stm32/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/stm32/Kconfig

## Purpose
This Kconfig file controls common STM32MP clock-driver availability for STM32MP13, STM32MP15, STM32MP21, and STM32MP25 families.

## Important APIs, Types, And Functions
`COMMON_CLK_STM32MP` is a menuconfig depending on `ARCH_STM32 || COMPILE_TEST` and selecting `RESET_CONTROLLER`. Family-specific bools enable `COMMON_CLK_STM32MP135`, `COMMON_CLK_STM32MP157`, `COMMON_CLK_STM32MP215`, and `COMMON_CLK_STM32MP257` with ARM/ARM64 dependencies.

## Control Flow
No runtime control flow. Kconfig selects which STM32MP clock and reset objects the Makefile builds.

## State And Persistence
No runtime state. Defaults mostly follow `ARCH_STM32`; STM32MP215 defaults to `y` when its dependencies are met.

## Dependencies And Integration Points
The selections coordinate with `drivers/clk/stm32/Makefile`, which builds SoC-specific clock files, shared core files, and reset support. `RESET_CONTROLLER` is selected at the menu level because these clock drivers include reset-provider functionality.

## Risks
Architecture dependencies must match actual SoC support. Enabling family drivers under `COMPILE_TEST` can expose missing include or type dependencies across ARM and ARM64.

## Test Signals
Kconfig build matrices should include ARCH_STM32, ARM-only, ARM64-only, and COMPILE_TEST combinations for every family option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/stm32/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/stm32/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/stm32/Makefile

## Purpose
This Makefile maps STM32MP clock Kconfig symbols to their object files.

## Important APIs, Types, And Functions
It builds `clk-stm32mp13.o`, `clk-stm32mp1.o`, `clk-stm32mp21.o`, or `clk-stm32mp25.o` depending on the selected SoC family. Newer families also build `clk-stm32-core.o`; all listed families build `reset-stm32.o`.

## Control Flow
No runtime flow. Kbuild uses the selected symbols to include the correct object set.

## State And Persistence
No state. The rule controls which drivers and reset support are linked.

## Dependencies And Integration Points
It integrates with `stm32/Kconfig`. The object combinations show that MP13, MP21, and MP25 use shared core support, while MP15 uses the older `clk-stm32mp1.o` plus reset object.

## Risks
Changing object groupings can break shared-core linkage or reset provider availability. Build tests are needed because shared object dependencies differ by family.

## Test Signals
Build each `COMMON_CLK_STM32MP*` option individually and in combinations allowed by Kconfig, verifying reset support links successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/stm32/Makefile -->
