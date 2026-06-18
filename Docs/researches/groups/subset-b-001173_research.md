# subset-b-001173 clock-driver research

This grouped report covers the requested source-tree subset under `sources/distributed-fs/ceph-client/drivers/clk/`. Each file section is bounded by the required markers so it can be split into the mapped per-file research documents without losing the source path.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-s10.c -->
# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-s10.c

## Purpose
This file is the Stratix10 clock manager platform driver. It describes the Stratix10 clock tree in static tables and registers PLL, peripheral counter, peripheral core, and gate clocks with the Linux common clock framework (CCF). It is bound from Device Tree via `intel,stratix10-clkmgr` and exposes clocks through an `of_clk_hw_onecell_get` provider.

## Important APIs, Types, And Functions
The static topology data uses `struct clk_parent_data`, `struct stratix10_pll_clock`, `struct stratix10_perip_c_clock`, `struct stratix10_perip_cnt_clock`, and `struct stratix10_gate_clock` from `stratix10-clk.h`. The provider-side storage is `struct stratix10_clock_data`, which combines the register base with a flexible `clk_hw_onecell_data` array.

The local registration helpers are `s10_clk_register_pll()`, `s10_clk_register_c_perip()`, `s10_clk_register_cnt_perip()`, and `s10_clk_register_gate()`. Each iterates a static table, calls the matching lower-level registration helper (`s10_register_pll()`, `s10_register_periph()`, `s10_register_cnt_periph()`, or `s10_register_gate()`), logs failures, and stores successful `clk_hw` pointers by dt-binding clock ID. `s10_clkmgr_init()` maps registers, allocates the onecell data, initializes all slots to `ERR_PTR(-ENOENT)`, registers the tables, and installs the OF provider.

## Control Flow
Module initialization uses `core_initcall(s10_clk_init)` to register a platform driver early. Probe delegates directly to `s10_clkmgr_init()`. The init path maps MMIO resource 0, allocates `STRATIX10_NUM_CLKS` hardware slots, fills absent entries with `-ENOENT`, then registers clocks in dependency order: PLLs, core peripheral clocks, counter peripheral clocks, and gates.

The clock topology has explicit parent groups: PLL input muxes from oscillator/internal/free clocks, counter muxes from main/peripheral PLLs and boot sources, free-clock muxes for MPU/NOC/peripherals, and final functional gate clocks for MPU, L4, CoreSight, EMAC, SDMMC, USB, SPI, NAND, GPIO debounce, and PSI references.

## State And Persistence
Runtime state is devm-managed and exists for the lifetime of the platform device. Persistent hardware state is in the clock manager MMIO registers; the driver reads or modifies them indirectly through the lower-level Stratix10 helpers. The provider array intentionally records failed or missing clocks as `ERR_PTR(-ENOENT)` so consumers get deterministic missing-clock behavior.

## Dependencies And Integration Points
The file depends on `dt-bindings/clock/stratix10-clock.h` for clock IDs and on `stratix10-clk.h` for record layouts and registration helper prototypes. It integrates with the platform bus, Device Tree matching, MMIO resource mapping, and CCF onecell lookup. Parent names such as `osc1`, `cb-intosc-hs-div2-clk`, and `f2s-free-clk` must match firmware/Device Tree clock names.

## Risks
Registration helper failures are logged but do not abort initialization, so a partially registered provider can be exposed. Static table ID mismatches with `STRATIX10_NUM_CLKS` or dt-bindings would silently put clocks in wrong onecell slots. Critical clocks are marked selectively; missing a critical flag on boot-required fabric clocks could allow late unused-clock disabling to break the system. Many mux and bypass register offsets are literal constants, so hardware revision drift is risky.

## Test Signals
Useful tests include booting a Stratix10 DT with `intel,stratix10-clkmgr`, verifying `/sys/kernel/debug/clk/clk_summary`, checking that consumers can resolve all binding IDs, and exercising rate/parent changes for MPU, NOC, EMAC, SDMMC, and GPIO debounce clocks. Negative tests should confirm missing optional clocks return `-ENOENT` rather than stale pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-s10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk.c

## Purpose
This tiny file declares early OF clock providers for legacy SoCFPGA and Arria10 clock nodes. It is the Device Tree binding dispatch layer that connects compatible strings such as `altr,socfpga-pll-clock` and `altr,socfpga-a10-gate-clk` to the actual initialization routines declared in `clk.h`.

## Important APIs, Types, And Functions
The file uses `CLK_OF_DECLARE()` for six providers: `socfpga_pll_init`, `socfpga_periph_init`, `socfpga_gate_init`, `socfpga_a10_pll_init`, `socfpga_a10_periph_init`, and `socfpga_a10_gate_init`. There are no local data structures or runtime functions beyond these declarations.

## Control Flow
At early boot, the OF clock framework scans matching clock nodes and calls the registered init function for each compatible. The actual parsing, register mapping, and clock registration live in other SoCFPGA clock files; this file only wires compatible strings to those entry points.

## State And Persistence
No local state is stored. Persistent effects occur in the called init routines, which register clocks and may map global clock-manager bases.

## Dependencies And Integration Points
It depends on `<linux/of.h>` and the SoCFPGA-local declarations in `clk.h`. It integrates with CCF early clock setup rather than a platform driver probe path.

## Risks
Compatible string typos here prevent entire legacy SoCFPGA clock classes from registering. Because this is early boot code, failures may surface as downstream consumer probe deferrals or timer/console breakage rather than direct errors in this file.

## Test Signals
Boot tests on legacy SoCFPGA and Arria10 DTBs should show that all compatible clock nodes call their expected init routines. Static checks can verify the compatible strings match binding documents and DTS usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk.h -->
# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk.h

## Purpose
This header declares the shared legacy SoCFPGA clock-manager interface. It defines common register offsets, helper macros, global MMIO base symbols, init function prototypes, and simple wrapper structures for PLL, gate, and peripheral clocks.

## Important APIs, Types, And Functions
Constants include `CLKMGR_CTRL`, `CLKMGR_BYPASS`, `CLKMGR_DBCTRL`, `CLKMGR_L4SRC`, `CLKMGR_PERPLL_SRC`, and `SOCFPGA_MAX_PARENTS`. `SYSMGR_SDMMC_CTRL_SET()` and `SYSMGR_SDMMC_CTRL_SET_AS10()` encode SDMMC sample/drive-select fields for system-manager integration.

The header exposes `clk_mgr_base_addr` and `clk_mgr_a10_base_addr`, plus init prototypes for standard and Arria10 PLL, peripheral, and gate clocks. `struct socfpga_pll` wraps `struct clk_gate`; `struct socfpga_gate_clk` and `struct socfpga_periph_clk` carry parent name, fixed divider, optional divider/bypass registers, field widths/shifts, and for gates a `regmap *sys_mgr_base_addr`.

## Control Flow
No executable flow exists in the header. The data structures are consumed by implementation files that parse Device Tree, map registers, construct `clk_hw` instances, and install operations for rate and gate control.

## State And Persistence
The global MMIO bases represent process-wide state set during clock-manager initialization. The per-clock structs store register pointers and bitfield metadata but not persistent policy. Hardware registers hold the effective divider, bypass, and gate state.

## Dependencies And Integration Points
The header depends on `<linux/clk-provider.h>` and implicitly on CCF, MMIO, and regmap users in implementation files. It is shared by legacy SoCFPGA clock declarations in `clk.c` and lower-level clock implementations elsewhere in the directory.

## Risks
Global base-address state can be fragile if multiple compatible controllers or deferred init paths are introduced. Register field metadata is stored as raw offsets/pointers, so incorrect DT parsing or SoC variant selection can lead to wrong MMIO writes. The `streq()` macro hides raw `strcmp()` semantics and assumes non-NULL strings.

## Test Signals
Static build coverage should compile both legacy and Arria10 paths. Runtime tests should validate SDMMC timing register encodings, bypass transitions, and that all legacy OF-declared nodes resolve parent clocks correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/stratix10-clk.h -->
# sources/distributed-fs/ceph-client/drivers/clk/socfpga/stratix10-clk.h

## Purpose
This header defines the hardware description records and registration API used by Stratix10-family, Agilex, N5X, and Agilex5 clock providers. It standardizes how SoC-specific topology tables describe PLLs, peripheral counters, gates, mux parents, divider fields, bypass controls, and onecell provider storage.

## Important APIs, Types, And Functions
`struct stratix10_clock_data` stores the MMIO base plus a trailing `clk_hw_onecell_data`. The clock record structs are `stratix10_pll_clock`, `stratix10_perip_c_clock`, `n5x_perip_c_clock`, `stratix10_perip_cnt_clock`, `stratix10_gate_clock`, `agilex5_pll_clock`, `agilex5_perip_cnt_clock`, and `agilex5_gate_clock`.

The prototypes expose registration helpers: `s10_register_pll()`, `agilex_register_pll()`, `n5x_register_pll()`, `agilex5_register_pll()`, `s10_register_periph()`, `n5x_register_periph()`, `s10_register_cnt_periph()`, `agilex5_register_cnt_periph()`, `s10_register_gate()`, `agilex_register_gate()`, and `agilex5_register_gate()`.

## Control Flow
There is no executable code. SoC drivers populate const arrays of these structures, then call the matching helper to allocate or register `clk_hw` implementations. The helpers interpret offsets, shifts, parent data, and flags according to the clock class.

## State And Persistence
The record structs are static topology descriptions. Runtime state is in registered `clk_hw` objects and in hardware registers addressed relative to the provider base. The onecell array stores exported clock handles by dt-binding ID.

## Dependencies And Integration Points
This header integrates SoC-specific clock-table files with shared implementation code in the SoCFPGA clock subsystem. It depends on CCF types, firmware-node parent data, and dt-binding IDs in individual providers.

## Risks
Many structs are similar but not interchangeable; using the wrong registration helper for a table silently misinterprets fields. `parent_name`, `parent_names`, `parent_data`, and `parent_hws` variants must match the helper and kernel CCF registration API. Array IDs must remain synchronized with DT bindings and the allocated onecell size.

## Test Signals
Compile coverage across Stratix10, Agilex, N5X, and Agilex5 configurations is important. Runtime validation should inspect `clk_summary`, parent names, divider rates, and gate states for each SoC family after boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/stratix10-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/sophgo/Kconfig

## Purpose
This Kconfig file exposes Sophgo clock-controller drivers for CV1800/CV18xx, SG2042, and SG2044 families. It declares build-time feature switches and dependency relationships between PLL, clock-generator, and subsystem gate drivers.

## Important APIs, Types, And Functions
The symbols are `CLK_SOPHGO_CV1800`, `CLK_SOPHGO_SG2042_PLL`, `CLK_SOPHGO_SG2042_CLKGEN`, `CLK_SOPHGO_SG2042_RPGATE`, `CLK_SOPHGO_SG2044`, and `CLK_SOPHGO_SG2044_PLL`. SG2042 CLKGEN depends on SG2042 PLL; SG2042 RPGATE depends on SG2042 CLKGEN. SG2044 PLL selects `MFD_SYSCON` and `REGMAP_MMIO` because it uses a parent syscon regmap.

## Control Flow
Kconfig controls which objects the Makefile builds. There is no runtime code, but dependency edges enforce that downstream SG2042 providers are not built without their upstream clock providers.

## State And Persistence
No runtime state is stored. The selected symbols determine module/built-in availability and therefore whether matching Device Tree nodes can bind.

## Dependencies And Integration Points
All symbols depend on `ARCH_SOPHGO || COMPILE_TEST` except chained SG2042 subdrivers, which depend on the upstream Sophgo clock symbols. The file integrates with `drivers/clk/sophgo/Makefile` and Device Tree-compatible platform drivers in the same directory.

## Risks
If a downstream symbol lacks a dependency on its upstream clock provider, consumers may get unresolved parent clocks at runtime. The SG2044 help text has a typo (`mulitple`) but the functional dependency is correct. Modular combinations need testing because these are tristate symbols.

## Test Signals
Run `allyesconfig`, `allmodconfig`, and `COMPILE_TEST` builds. Runtime tests should verify module autoload and probe ordering for SG2042 PLL -> CLKGEN -> RPGATE and SG2044 PLL plus main clock controller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/sophgo/Makefile

## Purpose
This Makefile maps Sophgo Kconfig symbols to clock-driver objects. It also composes the CV1800 multi-object module from top-level, common, IP, and PLL implementation files.

## Important APIs, Types, And Functions
`clk-sophgo-cv1800.o` is built from `clk-cv1800.o`, `clk-cv18xx-common.o`, `clk-cv18xx-ip.o`, and `clk-cv18xx-pll.o`. SG2042 and SG2044 drivers are separate objects: `clk-sg2042-clkgen.o`, `clk-sg2042-pll.o`, `clk-sg2042-rpgate.o`, `clk-sg2044.o`, and `clk-sg2044-pll.o`.

## Control Flow
The kernel build system includes object files when the corresponding config symbol is enabled. CV1800 helper objects are linked only as part of the aggregate module.

## State And Persistence
No runtime state exists. Build output shape affects module names, symbol linkage, and which platform drivers are available.

## Dependencies And Integration Points
This file integrates directly with `Kconfig`, module metadata in each `.c` file, and the kernel build system's `obj-$(CONFIG_...)` and `foo-y` conventions.

## Risks
Leaving a helper object out of `clk-sophgo-cv1800-y` causes unresolved symbols for exported `clk_ops` or common helpers. Splitting SG2042 into independent objects means dependency mistakes in Kconfig can become runtime parent-clock failures.

## Test Signals
Build CV1800 as built-in and module, build SG2042 symbols in chained combinations, and build SG2044 main and PLL controllers. `modinfo` should show expected module descriptions from the source files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv1800.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv1800.c

## Purpose
This is the top-level CV1800/CV1810/SG2000 clock controller driver. It declares the complete clock topology for the CV18xx family using the reusable CV18xx PLL/IP clock classes, performs SoC-specific pre-initialization, registers each `clk_hw`, and publishes an OF onecell provider.

## Important APIs, Types, And Functions
Local descriptor types are `struct cv1800_clk_desc` and `struct cv1800_clk_ctrl`. The descriptor selects the onecell table and optional `pre_init()` hook for each compatible. `CV1800_DIV_FLAG` standardizes one-based, round-closest dividers. The file uses clock-construction macros from `clk-cv18xx-ip.h` and `clk-cv18xx-pll.h`: `CV1800_INTEGRAL_PLL`, `CV1800_FACTIONAL_PLL`, `CV1800_GATE`, `CV1800_DIV`, `CV1800_BYPASS_DIV`, `CV1800_FIXED_DIV`, `CV1800_BYPASS_FIXED_DIV`, `CV1800_MUX`, `CV1800_BYPASS_MUX`, `CV1800_MMUX`, and `CV1800_ACLK`.

Key functions are `cv18xx_clk_disable_auto_pd()`, `cv18xx_clk_disable_a53()`, `cv1800_pre_init()`, `cv1810_pre_init()`, `sg2000_pre_init()`, `cv1800_clk_init_ctrl()`, and `cv1800_clk_probe()`. Matching compatibles are `sophgo,cv1800-clk`, `sophgo,cv1800b-clk`, `sophgo,cv1810-clk`, `sophgo,cv1812h-clk`, and `sophgo,sg2000-clk`.

## Control Flow
Probe maps MMIO resource 0, retrieves match data, allocates a controller, runs descriptor-specific pre-init, then calls `cv1800_clk_init_ctrl()`. Registration walks the selected `clk_hw_onecell_data` array, skips NULL entries, initializes each clock's shared base and lock through `hw_to_cv1800_clk_common()`, and registers the hardware object with `devm_clk_hw_register()`. Finally it installs `devm_of_clk_add_hw_provider()`.

The topology begins with oscillator parents and PLLs: FPLL and MIPIMPLL as integral PLLs, and MPLL/TPLL/A0PLL/DISPPLL/CAM0PLL/CAM1PLL as fractional PLLs with synthesizer controls. Downstream clocks define TPU, AXI4/AXI6, timers, RTC, storage, GPIO, Ethernet, audio, SDMA, SPI, UART, I2C, USB, VIP, camera outputs, video codec, PWM, C906, and A53 clocks. `cv1800_hw_clks` is smaller and excludes unsupported `CLK_DISP_SRC_VIP`; `cv1810_hw_clks` includes it and is reused for SG2000.

## State And Persistence
The clock tree is represented by static global `clk_hw` objects. Probe writes runtime state into each `cv1800_clk_common` (`base` and shared spinlock pointer). Hardware state lives in clock-enable, divider, mux, bypass, PLL, and synthesizer registers. Pre-init permanently adjusts hardware state for the running boot: CV1800 disables unsupported display source VIP, CV1800/CV1810 force A53-related bypass to avoid hangs on variants where A53 is unused, and all variants disable PLL auto power-down fields.

## Dependencies And Integration Points
The file depends on CV1800 register offsets and clock ID limits from `clk-cv1800.h`, common bit helpers from `clk-cv18xx-common.h`, IP clock ops from `clk-cv18xx-ip.h`, PLL ops from `clk-cv18xx-pll.h`, and dt-bindings in `sophgo,cv1800.h`. It integrates with platform probing, Device Tree match data, CCF parent-data resolution, and downstream IP consumers requesting binding IDs.

## Risks
This file is table-heavy; a wrong register, bit shift, parent list, or onecell index can break a whole subsystem without compile-time detection. Some clocks are marked `CLK_IS_CRITICAL` or `CLK_IGNORE_UNUSED`; those policy choices need hardware validation because overuse hides unused-clock bugs while underuse can hang boot. The comment on A53 states bypass must not be disabled on CV180x/CV181x or the SoC hangs, so parent/rate changes on `clk_a53` are particularly dangerous. The Ethernet 500M clocks appear to use `REG_DIV_CLK_GPIO_DB` rather than the nearby Ethernet-specific register defines, which should be checked against the TRM.

## Test Signals
Boot each compatible and inspect `clk_summary` for parent/rate correctness. Exercise `clk_set_rate()` and `clk_set_parent()` for storage, UART, I2C, audio, video, and C906/A53 paths. Verify pre-init register writes with early debug reads. Tests should include suspend/resume or late unused-clock disabling to ensure critical and ignore-unused flags are correct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv1800.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv1800.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv1800.h

## Purpose
This header defines CV1800/CV1810 clock count limits and register offsets for PLL and clock-generator blocks. It is the register map contract consumed by the CV18xx top-level, PLL, and IP clock descriptions.

## Important APIs, Types, And Functions
`CV1800_CLK_MAX` and `CV1810_CLK_MAX` size the onecell arrays based on dt-binding IDs. The file defines PLL G2 and G6 control/status/SSC/synthesizer registers, fractional APLL registers, PLL output clock CSR registers, camera source divider registers, clock enable registers `REG_CLK_EN_0` through `REG_CLK_EN_4`, mux/bypass registers, and a large set of divider registers for CPU, TPU, storage, Ethernet, GPIO, SDMA audio, camera, AXI, DSI, VIP, codec, SPI, I2C, audio source, PWM, debug, RTC, C906, and VIP extension paths.

## Control Flow
No executable code exists. The constants are embedded into static clock declarations and pre-init functions in `clk-cv1800.c` and into register operations in the CV18xx helper files.

## State And Persistence
The constants describe persistent hardware registers relative to the controller base. Runtime writes using these offsets determine gate, divider, mux, bypass, PLL, and synthesizer state.

## Dependencies And Integration Points
The header includes `dt-bindings/clock/sophgo,cv1800.h`, so ID limits track public Device Tree ABI. It integrates with the CV1800 aggregate module and all CV18xx clock-class helpers that interpret fields at these offsets.

## Risks
Register offset mistakes propagate into all macros using the constant. `CV1800_CLK_MAX` and `CV1810_CLK_MAX` must remain synchronized with dt-bindings; otherwise provider arrays can omit clocks or expose invalid IDs. Hardware revision differences between CV1800, CV1810, and SG2000 need explicit handling in the descriptor layer.

## Test Signals
Compile checks catch missing constants but not wrong offsets. Runtime smoke tests should read back selected registers after enabling, setting rates, or changing parents for representative PLL, divider, mux, and gate clocks on each SoC variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv1800.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv18xx-common.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv18xx-common.c

## Purpose
This file provides shared low-level register helpers for CV18xx clock classes. It centralizes locked bit set/clear operations, unlocked bit checks, and PLL lock polling.

## Important APIs, Types, And Functions
`cv1800_clk_setbit()` and `cv1800_clk_clearbit()` perform spinlock-protected read-modify-write operations on a single bit described by `struct cv1800_clk_regbit`. `cv1800_clk_checkbit()` reads a bit without taking the shared lock. `cv1800_clk_wait_for_lock()` polls a status register until a lock mask is set, warning after `PLL_LOCK_TIMEOUT_US` microseconds.

## Control Flow
Set and clear helpers save IRQ flags, read `common->base + field->reg`, modify `BIT(field->shift)`, write back, and release the lock. Lock polling returns immediately when the requested mask is zero; otherwise it uses `readl_relaxed_poll_timeout()` with a 100 microsecond interval and 200 millisecond timeout.

## State And Persistence
The functions mutate MMIO registers and rely on `struct cv1800_clk_common` having already been initialized with the controller base and shared lock. There is no separately allocated state.

## Dependencies And Integration Points
These helpers are used by CV18xx gate, divider, mux, audio, and PLL ops. They depend on Linux MMIO, polling, spinlock, and warning facilities, plus field descriptors from `clk-cv18xx-common.h`.

## Risks
`cv1800_clk_checkbit()` is intentionally unlocked, so callers that make decisions from it can race with concurrent set/clear paths. Poll timeout only warns; callers continue after a failed lock, which may leave clocks at unexpected rates. All helpers assume `common->lock` is valid before any CCF operation is invoked.

## Test Signals
Unit-style register tests can use fake MMIO to validate set/clear masks. Hardware tests should force PLL rate changes and confirm lock status polling succeeds and warning paths are observable when hardware fails to lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv18xx-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv18xx-common.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv18xx-common.h

## Purpose
This header defines the shared data model and bitfield helpers used by all CV18xx clock classes. It is the common substrate for gates, dividers, muxes, audio clocks, and PLLs.

## Important APIs, Types, And Functions
`struct cv1800_clk_common` embeds `struct clk_hw`, an MMIO base, a shared spinlock pointer, and feature flags. `struct cv1800_clk_regbit` describes a single bit; `struct cv1800_clk_regfield` describes a multi-bit field with an optional initial value and divider flags. `CV1800_CLK_COMMON`, `CV1800_CLK_BIT`, and `CV1800_CLK_REG` initialize those structures.

Inline-like macros `cv1800_clk_regfield_genmask()`, `cv1800_clk_regfield_get()`, `cv1800_clk_regfield_set()`, and `_CV1800_SET_FIELD()` implement field packing and extraction. The header declares `cv1800_clk_setbit()`, `cv1800_clk_clearbit()`, `cv1800_clk_checkbit()`, and `cv1800_clk_wait_for_lock()`.

## Control Flow
No executable flow exists beyond macros. The initialization macro uses `CLK_HW_INIT_PARENTS_DATA()` so all CV18xx classes use firmware/clk_hw parent-data arrays consistently.

## State And Persistence
The common struct is embedded in each static clock object. At probe time, the top-level driver sets its `base` and `lock`; after that, CCF callbacks use those pointers to access persistent hardware registers.

## Dependencies And Integration Points
The header depends on CCF, compiler helpers, and bitfield macros. It is included by both `clk-cv18xx-ip.*` and `clk-cv18xx-pll.*`, and indirectly by the top-level CV1800 clock table.

## Risks
Field macros assume valid widths and shifts; invalid descriptors can generate undefined or unintended masks. `initval` carries special semantics in divider code, so table authors must distinguish fixed dividers, hardware default dividers, and writable dividers carefully.

## Test Signals
Static analysis should catch impossible shifts/widths when constants are visible. Runtime tests should verify descriptor initialization for representative gate, divider, mux, and PLL clocks after `cv1800_clk_init_ctrl()` sets base/lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv18xx-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv18xx-ip.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv18xx-ip.c

## Purpose
This file implements the non-PLL CV18xx clock classes: gates, dividers, bypass dividers, muxes, bypass muxes, dual-path multi-muxes, and audio fractional clocks. These `clk_ops` power the static clock objects declared in `clk-cv1800.c`.

## Important APIs, Types, And Functions
The exported operation tables are `cv1800_clk_gate_ops`, `cv1800_clk_div_ops`, `cv1800_clk_bypass_div_ops`, `cv1800_clk_mux_ops`, `cv1800_clk_bypass_mux_ops`, `cv1800_clk_mmux_ops`, and `cv1800_clk_audio_ops`.

Shared helpers include `div_helper_set_rate()`, `div_helper_get_clockdiv()`, `div_helper_determine_rate()`, `div_is_better_rate()`, and `mux_helper_determine_rate()`. Gate callbacks just set or clear the gate bit. Divider callbacks compute divider values with CCF divider helpers and handle hardware initial values via `DIV_FACTOR_SEL`. Mux callbacks read/write parent fields. Bypass variants treat parent index 0 as bypass/raw parent and parent index 1+ as divided/muxed paths. Multi-mux callbacks use two divider/mux register banks plus `parent2sel` and `sel2parent` lookup tables. Audio callbacks program M/N fractional registers for a fixed target rate using `gcd()`.

## Control Flow
Rate determination generally loops possible parents unless `CLK_SET_RATE_NO_REPARENT` is set. For each parent, a class-specific round function computes a candidate rate, and the best candidate is selected according to closest-rate or not-greater-than-target semantics. Set-rate writes divider fields under the shared spinlock. Parent changes on muxes write field registers; bypass classes set or clear bypass bits.

The multi-mux class has more complex flow: bypass forces parent 0 and raw parent rate; otherwise `clk_sel` selects one of two mux/divider banks. `mmux_set_parent()` sets bypass for oscillator/invalid paths, clears bypass for normal paths, toggles `clk_sel`, then writes the selected mux field. Audio set-rate computes `m = parent/2/gcd(parent/2, rate)` and `n = rate/gcd(parent/2, rate)`, writes M/N, then enables and updates the divider.

## State And Persistence
The class instances are static objects with descriptors for gate bits, divider fields, mux fields, bypass bits, and lookup tables. Persistent hardware state is in MMIO registers. The shared spinlock serializes most write paths, but some helper calls perform their own locked read-modify-write operations.

## Dependencies And Integration Points
The implementation depends on CCF divider/mux helpers, `clk_rate_request`, Linux MMIO, spinlocks, `gcd()`, and common CV18xx bit helpers. It integrates with the top-level CV1800 driver through macro-generated objects and `devm_clk_hw_register()`.

## Risks
`mmux_set_rate()` returns `parent_rate` when bypass is active even though the callback returns `int`, which is unusual and should be reviewed. `mmux_set_parent()` calls bit helpers that lock internally, then later takes the lock for mux-field writes; the overall parent transition is not atomic across bypass/selector/mux fields. Several paths rely on lookup tables being correct; an invalid parent index can trigger `BUG()` in `mmux_get_parent_id()`. Audio M/N calculations do not validate field-width overflow before writing.

## Test Signals
Exercise enable/disable/is_enabled for each class. Rate tests should cover fixed dividers, writable dividers, bypass active/inactive behavior, mux parent changes, multi-mux C906/A53 parent selections, and audio rate programming to 24.576 MHz. Concurrent parent/rate-change stress tests are especially useful for multi-mux paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv18xx-ip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv18xx-ip.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv18xx-ip.h

## Purpose
This header defines all non-PLL CV18xx clock object layouts and declaration macros. It lets the top-level clock table declare many gates/dividers/muxes compactly while binding each object to the correct `clk_ops`.

## Important APIs, Types, And Functions
Clock structs are `cv1800_clk_gate`, `cv1800_clk_div`, `cv1800_clk_bypass_div`, `cv1800_clk_mux`, `cv1800_clk_bypass_mux`, `cv1800_clk_mmux`, and `cv1800_clk_audio`. Declaration macros include `CV1800_GATE`, `CV1800_DIV`, `CV1800_BYPASS_DIV`, `CV1800_FIXED_DIV`, `CV1800_BYPASS_FIXED_DIV`, `CV1800_MUX`, `CV1800_BYPASS_MUX`, `CV1800_MMUX`, and `CV1800_ACLK`.

The header exports the operation tables implemented in `clk-cv18xx-ip.c`.

## Control Flow
No runtime flow exists in the header. The macros initialize embedded `cv1800_clk_common` records with `CLK_HW_INIT_PARENTS_DATA()` and attach class-specific descriptors for gate, divider, mux, bypass, selector, and audio fields.

## State And Persistence
Each macro expands to a static object whose descriptors are later completed with MMIO base and lock in the top-level probe. The descriptors encode how persistent hardware registers are manipulated by CCF callbacks.

## Dependencies And Integration Points
It depends on the common CV18xx header and on CCF types. The macro names are used extensively by `clk-cv1800.c`, so changes here affect all CV1800/CV1810/SG2000 clock definitions.

## Risks
The macros hide many positional arguments; swapping a register, shift, width, or init value is easy and hard to detect in review. The fixed-divider macro uses width 0 and initval as a sentinel, so helper code must continue to preserve that convention.

## Test Signals
Build-time coverage verifies macro expansion. Runtime validation should map each macro family to at least one clock in `clk_summary` and test rate/parent/gate behavior for that instance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv18xx-ip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv18xx-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv18xx-pll.c

## Purpose
This file implements CV18xx PLL clock operations for integral PLLs and fractional PLLs. It calculates rates from hardware fields, searches valid divider/programming combinations, writes PLL registers, handles power-down bits, and waits for lock.

## Important APIs, Types, And Functions
The exported operation tables are `cv1800_clk_ipll_ops` and `cv1800_clk_fpll_ops`. Integral helpers include `ipll_calc_rate()`, `ipll_recalc_rate()`, `ipll_find_rate()`, `ipll_determine_rate()`, `ipll_check_mode_ctrl_restrict()`, and `ipll_set_rate()`. Common PLL helpers include `pll_get_mode_ctrl()`, `pll_enable()`, `pll_disable()`, and `pll_is_enable()`.

Fractional helpers include `fpll_is_factional_mode()`, `fpll_calc_rate()`, `fpll_recalc_rate()`, `fpll_find_synthesizer()`, `fpll_find_rate()`, `fpll_determine_rate()`, `fpll_check_mode_ctrl_restrict()`, `fpll_set_rate()`, `fpll_get_parent()`, and `fpll_set_parent()`.

## Control Flow
Integral rate recalculation decodes pre-divider, divider, and post-divider fields and computes `parent * div / (pre * post)`. Integral set-rate searches all configured pre/div/post limits for the best rate not exceeding the target, computes mode and current-control fields, writes the masked PLL register under the shared lock, and waits for the lock status bit.

Fractional PLLs fall back to integral behavior when the synthesizer enable bit is clear. When fractional mode is active, recalculation reads the synthesizer set register and computes a rate using the fixed-point synthesizer factor. Set-rate searches PLL divider ranges and the synthesizer value, writes synthesizer and PLL registers under lock, then waits for lock. Fractional parent selection is modeled as parent index 0 for integral mode and 1 for fractional mode.

## State And Persistence
The PLL object stores register offsets, power-down bit, status bit, limit table, and optional synthesizer descriptor. Runtime state is in PLL control/status/synthesizer MMIO registers. Enabling clears the power-down bit; disabling sets it.

## Dependencies And Integration Points
The implementation uses CCF, Linux MMIO, spinlocks, `do_div`, limit descriptors from `clk-cv18xx-pll.h`, and common bit helpers. Top-level CV1800 clock declarations instantiate these PLL objects and mark critical PLLs.

## Risks
Several search functions ignore or do not propagate `-EINVAL` in callers; if no rate is found, set-rate may still proceed with zeroed programming. Fractional code indexes `pll->pll_limit[2]`, but the visible limit arrays in the top-level driver contain two entries, so this deserves immediate review for out-of-bounds access or missing fractional limit data. `fpll_find_synthesizer()` uses a binary-search-like loop where `trate` must be meaningful after loop exit; boundary behavior needs testing. Poll timeout only warns, allowing operation to continue after failed lock.

## Test Signals
Test integral PLL rate rounding across min/max limits and fractional PLL mode switching. Hardware tests should verify lock polling, power-down enable/disable, and measured output rates for MPLL/TPLL/A0PLL/DISPPLL/CAM PLLs. KASAN or UBSAN builds would be valuable for the fractional limit indexing risk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv18xx-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv18xx-pll.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv18xx-pll.h

## Purpose
This header defines CV18xx PLL descriptors, limits, field masks, and declaration macros for integral and fractional PLL clocks.

## Important APIs, Types, And Functions
`struct cv1800_clk_pll_limit` contains min/max ranges for `pre_div`, `div`, `post_div`, `ictrl`, and `mode`. `struct cv1800_clk_pll_synthesizer` describes fractional synthesizer enable, half-clock, control, and set registers. `struct cv1800_clk_pll` embeds the common clock state, PLL register, power-down bit, status bit, limit pointer, and optional synthesizer pointer.

Field masks and accessors cover PLL pre-divider, post-divider, mode, divider, and current-control fields. `PLL_COPY_REG()` preserves unrelated bits while copying the programmable PLL fields. Macros `CV1800_INTEGRAL_PLL()` and `CV1800_FACTIONAL_PLL()` instantiate PLL objects with the correct operation table.

## Control Flow
The header has no runtime flow. Its macros bind objects to `cv1800_clk_ipll_ops` or `cv1800_clk_fpll_ops`; the implementation file interprets field masks and limit ranges during rate operations.

## State And Persistence
The structures are static descriptors completed at probe with base and lock through the embedded common object. Hardware register fields persist PLL configuration and status.

## Dependencies And Integration Points
It depends on `clk-cv18xx-common.h` for common clock state and bit descriptors. Top-level CV1800 declarations use this header for every root PLL and fractional synthesizer.

## Risks
The limit pointer is untyped with respect to array length, yet fractional implementation indexes beyond the first element. Incorrect limits can cause invalid hardware programming or excessive search time. Positional macro arguments for status and power-down bits are easy to mix up.

## Test Signals
Build tests ensure macro consumers compile. Runtime PLL tests should validate field extraction, `PLL_COPY_REG()` preservation, and both integral and fractional declarations under rate changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv18xx-pll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-sg2042-clkgen.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-sg2042-clkgen.c

## Purpose
This file is the SG2042 clock-generator driver. It registers divider, gate, and mux clocks fed by SG2042 PLL outputs, arranges them in hardware clock-tree order, and exposes them through a CCF onecell provider for `sophgo,sg2042-clkgen`.

## Important APIs, Types, And Functions
Local clock classes are `struct sg2042_divider_clock`, `struct sg2042_gate_clock`, and `struct sg2042_mux_clock`. Divider ops are implemented by `sg2042_clk_divider_recalc_rate()`, `sg2042_clk_divider_determine_rate()`, and `sg2042_clk_divider_set_rate()`. Mux rate-change safety is implemented by `sg2042_mux_notifier_cb()`.

Registration helpers are `sg2042_clk_register_divs()`, `sg2042_clk_register_gates()`, `sg2042_clk_register_gates_fw()`, `sg2042_clk_register_muxs()`, and `sg2042_init_clkdata()`. Static tables define level-1 gates, level-1 dividers, top-level muxes, level-2 dividers, and level-2 gates.

## Control Flow
Probe maps MMIO resource 0 and calculates the total number of clocks from all tables. It registers level-1 gates first because dividers depend on their returned `clk_hw` pointers. It then registers level-1 dividers, muxes, level-2 dividers, and level-2 gates. During registration, selected returned `clk_hw` pointers are written into one-element parent arrays used by downstream definitions.

Divider set-rate asserts reset, writes divider factor and factor-source bit, then deasserts reset under a shared lock. Read-only dividers return the current/default divider during determine-rate. Non-read-only muxes register a notifier that switches the mux to FPLL before a parent rate change and restores the original parent afterward.

## State And Persistence
`struct sg2042_clk_data` stores MMIO base and onecell output. Static parent arrays start as NULL and are patched during registration to connect generated `clk_hw`s. Divider hardware state is in `CLKDIVREG*` registers, including reset, factor-select, and factor fields. Gate state is in `CLKENREG*`; mux state is in `CLKSELREG0`.

## Dependencies And Integration Points
The driver depends on SG2042 PLL clocks named by firmware (`mpll`, `fpll`, `dpll0`, `dpll1`) and dt-binding IDs from `sophgo,sg2042-clkgen.h`. It uses generic CCF gate, mux, and divider helpers plus the shared `sg2042_clk_data` type from `clk-sg2042.h`.

## Risks
The parent arrays patched during registration make ordering essential; reordering tables or registration calls can leave downstream parents NULL. The notifier uses magic parent indices where index 1 is FPLL, noted by a FIXME. Some clocks are intentionally inaccurate because fixed 1/2 dividers are not modeled for PCIe AXI clocks. Divider default `initval` values compensate for unreadable hardware defaults; wrong defaults yield wrong reported rates.

## Test Signals
Boot SG2042 with PLL and CLKGEN nodes and verify all binding IDs resolve. Test rate changes for RP CPU normal and AXI DDR mux paths to ensure notifier switching is correct. Inspect `clk_summary` for DDR, timer, UART, eMMC, SD, GPIO debounce, Ethernet, and AXI rates. Confirm read-only DDR dividers refuse changes but report expected defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-sg2042-clkgen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-sg2042-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-sg2042-pll.c

## Purpose
This file is the SG2042 PLL driver. It registers MPLL, FPLL, DPLL0, and DPLL1 clocks from SYS_CTRL registers and implements rate calculation/programming for writable PLLs.

## Important APIs, Types, And Functions
`struct sg2042_pll_clock` describes a PLL `clk_hw`, binding ID, register base, lock, control offset, status lock/updating bits, and enable bit. `struct sg2042_pll_ctrl` holds decoded frequency parameters: `fbdiv`, `postdiv1`, `postdiv2`, and `refdiv`.

Core helpers include `sg2042_pll_ctrl_encode()`, `sg2042_pll_ctrl_decode()`, `sg2042_pll_enable()`, `sg2042_pll_recalc_rate()`, `sg2042_pll_get_postdiv_1_2()`, `sg2042_get_pll_ctl_setting()`, and CCF callbacks `sg2042_clk_pll_recalc_rate()`, `sg2042_clk_pll_determine_rate()`, and `sg2042_clk_pll_set_rate()`.

## Control Flow
Probe allocates onecell data sized to the PLL table, maps the SYS_CTRL PLL resource, initializes each PLL's base and shared lock, registers the `clk_hw`, stores it by ID, and adds the OF provider. The PLL programming path disables the PLL, searches valid control settings for the target rate, writes the encoded control register, re-enables the PLL, and waits for lock/updating bits in the enable helper.

Rate search requires a 25 MHz parent and target output between 16 MHz and 3.2 GHz. It iterates REFDIV and FBDIV ranges while enforcing FREF/REFDIV and VCO constraints, then derives postdiv1/postdiv2 from a small product table.

## State And Persistence
The PLL driver stores static PLL descriptors and runtime base/lock pointers. Hardware state persists in SYS_CTRL PLL status, enable, and control registers. FPLL and DPLLs are registered read-only; MPLL is writable.

## Dependencies And Integration Points
It depends on dt-binding IDs from `sophgo,sg2042-pll.h`, the shared SG2042 data structure, CCF, MMIO, polling, and 64-bit division helpers. Downstream SG2042 clock-generator nodes consume firmware-named PLL outputs.

## Risks
`sg2042_get_pll_ctl_setting()` requires `parent_rate == 25 MHz`; alternate oscillator descriptions fail. The post-divider search rounds by selecting the first product not less than the computed value, so rate accuracy depends on the table. Set-rate always re-enables the PLL even after search failure, but returns the error. Poll timeouts warn but do not abort enabling.

## Test Signals
Validate MPLL set-rate across the supported range, read-only behavior for FPLL/DPLLs, and measured output rates. Confirm parent rate from Device Tree is exactly 25 MHz or gracefully rejected. Boot tests should verify SG2042 CLKGEN can resolve `mpll`, `fpll`, `dpll0`, and `dpll1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-sg2042-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-sg2042-rpgate.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-sg2042-rpgate.c

## Purpose
This file is the SG2042 RP subsystem gate driver. It exposes individual gates for 32 RXU clocks and 16 MP clocks under the `sophgo,sg2042-rpgate` compatible.

## Important APIs, Types, And Functions
`struct sg2042_rpgate_clock` describes a gate clock ID, init data, enable register offset, and bit index. The `SG2042_GATE_FW()` macro declares firmware-parented gates. `sg2042_clk_register_rpgates()` registers each gate with `devm_clk_hw_register_gate_parent_data()`. `sg2042_rpgate_probe()` allocates onecell storage, maps registers, registers gates, and adds the OF provider.

## Control Flow
Probe maps the SYS_CTRL gate resource, then loops over the static `sg2042_gate_rp[]` table. Every entry uses parent name `rpgate`, which is expected to come from the clock generator. RXU gates share `R_RP_RXU_CLK_ENABLE` with distinct bits. MP gates use per-core control registers with bit 0 and are marked `CLK_IS_CRITICAL`.

## State And Persistence
Gate state persists in SYS_CTRL RP gate registers. Runtime state is limited to devm-managed onecell data and MMIO base. A shared spinlock serializes gate writes through the generic gate helper.

## Dependencies And Integration Points
The driver depends on dt-binding IDs from `sophgo,sg2042-rpgate.h`, the shared `sg2042_clk_data` struct, and the upstream `rpgate` parent clock from SG2042 CLKGEN. It integrates with CCF generic gates and Device Tree clock providers.

## Risks
All gates depend on the firmware parent name `rpgate`; naming mismatch prevents parent resolution. MP clocks are critical and therefore resistant to unused-clock cleanup, which is appropriate for processors but should match actual hardware bring-up needs. The file defines status register offsets but does not use them, so gate enable does not verify hardware acknowledgement.

## Test Signals
Boot SG2042 with RP gate node and inspect all RXU/MP gates in `clk_summary`. Verify non-critical RXU gates can be toggled safely and MP gates remain enabled. Confirm parent resolution to the SG2042 clock generator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-sg2042-rpgate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-sg2042.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-sg2042.h

## Purpose
This header defines the common SG2042 clock-provider data container shared by the SG2042 PLL, clock-generator, and RP-gate drivers.

## Important APIs, Types, And Functions
`struct sg2042_clk_data` holds an MMIO base pointer and a trailing `clk_hw_onecell_data` used for OF provider registration. The `onecell_data` member must remain last when allocated with `struct_size()`.

## Control Flow
No executable flow exists. Each SG2042 driver allocates this structure, maps its resource into `iobase`, fills `onecell_data.hws[]`, and passes it to `devm_of_clk_add_hw_provider()`.

## State And Persistence
The structure is devm-managed per platform device. It owns the provider's hardware pointer array and base address for register access. Hardware state lives in the mapped controller registers.

## Dependencies And Integration Points
The header depends on CCF and MMIO types. It is included by `clk-sg2042-pll.c`, `clk-sg2042-clkgen.c`, and `clk-sg2042-rpgate.c`.

## Risks
All users rely on flexible-array-style allocation through `struct_size()`. Mis-sizing `num_clks` or using a binding ID outside the allocation corrupts the provider table. The shared type does not encode which register block is mapped, so each driver must pass the correct resource.

## Test Signals
Compile all SG2042 drivers and verify no allocation warnings. Runtime checks should confirm each provider's `onecell_data.num` covers its highest dt-binding ID and that all expected IDs return valid or intentional missing clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-sg2042.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-sg2044-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-sg2044-pll.c

## Purpose
This file is the SG2044 PLL clock-controller driver. It registers FPLL, DPLL, and MPLL clocks backed by a parent syscon regmap, exposes them through a platform-device ID table, and supports rate changes for MPLLs while registering FPLLs/DPLLs as read-only.

## Important APIs, Types, And Functions
Important structs are `sg2044_pll_limit`, `sg2044_pll_internal`, `sg2044_clk_common`, `sg2044_pll`, `sg2044_pll_desc_data`, and `sg2044_pll_ctrl`. Rate helpers include `sg2044_pll_calc_vco_rate()`, `sg2044_pll_calc_rate()`, `sg2044_pll_recalc_rate()`, `sg2042_pll_compute_postdiv()` (name appears inherited from SG2042), `sg2044_compute_pll_setting()`, `sg2044_pll_determine_rate()`, `sg2044_pll_poll_update()`, `sg2044_pll_enable()`, `sg2044_pll_update_vcosel()`, and `sg2044_pll_set_rate()`.

Macros `DEFINE_SG2044_PLL()` and `DEFINE_SG2044_PLL_RO()` declare writable and read-only PLLs. The static table includes three FPLLs, eight DPLLs, and six MPLLs. `sg2044_pll_init_ctrl()` initializes common state and registers all PLLs.

## Control Flow
Probe retrieves the parent device's syscon regmap with `device_node_to_regmap()`, gets descriptor data from `platform_get_device_id()`, allocates onecell storage, and registers each PLL. Set-rate clamps/searches valid PLL parameters, computes VCO rate, adds calibration/update bits, takes the shared lock with cleanup guards, disables the PLL, updates VCO select, writes high-control fields, and re-enables the PLL after lock polling.

## State And Persistence
Runtime state is the regmap pointer, shared lock, onecell provider, and each PLL's syscon offset. Hardware state persists in syscon PLL control, status, and enable registers under `SG2044_SYSCON_PLL_OFFSET`. Read-only FPLL/DPLL clocks still report rates from hardware fields.

## Dependencies And Integration Points
The driver depends on `MFD_SYSCON`, `REGMAP_MMIO`, CCF, cleanup guard macros, and dt-binding IDs from `sophgo,sg2044-pll.h`. The main SG2044 clock controller consumes firmware parent names such as `fpll0`, `dpll0`, and `mpll0`.

## Risks
The helper named `sg2042_pll_compute_postdiv()` in an SG2044 driver is confusing and can mislead maintenance, though functionally local. `sg2044_pll_set_rate()` ignores the return value from `sg2044_pll_update_vcosel()` and the final enable call is not stored in `ret`, so failures can be missed. Read-only PLLs only expose recalculation, not determine-rate, which may affect consumers asking for rounded rates. The platform-device ID path requires an MFD child named `sg2044-pll`; OF matching is not used directly.

## Test Signals
Probe tests must validate parent syscon child creation and provider registration. Rate tests should cover MPLL set-rate at boundaries, VCO select threshold near 2.4 GHz, and lock timeout behavior. Main SG2044 clock consumers should resolve all PLL firmware names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-sg2044-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-sg2044.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-sg2044.c

## Purpose
This is the SG2044 main clock-controller driver. It models non-PLL clocks as divider, mux, and gate objects, registers them against the MMIO clock-controller block, and exposes a onecell provider for `sophgo,sg2044-clk`.

## Important APIs, Types, And Functions
Internal types are `sg2044_div_internal`, `sg2044_mux_internal`, `sg2044_gate_internal`, `sg2044_clk_common`, `sg2044_div`, `sg2044_mux`, `sg2044_gate`, `sg2044_clk_ctrl`, and `sg2044_clk_desc_data`. Divider callbacks are `sg2044_div_recalc_rate()`, `sg2044_div_determine_rate()`, `sg2044_div_set_rate()`, and gateable divider enable/disable/is_enabled functions. Mux safety uses `sg2044_mux_notifier_cb()`. Registration is handled by `sg2044_clk_init_ctrl()` and `sg2044_clk_probe()`.

Declaration macros define gateable dividers, plain dividers, parent-data dividers, read-only dividers, muxes, and gates. Static common arrays group all dividers, muxes, and gates for descriptor-driven registration.

## Control Flow
Probe maps MMIO resource 0, retrieves match descriptor data, allocates onecell storage sized to divider + mux + gate counts, and calls `sg2044_clk_init_ctrl()`. Initialization registers dividers first, then muxes, then gates. Muxes are registered with `devm_clk_hw_register_mux_parent_data_table()` and non-read-only muxes get notifiers that switch to parent index 0 before parent rate changes and restore the saved parent after. Gates are registered after resolving their parent `clk_hw` pointers through the already-filled onecell table.

Divider set-rate asserts the divider, writes a new factor and selects the register factor source, then deasserts. Gateable dividers also expose branch enable/disable via bit 4. Read-only dividers report rates from either hardware factor or default `initval`.

## State And Persistence
Static clock objects describe all SG2044 divisors, muxes, and gates. Probe writes the shared MMIO base and lock into each common object. Hardware state lives in clock divider/gate/mux registers, with divider reset/factor-source/branch-enable bits and gate enable bits persisted until hardware reset.

## Dependencies And Integration Points
The driver depends on PLL parent clocks exposed by `clk-sg2044-pll.c` through firmware names (`fpll0`, `mpll0`, `dpll0`, etc.), CCF generic gate and mux helpers, CCF divider helpers, cleanup guard macros, and dt-binding IDs from `sophgo,sg2044-clk.h`. It integrates with platform probing and Device Tree clock consumers.

## Risks
`ctrl->data.num` is set to the count of registered clocks, not necessarily the highest dt-binding ID plus one. If IDs are sparse or larger than the count, onecell lookup can be wrong or out of bounds. `sg2044_div_internal.flags` mixes divider flags with `CLK_IS_CRITICAL` in several declarations; CCF flags belong in `common.hw.init->flags`, not divider flags, so critical policy may not apply as intended for those gateable dividers. Parent fix-up warns when a parent ID has not been registered, making registration order critical. Mux notifiers assume parent index 0 is the safe fixed parent.

## Test Signals
Boot SG2044 and check that every dt-binding ID resolves, especially high-valued or sparse IDs. Inspect `clk_summary` for AP/RP/TPU/NOC, DDR0-7, VC, CXP, timers, UART, GPIO, SD/eMMC, Ethernet, and PKA clocks. Exercise divider rate changes, gateable divider enable/disable, non-read-only mux parent rate changes, and late unused-clock cleanup to validate critical-clock policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-sg2044.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/spacemit/Kconfig

## Purpose
This Kconfig file declares clock support for SpacemiT platforms. It provides a common CCU symbol plus selectable K1 and K3 SoC clock-controller drivers.

## Important APIs, Types, And Functions
The symbols are `SPACEMIT_CCU`, `SPACEMIT_K1_CCU`, and `SPACEMIT_K3_CCU`. The common symbol is tristate and selects `AUXILIARY_BUS` and `MFD_SYSCON`. K1 and K3 symbols are user-visible tristates that select the common CCU support.

## Control Flow
Configuration selection controls which Makefile objects are built. Selecting either SoC-specific CCU pulls in the shared CCU core.

## State And Persistence
No runtime state exists in this file. Build configuration determines module availability and dependency inclusion.

## Dependencies And Integration Points
The menu is visible when `ARCH_SPACEMIT || COMPILE_TEST`. It integrates with `drivers/clk/spacemit/Makefile`, shared CCU implementation files, and SoC-specific K1/K3 sources elsewhere in the directory.

## Risks
Because the common CCU symbol is hidden, all SoC-specific symbols must continue to select it. Missing dependencies on syscon or auxiliary bus would break shared CCU probe paths, but both are selected here.

## Test Signals
Run build coverage for `ARCH_SPACEMIT`, `COMPILE_TEST`, K1-only, K3-only, both built-in, and both modular configurations. Runtime tests should verify module autoload and shared CCU dependency loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/spacemit/Makefile

## Purpose
This Makefile maps SpacemiT Kconfig symbols to common and SoC-specific clock-controller objects.

## Important APIs, Types, And Functions
`spacemit-ccu.o` is built from common helper files `ccu_common.o`, `ccu_pll.o`, `ccu_mix.o`, and `ccu_ddn.o`. `spacemit-ccu-k1.o` includes `ccu-k1.o`; `spacemit-ccu-k3.o` includes `ccu-k3.o`.

## Control Flow
The kernel build system links the aggregate common module when `CONFIG_SPACEMIT_CCU` is enabled and links K1/K3 modules based on their SoC-specific symbols.

## State And Persistence
No runtime state exists. The object grouping controls module boundaries and symbol linkage.

## Dependencies And Integration Points
This file integrates with the SpacemiT Kconfig menu and the shared CCU implementation files in the same directory. The SoC-specific objects depend on common code being available through `SPACEMIT_CCU`.

## Risks
Omitting a common helper object can cause unresolved symbols in K1/K3 modules. If common helpers export module symbols implicitly within the same aggregate only, moving objects between modules needs careful linkage review.

## Test Signals
Build common, K1, and K3 configurations as modules and built-ins. Confirm generated module names match expected platform-driver aliases and that K1/K3 modules can load with the common CCU module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/Makefile -->
