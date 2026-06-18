# subset-b-001175 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/spear3xx_clock.c -->
# sources/distributed-fs/ceph-client/drivers/clk/spear/spear3xx_clock.c

## Purpose
Initializes the common clock tree for ST SPEAr300/310/320 family machines. It registers oscillator roots, PLL/VCO clocks, synthesizers, muxes, dividers, gates, RAS clocks, and machine-specific fixed-factor or muxed peripheral clocks.

## Important APIs, Types, And Functions
The main entry point is `spear3xx_clk_init(void __iomem *misc_base, void __iomem *soc_config_base)`. It uses common clock framework helpers plus SPEAr-specific helpers from `clk.h`: `clk_register_vco_pll`, `clk_register_aux`, and `clk_register_gpt`. Local rate tables `pll_rtbl`, `aux_rtbl`, and `gpt_rtbl` encode supported PLL, auxiliary synth, and GPT synth settings. Conditional helpers `spear300_clk_init`, `spear310_clk_init`, and `spear320_clk_init` add per-machine device clock aliases.

## Control Flow
Initialization registers 32 kHz and 24 MHz oscillators, creates the fixed 48 MHz `pll3_clk`, configures PLL1/PLL2 from MISC registers, derives CPU/AHB/APB/DDR clocks, then walks through UART, FIRDA, GPT, generic synth, USB, AHB, APB, and RAS gate registration. The final `of_machine_is_compatible` branch selects SPEAr300, SPEAr310, or SPEAr320 additions; SPEAr320 also programs mux parents for I2S, SDHCI, SMII, and UARTx clocks and forces UART1/UART2 to `ras_apb_clk`.

## State And Persistence
State is persisted in the hardware clock-control registers under `misc_base` and, for SPEAr320, `soc_config_base`. The driver also installs global clkdev lookup entries. A single static spinlock serializes register updates among the registered clock operations.

## Dependencies And Integration Points
Depends on the Linux common clock framework, clkdev lookup, device tree machine compatibles, and SPEAr helper clock implementations in the sibling `clk-*` files. Integration is by string aliases such as `d0000000.serial`, `fc980000.gpio`, `70000000.sdhci`, and RAS clock names consumed by platform devices.

## Risks And Edge Cases
The code assumes valid MMIO bases and does little error checking after clock registration, so a failed registration can leave later aliases pointing at error clocks. Register bit definitions and parent arrays must match silicon; wrong mux masks can select reserved parents. SPEAr320 has special enforced UART parents that can surprise rate changes. Conditional machine blocks mean build configuration affects available aliases.

## Test Signals
Useful signals are boot-time clock registration without warnings, `/sys/kernel/debug/clk/clk_summary` parent/rate sanity, successful probe of UART/I2C/GPIO/USB/storage devices on each SPEAr3xx variant, and exercising rate changes on UART/FIRDA/GPT/generic synth clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/spear3xx_clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/spear6xx_clock.c -->
# sources/distributed-fs/ceph-client/drivers/clk/spear/spear6xx_clock.c

## Purpose
Builds the SPEAr6xx clock tree for the ARM platform clock framework. It provides root oscillators, PLLs, bus clocks, synth-backed muxes, peripheral gates, and clkdev aliases for SPEAr600-class devices.

## Important APIs, Types, And Functions
The exported initializer is `spear6xx_clk_init(void __iomem *misc_base)`. It defines hardware register offsets and masks, parent arrays for CLCD/FIRDA/UART/GPT/DDR, and three rate tables: `pll_rtbl`, `aux_rtbl`, and `gpt_rtbl`. It uses CCF primitives plus `clk_register_vco_pll`, `clk_register_aux`, and `clk_register_gpt`.

## Control Flow
The function registers `osc_32k_clk` and `osc_30m_clk`, gates RTC, creates `pll3_clk`, registers PLL1/PLL2 from PLL control/frequency registers, derives CPU/AHB/APB and DDR clocks, then registers shared UART/FIRDA/CLCD synth and mux chains. GPT0/1 share one synth while GPT2 and GPT3 have dedicated synths. It then registers USB, DMA, FSMC, GMAC, I2C, JPEG, SMI, ADC, GPIO, and SSP clocks.

## State And Persistence
Clock state lives in the MISC register block and in global clkdev registrations. The static `_lock` protects mux/divider/gate register updates made by registered clock ops.

## Dependencies And Integration Points
Depends on Linux CCF, clkdev, SPEAr-specific clock helper code, and platform device names such as `d0000000.serial`, `fc200000.clcd`, `e1800000.ehci`, and `d0200000.i2c`. Downstream platform drivers acquire clocks by these aliases rather than by this file directly.

## Risks And Edge Cases
No registration failures are handled inline. `pll3_clk` is declared as derived from `osc_24m_clk` while the file registers `osc_30m_clk`; this is likely an old naming quirk but is a parent-name risk. Duplicate `GPT1_CLK_ENB` and `GPT2_CLK_ENB` definitions both use bit 11, so hardware documentation should be checked before modifying timer gates. Incorrect mux masks can break display, timer, or serial clocks.

## Test Signals
Boot should show all SPEAr6xx clocks registered and peripherals probing. Clock summary should show plausible PLL, AHB, APB, CLCD, UART, FIRDA, and GPT rates. Runtime tests should include serial console, display, timers, USB host/device, I2C, SPI, GPIO, and flash access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/spear6xx_clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/sprd/Kconfig

## Purpose
Defines build-time configuration for the Spreadtrum clock framework and supported Spreadtrum SoC clock drivers.

## Important APIs, Types, And Functions
The key symbols are `SPRD_COMMON_CLK`, `SPRD_SC9860_CLK`, `SPRD_SC9863A_CLK`, and `SPRD_UMS512_CLK`. `SPRD_COMMON_CLK` is a tristate selected by `ARCH_SPRD` by default and selects `REGMAP_MMIO`; SoC symbols are gated by `SPRD_COMMON_CLK`.

## Control Flow
Kconfig evaluation first enables the common framework when compiling for Spreadtrum or `COMPILE_TEST`; then it conditionally exposes the SC9860, SC9863A, and UMS512 drivers. Defaults follow `ARM64 && ARCH_SPRD`.

## State And Persistence
No runtime state. The selected symbols persist in the kernel `.config` and decide which objects are built into the kernel or as modules.

## Dependencies And Integration Points
Integrates the Spreadtrum clock subtree with the kernel build system, architecture selection, compile-test coverage, and regmap MMIO support used by `common.c`.

## Risks And Edge Cases
Because SoC drivers are tristate, module/built-in combinations must remain linkable with `clk-sprd.o`. `COMPILE_TEST` can expose missing headers or assumptions on non-SPRD platforms. Forgetting to select `REGMAP_MMIO` would break MMIO-backed registration.

## Test Signals
Expected signals are successful `allyesconfig`/`allmodconfig` and targeted ARM64 Spreadtrum builds, with `clk-sprd.o` and selected SoC objects appearing according to `.config`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/sprd/Makefile

## Purpose
Maps Spreadtrum clock Kconfig symbols to build objects.

## Important APIs, Types, And Functions
`clk-sprd.o` is built from `common.o`, `gate.o`, `mux.o`, `div.o`, `composite.o`, and `pll.o` under `CONFIG_SPRD_COMMON_CLK`. SoC drivers are separate objects: `sc9860-clk.o`, `sc9863a-clk.o`, and `ums512-clk.o`.

## Control Flow
Kbuild links the common helper object when the common symbol is enabled, then links each SoC-specific platform driver according to its symbol.

## State And Persistence
No runtime state. Build output placement determines whether symbols are available built-in or as loadable modules.

## Dependencies And Integration Points
The SoC object files depend on exported symbols from the common helper modules (`sprd_clk_probe`, `sprd_clk_regmap_init`, and `sprd_*_ops`). This file is the integration point between Kconfig and those link dependencies.

## Risks And Edge Cases
Missing a helper object causes unresolved symbols in SoC modules. Adding a new SoC driver requires both Kconfig and Makefile updates. If helper code is modular while a SoC driver is built-in, symbol availability must remain valid through Kconfig dependencies.

## Test Signals
Build logs should show `clk-sprd.o` plus selected SoC objects. `modinfo` should work for modular builds, and no unresolved symbol warnings should appear at link or module load time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/common.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sprd/common.c

## Purpose
Provides shared Spreadtrum clock registration infrastructure: acquiring a regmap for a clock block, attaching it to all clock descriptors, registering clock hardware, and publishing a device-tree clock provider.

## Important APIs, Types, And Functions
`sprd_clk_regmap_init(struct platform_device *pdev, const struct sprd_clk_desc *desc)` resolves a regmap from `sprd,syscon`, a syscon parent node, or direct MMIO resource. `sprd_clk_probe(struct device *dev, struct clk_hw_onecell_data *clkhw)` registers every non-null `clk_hw` and calls `devm_of_clk_add_hw_provider`. `sprd_clk_set_regmap` assigns the resolved regmap into each `sprd_clk_common`.

## Control Flow
During SoC platform probe, match data supplies a descriptor. Regmap init chooses the access path, initializes MMIO regmap if needed, and stamps the regmap into all common clock records. Probe then iterates the onecell array, skips holes, registers each clock with devm lifetime, and exposes `of_clk_hw_onecell_get` for DT consumers.

## State And Persistence
The persistent runtime state is each clock object's `regmap` pointer plus registered CCF hardware and OF provider records. Hardware register values are not initialized here; individual clock ops mutate them later.

## Dependencies And Integration Points
Depends on regmap, syscon, platform devices, OF address/resource handling, and CCF provider APIs. Every Spreadtrum SoC driver uses this file's exported symbols from its probe function.

## Risks And Edge Cases
The syscon-parent detection uses an `of_get_parent` expression that must always release node references correctly. All descriptor `clk_clks` entries must match the clocks later registered through `hw_clks`; missed entries leave a null regmap and later crashes. Registration stops on first failed clock, leaving devm cleanup to unwind.

## Test Signals
Probe logs should not show syscon/regmap errors or "Couldn't register clock" messages. DT consumers should resolve clocks by phandle. Compile tests should cover syscon and MMIO probe variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/common.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sprd/common.h

## Purpose
Defines the common data contracts shared by all Spreadtrum clock classes and SoC descriptors.

## Important APIs, Types, And Functions
`struct sprd_clk_common` embeds the regmap pointer, register offset, and `struct clk_hw`. `struct sprd_clk_desc` groups the mutable common-clock array with the public `clk_hw_onecell_data`. `hw_to_sprd_clk_common` converts a `clk_hw` back to its Spreadtrum common container. Prototypes expose `sprd_clk_regmap_init` and `sprd_clk_probe`.

## Control Flow
This header has no runtime control flow, but its container layout is used by every clk op implementation to recover register metadata from generic CCF callbacks.

## State And Persistence
The common structure stores persistent per-clock register metadata and the regmap pointer filled during platform probe.

## Dependencies And Integration Points
Includes CCF, OF platform, and regmap headers. It is included by all Spreadtrum gate, mux, divider, composite, PLL, and SoC table files.

## Risks And Edge Cases
Changing the embedded layout or conversion helper would break all `hw_to_*` wrappers. Descriptor arrays must include every clock with register-backed ops so `sprd_clk_regmap_init` can fill `regmap`.

## Test Signals
The strongest signal is successful build and boot probe of multiple Spreadtrum clock classes. Sparse or CFI-like checks would catch invalid container assumptions only indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/composite.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sprd/composite.c

## Purpose
Implements Spreadtrum composite clocks that combine parent selection and divider control in one clock hardware object.

## Important APIs, Types, And Functions
Exports `sprd_comp_ops`. Internal callbacks are `sprd_comp_get_parent`, `sprd_comp_set_parent`, `sprd_comp_determine_rate`, `sprd_comp_recalc_rate`, and `sprd_comp_set_rate`. They delegate to mux helpers from `mux.c` and divider helpers from `div.c`.

## Control Flow
CCF calls the composite ops. Parent operations read or write the mux field in the shared register. Rate operations determine divider feasibility, recalculate from the divider field, or write a new divider while preserving unrelated bits.

## State And Persistence
No private state beyond `struct sprd_comp`; parent and rate state persist in regmap-backed hardware registers.

## Dependencies And Integration Points
Depends on `struct sprd_comp` from `composite.h`, `sprd_mux_helper_*`, `sprd_div_helper_*`, and CCF divider algorithms. SoC files instantiate these clocks for UART, I2C, SPI, buses, CPU, GPU, display, and sensor domains.

## Risks And Edge Cases
Mux and divider updates are separate read-modify-write operations without an explicit lock in this layer, so concurrent updates to the same register fields rely on regmap serialization and non-overlapping fields. `determine_rate` only considers divider width and does not select a better parent itself.

## Test Signals
Clock summary should report correct parent and divided rates. Runtime tests include changing rates on composite peripheral clocks and checking that parent selection and divider fields both reflect the requested configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/composite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/composite.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sprd/composite.h

## Purpose
Declares the Spreadtrum composite clock structure and macro family used by SoC tables.

## Important APIs, Types, And Functions
`struct sprd_comp` embeds `struct sprd_mux_ssel`, `struct sprd_div_internal`, and `struct sprd_clk_common`. Macros such as `SPRD_COMP_CLK`, `SPRD_COMP_CLK_TABLE`, `SPRD_COMP_CLK_DATA`, and offset variants initialize composite clocks with parent-name arrays or `clk_parent_data`. `hw_to_sprd_comp` recovers the composite from a `clk_hw`.

## Control Flow
The macros create static clock objects with register offset, mux field, divider field, parent descriptors, flags, and `sprd_comp_ops`. Runtime control passes through the ops defined in `composite.c`.

## State And Persistence
Stores mux/divider field metadata and common register state for each static SoC clock. Hardware register values persist outside the structure.

## Dependencies And Integration Points
Includes `common.h`, `mux.h`, and `div.h`. Used heavily by SC9860 and SC9863A SoC files for clocks that need both source selection and divisors.

## Risks And Edge Cases
Macro argument order is dense and easy to misread; swapped shifts, widths, or offsets silently target wrong fields. Parent-data variants must match whether the parent is named by firmware name, direct hw pointer, or legacy string.

## Test Signals
Build coverage catches type mismatches. Hardware validation should confirm generated clock names, parent counts, mux table mappings, and rate changes for each macro instance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/composite.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/div.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sprd/div.c

## Purpose
Implements Spreadtrum divider-only clocks and helper functions reused by composite clocks.

## Important APIs, Types, And Functions
Exports `sprd_div_ops`, `sprd_div_helper_recalc_rate`, and `sprd_div_helper_set_rate`. The callbacks use CCF helpers `divider_determine_rate`, `divider_recalc_rate`, and `divider_get_val`.

## Control Flow
For rate reads, the driver reads `common->reg + div->offset`, extracts the divider field, and delegates rate calculation to CCF. For rate writes, it computes the encoded divider value, masks the target field out of the register, and writes the new field value.

## State And Persistence
Divider configuration persists in hardware registers. The driver stores only static metadata: base register, optional offset, shift, and width.

## Dependencies And Integration Points
Depends on regmap through `sprd_clk_common`, CCF divider helpers, and `div.h`. Used directly by SoC `SPRD_DIV_*` clocks and indirectly through composite clocks.

## Risks And Edge Cases
There is no explicit lock around read-modify-write, so shared registers require careful field partitioning. The code ignores regmap read/write errors and always returns success from `set_rate`. Width values must be sane; `(1 << width)` overflows if a too-large width were introduced.

## Test Signals
Clock rate get/set tests should verify requested divider changes, register bit values, and unchanged neighboring fields. Fault-injection regmap tests would expose ignored I/O errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/div.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/div.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sprd/div.h

## Purpose
Defines divider clock metadata, initializers, and helper prototypes for Spreadtrum divider-backed clocks.

## Important APIs, Types, And Functions
`struct sprd_div_internal` describes register offset, shift, and width. `struct sprd_div` embeds that metadata with `sprd_clk_common`. Macros include `SPRD_DIV_CLK`, `SPRD_DIV_CLK_FW_NAME`, and `SPRD_DIV_CLK_HW`. `hw_to_sprd_div` performs container conversion.

## Control Flow
No direct runtime control flow. Macro expansion statically binds divider clocks to `sprd_div_ops`; CCF callbacks later use the metadata.

## State And Persistence
The structures persist static field descriptions and common clock registration data. Actual divider values persist in MMIO/syscon registers.

## Dependencies And Integration Points
Includes `common.h` and is included by `composite.h` and SoC clock tables. It exposes helper functions used by `composite.c`.

## Risks And Edge Cases
Macro variants must match the parent representation used by the SoC file. Wrong offsets or field widths affect hardware outside the intended divider. The signed offset field permits non-zero offsets but still expects valid register windows.

## Test Signals
Compile coverage for macro variants, clock summary rate checks, and register-level validation after setting divider rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/div.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/gate.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sprd/gate.c

## Purpose
Implements Spreadtrum gate clocks, including normal read-modify-write gates, set/clear-register gates, and PLL gates that delay after prepare.

## Important APIs, Types, And Functions
Exports `sprd_gate_ops`, `sprd_sc_gate_ops`, and `sprd_pll_sc_gate_ops`. Core helpers are `clk_gate_toggle`, `clk_sc_gate_toggle`, and `sprd_gate_is_enabled`. PLL prepare uses `sprd_pll_sc_gate_prepare` with `udelay`.

## Control Flow
Enable/disable callbacks compute whether setting a bit means enable or disable, then either update the base register or write the mask to a set/clear companion register. `is_enabled` optionally checks the parent first for `SPRD_GATE_NON_AON`, reads the base register, applies `CLK_GATE_SET_TO_DISABLE`, and returns bit state.

## State And Persistence
Gate state persists in hardware enable registers. Set/clear gates write transient command registers but read state from the base register. The only in-memory state is each gate's mask, flags, set/clear offset, and delay.

## Dependencies And Integration Points
Depends on CCF gate semantics, regmap, delay APIs, and parent-clock state checks. SoC files use gate macros for PMU, AHB/APB, AON, multimedia, and PLL enable controls.

## Risks And Edge Cases
Normal gates do read-modify-write without a local lock and ignore regmap errors. Set/clear offset must match hardware layout exactly. `SPRD_GATE_NON_AON` prevents reads while parent power is off, but incorrect parent modeling can still cause unsafe reads. PLL gates need correct settle delays.

## Test Signals
Enable/disable tests should confirm base/set/clear register writes and `is_enabled` behavior. Boot should avoid unused critical gates being shut off incorrectly. PLL consumers should work after prepare delays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/gate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/gate.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sprd/gate.h

## Purpose
Declares Spreadtrum gate clock structures, flags, and macro families for normal, set/clear, PLL set/clear, parent-hw, and firmware-name parents.

## Important APIs, Types, And Functions
`struct sprd_gate` stores enable mask, flags, set/clear offset, optional delay, and common clock data. `SPRD_GATE_NON_AON` marks gates whose register block should be read only when the parent is enabled. Macro families include `SPRD_GATE_CLK`, `SPRD_SC_GATE_CLK`, `SPRD_PLL_SC_GATE_CLK`, and `_HW`/`_FW_NAME` variants.

## Control Flow
Macro expansion chooses one of the exported ops tables and initializes static gate objects. Runtime behavior is provided by `gate.c`.

## State And Persistence
Static metadata persists masks, flags, register offsets, and delay settings. Hardware stores the actual enable state.

## Dependencies And Integration Points
Includes `common.h` and is consumed by SoC clock tables for most domain enable clocks. The flags intentionally share CCF gate flag values and add Spreadtrum-specific bits from bit 3 upward.

## Risks And Edge Cases
The macro matrix is broad; choosing the wrong parent form or ops table can create a clock that registers but cannot safely control hardware. `CLK_GATE_HIWORD_MASK` is reserved by comments but not implemented in `gate.c`, so users must not assume generic gate semantics unless code supports them.

## Test Signals
Compile tests for all macro variants, clock summary parent correctness, and hardware toggling checks for normal gates, set/clear gates, PLL gates, and non-AON gates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/gate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/mux.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sprd/mux.c

## Purpose
Implements Spreadtrum mux-only clocks and helper routines reused by composite clocks.

## Important APIs, Types, And Functions
Exports `sprd_mux_ops`, `sprd_mux_helper_get_parent`, and `sprd_mux_helper_set_parent`. `sprd_mux_ops` provides get/set parent plus `__clk_mux_determine_rate`.

## Control Flow
Get-parent reads the mux field from the register. Without a table it returns the raw encoded value; with a table it maps sparse or ranged hardware encodings back to CCF parent indexes. Set-parent optionally maps the CCF index through the table, clears the mux field, and writes the encoded value.

## State And Persistence
Parent selection persists in hardware registers. In-memory state is limited to mux shift, width, optional table, and common register metadata.

## Dependencies And Integration Points
Depends on CCF parent APIs, regmap, and `mux.h`. Composite clocks call the helper functions; SoC files instantiate standalone muxes for bus, reference, and peripheral selectors.

## Risks And Edge Cases
Table mapping assumes monotonic table values and treats the last parent as a fallback. Read/write errors are ignored. Read-modify-write is not locally locked, so fields sharing a register require care.

## Test Signals
Parent switching should update expected register bits and clock summary parent names. Sparse-table muxes such as MCU selectors need explicit tests for each encoded parent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/mux.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sprd/mux.h

## Purpose
Defines Spreadtrum mux clock structures, initialization macros, and helper prototypes.

## Important APIs, Types, And Functions
`struct sprd_mux_ssel` describes source-select shift, width, and optional hardware encoding table. `struct sprd_mux` combines that metadata with `sprd_clk_common`. Macros include `SPRD_MUX_CLK`, `SPRD_MUX_CLK_TABLE`, `SPRD_MUX_CLK_DATA`, and table/data variants. `hw_to_sprd_mux` performs container conversion.

## Control Flow
No direct control flow. Macro expansion binds static mux objects to `sprd_mux_ops`; callbacks in `mux.c` perform register reads and writes.

## State And Persistence
Stores static parent selection metadata and common register information. Parent choice persists in the hardware field.

## Dependencies And Integration Points
Includes `common.h`; included by `composite.h` and SoC files. Parent data variants support modern DT parent descriptions.

## Risks And Edge Cases
Sparse table values must match hardware encodings and parent order. Width/shift mistakes can corrupt adjacent fields. Parent-name versus parent-data macro mismatches can break clock resolution.

## Test Signals
Build coverage for macro variants and runtime parent-resolution tests using `clk_summary` and DT consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/mux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sprd/pll.c

## Purpose
Implements adjustable Spreadtrum PLL clocks, including multi-register factor extraction, fractional rate calculation, PLL rate programming, ibias selection, and settle delays.

## Important APIs, Types, And Functions
Exports `sprd_pll_ops`. Key helpers are `sprd_pll_read`, `sprd_pll_write`, `pll_get_refin`, `pll_get_ibias`, `_sprd_pll_recalc_rate`, and `_sprd_pll_set_rate`. Bit-field macros (`pindex`, `pshift`, `pmask`, `pinternal_val`) interpret `struct clk_bit_field` descriptions.

## Control Flow
Rate recalculation allocates a config snapshot for all PLL registers, determines reference input, applies pre/post divider semantics, and computes integer or SDM fractional output. Rate setting allocates per-register masks/values, derives postdiv, DIV_S, SDM_EN, NINT, KINT, and IBIAS values, writes each changed register, verifies written bits, and delays if all writes matched.

## State And Persistence
PLL configuration persists in hardware registers. The driver stores factor metadata, register count, ibias threshold table, fractional constants, FVCO threshold, flag semantics, and delay.

## Dependencies And Integration Points
Depends on regmap, delay, slab allocation, and CCF. SoC PLL descriptors in SC9860/SC9863A provide the factor maps and ibias tables. PLL gates in `gate.c` often parent these PLLs.

## Risks And Edge Cases
Allocation failure returns parent rate or `-ENOMEM`. Read/write errors are mostly ignored except writeback comparison. `determine_rate` returns 0 without adjusting the request, so CCF may accept unsupported targets until set-rate quantizes them. Factor descriptions spanning registers must be exact, or rate math corrupts PLL programming. `do_div` mutates operands, so maintenance needs care.

## Test Signals
Hardware tests should verify PLL recalc against known register defaults, set-rate to representative integer and fractional targets, ibias field selection across thresholds, writeback verification failures, and required settle delays before consumers run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/pll.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sprd/pll.h

## Purpose
Declares PLL data structures, factor indexes, and constructor macros for Spreadtrum PLL clocks.

## Important APIs, Types, And Functions
`struct reg_cfg` stores pending register value/mask pairs. `struct clk_bit_field` maps factor shift and width. The PLL factor enum covers lock, div mode, modulation, SDM, reference input, ibias, N/NINT/KINT, prediv, and postdiv. `struct sprd_pll` stores register count, ibias table, factor table, delay, fractional constants, FVCO behavior, and common clock data. Macros include `SPRD_PLL_WITH_ITABLE_K_FVCO`, `SPRD_PLL_WITH_ITABLE_1K`, `SPRD_PLL_FW_NAME`, and `SPRD_PLL_HW`.

## Control Flow
No direct runtime flow. Macro expansion initializes static PLL objects that use `sprd_pll_ops`; runtime interpretation happens in `pll.c`.

## State And Persistence
The structure stores static PLL formula metadata and common register location. Hardware registers store the live PLL configuration.

## Dependencies And Integration Points
Includes `common.h` and is consumed by SC9860/SC9863A SoC files. Fixed-factor clocks often derive from these PLL `clk_hw` objects.

## Risks And Edge Cases
Factor table indexes must align exactly with the enum. `regs_num` controls bounds for register access and allocation, so an incorrect value can hide fields or trigger warnings. Ibias table element zero is a count, which is easy to misuse.

## Test Signals
Compile-time macro coverage, rate recalc/set-rate validation for each PLL descriptor, and comparing exposed fixed-factor child rates against expected PLL outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/pll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/sc9860-clk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sprd/sc9860-clk.c

## Purpose
Describes and registers the full Spreadtrum SC9860 clock topology: PMU gates, PLLs, AP clocks, always-on prediv clocks, AP/AON gates, secure MCU clocks, AGCP audio gates, GPU/VSP/CAM/DISP clocks and gates, and AP APB gates.

## Important APIs, Types, And Functions
The platform driver entry is `sc9860_clk_probe`. It uses `sprd_sc9860_clk_ids` match data to select one `sprd_clk_desc`, then calls `sprd_clk_regmap_init` and `sprd_clk_probe`. The file instantiates hundreds of static CCF objects through `CLK_FIXED_FACTOR`, `SPRD_SC_GATE_CLK`, `SPRD_GATE_CLK`, `SPRD_PLL_WITH_ITABLE_*`, `SPRD_MUX_CLK`, `SPRD_COMP_CLK`, and `SPRD_DIV_CLK`.

## Control Flow
Each compatible string maps to a descriptor for a separate register block, with comments recording physical base regions. Probe is generic: match compatible, initialize regmap for that block, then register the descriptor's onecell clock array. Parent dependencies cross descriptors by clock name, so PLL and fixed-factor clocks feed AP/AON/peripheral muxes and gates when all matching DT nodes probe.

## State And Persistence
Static descriptors hold clock metadata and onecell indexes from dt-bindings. Runtime state is regmap pointers installed into each `sprd_clk_common`, registered CCF clocks, and hardware register values changed by mux/divider/gate/PLL ops.

## Dependencies And Integration Points
Depends on Spreadtrum common helpers, dt-binding IDs for SC9860, CCF fixed-factor helpers, platform driver matching, and DT nodes with compatible strings such as `sprd,sc9860-pll`, `sprd,sc9860-aon-gate`, `sprd,sc9860-cam-gate`, and `sprd,sc9860-apapb-gate`. Consumers acquire clocks by phandle indexes.

## Risks And Edge Cases
Large static tables create high risk of mismatched ID indexes, wrong parent names, register offsets, or bit masks. Many gates use `CLK_IGNORE_UNUSED` to protect boot-critical clocks; removing one can break console, timers, or always-on infrastructure. Sparse mux table `mcu_table` must match hardware encoding. Cross-block probe ordering relies on CCF deferred resolution of parent names.

## Test Signals
Build with `CONFIG_SPRD_SC9860_CLK`, boot on SC9860 DT, and verify no provider registration errors. Check `clk_summary` for PLL children and domain clocks, exercise UART/I2C/SPI/SDIO/eMMC/GPU/VSP/CAM/DISP consumers, and confirm set/clear gate register writes through debug or hardware functionality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/sc9860-clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/sc9863a-clk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sprd/sc9863a-clk.c

## Purpose
Defines the Spreadtrum SC9863A clock providers and platform driver, covering PMU PLL gates, PLL/MPLL/RPLL/DPLL blocks, AON clocks, AP clocks, AHB/APB gates, multimedia gates, camera sensor gates, and AP APB gates.

## Important APIs, Types, And Functions
`sc9863a_clk_probe` is the platform probe. `sprd_sc9863a_clk_ids` maps compatible strings to descriptors. The file uses parent-data-aware macros (`SPRD_*_DATA`, `SPRD_*_HW`, `SPRD_*_FW_NAME`) in addition to fixed-factor and PLL macros, allowing direct `clk_hw` parent references and firmware-name parents.

## Control Flow
Each DT clock node probes independently, selects its descriptor, initializes the regmap, and registers the descriptor's onecell clocks. The topology starts with PLL gates and PLLs, derives fixed-factor PLL outputs, then provides AON/AP muxes, composites, dividers, and gates for CPU, buses, storage, display, GPU, multimedia, camera, timers, serial, SPI, I2C, and audio domains.

## State And Persistence
Static clock objects and onecell arrays encode all IDs and register fields. Runtime state is the assigned regmap, CCF registration records, OF providers, and hardware state in set/clear and configuration registers.

## Dependencies And Integration Points
Depends on dt-bindings for SC9863A, Spreadtrum common helper modules, regmap/syscon/MMIO access, CCF parent data APIs, and DT compatibles such as `sprd,sc9863a-aon-clk`, `sprd,sc9863a-ap-clk`, `sprd,sc9863a-mm-gate`, and `sprd,sc9863a-apapb-gate`.

## Risks And Edge Cases
This table mixes parent strings, firmware names, and direct `clk_hw` parent references; using the wrong macro can break parent lookup. Some fixed-factor `dpll1-*` children are parented from `dpll0.common.hw`, which should be checked against hardware intent. Critical gates use `CLK_IGNORE_UNUSED`, including console-related UART1 and always-on infrastructure. `SPRD_GATE_NON_AON` camera sensor gates depend on parent state checks to avoid unsafe reads.

## Test Signals
Boot SC9863A with all clock nodes present and inspect provider registration logs. Validate PLL and fixed-factor rates in `clk_summary`, confirm console UART remains enabled, test I2C/SPI/SDIO/eMMC/display/GPU/camera/audio consumers, and verify non-AON gate reads do not fault when the multimedia parent is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sprd/sc9863a-clk.c -->
