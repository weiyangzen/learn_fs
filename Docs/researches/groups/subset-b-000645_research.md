# subset-b-000645 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/pm.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-at91/pm.c

Purpose: implements AT91/Microchip suspend, standby, ultra-low-power, backup, and cpuidle integration for several AT91 families. It owns global `soc_pm` state, maps PMC/RAMC/SHDWC/SFRBU/DDR PHY resources from device tree, copies the final suspend trampoline into SRAM, and installs `platform_suspend_ops`.

Important APIs/types/functions: defines `struct at91_pm_bu`, `struct at91_pm_sfrbu_regs`, Ethernet quirk structures, `struct at91_soc_pm`, wake-source tables, and `pm_modes`. Exported API is `at91_suspend_entering_slow_clock()`. Init entry points include `at91rm9200_pm_init()`, `at91sam9_pm_init()`, `sam9x60_pm_init()`, `sam9x7_pm_init()`, `sama5_pm_init()`, `sama5d2_pm_init()`, and `sama7_pm_init()`. Core paths are `at91_pm_begin()`, `at91_pm_enter()`, `at91_suspend_finish()`, `at91_pm_modes_init()`, `at91_dt_ramc()`, `at91_pm_sram_init()`, and `at91_pm_backup_init()`.

Control flow: early parameter `atmel.pm_modes=` selects standby/suspend modes. The SoC-specific init validates supported modes, maps RAM controller and optional PM controllers, sets wake-source callbacks, and registers suspend ops only after SRAM code is copied. Suspend begins by selecting `soc_pm.data.mode`, programming ULP1 wake sources, and marking backup state. Enter checks Ethernet quirks and slow-clock safety, calls the SRAM suspend routine directly or through `cpu_suspend()` for backup, then restores outer cache and wake-source programming.

State and persistence: persistent state lives in global `soc_pm`, mapped controller pointers, Ethernet device/node references, SRAM function pointer `at91_suspend_sram_fn`, and secure RAM backup structure `soc_pm.bu`. Backup mode stores a canary, resume physical address, DDR PHY calibration, and the first memory words that may be corrupted by recalibration.

Dependencies and integration: depends on ARM suspend/cache APIs, genalloc SRAM pools, OF platform lookup, Atmel PMC/RAMC register definitions, SMCCC secure calls via `sam_secure`, clock framework, wakeup-source accounting, and platform cpuidle. Device tree compatibility strings choose RAMC, PMC, wake sources, Ethernet clocks, SHDWC, SFRBU, secure SRAM, and DDR PHY.

Risks: this code writes raw power, clock, and memory-controller registers while RAM may be in self-refresh, so ordering, cache flushes, and SRAM copy correctness are critical. Missing DT nodes silently downgrade requested modes in some cases, while backup mode can fail without secure RAM or DDR PHY mapping. Ethernet WoL quirks deliberately disable clocks or block suspend, so regressions can either lose wake capability or hang affected MACs. The secure PM fallback path relies on firmware return values and mode indexes matching `pm_modes`.

Test signals: boot on each supported SoC with `CONFIG_ATMEL_PM`, suspend/resume for `standby`, `ulp0`, `ulp0-fast`, `ulp1`, and `backup` where supported, `atmel.pm_modes=` parsing, WoL-only and mixed wake-source cases, missing-controller DT fallback, secure PM firmware paths, and repeated backup resume preserving DDR contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/pm.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-at91/pm.h

Purpose: declares the AT91 PM data contract shared between C setup code and the SRAM assembly suspend routine.

Important APIs/types/functions: defines memory-controller IDs `AT91_MEMCTRL_MC`, `AT91_MEMCTRL_SDRAMC`, and `AT91_MEMCTRL_DDRSDR`; suspend mode constants `AT91_PM_STANDBY`, `AT91_PM_ULP0`, `AT91_PM_ULP0_FAST`, `AT91_PM_ULP1`, and `AT91_PM_BACKUP`; and `struct at91_pm_data` with controller bases, PMC metadata, mode, memory-controller type, and masks.

Control flow: C code fills `struct at91_pm_data` during SoC-specific PM init and passes it to `at91_pm_suspend_in_sram()`. Assembly uses generated offsets from `pm_data-offsets.c` to read the same structure without C layout assumptions.

State and persistence: no executable state; the structure carries persistent mapped I/O addresses and selected mode across the final suspend transition.

Dependencies and integration: included by `pm.c`, `pm_suspend.S`, and the offset generator. It couples ARM C code with assembly layout and Atmel PMC/RAMC register conventions.

Risks: field order and type changes require regenerating assembly offsets; mode constants are array indexes into PM mode maps, so renumbering would break validation and fallback logic.

Test signals: build-time offset generation, successful assembly build, and suspend smoke tests for all memory-controller families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/pm_data-offsets.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-at91/pm_data-offsets.c

Purpose: emits assembler constants for fields inside `struct at91_pm_data`.

Important APIs/types/functions: `main()` uses `DEFINE()` and `OFFSET()` for `PM_DATA_PMC`, `PM_DATA_RAMC0`, `PM_DATA_RAMC1`, `PM_DATA_RAMC_PHY`, `PM_DATA_MEMCTRL`, `PM_DATA_MODE`, `PM_DATA_PMC_MCKR_OFFSET`, `PM_DATA_PMC_VERSION`, `PM_DATA_PMC_MCKS`, `PM_DATA_PMC_MCKR`, `PM_DATA_PMC_PLLA`, `PM_DATA_PMC_MCKR_CSS`, `PM_DATA_PMC_MCKR_PRES`, `PM_DATA_PMC_MCKR_MDIV`, `PM_DATA_PMC_MCKR_CSS_OFFSET`, and `PM_DATA_PMC_MCKR_PRES_OFFSET`.

Control flow: compiled as a kernel offsets helper, not as runtime code. The generated constants are consumed by `pm_suspend.S`.

State and persistence: no runtime state. Its only persistent output is generated assembly offset metadata during the build.

Dependencies and integration: includes `pm.h` and `asm-offsets.h`; any `struct at91_pm_data` layout change is reflected here for assembly users.

Risks: missing offsets cause assembly to use stale or hardcoded layout assumptions. Incorrect type widths in `pm.h` would surface as broken suspend behavior rather than a normal C type error inside the assembly path.

Test signals: successful kernel build and inspection of generated offsets; suspend tests catch semantic mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/pm_data-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/pm_suspend.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-at91/pm_suspend.S

Purpose: provides the AT91 final suspend routine that runs from SRAM while clocks and DRAM are being reconfigured or powered down.

Important APIs/types/functions: exports `at91_pm_suspend_in_sram` and `at91_pm_suspend_in_sram_sz`. The assembly uses generated `PM_DATA_*` offsets, RAM controller constants, PMC fields, and conditionals for CPU v7, SAMA7, SAM9X60 PLL support, and legacy SAM v4/v5 controllers.

Control flow: the routine saves caller context, reads the selected mode and controller addresses from `struct at91_pm_data`, places SDRAM/DDR/UDDRC into the correct low-power state, switches master clocks toward slow-clock or low-power PLL configuration, performs WFI or backup shutdown sequencing, and restores clocks and memory-controller state before returning to C.

State and persistence: executes from SRAM because normal RAM may be unavailable. It preserves enough CPU/register state to resume, and relies on C code to preserve backup canary and DDR calibration data. Hardware state includes PMC, PLL, RAMC, DDR PHY, SFRBU, and SHDWC registers.

Dependencies and integration: tightly coupled to `pm.c` setup, `pm.h` layout, `pm_data-offsets.c` generated constants, ARM cache/outer-cache handling, and SoC Kconfig symbols that include or omit code paths.

Risks: this is timing- and ordering-sensitive assembly touching live clock and DRAM control registers. A wrong offset, missing cache flush, unsupported mode, or SoC conditional mismatch can hang the CPU before console output is available. SAMA7 and SAM9X60 PLL branches add extra integration risk because they depend on SoC-specific PMC semantics.

Test signals: link-time symbol size generation, suspend/resume loop tests in each PM mode, SRAM allocation/copy verification, stress with interrupts as wake sources, and failure-injection by omitting DT resources to ensure C code does not enter unsupported assembly paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/pm_suspend.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/sam9x60.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-at91/sam9x60.c

Purpose: registers the `sam9x60` AT91/Microchip device-tree machine descriptor.

Important APIs/types/functions: a compatible string table selects the SoC family and a `DT_MACHINE_START` block wires optional `.init_machine` PM initialization plus `.dt_compat` matching.

Control flow: during early ARM machine selection, the kernel matches the root DT compatible, then runs the descriptor's init hook to initialize PM or platform devices.

State and persistence: no local mutable state beyond descriptor registration; PM init may populate shared AT91 PM state.

Dependencies and integration: depends on AT91 `generic.h` init declarations, DT root compatible strings, and the ARM machine descriptor framework.

Risks: wrong compatible strings prevent the platform from matching or skip required PM initialization.

Test signals: boot with matching DT compatible, machine descriptor selection, and PM init messages for configured suspend support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/sam9x60.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/sam9x7.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-at91/sam9x7.c

Purpose: registers the `sam9x7` AT91/Microchip device-tree machine descriptor.

Important APIs/types/functions: a compatible string table selects the SoC family and a `DT_MACHINE_START` block wires optional `.init_machine` PM initialization plus `.dt_compat` matching.

Control flow: during early ARM machine selection, the kernel matches the root DT compatible, then runs the descriptor's init hook to initialize PM or platform devices.

State and persistence: no local mutable state beyond descriptor registration; PM init may populate shared AT91 PM state.

Dependencies and integration: depends on AT91 `generic.h` init declarations, DT root compatible strings, and the ARM machine descriptor framework.

Risks: wrong compatible strings prevent the platform from matching or skip required PM initialization.

Test signals: boot with matching DT compatible, machine descriptor selection, and PM init messages for configured suspend support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/sam9x7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/sam_secure.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-at91/sam_secure.c

Purpose: wraps AT91 secure monitor calls used by secure power-management firmware.

Important APIs/types/functions: global `optee_available`; macro `SAM_SIP_SMC_STD_CALL_VAL()`; functions `sam_smccc_call()`, `sam_linux_is_optee_available()`, and `sam_secure_init()`.

Control flow: `sam_secure_init()` locates an `optee` node with method `smc` and records availability. `sam_smccc_call()` encodes the SIP function number, invokes `arm_smccc_smc()`, and returns the result structure to PM code.

State and persistence: only the boot-time `optee_available` boolean persists.

Dependencies and integration: depends on ARM SMCCC, OF lookup, and `sam_secure.h` function IDs. `pm.c` uses it when `CONFIG_ATMEL_SECURE_PM` is enabled.

Risks: firmware ABI mismatches or absent OP-TEE nodes can disable secure PM or return unsupported modes. The wrapper does not validate function arguments beyond encoding the call number.

Test signals: boot with and without OP-TEE, secure suspend-mode negotiation, and checking firmware return values during SAMA5 secure PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/sam_secure.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/sam_secure.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-at91/sam_secure.h

Purpose: declares the secure PM interface shared by AT91 platform code.

Important APIs/types/functions: defines SIP function IDs `SAMA5_SMC_SIP_SET_SUSPEND_MODE` and `SAMA5_SMC_SIP_GET_SUSPEND_MODE`; declares `sam_secure_init()`, `sam_smccc_call()`, and `sam_linux_is_optee_available()`.

Control flow: callers initialize secure availability at machine init and call into secure firmware during PM setup.

State and persistence: header only; state is in `sam_secure.c`.

Dependencies and integration: includes Linux types and SMCCC result types through users. It is consumed by SAMA5 machine and PM code.

Risks: function ID changes must stay synchronized with firmware. Missing declarations would force duplicate SMCCC encodings.

Test signals: compile coverage under `CONFIG_ATMEL_SECURE_PM` and secure suspend negotiation on OP-TEE systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/sam_secure.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/sama5.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-at91/sama5.c

Purpose: registers SAMA5 device-tree machine descriptors and secure-cache setup.

Important APIs/types/functions: `sama5_l2c310_write_sec()` forwards L2C writes through `sam_smccc_call(SMC_CMD_L2X0SETUP1, ...)`; `sama5_secure_cache_init()` installs it in `outer_cache.write_sec`. Machine descriptors cover `atmel,sama5`, `atmel,sama5d4`, and `atmel,sama5d2`.

Control flow: DT machine matching calls SAMA5 PM init and optional secure cache init. The SAMA5D2 descriptor also initializes secure support via `sam_secure_init()`.

State and persistence: persistent effects are machine descriptor registration, outer-cache secure-write hook, and PM setup.

Dependencies and integration: integrates with `generic.h` PM init declarations, L2 cache controller hooks, secure SMCCC wrapper, and DT compatibles.

Risks: secure cache writes require firmware support; wrong compatible ordering can select the wrong PM path. Secure PM availability changes how `sama5d2_pm_init()` behaves.

Test signals: DT boot for SAMA5D3/D4/D2, L2 cache initialization under secure firmware, and suspend-mode registration messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/sama5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/sama7.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-at91/sama7.c

Purpose: registers the `sama7` AT91/Microchip device-tree machine descriptor.

Important APIs/types/functions: a compatible string table selects the SoC family and a `DT_MACHINE_START` block wires optional `.init_machine` PM initialization plus `.dt_compat` matching.

Control flow: during early ARM machine selection, the kernel matches the root DT compatible, then runs the descriptor's init hook to initialize PM or platform devices.

State and persistence: no local mutable state beyond descriptor registration; PM init may populate shared AT91 PM state.

Dependencies and integration: depends on AT91 `generic.h` init declarations, DT root compatible strings, and the ARM machine descriptor framework.

Risks: wrong compatible strings prevent the platform from matching or skip required PM initialization.

Test signals: boot with matching DT compatible, machine descriptor selection, and PM init messages for configured suspend support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/sama7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/samv7.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-at91/samv7.c

Purpose: registers the `samv7` AT91/Microchip device-tree machine descriptor.

Important APIs/types/functions: a compatible string table selects the SoC family and a `DT_MACHINE_START` block wires optional `.init_machine` PM initialization plus `.dt_compat` matching.

Control flow: during early ARM machine selection, the kernel matches the root DT compatible, then runs the descriptor's init hook to initialize PM or platform devices.

State and persistence: no local mutable state beyond descriptor registration; PM init may populate shared AT91 PM state.

Dependencies and integration: depends on AT91 `generic.h` init declarations, DT root compatible strings, and the ARM machine descriptor framework.

Risks: wrong compatible strings prevent the platform from matching or skip required PM initialization.

Test signals: boot with matching DT compatible, machine descriptor selection, and PM init messages for configured suspend support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-at91/samv7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-axxia/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-axxia/Kconfig

Purpose: defines the kernel configuration surface for the `mach-axxia` ARM machine family.

Important APIs/types/functions: Kconfig symbols in this file select the architecture or board family, CPU class, device-tree support, timers, SMP/PM prerequisites, and related driver dependencies.

Control flow: there is no runtime control flow. During configuration, selected symbols determine which machine descriptors, board files, SMP code, and low-level helpers are compiled.

State and persistence: persists only as `.config` choices that affect the kernel image.

Dependencies and integration: integrates this machine family into the ARM multiplatform build, Makefile object selection, DT machine matching, and common subsystems such as irqchip, clocksource, SMP, PM, and pinctrl where selected.

Risks: incorrect selects can produce kernels that build but miss required runtime infrastructure, while overly broad selects keep obsolete board code enabled. Rename or dependency changes must stay synchronized with the local Makefile and DT compatibles.

Test signals: `olddefconfig`/`savedefconfig`, all relevant defconfig builds, and boot checks that the expected object files are linked for selected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-axxia/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-axxia/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-axxia/Makefile

Purpose: maps `mach-axxia` Kconfig symbols to the machine-family object files built into the ARM kernel.

Important APIs/types/functions: `obj-y` and `obj-$(CONFIG_...)` lines select machine descriptors, board files, SMP helpers, PM helpers, and assembly startup objects.

Control flow: build-time only. Kbuild evaluates configuration symbols and links the listed objects into `vmlinux`.

State and persistence: no runtime state; the persistent effect is the linked kernel object set.

Dependencies and integration: must stay synchronized with Kconfig symbols, source filenames, and machine/CPU method declarations.

Risks: missing object entries lead to unresolved symbols or non-booting platforms; stale entries break builds when configs are enabled.

Test signals: compile all configs touching `mach-axxia`, verify expected objects in build logs, and boot platforms that require optional SMP/PM objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-axxia/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-axxia/axxia.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-axxia/axxia.c

Purpose: registers the LSI Axxia AXM55xx DT machine descriptor.

Important APIs/types/functions: `axxia_dt_match[]` and `DT_MACHINE_START(AXXIA_DT, ...)`.

Control flow: selected during ARM DT machine matching, with SMP handled separately by Axxia CPU method code.

State and persistence: descriptor-only; no mutable state.

Dependencies and integration: depends on Kconfig/Makefile and Axxia device-tree compatibles.

Risks: compatible drift prevents the platform from selecting the intended machine descriptor.

Test signals: AXM55xx DT boot and SMP method registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-axxia/axxia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-axxia/platsmp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-axxia/platsmp.c

Purpose: implements secondary CPU bring-up for LSI Axxia AXM55xx systems.

Important APIs/types/functions: defines reset-controller offsets `SC_CRIT_WRITE_KEY` and `SC_RST_CPU_HOLD`; `write_release_addr()`, `axxia_boot_secondary()`, `axxia_smp_prepare_cpus()`, and `axxia_smp_ops`.

Control flow: prepare maps the reset controller from the `syscon` compatible node and parks all secondary CPUs in reset while writing the physical `secondary_startup` release address. Booting a CPU clears that CPU's hold bit after using the critical-write key.

State and persistence: persistent mapped syscon state is used for subsequent CPU starts; the reset controller holds per-CPU release state.

Dependencies and integration: depends on OF syscon lookup, ARM `secondary_startup`, `smp_operations`, and Axxia reset register ABI.

Risks: incorrect reset-controller mapping or release address leaves secondary CPUs parked. The code assumes physical startup address fits the platform register and that CPU numbering matches reset bits.

Test signals: SMP boot on AXM55xx DT, CPU hotplug where applicable, and logs for reset-controller lookup failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-axxia/platsmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/Kconfig

Purpose: defines the kernel configuration surface for the `mach-bcm` ARM machine family.

Important APIs/types/functions: Kconfig symbols in this file select the architecture or board family, CPU class, device-tree support, timers, SMP/PM prerequisites, and related driver dependencies.

Control flow: there is no runtime control flow. During configuration, selected symbols determine which machine descriptors, board files, SMP code, and low-level helpers are compiled.

State and persistence: persists only as `.config` choices that affect the kernel image.

Dependencies and integration: integrates this machine family into the ARM multiplatform build, Makefile object selection, DT machine matching, and common subsystems such as irqchip, clocksource, SMP, PM, and pinctrl where selected.

Risks: incorrect selects can produce kernels that build but miss required runtime infrastructure, while overly broad selects keep obsolete board code enabled. Rename or dependency changes must stay synchronized with the local Makefile and DT compatibles.

Test signals: `olddefconfig`/`savedefconfig`, all relevant defconfig builds, and boot checks that the expected object files are linked for selected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/Makefile

Purpose: maps `mach-bcm` Kconfig symbols to the machine-family object files built into the ARM kernel.

Important APIs/types/functions: `obj-y` and `obj-$(CONFIG_...)` lines select machine descriptors, board files, SMP helpers, PM helpers, and assembly startup objects.

Control flow: build-time only. Kbuild evaluates configuration symbols and links the listed objects into `vmlinux`.

State and persistence: no runtime state; the persistent effect is the linked kernel object set.

Dependencies and integration: must stay synchronized with Kconfig symbols, source filenames, and machine/CPU method declarations.

Risks: missing object entries lead to unresolved symbols or non-booting platforms; stale entries break builds when configs are enabled.

Test signals: compile all configs touching `mach-bcm`, verify expected objects in build logs, and boot platforms that require optional SMP/PM objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm2711.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm2711.c

Purpose: provides Broadcom `bcm2711` machine or board glue.

Important APIs/types/functions: usually defines a root DT compatible table and `DT_MACHINE_START`; board variants may also define init, map-io, restart, or fault-handler hooks.

Control flow: ARM machine selection matches the compatible list, then optional hooks register platform devices, install abort/restart behavior, map fixed IO, or populate OF devices.

State and persistence: machine descriptors and any installed hooks persist for the boot lifetime; mapped IO or platform devices persist where used.

Dependencies and integration: integrates with ARM machine descriptors, Broadcom Kconfig/Makefile selection, OF platform population, SMP method files, and board-specific reset/fault hardware.

Risks: compatible mismatches or missing hooks can leave a board without restart, DMA zone setup, or required fault handling. Fixed IO mappings are address-layout sensitive.

Test signals: DT boot for the named Broadcom SoC, restart/fault behavior where implemented, and platform-device probe logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm2711.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm63xx_pmb.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm63xx_pmb.c

Purpose: powers up BCM63138 secondary CPU domains through the Broadcom PMB/BPCM reset controller.

Important APIs/types/functions: internal `bpcm_wr_rd_mask()` polls BPCM state after writes; `bcm63xx_pmb_get_resources()` parses CPU hardware ID and reset phandle; exported-to-local `bcm63xx_pmb_power_on_cpu()` performs PLL, CPU, RAM, clamp, and reset sequencing.

Control flow: SMP code passes a CPU node. The PMB helper maps the reset controller, serializes access with `pmb_lock`, checks if reset is already deasserted, powers CPU and memory rails, waits for status bits, clears clamps, deasserts reset, unmaps, and returns status.

State and persistence: no permanent mapping; each call maps/unmaps PMB registers. Hardware power/reset state persists after the function returns.

Dependencies and integration: uses reset phandle format with two cells, `bpcm_rd()`/`bpcm_wr()` from the BCM63xx reset framework, and is called by `bcm63xx_smp.c`.

Risks: polling loops have no explicit timeout inside this helper; a failed power transition can spin indefinitely if BPCM never reports the expected bit. CPU IDs above one are only warned about, not rejected.

Test signals: BCM63138 SMP boot, PMB status register tracing, invalid `resets` phandle tests, and secondary CPU reset/power sequencing on real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm63xx_pmb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm63xx_smp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm63xx_smp.c

Purpose: provides BCM63138 Cortex-A9 SMP startup.

Important APIs/types/functions: `scu_a9_enable()` maps/enables SCU, adjusts possible CPU mask, and disables VFP when secondary CPU lacks VFP; `bcm63138_smp_boot_secondary()` writes BootLUT reset vector and calls `bcm63xx_pmb_power_on_cpu()`; `bcm63138_smp_ops` registers the method.

Control flow: prepare enables the SCU and sets possible CPUs. Boot maps the `brcm,bcm63138-bootlut`, writes `secondary_startup` to `BOOTLUT_RESET_VECT`, locates the CPU node, powers it via PMB, and unmaps.

State and persistence: possible CPU mask and VFP capability are global CPU-feature state; BootLUT and PMB hardware retain reset vector/power state.

Dependencies and integration: depends on Cortex-A9 SCU helpers, VFP feature control, BootLUT DT node, PMB helper, and `CPU_METHOD_OF_DECLARE("brcm,bcm63138")`.

Risks: kernel-mode NEON forces UP restriction because CPU1 lacks VFP. Missing BootLUT or CPU node prevents secondary boot; mismatched reset phandles fail in PMB.

Test signals: boot logs showing VFP policy, `/proc/cpuinfo` CPU count, CPU1 online, and failure paths for absent BootLUT nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm63xx_smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm63xx_smp.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm63xx_smp.h

Purpose: provides local declarations, constants, or register definitions for `mach-bcm` code in `bcm63xx_smp.h`.

Important APIs/types/functions: the file defines macros, structure declarations, extern function prototypes, or register bit names consumed by sibling C/assembly files.

Control flow: header-only; control flow is in the including implementation files.

State and persistence: no independent state. Constants describe persistent hardware register layout or shared software contracts.

Dependencies and integration: included by platform init, PM, SMP, IRQ, PCIe, mux, or board glue in the same machine directory and sometimes by drivers using legacy platform data.

Risks: register offsets and bit masks are hardware ABI; mistakes compile cleanly but misprogram low-level SoC state. Prototype drift can hide integration errors across legacy board files.

Test signals: compile coverage of all including files, boot-time peripheral initialization, and targeted tests for the subsystem named by the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm63xx_smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm_5301x.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm_5301x.c

Purpose: provides Broadcom `bcm_5301x` machine or board glue.

Important APIs/types/functions: usually defines a root DT compatible table and `DT_MACHINE_START`; board variants may also define init, map-io, restart, or fault-handler hooks.

Control flow: ARM machine selection matches the compatible list, then optional hooks register platform devices, install abort/restart behavior, map fixed IO, or populate OF devices.

State and persistence: machine descriptors and any installed hooks persist for the boot lifetime; mapped IO or platform devices persist where used.

Dependencies and integration: integrates with ARM machine descriptors, Broadcom Kconfig/Makefile selection, OF platform population, SMP method files, and board-specific reset/fault hardware.

Risks: compatible mismatches or missing hooks can leave a board without restart, DMA zone setup, or required fault handling. Fixed IO mappings are address-layout sensitive.

Test signals: DT boot for the named Broadcom SoC, restart/fault behavior where implemented, and platform-device probe logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm_5301x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm_cygnus.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm_cygnus.c

Purpose: provides Broadcom `bcm_cygnus` machine or board glue.

Important APIs/types/functions: usually defines a root DT compatible table and `DT_MACHINE_START`; board variants may also define init, map-io, restart, or fault-handler hooks.

Control flow: ARM machine selection matches the compatible list, then optional hooks register platform devices, install abort/restart behavior, map fixed IO, or populate OF devices.

State and persistence: machine descriptors and any installed hooks persist for the boot lifetime; mapped IO or platform devices persist where used.

Dependencies and integration: integrates with ARM machine descriptors, Broadcom Kconfig/Makefile selection, OF platform population, SMP method files, and board-specific reset/fault hardware.

Risks: compatible mismatches or missing hooks can leave a board without restart, DMA zone setup, or required fault handling. Fixed IO mappings are address-layout sensitive.

Test signals: DT boot for the named Broadcom SoC, restart/fault behavior where implemented, and platform-device probe logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm_cygnus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm_hr2.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm_hr2.c

Purpose: provides Broadcom `bcm_hr2` machine or board glue.

Important APIs/types/functions: usually defines a root DT compatible table and `DT_MACHINE_START`; board variants may also define init, map-io, restart, or fault-handler hooks.

Control flow: ARM machine selection matches the compatible list, then optional hooks register platform devices, install abort/restart behavior, map fixed IO, or populate OF devices.

State and persistence: machine descriptors and any installed hooks persist for the boot lifetime; mapped IO or platform devices persist where used.

Dependencies and integration: integrates with ARM machine descriptors, Broadcom Kconfig/Makefile selection, OF platform population, SMP method files, and board-specific reset/fault hardware.

Risks: compatible mismatches or missing hooks can leave a board without restart, DMA zone setup, or required fault handling. Fixed IO mappings are address-layout sensitive.

Test signals: DT boot for the named Broadcom SoC, restart/fault behavior where implemented, and platform-device probe logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm_hr2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm_kona_smc.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm_kona_smc.c

Purpose: implements Broadcom Kona secure monitor call support using a small non-cacheable shared buffer.

Important APIs/types/functions: `struct bcm_kona_smc_data`, global `bcm_smc_buffer_phys` and `bcm_smc_buffer`, `bcm_kona_smc_init()`, `bcm_kona_do_smc()`, `__bcm_kona_smc()`, and public `bcm_kona_smc()`.

Control flow: init finds the compatible secure service node, reads its buffer size, allocates coherent memory, and stores physical/virtual addresses. Callers populate the shared buffer with service ID and arguments, execute the monitor call on CPU0 via `on_each_cpu()`/IPI-safe helper, and return the monitor status.

State and persistence: the shared coherent buffer and its physical address persist after init. Calls temporarily store arguments/results in that buffer.

Dependencies and integration: used by Kona L2 cache setup and other mobile Broadcom platform code; depends on DT, DMA coherent allocation, CPU affinity, and secure monitor ABI constants from `bcm_kona_smc.h`.

Risks: secure monitor calls are firmware ABI-sensitive and use global shared state, so concurrent callers would require serialization by higher-level assumptions. Missing init leaves later secure calls unable to communicate.

Test signals: successful `bcm_kona_smc_init()`, secure L2 enable return value `SEC_ROM_RET_OK`, and boot tests on BCM mobile SoCs with OP-TEE/secure ROM present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm_kona_smc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm_kona_smc.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm_kona_smc.h

Purpose: provides local declarations, constants, or register definitions for `mach-bcm` code in `bcm_kona_smc.h`.

Important APIs/types/functions: the file defines macros, structure declarations, extern function prototypes, or register bit names consumed by sibling C/assembly files.

Control flow: header-only; control flow is in the including implementation files.

State and persistence: no independent state. Constants describe persistent hardware register layout or shared software contracts.

Dependencies and integration: included by platform init, PM, SMP, IRQ, PCIe, mux, or board glue in the same machine directory and sometimes by drivers using legacy platform data.

Risks: register offsets and bit masks are hardware ABI; mistakes compile cleanly but misprogram low-level SoC state. Prototype drift can hide integration errors across legacy board files.

Test signals: compile coverage of all including files, boot-time peripheral initialization, and targeted tests for the subsystem named by the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm_kona_smc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm_nsp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm_nsp.c

Purpose: provides Broadcom `bcm_nsp` machine or board glue.

Important APIs/types/functions: usually defines a root DT compatible table and `DT_MACHINE_START`; board variants may also define init, map-io, restart, or fault-handler hooks.

Control flow: ARM machine selection matches the compatible list, then optional hooks register platform devices, install abort/restart behavior, map fixed IO, or populate OF devices.

State and persistence: machine descriptors and any installed hooks persist for the boot lifetime; mapped IO or platform devices persist where used.

Dependencies and integration: integrates with ARM machine descriptors, Broadcom Kconfig/Makefile selection, OF platform population, SMP method files, and board-specific reset/fault hardware.

Risks: compatible mismatches or missing hooks can leave a board without restart, DMA zone setup, or required fault handling. Fixed IO mappings are address-layout sensitive.

Test signals: DT boot for the named Broadcom SoC, restart/fault behavior where implemented, and platform-device probe logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/bcm_nsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/board_bcm21664.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/board_bcm21664.c

Purpose: provides Broadcom `board_bcm21664` machine or board glue.

Important APIs/types/functions: usually defines a root DT compatible table and `DT_MACHINE_START`; board variants may also define init, map-io, restart, or fault-handler hooks.

Control flow: ARM machine selection matches the compatible list, then optional hooks register platform devices, install abort/restart behavior, map fixed IO, or populate OF devices.

State and persistence: machine descriptors and any installed hooks persist for the boot lifetime; mapped IO or platform devices persist where used.

Dependencies and integration: integrates with ARM machine descriptors, Broadcom Kconfig/Makefile selection, OF platform population, SMP method files, and board-specific reset/fault hardware.

Risks: compatible mismatches or missing hooks can leave a board without restart, DMA zone setup, or required fault handling. Fixed IO mappings are address-layout sensitive.

Test signals: DT boot for the named Broadcom SoC, restart/fault behavior where implemented, and platform-device probe logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/board_bcm21664.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/board_bcm23550.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/board_bcm23550.c

Purpose: provides Broadcom `board_bcm23550` machine or board glue.

Important APIs/types/functions: usually defines a root DT compatible table and `DT_MACHINE_START`; board variants may also define init, map-io, restart, or fault-handler hooks.

Control flow: ARM machine selection matches the compatible list, then optional hooks register platform devices, install abort/restart behavior, map fixed IO, or populate OF devices.

State and persistence: machine descriptors and any installed hooks persist for the boot lifetime; mapped IO or platform devices persist where used.

Dependencies and integration: integrates with ARM machine descriptors, Broadcom Kconfig/Makefile selection, OF platform population, SMP method files, and board-specific reset/fault hardware.

Risks: compatible mismatches or missing hooks can leave a board without restart, DMA zone setup, or required fault handling. Fixed IO mappings are address-layout sensitive.

Test signals: DT boot for the named Broadcom SoC, restart/fault behavior where implemented, and platform-device probe logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/board_bcm23550.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/board_bcm281xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/board_bcm281xx.c

Purpose: provides Broadcom `board_bcm281xx` machine or board glue.

Important APIs/types/functions: usually defines a root DT compatible table and `DT_MACHINE_START`; board variants may also define init, map-io, restart, or fault-handler hooks.

Control flow: ARM machine selection matches the compatible list, then optional hooks register platform devices, install abort/restart behavior, map fixed IO, or populate OF devices.

State and persistence: machine descriptors and any installed hooks persist for the boot lifetime; mapped IO or platform devices persist where used.

Dependencies and integration: integrates with ARM machine descriptors, Broadcom Kconfig/Makefile selection, OF platform population, SMP method files, and board-specific reset/fault hardware.

Risks: compatible mismatches or missing hooks can leave a board without restart, DMA zone setup, or required fault handling. Fixed IO mappings are address-layout sensitive.

Test signals: DT boot for the named Broadcom SoC, restart/fault behavior where implemented, and platform-device probe logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/board_bcm281xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/board_bcm2835.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/board_bcm2835.c

Purpose: provides Broadcom `board_bcm2835` machine or board glue.

Important APIs/types/functions: usually defines a root DT compatible table and `DT_MACHINE_START`; board variants may also define init, map-io, restart, or fault-handler hooks.

Control flow: ARM machine selection matches the compatible list, then optional hooks register platform devices, install abort/restart behavior, map fixed IO, or populate OF devices.

State and persistence: machine descriptors and any installed hooks persist for the boot lifetime; mapped IO or platform devices persist where used.

Dependencies and integration: integrates with ARM machine descriptors, Broadcom Kconfig/Makefile selection, OF platform population, SMP method files, and board-specific reset/fault hardware.

Risks: compatible mismatches or missing hooks can leave a board without restart, DMA zone setup, or required fault handling. Fixed IO mappings are address-layout sensitive.

Test signals: DT boot for the named Broadcom SoC, restart/fault behavior where implemented, and platform-device probe logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/board_bcm2835.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/board_bcmbca.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/board_bcmbca.c

Purpose: provides Broadcom `board_bcmbca` machine or board glue.

Important APIs/types/functions: usually defines a root DT compatible table and `DT_MACHINE_START`; board variants may also define init, map-io, restart, or fault-handler hooks.

Control flow: ARM machine selection matches the compatible list, then optional hooks register platform devices, install abort/restart behavior, map fixed IO, or populate OF devices.

State and persistence: machine descriptors and any installed hooks persist for the boot lifetime; mapped IO or platform devices persist where used.

Dependencies and integration: integrates with ARM machine descriptors, Broadcom Kconfig/Makefile selection, OF platform population, SMP method files, and board-specific reset/fault hardware.

Risks: compatible mismatches or missing hooks can leave a board without restart, DMA zone setup, or required fault handling. Fixed IO mappings are address-layout sensitive.

Test signals: DT boot for the named Broadcom SoC, restart/fault behavior where implemented, and platform-device probe logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/board_bcmbca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/brcmstb.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/brcmstb.c

Purpose: provides Broadcom `brcmstb` machine or board glue.

Important APIs/types/functions: usually defines a root DT compatible table and `DT_MACHINE_START`; board variants may also define init, map-io, restart, or fault-handler hooks.

Control flow: ARM machine selection matches the compatible list, then optional hooks register platform devices, install abort/restart behavior, map fixed IO, or populate OF devices.

State and persistence: machine descriptors and any installed hooks persist for the boot lifetime; mapped IO or platform devices persist where used.

Dependencies and integration: integrates with ARM machine descriptors, Broadcom Kconfig/Makefile selection, OF platform population, SMP method files, and board-specific reset/fault hardware.

Risks: compatible mismatches or missing hooks can leave a board without restart, DMA zone setup, or required fault handling. Fixed IO mappings are address-layout sensitive.

Test signals: DT boot for the named Broadcom SoC, restart/fault behavior where implemented, and platform-device probe logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/brcmstb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/kona_l2_cache.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/kona_l2_cache.c

Purpose: implements `mach-bcm` platform support in `kona_l2_cache.c`.

Important APIs/types/functions: defines local init functions, platform data, register helpers, or machine descriptors used by the surrounding ARM machine family.

Control flow: called from machine init, board init, subsystem callbacks, or build-selected platform hooks; it configures hardware resources and hands them to generic Linux subsystems.

State and persistence: usually stores static descriptors, mapped register bases, platform devices, or hardware configuration that persists after boot.

Dependencies and integration: tied to sibling headers, Kconfig/Makefile selection, device-tree compatibles, ARM machine hooks, and the relevant Linux subsystem for clocks, IRQs, PM, SMP, PCI, or media.

Risks: low-level register constants and legacy platform-data assumptions are hardware-specific. Errors may show up as missing devices, failed probes, or boot-time hangs rather than compile failures.

Test signals: compile with the owning config enabled, boot on matching DT/board files, and exercise the subsystem initialized by this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/kona_l2_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/kona_l2_cache.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/kona_l2_cache.h

Purpose: provides local declarations, constants, or register definitions for `mach-bcm` code in `kona_l2_cache.h`.

Important APIs/types/functions: the file defines macros, structure declarations, extern function prototypes, or register bit names consumed by sibling C/assembly files.

Control flow: header-only; control flow is in the including implementation files.

State and persistence: no independent state. Constants describe persistent hardware register layout or shared software contracts.

Dependencies and integration: included by platform init, PM, SMP, IRQ, PCIe, mux, or board glue in the same machine directory and sometimes by drivers using legacy platform data.

Risks: register offsets and bit masks are hardware ABI; mistakes compile cleanly but misprogram low-level SoC state. Prototype drift can hide integration errors across legacy board files.

Test signals: compile coverage of all including files, boot-time peripheral initialization, and targeted tests for the subsystem named by the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/kona_l2_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/platsmp-brcmstb.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/platsmp-brcmstb.c

Purpose: implements Broadcom STB/Brahma-B15 SMP boot and CPU hotplug power control.

Important APIs/types/functions: power-zone bit definitions, per-CPU software state helpers, `pwr_ctrl_*()` register helpers, `brcmstb_cpu_power_on()`, `brcmstb_cpu_boot()`, `brcmstb_boot_secondary()`, optional `brcmstb_cpu_die()` and `brcmstb_cpu_kill()`, and `brcmstb_smp_ops`.

Control flow: prepare finds `brcm,brcmstb-smpboot`, maps `syscon-cpu` and `syscon-cont`, and records register offsets. Boot checks if CPU is powered, powers memory/clock/isolation zones if needed, writes the reset vector to the HIF control block, and deasserts reset. Hotplug death flushes coherency and waits in WFI; kill waits for software state to clear and powers the CPU zone down.

State and persistence: mapped syscon pointers and register offsets are global. Per-CPU software state is cache-synchronized because dying CPUs may have disabled coherency. Hardware power-zone state persists.

Dependencies and integration: uses OF phandles, ARM v7 coherency helpers, `secondary_startup`, `smp_operations`, jiffies timeouts, and Broadcom STB DT bindings.

Risks: panics on power-state timeout are deliberate because partial CPU power transitions are unrecoverable. CPU0 power-off is refused. Cache-synchronized software state is fragile but necessary around hotplug.

Test signals: SMP boot with `brcm,brahma-b15` CPU method, CPU hotplug online/offline loops, timeout-free power-zone polling, and validation of required syscon phandles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/platsmp-brcmstb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/platsmp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/platsmp.c

Purpose: implements Broadcom mobile, NSP, and BCM2836 SMP startup methods.

Important APIs/types/functions: `scu_a9_enable()`, `secondary_boot_addr_for()`, `kona_boot_secondary()`, `bcm23550_boot_secondary()`, `nsp_write_lut()`, `nsp_boot_secondary()`, `bcm2836_boot_secondary()`, and SMP operation tables for Kona, BCM23550, NSP, and BCM2836.

Control flow: Cortex-A9 platforms optionally enable SCU in prepare. Kona reads each CPU node's `secondary-boot-reg`, writes the physical `secondary_startup` address ORed with CPU ID, sends `sev`, and waits for ROM to clear the low bits. BCM23550 layers a CDC run-state command on top. NSP writes the startup address into SKU-ROM LUT and sends a wakeup IPI. BCM2836 writes `secondary_startup` to the local interrupt controller mailbox and sends `sev`.

State and persistence: no durable software state beyond CPU-present changes if SCU setup fails; boot registers/mailboxes/LUTs retain the last startup address.

Dependencies and integration: depends on CPU DT properties and compatible CPU methods, ARM SCU helpers, Broadcom local interrupt controller registers, and `secondary_startup`.

Risks: boot-register address or CPU ID mismatch strands secondaries. The Kona wait is short and local-clock based; slow firmware handoff can appear as timeout. BCM2836 mailbox offsets are register-layout sensitive.

Test signals: CPU online count across Broadcom mobile/NSP/Raspberry Pi compatible DTs, bad/missing `secondary-boot-reg` negative tests, and secondary boot timeout logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/platsmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/platsmp.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-bcm/platsmp.h

Purpose: provides local declarations, constants, or register definitions for `mach-bcm` code in `platsmp.h`.

Important APIs/types/functions: the file defines macros, structure declarations, extern function prototypes, or register bit names consumed by sibling C/assembly files.

Control flow: header-only; control flow is in the including implementation files.

State and persistence: no independent state. Constants describe persistent hardware register layout or shared software contracts.

Dependencies and integration: included by platform init, PM, SMP, IRQ, PCIe, mux, or board glue in the same machine directory and sometimes by drivers using legacy platform data.

Risks: register offsets and bit masks are hardware ABI; mistakes compile cleanly but misprogram low-level SoC state. Prototype drift can hide integration errors across legacy board files.

Test signals: compile coverage of all including files, boot-time peripheral initialization, and targeted tests for the subsystem named by the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-bcm/platsmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-berlin/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-berlin/Kconfig

Purpose: defines the kernel configuration surface for the `mach-berlin` ARM machine family.

Important APIs/types/functions: Kconfig symbols in this file select the architecture or board family, CPU class, device-tree support, timers, SMP/PM prerequisites, and related driver dependencies.

Control flow: there is no runtime control flow. During configuration, selected symbols determine which machine descriptors, board files, SMP code, and low-level helpers are compiled.

State and persistence: persists only as `.config` choices that affect the kernel image.

Dependencies and integration: integrates this machine family into the ARM multiplatform build, Makefile object selection, DT machine matching, and common subsystems such as irqchip, clocksource, SMP, PM, and pinctrl where selected.

Risks: incorrect selects can produce kernels that build but miss required runtime infrastructure, while overly broad selects keep obsolete board code enabled. Rename or dependency changes must stay synchronized with the local Makefile and DT compatibles.

Test signals: `olddefconfig`/`savedefconfig`, all relevant defconfig builds, and boot checks that the expected object files are linked for selected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-berlin/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-berlin/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-berlin/Makefile

Purpose: maps `mach-berlin` Kconfig symbols to the machine-family object files built into the ARM kernel.

Important APIs/types/functions: `obj-y` and `obj-$(CONFIG_...)` lines select machine descriptors, board files, SMP helpers, PM helpers, and assembly startup objects.

Control flow: build-time only. Kbuild evaluates configuration symbols and links the listed objects into `vmlinux`.

State and persistence: no runtime state; the persistent effect is the linked kernel object set.

Dependencies and integration: must stay synchronized with Kconfig symbols, source filenames, and machine/CPU method declarations.

Risks: missing object entries lead to unresolved symbols or non-booting platforms; stale entries break builds when configs are enabled.

Test signals: compile all configs touching `mach-berlin`, verify expected objects in build logs, and boot platforms that require optional SMP/PM objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-berlin/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-berlin/berlin.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-berlin/berlin.c

Purpose: registers Marvell Berlin DT machine support.

Important APIs/types/functions: Berlin compatible table for BG2/BG2CD/BG2Q families and `DT_MACHINE_START(BERLIN_DT, ...)` with SMP ops when configured.

Control flow: ARM machine matching selects the descriptor; SMP startup is provided by Berlin CPU method code.

State and persistence: descriptor-only state.

Dependencies and integration: depends on Berlin Kconfig symbols, Makefile objects, and DT root compatibles.

Risks: missing compatible entries prevent affected Berlin boards from booting under this descriptor.

Test signals: boot across BG2/BG2CD/BG2Q DTs and secondary CPU online when SMP is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-berlin/berlin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-berlin/headsmp.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-berlin/headsmp.S

Purpose: contains low-level ARM assembly support for `mach-berlin` in `headsmp.S`.

Important APIs/types/functions: exports assembly entry points or data symbols referenced by C platform code, typically for secondary CPU startup, secure monitor calls, or suspend routines.

Control flow: execution enters through exported labels from C or CPU reset firmware, performs register-level setup, and returns or branches into common ARM startup/resume code.

State and persistence: assembly mutates CPU registers and sometimes SoC reset/power registers; persistent software state is limited to exported symbols and code copied or referenced by C.

Dependencies and integration: tied to ARM calling conventions, linker symbols, machine-specific C files, and Kconfig symbols that include the object.

Risks: no type checking across the C/assembly boundary; wrong register usage, symbol naming, or section placement can fail only at boot/resume time.

Test signals: successful assembly/link, boot or suspend path that reaches the entry point, and CPU online/resume tests on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-berlin/headsmp.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-berlin/platsmp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-berlin/platsmp.c

Purpose: starts and hotplugs secondary CPUs on Marvell Berlin SoCs.

Important APIs/types/functions: reset register constants, external `boot_inst` from `headsmp.S`, `berlin_perform_reset_cpu()`, `berlin_boot_secondary()`, `berlin_smp_prepare_cpus()`, optional `berlin_cpu_die()`/`berlin_cpu_kill()`, and `berlin_smp_ops`.

Control flow: prepare maps the CPU control node and writes a boot instruction/address sequence used by the secondary reset vector. Boot performs a software reset for the requested CPU. Hotplug death exits coherency and waits; kill resets the CPU and reports success.

State and persistence: global `cpu_ctrl` mapping is retained after prepare; hardware reset vector/control registers persist the programmed startup path.

Dependencies and integration: couples C SMP ops with `headsmp.S` boot instruction, OF CPU control registers, ARM v7 cache/coherency helpers, and Berlin DT machine descriptor.

Risks: reset-vector programming must match the ROM/reset expectations. Missing control mapping disables SMP. Hotplug behavior is minimal and assumes reset reliably stops the core.

Test signals: SMP boot on Berlin BG2/BG2CD/BG2Q, CPU hotplug loops under `CONFIG_HOTPLUG_CPU`, and DT control-node validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-berlin/platsmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-clps711x/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-clps711x/Kconfig

Purpose: defines the kernel configuration surface for the `mach-clps711x` ARM machine family.

Important APIs/types/functions: Kconfig symbols in this file select the architecture or board family, CPU class, device-tree support, timers, SMP/PM prerequisites, and related driver dependencies.

Control flow: there is no runtime control flow. During configuration, selected symbols determine which machine descriptors, board files, SMP code, and low-level helpers are compiled.

State and persistence: persists only as `.config` choices that affect the kernel image.

Dependencies and integration: integrates this machine family into the ARM multiplatform build, Makefile object selection, DT machine matching, and common subsystems such as irqchip, clocksource, SMP, PM, and pinctrl where selected.

Risks: incorrect selects can produce kernels that build but miss required runtime infrastructure, while overly broad selects keep obsolete board code enabled. Rename or dependency changes must stay synchronized with the local Makefile and DT compatibles.

Test signals: `olddefconfig`/`savedefconfig`, all relevant defconfig builds, and boot checks that the expected object files are linked for selected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-clps711x/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-clps711x/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-clps711x/Makefile

Purpose: maps `mach-clps711x` Kconfig symbols to the machine-family object files built into the ARM kernel.

Important APIs/types/functions: `obj-y` and `obj-$(CONFIG_...)` lines select machine descriptors, board files, SMP helpers, PM helpers, and assembly startup objects.

Control flow: build-time only. Kbuild evaluates configuration symbols and links the listed objects into `vmlinux`.

State and persistence: no runtime state; the persistent effect is the linked kernel object set.

Dependencies and integration: must stay synchronized with Kconfig symbols, source filenames, and machine/CPU method declarations.

Risks: missing object entries lead to unresolved symbols or non-booting platforms; stale entries break builds when configs are enabled.

Test signals: compile all configs touching `mach-clps711x`, verify expected objects in build logs, and boot platforms that require optional SMP/PM objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-clps711x/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-clps711x/board-dt.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-clps711x/board-dt.c

Purpose: supplies DT machine support for Cirrus Logic CLPS711X ARM systems.

Important APIs/types/functions: static IO mapping constants, `clps711x_map_io()`, cpuidle platform resource/device registration in `clps711x_init()`, `clps711x_restart()`, and `DT_MACHINE_START(CLPS711X_DT, ...)`.

Control flow: machine mapping installs a fixed virtual mapping for CLPS711X registers. Init registers an `clps711x-cpuidle` platform device and populates OF devices. Restart writes to the system control region to trigger reset.

State and persistence: fixed IO mapping and a cpuidle platform device persist for the boot lifetime.

Dependencies and integration: depends on ARM machine descriptor hooks, `iotable_init`, OF platform population, CLPS711X register layout, and cpuidle driver matching.

Risks: fixed virtual mappings are sensitive to address conflicts. Restart assumes the mapped control register remains accessible late in shutdown.

Test signals: DT boot, cpuidle device probe, OF child population, and reboot/reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-clps711x/board-dt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/Kconfig

Purpose: defines the kernel configuration surface for the `mach-davinci` ARM machine family.

Important APIs/types/functions: Kconfig symbols in this file select the architecture or board family, CPU class, device-tree support, timers, SMP/PM prerequisites, and related driver dependencies.

Control flow: there is no runtime control flow. During configuration, selected symbols determine which machine descriptors, board files, SMP code, and low-level helpers are compiled.

State and persistence: persists only as `.config` choices that affect the kernel image.

Dependencies and integration: integrates this machine family into the ARM multiplatform build, Makefile object selection, DT machine matching, and common subsystems such as irqchip, clocksource, SMP, PM, and pinctrl where selected.

Risks: incorrect selects can produce kernels that build but miss required runtime infrastructure, while overly broad selects keep obsolete board code enabled. Rename or dependency changes must stay synchronized with the local Makefile and DT compatibles.

Test signals: `olddefconfig`/`savedefconfig`, all relevant defconfig builds, and boot checks that the expected object files are linked for selected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/Makefile

Purpose: maps `mach-davinci` Kconfig symbols to the machine-family object files built into the ARM kernel.

Important APIs/types/functions: `obj-y` and `obj-$(CONFIG_...)` lines select machine descriptors, board files, SMP helpers, PM helpers, and assembly startup objects.

Control flow: build-time only. Kbuild evaluates configuration symbols and links the listed objects into `vmlinux`.

State and persistence: no runtime state; the persistent effect is the linked kernel object set.

Dependencies and integration: must stay synchronized with Kconfig symbols, source filenames, and machine/CPU method declarations.

Risks: missing object entries lead to unresolved symbols or non-booting platforms; stale entries break builds when configs are enabled.

Test signals: compile all configs touching `mach-davinci`, verify expected objects in build logs, and boot platforms that require optional SMP/PM objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/clock.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/clock.h

Purpose: provides local declarations, constants, or register definitions for `mach-davinci` code in `clock.h`.

Important APIs/types/functions: the file defines macros, structure declarations, extern function prototypes, or register bit names consumed by sibling C/assembly files.

Control flow: header-only; control flow is in the including implementation files.

State and persistence: no independent state. Constants describe persistent hardware register layout or shared software contracts.

Dependencies and integration: included by platform init, PM, SMP, IRQ, PCIe, mux, or board glue in the same machine directory and sometimes by drivers using legacy platform data.

Risks: register offsets and bit masks are hardware ABI; mistakes compile cleanly but misprogram low-level SoC state. Prototype drift can hide integration errors across legacy board files.

Test signals: compile coverage of all including files, boot-time peripheral initialization, and targeted tests for the subsystem named by the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/common.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/common.c

Purpose: centralizes Davinci SoC initialization from a `davinci_soc_info` descriptor.

Important APIs/types/functions: global exported `davinci_soc_info`; `davinci_init_id()` decodes JTAG ID; `davinci_common_init()` copies SoC info, maps IO, initializes pinmux, and stores SRAM metadata; `davinci_init_late()` runs late board/device quirks.

Control flow: SoC-specific init such as `da850_init()` calls `davinci_common_init()` with IO descriptors, ID table, pinmux base/table, and SRAM data. Common init maps IO, identifies CPU variant, initializes pinmux if enabled, and exposes shared data to other Davinci helpers.

State and persistence: `davinci_soc_info` is global and exported; mapped IO and pinmux state persist after init.

Dependencies and integration: integrates with ARM `iotable_init`, Davinci mux code, CPU type helpers, `pdata_quirks_init()`, and SoC-specific files.

Risks: incorrect ID tables or JTAG mapping can misidentify the SoC. Global state means only one SoC descriptor can be active and consumers assume it is initialized early.

Test signals: boot logs showing detected CPU, pinmux setup success, late pdata quirks, and legacy platform device registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/common.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/common.h

Purpose: provides local declarations, constants, or register definitions for `mach-davinci` code in `common.h`.

Important APIs/types/functions: the file defines macros, structure declarations, extern function prototypes, or register bit names consumed by sibling C/assembly files.

Control flow: header-only; control flow is in the including implementation files.

State and persistence: no independent state. Constants describe persistent hardware register layout or shared software contracts.

Dependencies and integration: included by platform init, PM, SMP, IRQ, PCIe, mux, or board glue in the same machine directory and sometimes by drivers using legacy platform data.

Risks: register offsets and bit masks are hardware ABI; mistakes compile cleanly but misprogram low-level SoC state. Prototype drift can hide integration errors across legacy board files.

Test signals: compile coverage of all including files, boot-time peripheral initialization, and targeted tests for the subsystem named by the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/cputype.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/cputype.h

Purpose: provides local declarations, constants, or register definitions for `mach-davinci` code in `cputype.h`.

Important APIs/types/functions: the file defines macros, structure declarations, extern function prototypes, or register bit names consumed by sibling C/assembly files.

Control flow: header-only; control flow is in the including implementation files.

State and persistence: no independent state. Constants describe persistent hardware register layout or shared software contracts.

Dependencies and integration: included by platform init, PM, SMP, IRQ, PCIe, mux, or board glue in the same machine directory and sometimes by drivers using legacy platform data.

Risks: register offsets and bit masks are hardware ABI; mistakes compile cleanly but misprogram low-level SoC state. Prototype drift can hide integration errors across legacy board files.

Test signals: compile coverage of all including files, boot-time peripheral initialization, and targeted tests for the subsystem named by the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/cputype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/da850.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/da850.c

Purpose: describes TI DA850/OMAP-L138 SoC resources, pin muxing, IO maps, ID table, and VPIF platform devices.

Important APIs/types/functions: huge `da850_pins[]` mux table, `da850_io_desc[]`, `da850_ids[]`, VPIF display/capture resources and devices, `da850_register_vpif_display()`, `da850_register_vpif_capture()`, `davinci_soc_info_da850`, and `da850_init()`.

Control flow: board/DT code calls `da850_init()`, which delegates common setup through `davinci_common_init()` and maps SYSCFG0/SYSCFG1. Legacy video board code can then register VPIF capture/display devices with platform data.

State and persistence: mapped SYSCFG bases are stored globally in `da8xx_syscfg0_base` and `da8xx_syscfg1_base`; mux configuration data and platform-device definitions are static.

Dependencies and integration: depends on Davinci common init, mux macros, IRQ definitions, DA8xx constants, platform_device registration, and media VPIF platform data consumers.

Risks: the pinmux table is large and packed with register/offset/mode constants, making copy/paste mistakes high impact. VPIF devices share IRQ resources and require correct board-specific platform data.

Test signals: DA850 boot, pinmux debug output under `CONFIG_DAVINCI_MUX_DEBUG`, SYSCFG mapping warnings, VPIF capture/display probe on EVM/LCDK, and GPIO/peripheral pin tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/da850.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/da8xx-dt.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/da8xx-dt.c

Purpose: implements `mach-davinci` platform support in `da8xx-dt.c`.

Important APIs/types/functions: defines local init functions, platform data, register helpers, or machine descriptors used by the surrounding ARM machine family.

Control flow: called from machine init, board init, subsystem callbacks, or build-selected platform hooks; it configures hardware resources and hands them to generic Linux subsystems.

State and persistence: usually stores static descriptors, mapped register bases, platform devices, or hardware configuration that persists after boot.

Dependencies and integration: tied to sibling headers, Kconfig/Makefile selection, device-tree compatibles, ARM machine hooks, and the relevant Linux subsystem for clocks, IRQs, PM, SMP, PCI, or media.

Risks: low-level register constants and legacy platform-data assumptions are hardware-specific. Errors may show up as missing devices, failed probes, or boot-time hangs rather than compile failures.

Test signals: compile with the owning config enabled, boot on matching DT/board files, and exercise the subsystem initialized by this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/da8xx-dt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/da8xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/da8xx.h

Purpose: provides local declarations, constants, or register definitions for `mach-davinci` code in `da8xx.h`.

Important APIs/types/functions: the file defines macros, structure declarations, extern function prototypes, or register bit names consumed by sibling C/assembly files.

Control flow: header-only; control flow is in the including implementation files.

State and persistence: no independent state. Constants describe persistent hardware register layout or shared software contracts.

Dependencies and integration: included by platform init, PM, SMP, IRQ, PCIe, mux, or board glue in the same machine directory and sometimes by drivers using legacy platform data.

Risks: register offsets and bit masks are hardware ABI; mistakes compile cleanly but misprogram low-level SoC state. Prototype drift can hide integration errors across legacy board files.

Test signals: compile coverage of all including files, boot-time peripheral initialization, and targeted tests for the subsystem named by the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/da8xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/ddr2.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/ddr2.h

Purpose: provides local declarations, constants, or register definitions for `mach-davinci` code in `ddr2.h`.

Important APIs/types/functions: the file defines macros, structure declarations, extern function prototypes, or register bit names consumed by sibling C/assembly files.

Control flow: header-only; control flow is in the including implementation files.

State and persistence: no independent state. Constants describe persistent hardware register layout or shared software contracts.

Dependencies and integration: included by platform init, PM, SMP, IRQ, PCIe, mux, or board glue in the same machine directory and sometimes by drivers using legacy platform data.

Risks: register offsets and bit masks are hardware ABI; mistakes compile cleanly but misprogram low-level SoC state. Prototype drift can hide integration errors across legacy board files.

Test signals: compile coverage of all including files, boot-time peripheral initialization, and targeted tests for the subsystem named by the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/ddr2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/devices-da8xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/devices-da8xx.c

Purpose: provides DA8xx shared peripheral base-address helpers.

Important APIs/types/functions: global `da8xx_syscfg0_base`, `da8xx_syscfg1_base`, static `da8xx_ddr2_ctlr_base`, and `da8xx_get_mem_ctlr()`.

Control flow: callers request the DDR2 controller base; the helper lazily maps `DA8XX_DDR2_CTL_BASE` once and returns the cached mapping.

State and persistence: SYSCFG mappings are initialized by SoC setup; the DDR2 controller mapping persists after first use.

Dependencies and integration: used by DA8xx PM/sleep code and board glue needing memory-controller registers.

Risks: lazy mapping can fail late if memory is constrained, and callers must handle NULL. The globals assume `da850_init()` or equivalent ran first for SYSCFG bases.

Test signals: DDR2 low-power suspend path, callers checking non-NULL memory controller mapping, and boot warnings for failed `ioremap()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/devices-da8xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/hardware.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/hardware.h

Purpose: provides local declarations, constants, or register definitions for `mach-davinci` code in `hardware.h`.

Important APIs/types/functions: the file defines macros, structure declarations, extern function prototypes, or register bit names consumed by sibling C/assembly files.

Control flow: header-only; control flow is in the including implementation files.

State and persistence: no independent state. Constants describe persistent hardware register layout or shared software contracts.

Dependencies and integration: included by platform init, PM, SMP, IRQ, PCIe, mux, or board glue in the same machine directory and sometimes by drivers using legacy platform data.

Risks: register offsets and bit masks are hardware ABI; mistakes compile cleanly but misprogram low-level SoC state. Prototype drift can hide integration errors across legacy board files.

Test signals: compile coverage of all including files, boot-time peripheral initialization, and targeted tests for the subsystem named by the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/hardware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/irqs.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/irqs.h

Purpose: provides local declarations, constants, or register definitions for `mach-davinci` code in `irqs.h`.

Important APIs/types/functions: the file defines macros, structure declarations, extern function prototypes, or register bit names consumed by sibling C/assembly files.

Control flow: header-only; control flow is in the including implementation files.

State and persistence: no independent state. Constants describe persistent hardware register layout or shared software contracts.

Dependencies and integration: included by platform init, PM, SMP, IRQ, PCIe, mux, or board glue in the same machine directory and sometimes by drivers using legacy platform data.

Risks: register offsets and bit masks are hardware ABI; mistakes compile cleanly but misprogram low-level SoC state. Prototype drift can hide integration errors across legacy board files.

Test signals: compile coverage of all including files, boot-time peripheral initialization, and targeted tests for the subsystem named by the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/irqs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/mux.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/mux.c

Purpose: implements `mach-davinci` platform support in `mux.c`.

Important APIs/types/functions: defines local init functions, platform data, register helpers, or machine descriptors used by the surrounding ARM machine family.

Control flow: called from machine init, board init, subsystem callbacks, or build-selected platform hooks; it configures hardware resources and hands them to generic Linux subsystems.

State and persistence: usually stores static descriptors, mapped register bases, platform devices, or hardware configuration that persists after boot.

Dependencies and integration: tied to sibling headers, Kconfig/Makefile selection, device-tree compatibles, ARM machine hooks, and the relevant Linux subsystem for clocks, IRQs, PM, SMP, PCI, or media.

Risks: low-level register constants and legacy platform-data assumptions are hardware-specific. Errors may show up as missing devices, failed probes, or boot-time hangs rather than compile failures.

Test signals: compile with the owning config enabled, boot on matching DT/board files, and exercise the subsystem initialized by this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/mux.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/mux.h

Purpose: provides local declarations, constants, or register definitions for `mach-davinci` code in `mux.h`.

Important APIs/types/functions: the file defines macros, structure declarations, extern function prototypes, or register bit names consumed by sibling C/assembly files.

Control flow: header-only; control flow is in the including implementation files.

State and persistence: no independent state. Constants describe persistent hardware register layout or shared software contracts.

Dependencies and integration: included by platform init, PM, SMP, IRQ, PCIe, mux, or board glue in the same machine directory and sometimes by drivers using legacy platform data.

Risks: register offsets and bit masks are hardware ABI; mistakes compile cleanly but misprogram low-level SoC state. Prototype drift can hide integration errors across legacy board files.

Test signals: compile coverage of all including files, boot-time peripheral initialization, and targeted tests for the subsystem named by the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/mux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/pdata-quirks.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/pdata-quirks.c

Purpose: supplies legacy platform-data registration for DA850 boards still described by DT but requiring non-DT media subdevice details.

Important APIs/types/functions: `struct pdata_init`, TVP5146 and ADV7343 platform data, VPIF capture/display configs, `pdata_quirks_check()`, board-specific init functions, and `pdata_quirks_init()`.

Control flow: late init scans compatible strings such as `ti,da850-lcdk` and `ti,da850-evm`; matching entries register VPIF capture/display devices with board-specific subdevice and route data.

State and persistence: static platform data structures are handed to VPIF platform devices and persist for driver probing.

Dependencies and integration: integrates media I2C subdevices, VPIF platform APIs from `da850.c`, OF machine compatibility, and legacy board support.

Risks: this bridges old platform data into DT boot, so it can conflict with future full-DT descriptions if both instantiate devices. Shared static config is mutated for LCDK by reducing subdevice count.

Test signals: DA850 EVM/LCDK video capture/display probe, I2C subdevice detection at expected addresses, and absence of duplicate media device registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/pdata-quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/pm.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/pm.c

Purpose: implements Davinci suspend-to-RAM setup and entry using SRAM-resident assembly.

Important APIs/types/functions: `davinci_sram_suspend`, `pm_config`, `davinci_sram_push()`, `davinci_pm_suspend()`, `davinci_pm_enter()`, `davinci_pm_ops`, and `davinci_pm_init()`.

Control flow: init allocates SRAM, copies `davinci_cpu_suspend`, fills `davinci_pm_config` with DDR/PLL/deepsleep addresses, and registers suspend ops. Enter validates `PM_SUSPEND_MEM`, saves interrupt state, calls the SRAM suspend function, and restores state.

State and persistence: SRAM copy of suspend code and `pm_config` persist after init. Hardware state includes PLL, DDR2, and deepsleep registers manipulated during suspend.

Dependencies and integration: depends on `sram_alloc()`, `da8xx_get_mem_ctlr()`, assembly symbols from `sleep.S`, clock/PLL constants, and Linux suspend core.

Risks: failures to allocate SRAM or map DDR controller disable suspend. Assembly must run from SRAM while DDR/PLL state changes. Incorrect deepsleep count or PLL addresses can hang resume.

Test signals: suspend registration logs, SRAM allocation success, DA850 mem suspend/resume loops, and register tracing around DDR self-refresh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/pm.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/pm.h

Purpose: provides local declarations, constants, or register definitions for `mach-davinci` code in `pm.h`.

Important APIs/types/functions: the file defines macros, structure declarations, extern function prototypes, or register bit names consumed by sibling C/assembly files.

Control flow: header-only; control flow is in the including implementation files.

State and persistence: no independent state. Constants describe persistent hardware register layout or shared software contracts.

Dependencies and integration: included by platform init, PM, SMP, IRQ, PCIe, mux, or board glue in the same machine directory and sometimes by drivers using legacy platform data.

Risks: register offsets and bit masks are hardware ABI; mistakes compile cleanly but misprogram low-level SoC state. Prototype drift can hide integration errors across legacy board files.

Test signals: compile coverage of all including files, boot-time peripheral initialization, and targeted tests for the subsystem named by the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/pm_domain.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/pm_domain.c

Purpose: implements `mach-davinci` platform support in `pm_domain.c`.

Important APIs/types/functions: defines local init functions, platform data, register helpers, or machine descriptors used by the surrounding ARM machine family.

Control flow: called from machine init, board init, subsystem callbacks, or build-selected platform hooks; it configures hardware resources and hands them to generic Linux subsystems.

State and persistence: usually stores static descriptors, mapped register bases, platform devices, or hardware configuration that persists after boot.

Dependencies and integration: tied to sibling headers, Kconfig/Makefile selection, device-tree compatibles, ARM machine hooks, and the relevant Linux subsystem for clocks, IRQs, PM, SMP, PCI, or media.

Risks: low-level register constants and legacy platform-data assumptions are hardware-specific. Errors may show up as missing devices, failed probes, or boot-time hangs rather than compile failures.

Test signals: compile with the owning config enabled, boot on matching DT/board files, and exercise the subsystem initialized by this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/pm_domain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/psc.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/psc.h

Purpose: provides local declarations, constants, or register definitions for `mach-davinci` code in `psc.h`.

Important APIs/types/functions: the file defines macros, structure declarations, extern function prototypes, or register bit names consumed by sibling C/assembly files.

Control flow: header-only; control flow is in the including implementation files.

State and persistence: no independent state. Constants describe persistent hardware register layout or shared software contracts.

Dependencies and integration: included by platform init, PM, SMP, IRQ, PCIe, mux, or board glue in the same machine directory and sometimes by drivers using legacy platform data.

Risks: register offsets and bit masks are hardware ABI; mistakes compile cleanly but misprogram low-level SoC state. Prototype drift can hide integration errors across legacy board files.

Test signals: compile coverage of all including files, boot-time peripheral initialization, and targeted tests for the subsystem named by the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/psc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/sleep.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/sleep.S

Purpose: provides SRAM-executed Davinci CPU suspend and DDR PSC configuration assembly.

Important APIs/types/functions: exports `davinci_cpu_suspend`, `davinci_ddr_psc_config`, and `davinci_cpu_suspend_sz`; uses fields from `struct davinci_pm_config`.

Control flow: saves registers, programs DDR/PLL/deepsleep state, waits through fixed timing cycles, enters low-power state, and restores enough state for C resume. The DDR PSC helper manipulates power/sleep control sequences for memory.

State and persistence: executes from SRAM because DDR is placed into low-power/self-refresh state. It temporarily changes PLL, DDR2, and deepsleep controller registers.

Dependencies and integration: paired with `pm.c` copy/setup and `pm.h` structure layout; uses constants from Davinci clock and DDR definitions.

Risks: assembly timing loops depend on expected clock frequency and constants. Wrong struct layout or SRAM copy size can corrupt execution during suspend.

Test signals: link symbol size matches copied code, suspend/resume cycles, and DDR contents validation after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/sleep.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/sram.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/sram.c

Purpose: exposes Davinci SRAM allocation helpers backed by a `gen_pool`.

Important APIs/types/functions: `sram_get_gen_pool()`, exported `sram_alloc()`, exported `sram_free()`, and `sram_init()` core initcall.

Control flow: `sram_init()` locates an `mmio-sram` node, obtains its gen_pool, and caches it. Callers allocate/free SRAM regions and optionally receive DMA/physical addresses.

State and persistence: global `sram_pool` persists after core init; allocations remain until freed by callers.

Dependencies and integration: used by Davinci PM to copy suspend assembly; depends on OF platform SRAM provider and genalloc.

Risks: if SRAM provider probes too late or is absent, suspend allocation fails. Exported allocation helpers need callers to free with the same length.

Test signals: core init log absence of errors, `sram_alloc()` success in PM init, and gen_pool leak checks around users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/sram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/sram.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/sram.h

Purpose: provides local declarations, constants, or register definitions for `mach-davinci` code in `sram.h`.

Important APIs/types/functions: the file defines macros, structure declarations, extern function prototypes, or register bit names consumed by sibling C/assembly files.

Control flow: header-only; control flow is in the including implementation files.

State and persistence: no independent state. Constants describe persistent hardware register layout or shared software contracts.

Dependencies and integration: included by platform init, PM, SMP, IRQ, PCIe, mux, or board glue in the same machine directory and sometimes by drivers using legacy platform data.

Risks: register offsets and bit masks are hardware ABI; mistakes compile cleanly but misprogram low-level SoC state. Prototype drift can hide integration errors across legacy board files.

Test signals: compile coverage of all including files, boot-time peripheral initialization, and targeted tests for the subsystem named by the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-davinci/sram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-digicolor/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-digicolor/Kconfig

Purpose: defines the kernel configuration surface for the `mach-digicolor` ARM machine family.

Important APIs/types/functions: Kconfig symbols in this file select the architecture or board family, CPU class, device-tree support, timers, SMP/PM prerequisites, and related driver dependencies.

Control flow: there is no runtime control flow. During configuration, selected symbols determine which machine descriptors, board files, SMP code, and low-level helpers are compiled.

State and persistence: persists only as `.config` choices that affect the kernel image.

Dependencies and integration: integrates this machine family into the ARM multiplatform build, Makefile object selection, DT machine matching, and common subsystems such as irqchip, clocksource, SMP, PM, and pinctrl where selected.

Risks: incorrect selects can produce kernels that build but miss required runtime infrastructure, while overly broad selects keep obsolete board code enabled. Rename or dependency changes must stay synchronized with the local Makefile and DT compatibles.

Test signals: `olddefconfig`/`savedefconfig`, all relevant defconfig builds, and boot checks that the expected object files are linked for selected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-digicolor/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-digicolor/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-digicolor/Makefile

Purpose: maps `mach-digicolor` Kconfig symbols to the machine-family object files built into the ARM kernel.

Important APIs/types/functions: `obj-y` and `obj-$(CONFIG_...)` lines select machine descriptors, board files, SMP helpers, PM helpers, and assembly startup objects.

Control flow: build-time only. Kbuild evaluates configuration symbols and links the listed objects into `vmlinux`.

State and persistence: no runtime state; the persistent effect is the linked kernel object set.

Dependencies and integration: must stay synchronized with Kconfig symbols, source filenames, and machine/CPU method declarations.

Risks: missing object entries lead to unresolved symbols or non-booting platforms; stale entries break builds when configs are enabled.

Test signals: compile all configs touching `mach-digicolor`, verify expected objects in build logs, and boot platforms that require optional SMP/PM objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-digicolor/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-digicolor/digicolor.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-digicolor/digicolor.c

Purpose: registers the Conexant Digicolor flattened-device-tree machine descriptor.

Important APIs/types/functions: compatible table for `cnxt,cx92755` and `DT_MACHINE_START(DIGICOLOR, ...)`.

Control flow: ARM machine selection matches the DT root compatible and then relies on generic OF population and drivers.

State and persistence: no local mutable state beyond the machine descriptor.

Dependencies and integration: depends on the ARM DT machine framework and Kconfig/Makefile selection for `ARCH_DIGICOLOR`.

Risks: minimal code, but wrong compatible strings prevent boot-time machine match.

Test signals: Digicolor DT boot and successful platform driver population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-digicolor/digicolor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-dove/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-dove/Kconfig

Purpose: defines the kernel configuration surface for the `mach-dove` ARM machine family.

Important APIs/types/functions: Kconfig symbols in this file select the architecture or board family, CPU class, device-tree support, timers, SMP/PM prerequisites, and related driver dependencies.

Control flow: there is no runtime control flow. During configuration, selected symbols determine which machine descriptors, board files, SMP code, and low-level helpers are compiled.

State and persistence: persists only as `.config` choices that affect the kernel image.

Dependencies and integration: integrates this machine family into the ARM multiplatform build, Makefile object selection, DT machine matching, and common subsystems such as irqchip, clocksource, SMP, PM, and pinctrl where selected.

Risks: incorrect selects can produce kernels that build but miss required runtime infrastructure, while overly broad selects keep obsolete board code enabled. Rename or dependency changes must stay synchronized with the local Makefile and DT compatibles.

Test signals: `olddefconfig`/`savedefconfig`, all relevant defconfig builds, and boot checks that the expected object files are linked for selected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-dove/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-dove/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-dove/Makefile

Purpose: maps `mach-dove` Kconfig symbols to the machine-family object files built into the ARM kernel.

Important APIs/types/functions: `obj-y` and `obj-$(CONFIG_...)` lines select machine descriptors, board files, SMP helpers, PM helpers, and assembly startup objects.

Control flow: build-time only. Kbuild evaluates configuration symbols and links the listed objects into `vmlinux`.

State and persistence: no runtime state; the persistent effect is the linked kernel object set.

Dependencies and integration: must stay synchronized with Kconfig symbols, source filenames, and machine/CPU method declarations.

Risks: missing object entries lead to unresolved symbols or non-booting platforms; stale entries break builds when configs are enabled.

Test signals: compile all configs touching `mach-dove`, verify expected objects in build logs, and boot platforms that require optional SMP/PM objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-dove/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-dove/bridge-regs.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-dove/bridge-regs.h

Purpose: provides local declarations, constants, or register definitions for `mach-dove` code in `bridge-regs.h`.

Important APIs/types/functions: the file defines macros, structure declarations, extern function prototypes, or register bit names consumed by sibling C/assembly files.

Control flow: header-only; control flow is in the including implementation files.

State and persistence: no independent state. Constants describe persistent hardware register layout or shared software contracts.

Dependencies and integration: included by platform init, PM, SMP, IRQ, PCIe, mux, or board glue in the same machine directory and sometimes by drivers using legacy platform data.

Risks: register offsets and bit masks are hardware ABI; mistakes compile cleanly but misprogram low-level SoC state. Prototype drift can hide integration errors across legacy board files.

Test signals: compile coverage of all including files, boot-time peripheral initialization, and targeted tests for the subsystem named by the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-dove/bridge-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-dove/cm-a510.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-dove/cm-a510.c

Purpose: implements `mach-dove` platform support in `cm-a510.c`.

Important APIs/types/functions: defines local init functions, platform data, register helpers, or machine descriptors used by the surrounding ARM machine family.

Control flow: called from machine init, board init, subsystem callbacks, or build-selected platform hooks; it configures hardware resources and hands them to generic Linux subsystems.

State and persistence: usually stores static descriptors, mapped register bases, platform devices, or hardware configuration that persists after boot.

Dependencies and integration: tied to sibling headers, Kconfig/Makefile selection, device-tree compatibles, ARM machine hooks, and the relevant Linux subsystem for clocks, IRQs, PM, SMP, PCI, or media.

Risks: low-level register constants and legacy platform-data assumptions are hardware-specific. Errors may show up as missing devices, failed probes, or boot-time hangs rather than compile failures.

Test signals: compile with the owning config enabled, boot on matching DT/board files, and exercise the subsystem initialized by this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-dove/cm-a510.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-dove/common.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-dove/common.c

Purpose: implements legacy Marvell Dove SoC initialization: static IO maps, clock gates, Orion device registration, MBUS windows, PMU domains, timer, and restart.

Important APIs/types/functions: `dove_map_io()`, `dove_clk_init()`, many peripheral init wrappers (`dove_ehci*`, `dove_ge00_init()`, `dove_sata_init()`, UART/SPI/I2C/SDIO init), `dove_setup_cpu_wins()`, `dove_init()`, and `dove_restart()`.

Control flow: early init sets timer and MBUS base, timer init programs Orion timer with a fixed TCLK, and main init sets up cache, MBUS address windows, clock tree, PMU domains, RTC, and XOR engines. Board files call the peripheral wrappers for devices they populate.

State and persistence: static IO maps, clock registrations, MBUS windows, platform devices, and PMU domains persist for the boot lifetime.

Dependencies and integration: heavily integrates with Orion/plat helpers, Dove PMU, Marvell MBUS, clock framework, Tauros2 cache, and legacy board files.

Risks: fixed clock rate and static MBUS windows are legacy assumptions. Resource-window mistakes affect PCIe, crypto, bootrom, and scratchpad access. Restart spins forever after writing reset registers.

Test signals: Dove boot with expected TCLK log, peripheral driver probes, MBUS window dump, PMU domain registration, and reboot test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-dove/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-dove/common.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-dove/common.h

Purpose: provides local declarations, constants, or register definitions for `mach-dove` code in `common.h`.

Important APIs/types/functions: the file defines macros, structure declarations, extern function prototypes, or register bit names consumed by sibling C/assembly files.

Control flow: header-only; control flow is in the including implementation files.

State and persistence: no independent state. Constants describe persistent hardware register layout or shared software contracts.

Dependencies and integration: included by platform init, PM, SMP, IRQ, PCIe, mux, or board glue in the same machine directory and sometimes by drivers using legacy platform data.

Risks: register offsets and bit masks are hardware ABI; mistakes compile cleanly but misprogram low-level SoC state. Prototype drift can hide integration errors across legacy board files.

Test signals: compile coverage of all including files, boot-time peripheral initialization, and targeted tests for the subsystem named by the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-dove/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-dove/dove.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-dove/dove.h

Purpose: provides local declarations, constants, or register definitions for `mach-dove` code in `dove.h`.

Important APIs/types/functions: the file defines macros, structure declarations, extern function prototypes, or register bit names consumed by sibling C/assembly files.

Control flow: header-only; control flow is in the including implementation files.

State and persistence: no independent state. Constants describe persistent hardware register layout or shared software contracts.

Dependencies and integration: included by platform init, PM, SMP, IRQ, PCIe, mux, or board glue in the same machine directory and sometimes by drivers using legacy platform data.

Risks: register offsets and bit masks are hardware ABI; mistakes compile cleanly but misprogram low-level SoC state. Prototype drift can hide integration errors across legacy board files.

Test signals: compile coverage of all including files, boot-time peripheral initialization, and targeted tests for the subsystem named by the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-dove/dove.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-dove/irq.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-dove/irq.c

Purpose: implements `mach-dove` platform support in `irq.c`.

Important APIs/types/functions: defines local init functions, platform data, register helpers, or machine descriptors used by the surrounding ARM machine family.

Control flow: called from machine init, board init, subsystem callbacks, or build-selected platform hooks; it configures hardware resources and hands them to generic Linux subsystems.

State and persistence: usually stores static descriptors, mapped register bases, platform devices, or hardware configuration that persists after boot.

Dependencies and integration: tied to sibling headers, Kconfig/Makefile selection, device-tree compatibles, ARM machine hooks, and the relevant Linux subsystem for clocks, IRQs, PM, SMP, PCI, or media.

Risks: low-level register constants and legacy platform-data assumptions are hardware-specific. Errors may show up as missing devices, failed probes, or boot-time hangs rather than compile failures.

Test signals: compile with the owning config enabled, boot on matching DT/board files, and exercise the subsystem initialized by this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-dove/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-dove/irqs.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-dove/irqs.h

Purpose: provides local declarations, constants, or register definitions for `mach-dove` code in `irqs.h`.

Important APIs/types/functions: the file defines macros, structure declarations, extern function prototypes, or register bit names consumed by sibling C/assembly files.

Control flow: header-only; control flow is in the including implementation files.

State and persistence: no independent state. Constants describe persistent hardware register layout or shared software contracts.

Dependencies and integration: included by platform init, PM, SMP, IRQ, PCIe, mux, or board glue in the same machine directory and sometimes by drivers using legacy platform data.

Risks: register offsets and bit masks are hardware ABI; mistakes compile cleanly but misprogram low-level SoC state. Prototype drift can hide integration errors across legacy board files.

Test signals: compile coverage of all including files, boot-time peripheral initialization, and targeted tests for the subsystem named by the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-dove/irqs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-dove/mpp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-dove/mpp.c

Purpose: implements `mach-dove` platform support in `mpp.c`.

Important APIs/types/functions: defines local init functions, platform data, register helpers, or machine descriptors used by the surrounding ARM machine family.

Control flow: called from machine init, board init, subsystem callbacks, or build-selected platform hooks; it configures hardware resources and hands them to generic Linux subsystems.

State and persistence: usually stores static descriptors, mapped register bases, platform devices, or hardware configuration that persists after boot.

Dependencies and integration: tied to sibling headers, Kconfig/Makefile selection, device-tree compatibles, ARM machine hooks, and the relevant Linux subsystem for clocks, IRQs, PM, SMP, PCI, or media.

Risks: low-level register constants and legacy platform-data assumptions are hardware-specific. Errors may show up as missing devices, failed probes, or boot-time hangs rather than compile failures.

Test signals: compile with the owning config enabled, boot on matching DT/board files, and exercise the subsystem initialized by this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-dove/mpp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-dove/mpp.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-dove/mpp.h

Purpose: provides local declarations, constants, or register definitions for `mach-dove` code in `mpp.h`.

Important APIs/types/functions: the file defines macros, structure declarations, extern function prototypes, or register bit names consumed by sibling C/assembly files.

Control flow: header-only; control flow is in the including implementation files.

State and persistence: no independent state. Constants describe persistent hardware register layout or shared software contracts.

Dependencies and integration: included by platform init, PM, SMP, IRQ, PCIe, mux, or board glue in the same machine directory and sometimes by drivers using legacy platform data.

Risks: register offsets and bit masks are hardware ABI; mistakes compile cleanly but misprogram low-level SoC state. Prototype drift can hide integration errors across legacy board files.

Test signals: compile coverage of all including files, boot-time peripheral initialization, and targeted tests for the subsystem named by the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-dove/mpp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-dove/pcie.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-dove/pcie.c

Purpose: supplies legacy PCIe host-controller support for the two Marvell Dove PCIe ports.

Important APIs/types/functions: `struct pcie_port`, `dove_pcie_setup()`, config accessors `pcie_rd_conf()`/`pcie_wr_conf()`, root-complex fixup `rc_pci_fixup()`, `dove_pcie_scan_bus()`, `dove_pcie_map_irq()`, `add_pcie_port()`, and `dove_pcie_init()`.

Control flow: init checks each requested port's link status, enables its clock, records the base, and calls `pci_common_init()`. Setup assigns bus numbers, maps IO space, requests MEM windows, and adds resources. Config access is serialized per-port and rejects impossible local-bus device numbers.

State and persistence: `pcie_port[]`, `num_pcie_ports`, resource windows, enabled clocks, and `vga_base` persist for PCI core use.

Dependencies and integration: depends on Orion PCIe helpers, ARM legacy PCI APIs, Dove MBUS windows from `common.c`, clock lookup, and IRQ definitions.

Risks: panics if PCIe memory resource request fails. Link-down ports are ignored, changing controller numbering. Legacy PCI APIs and fixed windows complicate migration to DT PCIe.

Test signals: PCI enumeration on both ports, config-space read/write correctness, root-complex class fixup, IRQ routing, and link-down boot behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-dove/pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-dove/pm.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-dove/pm.h

Purpose: provides local declarations, constants, or register definitions for `mach-dove` code in `pm.h`.

Important APIs/types/functions: the file defines macros, structure declarations, extern function prototypes, or register bit names consumed by sibling C/assembly files.

Control flow: header-only; control flow is in the including implementation files.

State and persistence: no independent state. Constants describe persistent hardware register layout or shared software contracts.

Dependencies and integration: included by platform init, PM, SMP, IRQ, PCIe, mux, or board glue in the same machine directory and sometimes by drivers using legacy platform data.

Risks: register offsets and bit masks are hardware ABI; mistakes compile cleanly but misprogram low-level SoC state. Prototype drift can hide integration errors across legacy board files.

Test signals: compile coverage of all including files, boot-time peripheral initialization, and targeted tests for the subsystem named by the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-dove/pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-ep93xx/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-ep93xx/Kconfig

Purpose: defines the kernel configuration surface for the `mach-ep93xx` ARM machine family.

Important APIs/types/functions: Kconfig symbols in this file select the architecture or board family, CPU class, device-tree support, timers, SMP/PM prerequisites, and related driver dependencies.

Control flow: there is no runtime control flow. During configuration, selected symbols determine which machine descriptors, board files, SMP code, and low-level helpers are compiled.

State and persistence: persists only as `.config` choices that affect the kernel image.

Dependencies and integration: integrates this machine family into the ARM multiplatform build, Makefile object selection, DT machine matching, and common subsystems such as irqchip, clocksource, SMP, PM, and pinctrl where selected.

Risks: incorrect selects can produce kernels that build but miss required runtime infrastructure, while overly broad selects keep obsolete board code enabled. Rename or dependency changes must stay synchronized with the local Makefile and DT compatibles.

Test signals: `olddefconfig`/`savedefconfig`, all relevant defconfig builds, and boot checks that the expected object files are linked for selected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-ep93xx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-exynos/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-exynos/Kconfig

Purpose: defines the kernel configuration surface for the `mach-exynos` ARM machine family.

Important APIs/types/functions: Kconfig symbols in this file select the architecture or board family, CPU class, device-tree support, timers, SMP/PM prerequisites, and related driver dependencies.

Control flow: there is no runtime control flow. During configuration, selected symbols determine which machine descriptors, board files, SMP code, and low-level helpers are compiled.

State and persistence: persists only as `.config` choices that affect the kernel image.

Dependencies and integration: integrates this machine family into the ARM multiplatform build, Makefile object selection, DT machine matching, and common subsystems such as irqchip, clocksource, SMP, PM, and pinctrl where selected.

Risks: incorrect selects can produce kernels that build but miss required runtime infrastructure, while overly broad selects keep obsolete board code enabled. Rename or dependency changes must stay synchronized with the local Makefile and DT compatibles.

Test signals: `olddefconfig`/`savedefconfig`, all relevant defconfig builds, and boot checks that the expected object files are linked for selected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-exynos/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-exynos/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-exynos/Makefile

Purpose: maps `mach-exynos` Kconfig symbols to the machine-family object files built into the ARM kernel.

Important APIs/types/functions: `obj-y` and `obj-$(CONFIG_...)` lines select machine descriptors, board files, SMP helpers, PM helpers, and assembly startup objects.

Control flow: build-time only. Kbuild evaluates configuration symbols and links the listed objects into `vmlinux`.

State and persistence: no runtime state; the persistent effect is the linked kernel object set.

Dependencies and integration: must stay synchronized with Kconfig symbols, source filenames, and machine/CPU method declarations.

Risks: missing object entries lead to unresolved symbols or non-booting platforms; stale entries break builds when configs are enabled.

Test signals: compile all configs touching `mach-exynos`, verify expected objects in build logs, and boot platforms that require optional SMP/PM objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-exynos/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-exynos/common.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-exynos/common.h

Purpose: provides local declarations, constants, or register definitions for `mach-exynos` code in `common.h`.

Important APIs/types/functions: the file defines macros, structure declarations, extern function prototypes, or register bit names consumed by sibling C/assembly files.

Control flow: header-only; control flow is in the including implementation files.

State and persistence: no independent state. Constants describe persistent hardware register layout or shared software contracts.

Dependencies and integration: included by platform init, PM, SMP, IRQ, PCIe, mux, or board glue in the same machine directory and sometimes by drivers using legacy platform data.

Risks: register offsets and bit masks are hardware ABI; mistakes compile cleanly but misprogram low-level SoC state. Prototype drift can hide integration errors across legacy board files.

Test signals: compile coverage of all including files, boot-time peripheral initialization, and targeted tests for the subsystem named by the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-exynos/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-exynos/exynos-smc.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-exynos/exynos-smc.S

Purpose: provides the ARM assembly wrapper for Samsung Exynos secure monitor calls.

Important APIs/types/functions: exports `exynos_smc`, which executes the SMC instruction with arguments in ARM calling-convention registers and returns to the caller.

Control flow: C callers pass command and arguments; the wrapper issues the monitor call and returns after secure firmware completes.

State and persistence: no software state; secure firmware may mutate hardware state according to command.

Dependencies and integration: paired with Exynos SMC command definitions in `smc.h` and used by Exynos firmware, power, cache, and SMP code.

Risks: SMC ABI is firmware-specific and failures may not be expressible as normal Linux errors. Calling it without secure firmware support can trap or hang.

Test signals: Exynos boot under secure firmware, CPU power/suspend operations using SMC, and build coverage for ARM assembly exports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-exynos/exynos-smc.S -->
