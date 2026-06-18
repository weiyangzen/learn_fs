# subset-b-005365 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/biuctrl.c -->
# sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/biuctrl.c

Purpose: Broadcom STB CPU BIU control early init code. It maps the `brcm,brcmstb-cpu-biu-ctrl` register block, selects per-CPU-family register offsets, configures MCP write pairing, read/write credits, MCP flow credits, writeback throttling, and B53/A72 read-ahead cache controls.

Important APIs and functions: `brcmstb_biuctrl_init()` is an `early_initcall`; `setup_hifcpubiuctrl_regs()` maps MMIO and chooses `b15_cpubiuctrl_regs`, `b53_cpubiuctrl_regs`, `b53_cpubiuctrl_no_wb_regs`, or `a72_cpubiuctrl_regs`; `mcp_write_pairing_set()`, `a72_b53_rac_enable_all()`, and `mcp_a72_b53_set()` write the tuning registers. `cbc_readl()` and `cbc_writel()` centralize offset validity and skip RAC writes when `CONFIG_CACHE_B15_RAC` owns RAC handling.

Control flow: init finds the BIU node, maps registers, reads CPU node compatibility, handles the 7260A0 no-writeback-controller exception, applies write-pairing policy from device tree, enables RAC where applicable, and applies A72/B53 MCP tuning for known family IDs. On suspend, syscore ops save all BIU control registers and restore them on resume.

State and persistence: global `cpubiuctrl_base`, `mcp_wr_pairing_en`, selected register offset table, and `cpubiuctrl_reg_save[]` persist for runtime and sleep transitions. Hardware register state is the durable side effect across boot and resume.

Dependencies and integration: depends on OF, MMIO, CPU compatible strings, `brcmstb_get_family_id()`, `BRCM_ID()`/`BRCM_REV()`, optional PM sleep syscore registration, and optional B15 RAC cache driver. It integrates before most drivers through early init because memory bus/cache policy affects broad system behavior.

Risks and test signals: risks include wrong register layout selection, unsupported CPU node, stale family ID if `common.c` early init did not populate it, and suspend/resume restoring sentinel reads from unavailable registers. Test signals are boot logs for MCP/RAC messages, memcpy or memory throughput checks on B53/A72, suspend/resume stability, and absence of unsupported CPU or MMIO mapping errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/biuctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/common.c -->
# sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/common.c

Purpose: common Broadcom STB SoC identification support. It reads family and product IDs from the SUN_TOP control block very early, exports those IDs, and registers a `soc_device` with family, SoC ID, and revision strings.

Important APIs and functions: `brcmstb_get_family_id()` and `brcmstb_get_product_id()` are exported symbols consumed by other Broadcom STB code such as BIU tuning. `brcmstb_soc_device_early_init()` is an `early_initcall` that maps the first SUN_TOP compatible node and reads offsets 0 and 4. `brcmstb_soc_device_init()` is an `arch_initcall` that allocates `struct soc_device_attribute`, formats `family`, `soc_id`, and `revision`, and calls `soc_device_register()`.

Control flow: both init paths are non-fatal on multi-platform kernels. If no matching SUN_TOP node exists, they return success without registering anything. The early path only reads and caches IDs; the arch path creates user-visible SoC metadata in sysfs.

State and persistence: persistent state is limited to static `family_id` and `product_id` globals plus the registered `soc_device`. There is no cleanup path because this is built-in early platform metadata.

Dependencies and integration: requires OF matching against several Broadcom SUN_TOP compatible strings, `of_iomap()`, `soc_device_register()`, and exported Linux SoC bus metadata. It is an integration point for later drivers that need hardware-family conditionals before normal device probing.

Risks and test signals: risk centers on ID format interpretation because the code shifts differently depending on high nibble presence. Allocation failure can return `-ENOMEM`, but strings allocated before a failed register are freed. Test signals include `/sys/devices/soc0` family/soc_id/revision contents, exported ID users taking the intended family branches, and clean boot on non-Broadcom multi-platform kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/pm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/pm/Makefile

Purpose: build glue for Broadcom STB power management support. It compiles the MIPS PM C implementation and S2/S3 assembly helpers when `CONFIG_MIPS` is enabled.

Important API/build behavior: `obj-$(CONFIG_MIPS)` adds `pm-mips.o`, `s2-mips.o`, and `s3-mips.o`. These objects provide `brcm_pm_do_s2()`, `brcm_pm_do_s3()`, `s3_reentry`, and the arch init logic that installs suspend and power-off operations.

Control flow and integration: the Makefile keeps this PM implementation architecture-specific. Non-MIPS builds of the brcmstb PM directory do not consume the MIPS-only assembly and CP0 register dependencies.

State and persistence: no runtime state is defined here; persistence is via kernel build composition.

Dependencies, risks, and tests: depends on Kbuild selecting this subdirectory from the parent Broadcom STB SoC build. Risks are missing PM symbols if the object list diverges from `pm.h` declarations. Test signals are successful MIPS build/link with suspend symbols resolved and absence of these objects in non-MIPS builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/pm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/pm/pm-mips.c -->
# sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/pm/pm-mips.c

Purpose: MIPS-specific Broadcom STB suspend, deep standby, and power-off orchestration. It maps AON, SRAM, DDR PHY, MEMC arbiter, and timer blocks, installs `platform_suspend_ops`, and provides S2, S3, and S5 control paths around low-level assembly.

Important APIs and functions: `brcmstb_pm_init()` is an `arch_initcall`; `brcmstb_pm_enter()` handles `PM_SUSPEND_STANDBY` and `PM_SUSPEND_MEM`; `brcmstb_pm_s5()` becomes `pm_power_off`; `brcmstb_pm_s2()` prepares the six-word argument block for `brcm_pm_do_s2()`; `brcmstb_pm_s3()` saves CP0 state, MEMC RTS registers, flushes TLB/cache, and calls `brcm_pm_do_s3()`. `brcm_pm_save_cp0_context()` and `brcm_pm_restore_cp0_context()` preserve generic and Broadcom CP0 registers.

Control flow: init maps required OF nodes and bails out with cleanup on mapping failures. S2/S3 both start with `brcmstb_pm_handshake()`, redirect exception vectors to warm restart, run the selected low-power helper, then restore normal interrupt vector behavior. S3 writes a magic value and reentry address into AON SRAM, inhibits DDR reset pulses, saves register context, enters deep standby, then reinitializes CPU/TLB state and restores saved context after wake.

State and persistence: global `ctrl` holds MMIO mappings and MEMC count. S3 persists warm-boot metadata in AON SRAM and saves CP0/MEMC state on the stack for restoration. S5 clears the S3 magic so the next boot is cold.

Dependencies and integration: depends on BMIPS CP0 helpers, `bmips_cpu_setup()`, `BMIPS_WARM_RESTART_VEC`, OF-compatible AON/DDR/timer nodes, assembly helpers in `s2-mips.S` and `s3-mips.S`, and Linux suspend core.

Risks and test signals: high-risk areas include raw physical pointer truncation to `u32`, fixed MEMC0 arbiter assumptions for RTS restore, IRQ/vector state during wake, and hardware timing races covered by the 3 ms handshake delay. Test signals include standby/mem suspend cycles, S5 power-off, warm-boot magic behavior, DDR resume stability, and no leaks from failed MMIO mapping paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/pm/pm-mips.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/pm/pm.h -->
# sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/pm/pm.h

Purpose: shared constants and prototypes for Broadcom STB AON power management. It defines MMIO offsets, bit masks, and the assembly helper contracts used by C and assembly sources.

Important APIs/types/macros: AON offsets include `AON_CTRL_PM_CTRL`, `AON_CTRL_PM_INITIATE`, and `AON_CTRL_HOST_MISC_CMDS`; DDR/timer offsets include `DDR40_PHY_CONTROL_REGS_0_PLL_STATUS`, `DDR40_PHY_CONTROL_REGS_0_STANDBY_CTRL`, and timer registers. Power command masks include `PM_S2_COMMAND`, `PM_COLD_CONFIG`, `PM_WARM_CONFIG`, and method-1 variants. For MIPS, it declares `brcm_pm_do_s2(u32 *s2_params)`, `brcm_pm_do_s3(void __iomem *, int)`, and `s3_reentry`.

Control flow and integration: the header is included from `pm-mips.c`, `s2-mips.S`, and `s3-mips.S`, guaranteeing that C and assembly agree on register offsets and power-control bit encodings.

State and persistence: no state is owned here, but the constants define persistent side effects in AON SRAM/control registers and DDR PHY/timer blocks.

Dependencies and risks: depends on architecture-specific prototypes under `CONFIG_MIPS` and alternate declarations for non-MIPS assembly interfaces. Risks are ABI drift between the C callers and assembly helpers, especially if bit masks or offsets change without synchronized hardware validation.

Test signals: build coverage for both assembler and C inclusion, suspend/resume validation for every PM bit pattern, and power-off/warm-boot behavior matching AON register writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/pm/pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/pm/s2-mips.S -->
# sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/pm/s2-mips.S

Purpose: low-level MIPS assembly standby implementation for Broadcom STB S2. It executes with careful cache and interrupt handling while the CPU and PLLs enter and leave standby.

Important APIs and symbols: exports `LEAF(brcm_pm_do_s2)`, taking a `u32` parameter array with AON control base, DDR PHY base, timer base, I-cache line size, restart vector address, and restart vector size. It uses PM and timer constants from `pm.h`.

Control flow: the function saves callee-saved registers, loads arguments, locks its own code and the warm restart vector into I-cache, writes `PM_S2_COMMAND` to AON PM control, enables CP0 interrupt 2, waits, polls DDR PHY PLL status, delays roughly 1 ms with TIMER1, signals power-back-up through `AON_CTRL_HOST_MISC_CMDS`, clears PM control, unlocks I-cache lines, restores CP0 status and saved registers, then returns 0.

State and persistence: saves only CPU registers and CP0 status on the stack. Hardware state is changed in AON PM control, host misc command, DDR PHY polling, and timer registers. I-cache lock/unlock is transient but critical while memory/power state is unstable.

Dependencies and integration: called by `brcmstb_pm_s2()` after C code redirects vectors and prepares hardware. Depends on BMIPS CP0 interrupt behavior, valid KSEG/MMIO addresses in 32-bit arguments, and the warm restart vector being present.

Risks and test signals: risks include incorrect cache line size, bad restart vector length, missed PLL-ready polling, and timer frequency assumptions in the fixed delay. Test signals are repeated S2 standby/resume cycles, interrupt wake behavior, cache coherency after return, and absence of hangs in PLL polling or timer wait loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/pm/s2-mips.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/pm/s3-mips.S -->
# sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/pm/s3-mips.S

Purpose: low-level MIPS deep standby helper for Broadcom STB S3. It saves enough CPU state to survive power-down, triggers warm deep standby, and provides the `s3_reentry` resume label written into AON SRAM by C code.

Important APIs and symbols: exports `brcm_pm_do_s3(aon_ctrl_base, dcache_linesz)` and global `s3_reentry`. It uses global `gp_regs` from `pm-mips.c` to save return address, callee-saved registers, GP/SP/FP, and CP0 status.

Control flow: entry saves GPRs and CP0 status, writes back the `gp_regs` cacheline, programs `PM_WARM_CONFIG` then `PM_WARM_CONFIG | PM_PWR_DOWN`, enables CP0 interrupt 2, and waits. Resume jumps to `s3_reentry`, clears branch prediction structures, resets selected MMU registers, calls `plat_wired_tlb_setup`, restores saved GPRs and CP0 status, and returns to the C caller.

State and persistence: uses `gp_regs` as the cross-standby state carrier and relies on C code to preserve broader CP0 and MEMC state. AON PM control is the hardware persistence point for standby entry, while AON SRAM contains the reentry address.

Dependencies and integration: tightly coupled to `brcmstb_pm_s3()`, `pm.h`, BMIPS CP0 register semantics, `BMIPS_WARM_RESTART_VEC`, and `plat_wired_tlb_setup`. It assumes the saved register block is flushed before caches or memory become unavailable.

Risks and test signals: risks include incomplete register save set, cache writeback failure, wrong TLB defaults, and reentry address mismatch. Test signals are successful `PM_SUSPEND_MEM` wake, restored kernel execution context, stable TLB/cache behavior after wake, and no branch predictor or CP0 status related faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/pm/s3-mips.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/canaan/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/canaan/Kconfig

Purpose: Kconfig entry for the Canaan Kendryte K210 system controller driver.

Important configuration: `SOC_K210_SYSCTL` is a boolean option depending on `RISCV`, `SOC_CANAAN_K210`, `OF`, and `COMMON_CLK_K210`; it defaults to `SOC_CANAAN_K210` and selects `PM` and `MFD_SYSCON`.

Control flow and integration: enabling this option builds the K210 system controller driver that performs early clock setup and populates sysctl child devices. The `COMMON_CLK_K210` dependency is essential because the C file calls `k210_clk_early_init()`.

State and persistence: no runtime state is defined in Kconfig; it gates build-time inclusion and selected framework dependencies.

Risks and test signals: risks are underselecting dependencies for early clock/syscon use or enabling the driver without OF. Test signals are Kconfig satisfiability for K210 RISC-V defconfigs and no missing symbol link errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/canaan/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/canaan/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/canaan/Makefile

Purpose: Kbuild file for Canaan SoC drivers.

Important build behavior: `obj-$(CONFIG_SOC_K210_SYSCTL) += k210-sysctl.o` compiles the K210 system controller only when the matching Kconfig option is enabled.

Control flow and integration: this Makefile connects the Canaan SoC directory to the K210 sysctl driver. Runtime behavior is entirely in `k210-sysctl.c`.

State and persistence: no runtime state.

Risks and test signals: risk is limited to object selection drift. Test signals are successful K210 builds and absence of the object when the option is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/canaan/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/canaan/k210-sysctl.c -->
# sources/distributed-fs/ceph-client/drivers/soc/canaan/k210-sysctl.c

Purpose: Canaan Kendryte K210 system controller driver and early SoC clock initializer. It enables the sysctl bus clock during platform probe and populates child devices, while very early init maps the sysctl block to initialize PLL1/SRAM-capable clocks.

Important APIs and functions: `k210_sysctl_probe()` gets and enables the bus clock with devm clock APIs and calls `devm_of_platform_populate()`. `builtin_platform_driver(k210_sysctl_driver)` registers the OF platform driver for `canaan,k210-sysctl`. `k210_soc_early_init()` is registered via `SOC_EARLY_INIT_DECLARE()` for `canaan,kendryte-k210` and calls `k210_clk_early_init()` on a temporary mapping of fixed physical sysctl registers.

Control flow: the early init path uses the hard-coded K210 sysctl base before normal device model probing because PLL1 must be enabled before all SRAM can be used. Later, normal probe logs the controller, enables the clock, and creates child platform devices.

State and persistence: no private persistent struct is stored. Persistent side effects are clock controller state and child device creation. The early MMIO mapping is unmapped before return.

Dependencies and integration: depends on RISC-V SoC early init, OF platform population, common clock K210 support, and `soc/canaan/k210-sysctl.h`. It integrates parent sysctl with child clock/reset/syscon-like devices.

Risks and test signals: risks include hard-coded physical address mismatch, missing bus clock, and child population failure after the bus clock is enabled. Test signals are boot on K210 with full SRAM usable, `K210 system controller` probe log, child devices appearing, and no clock enable or ioremap panic failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/canaan/k210-sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/cirrus/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/cirrus/Kconfig

Purpose: Kconfig entry for Cirrus Logic EP93xx SoC support.

Important configuration: under `ARCH_EP93XX`, `EP93XX_SOC` defaults to yes and selects `SOC_BUS` and `AUXILIARY_BUS`. Help text describes locked syscon register access and auxiliary devices for reset, pinctrl, and clock functionality.

Control flow and integration: this option enables `soc-ep93xx.o`, which registers SoC metadata and auxiliary devices backed by syscon/regmap access.

State and persistence: build-time only.

Risks and test signals: risks are missing framework selects for auxiliary devices or SoC bus registration. Test signals are EP93xx defconfig coverage and build/link success with auxiliary bus enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/cirrus/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/cirrus/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/cirrus/Makefile

Purpose: Kbuild file for Cirrus SoC support.

Important build behavior: `obj-y += soc-ep93xx.o` always builds the EP93xx SoC driver when the directory is selected by architecture/Kconfig.

Control flow and integration: it relies on parent Kconfig scoping, so the object is included for EP93xx builds without a per-option object expression.

State and persistence: no runtime state.

Risks and test signals: risk is accidental inclusion outside intended architecture if directory selection changes. Test signals are EP93xx build success and absence of missing auxiliary/regmap symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/cirrus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/cirrus/soc-ep93xx.c -->
# sources/distributed-fs/ceph-client/drivers/soc/cirrus/soc-ep93xx.c

Purpose: Cirrus EP93xx syscon-backed SoC driver. It registers SoC bus metadata and creates auxiliary child devices for pinctrl, clock, and reset controllers that need coordinated writes through software-locked system controller registers.

Important APIs and functions: `ep93xx_syscon_probe()` is used by `builtin_platform_driver_probe()`. `ep93xx_regmap_write()` and `ep93xx_regmap_update_bits()` wrap locked writes by writing `EP93XX_SWLOCK_MAGICK` before the target register update under a spinlock. `ep93xx_adev_alloc()`, `ep93xx_controller_register()`, and `ep93xx_unregister_adev()` allocate, add, and devm-clean auxiliary devices. `ep93xx_soc_revision()` and `ep93xx_get_soc_rev()` convert syscon revision bits to SoC metadata.

Control flow: probe obtains match-data model, gets a regmap from the syscon node, maps the resource, allocates `soc_device_attribute`, reads revision, registers the SoC device, then creates model-specific pinctrl, revision-specific clock, and reset auxiliary devices. It logs errors for child registration failures but returns success after attempting all children.

State and persistence: `ep93xx_map_info` holds the regmap, raw base, and shared spinlock passed to child devices. The registered `soc_device` and auxiliary devices persist for runtime consumers.

Dependencies and integration: depends on OF compatible strings for EP9301/9302/9307/9312/9315, MFD syscon regmap, `linux/soc/cirrus/ep93xx.h`, auxiliary bus, and SoC bus. Child drivers consume `struct ep93xx_regmap_adev` operations.

Risks and test signals: risks include swlock ordering bugs, child device lifetime errors, and model-to-pinctrl mapping mismatches. Test signals include SoC sysfs revision, auxiliary devices binding to pinctrl/clk/reset drivers, safe locked register writes under concurrent users, and E2 SSP clock variant selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/cirrus/soc-ep93xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/dove/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/dove/Makefile

Purpose: Kbuild file for Marvell Dove SoC support.

Important build behavior: `obj-y += pmu.o` builds the Dove PMU driver whenever the Dove SoC directory is selected.

Control flow and integration: runtime power-domain, reset, and IRQ-controller behavior lives in `pmu.c`.

State and persistence: no runtime state.

Risks and test signals: risk is object inclusion outside intended machine scope if parent selection changes. Test signals are build success for Dove platforms and successful link with PM domain/reset/IRQ dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/dove/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/dove/pmu.c -->
# sources/distributed-fs/ceph-client/drivers/soc/dove/pmu.c

Purpose: Marvell Dove PMU support for power domains, optional reset controller, and a chained PMU interrupt controller. It supports both legacy platform initialization and device-tree based initialization.

Important APIs and functions: reset ops `pmu_reset_reset()`, `pmu_reset_assert()`, and `pmu_reset_deassert()` manipulate `PMC_SW_RST`. `pmu_domain_power_on()` and `pmu_domain_power_off()` implement generic PM domain transitions using `PMU_PWR`, `PMU_ISO`, and reset masks. `dove_init_pmu_irq()` creates a linear IRQ domain and generic chip. `dove_init_pmu_legacy()` consumes board-provided initdata, while `dove_init_pmu()` parses `marvell,dove-pmu` and `domains` OF children.

Control flow: initialization maps PMU/PMC bases, registers reset support if configured, creates each power domain, parses reset references to derive reset masks, then optionally installs the chained interrupt handler. Power-off enables isolation, asserts reset, and sets power-down bits; power-on clears power-down, releases reset, and disables isolation.

State and persistence: `struct pmu_data` persists MMIO bases, lock, irq domain/generic chip, and reset controller state. Each `struct pmu_domain` stores masks and generic PM domain state. Hardware PMU/PMC registers persist the actual power/reset/isolation state.

Dependencies and integration: integrates with reset controller framework, generic PM domains, OF power-domain providers, IRQ domains/generic chips, and platform-specific `linux/soc/dove/pmu.h` legacy data.

Risks and test signals: risks include the documented non-race-free PMU IRQ clear register, leaking allocated domains on partial failure, and misparsed reset phandles when reset support is disabled. Test signals are power-domain attach/detach behavior, reset assertions, interrupt delivery through child IRQs, and legacy and DT boot coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/dove/pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/Kconfig

Purpose: top-level Kconfig menu for NXP/Freescale QorIQ SoC drivers.

Important configuration: includes submenus for DPAA1 QBMan and QUICC Engine. `FSL_GUTS` selects `SOC_BUS` and supports global utility block SoC identification. `FSL_MC_DPIO` is a tristate depending on `FSL_MC_BUS` and `NET`, selecting `SOC_BUS`, `FSL_GUTS`, and `DIMLIB`. `DPAA2_CONSOLE` exposes MC/AIOP firmware logs. `FSL_RCPM` gates ARM/ARM64 sleep wakeup control.

Control flow and integration: these options determine whether SoC identity, DPAA1 BMan/QMan, DPAA2 DPIO service, firmware console, and RCPM code are compiled.

State and persistence: build-time selection only.

Risks and test signals: risks are dependency gaps between DPAA2 service APIs and networking/MC bus requirements. Test signals are config coverage for Layerscape, COMPILE_TEST, and absence of missing symbols for DIMLIB or FSL_GUTS consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/Makefile

Purpose: Kbuild routing for Freescale/NXP SoC driver subdirectories and objects.

Important build behavior: DPAA builds `qbman/`, QUICC/CPM build `qe/`, and individual options add `rcpm.o`, `guts.o`, `dpio/`, and `dpaa2-console.o`.

Control flow and integration: it maps the Kconfig feature set to concrete object directories, keeping DPAA1 and DPAA2 components separate.

State and persistence: no runtime state.

Risks and test signals: risks are object selection drift or whitespace-sensitive Kbuild mistakes. Test signals are enabled options producing expected objects and disabled options not exporting unwanted APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/dpaa2-console.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/dpaa2-console.c

Purpose: DPAA2 firmware console driver. It exposes Management Complex and AIOP circular firmware log buffers as misc character devices `/dev/dpaa2_mc_console` and `/dev/dpaa2_aiop_console`.

Important APIs and functions: `dpaa2_console_probe()` records the MC firmware base-address register resource and registers both misc devices. `get_mc_fw_base_address()` maps MC base registers and reconstructs the firmware base address. `dpaa2_generic_console_open()` maps a log buffer, validates magic, computes start/end/current pointers, and handles wraparound. `dpaa2_console_read()` copies log bytes from IO memory to userspace, including circular wrap handling. `dpaa2_console_remove()` deregisters devices.

Control flow: probe only prepares global resource and device nodes. Each open maps the firmware log buffer based on current MC base address, verifies header fields, and initializes per-file `console_data`. Reads refresh `last_byte`, limit to requested count, copy in one or two segments, and advance `cur_ptr`; close unmaps and frees.

State and persistence: global `mc_base_addr` stores the base register resource. Per-open `console_data` stores MMIO mapping and read cursor, so each file descriptor has independent read position. Firmware log memory is external persistent state owned by MC/AIOP firmware.

Dependencies and integration: depends on OF resource translation, miscdevice, IO mapping, firmware log header layout, and userspace reads through char devices.

Risks and test signals: risks include trusting firmware-provided `buf_start`/`buf_length`, large per-read `kmalloc(count)`, races with firmware updating circular buffer, and mapping failure when MC base registers are unavailable. Test signals are correct misc devices, magic validation, wraparound reads, EOF behavior when `cur_ptr == end_of_data`, and clean unload/reprobe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/dpaa2-console.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/Makefile

Purpose: Kbuild file for the DPAA2 DPIO driver and service layer.

Important build behavior: `fsl-mc-dpio-y` links `dpio.o`, `qbman-portal.o`, `dpio-service.o`, and `dpio-driver.o`; `obj-$(CONFIG_FSL_MC_DPIO)` builds the module or built-in object.

Control flow and integration: this object grouping combines MC command wrappers, software portal mechanics, exported DPAA2 IO service APIs, and fsl-mc bus probing into one driver.

State and persistence: no direct runtime state.

Risks and test signals: risk is missing one component from the composite object, producing unresolved service or portal symbols. Test signals are build/link success and exported `dpaa2_io_*` APIs present when `CONFIG_FSL_MC_DPIO` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/dpio-cmd.h -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/dpio-cmd.h

Purpose: DPAA2 Management Complex wire command definitions for DPIO objects.

Important APIs/types/macros: defines DPIO API version 4.2, command ID encoding through `DPIO_CMD()`, command IDs for open/close/enable/disable/get-attr/reset/stashing-destination/API-version, and packed command/response parameter layouts `dpio_cmd_open`, `dpio_rsp_get_attr`, and `dpio_stashing_dest`.

Control flow and integration: included by `dpio.c` and `dpio-driver.c` so MC commands are encoded consistently. The response layout maps MC words to `struct dpio_attr` fields in host endian form.

State and persistence: no state; it defines the serialized command ABI between kernel and MC firmware.

Dependencies and risks: depends on `linux/fsl/mc.h` command header conventions and little-endian MC fields. Risks are ABI drift from MC firmware or incorrect field sizes/masks, especially `DPIO_CHANNEL_MODE_MASK` and portal offset fields.

Test signals: successful `dpio_get_api_version()`, `dpio_get_attributes()` returning sane portal offsets/version/clock, and MC command failures when IDs or versioning mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/dpio-cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/dpio-driver.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/dpio-driver.c

Purpose: fsl-mc bus driver for DPAA2 DPIO objects. It opens MC control sessions, configures the DPIO, maps software portal regions, creates a `dpaa2_io` service object, and wires interrupts to the service ISR.

Important APIs and functions: `dpaa2_dpio_probe()` performs object setup; `dpaa2_dpio_remove()` tears it down. `dpaa2_dpio_get_cluster_sdest()` derives stashing destination from SoC family. `register_dpio_irq_handlers()` requests the IRQ and sets affinity hint; `dpio_driver_init()` allocates `cpus_unused_mask` and registers the fsl-mc driver.

Control flow: probe allocates a private struct, allocates an MC portal, opens and resets the DPIO, reads attributes, enables it, assigns the next unused CPU, optionally sets stashing destination, maps CENA/CINH regions with classic or DDR-backed portal behavior, allocates MC IRQs, creates `dpaa2_io`, registers IRQ, logs success, and closes the MC session. Error paths unwind in reverse order. Remove stops the service, frees IRQs, returns CPU to the unused mask, opens/disables/closes the DPIO, and frees the MC portal.

State and persistence: `cpus_unused_mask` tracks CPU assignment. Per-device `dpio_priv` stores the `dpaa2_io` service. The DPIO object state persists in MC firmware/hardware across command calls.

Dependencies and integration: depends on fsl-mc bus, DPIO MC command wrappers, SoC bus matching for stashing, DPIO portal regions, IRQ allocation, and `dpaa2_io_create()` from the service layer.

Risks and test signals: risks include CPU/DPIO count mismatch, region_count assumptions, stashing destination unknown SoC handling, and possible unwind ordering around `dpaa2_io_create()` versus IRQ free. Test signals are DPIO probe logs, CPU affinity hints, MC command success, functional DPAA2 network drivers using service APIs, and clean hot-unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/dpio-driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/dpio-service.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/dpio-service.c

Purpose: exported DPAA2 IO service layer built on QBMan software portals. It selects per-CPU or round-robin DPIO services and exposes notification, enqueue, dequeue, buffer pool, query, and IRQ coalescing APIs to DPAA2 object drivers.

Important APIs and functions: creation/destruction through `dpaa2_io_create()` and `dpaa2_io_down()`. Selection through `dpaa2_io_service_select()`. IRQ dispatch through `dpaa2_io_irq()`. Notification APIs include `dpaa2_io_service_register()`, `dpaa2_io_service_deregister()`, and `dpaa2_io_service_rearm()`. Data APIs include pull, enqueue single/multiple, release/acquire, store create/destroy/next, FQ/BP count queries, IRQ coalescing, adaptive coalescing, and Net DIM update functions.

Control flow: DPIO creation initializes a `qbman_swp`, enables DQRR interrupts and optional push dequeue, inserts the object into global list/per-CPU array, and initializes DIM state. Service calls select a portal, build a QBMan descriptor, and call the relevant `qbman_swp_*` primitive. IRQ handling reads portal status, drains up to `DPAA_POLL_MAX` DQRR entries, invokes notification callbacks for SCNs, consumes entries, clears status, and uninhibits interrupts.

State and persistence: global `dpio_by_cpu[]`, `dpio_list`, and `dpio_list_lock` manage service selection. Each `dpaa2_io` owns a `qbman_swp`, notification list, management-command lock, notification lock, DIM counters, and device pointer. `dpaa2_io_store` owns DMA-mapped dequeue result memory.

Dependencies and integration: integrates with `soc/fsl/dpaa2-io.h`, MC DPIO driver, QBMan portal implementation, DMA mapping, device links, and networking DIMLIB.

Risks and test signals: risks include concurrency around round-robin service selection, missing `qbman_swp_finish()` in teardown, caller misuse of store polling, descriptor allocation fixed at 32 entries in multi-desc enqueue, and callbacks running in IRQ context. Test signals are DPAA2 Ethernet traffic, notification rearm correctness, DMA mapping checks, IRQ coalescing ethtool behavior, and stress with CPU affinity and hotplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/dpio-service.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/dpio.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/dpio.c

Purpose: low-level DPAA2 DPIO Management Complex command wrapper library.

Important APIs and functions: `dpio_open()` obtains an object token; `dpio_close()` releases it; `dpio_enable()`, `dpio_disable()`, and `dpio_reset()` send lifecycle commands; `dpio_get_attributes()` decodes portal offsets, portal ID, channel mode, priorities, QBMan version, and clock; `dpio_set_stashing_destination()` programs CPU cluster stashing; `dpio_get_api_version()` queries MC API version.

Control flow: each function builds `struct fsl_mc_command`, fills command header with `mc_encode_cmd_header()`, writes little-endian params where needed, calls `mc_send_command()`, and decodes response fields on success.

State and persistence: no local persistent state. Tokens returned by `dpio_open()` are used by callers as MC session state. Commands mutate DPIO object state in MC firmware/hardware.

Dependencies and integration: depends on `linux/fsl/mc.h`, `dpio.h`, and `dpio-cmd.h`. It is consumed primarily by `dpio-driver.c`.

Risks and test signals: risks include MC ABI field mismatch, endian errors, and callers using invalid tokens after close. Test signals are probe success through open/reset/get-attr/enable/close, API version matching expected 4.2, and failure handling from `mc_send_command()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/dpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/dpio.h -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/dpio.h

Purpose: public internal header for DPIO MC object control APIs and DPIO attribute/config types.

Important APIs/types: declares MC command wrappers from `dpio.c`; defines `enum dpio_channel_mode`, `struct dpio_cfg`, and `struct dpio_attr`. Attribute fields describe object ID, software portal CE/CI offsets, portal ID, notification mode/priorities, QBMan version, and clock frequency.

Control flow and integration: `dpio-driver.c` uses this header to open, reset, enable, inspect, and disable DPIO objects before creating a `dpaa2_io` service.

State and persistence: no state. Structs carry MC firmware state into driver setup.

Dependencies and risks: depends on `struct fsl_mc_io` from the MC bus. Risks are type drift with MC response structures and callers assuming notification priorities imply a valid local channel.

Test signals: build coverage for DPIO driver, valid decoded attributes during probe, and compile-time consistency with `dpio-cmd.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/dpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/qbman-portal.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/qbman-portal.c

Purpose: DPAA2 QBMan software portal implementation. It programs software portal registers and implements enqueue, volatile dequeue, DQRR consumption, buffer release/acquire, FQ/channel management, state queries, and interrupt coalescing for both direct and memory-backed portal modes.

Important APIs and functions: portal lifecycle `qbman_swp_init()`/`qbman_swp_finish()`; interrupt helpers; management command helpers `qbman_swp_mc_start()`, `qbman_swp_mc_submit()`, `qbman_swp_mc_result()`; descriptor builders for enqueue, pull, and release; function-pointer-selected implementations for direct versus memory-backed enqueue/pull/DQRR/release; management commands `qbman_swp_acquire()`, `qbman_swp_alt_fq_state()`, `qbman_swp_CDAN_set()`, `qbman_fq_query_state()`, and `qbman_bp_query()`.

Control flow: init allocates `qbman_swp`, computes SDQCR defaults, selects DQRR size and valid bits from QMan revision, programs SWP configuration, enables memory-backed mode for QMan rev >= 5.0, switches global function pointers to memory-backed implementations, initializes EQCR producer/consumer tracking, and sets initial coalescing. Runtime operations fill cache-enabled command slots, use valid-bit protocols and DMA barriers, and write cache-inhibited trigger registers when memory-backed mode requires read-trigger semantics.

State and persistence: each `qbman_swp` tracks MMIO bases, valid bits, SDQCR, VDQ availability/storage, DQRR next index, EQCR ring producer/consumer state, access spinlock, and coalescing settings. Global function pointers change process-wide after a rev >= 5 portal is initialized.

Dependencies and integration: depends on DPAA2 frame/dequeue layouts, relaxed MMIO, DMA barriers, portal mapping attributes from `dpio-driver.c`, and the service layer. It is hardware-facing and has no firmware fallback except management command response codes.

Risks and test signals: risks include global function pointer mutation if mixed portal revisions existed, valid-bit/ring wrap mistakes, incomplete locking on multi-desc direct paths, memory-backed DQRR prefetch using direct offset in one path, and timeout-only management completion. Test signals are high-rate enqueue/dequeue, buffer pool acquire/release, FQ/BP count queries, QMan rev 4.x and 5.x coverage, IRQ coalescing limits, and stress under concurrent service users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/qbman-portal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/qbman-portal.h -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/qbman-portal.h

Purpose: internal DPAA2 QBMan portal API and data-structure definitions shared between the portal implementation and DPIO service layer.

Important APIs/types: defines QMan revisions, `struct qbman_swp_desc`, interrupt masks, pull/enqueue/release descriptors, result type constants, FQ management verbs, `struct qbman_swp` portal state, function pointers for portal variants, and inline wrappers such as `qbman_swp_enqueue()`, `qbman_swp_pull()`, `qbman_swp_release()`, and `qbman_swp_dqrr_next()`. It also defines result classifiers for DQ, SCN, FQDAN, CDAN, CSCN, BPSCN, CGCU, retirement, and park notifications.

Control flow and integration: service code builds descriptors using these helpers and then calls variant-dispatched inline wrappers. The header also provides inline FQ/CDAN convenience functions that call management command implementations.

State and persistence: `struct qbman_swp` is the central persisted software representation of a hardware portal, including valid-bit state, ring cursors, interrupt coalescing, and adaptive coalescing state.

Dependencies and risks: depends on `soc/fsl/dpaa2-fd.h` layouts. Risks include exposing mutable portal internals across C files and relying on external function pointers that can be switched by `qbman_swp_init()`.

Test signals: compile-time consumers in `dpio-service.c`, correct result classification in notification IRQ paths, and successful portal operations through the inline wrapper indirection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/qbman-portal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/guts.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/guts.c

Purpose: Freescale/NXP QorIQ Global Utilities driver for SoC identification. It reads the System Version Register, matches known die families, optionally reads a unique SoC ID from SFP, and registers SoC bus metadata.

Important APIs and functions: `fsl_guts_init()` is a `core_initcall`; `fsl_soc_die_match()` maps SVR masks to die names; `fsl_guts_get_soc_uid()` maps an SFP node and reads a 64-bit UID. Tables include many PowerPC and Layerscape ARM-compatible GUTS/DCFG nodes plus LS1028A SFP data.

Control flow: init finds the first matching GUTS/DCFG node, maps it, reads SVR in little or big endian based on DT property, allocates `soc_device_attribute`, fills machine/family/soc_id/revision/serial_number, registers the SoC device, and logs machine/family/revision. Allocation failures unwind allocated strings.

State and persistence: persistent state is the registered SoC device. No long-lived MMIO mapping remains after reading SVR/UID.

Dependencies and integration: depends on OF, `struct ccsr_guts` layout, SoC bus, optional SFP compatible nodes, and callers such as DPIO stashing logic that use `soc_device_match()` on family strings.

Risks and test signals: risks include matching only the first GUTS node, endian property mistakes, SVR mask table gaps, and serial number allocation failure after otherwise valid metadata. Test signals are `/sys/devices/soc0` contents, boot logs, DPIO SoC matching, LS1028A serial number presence, and clean no-op on non-QorIQ systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/guts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/Kconfig

Purpose: Kconfig menu for DPAA1 QBMan support, including BMan/QMan framework and self-tests.

Important configuration: `FSL_DPAA` is a menuconfig depending on supported Freescale/Layerscape architectures with 64-bit DMA addresses and selects `GENERIC_ALLOCATOR`. It enables BMan and QMan infrastructure. Optional `FSL_DPAA_CHECKING` adds runtime API assertions. `FSL_BMAN_TEST` and `FSL_QMAN_TEST` build self-test modules; API and stash tests refine coverage.

Control flow and integration: these options gate compilation of BMan/QMan CCSR, portals, high-level APIs, shared DPAA helpers, and tests.

State and persistence: no runtime state; configuration controls object inclusion and assertion behavior.

Risks and test signals: risks include enabling DPAA without proper DMA address width or genalloc support. Test signals are DPAA platform builds, self-test module availability, and optional checking warnings during stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/Makefile

Purpose: Kbuild file for DPAA1 BMan/QMan framework objects and tests.

Important build behavior: `CONFIG_FSL_DPAA` builds `bman_ccsr.o`, `qman_ccsr.o`, `bman_portal.o`, `qman_portal.o`, `bman.o`, `qman.o`, and `dpaa_sys.o`. `CONFIG_FSL_BMAN_TEST` and `CONFIG_FSL_QMAN_TEST` build composite test modules with optional API/stash test objects.

Control flow and integration: the object list ensures low-level hardware setup, portal probing, API layers, and shared helpers are all linked together for DPAA1.

State and persistence: no runtime state.

Risks and test signals: risks are missing cross-object symbols if object lists drift. Test signals are build/link success for DPAA, BMan test module containing `bman_test_api.o` when configured, and QMan test variants matching Kconfig.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman.c

Purpose: DPAA1 BMan high-level portal and buffer-pool API. It implements per-CPU affine portals, release command ring handling, management-command acquire/query mechanics, portal IRQ handling, BPID allocation, and exported pool acquire/release functions.

Important APIs and functions: exported APIs include `bman_create_affine_portal()`, `bman_p_irqsource_add()`, `bm_shutdown_pool()`, `bman_new_pool()`, `bman_free_pool()`, `bman_get_bpid()`, `bman_release()`, `bman_acquire()`, and `bman_get_bm_portal_config()`. Internal subsystems include RCR helpers (`bm_rcr_init()`, `bm_rcr_start()`, `bm_rcr_pvb_commit()`), management command helpers (`bm_mc_start()`, `bm_mc_commit()`, `bm_mc_result_timeout()`), and portal setup `bman_create_portal()`.

Control flow: portal creation maps config addresses into `bm_portal`, initializes RCR and management command state, disables BSCN interrupts, clears stale interrupts, requests IRQ, sets affinity, verifies the RCR is clean, and enables interrupts. `bman_release()` waits for an RCR entry, fills buffers and BPID, commits with valid bit, and uses the affine portal for the current CPU. `bman_acquire()` issues an MC acquire command and copies returned buffers.

State and persistence: per-CPU `bman_affine_portal`, `affine_mask`, portal RCR/MC rings, IRQ source masks, and global `bm_bpalloc` persist. Hardware portal rings and BMan pools carry persistent buffer state.

Dependencies and integration: depends on `bman_priv.h`, `dpaa_sys.h`, DPAA cache helpers, genalloc BPID pool from `bman_ccsr.c`, and portal configs from `bman_portal.c`.

Risks and test signals: risks include CPU-affine assumptions, local IRQ/preemption interactions around `get_cpu_var()`, RCR timeout under pressure, copying `num` buffers instead of returned count in acquire callers, and cleanup loops on kexec. Test signals are BMan self-test pass, buffer pool leak cleanup, IRQ affinity behavior, and stress release/acquire across CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman_ccsr.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman_ccsr.c

Purpose: DPAA1 BMan CCSR hardware initialization and error interrupt handling. It maps the global BMan block, detects revision, configures private FBPR memory, seeds BPID allocation, and exposes probe/cleanup status to portal code.

Important APIs and functions: global `bman_ip_rev` is exported. `fsl_bman_probe()` is the built-in platform probe. `bm_set_memory()` programs FBPR base/size or detects preconfigured memory after kexec. `bman_isr()` reports hardware errors and disables one-shot low-watermark interrupts. `bman_is_probed()`, `bman_requires_cleanup()`, and `bman_done_cleanup()` coordinate portal probing and kexec cleanup.

Control flow: probe maps CCSR, reads IP revision, initializes reserved private memory through `qbman_init_private_mem()`, writes FBPR registers, installs shared error IRQ, disables BSCN error interrupt, clears stale errors, enables error interrupts, creates `bm_bpalloc`, seeds BPID range, and marks BMan probed.

State and persistence: persistent globals include `bm_ccsr_start`, `bman_ip_rev`, probe and cleanup flags, `fbpr_a/fbpr_sz`, and `bm_bpalloc`. Hardware FBPR register contents can persist across kexec and are treated specially.

Dependencies and integration: depends on OF platform resources, reserved memory helper in `dpaa_sys.c`, genalloc, BMan portal cleanup in `bman_portal.c`, and `bman.c` BPID allocation.

Risks and test signals: risks include inability to change FBPR base after prior firmware/kernel setup, revision table gaps, error IRQ flood except disabled FLWI, and private memory without `struct page` DMA mapping. Test signals are BMan probe success, BPID pool size matching revision, error interrupt logs, kexec cleanup path, and `bman_is_probed()` unblocking portals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman_ccsr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman_portal.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman_portal.c

Purpose: DPAA1 BMan portal platform driver. It maps CE/CI portal regions, assigns portals to CPUs, initializes affine BMan portals, handles CPU hotplug IRQ affinity changes, and performs kexec cleanup when needed.

Important APIs and functions: `bman_portal_probe()` performs platform probing; `init_pcfg()` calls `bman_create_affine_portal()` and enables RCR interrupt source; `bman_online_cpu()` and `bman_offline_cpu()` move IRQ affinity; `bman_portals_probed()` exports portal probe status; `bman_portal_driver_register()` registers platform driver and CPU hotplug callbacks.

Control flow: probe defers until BMan CCSR is probed, allocates portal config, obtains CE/CI resources and IRQ, maps CE with `memremap()` and CI with `ioremap()`, assigns the first unused CPU under `bman_lock`, initializes the portal when assigned, adjusts affinity if CPU is offline, and, once all portals are considered probed, drains all pools if BMan required cleanup.

State and persistence: `affine_bportals[NR_CPUS]`, `portal_cpus`, `__bman_portals_probed`, and per-config mappings persist. Hardware portal rings persist in mapped CE/CI regions.

Dependencies and integration: depends on `bman_is_probed()` from CCSR, `bman_create_affine_portal()` from API layer, DPAA portal resource ordering, CPU hotplug, and IRQ affinity support.

Risks and test signals: risks include `__bman_portals_probed` set when CPU slots are exhausted rather than when all device-tree portals are seen, cleanup depending on a usable affine portal, and no full remove path. Test signals are portal probe logs per CPU, IRQ affinity changes across CPU online/offline, successful pool shutdown after kexec, and DPAA buffer operations on every assigned CPU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman_portal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman_priv.h -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman_priv.h

Purpose: private BMan header connecting CCSR, portal, and high-level BMan API implementation files.

Important APIs/types/macros: defines portal interrupt source `BM_PIRQ_RCRI`, BMan revision constants, external `bman_ip_rev` and `bm_bpalloc`, `struct bm_portal_config`, `bman_create_affine_portal()`, `bman_p_irqsource_add()`, visible IRQ mask, `bman_get_bm_portal_config()`, cleanup status functions, and `bm_shutdown_pool()`.

Control flow and integration: included by `bman.c`, `bman_ccsr.c`, `bman_portal.c`, and tests so they share portal configuration, revision state, and cleanup contracts.

State and persistence: declares externally-owned persistent state rather than owning it. `bm_portal_config` carries mapped CE/CI addresses, device, CPU, and IRQ for each portal.

Dependencies and risks: depends on `dpaa_sys.h` and public `soc/fsl/bman.h`. Risks include tight coupling among implementation files and exported globals that require initialization ordering discipline.

Test signals: compile-time consistency across BMan objects, portal probe calling API functions correctly, and tests seeing revision constants through the private include path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman_test.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman_test.c

Purpose: BMan self-test module entry point. It invokes configured BMan API tests at module initialization.

Important APIs and functions: `test_init()` conditionally calls `bman_test_api()` when `CONFIG_FSL_BMAN_TEST_API` is enabled. `test_exit()` is empty. The file declares module metadata and uses `module_init()`/`module_exit()`.

Control flow: loading the test module runs the API test once through a one-iteration loop. There is no runtime service after init.

State and persistence: no state is owned here beyond module lifetime. The called test allocates and frees BMan pool resources.

Dependencies and integration: depends on `bman_test.h` and optional `bman_test_api.c` linkage controlled by Kbuild.

Risks and test signals: risks include running destructive hardware API tests on systems where BMan is shared with active users. Test signals are module load logs from `bman_test_api()`, warning-free completion, and clean module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman_test.h -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman_test.h

Purpose: private header for BMan self-test code.

Important APIs: includes `bman_priv.h`, sets `pr_fmt`, and declares `void bman_test_api(void)`.

Control flow and integration: shared by the test module entry and API test implementation so `bman_test.c` can call the optional API test.

State and persistence: no state.

Risks and test signals: risk is test code depending on private implementation details through `bman_priv.h`. Test signals are successful test module build with and without API test object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman_test_api.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman_test_api.c

Purpose: high-level BMan API self-test. It allocates a pool, releases synthetic buffers, reacquires them, and verifies that every released token is returned exactly once.

Important APIs and functions: `bman_test_api()` drives the test. `bufs_init()` initializes 93 synthetic buffer addresses. `bufs_cmp()` handles BMan revision 2.x 40-bit address masking. `bufs_confirm()` checks one-to-one matching between input and output arrays.

Control flow: the test creates a BMan pool, repeats three loops of releasing buffers in batches up to 8, acquiring them back in reverse output slots, checking empty-pool behavior, and confirming token equality. It frees the pool on success and warns on failure paths.

State and persistence: static `pool`, `bufs_in`, `bufs_out`, and `bufs_received` are module-global test state. The BMan pool is hardware/global state during test and is freed afterward.

Dependencies and integration: depends on public BMan APIs, private `bman_ip_rev` revision information, and the BMan portal infrastructure being initialized on the executing CPU.

Risks and test signals: risks include synthetic addresses colliding with revision-specific masking, running on a CPU without an affine portal, and leaving a pool allocated on failure. Test signals are start/finish logs, no WARNs from buffer match counts or acquire counts, and no pool leaks after module load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman_test_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/dpaa_sys.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/dpaa_sys.c

Purpose: shared DPAA helper for initializing QBMan private reserved memory. It locates a reserved-memory node, returns base/size, and patches a missing `reg` property so kexec preserves the same memory placement.

Important APIs and functions: `qbman_init_private_mem(struct device *dev, int idx, const char *compat, dma_addr_t *addr, size_t *size)` first checks the device's `memory-region` phandle at `idx`, then falls back to a compatible search, then calls `of_reserved_mem_lookup()`.

Control flow: after finding reserved memory, it writes base and size to outputs. If the node lacks `reg`, it devm-allocates a `struct property`, four big-endian cells for 64-bit base/size, a `reg` name string, and adds the property to the live OF tree with `of_add_property()`.

State and persistence: no module-global state. It mutates the live device tree by adding `reg` when absent; that mutation persists for the running kernel and supports kexec address preservation.

Dependencies and integration: used by BMan CCSR and likely QMan CCSR. Depends on OF reserved memory, dynamic OF property modification, and device-managed allocation.

Risks and test signals: risks include fallback compatible finding the wrong node, adding properties to immutable or unexpected live tree state, and the DMA API caveat that memory is not backed by `struct page`. Test signals are BMan/QMan private memory base/size logs, kexec retaining FBPR/FQD/PFDR regions, and no `of_add_property()` failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/dpaa_sys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/dpaa_sys.h -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/dpaa_sys.h

Purpose: shared DPAA1 system helper header. It provides cache maintenance wrappers, ring helpers, portal resource constants, assertion behavior, private-memory init prototype, memremap policy, and IRQ affinity helper.

Important APIs/macros: `DPAA_PORTAL_CE` and `DPAA_PORTAL_CI` index portal resources. `dpaa_flush()`, `dpaa_invalidate()`, `dpaa_zero()`, `dpaa_touch_ro()`, and `dpaa_invalidate_touch_ro()` abstract cache operations. `DPAA_ASSERT()` becomes `WARN_ON()` under checking. `dpaa_cyc_diff()` computes cyclic ring distance. `DPAA_GENALLOC_OFF` avoids genalloc zero ambiguity. `QBMAN_MEMREMAP_ATTR` selects WB on PPC and WC elsewhere. `dpaa_set_portal_irq_affinity()` validates and sets IRQ affinity.

Control flow and integration: BMan and QMan portal code use these helpers for ring cache handling, portal mapping, BPID/FQID allocation, and CPU affinity.

State and persistence: no persistent state. Inline helpers perform immediate cache or IRQ operations.

Dependencies and risks: depends on architecture cacheflush support, prefetch, genalloc, platform devices, OF reserved memory, and IRQ affinity APIs. Risks include architecture-specific cache assumptions, especially PPC-only flush behavior and ARM non-cacheable mapping assumptions.

Test signals: portal rings operate without stale cache data, checking builds produce warnings for invalid API state, portal IRQs affined to expected CPUs, and memremap attributes matching platform coherency requirements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/dpaa_sys.h -->
