# Research: subset-b-001172

This grouped report covers Samsung, SiFive, and Intel SoCFPGA clock-controller source files under `sources/distributed-fs/ceph-client/drivers/clk/`. Each source file has its own source-path-preserving section for reconciliation into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-pll.c

Purpose: implements Samsung common clock framework PLL providers. It converts SoC PLL descriptor records from `struct samsung_pll_clock` into `struct clk_hw` instances and supplies per-PLL-family `clk_ops` for rate recalculation, rate selection, rate programming, enable, disable, and lock waiting.

Important APIs/types/functions: the private `struct samsung_clk_pll` stores `clk_hw`, MMIO lock/control registers, type, enable/lock bit offsets, and an optional copied `samsung_pll_rate_table`. `_samsung_clk_register_pll()` selects ops for every `enum samsung_pll_type` and registers the PLL; `samsung_clk_register_pll()` iterates descriptor arrays. Shared helpers include `samsung_get_pll_settings()`, `samsung_pll_determine_rate()`, `samsung_pll_lock_wait()`, and `samsung_pll3xxx_enable()/disable()`. PLL families implemented include 2126, 3000, 35xx/142xx/A9FRACM, 36xx/2650, 0822x/0831x, 45xx, 46xx/1460x, 6552/6553, 2550x/2550xx, 2650x/2650xx, 531x/4311, 1031x, and A9FRACO.

Control flow: registration allocates one PLL object, initializes parent/name/flags, duplicates the rate table when present, chooses full ops when programming is possible and minimal recalc ops otherwise, maps `lock_reg` and `con_reg` from the Samsung provider base, registers with CCF, then stores the hardware pointer in the provider lookup table. Runtime rate ops read register fields, compute VCO/output with `do_div()` or `div64_u64()`, and set-rate paths locate exact table entries, update PMS/K/AFC/MFR/MRR/VSEL fields, set lock time, write MMIO, and poll lock bits when required.

State and persistence: state lives in PLL hardware registers and in the in-memory copied rate table. There is no explicit suspend code here; Samsung CMU code saves/restores registers using lists supplied by SoC files. Lock waits use atomic polling rather than timekeeping, which matters during early boot and suspend paths.

Dependencies/integration: depends on Linux CCF, relaxed MMIO, `readl_relaxed_poll_timeout_atomic()`, Samsung `clk.h` descriptors, and rate tables built with `clk-pll.h` macros. SoC files pass descriptors into `samsung_clk_register_pll()`.

Risks: exact-rate tables must be sorted descending and terminated by zero; missing tables silently expose read-only recalc-only PLLs. Hardware bitfield differences are dense and easy to regress. The local source contains duplicated `pr_err()` text in `samsung_pll35xx_set_rate()`, which looks like a copied-source defect worth build-checking. Rate programming can temporarily bypass/disable PLLs, so parent/bypass mux sequencing is critical for A9FRACO and related families.

Test signals: build with Samsung clock drivers enabled, boot DT platforms that instantiate multiple PLL types, inspect `/sys/kernel/debug/clk/clk_summary`, exercise `clk_set_rate()` for PLLs with tables, test suspend/resume lock recovery, and confirm invalid rates return `-EINVAL` without register writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-pll.h -->
# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-pll.h

Purpose: declares Samsung PLL family identifiers and rate-table construction helpers shared by Samsung SoC clock drivers and `clk-pll.c`.

Important APIs/types/functions: `enum samsung_pll_type` enumerates all supported hardware layouts. `struct samsung_pll_rate_table` stores output rate plus m/p/s/k/afc/mfr/mrr/vsel fields. Macros such as `PLL_RATE`, `PLL_VALID_RATE`, `PLL_FRACO_RATE`, `PLL_35XX_RATE`, `PLL_36XX_RATE`, `PLL_4508_RATE`, `PLL_4600_RATE`, `PLL_4650_RATE`, and `PLL_A9FRACO_RATE` create table entries and can compile-time validate requested output rates.

Control flow: no runtime code. The header shapes compile-time descriptor data that SoC tables pass through `struct samsung_pll_clock` to `samsung_clk_register_pll()`.

State and persistence: no storage beyond generated constant tables. Correctness persists through static table definitions and sentinel termination expected by the registration code.

Dependencies/integration: included by Samsung common `clk.h` and PLL implementations. It relies on kernel `BIT()` and `BUILD_BUG_ON_ZERO()` style compile-time checks from included kernel headers.

Risks: the table macros assume known reference frequency and exact integer arithmetic; incorrect `_fin`, shift width, or fractional encoding causes compile-time failures for validated macros or runtime wrong rates for hand-written entries. The note that rate tables must be sorted descending is relied on by `samsung_pll_determine_rate()`.

Test signals: compile SoC PLL tables with validation macros enabled, inspect generated rates through CCF, and add tests/reviews that every programmable PLL table is descending and zero-terminated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-pll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-s3c64xx.c -->
# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-s3c64xx.c

Purpose: describes and registers the common clock tree for Samsung S3C6400 and S3C6410 SoCs.

Important APIs/types/functions: `s3c64xx_clk_init()` is the main initializer; `s3c6400_clk_init()` and `s3c6410_clk_init()` are `CLK_OF_DECLARE` entry points. Static arrays define register save sets, parent lists, fixed clocks, muxes, dividers, gates, PLLs, and legacy clkdev aliases. Helper macros distinguish bus, source, and always-on gates.

Control flow: initialization maps the DT node if present, allocates a Samsung provider for `NR_CLKS`, optionally registers legacy fixed external clocks, registers PLLs, fixed internal clocks, common mux/div/gate tables, then selects S3C6400 or S3C6410-specific tables. It registers clkdev aliases, registers sleep-save lists, publishes the OF clock provider, and logs key derived rates.

State and persistence: `reg_base` and `is_s3c6400` are static boot-time state. Clock hardware state resides in CMU registers. Suspend/resume persistence is delegated to Samsung common sleep support using `s3c64xx_clk_regs` and extra S3C6410 registers.

Dependencies/integration: depends on `dt-bindings/clock/samsung,s3c64xx-clock.h`, Samsung `clk.h`/`clk-pll.h`, CCF, OF address mapping, and legacy device names for aliases used by non-DT board support.

Risks: shared tables contain many literal register offsets and bit positions; ID mismatches break DT consumers. Parent names such as `"none"` and SoC-specific parent differences can produce orphan clocks if changed. The local source has a duplicated `SCLK_LCD27` gate entry, which could duplicate registration of one ID/name. Legacy aliases are behavioral ABI for old board files.

Test signals: boot S3C6400 and S3C6410 DTs, confirm provider registration and rate log, check aliases for UART/MMC/I2S/USB devices, inspect clock summary for orphan/missing clocks, and run suspend/resume to validate saved CMU registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-s3c64xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-s5pv210-audss.c -->
# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-s5pv210-audss.c

Purpose: platform driver for the S5PV210-compatible audio subsystem clock controller.

Important APIs/types/functions: `s5pv210_audss_clk_probe()` maps ASS registers, allocates onecell clock data, obtains parent clocks (`hclk`, `fout_epll`, `sclk_audio0`, optional `iiscdclk0`, optional `xxti`), and registers mux/divider/gate clocks. `s5pv210_audss_clk_suspend()` and `s5pv210_audss_clk_resume()` save/restore ASS source/divider/gate registers via syscore ops.

Control flow: probe maps resources with `devm_platform_ioremap_resource()`, builds parent-name arrays from acquired clocks or fallback names, registers two muxes, two dividers, the I2S gate, and six HCLK gates. It validates every slot, publishes an OF onecell provider, then registers syscore suspend hooks when PM sleep is enabled. Error handling unregisters any successfully registered clocks.

State and persistence: static `reg_base` and `clk_data` point at the active controller; a global spinlock serializes register updates. PM state is a three-register `reg_save` array. Several HCLK gates are `CLK_IGNORE_UNUSED`, preserving audio subsystem access clocks.

Dependencies/integration: depends on platform device probing, DT compatible `"samsung,s5pv210-audss-clock"`, `dt-bindings/clock/s5pv210-audss.h`, parent clocks from the main CMU, CCF mux/divider/gate helpers, and syscore PM.

Risks: optional parents fall back to string names, so missing providers may leave orphans but not fail probe. Static globals assume a single controller instance. Provider add failure cleans clocks but syscore is only registered after provider success. Parent ordering is hardware ABI for mux fields.

Test signals: probe on S5PV210 audio DT, verify all `AUDSS_MAX_CLKS` slots are valid or expected, check I2S clock parent/rate changes, validate audio after suspend/resume, and test missing optional codec clock handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-s5pv210-audss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-s5pv210.c -->
# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-s5pv210.c

Purpose: main CMU clock-tree description for Samsung S5PV210 and S5P6442 SoCs.

Important APIs/types/functions: `__s5pv210_clk_init()` registers the tree; `s5pv210_clk_dt_init()` and `s5p6442_clk_dt_init()` are DT entry points. The file defines register offsets, PLL IDs, saved register list, many parent arrays, common and SoC-specific mux/divider/gate/fixed-factor/fixed-rate tables, PLL descriptors, and legacy aliases.

Control flow: DT init maps CMU registers and calls the shared initializer with a SoC selector. The initializer allocates a Samsung provider, registers the early read-only `fin_pll` mux before PLLs, selects S5PV210 or S5P6442 fixed-rate/PLL/mux/div/gate tables, then registers common mux/div/gate and fixed-factor tables. It adds aliases, registers sleep-save state, publishes the provider, and logs key PLL mux rates.

State and persistence: static `reg_base` is the CMU base. Hardware state spans source, mask, divider, gate, PLL, output, and misc registers. `s5pv210_clk_regs` drives save/restore across suspend through Samsung common syscore support.

Dependencies/integration: depends on `dt-bindings/clock/s5pv210.h`, Samsung `clk.h`/`clk-pll.h`, OF mapping, and CCF. Audio subsystem clocks consume names such as `sclk_audio0`.

Risks: the clock tree is large and register-table-driven; ID or name drift breaks DT consumers. S5P6442 shares many tables but has different parent availability and fixed USB PHY rate. The local source contains a duplicated `MOUT_D1SYNC` mux entry in the S5P6442 table. Legacy aliases remain important for old board/device integrations.

Test signals: boot both compatible strings, inspect `clk_summary` for missing or duplicated IDs, validate rates for PLLs/muxes such as APLL/MPLL/EPLL/VPLL, confirm audio/display/MMC/USB consumers resolve parents, and run suspend/resume register-retention tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-s5pv210.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk.c -->
# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk.c

Purpose: common Samsung clock-provider infrastructure used by Samsung SoC clock drivers.

Important APIs/types/functions: `samsung_clk_init()` allocates `struct samsung_clk_provider`; registration helpers add fixed-rate, fixed-factor, mux, divider, gate, alias, PLL, and CPU clocks. `samsung_cmu_register_clocks()` and `samsung_cmu_register_one()` register full CMU descriptors. Sleep support includes `samsung_clk_save()`, `samsung_clk_restore()`, `samsung_clk_alloc_reg_dump()`, and `samsung_clk_extended_sleep_init()`. Auto-gate support includes `samsung_is_auto_capable()`, `samsung_register_auto_gate()`, and `samsung_en_dyn_root_clk_gating()`.

Control flow: callers allocate a provider with a register base and clock ID count, invoke table registration helpers, then publish an OF onecell provider. CMU registration copies auto-gate/sysreg offsets, registers clock classes in PLL/mux/div/gate/fixed/CPU order, optionally registers register-save caches, enables dynamic root clock gating, and adds the provider.

State and persistence: provider state includes MMIO base, optional device, sysreg regmap, spinlock, auto-gate flags, offsets, and `clk_hw_onecell_data`. Suspend state is kept in a global `clock_reg_cache_list` and restored by syscore ops. Auto gate state is stored in hardware debug/sysreg registers.

Dependencies/integration: depends on Linux CCF, clkdev, OF provider APIs, syscon regmap, syscore PM, and Samsung descriptor types from `clk.h`.

Risks: registration helper failures generally log and continue, which can leave sparse providers. `samsung_clk_add_lookup()` ignores ID 0 by design, so descriptors requiring lookup must use nonzero IDs. The local source shows a duplicated `for` line in `samsung_clk_register_div()`, which would be a compile-significant source-copy issue. Auto clock mode requires exact resource sizing and sysreg phandles.

Test signals: build all Samsung CMUs, boot DT nodes with `of_clk_hw_onecell_get`, verify missing IDs are `ERR_PTR(-ENOENT)`, exercise PM save/restore, test auto-gate resource-size fallback, and check error logs for failed registrations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk.h -->
# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk.h

Purpose: central Samsung clock-driver interface and descriptor schema.

Important APIs/types/functions: declares `struct samsung_clk_provider`, `samsung_clock_alias`, fixed-rate/fixed-factor/mux/div/gate/PLL/CPU descriptor types, `samsung_clk_reg_dump`, `samsung_clock_reg_cache`, and `samsung_cmu_info`. Macros `ALIAS`, `FRATE`, `FFACTOR`, `MUX`, `MUX_F`, `nMUX`, `DIV`, `DIV_F`, `DIV_T`, `GATE`, `PLL`, and `CPU_CLK` construct static tables. Function prototypes expose the registration, provider, sleep, auto-gate, and CMU helpers.

Control flow: no runtime implementation, but the header dictates the order and data passed to `clk.c`, `clk-pll.c`, and CPU clock code. SoC files build arrays of these descriptors and pass them into common registration helpers.

State and persistence: describes provider runtime state, onecell clock arrays, PM register caches, and CMU save/suspend register lists. Persistence itself is implemented in `clk.c`.

Dependencies/integration: includes CCF, mod device table, regmap, `clk-pll.h`, and `clk-cpu.h`; it is the contract between Samsung SoC table files and common clock code.

Risks: macros encode policy such as `CLK_SET_RATE_NO_REPARENT`; changing them alters many SoC clocks. `clk_data` must remain last in `samsung_clk_provider` because it is flex-array allocated. The local `__GATE` macro contains a duplicated `.parent_name` initializer, which should be compile-reviewed. Descriptor comments and fields must stay synchronized with common registration code.

Test signals: compile all Samsung clock users, use sparse/build warnings to catch duplicated initializers or flex-array misuse, and boot representative SoCs to ensure descriptor IDs line up with DT binding constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/samsung/clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sifive/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/sifive/Kconfig

Purpose: Kconfig menu for SiFive SoC clock support and the PRCI driver.

Important APIs/types/functions: `menuconfig CLK_SIFIVE` gates SiFive clock drivers and defaults to `ARCH_SIFIVE`; `config CLK_SIFIVE_PRCI` enables the PRCI driver as tristate and selects `RESET_CONTROLLER`, `RESET_SIMPLE`, and `CLK_ANALOGBITS_WRPLL_CLN28HPC`.

Control flow: build-system configuration only. When enabled, the Makefile builds `sifive-prci.o`, which includes FU540/FU740 descriptors and registers the platform driver.

State and persistence: no runtime state; Kconfig choices determine compiled code and module availability.

Dependencies/integration: ties architecture selection, compile-test support, reset framework, and Analog Bits WRPLL helper library to the PRCI clock driver.

Risks: missing selects would break link/build for reset or WRPLL APIs. Defaulting to `ARCH_SIFIVE` means platform kernels likely include the driver unless explicitly disabled.

Test signals: Kconfig dependency resolution for built-in and module builds, `COMPILE_TEST` builds on non-SiFive architectures, and link checks for WRPLL/reset symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sifive/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sifive/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/sifive/Makefile

Purpose: connects the SiFive PRCI Kconfig symbol to the object build.

Important APIs/types/functions: `obj-$(CONFIG_CLK_SIFIVE_PRCI) += sifive-prci.o`.

Control flow: kbuild includes the PRCI implementation when the symbol is built-in or module-enabled.

State and persistence: no runtime state.

Dependencies/integration: relies on `Kconfig` selecting dependencies and on `sifive-prci.c` including its descriptor headers.

Risks: adding new SiFive clock drivers will require extending this file; the current single-object build means FU540/FU740 descriptor headers are compiled into `sifive-prci.o`.

Test signals: build with `CONFIG_CLK_SIFIVE_PRCI=y`, `m`, and unset; verify module object generation and no orphan objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sifive/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sifive/fu540-prci.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sifive/fu540-prci.h

Purpose: FU540-specific PRCI clock descriptor table included by the SiFive PRCI driver.

Important APIs/types/functions: defines WRPLL metadata for `corepll`, `ddrpll`, and `gemgxlpll`; defines `clk_ops` sets for programmable WRPLLs, read-only WRPLLs, and `tlclk`; and builds `__prci_init_clocks_fu540[]` plus `prci_clk_fu540`.

Control flow: `sifive-prci.c` selects `prci_clk_fu540` via OF match data for `"sifive,fu540-c000-prci"`. Registration iterates the array, reads current WRPLL CFG0 into each `pwd`, and registers one `clk_hw` per descriptor.

State and persistence: static descriptor data persists for the module lifetime. WRPLL current config is cached in each `__prci_wrpll_data.c` during probe and updated on set-rate.

Dependencies/integration: depends on `dt-bindings/clock/sifive-fu540-prci.h`, common PRCI types, and bypass helpers. Core PLL rate changes bypass through HFCLK and return to COREPLL; DDRPLL is recalc-only.

Risks: array indices are DT ABI. FU540 assumes sole PRCI ownership. Incorrect bypass callbacks can glitch CPU clock transitions.

Test signals: probe FU540 DT, verify four exposed clocks, set core/gemgxl PLL rates, confirm DDRPLL is read-only, and check TLCLK divides according to mux status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sifive/fu540-prci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sifive/fu740-prci.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sifive/fu740-prci.h

Purpose: FU740-specific PRCI descriptor table for additional PLLs and auxiliary clocks.

Important APIs/types/functions: defines WRPLL metadata for core, DDR, GEMGXL, DVFS core, HFPCLK, and CLTX PLLs. It supplies clk ops for programmable/read-only WRPLLs, TLCLK, HFPCLK divider, and PCIe auxiliary gate, then publishes `__prci_init_clocks_fu740[]` and `prci_clk_fu740`.

Control flow: the PRCI platform driver selects this descriptor for `"sifive,fu740-c000-prci"`. Registration binds each descriptor to the common PRCI MMIO context. Rate changes use common WRPLL code, with bypass callbacks for core, DVFS core, and HFPCLK muxes.

State and persistence: static descriptor arrays plus per-PLL cached WRPLL config. PCIe AUX state is a hardware enable bit, not cached.

Dependencies/integration: depends on FU740 DT binding IDs, common PRCI functions, and the WRPLL library. It integrates PRCI as both a clock provider and reset provider through the main C file.

Risks: more mux layers increase bypass-order risk. `pclk` is derived from `hfpclkpll` via a divider register; wrong parent names or binding IDs break consumers. PCIe AUX has only enable/disable/is_enabled and no rate ops.

Test signals: probe FU740 DT, verify all nine clocks, exercise HFPCLK/DVFS/core PLL rate changes, toggle PCIe AUX, and validate consumers such as PCIe and Ethernet after rate changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sifive/fu740-prci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sifive/sifive-prci.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sifive/sifive-prci.c

Purpose: runtime driver for SiFive FU540/FU740 Power Reset Clock Interface blocks.

Important APIs/types/functions: low-level `__prci_readl()/__prci_writel()`, WRPLL pack/unpack/read/write helpers, clock ops `sifive_prci_wrpll_recalc_rate()`, `determine_rate()`, `set_rate()`, `sifive_prci_clock_enable()/disable()/is_enabled()`, TLCLK and HFPCLK recalc ops, mux-select helpers, PCIe AUX ops, `__prci_register_clocks()`, and `sifive_prci_probe()`.

Control flow: probe gets OF match descriptor, allocates `struct __prci_data` with a flexible onecell array, maps PRCI registers, registers an active-low simple reset controller at `DEVICESRESETREG`, then registers all descriptor clocks. Clock registration requires exactly two DT parents (`hfclk` and `rtcclk`), initializes each `clk_hw`, caches WRPLL CFG0 for PLL clocks, registers with devm CCF, and publishes onecell provider. Rate changes compute WRPLL settings, optionally switch to bypass, write config, and delay for calculated lock time.

State and persistence: per-device state includes MMIO base, reset controller, and onecell data. Per-clock state stores PRCI pointer and optional WRPLL cached config. Hardware registers persist actual enable/mux/reset state; no explicit suspend/resume code is present.

Dependencies/integration: depends on the Analog Bits WRPLL helper, CCF, reset-simple, OF/platform driver APIs, and FU540/FU740 descriptor headers. It registers as `sifive-clk-prci`.

Risks: parent count is strict and fails probe if DT has a different shape. Bypass helpers have no locking, so CCF serialization assumptions matter. `sifive_prci_wrpll_set_rate()` leaves bypass enabled until clock enable disables bypass for some flows, so sequencing should be reviewed for active consumers. Reset and clock registers share one MMIO block.

Test signals: module/built-in probe on FU540/FU740 DTs, reset-controller consumers, clock rate set/recalc for WRPLLs, parent-count failure tests, PCIe AUX toggle, and boot stability under CPU/core PLL changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sifive/sifive-prci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sifive/sifive-prci.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sifive/sifive-prci.h

Purpose: shared PRCI register map, bitfields, data structures, and function prototypes.

Important APIs/types/functions: register offsets/masks cover CORE/DDR/GEMGXL/CLTX/DVFSCORE/HFPCLK PLLs, CORECLKSEL/COREPLLSEL/HFPCLKPLLSEL muxes, PCIe AUX, reset register, and clock mux status. Defines `EXPECTED_CLK_PARENT_COUNT`, `PRCI_RST_NR`, `struct __prci_data`, `struct __prci_wrpll_data`, `struct __prci_clock`, `struct prci_clk_desc`, and prototypes for mux helpers and clock ops.

Control flow: no implementation, but descriptor headers and `sifive-prci.c` share this contract. The common driver uses offsets from descriptor `pwd` records to read/write hardware.

State and persistence: describes cached WRPLL config (`wrpll_cfg c`) and per-device MMIO/reset/onecell state. Persistence is controlled by hardware and by the runtime cache in `sifive-prci.c`.

Dependencies/integration: includes WRPLL helper definitions, CCF, reset-simple, and platform device headers.

Risks: bitfield macros for HFPCLK use names that appear inconsistent with the offset macro spelling (`PRCI_HFPCLKPLL_CFG0_*` referring to `PRCI_HFPCLKPLLCFG0_*`), so build coverage is important. Register layout assumptions are shared across PLL types; mistakes affect all SoCs.

Test signals: compile with both FU540 and FU740 descriptors, verify reset count and bit positions against bindings/manuals, and boot-test all OF match variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sifive/sifive-prci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/socfpga/Kconfig

Purpose: Kconfig selection for Intel SoCFPGA clock controller support.

Important APIs/types/functions: `CLK_INTEL_SOCFPGA` gates the family; `CLK_INTEL_SOCFPGA32` selects Aria/Cyclone-era 32-bit ARM clock drivers; `CLK_INTEL_SOCFPGA64` selects Stratix/Agilex/N5X/Agilex5 ARM64/eASIC drivers.

Control flow: configuration controls which objects in the SoCFPGA Makefile are built.

State and persistence: no runtime state.

Dependencies/integration: defaults follow `ARCH_INTEL_SOCFPGA`, with `COMPILE_TEST` support when architecture constraints are met.

Risks: splitting 32-bit and 64-bit symbols means a platform can miss required objects if architecture defaults or compile-test dependencies are wrong.

Test signals: build matrix for ARM, ARM64, ARCH_INTEL_SOCFPGA, and COMPILE_TEST; verify expected objects are included for each symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/socfpga/Makefile

Purpose: maps SoCFPGA Kconfig symbols to the correct clock-driver object sets.

Important APIs/types/functions: `CLK_INTEL_SOCFPGA32` builds `clk.o`, older gate/PLL/peripheral helpers, and Arria10 variants. `CLK_INTEL_SOCFPGA64` builds Stratix10 common files plus Agilex and Agilex5 platform drivers.

Control flow: kbuild compiles family-specific object groups.

State and persistence: no runtime state.

Dependencies/integration: assumes shared headers such as `clk.h` and `stratix10-clk.h` are consumed by listed objects.

Risks: object ordering matters for built-in init availability but registration is primarily through initcalls/OF declarations. New SoC descriptors must be added under the right symbol.

Test signals: compile each config symbol independently and together under `COMPILE_TEST`, checking for missing prototypes and duplicate symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-agilex.c -->
# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-agilex.c

Purpose: platform driver and descriptor tables for Intel Agilex and N5X clock managers.

Important APIs/types/functions: parent-data mux arrays, `agilex_pll_clks`, N5X/Agilex peripheral counter tables, gate tables, registration loops for PLL/peripheral/gate classes, `agilex_clkmgr_init()`, `n5x_clkmgr_init()`, and `agilex_clkmgr_probe()`.

Control flow: probe dispatches by OF match data (`intel,agilex-clkmgr` or `intel,easic-n5x-clkmgr`). Init maps clock manager MMIO, allocates `stratix10_clock_data`, initializes all slots to `ERR_PTR(-ENOENT)`, registers PLLs, PLL counter outputs, peripheral counters, and gates, then publishes an OF onecell provider.

State and persistence: per-device `stratix10_clock_data` holds base and onecell clock array. Hardware register state determines rates, parents, gates, and bypasses; there is no suspend state here.

Dependencies/integration: depends on `stratix10-clk.h`, helper implementations in `clk-pll-s10.c`, `clk-periph-s10.c`, and `clk-gate-s10.c`, CCF, platform devices, and Agilex DT binding IDs.

Risks: registration helpers log and continue on individual clock failures, leaving sparse provider slots. N5X uses different PLL/peripheral recalc helpers but shares many tables. Parent-data names must match firmware/DT clock names exactly. `of_clk_add_hw_provider()` return is not checked.

Test signals: boot Agilex and N5X DTs, inspect onecell clock IDs, verify PLL rates differ correctly between Agilex and N5X, check EMAC/SDMMC/GPIO bypass parents, and validate critical `l4_sp_clk` stays enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-agilex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-agilex5.c -->
# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-agilex5.c

Purpose: platform driver and clock tables for Intel/Altera Agilex5 clock manager.

Important APIs/types/functions: string parent arrays for boot/main/peripheral PLLs and free/secondary muxes, `agilex5_pll_clks`, `agilex5_main_perip_c_clks`, `agilex5_main_perip_cnt_clks`, `agilex5_gate_clks`, registration loops, `agilex5_clkmgr_init()`, and `agilex5_clkmgr_probe()`.

Control flow: core initcall registers a platform driver. Probe dispatches to `agilex5_clkmgr_init()`, which maps MMIO, allocates `AGILEX5_NUM_CLKS` onecell storage, fills slots with `ERR_PTR(-ENOENT)`, registers PLLs, PLL counters, peripheral counters, and gates, then publishes the provider.

State and persistence: per-device onecell data and MMIO base persist via devm allocation. Actual mux/gate/divider state lives in clock manager registers. No explicit PM state is present.

Dependencies/integration: uses `dt-bindings/clock/intel,agilex5-clkmgr.h`, shared Stratix10 helper prototypes, Agilex5-specific structures in `stratix10-clk.h`, and the helper ops from PLL/periph/gate S10 files.

Risks: large literal tables define DT ABI IDs and register offsets; mistakes affect CPU, NoC, USB, SDMMC, NAND, and debug clocks. Parent names are plain strings, unlike Agilex parent-data, so DT/provider naming must match. Provider registration return is not checked. Some gates have no gate register but use divider/bypass data.

Test signals: boot Agilex5 DT, verify `AGILEX5_NUM_CLKS` coverage, inspect critical L4 clocks, test CPU/free-clock parent selections, validate USB31/SDMMC/NAND clocks, and check provider errors in boot logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-agilex5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-gate-a10.c -->
# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-gate-a10.c

Purpose: Arria10 SoCFPGA gate-clock registration and rate recalculation helper.

Important APIs/types/functions: `socfpga_gate_clk_recalc_rate()` computes fixed or power-of-two divider rates; `__socfpga_gate_init()` parses DT `clk-gate`, `fixed-divider`, `div-reg`, parent clocks, and `clock-output-names`; `socfpga_a10_gate_init()` is the exported initializer.

Control flow: the OF-declared caller invokes `socfpga_a10_gate_init()`. The helper allocates a `socfpga_gate_clk`, optionally installs CCF gate enable/disable ops, configures divider metadata, registers one `clk_hw`, and exposes it as a simple OF provider.

State and persistence: per-clock allocated state stores gate register, bit index, divider register/shift/width, and fixed divider. Hardware gate/divider registers carry actual state.

Dependencies/integration: depends on global `clk_mgr_a10_base_addr` initialized by Arria10 PLL code, shared `clk.h` structures, CCF gate ops, and DT properties.

Risks: mutating the static `gateclk_ops` enable/disable fields has global side effects across clocks. Initialization assumes the clock manager base has already been mapped. No unregister path is needed for early init but error cleanup only frees local allocation.

Test signals: boot Arria10 DT with gate clocks, verify enable/disable callbacks for clocks with `clk-gate`, inspect divided rates, and confirm init ordering maps `clk_mgr_a10_base_addr` before gate nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-gate-a10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-gate-s10.c -->
# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-gate-s10.c

Purpose: Stratix10/Agilex/Agilex5 gate-clock helper implementation.

Important APIs/types/functions: recalc helpers for normal gates and debug clock, parent-selection helpers `socfpga_gate_get_parent()` and `socfpga_agilex_gate_get_parent()`, and constructors `s10_register_gate()`, `agilex_register_gate()`, and `agilex5_register_gate()`.

Control flow: SoC descriptor drivers call a constructor per table entry. Each constructor allocates `socfpga_gate_clk`, assigns gate register/bit, divider metadata, bypass register/shift, fixed divider, selects normal/debug ops and Stratix10 vs Agilex parent logic, initializes parent data or names, and registers a `clk_hw`.

State and persistence: allocated clock state stores gate, divider, and bypass MMIO addresses. Parent choice is read from bypass registers, with special two-level EMAC boot-clock bypass handling.

Dependencies/integration: depends on `stratix10-clk.h` descriptor layouts, shared `clk.h`, CCF gate ops, and SoC descriptor tables.

Risks: `gateclk_ops` is a mutable static and constructors assign enable/disable repeatedly. EMAC parent logic subtracts family-specific offsets from bypass registers, so wrong table offsets can read unrelated registers. Debug clock divider treats decoded values specially. Agilex5 uses parent-name arrays, while S10/Agilex may use parent-data.

Test signals: verify gate enable/disable through CCF, inspect EMAC parent under MACA/MACB/boot bypass states, validate `cs_pdbg_clk` divider behavior, and boot S10/Agilex/Agilex5 descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-gate-s10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-gate.c -->
# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-gate.c

Purpose: legacy 32-bit SoCFPGA gate-clock helper for Cyclone/Arria-era DT clock nodes.

Important APIs/types/functions: `socfpga_clk_get_parent()`, `socfpga_clk_set_parent()`, `socfpga_clk_get_div()`, `socfpga_clk_recalc_rate()`, `socfpga_clk_determine_rate()`, and `socfpga_gate_init()`.

Control flow: `socfpga_gate_init()` allocates gate state, duplicates ops so parent callbacks can be disabled for single-parent clocks, parses gate and divider DT properties, registers the clock, and publishes a simple provider. Parent get/set handles L4 MP/SP clocks, MMC/NAND/NAND_X, and QSPI through clock-manager source registers.

State and persistence: per-clock state stores optional gate register/bit, fixed divider, divider register/shift/width. Hardware source, gate, and divider registers persist actual state.

Dependencies/integration: uses global `clk_mgr_base_addr` from the legacy PLL init, shared `clk.h`, CCF, OF properties, and clock manager register constants.

Risks: GPIO_DB divider detection uses a bitwise test against the divider-register pointer value and offset, which is fragile. Parent handling is name-based and supports only known clock names. Missing or late `clk_mgr_base_addr` mapping breaks registration.

Test signals: boot legacy SoCFPGA DT, test parent switching for L4/MMC/NAND/QSPI clocks, validate fixed and register-derived dividers, and check one-parent gates have no get/set-parent ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-gate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-periph-a10.c -->
# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-periph-a10.c

Purpose: Arria10 peripheral clock registration helper.

Important APIs/types/functions: `clk_periclk_recalc_rate()`, `clk_periclk_get_parent()`, `__socfpga_periph_init()`, and `socfpga_a10_periph_init()`.

Control flow: initialization parses DT register offset, optional `div-reg`, optional `fixed-divider`, output name, and parents. It registers one peripheral clock with recalc and parent-selection ops and publishes it as a simple provider.

State and persistence: allocated `socfpga_periph_clk` stores clock register, optional divider register, bitfield metadata, and fixed divider. Hardware registers hold parent/divider state.

Dependencies/integration: depends on global `clk_mgr_a10_base_addr`, shared `clk.h`, CCF, and OF properties. Special parent decoding applies to `mpu_free_clk`, `noc_free_clk`, and `sdmmc_free_clk`.

Risks: name-based parent decoding means renamed clocks return parent 0. The function assumes base mapping has already happened. Parent arrays are filled from DT and limited to `SOCFPGA_MAX_PARENTS`.

Test signals: boot Arria10 DT, confirm free-clock parent decoding, validate fixed and register divider math, and inspect provider registration per peripheral node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-periph-a10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-periph-s10.c -->
# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-periph-s10.c

Purpose: Stratix10/Agilex/N5X/Agilex5 peripheral-clock helper constructors.

Important APIs/types/functions: `n5x_clk_peri_c_clk_recalc_rate()`, `clk_peri_c_clk_recalc_rate()`, `clk_peri_cnt_clk_recalc_rate()`, `clk_periclk_get_parent()`, `s10_register_periph()`, `n5x_register_periph()`, `s10_register_cnt_periph()`, and `agilex5_register_cnt_periph()`.

Control flow: descriptor-driven SoC drivers call constructors for PLL counter outputs and peripheral counters. Constructors allocate `socfpga_periph_clk`, assign register/bypass/fixed-divider metadata, initialize parent names or parent-data, select ops by family, and register the clock.

State and persistence: per-clock state stores divider register, shift, fixed divider, optional bypass register and shift. Parent selection checks bypass first, then source field.

Dependencies/integration: depends on `stratix10-clk.h` descriptors, CCF, MMIO, shared `clk.h`, and SoC table files.

Risks: `clk_peri_c_clk_recalc_rate()` divides by the raw low register field and can divide by zero if hardware reads zero; this should be validated against hardware guarantees. Agilex5 parent names differ from parent-data flow. N5X has distinct field widths and shifts.

Test signals: validate recalc rates for PLL C counters and peripheral counters on S10/Agilex/N5X/Agilex5, test bypass parent reporting, and run boot-time clock summary checks for divide-by-zero or zero-rate warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-periph-s10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-periph.c -->
# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-periph.c

Purpose: legacy 32-bit SoCFPGA peripheral clock helper.

Important APIs/types/functions: `clk_periclk_recalc_rate()`, `clk_periclk_get_parent()`, `__socfpga_periph_init()`, and `socfpga_periph_init()`.

Control flow: DT initialization allocates a `socfpga_periph_clk`, points it at `clk_mgr_base_addr + reg`, parses optional divider metadata and fixed divider, fills parent names, registers a CCF clock, and exposes a simple provider.

State and persistence: per-clock state stores divider configuration. DBCTRL controls parent selection; clock registers control final divider.

Dependencies/integration: relies on legacy PLL mapping of `clk_mgr_base_addr`, shared `clk.h`, CCF, and OF properties.

Risks: parent get always reads `CLKMGR_DBCTRL` bit 0, so it only matches the legacy hardware model. If `fixed-divider` is absent and divider fields read zero, the code still divides by register value plus one. Init ordering with PLL mapping is required.

Test signals: boot legacy SoCFPGA clock DT, verify peripheral rates against hardware manual, check parent bit changes, and confirm simple provider registration for each node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-periph.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-pll-a10.c -->
# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-pll-a10.c

Purpose: Arria10 PLL clock helper and clock-manager base mapper.

Important APIs/types/functions: `clk_pll_recalc_rate()`, `clk_pll_get_parent()`, `__socfpga_pll_init()`, and `socfpga_a10_pll_init()`. Global `clk_mgr_a10_base_addr` is used by Arria10 gate/peripheral helpers.

Control flow: init parses the PLL node `reg`, maps the `"altr,clk-mgr"` node, sets the PLL register pointer, gathers parent names manually, registers a PLL CCF clock, and publishes it as a simple provider.

State and persistence: global base address persists after first map. Each PLL clock stores its register and external-enable bit index. Hardware VCO registers hold dividers and parent source.

Dependencies/integration: depends on OF clock manager node, CCF, shared `clk.h`, and Arria10-specific gate/peripheral helpers using the global base.

Risks: `BUG_ON(!clk_mgr_a10_base_addr)` panics on missing mapping. The maximum parent count macro is misspelled `SOCFGPA_MAX_PARENTS` but internally consistent. No unmap or devm management because this is early init style.

Test signals: boot Arria10 DT, confirm PLL parent indices and VCO rates, ensure gate/peripheral helpers see the mapped base, and test absent/malformed clock-manager node handling in build or DT validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-pll-a10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-pll-s10.c -->
# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-pll-s10.c

Purpose: shared PLL constructors and rate ops for Stratix10, Agilex, N5X, and Agilex5.

Important APIs/types/functions: recalc functions for N5X, Agilex, Stratix10, and boot clocks; parent selectors; prepare callbacks that deassert PLL reset; ops tables; and constructors `s10_register_pll()`, `agilex_register_pll()`, `n5x_register_pll()`, `agilex5_register_pll()`.

Control flow: SoC descriptor drivers call the appropriate constructor per PLL entry. Constructors allocate `socfpga_pll`, assign the MMIO offset, choose boot vs family PLL ops, initialize parent data or parent names, register with CCF, and return the hardware pointer for insertion into onecell data.

State and persistence: per-PLL allocated state stores register pointer and power bit. Hardware registers control source, divider, feedback, reset, and boot divider state.

Dependencies/integration: uses descriptor structures from `stratix10-clk.h`, shared `clk.h`, CCF, and SoC platform drivers.

Risks: rate formulas differ by family and use different offsets; table/constructor mismatch produces wrong rates. `clk_boot_get_parent()` returns a masked value after shifting but uses the full mask constant, which deserves hardware validation. `clk_pll_recalc_rate()` divides by `refdiv` without adding one; DT/hardware must ensure nonzero.

Test signals: compare computed PLL rates with firmware/hardware readouts for S10/Agilex/N5X/Agilex5, check prepare deasserts reset, validate boot clock parent/divider, and inspect clock summary after boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-pll-s10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-pll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-pll.c

Purpose: legacy 32-bit SoCFPGA PLL clock helper.

Important APIs/types/functions: global `clk_mgr_base_addr`, `clk_pll_recalc_rate()`, `clk_pll_get_parent()`, `__socfpga_pll_init()`, and `socfpga_pll_init()`.

Control flow: DT initialization maps the clock-manager node, records the base globally, creates a PLL clock from the node register offset and parent list, registers it with CCF, and publishes a simple provider.

State and persistence: global base address is shared with legacy gate/peripheral helpers. Per-PLL state stores register pointer and external-enable bit. Hardware registers hold bypass, source, DIVF, and DIVQ state.

Dependencies/integration: depends on OF compatible `"altr,clk-mgr"`, legacy constants in `clk.h`, CCF, and simple provider APIs.

Risks: `clk_pll_recalc_rate()` checks only `MAINPLL_BYPASS`, so other bypass bits defined in the file are not used by this helper. Missing clock-manager mapping triggers `BUG_ON`. Register offsets and parent order come from DT and must match hardware.

Test signals: boot Cyclone/Arria legacy DT, verify PLL rates with and without bypass, confirm dependent gate/peripheral nodes initialize after base mapping, and inspect provider registration logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-pll.c -->
