# Research: subset-b-001088

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-gate.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-gate.c

Purpose: generic common-clock gate implementation for clocks whose only hardware control is one register bit. It provides the reusable `clk_gate_ops` and registration/unregistration helpers used by many SoC drivers.

Important APIs, types, and functions: `struct clk_gate` is supplied by `<linux/clk-provider.h>`. `clk_gate_readl()` and `clk_gate_writel()` abstract normal vs big-endian MMIO. `clk_gate_endisable()` implements enable/disable writes, including `CLK_GATE_SET_TO_DISABLE` polarity and `CLK_GATE_HIWORD_MASK` write-mask semantics. Exported APIs include `clk_gate_is_enabled()`, `clk_gate_ops`, `__clk_hw_register_gate()`, `clk_register_gate()`, `clk_unregister_gate()`, `clk_hw_unregister_gate()`, and `__devm_clk_hw_register_gate()`.

Control flow: common clock core calls `.enable`, `.disable`, and `.is_enabled`. Registration builds `clk_init_data`, validates hiword bit indexes, allocates `struct clk_gate`, then registers either with `clk_hw_register()` or `of_clk_hw_register()` depending on the `dev`/`np` inputs. Devres registration wraps the raw registration and unregisters automatically through `devm_clk_hw_release_gate()`.

State and persistence: persistent state is the target MMIO bit and the allocated `clk_gate`; no disk or firmware state is stored. Optional spinlock serializes read-modify-write access. Hiword mode avoids read-modify-write by writing the mask in the upper halfword.

Dependencies and integration points: integrates with the Linux common clock framework, OF clock registration, device-managed resources, MMIO helpers, and optional caller-provided spinlocks. SoC drivers depend on it for simple gate leaves.

Risks and test signals: invalid hiword bit indexes are rejected, but callers must supply a valid mapped register and correct polarity flags. RMW mode can race with other fields unless a shared lock is passed. KUnit coverage is in `clk-gate_test.c` for registration, parent selection, normal/inverted gates, hiword writes, and `is_enabled()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-gate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-gate_test.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-gate_test.c

Purpose: KUnit test coverage for the generic gate clock in `clk-gate.c`. It verifies registration variants, enable/disable hardware bit behavior, inverted polarity, hiword-mask writes, parent propagation, and `is_enabled()` results.

Important APIs, types, and functions: `clk_gate_test_context` owns fake MMIO storage, parent clock, and gate clock. `clk_gate_register_test_*()` exercises device registration, parent-name, parent-data, legacy parent-data, parent-hw, and invalid hiword index paths. Runtime suites use `clk_prepare_enable()`, `clk_disable_unprepare()`, `clk_hw_is_enabled()`, and `clk_hw_is_prepared()`. Test init helpers register fixed-rate parents and gate clocks against fake `__iomem` memory.

Control flow: KUnit creates suites through `kunit_test_suites()`. Registration tests allocate clocks directly and unregister them in-test. Functional tests allocate context in suite `.init`, register a fixed-rate parent plus a gate, perform enable/disable operations, then clean up in `.exit`. Separate suites configure normal gate bit 5, inverted bit 15, hiword bit 9, and one-off `is_enabled` cases.

State and persistence: state is only fake little-endian register memory stored inside the KUnit context. No persistent state exists beyond each test case. The fake register is intentionally placed at the end of the context to let KASAN catch out-of-bounds register access.

Dependencies and integration points: depends on KUnit, platform device registration, fixed-rate clock helpers, common clock APIs, and the exported gate registration APIs. It is the direct test signal for `clk-gate.c`.

Risks and test signals: covers core gate semantics but not big-endian access or locking races. The hiword invalid test asserts bit indexes above 15 fail. The prepare/enable assertions also verify parent clock propagation through the common clock framework.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-gate_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-gemini.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-gemini.c

Purpose: Cortina Gemini SoC clock and reset controller driver. It supplies early fixed/factor clocks, later gated peripheral clocks, a custom PCI clock, and a self-deasserting reset controller for the Gemini syscon.

Important APIs, types, and functions: `gemini_gate_data` describes gate bits and parent names. `clk_gemini_pci` implements PCI rate, parent, and enable operations using `gemini_pci_clk_ops`. `gemini_reset` implements reset-controller callbacks through `gemini_reset_ops`. `gemini_cc_init()` performs early `CLK_OF_DECLARE_DRIVER` setup, while `gemini_clk_probe()` fills clocks that should defer until the platform driver binds.

Control flow: early init allocates `gemini_clk_data`, initializes all slots to `-EPROBE_DEFER`, reads `GEMINI_GLOBAL_STATUS`, registers `xtal`, `vco`, `ahb`, and `apb`, and exposes the onecell provider. Probe maps the syscon MMIO resource, obtains a regmap, registers the reset controller, derives CPU/security clocks from register fields, registers gate clocks using `CLK_GATE_SET_TO_DISABLE`, then adds TVC, PCI, and UART clocks.

State and persistence: state is held in syscon registers and the global `gemini_clk_data`. Gate bits default to ungated at boot. Reset writes are self-deasserting. No persistent storage exists beyond hardware register state.

Dependencies and integration points: integrates with syscon/regmap, reset-controller, DT bindings for Gemini clock/reset IDs, common clock fixed-rate/factor/gate helpers, and `builtin_platform_driver`.

Risks and test signals: several comments note unclear TVC and PCI parents, so rate accuracy is partly board-knowledge dependent. Gate RMW is protected by `gemini_clk_lock`. Reset status reads a self-clearing register, which may be transient. Test signals are boot probe success, onecell lookup by DT ID, PCI 33/66 MHz switching, and reset-controller consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-gemini.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-gpio.c

Purpose: GPIO-controlled clock provider for three variants: GPIO gate clocks, GPIO mux clocks, and gated fixed-rate clocks optionally backed by a regulator.

Important APIs, types, and functions: `struct clk_gpio` holds a GPIO descriptor and clock hardware. Gate ops are split between non-sleeping GPIO `.enable/.disable` and sleeping GPIO `.prepare/.unprepare`. Mux ops use `gpiod_get_value_cansleep()` and `gpiod_set_value_cansleep()`. `struct clk_gated_fixed` adds `supply` and `rate`; its ops combine regulator prepare state, GPIO output state, and fixed-rate recalc.

Control flow: `gpio_clk_driver_probe()` distinguishes `"gpio-mux-clock"` from `"gpio-gate-clock"`, validates mux parent count, gets the `select` or `enable` GPIO, registers a clock with parent data indexes, and publishes an OF provider. `clk_gated_fixed_probe()` reads `clock-frequency`, optional `clock-output-names`, optional `vdd` regulator, optional enable GPIO, selects sleeping or non-sleeping ops, registers the fixed clock, and publishes it.

State and persistence: clock state is GPIO output level and optional regulator enable state. Rate is stored in memory from firmware properties. There is no persistent software state across probe removal except hardware pin/regulator state managed by devres and providers.

Dependencies and integration points: depends on GPIO descriptor APIs, regulator framework, device properties, OF clock provider helpers, and common clock parent-data support. Built-in platform drivers bind DT-compatible nodes.

Risks and test signals: sleeping GPIOs must only be toggled in prepare paths; non-sleeping gates use enable paths. `clk_sleeping_gated_fixed_unprepare()` disables regulator before lowering GPIO, which may matter electrically. Mux requires exactly two parents. Test signals are DT probe, GPIO polarity behavior from descriptors, regulator enable/disable balance, and child clock parent/rate observations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-hi655x.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-hi655x.c

Purpose: clock provider for the Hi655x PMIC 32.768 kHz clock. It exposes one clock through the common clock framework and controls it through the parent PMIC regmap.

Important APIs, types, and functions: `struct hi655x_clk` links `struct hi655x_pmic` to `struct clk_hw`. `hi655x_clk_recalc_rate()` returns the fixed 32768 Hz rate. `hi655x_clk_enable()` updates `HI655X_CLK_SET` at `HI655X_CLK_BASE`; prepare/unprepare wrap it. `hi655x_clk_probe()` gets parent driver data, optional `clock-output-names`, registers the clock, and adds an OF provider.

Control flow: module platform probe allocates managed state, reads the parent MFD device data, initializes `clk_init_data`, registers with `devm_clk_hw_register()`, and exposes `of_clk_hw_simple_get()`. Runtime clock prepare/unprepare maps directly to regmap update calls.

State and persistence: hardware state is a PMIC register bit. Software state is devm-managed and tied to the platform device lifetime. The rate is constant and not persisted elsewhere.

Dependencies and integration points: depends on the Hi655x MFD/PMIC parent, regmap, platform driver infrastructure, OF properties on the parent node, and common clock provider APIs.

Risks and test signals: `hi655x_clk_is_prepared()` tests `val & HI655X_CLK_BASE`, which is suspicious because the enable mask is `HI655X_CLK_SET`; this may misreport prepared state. Probe assumes parent driver data is present. Test signals should include prepare/unprepare register updates, `is_prepared()` correctness, and provider lookup from PMIC child nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-hi655x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-highbank.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-highbank.c

Purpose: early OF clock driver for Calxeda Highbank PLL, CPU bus/peripheral, and eMMC peripheral clocks.

Important APIs, types, and functions: `struct hb_clk` stores a clock hw and register pointer. `clk_pll_ops` implements prepare/unprepare, enable/disable, recalc, determine, and set-rate for Highbank PLLs. `a9periphclk_ops`, `a9bclk_ops`, and `periclk_ops` implement derived clock rates and peripheral divider setting. `hb_clk_init()` is the shared OF registration helper.

Control flow: `CLK_OF_DECLARE` callbacks invoke `hb_clk_init()` with the right ops. The helper reads the per-node `reg` offset, finds the `"calxeda,hb-sregs"` system register node, maps registers, initializes parent/name data, registers the clock, and adds a simple OF provider. PLL set-rate calculates dividers, may enter bypass/reset to relock when `divf` changes, waits for lock bits, then restores external enable.

State and persistence: all state is MMIO PLL/divider registers plus allocated `hb_clk` instances. PLL prepare and set-rate busy-wait until lock bits are asserted. There is no devres cleanup for these early registered clocks.

Dependencies and integration points: depends on OF clock declarations, MMIO accessors, common clock divider math, and Highbank system-register DT layout.

Risks and test signals: lock waits have no timeout and can hang if hardware never locks. `BUG_ON(!hb_clk->reg)` is fatal for missing sysreg mapping. Set-rate only accepts even peripheral dividers. Test signals are boot-time clock registration, PLL rate recalc after bootloader setup, set-rate relock behavior, and eMMC divider programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-highbank.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-hsdk-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-hsdk-pll.c

Purpose: Synopsys HSDK PLL clock driver for ARC core, general-purpose, and HDMI PLLs. It maps requested rates to supported hardware PLL configurations and programs CGU registers.

Important APIs, types, and functions: `hsdk_pll_cfg` is a supported-rate table entry. `hsdk_pll_clk` stores MMIO register bases, optional core-specific register, device data, and clock hw. `hsdk_pll_devdata` selects a rate table and update callback. `hsdk_pll_ops` implements recalc, determine, and set-rate. `of_hsdk_pll_clk_setup()` registers the early core PLL; `hsdk_pll_clk_probe()` registers platform GP/HDMI PLLs.

Control flow: determine-rate chooses the nearest table rate. set-rate searches for an exact table entry and calls either common or core update. Common update writes PLL fields, delays 100 us, then checks lock and error bits. Core update also adjusts the core interface divider before or after the PLL transition depending on the 500 MHz threshold.

State and persistence: state is CGU PLL control/status registers and, for the core PLL, a special interface-divider register. No persistent software state exists beyond clock objects. The driver uses static tables rather than deriving arbitrary PLL parameters.

Dependencies and integration points: depends on platform resources, OF match data, early `CLK_OF_DECLARE` for CPU timer needs, common clock APIs, MMIO, and fixed parent count constraints.

Risks and test signals: common PLL probe does not map `spec_regs`, which is only needed by core data. Lock wait is a fixed delay followed by status checks, so slow hardware can fail with `-ETIMEDOUT`. Unsupported exact rates return `-EINVAL` even if determine-rate would round. Test signals include nearest-rate decisions, exact set-rate success, lock/error handling, and early core clock availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-hsdk-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-k210.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-k210.c

Purpose: Canaan Kendryte K210 SoC clock controller driver. It registers PLL0/1/2, ACLK, and all SoC gate/divider/mux clocks from sysctl registers, plus an early helper to enable PLL1 for AI SRAM.

Important APIs, types, and functions: `k210_clk_cfg` describes per-clock gate/divider/mux fields. `k210_pll` and `k210_sysclk` hold PLL and controller state. `k210_pll_ops` and `k210_pll2_ops` implement PLL enable/disable/recalc and PLL2 parent selection. `k210_aclk_ops` manages CPU/ACLK parent and divider. `k210_clk_ops` and `k210_clk_mux_ops` implement child gates, dividers, and muxes. `k210_clk_init()` is the `CLK_OF_DECLARE` entry.

Control flow: init allocates `k210_sysclk`, maps parent sysctl registers, registers PLLs, registers ACLK, then registers critical CPU/SRAM/AI clocks and all peripheral clocks by parent group. A final loop verifies every `K210_NUM_CLKS` entry registered before publishing the onecell provider. PLL enable may reparent ACLK to the input oscillator before changing PLL0, programs PLL factors, pulses reset with reference-SDK NOPs, waits for lock, enables PLL output, then restores ACLK to PLL0.

State and persistence: state is sysctl MMIO plus in-memory clock descriptors. A global spinlock serializes PLL, mux, and gate register updates. Critical flags keep CPU/SRAM/AI clocks from being disabled.

Dependencies and integration points: depends on K210 sysctl register definitions, DT clock IDs, OF early clock registration, common clock framework, MMIO, and spinlocks.

Risks and test signals: PLL lock wait has no timeout. `k210_aclk_set_selector()` clears with `reg &= K210_ACLK_SEL`, which appears to preserve only the selector bit rather than clearing it while preserving other fields. Registration aborts silently if any clock ID remains unset. Test signals are boot-time CPU rate log, provider lookups for all IDs, PLL1 early init, critical clock retention, and mux/divider register behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-k210.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-lan966x.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-lan966x.c

Purpose: Microchip LAN966x/LAN969x generic clock controller driver. It registers per-peripheral generic clocks with parent mux and prescaler controls, and optional additional simple gate clocks from a second MMIO resource.

Important APIs, types, and functions: `lan966x_gck` stores one generic clock register. `lan966x_gck_ops` implements enable/disable, set/recalc/determine rate, and get/set parent. `clk_gate_soc_desc` describes optional gate clocks. `lan966x_match_data` selects SoC-specific names, counts, and gate descriptors.

Control flow: probe reads match data, allocates `clk_hw_onecell_data`, maps resource 0 as the generic clock base, sets shared init ops, registers each generic clock at `base + i * 4`, then optionally maps resource 1 and registers SoC gate clocks. Finally it exposes the onecell provider with either generic-only or total clock count.

State and persistence: hardware state is per-clock `GCK_ENA`, `GCK_SRC_SEL`, and `GCK_PRESCALER` fields plus optional gate bits. Software state is devm-managed. A file-scope `base` is used during registration.

Dependencies and integration points: depends on platform resources, OF match data, common clock onecell provider, `FIELD_GET/PREP`, and generic gate helpers with a shared spinlock.

Risks and test signals: `lan966x_gck_set_rate()` does not validate divider overflow or exact divisibility; a zero divider can underflow if requested rate exceeds parent rate. `hw_data->num` changes only when resource 1 exists, so DT IDs differ by available resource. The global `base` is not per-device safe if multiple instances were ever probed. Test signals are DT binding coverage for both SoCs, parent selection, prescaler programming, and optional gate resource presence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-lan966x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-lmk04832.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-lmk04832.c

Purpose: SPI common-clock driver for the TI LMK04832 ultra-low-noise clock jitter cleaner. It models OSCin to VCO, SYSREF/SCLK, paired DCLKs, and 14 CLKOUT outputs as a clock tree.

Important APIs, types, and functions: `lmk04832_device_info` stores chip identity and VCO ranges. `struct lmk04832` owns regmap, input clock, reset GPIO, VCO/SCLK hw, DCLK/CLKOUT arrays, SYSREF/SYNC properties, and onecell provider data. `lmk04832_vco_ops`, `lmk04832_sclk_ops`, `lmk04832_dclk_ops`, and `lmk04832_clkout_ops` implement rate, prepare, mux, and enable behavior. `lmk04832_sclk_sync_sequence()` performs the deterministic SYSREF/DCLK synchronization flow.

Control flow: probe gets enabled `oscin`, optional reset GPIO, allocates clock arrays, reads TI-specific firmware properties and child CLKOUT format/sysref settings, initializes regmap, resets the chip, optionally configures 4-wire SPI readback, verifies product ID and mask revision, registers VCO, optionally sets its rate, registers SCLK, registers every paired DCLK and CLKOUT, and publishes a onecell provider. Rate changes on SCLK or DCLK program divider registers and rerun the sync sequence.

State and persistence: hardware state is entirely in LMK registers over SPI. The driver also keeps desired `clkout.format`, `sysref` source choice, SYSREF delay, pulse count, mux mode, and VCO target in memory from DT properties. Regmap has no cache, so reads/writes hit hardware.

Dependencies and integration points: depends on SPI, regmap, GPIO, parent `oscin` clock, OF child nodes, common clock framework, gcd/divider math, and TI LMK register semantics.

Risks and test signals: there are several correctness-sensitive details: VCO range validation, PLL2 divider limits, SYSREF divider range, DCLK divide-by-2/3 workaround, and the long sync register sequence. `lmk04832_clkout_is_enabled()` returns `enabled && !fmt`, which appears inverted relative to a nonzero active format and should be tested. Test signals include ID readback, provider registration for 14 outputs, exact rate acceptance/rejection, sync sequence failures, and suspend-free hardware reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-lmk04832.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-lochnagar.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-lochnagar.c

Purpose: Cirrus Logic Lochnagar board clock driver for Lochnagar 1 and 2 MFD variants. It exposes board clock outputs with selectable parents and enable bits via the parent regmap.

Important APIs, types, and functions: `lochnagar_clk` stores per-clock register/mask metadata and a `clk_hw`. `lochnagar_clk_priv` owns regmap and the fixed-size clock array. `lochnagar_config` selects parent lists and clock descriptions for Lochnagar 1 or 2. `lochnagar_clk_ops` implements prepare/unprepare and parent set/get. `lochnagar_of_clk_hw_get()` indexes clocks from DT phandles.

Control flow: probe allocates private data, obtains parent regmap, copies the variant clock table, initializes shared parent data, registers each named clock, then registers a custom OF provider. Prepare sets the enable mask in `cfg_reg`; unprepare clears it. Parent changes update `src_reg` with the raw parent index.

State and persistence: state is MFD register bits for enable and source selection. The copied clock array stores per-device metadata and backpointers. No persistent software state exists.

Dependencies and integration points: depends on Lochnagar MFD register definitions, DT clock bindings, regmap, platform driver matching, firmware parent names, and common clock APIs.

Risks and test signals: `get_parent()` returns `clk_hw_get_num_parents()` on regmap read failure, intentionally producing an invalid parent index. Source masks assume register values map directly to parent indexes. Probe assumes match data and parent regmap are valid. Test signals are variant-specific clock count/name registration, phandle index validation, enable bit writes, and parent switch register values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-lochnagar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-loongson1.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-loongson1.c

Purpose: early OF clock driver for Loongson-1 LS1B and LS1C SoCs. It registers PLL, CPU, DC, AHB, and APB clocks with SoC-specific divider layouts.

Important APIs, types, and functions: `ls1x_clk_pll_data` describes fixed/integer/fractional PLL fields. `ls1x_clk_div_data` describes divider fields, bypass bits, optional divider tables, and lock. `ls1x_clk` binds a register offset and data block to `clk_hw`. Macro-generated `LS1X_CLK_PLL` and `LS1X_CLK_DIV` instances define the LS1B/LS1C clock trees. `ls1x_clk_init()` maps registers and registers onecell clocks.

Control flow: OF init maps the controller, iterates the onecell array, assigns register pointers to non-APB custom clocks, registers each clock, then adds the onecell provider. Divider set-rate locks, bypasses the clock according to bypass polarity, updates divider bits, restores normal path, and unlocks.

State and persistence: state is clock controller MMIO and static clock objects. A global spinlock protects divider register changes. The fixed APB clocks are static fixed-factor children.

Dependencies and integration points: depends on Loongson DT clock IDs, OF early registration, common clock divider helpers, MMIO, and spinlocks.

Risks and test signals: `ls1x_pll_rate_part()` uses `GENMASK(shift + width, shift)`, which may include one extra bit compared with typical width handling. Error cleanup unregisters clocks while iterating backward but sparse arrays need care. Test signals are LS1B/LS1C rate recalc from boot registers, divider set-rate bypass behavior, onecell IDs, and APB fixed-factor propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-loongson1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-loongson2.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-loongson2.c

Purpose: platform clock driver for Loongson2/LS2K SoC families. It registers PLL, scale, divider, gate, and fixed clocks from SoC-specific clock tables.

Important APIs, types, and functions: `loongson2_clk_board_info` is the central table format, with macros for `CLK_PLL`, `CLK_SCALE`, `CLK_SCALE_MODE`, `CLK_DIV`, `CLK_GATE`, and `CLK_FIXED`. `loongson2_clk_provider` owns MMIO base, device, lock, and onecell data. Custom recalc ops handle PLL and frequency-scale clocks; standard common-clock helpers register dividers, gates, and fixed-rate clocks.

Control flow: probe gets match data and reference clock parent name, computes the maximum clock ID, allocates a flexible provider, maps registers, initializes all onecell slots to `-ENOENT`, then iterates table entries. Each entry selects a registration path based on type and stores the resulting hw by table ID. The provider is added after all entries register.

State and persistence: hardware state is 64-bit clock control registers read through non-atomic lo/hi helpers. Divider/gate updates use a provider spinlock. Table data is static and the provider is devm-managed.

Dependencies and integration points: depends on Loongson DT clock bindings, OF/platform matching for multiple compatible strings, common gate/divider/fixed helpers, 64-bit MMIO accessors, and onecell provider consumers.

Risks and test signals: the probe loop indexes `data[i]` up to `clks_num`, assuming table IDs are dense and in order; sparse or out-of-order tables could read sentinel/invalid entries. PLL recalc divides by register `div` without zero guard. Gate bit indexes can exceed 31 for 64-bit registers while generic gate helpers operate on 32-bit registers, so high-bit gates need validation. Test signals are each compatible's full ID map, fixed clocks, high-bit gates, and rate recalc with bootloader-programmed PLLs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-loongson2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-max77686.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-max77686.c

Purpose: MFD child clock driver for Maxim MAX77686, MAX77802, and MAX77620 32 kHz clock outputs.

Important APIs, types, and functions: `max77686_hw_clk_info` describes each output name, register, enable mask, and flags. `max77686_clk_init_data` stores regmap, `clk_hw`, init data, and selected hardware info. `max77686_clk_driver_data` holds chip kind and clock array. `max77686_clk_ops` implements prepare/unprepare/is_prepared and fixed 32768 Hz recalc. `of_clk_max77686_get()` provides indexed DT lookup.

Control flow: probe obtains the parent MFD regmap, selects the chip-specific clock table from platform ID data, allocates clock data, reads optional parent `clock-output-names`, registers each clock and clkdev alias, optionally adds an OF provider, then enables low-jitter mode for MAX77802.

State and persistence: state is the PMIC RTC/32 kHz register bits and per-device devm-managed clock descriptors. Rate is fixed. Low-jitter mode is programmed once at probe for MAX77802.

Dependencies and integration points: depends on Maxim MFD IDs/regmaps, DT clock bindings, common clock framework, clkdev, and platform-device IDs from the parent MFD.

Risks and test signals: `max77686_clk_unprepare()` passes bitwise complement of the enable mask as the value to `regmap_update_bits()`; regmap masks it back down, but using zero would be clearer. Probe requires a valid platform ID and parent regmap. Test signals are per-chip clock counts, `clock-output-names` override, OF phandle indexes, low-jitter bit programming, and prepare-state reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-max77686.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-max9485.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-max9485.c

Purpose: I2C driver for the Maxim MAX9485 programmable audio clock generator. It exposes MCLK output, programmable CLKOUT, and two gated child outputs.

Important APIs, types, and functions: `max9485_rate` maps exact output rates to one-byte hardware register values. `max9485_driver_data` stores input clock, I2C client, shadow register value, regulator, reset GPIO, and four clock hw entries. `max9485_clk_hw` links each clock to an enable bit and driver data. `max9485_clkout_*` implements rate selection; `max9485_clk_prepare/unprepare()` toggles output enable bits.

Control flow: probe gets `xclk`, enables `vdd`, gets optional reset GPIO, reads the current device register into `reg_value`, registers four clocks with parent relationships, and adds an OF provider. `max9485_update_bits()` updates the shadow byte then sends it over I2C. Suspend deasserts reset; resume reasserts reset and writes the shadow register back.

State and persistence: the single hardware register is mirrored in `drvdata->reg_value`; this shadow is the source for rate recalc and resume restore. The supply regulator is enabled at probe and not disabled by a local remove path because devm/resource teardown owns it.

Dependencies and integration points: depends on I2C, regulator, GPIO, parent input clock, DT clock-output names, common clock framework, and PM sleep ops.

Risks and test signals: `max9485_update_bits()` mutates the shadow before knowing whether I2C send succeeded, so failed writes can desynchronize software and hardware. `max9485_of_clk_get()` lacks bounds checking. Parent selection uses `parent_index > 0`, so index 0 is treated as external xclk rather than an internal parent. Test signals are exact/rounded rate selection, suspend/resume restore, I2C failure behavior, and phandle index validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-max9485.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-milbeaut.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-milbeaut.c

Purpose: Socionext Milbeaut M10V clock controller driver. It provides early PLL/fixed/rclk setup and platform-probed divider/mux clocks for the full clock controller.

Important APIs, types, and functions: data tables describe fixed-factor PLLs, fixed dividers, programmable dividers, and muxes. Custom `m10v_mux_ops` write mux values with a write-enable bit. `m10v_clk_divider` extends divider behavior with an optional `write_valid_reg` handshake. `m10v_cc_init()` is the early `CLK_OF_DECLARE_DRIVER` path; `m10v_clk_probe()` completes deferred clocks.

Control flow: early init allocates global onecell data, maps registers, initializes all exported clocks to `-EPROBE_DEFER`, registers bootloader-programmed PLL fixed factors, registers `rclk` needed by timers, and adds the provider. Platform probe maps the same block, registers programmable dividers, fixed dividers, and muxes, then verifies all exported IDs have real clocks. Divider set-rate writes value plus write-enable bit and optionally polls `CLKSEL(11)` until hardware clears the request.

State and persistence: state is MMIO register fields and global `m10v_clk_data`. Some clocks are early fixed-factor representations of bootloader state. A global spinlock protects mux/divider RMW.

Dependencies and integration points: depends on OF early clock setup, platform driver probing, common clock fixed/divider/mux helpers, MMIO polling, and Milbeaut register layout.

Risks and test signals: `m10v_clk_data` is global and shared across early/probe phases. Several custom registrations allocate with `kzalloc` and no explicit unregister in normal built-in use. Poll timeout only logs an error but still returns success. Test signals are timer availability from early `rclk`, later replacement of deferred clocks, divider handshake behavior, and onecell exported IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-milbeaut.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-moxart.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-moxart.c

Purpose: early OF clock driver for MOXA ART SoC PLL and APB clocks, represented as fixed-factor clocks derived from boot-time register strap values.

Important APIs, types, and functions: `moxart_of_pll_clk_init()` reads PLL multiplier from offset `0x30`, registers a fixed-factor clock, creates a clkdev alias, and adds a simple OF provider. `moxart_of_apb_clk_init()` reads APB divider selector from offset `0x0c`, maps it through `div_idx`, doubles it, and registers the APB fixed-factor clock.

Control flow: each `CLK_OF_DECLARE` callback reads optional `clock-output-names`, gets parent name, maps the node, reads the relevant field, unmaps the node, checks that the parent clock can be obtained, registers the fixed-factor clock, registers clkdev, and adds the provider.

State and persistence: no mutable software state is retained except registered clock objects. Hardware register values are sampled once at boot and modeled as fixed factors.

Dependencies and integration points: depends on OF early clock init, MMIO mapping, common fixed-factor registration, clkdev, and parent clocks described in DT.

Risks and test signals: `of_clk_get()` references are not released with `clk_put()`. If fixed-factor registration fails after mapping has been unmapped there is no allocated private state to clean, but parent references still matter. APB selector values above 4 silently fall back to index 0. Test signals are boot clock rates from strap registers, provider lookup, and clkdev alias availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-moxart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-multiplier.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-multiplier.c

Purpose: generic common-clock multiplier implementation. It calculates, selects, and programs integer multiplier fields in MMIO registers.

Important APIs, types, and functions: `struct clk_multiplier` is supplied by the clock provider headers. `clk_mult_readl()` and `clk_mult_writel()` abstract endian mode. `clk_multiplier_recalc_rate()` reads the multiplier field and applies `CLK_MULTIPLIER_ZERO_BYPASS`. `__bestmult()` chooses a multiplier, optionally asking the parent to round its rate when `CLK_SET_RATE_PARENT` is set. `clk_multiplier_ops` exports recalc, determine-rate, and set-rate.

Control flow: determine-rate computes the best multiplier and adjusted parent rate, then returns the resulting output rate. set-rate computes the target factor, locks if provided, read-modify-writes the multiplier field, and unlocks. Recalc reads the current field and multiplies the parent rate.

State and persistence: persistent state is only the hardware multiplier field. Software state is the `clk_multiplier` object supplied by the registering driver. Optional locking protects shared registers.

Dependencies and integration points: integrates with common clock rate negotiation, parent-rate rounding, MMIO helpers, endian flags, spinlocks, and exported `clk_multiplier_ops` used by platform drivers.

Risks and test signals: no explicit range check in set-rate means callers rely on prior determine-rate or hardware field truncation behavior. `__bestmult()` iterates `i < maxmult`, excluding the maximum possible encoded multiplier from parent-rate search. Test signals should cover zero-bypass, round-closest, set-rate-parent negotiation, endian access, and max multiplier boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-multiplier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-mux.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-mux.c

Purpose: generic common-clock mux implementation for clocks that select one parent from a register field. It also provides registration/unregistration helpers and conversion helpers for table/index encodings.

Important APIs, types, and functions: `clk_mux_val_to_index()` maps raw hardware values to parent indexes using optional tables, one-based indexes, or bit indexes. `clk_mux_index_to_val()` performs the inverse. `clk_mux_ops` supports get/set parent and rate determination; `clk_mux_ro_ops` supports read-only muxes. `__clk_hw_register_mux()`, `__devm_clk_hw_register_mux()`, `clk_register_mux_table()`, `clk_unregister_mux()`, and `clk_hw_unregister_mux()` are exported.

Control flow: get-parent reads, shifts, masks, and converts the register value. set-parent converts the requested index, locks if provided, either writes a hiword mask or performs RMW, then writes the new value. Registration validates hiword width, allocates `struct clk_mux`, fills `clk_init_data` with parent names/hws/data, selects writable or read-only ops, and registers with device or OF context.

State and persistence: hardware state is the mux register field. Software state is allocated mux metadata and optional table. Hiword mode avoids preserving unrelated fields through RMW. Optional locks protect shared registers.

Dependencies and integration points: core common-clock helper used by many platform drivers. Depends on MMIO accessors, endian flags, OF/device registration, devres, and clock rate helper `clk_mux_determine_rate_flags()`.

Risks and test signals: invalid hardware values return `-EINVAL` from a function typed as `u8` in get-parent paths, which can become an out-of-range parent index. Caller-provided masks/tables must match parent count. Test signals include table and index modes, hiword validation, read-only mux behavior, endian access, and devm unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-nomadik.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-nomadik.c

Purpose: ST-Ericsson Nomadik SRC clock implementation. It initializes oscillator policy, exposes PLL and source-gated clocks, registers HCLK divider clocks, and provides debugfs visibility.

Important APIs, types, and functions: `nomadik_src_init()` maps the SRC block, configures timer clock source bits, handles DT oscillator-disable properties, and registers a reboot notifier. `clk_pll` and `pll_clk_ops` model PLL1/PLL2. `clk_src` and `src_clk_ops` model peripheral gates with separate enable/disable/status registers. OF setup functions register PLL, HCLK divider, and SRC clocks.

Control flow: each OF clock setup lazily calls `nomadik_src_init()` if the SRC base is not mapped. PLL enable/disable updates `SRC_PLLCR`, respecting PLL1 override semantics. SRC enable writes the enable register and spins until status is set; disable writes the disable register and spins until status clears. Reboot handler force-enables the main crystal so reset can complete.

State and persistence: global `src_base` and boot debugfs snapshots persist for the system lifetime. Hardware state includes oscillator control, PLL control, peripheral enable/status registers, and divider bits. A spinlock protects `SRC_CR`/PLL RMW operations.

Dependencies and integration points: depends on OF early clocks, MMIO, reboot notifier, common clock divider helper, debugfs/seq_file when enabled, and Nomadik DT properties.

Risks and test signals: enable/disable loops have no timeout. The reboot notifier depends on `src_base` being initialized. Debugfs captures boot state after SRC init only. Test signals are oscillator DT property effects, PLL rate recalc, peripheral gate status transitions, HCLK divider rate, reboot path, and debugfs output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-nomadik.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-npcm7xx.c -->
# sources/distributed-fs/ceph-client/drivers/clk/clk-npcm7xx.c

Purpose: Nuvoton NPCM7xx clock generator driver. It is read-mostly: bootloader initializes hardware, and the driver registers PLLs, muxes, fixed dividers, and dividers so consumers can query current rates.

Important APIs, types, and functions: `npcm7xx_clk_pll` and `npcm7xx_clk_pll_ops` recalculate PLL rates from PLLCON fields. Tables `npcm7xx_plls`, `npcm7xx_muxes`, and `npcm7xx_divs` describe all registered clocks and exported onecell IDs. `npcm7xx_clk_init()` is the `CLK_OF_DECLARE` entry.

Control flow: init converts the DT resource to an MMIO mapping, allocates onecell data, initializes exported IDs to `-EPROBE_DEFER`, registers PLLs, registers fixed `/2` PLL clocks, registers mux-table clocks against `CLKSEL`, registers divider clocks against `CLKDIV*`, and adds the OF provider. Failures free the onecell data and unmap the base.

State and persistence: hardware state is bootloader-programmed clock generator registers. Software state is allocated clock objects and onecell data. A global spinlock protects mux/divider operations even though the driver comments emphasize reading current settings.

Dependencies and integration points: depends on DT clock bindings, OF early clock setup, common clock mux/divider/fixed-factor helpers, MMIO, bitfield helpers, and onecell provider consumers.

Risks and test signals: PLL recalc divides by `indv * otdv1 * otdv2` without zero checks. `of_node_put(clk_np)` is called on the node passed to the OF declare callback, which may not be owned by the function. Error paths do not unregister already registered clocks. Test signals are exported ID coverage, PLL recalc from real boot registers, mux table mappings, divider rates, and failure behavior on invalid register fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-npcm7xx.c -->
