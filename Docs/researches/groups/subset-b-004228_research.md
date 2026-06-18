# subset-b-004228 Research

Grouped research for memory-controller, external-bus, and flash-interface sources under `sources/distributed-fs/ceph-client/drivers/memory`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/renesas-rpc-if.c -->
# sources/distributed-fs/ceph-client/drivers/memory/renesas-rpc-if.c

Purpose: core Renesas RPC-IF/xSPI platform driver that exposes a common flash controller service to SPI NOR and HyperFlash virtual child drivers. It maps controller registers and direct-map aperture, chooses either RPC-IF or xSPI register programming based on compatible data, and exports preparation, manual-transfer, direct-map read, and xSPI direct-map write helpers.

Important APIs/types/functions: `struct rpcif_impl` selects hardware-specific callbacks, status register, and completion bit. `struct rpcif_info` binds regmap config, implementation, controller type, and timing. `struct rpcif_priv` stores MMIO, regmap, reset, clocks, virtual child platform device, direct-map size, prepared command fields, transfer buffer, and current bus state. Exported APIs are `rpcif_sw_init()`, `rpcif_hw_init()`, `rpcif_prepare()`, `rpcif_manual_xfer()`, `rpcif_dirmap_read()`, and `xspi_dirmap_write()`.

Control flow: probe inspects the first flash child node and creates `rpc-if-spi` for `jedec,spi-nor` or `rpc-if-hyperflash` for `cfi-flash`. It maps `regs` and `dirmap`, initializes a custom regmap, obtains reset and optional clocks, and registers the virtual child. Callers initialize hardware, call `rpcif_prepare()` with a `struct rpcif_op`, then use manual or direct-map transfer helpers under runtime PM. RPC-IF manual transfers program SM* registers and move data in 1/2/4/8 byte chunks. RPC reads without an address phase use the direct-map workaround. xSPI manual transfers program command/address/data buffers and wait on `XSPI_INTS_CMDCMP`. Direct-map paths configure read/write command-map state before `memcpy_fromio()` or `memcpy_toio()`.

State and persistence: runtime state is volatile hardware register programming plus cached prepared command fields in `rpcif_priv`. Clocks are intentionally kept enabled across runtime use because toggling the SPI clocks at runtime can break flash writes. Suspend disables clocks and resume re-enables them. There is no disk persistence.

Dependencies and integration: integrates with platform OF matching, regmap, reset control, runtime PM, Linux clock APIs, `memory/renesas-rpc-if.h`, `renesas-rpc-if-regs.h`, and `renesas-xspi-if-regs.h`. Its virtual child devices are the main integration point for SPI NOR and HyperFlash memory drivers.

Risks: `rpcif_reg_read()` and `rpcif_reg_write()` depend on `xfer_size` being set before SMRDR/SMWDR access. Error recovery resets hardware and reinitializes using `bus_size == 2` as a HyperFlash hint, which must remain aligned with init state. The xSPI direct write caps one write to `MWRSIZE_MAX`. Probe accepts only the first child and rejects unknown flash compatibles. Many bitfield values are controller-specific and easy to regress without hardware.

Test signals: build with RPC-IF and xSPI compatibles, probe SPI NOR and CFI HyperFlash children, read JEDEC ID through the no-address workaround, exercise 1/2/4/8 byte manual transfers, direct-map reads across aperture boundaries, xSPI mapped writes under 64 bytes and shorter push writes, suspend/resume clock restoration, and timeout/error reset recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/renesas-rpc-if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/renesas-xspi-if-regs.h -->
# sources/distributed-fs/ceph-client/drivers/memory/renesas-xspi-if-regs.h

Purpose: register definition header for the Renesas RZ xSPI interface used by `renesas-rpc-if.c`. It names wrapper, bridge-map, command-map, command-direct, calibration, interrupt, and protocol-mode bitfields.

Important APIs/types/functions: no functions or types are declared. The important constants are `XSPI_BMCFG_*`, `XSPI_CMCFG*`, `XSPI_LIOCFGCS0`, `XSPI_BMCTL*`, `XSPI_CDCTL0`, `XSPI_CDTBUF0`, command data/address buffer offsets, interrupt bits, `MWRSIZE_MAX`, and protocol encodings such as `PROTO_1S_2S_2S` and `PROTO_4S_4S_4S`.

Control flow: included by the Renesas core driver when programming xSPI hardware. The core combines macros with `regmap_update_bits()` and `regmap_write()` to configure command-map direct reads/writes, manual transfers, protocol width, chip-select timing, interrupt enable/clear, and maximum combined mapped write size.

State and persistence: the header stores no state. It defines the volatile MMIO layout that determines xSPI controller state when written by the driver.

Dependencies and integration: depends only on `<linux/bits.h>`. Integration is private to xSPI-capable Renesas memory-controller code.

Risks: incorrect masks or shifts can silently program invalid command/address/data sizes. `PROTO_1S_4S_4S` and `PROTO_4S_4S_4S` values must match hardware encoding. `MWRSIZE_MAX` is consumed as a write-size limit and affects direct-map write chunking.

Test signals: compile the xSPI path, confirm `max_register = XSPI_INTE` covers the highest used offset, validate manual read/write completion interrupts, and verify direct-map read/write protocol modes with single, dual, and quad bus-width operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/renesas-xspi-if-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/samsung/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/memory/samsung/Kconfig

Purpose: Kconfig menu for Samsung Exynos memory-controller drivers. It gates the Exynos5422 Dynamic Memory Controller DVFS driver and the Exynos SROM controller driver under a top-level `SAMSUNG_MC` option.

Important APIs/types/functions: configuration symbols are `SAMSUNG_MC`, `EXYNOS5422_DMC`, and `EXYNOS_SROM`. `EXYNOS5422_DMC` selects `DDR`, depends on Exynos or compile-test I/O support, simple ondemand devfreq governor, `PM_DEVFREQ`, and `PM_DEVFREQ_EVENT`. `EXYNOS_SROM` depends on ARM Exynos or compile-test I/O support.

Control flow: enabling `SAMSUNG_MC` exposes the two child options. The DMC option permits building `exynos5422-dmc.o` as built-in or module. The SROM option is boolean and builds `exynos-srom.o` when selected.

State and persistence: no runtime state. The file controls build-time availability and dependency closure for runtime drivers.

Dependencies and integration: integrates with `drivers/memory/samsung/Makefile` and kernel subsystems needed by the drivers: DDR timing helpers, devfreq, devfreq-event, regulators, clocks, and platform MMIO.

Risks: missing devfreq or DDR dependencies would produce compile or link failures in `exynos5422-dmc.c`. Making SROM modular would conflict with its `builtin_platform_driver()` use. The `COMPILE_TEST` branches are important for cross-architecture build coverage.

Test signals: run Kconfig combinations for `ARCH_EXYNOS`, `COMPILE_TEST`, devfreq disabled, and SROM-only builds; confirm the Makefile selects only the intended objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/samsung/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/samsung/Makefile -->
# sources/distributed-fs/ceph-client/drivers/memory/samsung/Makefile

Purpose: object mapping for Samsung memory-controller drivers.

Important APIs/types/functions: maps `CONFIG_EXYNOS5422_DMC` to `exynos5422-dmc.o` and `CONFIG_EXYNOS_SROM` to `exynos-srom.o`.

Control flow: kbuild includes these objects when their Kconfig symbols are enabled. There is no composite object or special ordering logic.

State and persistence: no runtime state. Build output depends only on selected Kconfig symbols.

Dependencies and integration: paired with `drivers/memory/samsung/Kconfig`. The selected objects integrate with platform-driver registration in their respective C files.

Risks: symbol/object name drift would leave drivers unbuilt. Because SROM is boolean and uses `builtin_platform_driver()`, changing this Makefile to modular behavior would require code changes.

Test signals: inspect `make M=drivers/memory/samsung` or full kernel build logs for `exynos5422-dmc.o` and `exynos-srom.o` under corresponding configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/samsung/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/samsung/exynos-srom.c -->
# sources/distributed-fs/ceph-client/drivers/memory/samsung/exynos-srom.c

Purpose: Samsung Exynos SROM controller driver for static external memory banks. It configures child bank timing from device tree, populates child devices when all banks decode successfully, and saves/restores SROM registers across system sleep.

Important APIs/types/functions: `struct exynos_srom_reg_dump` stores register offset/value pairs. `struct exynos_srom` stores device, MMIO base, and register dump array. Key helpers are `exynos_srom_alloc_reg_dump()`, `exynos_srom_configure_bank()`, `exynos_srom_probe()`, `exynos_srom_save()`, and `exynos_srom_restore()`.

Control flow: probe maps the controller resource, allocates dump entries for `BW` and `BC0..BC3`, then iterates child nodes. Each child must provide `reg` and `samsung,srom-timing`; `reg-io-width` defaults to 1 byte and `samsung,srom-page-mode` sets the page-mode bit. `exynos_srom_configure_bank()` updates the packed `BW` chip-select field and writes the timing register. If any bank is malformed, the driver remains bound for suspend/resume but skips `of_platform_populate()`.

State and persistence: configured SROM register values persist in hardware while powered. The driver keeps a sleep-time snapshot of selected registers in memory and restores them on resume. It does not persist data to disk.

Dependencies and integration: uses OF child parsing, platform MMIO mapping, relaxed I/O accessors, and `of_platform_populate()` for external-memory children. Register bit definitions come from `exynos-srom.h`.

Risks: bank index is converted to a shift and register offset by multiplying by four; bad DT bank numbers can address unintended bank-control offsets because only child parsing validates required properties. The dump array uses `kzalloc_objs()` rather than devm and has no explicit free path, acceptable for builtin lifetime but worth noting. A single bad child prevents all child device population.

Test signals: boot with `samsung,exynos4210-srom`, validate each child bank timing in `BW/BCx`, check 8-bit and 16-bit external devices, inject malformed child timing and confirm no children populate, then run suspend/resume and verify registers are restored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/samsung/exynos-srom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/samsung/exynos-srom.h -->
# sources/distributed-fs/ceph-client/drivers/memory/samsung/exynos-srom.h

Purpose: private register definition header for the Exynos SROM controller.

Important APIs/types/functions: defines offsets `EXYNOS_SROM_BW` and `EXYNOS_SROM_BC0` through `EXYNOS_SROM_BC5`, packed bit shifts for data width, address mode, wait enable, byte enable, chip-select shifts, `EXYNOS_SROM_BW__CS_MASK`, and `BCx` timing/page-mode shifts.

Control flow: `exynos-srom.c` uses these constants to update the packed bus-width/control register and compose each bank-control timing value from DT timing cells.

State and persistence: no state is stored in the header. It describes hardware register state that the C driver saves, restores, and configures.

Dependencies and integration: private to the Samsung SROM driver. It intentionally has only include guards and macros.

Risks: the comment says one `BW` register holds four chip-select fields even though offsets and shifts include NCS4/NCS5, so maintainers must verify SoC-specific coverage before adding bank 4/5 programming. Incorrect shift definitions directly alter external-bus timings.

Test signals: compile `exynos-srom.c`, compare generated `BW`/`BCx` values against the Exynos SROM manual, and test page-mode and 16-bit width device-tree configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/samsung/exynos-srom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/samsung/exynos5422-dmc.c -->
# sources/distributed-fs/ceph-client/drivers/memory/samsung/exynos5422-dmc.c

Purpose: Exynos5422 Dynamic Memory Controller driver providing devfreq-based DRAM/DMC voltage and frequency scaling. It calculates LPDDR3 timing registers from DT DDR timing data, switches memory clocks through a safe bypass path, and estimates load through devfreq-event counters or DREX performance-counter interrupts.

Important APIs/types/functions: `struct exynos5_dmc` owns MMIO bases for two DREX channels, clock/regmap/regulator handles, OPP table, current rate/voltage, generated timing arrays, devfreq counters, IRQ timestamps, and governor load data. Core functions include `exynos5_init_freq_table()`, `of_get_dram_timings()`, `create_timings_aligned()`, `exynos5_dmc_target()`, `exynos5_dmc_change_freq_and_volt()`, `exynos5_dmc_get_status()`, `exynos5_performance_counters_init()`, `dmc_irq_thread()`, and `exynos5_dmc_probe()`.

Control flow: probe maps both DREX resources, gets the clock syscon, loads OPPs, obtains `vdd`, initializes clocks and current voltage, generates timings, enables pause-on-clock-switching, and chooses IRQ mode only when both named IRQs and module parameter `irqmode=1` are present. Devfreq calls `exynos5_dmc_target()`, which chooses a recommended OPP, locks, raises voltage if needed, switches to the stable SPLL bypass parent, programs bypass timing bank 1, programs final timing bank 0, changes BPLL rate, switches back to BPLL, then lowers voltage if possible. Polling mode reads devfreq-event devices. IRQ mode estimates load from counter overflow intervals and calls `update_devfreq()`.

State and persistence: persistent runtime state is in `exynos5_dmc`: current rate/voltage, timing arrays, counter handles, and last overflow timestamps. Hardware state spans DREX timing registers, clock muxes/PLLs, regulator voltage, performance-counter registers, and pause configuration. No disk persistence exists.

Dependencies and integration: depends on clocks, regulators, PM OPP, devfreq simple ondemand, devfreq-event, syscon regmap, LPDDR3 parsing from `of_memory.h`, and DDR timing definitions. Device tree must provide DREX resources, `samsung,syscon-clk`, OPP table, `vdd`, clock names, `device-handle`, and optionally `devfreq-events` or DREX IRQs.

Risks: frequency/voltage transition ordering is safety critical. `of_get_dram_timings()` allocates timing arrays sized by `TIMING_COUNT` even though indexed by `opp_count`; this assumes OPP count does not exceed the number of timing fields. `exynos5_dmc_align_bypass_dram_timings()` computes an index but always uses highest-frequency bypass timings. Several `clk_prepare_enable()` calls ignore return values. The global devfreq profile is mutated for initial frequency and polling interval, so multiple instances would share profile state.

Test signals: probe with valid OPP and LPDDR3 DT data, verify generated timing registers per OPP, run devfreq transitions up and down under memory load, check regulator voltage ordering, test polling and `irqmode=1`, confirm counters reset/reenable, run suspend-like clock parent stress, and validate cleanup disables counters and BPLL clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/samsung/exynos5422-dmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/stm32-fmc2-ebi.c -->
# sources/distributed-fs/ceph-client/drivers/memory/stm32-fmc2-ebi.c

Purpose: STM32 FMC2 External Bus Interface driver configuring SRAM, PSRAM, NOR, and NAND chip-select resources from device-tree child nodes. It translates bus/timing properties into FMC2 registers, handles STM32MP1 versus STM32MP25 register differences, restores setup after sleep, and populates child devices.

Important APIs/types/functions: `struct stm32_fmc2_ebi_data` supplies per-SoC property tables, enable register/bit, setup save/restore callbacks, optional RIF access checks, and semaphore callbacks. `struct stm32_fmc2_ebi` stores device, clock, regmap, bank assignment, security access, semaphore bitmap, and saved register values. `struct stm32_fmc2_prop` describes one DT property, including validation, timing conversion, and setter callbacks. Major helpers include transaction-type setup, bus-width/cache-size setters, timing conversion, `stm32_fmc2_ebi_mp25_check_rif()`, `stm32_fmc2_ebi_parse_dt()`, probe/remove, and PM callbacks.

Control flow: probe gets a syscon regmap from the node, clock, optional reset, enables runtime PM, resets hardware, checks MP25 RIF/secure access, parses each available child `reg`, rejects duplicate/invalid banks, optionally acquires semaphores, configures EBI chip selects, marks assigned banks, verifies NWAIT sharing on MP1, enables FMC2, populates children, and saves setup. Each chip select is disabled while its property table is applied, then re-enabled. Suspend disables FMC2, releases semaphores, runtime-suspends the clock, and selects sleep pins. Resume reacquires semaphores, restores saved registers, and re-enables FMC2.

State and persistence: runtime state includes assigned bank bitmap, saved BCR/BTR/BWTR/PCSCNTR/CFGR values, access-granted flag, and taken MP25 semaphores. Hardware state is the actual FMC2 bus configuration and resource isolation state. State is preserved only in kernel memory across sleep.

Dependencies and integration: uses regmap, runtime PM, clock/reset, pinctrl sleep states, OF child parsing, `of_platform_populate()`, and STM32 MP25 RIF/semaphore register conventions. It supports compatibles `st,stm32mp1-fmc2-ebi` and `st,stm32mp25-fmc2-ebi`.

Risks: property descriptors are order-sensitive because transaction type must be parsed first. Validation callbacks silently skip unsupported optional properties, which can mask DT mistakes. MP25 secure/CID/semaphore behavior can leave access read-only if CFGR is secure. Timing conversion depends on a nonzero HCLK rate. NWAIT cannot be shared between EBI and NAND on MP1. Error cleanup must release semaphores and disable configured banks.

Test signals: validate DTs for each transaction type, 8/16-bit buses, cclk and mux modes, async/sync timing properties, MP1 NWAIT with NAND conflict, MP25 secure and semaphore access-denied paths, suspend/resume register restoration, child population, and runtime PM clock enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/stm32-fmc2-ebi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/stm32_omm.c -->
# sources/distributed-fs/ceph-client/drivers/memory/stm32_omm.c

Purpose: STM32 Octo Memory Manager driver for STM32MP25. It validates two OSPI child memory-map regions, configures OMM mux and chip-select override behavior, coordinates child clocks/resets, manages AMCR syscfg memory split, and populates OSPI child devices.

Important APIs/types/functions: `struct stm32_omm` stores memory-map resource, three clocks (`omm`, `ospi1`, `ospi2`), child resets, MMIO base, saved `OMM_CR`, child count, and whether the OMM should be restored. Key helpers are `stm32_omm_set_amcr()`, `stm32_omm_toggle_child_clock()`, `stm32_omm_disable_child()`, `stm32_omm_configure()`, `stm32_omm_check_access()`, probe/remove, and runtime/system PM callbacks.

Control flow: probe maps `regs`, gets the `memory_map` resource, checks exactly two children and firewall grants, gets released child resets, enables runtime PM, then either configures OMM when parent and both children are accessible or only verifies AMCR coherency when access is restricted. Configuration fetches all clocks, resets both OSPI children to ensure disabled state, enables runtime PM, computes max child clock rate, resets OMM, parses optional `st,omm-mux`, `st,omm-req2ack-ns`, and `st,omm-cssel-ovr`, writes `OMM_CR`, sets AMCR, then populates children. If mux mode is enabled, child OSPI clocks remain on.

State and persistence: `omm->cr` caches the programmed control register for resume. `restore_omm` marks whether the driver owns OMM programming. Hardware state includes OMM mux/override bits, AMCR memory split, OSPI reset state, and clock enables. There is no persistent storage outside registers.

Dependencies and integration: depends on clocks, reset control, syscon regmap lookup by `st,syscfg-amcr`, STM32 firewall APIs, OF address resources, pinctrl, runtime PM, and platform child population.

Risks: `stm32_omm_set_amcr()` compares DT memory regions against a syscfg register even when it cannot write it, so preconfigured firmware must match DT. The code assumes two children and memory-region names `ospi1`/`ospi2`. `req2ack` conversion uses the fastest child clock and clamps at 256. On populate failure, mux child clocks are disabled only when mux bit is set. Firewall denial changes behavior from configuration to validation-only.

Test signals: probe with two OSPI children, overlapping memory-region rejection, AMCR mismatch rejection, firewall allowed and denied cases, mux and chip-select override DT options, runtime PM clock control, suspend/resume restoration, and child clock state when mux is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/stm32_omm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/memory/tegra/Kconfig

Purpose: Kconfig menu for NVIDIA Tegra memory-controller and external-memory-controller support.

Important APIs/types/functions: `TEGRA_MC` is the top-level bool, defaulting on `ARCH_TEGRA` and selecting `INTERCONNECT`. Child options enable EMC drivers for Tegra20, Tegra30, Tegra124, and Tegra210. Tegra124 selects `TEGRA124_CLK_EMC` on Tegra, Tegra20 selects devfreq and DDR helpers, and Tegra30 selects PM OPP and DDR. `TEGRA210_EMC_TABLE` is an internal bool selected by `TEGRA210_EMC`.

Control flow: when `TEGRA_MC` is enabled, users or platform defaults can enable SoC-specific EMC drivers. The Makefile then includes common MC code plus relevant SoC tables and EMC implementations.

State and persistence: no runtime state. This file controls which memory controller, SMMU/interconnect, reset, timing, and EMC code is compiled.

Dependencies and integration: integrates with `drivers/memory/tegra/Makefile`, SoC architecture symbols, common clock, interconnect, devfreq, PM OPP, and DDR helper subsystems.

Risks: incorrect dependencies can break compile-test or omit required clock/OPP/devfreq support. `TEGRA_MC` selecting interconnect affects runtime topology expectations in `mc.c` and `tegra124-emc.c`.

Test signals: compile with `ARCH_TEGRA`, compile-test each EMC option, and verify selected object files and required subsystem symbols are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/Makefile -->
# sources/distributed-fs/ceph-client/drivers/memory/tegra/Makefile

Purpose: kbuild rules for Tegra memory-controller and EMC drivers.

Important APIs/types/functions: builds the composite `tegra-mc.o` from `mc.o` plus SoC description files selected by architecture config. Separate objects are built for Tegra20/30/124/210 EMC drivers and newer Tegra186-family EMC code. `tegra210-emc-y` composes the Tegra210 EMC core and clock-characterization table.

Control flow: `obj-$(CONFIG_TEGRA_MC)` emits `tegra-mc.o`; `tegra-mc-$(CONFIG_ARCH_...)` appends SoC data such as `tegra114.o`. EMC object selection follows `CONFIG_TEGRA*_EMC` and newer architecture symbols.

State and persistence: no runtime state. Build output follows the selected Kconfig and architecture symbols.

Dependencies and integration: paired with Tegra Kconfig and common driver registration in `mc.c`. The SoC files provide `struct tegra_mc_soc` instances referenced by `mc.c` OF match tables.

Risks: missing SoC object selection causes unresolved `tegra*_mc_soc` references when the OF match entry is compiled. Newer architectures deliberately reuse `tegra186-emc.o`, so object sharing must remain compatible.

Test signals: build each Tegra architecture configuration and compile-test EMC options; inspect `tegra-mc-y` expansion for the expected SoC table files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/mc.c -->
# sources/distributed-fs/ceph-client/drivers/memory/tegra/mc.c

Purpose: common NVIDIA Tegra Memory Controller platform driver. It binds SoC data tables to MMIO, error interrupts, SMMU, reset-controller hot resets, EMEM timing programming, latency allowance defaults, carveout queries, and interconnect provider nodes.

Important APIs/types/functions: exported APIs include `devm_tegra_memory_controller_get()`, `tegra_mc_probe_device()`, `tegra_mc_get_carveout_info()`, `tegra_mc_write_emem_configuration()`, and `tegra_mc_get_emem_device_count()`. Internal core paths include hotreset assert/deassert/status, `tegra_mc_setup_latency_allowance()`, `tegra_mc_setup_timings()`, `tegra30_mc_probe()`, `tegra30_mc_handle_irq()`, `tegra_mc_interconnect_setup()`, and `tegra_mc_probe()`.

Control flow: `arch_initcall()` registers the platform driver early. Probe selects SoC data by OF match, coerces DMA mask to SoC address width, maps registers, creates debugfs root, runs SoC probe hooks, detects enabled channels, registers IRQs and writes masks, registers reset controller if available, initializes interconnect provider nodes, and optionally probes Tegra SMMU. Error IRQ handling identifies channel, decodes status/address/client/error type, logs rate-limited diagnostics, and clears channel/global status. Hotreset assert blocks DMA, waits for idling, then asserts SoC reset; deassert releases reset and unblocks DMA.

State and persistence: `struct tegra_mc` holds SoC data, MMIO pointers, channel count, loaded timing table, reset controller, interconnect provider, SMMU pointer, spinlock, and debugfs root. Hardware state includes interrupt masks, latency allowance registers, EMEM timing registers, reset control bits, and SMMU configuration. No disk persistence exists.

Dependencies and integration: integrates with SoC description files such as `tegra114.c`, `soc/tegra/mc.h`, reset framework, IRQ subsystem, interconnect framework, debugfs, device tree timings selected by RAM code, Tegra fuse RAM code, and optional `CONFIG_TEGRA_IOMMU_SMMU`.

Risks: SoC data must keep client IDs, masks, error status formats, reset bits, and register offsets aligned with silicon. `prevent_deferred_probe` makes missing resources more visible. Error handling for >32-bit addresses requires correct `has_addr_hi_reg` or `mc_addr_hi_mask`. Hotreset waits are bounded and can fail if DMA never idles. Interconnect setup errors are logged but do not fail probe.

Test signals: boot each supported compatible, inject SMMU/page/security errors and verify decoded client/address logs, exercise reset controls for clients, load RAM-code-specific timings and call EMC reconfiguration, validate ICC node registration and sync_state, and test carveout base/size queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/mc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/mc.h -->
# sources/distributed-fs/ceph-client/drivers/memory/tegra/mc.h

Purpose: private Tegra memory-controller header containing common register offsets, error bit definitions, inline MMIO helpers, SoC externs, shared reset ops, IRQ handler declarations, and internal ICC node IDs.

Important APIs/types/functions: defines MC interrupt/status bits, EMEM arbitration/timing registers, error-status field masks, channel and MSS/Tegra264 register offsets, `MC_BROADCAST_CHANNEL`, `tegra_mc_scale_percents()`, `icc_provider_to_tegra_mc()`, `mc_ch_readl()`, `mc_ch_writel()`, `mc_readl()`, `mc_writel()`, SoC extern declarations, `tegra30_mc_probe()`, `tegra30_mc_handle_irq()`, and `TEGRA_ICC_MC/EMC/EMEM` IDs.

Control flow: included by `mc.c` and SoC table files. Inline accessors route broadcast and per-channel MMIO through the appropriate register bases and gracefully return/do nothing if channel broadcast registers are absent.

State and persistence: no independent state. It defines how driver state in `struct tegra_mc` is interpreted when accessing registers and ICC providers.

Dependencies and integration: includes Linux bits/I/O/types and public `<soc/tegra/mc.h>`. It bridges the common driver, SoC description files, SMMU, reset, interrupt, and interconnect code.

Risks: shared register constants are consumed across many SoCs; adding newer SoC fields can accidentally affect older decode paths. `mc_ch_readl()` returning zero when no broadcast channel exists can hide accidental channel access in code that should use `mc_readl()`. Internal ICC IDs must not collide with DT node IDs.

Test signals: compile all Tegra MC variants, validate 32-bit and 64-bit address error decoding, test channel and non-channel SoCs, and run interconnect provider setup using the reserved internal ICC IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/mc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra114.c -->
# sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra114.c

Purpose: Tegra114 SoC data table for the common Tegra memory-controller driver. It enumerates memory clients, latency allowance defaults, SMMU swgroups, reset lines, interrupt masks, and SoC capabilities.

Important APIs/types/functions: the file defines `tegra114_mc_clients[]`, `tegra114_swgroups[]`, `tegra114_groups[]`, `tegra114_smmu_soc`, `tegra114_mc_resets[]`, `tegra114_mc_intmasks[]`, and exported `tegra114_mc_soc`. Client entries map hardware client IDs to names, SMMU enable register bits, latency allowance registers, swgroups, and defaults. Reset entries map DT reset IDs to MC reset control/status bits.

Control flow: `mc.c` selects `tegra114_mc_soc` for compatible `nvidia,tegra114-mc`. During common probe, latency allowance defaults are written from the client table, SMMU setup uses swgroup/group data, IRQ mask enables invalid SMMU page, security violation, and EMEM decode errors, and reset-controller calls use `tegra_mc_reset_ops_common` with the reset table.

State and persistence: no mutable state in this file. Tables describe persistent hardware programming performed by the common driver and SMMU code.

Dependencies and integration: includes Tegra114 memory DT bindings for reset IDs and public/private Tegra MC headers. Integrates with common MC probe, Tegra SMMU, reset framework, error IRQ decoding, and latency allowance setup.

Risks: table correctness is critical: client ID, SMMU bit, latency register, swgroup, and reset bit mismatches cause wrong device attribution or unsafe reset behavior. The DRM SMMU group aggregates several swgroups and must match display/GPU users. Interrupt mask coverage is intentionally narrow compared with newer SoCs.

Test signals: boot Tegra114, verify all memory client IDs decode in MC fault logs, exercise SMMU swgroup enable/disable, assert/deassert each listed reset, check latency allowance register defaults, and trigger masked MC interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra114.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra124-emc.c -->
# sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra124-emc.c

Purpose: NVIDIA Tegra124/Tegra132 External Memory Controller driver. It loads RAM-code-specific EMC timing tables, registers clock-change callbacks used by the Tegra EMC clock, manages OPP-backed voltage/rate changes, exposes debugfs rate clamps, and provides an EMC/DRAM interconnect provider.

Important APIs/types/functions: `struct emc_timing` stores one rate and all burst, calibration, mode, power, pad, ZCAL, and config values needed for a frequency switch. `struct tegra_emc` stores device, MC handle, MMIO, clock, DRAM type/width/count, timing table, last timing, debugfs state, ICC provider, requested min/max rates, and rate mutex. Key functions are `tegra124_emc_prepare_timing_change()`, `tegra124_emc_complete_timing_change()`, `tegra124_emc_load_timings_from_dt()`, `emc_request_rate()`, debugfs min/max setters, `emc_icc_set()`, `tegra124_emc_opp_table_init()`, and probe.

Control flow: probe maps EMC registers, obtains the common MC through `nvidia,memory-controller`, selects a timing subnode by fuse RAM code, reads current DRAM state, registers EMC clock callbacks, gets the `emc` clock, initializes OPP supported-hardware filtering, initializes request clamps, optionally creates debugfs, and registers the EMC interconnect provider. Rate changes go through OPP and clock callbacks: prepare disables dynamic self-refresh/autocal as needed, programs burst registers and MC EMEM arbitration, queues clock-change commands and DRAM mode-register operations, then complete waits for clock-change completion, restores autocal/power/ZCAL/pad state, and caches the new timing.

State and persistence: driver state includes timing table, last applied timing, DRAM geometry, debug clamp values, and per-source rate requests. Hardware state includes EMC timing registers, calibration, mode registers, self-refresh/power bits, MC EMEM timing registers, clock rate, and voltage state managed by OPP.

Dependencies and integration: depends on Tegra clock callbacks (`tegra124_clk_set_emc_callbacks()`), common MC APIs, fuse RAM code, PM OPP, debugfs, interconnect framework, DT timing properties, and SoC speedo ID for OPP hardware selection.

Risks: timing-change sequencing is highly hardware-specific; wrong ordering can corrupt memory. Missing timing data only logs an informational message but leaves fewer valid rates. `try_module_get(THIS_MODULE)` intentionally prevents unload. Interconnect initialization errors are returned through helper logging but the probe ignores the return value. Debugfs min/max and ICC requests share rate clamps, so out-of-range combinations return `-ERANGE`.

Test signals: boot Tegra124/Tegra132 with timing tables for the active RAM code, verify OPP voltage initialization, change rates through clock/OPP, debugfs min/max, and ICC bandwidth requests, observe successful CLKCHANGE completion, validate MC EMEM timing writes, and stress memory traffic during repeated rate transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra124-emc.c -->
