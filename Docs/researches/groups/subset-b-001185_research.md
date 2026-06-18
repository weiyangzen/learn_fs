# subset-b-001185 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk.h -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk.h

## Purpose

`clk.h` is the private interface for the NVIDIA Tegra clock-controller implementation. It centralizes register offsets, valid enable masks, private clock data structures, flag definitions, helper prototypes, and SoC-specific initialization entry points used by the many Tegra clock source files. The header is not a standalone driver; it is the shared contract between Tegra clock implementations for PLLs, fractional dividers, peripheral clocks, super clocks, SDMMC mux/dividers, EMC clocks, reset handling, and device-tree provider setup.

## Important APIs, Types, And Functions

The top of the file defines the common CAR register offsets for clock enable banks `L/H/U/V/W/X/Y`, set/clear aliases, reset-device banks, and Tegra210 valid-bit masks. `struct tegra_clk_sync_source`, `struct tegra_clk_frac_div`, `struct tegra_clk_pll_freq_table`, `struct pdiv_map`, `struct div_nmp`, `struct tegra_clk_pll_params`, `struct tegra_clk_pll`, and `struct tegra_clk_pll_out` describe the PLL and divider plumbing. The PLL params structure is the largest contract: it carries base/misc register offsets, masks and shifts for M/N/P, lock bits, SDM data, fixed-rate tables, p-div mappings, step registers, output masks, and per-PLL operation callbacks.

Peripheral clock interfaces are represented by `struct tegra_clk_periph_regs`, `struct tegra_clk_periph_gate`, `struct tegra_clk_periph_fixed`, `struct tegra_clk_periph`, `struct tegra_periph_init_data`, `TEGRA_CLK_PERIPH()`, `TEGRA_INIT_DATA_TABLE()`, and `TEGRA_INIT_DATA()`. CPU and system muxing is represented by `struct tegra_clk_super_mux` and the `tegra_clk_register_super_*()` family. The late file-level APIs expose `tegra_clk_init()`, `tegra_lookup_dt_id()`, `tegra_add_of_provider()`, `tegra_register_devclks()`, per-SoC init hooks, EMC registration hooks, suspend/resume hooks, and low-level helpers such as `tegra_pll_wait_for_lock()`, `tegra_pll_p_div_to_hw()`, and `div_frac_get()`.

## Control Flow

Consumers include SoC-specific Tegra clock files. Their normal flow is to map the CAR base, call `tegra_clk_init()` to allocate the clock array, register fixed/oscillator/PLL/peripheral/super/audio/EMC clocks through the prototypes here, populate duplicate device clock lookups, initialize default rates and parents from `struct tegra_clk_init_table`, and add a device-tree clock provider through `tegra_add_of_provider()`. Runtime control is then delegated to CCF operations implemented in the corresponding `.c` files, using the register offsets and masks encoded by these structures.

## State And Persistence Behavior

The header describes hardware state rather than owning it. Persistent state lives in CAR registers: enable bits, reset bits, PLL programming, peripheral mux/divider fields, PLL output gates, and suspend/resume shadow state maintained by implementation files. Several structures contain pointers to shared locks, reg bases, and clock arrays, so a bad initializer can couple unrelated clocks to the wrong register bank. The valid enable masks prevent writes to reserved bits for Tegra210 banks.

## Dependencies And Integration Points

This file depends on Linux CCF types, Tegra device-tree clock IDs from `<dt-bindings/clock/tegra*.h>`, reset-controller integration, EMC support, and SoC-specific Tegra clock implementation files. `CONFIG_ARCH_TEGRA_124_SOC` gates the Tegra124 EMC registration path and supplies stubs otherwise. Device-tree integration depends on onecell clock provider arrays and stable DT clock IDs.

## Risks And Edge Cases

Register bank offsets and bit masks are hardware-sensitive. An incorrect bank, reset bit, or PLL field can disable a live peripheral or program a PLL outside its safe range. PLL flags such as `TEGRA_PLL_USE_LOCK`, `TEGRA_PLL_BYPASS`, `TEGRA_PLLM`, `TEGRA_PLLU`, and `TEGRA_MDIV_NEW` select different algorithms in implementation files, so table-driven additions must match the exact PLL generation. The periph macros hide many positional parameters; initializer ordering mistakes are easy to compile but hard to diagnose at boot. EMC function stubs return safe defaults when Tegra124 support is absent, which can mask missing config until a board expects dynamic EMC handling.

## Test Signals

Build Tegra clock drivers across representative SoC configs, including with and without `CONFIG_ARCH_TEGRA_124_SOC`. Boot tests should inspect `/sys/kernel/debug/clk/clk_summary`, verify DT clock IDs resolve, exercise peripheral gates and resets, test CPU/super-clock rate transitions, and run suspend/resume to confirm CAR state restoration. PLL-focused tests should validate lock polling and output frequencies against hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/cvb.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/cvb.c

## Purpose

`cvb.c` converts NVIDIA Tegra CVB voltage tables into Linux OPP entries. CVB tables describe the voltage needed for a clock frequency as a quadratic function of the chip's speedo value, with process/speedo table selection, rail alignment, and min/max voltage clamping. The resulting operating points are registered with the OPP core for consumers such as CPU or GPU DVFS drivers.

## Important APIs, Types, And Functions

`get_cvb_voltage()` evaluates `((c2 * speedo / s_scale + c1) * speedo / s_scale + c0)` using rounded integer arithmetic. `round_cvb_voltage()` applies the table voltage scale and aligns the result to the regulator's microvolt offset and step. `round_voltage()` rounds min/max limits up or down to the same regulator alignment. `build_opp_table()` walks up to `MAX_DVFS_FREQS`, stops at the first zero frequency or a frequency above `max_freq`, clamps each calculated voltage, and calls `dev_pm_opp_add()`.

The exported `tegra_cvb_add_opp_table()` selects the first CVB table whose `speedo_id` and `process_id` match, allowing `-1` wildcards, then builds the OPP table and returns the selected table or `ERR_PTR()`. `tegra_cvb_remove_opp_table()` removes the same frequency range with `dev_pm_opp_remove()`.

## Control Flow

A Tegra DVFS user supplies the device, CVB table array, rail alignment, process and speedo identifiers, raw speedo value, and maximum safe rate. The function scans tables in order and immediately attempts the first match. For each entry, it calculates millivolts from coefficients, rounds to rail requirements, clamps to table limits, converts to microvolts, and registers the OPP. Cleanup uses the returned table pointer and the same `max_freq` boundary to remove entries.

## State And Persistence Behavior

This file stores no private state. Its persistent side effect is the OPP table entries attached to `dev` in the OPP core. Partial failure during `build_opp_table()` returns immediately and does not roll back already added OPPs, so callers need to handle cleanup if they retry or abort after a mid-table failure.

## Dependencies And Integration Points

The code depends on `linux/pm_opp.h`, Tegra CVB structures from `cvb.h`, and regulator alignment values supplied by the platform. It integrates with whichever clock/voltage driver later consumes OPP entries for DVFS. The semantics of speedo/process IDs must match Tegra fuse-reading code outside this file.

## Risks And Edge Cases

Table ordering matters because selection stops at the first compatible table. Bad `voltage_scale`, `speedo_scale`, or rail alignment can silently over- or under-voltage every OPP. If `align->step_uv` is zero, `round_cvb_voltage()` uses a default scaled 1000 uV step but still multiplies `offset_uv` by `v_scale`, so table authors must understand the combined scale. Duplicate OPP frequencies or unsupported voltages surface as `dev_pm_opp_add()` errors. A failure after adding earlier OPPs leaves partial state unless the caller removes it.

## Test Signals

Unit-style validation can feed known speedo/coefficient/table values and compare generated microvolt OPPs. Platform tests should verify OPP entries in debugfs/sysfs, confirm max-frequency truncation, exercise wildcard and exact speedo/process matches, and test cleanup by unloading or reprobes. DVFS stress tests should confirm regulators accept the aligned voltages and frequency transitions remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/cvb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/cvb.h -->
# sources/distributed-fs/ceph-client/drivers/clk/tegra/cvb.h

## Purpose

`cvb.h` declares the data model and exported helpers for Tegra CVB voltage-table handling. It is the shared contract between SoC-specific Tegra DVFS data and the implementation in `cvb.c`.

## Important APIs, Types, And Functions

`MAX_DVFS_FREQS` caps each table at 40 entries. `struct rail_alignment` describes regulator offset and step in microvolts. `struct cvb_coefficients` stores the quadratic coefficients used to calculate voltage from speedo. `struct cvb_table_freq_entry` pairs a frequency with coefficients. `struct cvb_cpu_dfll_data` carries CPU DFLL tuning values and the minimum millivoltage threshold for high tuning. `struct cvb_table` adds speedo/process matching, min/max voltage limits, scaling factors, the frequency entries, and optional CPU DFLL data.

The public helpers are `tegra_cvb_add_opp_table()` and `tegra_cvb_remove_opp_table()`.

## Control Flow

The header is included by Tegra clock/DVFS code that defines static CVB tables and then asks `cvb.c` to materialize them as OPP entries. Callers retain the returned `struct cvb_table` pointer so they can later remove only the entries that were added.

## State And Persistence Behavior

The structures are plain configuration data, usually static and read-only in SoC files. Runtime persistence is indirect: the add/remove functions create or delete OPP core state for the target device. `cvb_cpu_dfll_data` also carries values that CPU DFLL integration may program into hardware outside this file.

## Dependencies And Integration Points

The header depends on Linux integer types and forward-declares `struct device`. It integrates with Tegra fuse/process identification, regulator alignment data, OPP core registration, and CPU DFLL tuning code.

## Risks And Edge Cases

All units must be consistent: frequencies are `unsigned long`, voltages in the table are millivolts, rail alignment uses microvolts, and scaling factors are integer divisors/multipliers used by the CVB formula. A table without a terminating zero frequency relies on the fixed `MAX_DVFS_FREQS` bound. Wildcard `speedo_id` or `process_id` values are implemented in `cvb.c` as `-1`, so table authors need to reserve that convention.

## Test Signals

Compile tests should cover all files that define CVB tables. Runtime validation should inspect generated OPP entries, ensure the selected table matches fuse values, and verify DFLL tuning thresholds for CPU tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tegra/cvb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tenstorrent/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/tenstorrent/Kconfig

## Purpose

This Kconfig entry exposes the Tenstorrent Atlantis PRCM clock controller driver as `CONFIG_TENSTORRENT_ATLANTIS_PRCM`. It controls compilation of the Atlantis PRCM clock provider.

## Important APIs, Types, And Functions

The symbol is a `tristate` named "Support for Tenstorrent Atlantis PRCM Clock Controller". It depends on `ARCH_TENSTORRENT || COMPILE_TEST`, defaults to `ARCH_TENSTORRENT`, and selects `REGMAP_MMIO`, `AUXILIARY_BUS`, and `MFD_SYSCON`.

## Control Flow

When enabled, the corresponding Makefile builds `atlantis-prcm.o`. On real Tenstorrent builds the default follows the architecture selection; on other architectures it is available only for compile testing.

## State And Persistence Behavior

There is no runtime state in this file. It determines whether the driver and its selected dependencies are part of the kernel image or module set.

## Dependencies And Integration Points

The selected dependencies match the driver's MMIO regmap use and auxiliary-device reset registration. The help text says the controller covers RCPU, HSIO, MMIO, and PCIe domains, although the current source in this subset registers the RCPU-compatible data.

## Risks And Edge Cases

Because the symbol selects auxiliary bus and syscon support, dependency drift in the driver must be reflected here. If future Atlantis domains are added without Kconfig help or dependency updates, builds may succeed but DT users can fail to bind needed reset or regmap helpers.

## Test Signals

Run `allyesconfig` or `COMPILE_TEST` builds with this symbol as module and built-in. On Tenstorrent configs, verify it defaults on and that `atlantis-prcm.o` is included.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tenstorrent/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tenstorrent/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/tenstorrent/Makefile

## Purpose

This Makefile connects `CONFIG_TENSTORRENT_ATLANTIS_PRCM` to the Atlantis PRCM clock-controller object.

## Important APIs, Types, And Functions

The only build rule is `obj-$(CONFIG_TENSTORRENT_ATLANTIS_PRCM) += atlantis-prcm.o`.

## Control Flow

Kbuild includes `atlantis-prcm.o` as built-in, module, or omitted according to the Kconfig symbol value.

## State And Persistence Behavior

There is no runtime state. The file only affects build composition.

## Dependencies And Integration Points

It integrates with `drivers/clk/tenstorrent/Kconfig` and the top-level clock-driver build. Any future Tenstorrent clock files must be added here or they will not build.

## Risks And Edge Cases

The rule is intentionally simple. The main risk is forgetting to update it when the driver is split into multiple objects or when domain-specific files are introduced.

## Test Signals

Check that enabling `CONFIG_TENSTORRENT_ATLANTIS_PRCM=m` produces `atlantis-prcm.ko`, and enabling it built-in links the object into the kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tenstorrent/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tenstorrent/atlantis-prcm.c -->
# sources/distributed-fs/ceph-client/drivers/clk/tenstorrent/atlantis-prcm.c

## Purpose

`atlantis-prcm.c` is the Tenstorrent Atlantis PRCM clock-controller driver. It registers CCF clocks for the RCPU clock domain, including PLLs, muxes, read-only dividers, gates, shared gates, and fixed-factor aliases. It also creates an auxiliary reset device for the same PRCM block.

## Important APIs, Types, And Functions

The driver defines register offsets for RCPU and NOCC PLL/config/gate registers and bitfields for PLL enable, bypass, dividers, feedback divider, lock detect, and lock status. `struct atlantis_clk_common` embeds `clk_hw`, an integer clock ID, and a regmap pointer shared by all custom clock types. Specialized wrappers model muxes, gates, dividers, PLLs, shared gates, and fixed factors.

Clock operations include `atlantis_clk_mux_get_parent()`/`set_parent()`, `atlantis_clk_gate_enable()`/`disable()`/`is_enabled()`, `atlantis_clk_divider_recalc_rate()`, `atlantis_clk_fixed_factor_recalc_rate()`, and `atlantis_clk_pll_enable()`/`disable()`/`recalc_rate()`/`is_enabled()`. Shared gates use `refcnt_qspi`, `refcnt_can0`, and `refcnt_can1` protected by `refcount_lock` so paired functional and bus clocks manipulate one hardware gate bit.

The macro layer (`ATLANTIS_PLL_DEFINE`, `ATLANTIS_MUX_DEFINE`, `ATLANTIS_DIVIDER_DEFINE`, `ATLANTIS_GATE_DEFINE`, `ATLANTIS_GATE_SHARED_DEFINE`, `ATLANTIS_FIXED_FACTOR_DEFINE`) instantiates the clock topology. `atlantis_prcm_clocks_register()` registers all `clk_hw`s and publishes a onecell provider. `atlantis_prcm_probe()` maps MMIO, initializes regmap, registers clocks, and creates the reset auxiliary device.

## Control Flow

The platform driver matches `tenstorrent,atlantis-prcm-rcpu`. Probe maps resource 0 with `devm_platform_ioremap_resource()`, wraps it in a 32-bit MMIO regmap, gets match data, and registers every clock in `atlantis_rcpu_clks`. During registration, each static clock object's `common.regmap` is assigned and its ID indexes the provider array. After clock registration, `devm_auxiliary_device_create()` creates a reset child named by `reset_name`.

Runtime PLL enable first forces bypass, toggles the enable register bit low then high, polls the PLL config register for `PLL_CFG_LOCK_BIT`, clears bypass, and optionally enables an output gate. Disable switches to bypass and powers down the PLL. Rate recalculation returns the parent rate in bypass and otherwise computes `parent * fbdiv / (refdiv * postdiv1 * postdiv2)`, normalizing zero divisors to one except for zero `fbdiv`.

## State And Persistence Behavior

The driver has static clock descriptors and static shared-gate reference counters. Hardware register state persists across CCF operations: PLL bypass and enable bits, mux selectors, divider fields, and gate bits. The shared-gate counters are in-memory only and represent Linux's view of paired consumers, not hardware state after reboot or firmware changes. The regmap uses `REGCACHE_NONE`, so reads and writes go directly to MMIO.

## Dependencies And Integration Points

The driver depends on CCF, regmap MMIO, platform devices, auxiliary bus, and DT binding IDs from `tenstorrent,atlantis-prcm-rcpu.h`. It integrates with device tree through `of_clk_hw_onecell_get`. Reset support is delegated to an auxiliary device, so a matching auxiliary reset driver is expected elsewhere.

## Risks And Edge Cases

The PLL enable path assumes the lock bit appears within `PLL_LOCK_TIMEOUT_US`; slow silicon or incorrect reference clocks can fail probe-time or runtime enables. Optional PLL output gates are represented by `cg_reg_enable`; for `rcpu_pll_clk` this is zero and the final update writes a zero mask, which should be harmless but relies on regmap semantics. Shared gate reference counts can become inconsistent if CCF disables unused clocks without matching prior enables; the custom `disable_unused` only clears hardware when the counter is zero. Divider clocks implement recalc only, so consumers cannot program divider fields through CCF.

## Test Signals

Build with `CONFIG_TENSTORRENT_ATLANTIS_PRCM` built-in and as a module. Boot an Atlantis DT with `tenstorrent,atlantis-prcm-rcpu`, verify the clock provider registers all binding IDs, and inspect `clk_summary` for RCPU, NOCC, LSIO, QSPI, CAN, UART, SPI, I2C, GPIO, timer, watchdog, security, and fixed-factor clocks. Exercise shared QSPI and CAN clocks with multiple consumers and verify the shared gate stays enabled until the last consumer disables it. Validate PLL rates against register fields and confirm the auxiliary reset device binds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/tenstorrent/atlantis-prcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/thead/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/thead/Kconfig

## Purpose

This Kconfig entry exposes the T-HEAD TH1520 AP clock controller driver as `CONFIG_CLK_THEAD_TH1520_AP`.

## Important APIs, Types, And Functions

The symbol is a boolean named "T-HEAD TH1520 AP clock support". It depends on `ARCH_THEAD || COMPILE_TEST` and `64BIT`, defaults to `ARCH_THEAD`, and selects `REGMAP_MMIO`.

## Control Flow

When enabled, the T-Head Makefile builds `clk-th1520-ap.o`, which registers AP and VO clock providers for matching TH1520 device-tree nodes.

## State And Persistence Behavior

No runtime state is stored here. It controls compile-time availability and whether the driver is linked into the kernel.

## Dependencies And Integration Points

The `64BIT` dependency matches TH1520 platform assumptions. `REGMAP_MMIO` is required by the driver's MMIO-backed PLL and divider code.

## Risks And Edge Cases

If the driver is needed on a configuration that does not select `ARCH_THEAD`, it is available only through compile-test paths. Future driver changes requiring other framework helpers must update the `select` list.

## Test Signals

Compile 64-bit T-Head and compile-test configurations with the symbol enabled. Ensure the object is built and DT compatibles `thead,th1520-clk-ap` and `thead,th1520-clk-vo` can bind at runtime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/thead/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/thead/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/thead/Makefile

## Purpose

This Makefile connects the TH1520 AP clock-controller Kconfig symbol to its implementation object.

## Important APIs, Types, And Functions

The build rule is `obj-$(CONFIG_CLK_THEAD_TH1520_AP) += clk-th1520-ap.o`.

## Control Flow

Kbuild includes the TH1520 clock driver when `CONFIG_CLK_THEAD_TH1520_AP` is enabled.

## State And Persistence Behavior

There is no runtime state. The file only affects kernel build composition.

## Dependencies And Integration Points

It integrates with `drivers/clk/thead/Kconfig`. Any split of AP and VO clock support into separate files would need corresponding Makefile updates.

## Risks And Edge Cases

The rule is minimal. The main maintenance risk is adding new T-Head clock-controller files without adding objects here.

## Test Signals

Build a kernel with `CONFIG_CLK_THEAD_TH1520_AP=y` and verify `clk-th1520-ap.o` is linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/thead/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/thead/clk-th1520-ap.c -->
# sources/distributed-fs/ceph-client/drivers/clk/thead/clk-th1520-ap.c

## Purpose

`clk-th1520-ap.c` is the T-HEAD TH1520 clock-controller driver for AP and VO clock domains. It provides PLL, mux, divider, gate, fixed-factor, and CPU DVFS-safe clock switching support through the Linux common clock framework.

## Important APIs, Types, And Functions

The file defines TH1520 PLL bitfields for feedback divider, reference divider, postdividers, bypass, VCO reset, fractional mode, and lock status. `struct ccu_common` wraps shared clock metadata and regmap state. `struct ccu_pll`, `struct ccu_div`, `struct ccu_mux`, and `struct ccu_gate` model the custom and standard CCF clock types. `ccu_div_ops` implements enable, parent, rate, and divider programming. `clk_pll_ops` implements PLL enable/disable, lock polling, rate lookup, and rate programming from discrete `struct ccu_pll_cfg` tables.

The special `c910_clk_ops` implements glitchless CPU clock DVFS by selecting the unused parent, programming that parent rate, then reparenting. `c910_clk_notifier_cb()` keeps `c910_bus_clk` below `TH1520_C910_BUS_MAX_RATE` during CPU rate changes. Static topology data defines CPU PLL0/1, GMAC, VIDEO, DPU0/1, TEE PLLs, CPU/bus/peripheral/AXI/VO dividers, AP gates, VO gates, UART muxing, and fixed-factor clocks.

## Control Flow

The platform driver matches `thead,th1520-clk-ap` and `thead,th1520-clk-vo`, each with different `th1520_plat_data`. Probe allocates a `clk_hw_onecell_data`, maps MMIO, creates a regmap, then registers PLLs, dividers, muxes, and gates from the platform-data arrays. For AP data it additionally registers `osc_12m`, `gmac-pll-clk-100m`, `emmc-sdio-ref`, and a notifier on the C910 clock. Finally it publishes the onecell provider.

PLL rate changes disable the PLL by asserting VCO reset, write the best matching table configuration, update fractional/integer mode bits, re-enable, poll `TH1520_PLL_STS`, and delay for stability. Divider rate changes temporarily clear the divider-enable bit, write the new divisor, then re-enable it; read-only dividers reject mismatched rate changes. Gate and mux clocks use standard `clk_gate_ops` and `clk_mux_ops` once their MMIO register pointers are set.

## State And Persistence Behavior

Persistent state lives in the TH1520 clock registers: PLL configuration and reset bits, mux selectors, dividers, and gate bits. The driver's static clock descriptors receive the runtime regmap or MMIO register pointer at probe. Critical flags keep CPU, bus, NPU/VP/VO infrastructure, and selected PLLs enabled. The CPU bus notifier changes divider state around CPU clock transitions and therefore has persistent hardware side effects.

## Dependencies And Integration Points

The driver depends on DT binding IDs from `thead,th1520-clk-ap.h`, CCF, regmap MMIO, platform devices, and device-tree parent index 0 for `osc_24m`. It exposes AP and VO onecell clock providers to CPU, display, HDMI, MIPI DSI, GPU, GMAC, eMMC/SDIO, UART, SPI, QSPI, I2C, GPIO, DMA, watchdog, timer, mailbox, SRAM, and NPU consumers.

## Risks And Edge Cases

The C910 path is sensitive: parent switching and the bus-divider notifier must maintain the 750 MHz bus limit during both scale-up and scale-down. The PLL code chooses nearest table entries, so unsupported requested rates silently round. Divider programming assumes the enable bit can be toggled safely around divisor writes. Divider clocks with `div_en == 0` are treated as read-only by `ccu_div_set_rate()`, so callers requesting unsupported rates will receive `-EINVAL` rather than hardware reprogramming. VO gate clocks use register offsets `0x0` and `0x4`, so the AP/VO compatible must map the correct MMIO region.

## Test Signals

Compile with `CONFIG_CLK_THEAD_TH1520_AP=y` and treat warnings around initializers as blockers. Boot TH1520 AP and VO DT nodes and inspect `clk_summary` for PLLs, C910, AP bus clocks, peripheral gates, DPU pixel clocks, HDMI, MIPI DSI, and GPU clocks. Stress CPU frequency changes while monitoring `c910-bus` rate. Exercise display pipelines, GMAC, eMMC/SDIO, UART/I2C/SPI/QSPI, timers, watchdogs, and GPIO. Validate PLL output rates against table values and register fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/thead/clk-th1520-ap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/Kconfig

## Purpose

This Kconfig file defines the optional TI ADPLL clock driver symbol.

## Important APIs, Types, And Functions

`CONFIG_COMMON_CLK_TI_ADPLL` is a tristate "Clock driver for dm814x ADPLL". It depends on `ARCH_OMAP2PLUS || COMPILE_TEST`, defaults to `y` for `SOC_TI81XX`, and enables the DM814x ADPLL CCF platform driver.

## Control Flow

When selected, the TI Makefile builds `adpll.o`. The default enables the driver for TI81xx SoCs that need it while still allowing compile coverage elsewhere.

## State And Persistence Behavior

No runtime state is stored here. The file controls build inclusion only.

## Dependencies And Integration Points

The dependency matches OMAP2+ clock infrastructure and compile-test use. The ADPLL driver itself also depends on platform devices, device tree, and CCF.

## Risks And Edge Cases

If ADPLL support is needed on a newly supported TI SoC, the default or dependency may need adjustment. Keeping this as a separate symbol from the OMAP2PLUS core clock files allows modular compile testing but also means DT nodes will not bind if the symbol is off.

## Test Signals

Build with `CONFIG_COMMON_CLK_TI_ADPLL=y`, `m`, and disabled. On TI81xx configs, confirm the default includes ADPLL support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/Makefile

## Purpose

The TI clock Makefile selects the common TI/OMAP clock framework objects and SoC-specific clock initialization files for OMAP2+, AM33xx, TI81xx, OMAP3/4/5, DRA7xx, AM43xx, and the optional ADPLL platform driver.

## Important APIs, Types, And Functions

When `CONFIG_ARCH_OMAP2PLUS=y`, `obj-y` includes foundational objects `clk.o`, `autoidle.o`, and `clockdomain.o`. `clk-common` expands to DPLL, composite, divider, gate, fixed-factor, mux, APLL, clock-type, and clkctrl helpers. SoC blocks add `clk-33xx.o`, `clk-814x.o`, `clk-816x.o`, `clk-2xxx.o`, `clk-3xxx.o`, `clk-44xx.o`, `clk-54xx.o`, `clk-7xx.o`, `clk-dra7-atl.o`, and DPLL variant files as needed. Outside the OMAP2PLUS block, `obj-$(CONFIG_COMMON_CLK_TI_ADPLL) += adpll.o` builds the ADPLL driver.

## Control Flow

Kbuild evaluates SoC config symbols and includes the correct combination of shared clock infrastructure and SoC init data. The ADPLL object is controlled independently by its own Kconfig symbol.

## State And Persistence Behavior

This file has no runtime state. Build composition determines which init functions, clock data tables, and platform drivers are available.

## Dependencies And Integration Points

The Makefile encodes coupling between SoC init files and helper implementations. For example, OMAP3 and AM33xx need `dpll3xxx.o`, OMAP4/5/DRA7 need `dpll44xx.o`, and legacy OMAP2/3 include `interface.o`.

## Risks And Edge Cases

Incorrect object combinations can compile but fail at runtime with missing init symbols or unregistered clock types. New SoC support must include both common helper files and the right DPLL variant. Moving `adpll.o` inside the OMAP2PLUS conditional would reduce compile-test coverage and break module builds for its independent symbol.

## Test Signals

Run representative builds for AM33xx, AM43xx, OMAP2, OMAP3, OMAP4, OMAP5, DRA7xx, TI81xx, and `COMMON_CLK_TI_ADPLL=m`. Link errors are strong signals of missing Makefile dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/adpll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/adpll.c

## Purpose

`adpll.c` is a platform driver for TI DM814x ADPLL clocks. It maps an ADPLL register block, registers a DCO clock and its derived internal/output clocks, and exposes the configured outputs through a device-tree onecell provider. It supports both ADPLL-S and ADPLL-LJ layouts.

## Important APIs, Types, And Functions

The file defines register offsets and bit positions for PLLSS lock/unlock, power control, clock control, dividers, fractional divider, bandwidth control, status, M3 divider, and ramp control. `struct ti_adpll_platform_data` describes layout differences: type S has three inputs and four outputs with DCO as an output; type LJ has two inputs and three outputs. `struct ti_adpll_data` owns the device, mapped registers, physical address, spinlock, parent names/clocks, registered clocks, onecell outputs, and embedded DCO `clk_hw`.

Helper constructors register dividers, muxes, gates, fixed factors, and custom clkout clocks. `ti_adpll_prepare()` clears idle bypass and waits for lock; `ti_adpll_unprepare()` sets idle bypass; `ti_adpll_recalc_rate()` computes DCO rate from M/N/fractional fields and type-S multipliers. `ti_adpll_init_children_adpll_s()` and `_lj()` build the topology for each hardware variant. `ti_adpll_probe()` wires all steps together and `ti_adpll_remove()` unregisters resources.

## Control Flow

Probe allocates `ti_adpll_data`, maps resource 0, unlocks the global PLLSS MMR for type S, chooses the register base offset, resolves parent clocks from DT, allocates clock bookkeeping, registers the DCO and internal N2 divider, then registers type-specific children. Type S creates bypass mux, M2 divider, div2 fixed factor, `clkout`, `clkoutx2`, optional HIF mux, and M3 output. Type LJ creates gated DCO output, M2 divider, gated M2 output, bypass mux, and `clkout`. Finally the driver adds an OF clock provider.

Runtime output parent selection reflects hardware bypass status: clkouts use DCO-derived parents when not bypassed and bypass parents when the status bit says bypass. Gates delegate to `clk_gate_ops` with the ADPLL spinlock. Resource cleanup walks registered clocks in reverse order, drops clkdev lookups, and calls stored unregister callbacks.

## State And Persistence Behavior

Hardware registers retain PLL power, bypass, lock, divider, and gate state. The driver stores in-memory clock registration data and clkdev lookups for legacy con_id lookup. Spinlock-protected register access coordinates shared ADPLL control fields. The provider's output array persists until device removal.

## Dependencies And Integration Points

The driver depends on platform devices, OF, CCF, clkdev, MMIO accessors, and DT compatibles `ti,dm814-adpll-s-clock` and `ti,dm814-adpll-lj-clock`. It integrates with parent clocks listed in DT, output names from `clock-output-names`, and legacy clkdev con_id naming derived from the physical address.

## Risks And Edge Cases

Type-S HIF handling registers M3 using `d->clocks[TI_ADPLL_HIF].clk`, but HIF is only initialized when the third parent clock is present; the earlier input validation normally requires it. `ti_adpll_prepare()` ignores the return value from `ti_adpll_wait_lock()` and always returns zero, so lock failures may be visible only through logs and a false prepared state. Rate recalc returns zero in bypass because DCO output is considered low. The driver mixes devm-managed registration with explicit unregister callbacks in its error/remove cleanup path, so cleanup behavior should be checked carefully for double-unregister regressions if refactored.

## Test Signals

Compile with `CONFIG_COMMON_CLK_TI_ADPLL` built-in and module. Probe DT nodes for both ADPLL-S and ADPLL-LJ, verify all `clock-output-names` are present, and inspect onecell outputs. Exercise prepare/unprepare, bypass parent switching, clkout gates, and DCO rate calculation against programmed M/N/fractional registers. Fault-injection or hardware tests should validate lock-timeout logging and behavior when parent clocks are missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/adpll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/apll.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/apll.c

## Purpose

`apll.c` implements TI OMAP APLL clock support for DRA7 APLL nodes and legacy OMAP2 APLL nodes. It provides CCF operations for enabling, disabling, checking lock/enable state, fixed-rate recalculation, autoidle control, and device-tree clock registration.

## Important APIs, Types, And Functions

DRA7 support uses `dra7_apll_enable()`, `dra7_apll_disable()`, `dra7_apll_is_enabled()`, and `apll_ck_ops`. It programs `APLL_FORCE_LOCK` or `APLL_AUTO_IDLE` through `dpll_data` control registers and polls idlest status up to `MAX_APLL_WAIT_TRIES`. `of_dra7_apll_setup()` parses parent clocks and register addresses, allocates `clk_hw_omap` and `dpll_data`, and defers registration via `ti_clk_retry_init()` if references are unavailable.

OMAP2 support uses `omap2_apll_is_enabled()`, `omap2_apll_recalc()`, `omap2_apll_enable()`, `omap2_apll_disable()`, and `omap2_apll_hwops` for autoidle. `of_omap2_apll_setup()` parses a single parent, `ti,clock-frequency`, enable bit, idlest shift, and three register addresses, then registers the clock provider.

## Control Flow

`CLK_OF_DECLARE()` hooks call setup functions early for compatible strings `ti,dra7-apll-clock` and `ti,omap2-apll-clock`. DRA7 registration obtains reference and bypass parent clocks, stores their hardware pointers in `dpll_data`, registers the OMAP hardware clock, adds an OF provider, and frees temporary init data. Runtime enable writes the force-lock state and polls idlest until locked. Disable moves to auto-idle. OMAP2 enable writes the locked state and polls idlest; disable writes stopped state; recalc returns the fixed configured frequency only when locked.

## State And Persistence Behavior

APLL state is held in PRCM/DPLL registers: control, autoidle, and idlest fields. Allocated `clk_hw_omap` and `dpll_data` persist as registered CCF objects after setup. OMAP2 autoidle count integration is via `clk_hw_omap_ops`, with actual allow/deny writes delegated to the helper functions in this file.

## Dependencies And Integration Points

The file depends on TI clock low-level ops (`ti_clk_ll_ops`), `clock.h`, OMAP clock registration helpers, DT register parsing, retry initialization, and CCF. It integrates with the OMAP autoidle framework through `allow_idle` and `deny_idle` operations.

## Risks And Edge Cases

Polling loops use a very large retry bound with 1 us delay, so hardware failure can stall boot for noticeable time. In `omap2_apll_set_autoidle()`, the computed value is written to `control_reg` rather than `autoidle_reg`; that is a risk signal because the function reads from `autoidle_reg`. DRA7 setup accepts at least one parent but later attempts to fetch parent index 1, so malformed DT with only one parent will defer/fail later. Retry and cleanup paths must avoid leaking allocated init data.

## Test Signals

Boot DRA7 and OMAP2 DTs containing APLL nodes and check provider registration. Enable and disable APLL consumers while tracing register values and idlest transitions. Verify OMAP2 fixed-rate reporting drops to zero when stopped and returns `ti,clock-frequency` when locked. Test autoidle all-enable/all-disable paths and malformed DT parent/register cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/apll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/autoidle.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/autoidle.c

## Purpose

`autoidle.c` provides TI OMAP clock autoidle support. It lets individual OMAP clocks deny or allow hardware autoidle through per-clock callbacks and also tracks generic device-tree autoidle bit definitions for global enable/disable operations.

## Important APIs, Types, And Functions

`struct clk_ti_autoidle` stores a register, bit shift, flags, name, and list node for generic autoidle bits. `autoidle_clks` stores all DT-discovered entries and `autoidle_spinlock` serializes non-atomic read/modify/write operations. `omap2_clk_deny_idle()` and `omap2_clk_allow_idle()` validate a `struct clk`, convert it to `clk_hw_omap`, and call internal helpers that update `autoidle_count` and invoke `deny_idle` or `allow_idle` only on 0-to-1 and 1-to-0 transitions.

`of_ti_clk_autoidle_setup()` parses `ti,autoidle-shift`, register address 0, and optional `ti,invert-autoidle-bit`, then adds the entry to the generic list. `omap2_clk_enable_autoidle_all()` and `omap2_clk_disable_autoidle_all()` walk both CCF OMAP clocks and generic list entries to allow or deny hardware autoidle globally.

## Control Flow

During clock DT setup, nodes with `ti,autoidle-shift` are registered in `autoidle_clks`. During SoC clock init, several TI files call `omap2_clk_disable_autoidle_all()` to force clocks out of autoidle for predictable initialization. Later code can call the enable-all path to restore hardware autoidle. Individual clock users can deny and allow idle around critical sections using the exported functions.

## State And Persistence Behavior

The file maintains two forms of state: per-clock `autoidle_count` in `clk_hw_omap` and a global list of generic autoidle register bits. Hardware autoidle state persists in PRCM registers. The list entries allocated during init are not freed, which matches early boot clock setup lifetime.

## Dependencies And Integration Points

The code depends on TI clock low-level read/write ops, `clock.h`, OMAP CCF iteration via `omap2_clk_for_each()`, and DT properties. It integrates with OMAP APLL, interface clock, DPLL, and clockdomain helpers through `allow_idle`/`deny_idle` callbacks.

## Risks And Edge Cases

`_omap2_clk_allow_idle()` decrements `autoidle_count` without an explicit underflow guard; unbalanced allow calls can wrap the counter and prevent autoidle from being restored. Generic autoidle read/modify/write operations are not locked by `autoidle_spinlock` in the global allow/deny functions, so callers rely on init-time or externally serialized use. Inverted autoidle bits must be described accurately or global enable/disable will do the opposite of what hardware expects.

## Test Signals

Boot logs should show no autoidle setup failures for valid DT nodes. Instrument PRCM registers before and after `omap2_clk_disable_autoidle_all()` and `omap2_clk_enable_autoidle_all()`. Add tests for balanced and intentionally unbalanced deny/allow sequences, and verify inverted-bit DT nodes change in the expected direction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/autoidle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clk-2xxx.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/clk-2xxx.c

## Purpose

`clk-2xxx.c` performs clock alias registration and early initialization for OMAP2420 and OMAP2430 SoCs. It maps legacy device/connection names to DT clock names, initializes OMAP2 clock type voltage/processor scaling support, disables autoidle, enables required early clocks, and logs the main clock rates.

## Important APIs, Types, And Functions

`omap2xxx_clks[]` is the common alias table for OMAP2, covering fixed clocks, APLLs, DPLL/core/MPU/DSP/GFX clocks, DSS, timers, MCBSP, McSPI, UART, GPIO, watchdog, I2C, crypto, USB, and timer parent aliases. `omap2420_clks[]` and `omap2430_clks[]` add SoC-specific aliases. `enable_init_clks[]` lists clocks kept enabled during init: APLL96, APLL54, sync 32k, omapctrl, GPMC, and SDRC. `omap2xxx_dt_clk_init()` performs common initialization, while `omap2420_dt_clk_init()` and `omap2430_dt_clk_init()` select the SoC-specific table.

## Control Flow

The SoC-specific init function calls `omap2xxx_dt_clk_init()` with a selector. Common aliases are registered first, then OMAP2420 or OMAP2430 aliases. `omap2xxx_clkt_vps_init()` initializes clock-type behavior, autoidle is disabled globally, required init clocks are enabled, and an informational crystal/DPLL/MPU rate line is printed using `clk_get_sys()` and `clk_get_rate()`.

## State And Persistence Behavior

The persistent software state is CCF alias registration and enabled init clocks. Hardware PRCM state changes when autoidle is disabled and the init clocks are prepared/enabled. The file does not store private mutable state after init.

## Dependencies And Integration Points

It depends on TI DT clock registration helpers, OMAP2 clock-type support, autoidle support, and the legacy consumer naming expected by OMAP platform devices. It integrates with board DT data that defines the underlying clock nodes referenced by the alias names.

## Risks And Edge Cases

Alias names are compatibility-sensitive. Removing or renaming entries can break older platform devices that still request clocks by legacy con_id/dev_id. Missing base clocks cause rate logging or init-clock enables to fail. The init sequence assumes autoidle should be disabled before enabling critical boot clocks.

## Test Signals

Boot OMAP2420 and OMAP2430 DT systems and verify the crystal/DPLL/MPU rate line. Check that legacy consumers such as timers, I2C, McSPI, MCBSP, DSS, USB, watchdog, crypto, and MMC obtain clocks. Confirm listed init clocks remain enabled and that autoidle disable does not regress suspend/resume expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clk-2xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clk-33xx.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/clk-33xx.c

## Purpose

`clk-33xx.c` defines AM33xx clkctrl metadata, legacy aliases, and clock initialization fixups. It describes PRCM clkctrl register blocks for AM335x-style domains and applies platform-specific parent selections for timers and watchdogs.

## Important APIs, Types, And Functions

The file declares many `omap_clkctrl_reg_data` arrays for L4LS, L3S, L3, L4HS, PRUSS OCP, CPSW 125 MHz, LCDC, 24 MHz, L4 WKUP, L3 AON, WKUP M3, MPU, RTC, GFX L3, and CEFUSE domains. Bit-data arrays describe GPIO debounce gates and debug subsystem mux/divider/gate bits. `am3_clkctrl_data[]` maps physical clkctrl base addresses to these arrays. `am33xx_clks[]` provides legacy aliases for timers, GPIO debounce clocks, debug clocks, STM/trace clocks, and clkdiv32k. `enable_init_clks[]` lists DDR/MPU DPLL outputs, L3/L4 clocks, errata-related debug clock, suspend-needed L3 main, and `clkout2_ck`.

## Control Flow

`am33xx_dt_clk_init()` registers aliases, disables autoidle, adds aliases, enables init clocks, then applies fixups: timer3 and timer6 parents are set to `sys_clkin_ck` because default TCLKIN may be absent; WDT1 parent is set to `clkdiv32k_ick` to avoid inaccurate on-chip 32 kHz RC oscillator behavior.

## State And Persistence Behavior

The clkctrl metadata is `__initconst` and discarded after boot. Persistent effects are registered clocks/aliases and PRCM register state from enabled init clocks and parent selections. The timer and watchdog parent changes persist in hardware mux registers until reset or later clock operations.

## Dependencies And Integration Points

The file depends on AM3 DT binding constants, TI clkctrl helpers, OMAP autoidle, and CCF lookup by legacy names. It integrates with AM33xx peripherals including UART, MMC, ELM, I2C, SPI, timers, RNG, GPIO, DCAN, EPWMSS, GPMC, MCASP, PRUSS, CPSW, LCDC, WKUP, debug, RTC, GFX, and CEFUSE.

## Risks And Edge Cases

The fixup code does not check `clk_get_sys()` return values before `clk_set_parent()`, so missing aliases can produce bad pointer usage depending on CCF behavior. Clkctrl names such as `l3-aon-clkctrl:0000:0` are generated contracts with consumers; typos break aliases and init clocks. Errata-driven always-on clocks must be preserved for suspend and debug stability.

## Test Signals

Boot AM335x/AM33xx DT systems and verify clkctrl registration, timer3/timer6 parent selection, WDT1 parent selection, and `clkout2_ck` availability for external peripherals. Exercise GPIO debounce, UART, MMC, I2C, SPI, DCAN, PRUSS, CPSW, LCDC, RTC, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clk-33xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clk-3xxx.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/clk-3xxx.c

## Purpose

`clk-3xxx.c` provides OMAP3/AM35xx clock initialization and special clock hardware operations. It handles ES-specific SSI/DSS/USBHOST/HSOTGUSB idlest bit locations, AM35xx IPSS companion/ack logic, aliases for OMAP3 variants, DPLL5 USB erratum programming, and early init sequencing.

## Important APIs, Types, And Functions

The file exports several `clk_hw_omap_ops`: `clkhwops_omap3430es2_iclk_ssi_wait`, `clkhwops_omap3430es2_dss_usbhost_wait`, `clkhwops_omap3430es2_iclk_dss_usbhost_wait`, `clkhwops_omap3430es2_iclk_hsotgusb_wait`, `clkhwops_am35xx_ipss_module_wait`, and `clkhwops_am35xx_ipss_wait`. Their `find_idlest` and `find_companion` callbacks adjust register offsets and bit positions where default OMAP logic does not match hardware.

Alias tables cover common OMAP3 timer aliases, OMAP3430 ES1/ES2 SSI and USB clock names, AM35xx clocks, and DSS variants. `omap3_clk_lock_dpll5()` programs DPLL5 and its M2 divider for the USB host clock drift erratum. `omap3xxx_dt_clk_init()` performs variant-specific registration and common initialization.

## Control Flow

Variant init functions call `omap3xxx_dt_clk_init()` with a SoC selector. The common function registers base and variant alias tables, disables autoidle, adds aliases, enables `sdrc_ick`, `gpmc_fck`, and `omapctrl_ick`, prints oscillator/core/MPU rates, and locks DPLL5 for all but OMAP3430 ES1. Runtime enable paths using the exported hwops call the custom idlest/companion callbacks while waiting for module clocks.

## State And Persistence Behavior

Alias registrations and init clock enables persist in CCF state. DPLL5 programming persists in hardware registers and is required for stable USB host operation. The exported `clk_hw_omap_ops` are static const behavior tables used by clock definitions elsewhere.

## Dependencies And Integration Points

The file depends on `clock.h`, TI/OMAP clock helpers, OMAP3 DPLL definitions, autoidle, and CCF. It integrates with SSI, DSS, USBHOST, HSOTGUSB, AM35xx IPSS, SDRC, GPMC, omapctrl, timers, and variant-specific DT clock data.

## Risks And Edge Cases

Hardware idlest bit shifts differ by module and chip revision; using default wait ops can hang enables or skip needed waits. `omap3_clk_lock_dpll5()` does not check `clk_get()` errors before setting rates and preparing clocks. The USB erratum frequency must stay aligned with DPLL implementation expectations because DPLL rate handlers detect the special frequency.

## Test Signals

Boot OMAP3430 ES1, OMAP3430 ES2+, OMAP3630, and AM35xx variants where possible. Exercise SSI, DSS, USB host, HSOTGUSB, and AM35xx IPSS peripherals while checking module enable waits. Verify DPLL5 and DPLL5_M2 rates for USB host and inspect boot rate logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clk-3xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clk-43xx.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/clk-43xx.c

## Purpose

`clk-43xx.c` defines AM43xx and AM438x clkctrl metadata, clock aliases, and initialization fixups. It describes AM4 PRCM domains and sets the CPSW CPTS reference clock parent for stable PTP operation.

## Important APIs, Types, And Functions

The file declares clkctrl register arrays for L3S TSC, L4 WKUP AON, L4 WKUP, MPU, GFX L3, RTC, L3, L3S, PRUSS OCP, L4LS, EMIF, DSS, and CPSW 125 MHz domains. Bit-data arrays describe counter 32K, GPIO debounce gates, and USB OTG SS refclk gates. `am4_clkctrl_data[]` covers the full AM43xx set, while `am438x_clkctrl_data[]` omits RTC-related blocks for AM438x. `am43xx_clks[]` provides legacy aliases for timers, GPIO debounce clocks, synctimer, and USB refclks. `enable_init_clks[]` keeps L3 main enabled for suspend.

## Control Flow

`am43xx_dt_clk_init()` registers aliases, disables autoidle, enables the init clocks, adds aliases, and then changes `cpsw_cpts_rft_clk` parent to `dpll_core_m5_ck` because the default `dpll_core_m4_ck` causes PTP clockcheck errors.

## State And Persistence Behavior

The clkctrl descriptions are init-only. Persistent state includes registered CCF clocks/aliases, disabled autoidle state, enabled L3 main clock, and the hardware mux parent selection for `cpsw_cpts_rft_clk`.

## Dependencies And Integration Points

The file depends on AM4 binding constants, TI clkctrl helpers, OMAP autoidle, and CCF legacy lookup. It integrates with AM43xx peripherals including ADC/TSC, WKUP M3, MPU, GFX, RTC, AES/DES/SHA/TPCC/TPTC, USB OTG SS, PRUSS, GPIO, DCAN, EPWMSS, ELM, HDQ, I2C, mailbox, MMC, RNG, SPI, timers, UART, OCP2SCP, EMIF, DSS, and CPSW.

## Risks And Edge Cases

The CPTS parent fixup assumes both named clocks are registered; missing aliases can break PTP setup. AM43xx and AM438x clkctrl data differ, so using the wrong table can expose nonexistent RTC blocks or omit needed clocks. `CLKF_NO_IDLEST` and `CLKF_SW_SUP` flags encode hardware behavior and should not be changed without TRM validation.

## Test Signals

Boot AM43xx and AM438x DTs and verify clkctrl coverage. Exercise CPSW PTP and confirm no clockcheck regressions. Test USB OTG SS, GPIO debounce, timers, UART/I2C/SPI/MMC, PRUSS, DSS, and suspend/resume with L3 main retained.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clk-43xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clk-44xx.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/clk-44xx.c

## Purpose

`clk-44xx.c` provides OMAP4 clock-controller metadata, aliases, and default DPLL programming. It describes many OMAP4 clkctrl modules and performs early configuration of the ABE and USB DPLLs.

## Important APIs, Types, And Functions

The file defines default rates `OMAP4_DPLL_ABE_DEFFREQ` and `OMAP4_DPLL_USB_DEFFREQ`. Large `omap_clkctrl_reg_data` and `omap_clkctrl_bit_data` tables describe MPUSS, Tesla/DSP, ABE, L4 AO, L3 main, Ducati/IPU, DMA, EMIF, D2D, L4 CFG, L3 INSTR, IVAHD, ISS, DSS, GPU, L3 INIT, L4 PER, L4 SECURE, and WKUP domains. Bit data models module subclocks as gates, muxes, and dividers for AESS, DMIC, McASP, McBSP, SlimBus, timers, DSS, GPU, MMC, HSI, USB host/OTG/TLL, OCP2SCP, GPIO, McSPI, UART, and security modules.

`omap4_clkctrl_data[]` maps physical clkctrl base addresses to register arrays. `omap44xx_clks[]` provides legacy aliases for audio, display, GPIO debounce, MMC, timers, USB host/TLL/OTG, MCBSP, SlimBus, and other generated clkctrl subclocks. `omap4xxx_dt_clk_init()` performs initialization.

## Control Flow

OMAP4 init registers aliases, disables autoidle, adds aliases, then sets the ABE DPLL reference and bypass muxes to `sys_32k_ck`, programs `dpll_abe_ck` to 98.304 MHz, programs `dpll_abe_m2x2_ck` to 196.608 MHz, programs USB DPLL to 960 MHz, and programs USB M2 to 480 MHz. Errors are logged but do not abort the init function.

## State And Persistence Behavior

Clkctrl tables are init-only metadata. Persistent effects include registered clocks/aliases, disabled autoidle state, ABE DPLL parent selections, ABE and USB DPLL rates, and any module clock state changed by consumers. The DPLL programming is essential after warm reboot and for USB operation.

## Dependencies And Integration Points

The file depends on OMAP4 binding constants, TI clkctrl helpers, DPLL support, autoidle, and CCF. It integrates with OMAP4 audio back end, display, GPU, IPU/Ducati, IVAHD, ISS, USB, MMC, timers, GPIO, I2C, UART, McSPI, SlimBus, McBSP, security accelerators, EMIF, and WKUP peripherals.

## Risks And Edge Cases

The init path logs DPLL setup failures but returns success, so downstream peripheral failures may be the only symptom. Many aliases are generated clkctrl names with register offsets and bit indices; any mismatch breaks legacy consumers. ABE DPLL warm-reboot behavior depends on both reference and bypass muxes using `sys_32k_ck`. USB DPLL rates must remain at preferred TRM values for USB stability.

## Test Signals

Boot OMAP4430/OMAP4460 systems and verify ABE and USB DPLL rates. Inspect `clk_summary` for ABE, DSS, GPU, MMC, USB host/OTG/TLL, and timer generated clocks. Exercise audio, display, USB, MMC, GPIO debounce, timers, I2C/SPI/UART, security modules, and warm reboot paths involving ABE timers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clk-44xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clk-54xx.c -->
# sources/distributed-fs/ceph-client/drivers/clk/ti/clk-54xx.c

## Purpose

`clk-54xx.c` provides OMAP5 clock-controller metadata, aliases, and default DPLL programming. It is the OMAP5 counterpart to the OMAP4 clock init file, with updated clkctrl domains and generated subclock aliases for OMAP54xx devices.

## Important APIs, Types, And Functions

The file defines `OMAP5_DPLL_ABE_DEFFREQ` at 98.304 MHz and `OMAP5_DPLL_USB_DEFFREQ` at 960 MHz. `omap_clkctrl_reg_data` and `omap_clkctrl_bit_data` arrays describe MPU, DSP, ABE, L3 main, IPU, DMA, EMIF, L4 CFG, L3 INSTR, L4 PER, L4 SECURE, IVA, DSS, GPU, L3 INIT, and WKUPAON domains. Bit data describes AESS divider, DMIC/McBSP sync muxes, timers, GPIO debounce clocks, DSS gates, GPU mux/divider bits, MMC mux/dividers, USB host/TLL gates and muxes, SATA refclk, USB OTG SS refclk, GPIO1 debounce, and timer1 mux.

`omap5_clkctrl_data[]` maps OMAP5 PRCM base addresses to these arrays. `omap54xx_clks[]` aliases generated clkctrl names for timers, audio, DSS, GPIO debounce, MCBSP, MMC, SATA, USB, and UTMI clocks. `omap5xxx_dt_clk_init()` performs init-time registration and DPLL programming.

## Control Flow

OMAP5 init registers aliases, disables autoidle, adds aliases, sets ABE DPLL reference and bypass muxes to `sys_32k_ck`, programs `dpll_abe_ck` and `dpll_abe_m2x2_ck`, programs USB DPLL and USB M2, and logs errors if any step fails. The function returns zero regardless of logged configuration errors.

## State And Persistence Behavior

The clkctrl metadata is init-only. Persistent state includes clock aliases, disabled autoidle, ABE mux parent choices, ABE DPLL rate, ABE M2x2 rate, USB DPLL rate, and USB M2 rate. Runtime module clock state is then managed by CCF consumers through clkctrl-generated clocks.

## Dependencies And Integration Points

The file depends on OMAP5 binding constants, TI clkctrl support, DPLL helpers, autoidle, and CCF. It integrates with OMAP5 DSP, ABE/audio, IPU, EMIF, DSS, GPU, MMC, USB host/TLL/OTG SS, SATA, timers, GPIO, I2C, McSPI, UART, security accelerators, DMA, and WKUPAON peripherals.

## Risks And Edge Cases

As with OMAP4, DPLL configuration errors are logged but not returned. Generated clkctrl aliases must match DT clock names and register bit positions exactly. ABE warm-reboot stability relies on both ABE reference and bypass muxes using `sys_32k_ck`. USB and SATA peripheral stability depends on correct high-frequency reference clock parents and DPLL rates.

## Test Signals

Boot OMAP5 hardware and verify ABE/USB DPLL rates and parent muxes. Inspect `clk_summary` for generated OMAP5 clkctrl clocks. Exercise audio, MCBSP, DSS/display, GPU, MMC, USB host/TLL/OTG SS, SATA, GPIO debounce, timers, I2C/SPI/UART, security modules, and warm reboot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ti/clk-54xx.c -->
