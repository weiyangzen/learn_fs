# subset-b-000657 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/sharpsl_pm.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/sharpsl_pm.c

Purpose: platform driver for Sharp Zaurus SL-C7xx/SL-Cxx00 battery, charger, APM, and suspend behavior. It turns board-specific callbacks from `struct sharpsl_charger_machinfo` into a common charger state machine, battery status reporting, offline charging during suspend, and sysfs/APM visibility.

Important APIs/types/functions: exports global `sharpsl_pm`, `sharpsl_battery_kick()`, `sharpsl_pm_led()`, battery threshold tables, and `sharpsl_pm_pxa_read_max1111()`. Internal work/timer/IRQ paths include `sharpsl_battery_thread()`, `sharpsl_charge_toggle()`, `sharpsl_ac_timer()`, `sharpsl_chrg_full_timer()`, `sharpsl_fatal_isr()`, `corgi_pxa_pm_enter()`, and `sharpsl_off_charge_battery()`.

Control flow: probe stores board callbacks, registers LED trigger, requests AC/battery GPIOs, wires IRQs, creates battery sysfs attributes, installs APM and suspend ops, then starts an AC debounce timer. Runtime alternates delayed work for battery sampling with timers/IRQs for AC and full-charge changes. Suspend enters PXA sleep, optionally schedules RTC wakeups for offline charging, and loops until board wakeup logic permits resume.

State and persistence: state is in global `sharpsl_pm`, delayed work, two timers, APM hook state, LED trigger state, and hardware RTC/PXA power registers. It persists no disk data; it mutates charger GPIOs, discharge lines, RTC alarm, and reset-source registers.

Dependencies and integration points: depends on PXA PM/RTC registers, MAX1111 ADC, GPIO IRQs, APM emulation, LED triggers, platform device data from board files such as `spitz_pm.c`, and `pxa_pm_enter()`. LCD backlight callbacks influence battery percentage thresholds.

Risks: high hardware risk because timing constants, blocking `mdelay()` loops, and GPIO polarity directly control charging. IRQ request errors are logged but do not abort probe, leaving degraded operation possible. Global mutable state is lightly serialized, so suspend/work/timer interactions are subtle. Offline charger loops can hide wakeup bugs and battery thresholds are board-calibrated constants.

Test signals: best signals are boot/probe logs, sysfs `battery_percentage`/`battery_voltage`, APM status, charger LED behavior, AC insertion/removal IRQs, full-charge IRQs, suspend/resume with AC present, and low/fatal battery wake-suspend paths. Unit testing would need mocked machinfo callbacks and jiffies/timer control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/sharpsl_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/sharpsl_pm.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/sharpsl_pm.h

Purpose: shared contract between SharpSL board files and the common SharpSL power driver.

Important APIs/types/functions: defines `struct sharpsl_charger_machinfo` callback/data table, `struct battery_thresh`, `struct battery_stat`, `struct sharpsl_pm_status`, charger mode constants, PM flag bits, LED values, MAX1111 channel constants, global `sharpsl_pm`, threshold arrays, and prototypes for `sharpsl_battery_kick()`, `sharpsl_pm_led()`, and `sharpsl_pm_pxa_read_max1111()`.

Control flow: no executable flow; consumers fill `sharpsl_charger_machinfo`, pass it as platform data to the `sharpsl-pm` device, then the driver calls these hooks for charger, ADC, suspend, wake, and backlight decisions.

State and persistence: describes in-memory driver state, timers, flags, charger mode, charge start time, and last sampled battery fields. Persistent effects are indirect through hardware callbacks.

Dependencies and integration points: integrated by `sharpsl_pm.c` and model-specific files such as `spitz_pm.c`. The data IDs map the common driver to board-specific ADC/GPIO reads.

Risks: callback polarity and threshold mistakes can produce unsafe charger behavior. The global state export couples board code tightly to one device instance.

Test signals: compile coverage catches signature drift; runtime validation needs board callback tests for every `SHARPSL_*` data selector and threshold table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/sharpsl_pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/sleep.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/sleep.S

Purpose: low-level PXA25x/PXA27x/PXA3xx suspend entry routines that finish CPU sleep after C code has prepared the system.

Important APIs/types/functions: assembly entry points are `pxa3xx_finish_suspend`, `pxa27x_finish_suspend`, and `pxa25x_finish_suspend`. They use SMEMC and clock register constants such as `MDREFR`, `CCCR`, `CLKCFG`, and `UNCACHED_PHYS_0`.

Control flow: PXA3xx writes sleep mode to coprocessor p14 and spins. PXA27x/PXA25x prepare the requested PWRMODE, physical-zero pointer, SDRAM self-refresh bits, and reduced clock settings, then branch into common CPU suspend code that executes from safe memory while clocks and SDRAM behavior change.

State and persistence: mutates CPU power mode, clock configuration, and SDRAM refresh/self-refresh state. No durable persistence, but correctness preserves DRAM contents across suspend.

Dependencies and integration points: called by PXA PM code; depends on `smemc.h`, PXA register definitions, ARM assembler macros, and board suspend paths such as SharpSL.

Risks: wrong register values can hang resume or corrupt memory. Errata workarounds are timing/order sensitive and SoC-family conditional assembly must match the selected kernel.

Test signals: suspend/resume smoke tests on each PXA family, resume PC validation, DRAM stress after resume, and clock-rate validation around sleep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/sleep.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/smemc.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/smemc.c

Purpose: PXA3xx static memory controller syscore save/restore and a helper to decode memory clock divider.

Important APIs/types/functions: `pxa3xx_smemc_suspend()`, `pxa3xx_smemc_resume()`, `smemc_init()`, and exported `pxa3xx_smemc_get_memclkdiv()`. Static saved state includes `msc[]`, `sxcnfg`, `memclkcfg`, and `csadrcfg[]`.

Control flow: `subsys_initcall` registers syscore ops only on PXA3xx. Suspend snapshots selected SMEMC timing/address registers. Resume restores them in a fixed order. The divider helper reads `MEMCLKCFG`, masks the low two bits, and returns a table value.

State and persistence: volatile kernel globals hold register images across suspend. Hardware SMEMC state is restored after resume; no disk persistence.

Dependencies and integration points: depends on `cpu_is_pxa3xx()`, syscore infrastructure, raw MMIO helpers, and register addresses from `smemc.h`. Suspend assembly and memory-mapped peripheral users rely on these timings staying coherent.

Risks: saved register coverage is minimal and PXA3xx-specific. Incorrect resume order or missing registers can break external memory devices.

Test signals: PXA3xx suspend/resume with devices on static memory chip selects, clock divider readback, and boot logs confirming syscore registration only on supported CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/smemc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/smemc.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/smemc.h

Purpose: PXA static memory controller register map and bit definitions.

Important APIs/types/functions: defines physical bases `PXA2XX_SMEMC_BASE`, `PXA3XX_SMEMC_BASE`, virtual base `SMEMC_VIRT`, register macros for SDRAM, static memory, PCMCIA, synchronous memory, memory clock, and chip-select address registers, plus bit definitions such as `MECR_NOS`, `MDCNFG_DE*`, and `MDREFR_*`.

Control flow: no functions; included by low-level C and assembly that read/write SMEMC registers.

State and persistence: names MMIO registers whose contents determine memory timing, refresh, self-refresh, PCMCIA timings, and chip-select address layout.

Dependencies and integration points: used by `smemc.c`, `sleep.S`, board files that touch `MSC0`, and PXA map code that creates the fixed virtual mapping.

Risks: macro addresses are raw hardware ABI. Any mismatch between virtual mapping and macro definitions causes bad MMIO access. Assembly inclusion constrains syntax and type usage.

Test signals: compile tests for C and assembly users, boot memory controller access, and suspend/resume memory integrity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/smemc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/spitz.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/spitz.c

Purpose: board support for Sharp SL-C3000 Spitz, SL-C3100 Borzoi, and SL-C1000 Akita PXA27x PDAs. It declares fixed GPIO/pin mux, platform devices, software nodes, memory devices, and machine descriptors.

Important APIs/types/functions: key init routines include `spitz_init()`, `spitz_fixup()`, `spitz_spi_init()`, `spitz_scoop_init()`, `spitz_pcmcia_init()`, `spitz_mkp_init()`, `spitz_keys_init()`, `spitz_leds_init()`, `spitz_mmc_init()`, `spitz_uhc_init()`, `spitz_lcd_init()`, `spitz_nand_init()`, `spitz_nor_init()`, `spitz_i2c_init()`, and `spitz_audio_init()`. Machine descriptors are `MACHINE_START(SPITZ)`, `BORZOI`, and `AKITA`.

Control flow: boot fixup saves Sharp parameters and adds a 64 MiB memblock. Machine init registers software GPIO nodes, reset/poweroff handlers, applies PXA MFP config, registers UART defaults, then conditionally instantiates SPI, SCOOP GPIO expanders, matrix keypad, gpio-keys, gpio-leds, MMC, PCMCIA, USB host, LCD, NOR, NAND, I2C, audio, and regulator constraints.

State and persistence: defines platform resources, partition tables, OOB layout callbacks, regulator constraints, software node properties, and poweroff/restart hooks. It mutates PXA PM/PCFR/MSC0 registers and card-power GPIO/SCOOP state.

Dependencies and integration points: integrates PXA27x core, SCOOP, PCMCIA, matrix-keypad, gpio-keys, LEDs, PXA SPI, ADS7846, corgi LCD, MAX1111, MMC, OHCI, PXA framebuffer, SharpSL NAND, physmap NOR, I2C devices, regulators, audio, and `sharpsl_pm`.

Risks: legacy non-DT board file has many compile-time optional paths; missing driver configs silently become no-op init stubs. Akita-specific differences for second SCOOP, MAX7310, NAND OOB, and audio/LCD GPIOs are easy to regress. Power sequencing for shared CF/SD rails is timing-sensitive.

Test signals: boot on all three machine IDs, device enumeration, keypad matrix, suspend key, LED triggers, SPI touchscreen/LCD/ADC, MMC detect/write-protect, PCMCIA slot count, NAND OOB behavior, NOR partitions, USB host power, and restart/poweroff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/spitz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/spitz.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/spitz.h

Purpose: board constants for the Sharp Spitz/Borzoi/Akita family.

Important APIs/types/functions: defines SCOOP GPIO bases and bit masks, Akita I/O expander base, many PXA GPIO numbers for reset, keys, switches, SD, CF, USB, touchscreen, LCD, charge, battery, and MAX1111 chip select, plus `SPITZ_IRQ_GPIO_*` IRQ translations.

Control flow: no executable flow; board and PM files consume these constants to wire platform devices and callbacks.

State and persistence: constants describe fixed board wiring and initial/suspend SCOOP output states. They become persistent hardware behavior through GPIO and SCOOP register programming.

Dependencies and integration points: included by `spitz.c` and `spitz_pm.c`; depends on PXA GPIO-to-IRQ macros and the legacy Sharp SCOOP expander model.

Risks: wrong polarity or GPIO number maps a driver to the wrong physical signal, with especially high risk around charger, battery cover, card power, and reset lines.

Test signals: hardware pin validation, GPIO IRQ events, card power toggles, charger status, and board-variant checks for Akita versus Spitz/Borzoi expanders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/spitz.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/spitz_pm.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/spitz_pm.c

Purpose: model-specific SharpSL power-management data and GPIO callbacks for Spitz, Borzoi, and Akita.

Important APIs/types/functions: callbacks include `spitz_charger_init()`, `spitz_measure_temp()`, `spitz_charge()`, `spitz_discharge()`, `spitz_discharge1()`, `spitz_presuspend()`, `spitz_postsuspend()`, `spitz_should_wakeup()`, `spitz_charger_wakeup()`, and `spitzpm_read_devdata()`. It defines exported `spitz_pm_machinfo` and registers a `sharpsl-pm` platform device.

Control flow: module init allocates and registers `spitzpm_device` with `spitz_pm_machinfo`. The common PM driver calls this file to request GPIOs, toggle charge/discharge/temp-measure pins, configure wakeup edges before suspend, restore GPIO18 mux after resume, decide whether a wake should be honored, and read ADC/GPIO status selectors.

State and persistence: stores `spitz_last_ac_status` and original GPIO18 config. Mutates board GPIOs and PWER/PRER/PFER wake registers. No disk persistence.

Dependencies and integration points: depends on `spitz.h`, PXA registers, `sharpsl_pm.c`, MAX1111 ADC helper, GPIO APIs, and machine type checks.

Risks: charger thresholds and GPIO polarities are safety-critical. Wakeup policy depends on several raw PXA edge-detect bits and can either miss a real wake or resume spuriously. GPIO18 mux save/restore is fragile.

Test signals: AC/battery/fatal GPIO reads, ADC values for battery/temp/AC, charger LED/current flow, wake from On key/AC/SD/CF/lid, and suspend/resume GPIO mux restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/spitz_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/standby.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/standby.S

Purpose: low-level PXA CPU standby path and PXA3 DDR calibration sequence used while entering standby.

Important APIs/types/functions: assembly symbols include `pxa_cpu_standby`, `pm_enter_standby_start`, and `pm_enter_standby_end`. Register constants describe PXA3 DDR controller offsets and calibration bits.

Control flow: `pxa_cpu_standby` executes coprocessor power-mode setup and loops around standby. The standby block programs DDR calibration registers, waits for completion/low-power events, and marks a copyable code region via start/end labels.

State and persistence: mutates CPU power mode and DDR controller calibration/power state. The labeled region is copied/executed by PM code from a safe location.

Dependencies and integration points: used by PXA PM core for standby, with SMEMC/PXA3 memory-controller assumptions.

Risks: pure assembly hardware sequencing with busy waits; incorrect offsets or copy boundaries can deadlock low-power entry.

Test signals: standby entry/exit on PXA targets, DDR stability after wake, and disassembly/link checks for start/end region size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/standby.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/udc.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/udc.h

Purpose: tiny board-facing declaration for configuring the PXA2xx USB device controller.

Important APIs/types/functions: forward-facing API is `pxa_set_udc_info(struct pxa2xx_udc_mach_info *info)`.

Control flow: no local flow; board files call the setter to hand platform data to the UDC core.

State and persistence: no local state. Platform data influences UDC runtime wiring.

Dependencies and integration points: depends on `struct pxa2xx_udc_mach_info` from the PXA UDC platform data area and integrates board files with the USB gadget controller.

Risks: declaration-only header can drift if the core signature changes. Wrong platform data causes USB role/connect behavior failures.

Test signals: compile coverage and USB gadget enumeration on boards that call the setter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/udc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-qcom/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-qcom/Kconfig

Purpose: Kconfig entry for ARMv7 Qualcomm devicetree platforms and optional reserved SMEM behavior.

Important APIs/types/functions: `menuconfig ARCH_QCOM` selects GIC, AMBA, Qualcomm clocksource, ARM architected timer, pinctrl, and SCM when SMP is enabled. `ARCH_QCOM_RESERVE_SMEM` reserves 2 MiB at the start of RAM for shared memory.

Control flow: build-time configuration only; enabling `ARCH_QCOM` pulls platform support and allows the SMP code in this directory to build via Makefile.

State and persistence: no runtime state. The SMEM option affects early memory reservation policy elsewhere.

Dependencies and integration points: tied to `ARCH_MULTI_V7`, DT boot, Qualcomm SCM firmware calls, SMP bring-up, and shared-memory expectations for IPQ40xx/MSM8x60/MSM8960.

Risks: selecting SCM only under SMP means non-SMP builds avoid that dependency. Misuse of the SMEM reservation can hide usable RAM or corrupt firmware-owned memory.

Test signals: Kconfig dependency resolution for ARMv7 multi-platform builds and boot tests on Qualcomm DT systems with and without SMEM reservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-qcom/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-qcom/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-qcom/Makefile

Purpose: build rule for Qualcomm ARM machine support.

Important APIs/types/functions: adds `platsmp.o` only when `CONFIG_SMP` is enabled.

Control flow: make-time object selection; no runtime flow.

State and persistence: none.

Dependencies and integration points: couples Qualcomm ARM support to the generic ARM SMP framework and Kconfig `CONFIG_SMP`.

Risks: non-SMP Qualcomm builds omit all code in this directory, so any future non-SMP machine hooks would need Makefile changes.

Test signals: build matrix with `ARCH_QCOM=y` and SMP on/off, confirming object inclusion matches expected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-qcom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-qcom/platsmp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-qcom/platsmp.c

Purpose: Qualcomm ARM secondary CPU bring-up and CPU hotplug support for several legacy enable-methods.

Important APIs/types/functions: release routines are `scss_release_secondary()`, `cortex_a7_release_secondary()`, `kpssv1_release_secondary()`, and `kpssv2_release_secondary()`. Boot wrappers call `qcom_boot_secondary()`. `qcom_smp_prepare_cpus()` programs the cold boot address through `qcom_scm_set_cold_boot_addr(secondary_startup_arm)`. `CPU_METHOD_OF_DECLARE` registers DT enable methods.

Control flow: prepare-cpus asks secure firmware to set the secondary boot vector and disables present CPUs if that fails. Per-CPU boot performs a one-time power/reset sequence using DT phandles to ACC/SAW/L2 nodes, records `cold_boot_done`, then sends a wakeup IPI. Hotplug `qcom_cpu_die()` waits in WFI.

State and persistence: per-CPU `cold_boot_done` avoids repeating cold release. Hardware state is in ACC, SAW, GCC, and power-gate registers.

Dependencies and integration points: depends on DT CPU nodes, Qualcomm SCM firmware, MMIO mapping, ARM SMP ops, and power/reset register layouts for MSM8660, Cortex-A7, KPSS v1, and KPSS v2.

Risks: power sequences are SoC-specific and delay/barrier sensitive. Missing DT phandles disable CPU bring-up. SCM failure disables SMP entirely. CPU hotplug only idles, so platform power-down is limited.

Test signals: secondary CPU online for each compatible string, SCM failure path, DT phandle validation, CPU hotplug WFI path, and stress with repeated CPU onlining.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-qcom/platsmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-realtek/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-realtek/Kconfig

Purpose: Kconfig entry for Realtek RTD1195 ARM SoC support.

Important APIs/types/functions: `menuconfig ARCH_REALTEK` depends on `ARCH_MULTI_V7` and selects GIC, ARM global timer, global timer sched clock, generic IRQ chip, and reset controller.

Control flow: build-time platform selection only.

State and persistence: none locally; selected timer/IRQ/reset infrastructure affects runtime platform initialization.

Dependencies and integration points: enables `rtd1195.o` through the directory Makefile and supports DT machine matching in `rtd1195.c`.

Risks: broad selections must match SoC hardware; missing reset/timer/GIC dependencies would break early boot.

Test signals: ARM multi-v7 configuration builds and RTD1195 DT boot with timer and IRQ setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-realtek/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-realtek/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-realtek/Makefile

Purpose: unconditional object list for Realtek machine support once the directory is selected.

Important APIs/types/functions: builds `rtd1195.o`.

Control flow: make-time object inclusion only.

State and persistence: none.

Dependencies and integration points: links the RTD1195 `DT_MACHINE_START` descriptor into ARM machine discovery.

Risks: any future Realtek SoC support needs explicit object additions; current file assumes the directory is only entered for relevant configs.

Test signals: build with `ARCH_REALTEK=y` and verify `rtd1195` machine descriptor is linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-realtek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-realtek/rtd1195.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-realtek/rtd1195.c

Purpose: DT machine descriptor and early memory reservation for Realtek RTD1195.

Important APIs/types/functions: `rtd1195_memblock_remove()` wraps `memblock_remove()` with error logging. `rtd1195_reserve()` removes boot ROM and peripheral register windows from RAM. `DT_MACHINE_START(rtd1195)` binds compatible `realtek,rtd1195`.

Control flow: during early machine reservation, it excludes `0x00000000..0x0000a800`, `0x18000000..0x18070000`, and `0x18100000..0x19100000` from the memblock allocator. The machine descriptor also disables L2C aux bits by setting val 0 and mask all ones.

State and persistence: mutates early memblock state, preventing kernel allocation from firmware/peripheral regions. No persistent storage.

Dependencies and integration points: integrates ARM DT machine selection, memblock allocator, and Realtek SoC memory map.

Risks: wrong ranges either waste RAM or allow the kernel to allocate over MMIO/ROM, causing hard-to-debug crashes. Error logging does not abort boot.

Test signals: early boot memory map, `/proc/iomem`, memblock debug output, and RTD1195 board boot stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-realtek/rtd1195.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/Kconfig

Purpose: Kconfig entry for Rockchip RK2928/RK3xxx ARMv7 SoCs.

Important APIs/types/functions: `ARCH_ROCKCHIP` depends on `ARCH_MULTI_V7` and selects pinctrl, reset controller, AMBA, GIC, L2X0, gpiolib, architected timer, SCU/TWD when SMP, DW APB timer, regulators, Rockchip timer, global timer sched clock, DMA zone for LPAE, and PM.

Control flow: build-time dependency selection; enables machine, PM, and SMP objects through Makefile.

State and persistence: none locally, but selected subsystems define early boot, interrupt, timer, pin, and suspend behavior.

Dependencies and integration points: targets DT-based Rockchip boards and supports `rockchip.c`, `platsmp.c`, and PM sleep code.

Risks: forced `PM` selection means suspend code is expected for this platform. Legacy ARM32 Rockchip support relies on many common subsystems being present.

Test signals: multi-v7 builds, DT boot for supported compatibles, SMP on A9/non-A9 variants, and suspend config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/Makefile

Purpose: object selection for Rockchip ARM machine support.

Important APIs/types/functions: forces `platsmp.o` to compile as ARMv7-A, builds `rockchip.o` under `CONFIG_ARCH_ROCKCHIP`, `pm.o sleep.o` under `CONFIG_PM_SLEEP`, and `headsmp.o platsmp.o` under `CONFIG_SMP`.

Control flow: make-time object inclusion only.

State and persistence: none.

Dependencies and integration points: links machine descriptor, suspend resume assembly, and SMP trampoline based on kernel config.

Risks: `platsmp.o` architecture flags must remain compatible with the assembly/register usage. PM sleep symbols are absent if `CONFIG_PM_SLEEP` is off, so callers use stubs.

Test signals: build matrix for Rockchip with SMP and PM_SLEEP combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/core.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/core.h

Purpose: shared declarations for Rockchip secondary CPU trampoline code.

Important APIs/types/functions: declares `rockchip_secondary_trampoline`, `rockchip_secondary_trampoline_end`, and mutable `rockchip_boot_fn`.

Control flow: no code; `platsmp.c` copies the trampoline range to SRAM and writes `rockchip_boot_fn` with the physical `secondary_startup` address.

State and persistence: `rockchip_boot_fn` is a word embedded in assembly and patched before copying to SRAM.

Dependencies and integration points: bridges `headsmp.S` and `platsmp.c`.

Risks: symbol range arithmetic and physical address patching must match assembly layout exactly.

Test signals: SMP boot on A9 Rockchip, objdump symbol order, and SRAM copy size validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/headsmp.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/headsmp.S

Purpose: minimal secondary CPU trampoline copied into Rockchip SRAM.

Important APIs/types/functions: defines `rockchip_secondary_trampoline`, global `rockchip_boot_fn`, and `rockchip_secondary_trampoline_end`.

Control flow: the trampoline loads the PC from the embedded boot-function word, causing a released secondary CPU to branch to `secondary_startup`.

State and persistence: `rockchip_boot_fn` storage is patched by C before the code is copied to SRAM.

Dependencies and integration points: consumed by `rockchip_smp_prepare_sram()` in `platsmp.c`.

Risks: alignment and range boundaries matter because code is copied as raw bytes. A bad physical address prevents secondary CPU boot.

Test signals: secondary CPU online, trampoline size check against SRAM reservation, and cache clean after copy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/headsmp.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/platsmp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/platsmp.c

Purpose: Rockchip ARM SMP bring-up and CPU hotplug support.

Important APIs/types/functions: key routines are `rockchip_smp_prepare_cpus()`, `rk3036_smp_prepare_cpus()`, `rockchip_boot_secondary()`, `rockchip_smp_prepare_sram()`, `rockchip_smp_prepare_pmu()`, `pmu_set_power_domain()`, `rockchip_get_core_reset()`, `rockchip_cpu_kill()`, and `rockchip_cpu_die()`. Registers CPU methods for `rockchip,rk3036-smp` and `rockchip,rk3066-smp`.

Control flow: prepare maps SRAM, locates PMU regmap when present, enables SCU on Cortex-A9 or counts cores from L2CTLR otherwise, powers down nonboot cores, and copies the trampoline into SRAM for A9. Booting a CPU powers its domain, then either relies on SRAM trampoline or writes BootROM mailbox values and sends `sev`.

State and persistence: global PMU/SRAM/SCU mappings, `ncores`, and `has_pmu` hold platform state. Hardware power domains and reset lines are mutated.

Dependencies and integration points: depends on DT nodes for SRAM, PMU, SCU, CPU resets, syscon regmaps, ARM SCU/cache helpers, reset controller, and generic SMP.

Risks: some error paths leak mappings or leave partial state but happen at init. Busy-wait power-domain polling has no timeout. A typo-like mailbox value `0xDEADBEAF` is hardware ABI. Reset controls are optional for Cortex-A9 but mandatory for other cores.

Test signals: CPU online/hotplug on rk3036 and rk3066/rk3188 families, DT missing-node failures, PMU power-domain status, and cache/SRAM trampoline validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/platsmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/pm.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/pm.c

Purpose: Rockchip RK3288 suspend-to-RAM setup, low-power mode programming, and resume boot data preparation.

Important APIs/types/functions: defines `struct rockchip_pm_data`, `rk3288_suspend_init()`, `rockchip_suspend_init()`, `rk3288_suspend_enter()`, `rk3288_suspend_prepare()`, `rk3288_suspend_finish()`, `rk3288_slp_mode_set()`, `rk3288_slp_mode_set_resume()`, `rockchip_lpmode_enter()`, `rk3288_config_bootdata()`, and suspend ops `rk3288_suspend_ops`.

Control flow: init finds PMU-compatible data, maps boot SRAM, obtains PMU/SGRF/GRF regmaps, copies `rockchip_slp_cpu_resume` into boot RAM, configures resume boot data, and installs suspend ops. Suspend prepare programs low-power mode registers; enter calls `cpu_suspend()` with `rockchip_lpmode_enter()`, which flushes caches and executes WFI; finish restores saved PMU/SGRF settings.

State and persistence: globals cache boot RAM mapping/physical address, regmaps, and saved PMU/SGRF register values. It writes fast-boot address, wakeup sources, oscillator/PLL counters, SIDDQ USB PHY bits, and power-mode controls.

Dependencies and integration points: depends on DT PMU node, syscon regmaps, SRAM region, assembly resume code in `sleep.S`, ARM `cpu_suspend`, regulator suspend framework, and `rockchip.c` machine init.

Risks: suspend register sequences are SoC-specific and can break resume. Boot RAM copy and physical address must be correct. USB PHY SIDDQ manipulation and oscillator disable decisions have board-level side effects.

Test signals: RK3288 suspend/resume, wake from GPIO/ARM interrupt, boot RAM code checksum/size, regulator suspend integration, and register restore checks after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/pm.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/pm.h

Purpose: Rockchip PM declarations and RK3288 PMU/SGRF register constants shared by C and assembly-adjacent code.

Important APIs/types/functions: declares `rockchip_slp_cpu_resume()` and `rockchip_suspend_init()` when `CONFIG_PM_SLEEP` is enabled, otherwise provides a stub. Defines RK3288 PMU wake/power/count registers, SGRF fast boot and watchdog gate bits, CPU debug bits, and wakeup enable masks.

Control flow: no runtime flow except the inline stub controlling whether `rockchip.c` calls real suspend setup.

State and persistence: constants address hardware PM registers whose contents persist across low-power entry until restored.

Dependencies and integration points: included by `pm.c`, `rockchip.c`, and resume assembly declarations.

Risks: write-mask bit definitions are easy to misuse; bad constants can prevent resume or leave watchdog/debug gates altered.

Test signals: compile with/without PM_SLEEP, suspend register programming tests, and resume path symbol linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/rockchip.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/rockchip.c

Purpose: Rockchip DT machine descriptor and early timer/suspend initialization.

Important APIs/types/functions: `rockchip_timer_init()`, `rockchip_dt_init()`, compatible table for RK2928/RK3066/RK3188/RK3228/RK3288/RV1108, and `DT_MACHINE_START(ROCKCHIP_DT)`.

Control flow: timer init special-cases RK3288 by mapping timer6/7 and enabling timer7 for the architected timer before calling `of_clk_init()` and `timer_probe()`. Machine init calls `rockchip_suspend_init()`.

State and persistence: temporarily maps timer registers and writes timer count/control values. No long-lived local state.

Dependencies and integration points: integrates common clock/timer DT probing, RK3288 bootloader workaround, and PM initialization.

Risks: fixed RK3288 physical timer address must be valid. If mapping fails, boot continues with an error and architected timer may not work.

Test signals: early clocksource availability, RK3288 timer workaround logs, DT compatible matching, and suspend ops registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/rockchip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/sleep.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/sleep.S

Purpose: Rockchip resume trampoline copied to SRAM for system suspend resume.

Important APIs/types/functions: `rockchip_slp_cpu_resume` is the executable resume entry; boot data globals include `rkpm_bootdata_l2ctlr_f`, `rkpm_bootdata_l2ctlr`, `rkpm_bootdata_cpusp`, `rkpm_bootdata_cpu_code`, and `rk3288_bootram_sz`.

Control flow: on resume it switches to SVC with interrupts/FIQs disabled, lets only CPU0 continue, optionally restores L2CTLR, loads saved stack pointer and CPU resume function pointer, then branches back into kernel resume code. Nonzero CPUs loop in WFE.

State and persistence: boot data words are filled by `pm.c` before suspend and consumed after resume from SRAM.

Dependencies and integration points: copied by RK3288 PM initialization and used by `cpu_suspend()` resume path.

Risks: incorrect boot data or SRAM copy causes resume hang. Only CPU0 resume is supported here; secondary CPUs must be re-managed elsewhere.

Test signals: RK3288 suspend/resume, L2CTLR restore validation, and bootram size consistency with copied code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/sleep.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/Kconfig

Purpose: Kconfig entry for Acorn RiscPC support.

Important APIs/types/functions: `ARCH_RPC` depends on ARMv4 multi-platform constraints, GCC version range, little endian, ATAGS, and MMU. It selects Acorn architecture support, PC FDC possibility, SA110 CPU, FIQ, PATA platform, ISA DMA API, legacy timer tick, machine I/O and memory headers, and no generic ioport mapping.

Control flow: build-time gating only.

State and persistence: none locally.

Dependencies and integration points: enables the legacy RiscPC machine files, IOMD IRQ/DMA, ecard bus, and ATAGS boot path.

Risks: explicit compiler constraints and deprecated ARMv4 assumptions make this fragile in modern toolchains. Lack of DT support means boot path is legacy.

Test signals: GCC 6-8 build, ATAGS boot on RiscPC, and compile rejection under unsupported compiler/architecture combos.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/Makefile

Purpose: object list for Acorn RiscPC machine support.

Important APIs/types/functions: builds `dma.o`, `ecard.o`, `ecard-loader.o`, `fiq.o`, `floppydma.o`, `io-acorn.o`, `irq.o`, `riscpc.o`, and `time.o`.

Control flow: make-time object inclusion only.

State and persistence: none.

Dependencies and integration points: links the platform's DMA, expansion-card bus, FIQ handlers, I/O helpers, interrupt controller, machine descriptor, and timer setup.

Risks: all objects are mandatory, so missing legacy interfaces break the platform build.

Test signals: full `ARCH_RPC` build and link symbol coverage for FIQ/DMA/ecard helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/dma.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/dma.c

Purpose: RiscPC DMA implementation for IOMD channels, floppy FIQ DMA, and virtual sound DMA.

Important APIs/types/functions: defines `struct iomd_dma`, `iomd_get_next_sg()`, `iomd_dma_handle()`, `iomd_request_dma()`, `iomd_enable_dma()`, `iomd_disable_dma()`, `iomd_set_dma_speed()`, floppy FIQ operations, and `rpc_dma_init()`.

Control flow: init resets IOMD DMA control registers, sets timing/extension registers, attaches DMA ops to six IOMD channels, and registers virtual floppy/sound channels. Enabling an invalid channel maps ISA-style buffers if needed, initializes scatterlist state, clears the controller, then enables interrupts. The IRQ handler ping-pongs A/B DMA descriptors until end flags stop transfer. Floppy DMA claims FIQ and installs input/output assembly handlers.

State and persistence: per-channel `iomd_dma` holds current SG address/length and state. Hardware IOMD DMA registers and FIQ handler/registers are mutated.

Dependencies and integration points: integrates ISA DMA API, IOMD registers, ARM FIQ framework, `floppydma.S`, and legacy drivers expecting ISA-like DMA.

Risks: cache-coherence fallback mapping lacks visible unmap in this file. Descriptor boundary math is page/transfer-size sensitive. FIQ claim failure leaves floppy DMA inactive. Interrupt disable state must match hardware A/B state.

Test signals: ISA DMA channel registration, floppy read/write using FIQ, podule DMA, sound virtual DMA clients, residue reporting, and DMA speed register values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/ecard-loader.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/ecard-loader.S

Purpose: assembly helpers that execute expansion-card loader bytecode in a RISC OS-like environment.

Important APIs/types/functions: provides `ecard_loader_reset()` and `ecard_loader_read()` called from `ecard.c`.

Control flow: the helpers set up expected register state, call into card-supplied loader code, and return reset/read results to the kernel ecard daemon.

State and persistence: mutates CPU registers and executes untrusted firmware-provided code; no kernel data persistence except returned values.

Dependencies and integration points: called only from the `kecardd` context after page-table mappings are prepared by `ecard_init_pgtables()`.

Risks: this deliberately trusts expansion-card loader code and runs it with kernel privilege. Calling convention and mapped virtual addresses must match old RISC OS assumptions.

Test signals: card chunk reads that require loaders, reset-on-shutdown behavior, and regression tests with cards on the quirk/loader paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/ecard-loader.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/ecard.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/ecard.c

Purpose: Acorn expansion-card bus implementation. It probes podule slots, reads card IDs/chunk directories, provides card resources, dispatches expansion-card interrupts, exposes sysfs/proc data, and implements ecard driver binding.

Important APIs/types/functions: public APIs include `ecard_readchunk()`, `ecard_request_resources()`, `ecard_release_resources()`, `ecard_setirq()`, `ecardm_iomap()`, `ecard_register_driver()`, `ecard_remove_driver()`, and `ecard_bus_type`. Core internals include `ecard_task()`, `ecard_readbytes()`, `ecard_probe()`, `ecard_irq_handler()`, `__ecard_address()`, and ecard bus probe/remove/shutdown methods.

Control flow: `postcore_initcall` registers the bus; `subsys_initcall` allocates IRQ descriptors, starts `kecardd`, probes slots 0-7 as EASI then IOC, probes network slot 8, installs a chained IRQ handler, and creates `/proc/bus/ecard/devices`. Loader-dependent reads are marshalled to `kecardd`, whose custom mm maps legacy I/O windows. Drivers match by manufacturer/product or simple ID, claim the card, request resources, and install IRQ ops.

State and persistence: global card linked list, slot map, ECTCR speed state, proc entry, per-card resources/sysfs attributes, loader buffers, and claimed/ops state. Hardware interrupt and address windows are configured; nothing persists across reboot.

Dependencies and integration points: depends on IOMD, IRQ core, driver core bus APIs, procfs, ARM MM/TLB helpers, ecard assembly loader, and RiscPC memory map.

Risks: explicitly trusts card vendor loader code. Interrupt lockup detection masks the parent interrupt after repeated unrecognized events. Probe/register error path can free cards after partial setup. Slot 8 has special indexed access state. Resource ownership and driver claimed state must stay paired.

Test signals: card detection in proc/sysfs, driver match/probe/remove/shutdown, loader chunk descriptions, EASI/IOC resource mapping, shared backplane interrupt dispatch, and lockup diagnostics with bad IRQ sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/ecard.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/ecard.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/ecard.h

Purpose: local helper definitions for RiscPC expansion-card chunk directory parsing.

Important APIs/types/functions: defines chunk directory layouts and helper macros/functions used by `ecard.c` to interpret IDs, start offsets, lengths, loader chunks, and strings.

Control flow: no standalone flow; parsing helpers are used while walking card ROM chunk directories in `ecard_readchunk()`.

State and persistence: no state, but structures map bytes read from card ROM into kernel interpretation.

Dependencies and integration points: private to ecard implementation and card loader code.

Risks: packed/byte-level interpretation must match Acorn card ROM format. Length/offset mistakes can cause out-of-range reads or wrong card identity.

Test signals: card description lookup, loader chunk loading, and known ROM image parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/ecard.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/fiq.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/fiq.S

Purpose: default RiscPC FIQ handler stub.

Important APIs/types/functions: defines `rpc_default_fiq_start` as the platform default FIQ entry.

Control flow: minimal assembly path for FIQ handling before another handler, such as floppy DMA, is installed.

State and persistence: affects CPU exception handling only through installed FIQ vector code.

Dependencies and integration points: linked by RiscPC FIQ setup and ARM FIQ framework.

Risks: a bad default FIQ path can lock the machine during unexpected fast interrupts.

Test signals: boot with no claimed FIQ users and floppy FIQ handler replacement/restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/fiq.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/floppydma.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/floppydma.S

Purpose: fast interrupt DMA copy routines for the RiscPC floppy controller.

Important APIs/types/functions: exposes input and output handler ranges such as `floppy_fiqin_start/end` and `floppy_fiqout_start/end` consumed by `dma.c`.

Control flow: FIQ handler copies data between floppy hardware FIFO and memory, updates the byte count register saved in FIQ regs, and returns quickly to minimize latency.

State and persistence: uses FIQ registers set by `floppy_enable_dma()` for count, buffer pointer, and controller base. No durable state.

Dependencies and integration points: installed via ARM FIQ framework by `dma.c` for virtual floppy DMA.

Risks: assembly must be reentrant only as FIQ context expects; wrong register convention corrupts transfer state. Buffer bounds rely on count from higher layers.

Test signals: floppy read/write data integrity, residue count, and FIQ claim/release behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/floppydma.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/include/mach/acornfb.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/include/mach/acornfb.h

Purpose: RiscPC framebuffer platform definitions for Acorn video modes, memory, and monitor configuration.

Important APIs/types/functions: declares/defines Acorn framebuffer data structures and constants used by the Acorn framebuffer driver and machine setup to describe VRAM, default modes, sync/timing, and monitor type.

Control flow: no executable flow; it is a platform ABI header for framebuffer setup.

State and persistence: structures describe boot-time framebuffer configuration and video memory layout.

Dependencies and integration points: consumed by RiscPC machine code and the `acornfb` driver.

Risks: stale mode/timing values can produce unusable display output. Header is platform-specific and not DT-discoverable.

Test signals: framebuffer probe, correct video mode selection, VRAM mapping, and console output on RiscPC displays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/include/mach/acornfb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/include/mach/hardware.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/include/mach/hardware.h

Purpose: central RiscPC physical/virtual hardware address map.

Important APIs/types/functions: defines I/O base/window constants for IOMD, IOC, EASI, MEMC, podule slots, network slot, and related platform address conversion values.

Control flow: no functions; address constants drive MMIO mappings and resource declarations.

State and persistence: constants define how kernel code sees fixed RiscPC hardware windows.

Dependencies and integration points: included by DMA, ecard, IRQ, I/O, and machine setup code, plus mach headers.

Risks: incorrect addresses break virtually every platform driver. These constants must match `io-acorn.S` and machine map descriptors.

Test signals: early boot I/O access, ecard resource ranges, IOMD IRQ/DMA operation, and `/proc/iomem`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/include/mach/hardware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/include/mach/io.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/include/mach/io.h

Purpose: RiscPC machine-specific I/O access translation declarations.

Important APIs/types/functions: provides macros/prototypes needed because `ARCH_RPC` selects `NEED_MACH_IO_H` and `NO_IOPORT_MAP`.

Control flow: no standalone runtime flow; generic I/O helpers include this when mapping port I/O to platform-specific address spaces.

State and persistence: no state; defines address translation behavior.

Dependencies and integration points: tied to `io-acorn.S`, legacy ISA/podule I/O, and drivers using inb/outb-style accesses.

Risks: wrong translation corrupts MMIO access or makes ISA-style drivers unusable.

Test signals: serial/IDE/parallel or podule drivers using port I/O and build coverage for `NEED_MACH_IO_H`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/include/mach/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/include/mach/irqs.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/include/mach/irqs.h

Purpose: RiscPC IRQ and FIQ numbering definitions.

Important APIs/types/functions: defines platform IRQ numbers for IOMD devices, expansion cards, timers, DMA, serial, and FIQ sources, plus board IRQ ranges.

Control flow: no local flow; constants are consumed by IRQ setup, DMA, ecard, and machine devices.

State and persistence: no state; constants encode interrupt wiring.

Dependencies and integration points: included by `irq.c`, `dma.c`, `ecard.c`, and device setup.

Risks: numbering must match the IRQ controller priority tables and generic IRQ descriptors. Wrong constants route interrupts to the wrong handlers.

Test signals: interrupt delivery for timer, DMA, expansion cards, keyboard/mouse, serial, and floppy FIQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/include/mach/irqs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/include/mach/isa-dma.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/include/mach/isa-dma.h

Purpose: RiscPC ISA DMA channel definitions.

Important APIs/types/functions: defines DMA channel identifiers and platform-specific ISA DMA constraints used by `dma.c` and legacy drivers.

Control flow: no executable flow.

State and persistence: no state; constants describe available DMA resources.

Dependencies and integration points: required because `ARCH_RPC` selects `ISA_DMA_API`; integrates IOMD and virtual floppy/sound DMA channels with generic ISA DMA users.

Risks: channel numbering mismatch breaks driver DMA requests.

Test signals: ISA DMA registration logs and drivers requesting floppy, podule, or sound DMA channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/include/mach/isa-dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/include/mach/memory.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/include/mach/memory.h

Purpose: RiscPC machine memory layout definitions.

Important APIs/types/functions: provides platform memory offset/limits required by `NEED_MACH_MEMORY_H`, including the physical memory layout expected by the SA110 RiscPC port.

Control flow: no runtime flow.

State and persistence: constants affect early memory mapping and address translation.

Dependencies and integration points: used by ARM memory initialization and RiscPC machine setup.

Risks: wrong physical offset or memory constants prevent boot or corrupt memory mapping.

Test signals: early boot memory detection, memblock layout, and successful userspace memory stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/include/mach/memory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/include/mach/uncompress.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/include/mach/uncompress.h

Purpose: early decompressor output support for RiscPC.

Important APIs/types/functions: implements low-level `putc`/flush helpers and UART/IOMD access assumptions used before the kernel proper is running.

Control flow: decompressor calls these helpers to emit early boot text such as uncompressing messages.

State and persistence: writes directly to early serial/display hardware; no lasting state beyond device output.

Dependencies and integration points: used by ARM compressed boot path when `ARCH_RPC` is selected and depends on bootloader-initialized low-level port state.

Risks: early MMIO assumptions must be valid before normal mappings. Bad polling can hang decompression.

Test signals: visible early boot output and no decompressor hangs with low-level debug enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/include/mach/uncompress.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/io-acorn.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/io-acorn.S

Purpose: assembly I/O access routines for Acorn/RiscPC legacy port space.

Important APIs/types/functions: provides low-level byte/word/long I/O primitives used by the ARM port I/O layer for this machine.

Control flow: callers enter small assembly routines that translate legacy I/O port operations to the RiscPC I/O windows and perform the access.

State and persistence: mutates only target hardware registers.

Dependencies and integration points: paired with `mach/io.h` and `hardware.h`; used by drivers that expect traditional port I/O.

Risks: assembly address translation must match the machine map; bad ordering/width handling can break legacy devices.

Test signals: podule/ISA-style device access, IDE/serial/parallel operations, and build/link coverage for I/O symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/io-acorn.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/irq.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/irq.c

Purpose: RiscPC IOMD interrupt controller setup and priority dispatch.

Important APIs/types/functions: defines priority lookup tables, low-level mask/unmask/ack behavior, chained/primary IRQ handlers, and init code that registers IOMD interrupt banks with the generic IRQ core.

Control flow: the top-level IRQ path reads IOMD pending/mask state, uses priority tables to select the highest pending source, and dispatches to generic IRQ handling. Init programs masks/clears and configures descriptors for normal IRQs and FIQ-capable sources.

State and persistence: hardware IOMD mask/request/clear registers hold interrupt enable/pending state. Static priority tables encode fixed dispatch order.

Dependencies and integration points: depends on IOMD register access, `mach/irqs.h`, ARM FIQ support, generic IRQ descriptors, and expansion-card chained interrupts.

Risks: priority tables are opaque and must match hardware bit layout. Incorrect masking can lose or storm interrupts. FIQ/IRQ split has low tolerance for mistakes.

Test signals: timer tick, DMA IRQs, keyboard/mouse/serial interrupts, expansion card parent IRQ dispatch, and interrupt storm handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/riscpc.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/riscpc.c

Purpose: main Acorn RiscPC machine descriptor and board initialization.

Important APIs/types/functions: defines I/O mappings, platform devices/resources for onboard peripherals, machine init, fixup/reserve behavior, and the `MACHINE_START` descriptor.

Control flow: early boot maps fixed I/O windows, initializes IRQ/timer through platform hooks, registers devices such as IDE/keyboard/mouse/display support, and uses ATAGS-era machine setup rather than DT.

State and persistence: installs static platform resources, memory mappings, and machine callbacks. No persistent storage.

Dependencies and integration points: integrates IOMD, ecard, DMA, Acorn framebuffer, legacy timers, and ATAGS boot.

Risks: highly legacy static setup; resource addresses must match hardware and the compiler/toolchain restrictions in Kconfig. Missing platform device registration can strand onboard hardware.

Test signals: complete RiscPC boot, onboard IDE/serial/keyboard/mouse/display, expansion cards, timer tick, and machine restart/power behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/riscpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/time.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/time.c

Purpose: RiscPC legacy timer and clock event/source setup.

Important APIs/types/functions: provides timer initialization and interrupt handling around IOMD timer registers for the platform tick.

Control flow: init programs the hardware timer period, registers the interrupt handler, and hooks into ARM timekeeping. The handler acknowledges the timer interrupt and advances kernel time via the clockevent/timer tick path.

State and persistence: hardware timer count/control registers and registered IRQ handler form runtime state.

Dependencies and integration points: depends on IOMD, `mach/irqs.h`, legacy timer tick selected by Kconfig, and machine descriptor `init_time`.

Risks: incorrect tick rate or acknowledgement causes lost ticks or interrupt storms. Legacy timer code lacks DT clock discovery.

Test signals: stable jiffies, scheduler timer operation, timer IRQ rate, and boot under `LEGACY_TIMER_TICK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-rpc/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/Kconfig

Purpose: common Samsung S3C/S3C64xx platform configuration, especially legacy ATAGS support.

Important APIs/types/functions: sources S3C64xx Kconfig, defines `PLAT_SAMSUNG`, `SAMSUNG_PM`, `S3C_LOWLEVEL_UART_PORT`, `SAMSUNG_ATAGS`, legacy device options (`S3C_DEV_*`, `SAMSUNG_DEV_*`), `GPIO_SAMSUNG`, `SAMSUNG_PM_GPIO`, and `SAMSUNG_WAKEMASK`.

Control flow: build-time only. DT-only platforms avoid ATAGS static devices, while legacy platforms select GPIO, device definitions, PM GPIO save/restore, and wake-mask helpers.

State and persistence: no local runtime state; selected options control which static platform devices and PM helpers are linked.

Dependencies and integration points: coordinates Makefile objects for `init`, `cpu`, `devs`, UART, GPIO, PM, and wake mask.

Risks: legacy ATAGS split means code may silently not build for DT platforms. Deprecated platform notice in CPU init underscores removal risk.

Test signals: config builds for DT-only and SAMSUNG_ATAGS paths, GPIO/PM option combinations, and low-level UART selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/Makefile

Purpose: build object selection for Samsung S3C platform support.

Important APIs/types/functions: includes `Makefile.s3c64xx`, always builds `init.o cpu.o`, builds platform data/devices/UART under `CONFIG_SAMSUNG_ATAGS`, builds `gpio-samsung.o` under `CONFIG_GPIO_SAMSUNG`, and PM helpers under `CONFIG_SAMSUNG_PM`, `CONFIG_SAMSUNG_PM_GPIO`, and `CONFIG_SAMSUNG_WAKEMASK`.

Control flow: make-time object inclusion only.

State and persistence: none.

Dependencies and integration points: mirrors Kconfig split between common CPU init, legacy static devices, GPIO, and PM.

Risks: missing object selection produces link failures or missing runtime platform support for legacy boards.

Test signals: build matrix across ATAGS, GPIO, PM, and wake-mask settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/cpu.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/cpu.c

Purpose: Samsung S3C64xx CPU identification.

Important APIs/types/functions: global `samsung_cpu_id` and `s3c64xx_init_cpu()`.

Control flow: reads CPU ID from `S3C_VA_SYS + 0x118`; if zero, writes/reads the S3C6400 alternate ID register at `0xA1C`. It logs the ID and a deprecation/removal warning.

State and persistence: stores detected ID in global `samsung_cpu_id` for `soc_is_*` helpers. Hardware registers are only read except the S3C6400 enable/write path.

Dependencies and integration points: depends on `map-base.h`, `cpu.h`, and early I/O mapping. GPIO and cpuidle code use `soc_is_s3c64xx()`.

Risks: detection before mapping is valid would fault. The warning is intentionally loud but not fatal.

Test signals: boot log CPU ID, S3C6400 fallback path, and `soc_is_s3c64xx()`-guarded init paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/cpu.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/cpu.h

Purpose: Samsung CPU ID helpers and init declarations.

Important APIs/types/functions: defines CPU ID/mask constants, `IS_SAMSUNG_CPU()` macro, inline `is_samsung_s3c6400()`, `is_samsung_s3c6410()`, `soc_is_s3c64xx()` family macros, `struct cpu_table`, and declarations for CPU/UART/subsystem init.

Control flow: inline helpers compare `samsung_cpu_id` with masks; other declarations are implemented elsewhere.

State and persistence: reads global `samsung_cpu_id`.

Dependencies and integration points: used across S3C GPIO, cpuidle, init, and board setup to gate SoC-specific behavior.

Risks: helpers return zero if CPU config symbols are absent, so code can compile but skip runtime paths. ID masks must match hardware.

Test signals: CPU ID detection and conditional paths for S3C6400/S3C6410.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/cpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/cpuidle-s3c64xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/cpuidle-s3c64xx.c

Purpose: simple cpuidle driver for S3C64xx that gates the ARM core while keeping the system active.

Important APIs/types/functions: `s3c64xx_enter_idle()`, `s3c64xx_cpuidle_driver`, and `s3c64xx_init_cpuidle()`.

Control flow: device init registers the driver only if `soc_is_s3c64xx()`. Entering idle updates `S3C64XX_PWR_CFG` WFI mode bits to IDLE, calls `cpu_do_idle()`, and returns the selected state index.

State and persistence: mutates S3C64xx power config register. Runtime state is managed by cpuidle core.

Dependencies and integration points: depends on CPU ID helpers, S3C64xx power registers, and ARM idle instruction.

Risks: only one shallow state; wrong PWRCFG bits could enter deeper stop/sleep unexpectedly.

Test signals: cpuidle state registration, idle residency, wake latency, and power config readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/cpuidle-s3c64xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/crag6410.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/crag6410.h

Purpose: shared board constants for the Wolfson Cragganmore 6410 platform.

Important APIs/types/functions: defines PMIC IRQ bases and GPIO bases for PCA935x, codec, Glenfarclas PMIC, Banff PMIC, and MMGPIO expanders.

Control flow: no executable flow.

State and persistence: constants allocate board IRQ/GPIO number ranges.

Dependencies and integration points: board files and platform devices use these bases when registering external chips.

Risks: overlapping ranges corrupt IRQ/GPIO namespace allocation.

Test signals: board device registration, external GPIO/IRQ expander operation, and no range collisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/crag6410.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/dev-audio-s3c64xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/dev-audio-s3c64xx.c

Purpose: static platform devices and GPIO mux setup for S3C64xx audio controllers.

Important APIs/types/functions: `s3c64xx_i2s_cfg_gpio()`, platform devices such as `s3c64xx_device_iis0` and sibling audio devices, resource arrays, and exported device symbols.

Control flow: board code registers these platform devices. The I2S GPIO callback selects pin banks/functions based on controller ID and returns `-EINVAL` for invalid IDs.

State and persistence: platform resources define MMIO ranges and DMA masks; GPIO configuration mutates pin mux registers.

Dependencies and integration points: integrates ASoC Samsung I2S/PCM/AC97 drivers, S3C IRQ/map constants, and GPIO config helpers.

Risks: wrong controller ID or pin function breaks audio routing. Static devices are legacy ATAGS-era and absent on DT-only platforms.

Test signals: ASoC device probe, I2S0/1/2 pinmux, playback/capture, and invalid-ID logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/dev-audio-s3c64xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/dev-uart-s3c64xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/dev-uart-s3c64xx.c

Purpose: S3C64xx UART resource definitions for legacy Samsung serial devices.

Important APIs/types/functions: declares per-UART resources for memory and IRQs and provides the resource table consumed by common UART device initialization.

Control flow: common UART init uses these resources when platform code calls `s3c24xx_init_uartdevs()`.

State and persistence: static resource arrays define UART MMIO/IRQ assignment.

Dependencies and integration points: integrates S3C serial driver, `dev-uart.c`, IRQ/map constants, and board-provided UART config.

Risks: incorrect resource order or IRQ mapping breaks console/serial ports.

Test signals: boot console on selected UART, all UART device probes, and low-level UART config match.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/dev-uart-s3c64xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/dev-uart.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/dev-uart.c

Purpose: common helper layer for registering Samsung legacy UART platform devices.

Important APIs/types/functions: functions include `s3c24xx_init_uartdevs()` and related setup that copies board `s3c2410_uartcfg` into serial platform data.

Control flow: CPU/board init passes UART resources and configs; this file creates/initializes platform device data for each configured port.

State and persistence: stores static platform data/resources for UART devices during boot.

Dependencies and integration points: used by `cpu.h` declarations, S3C64xx UART resources, and the Samsung serial driver.

Risks: shallow copying or wrong count can register ports with stale config. Legacy path is tied to ATAGS.

Test signals: serial platform devices present, console works on configured port, and UART count/config match board data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/dev-uart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/devs.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/devs.c

Purpose: legacy Samsung static platform device definitions for framebuffer, MMC/SDHCI, I2C, USB, keypad, PWM, SPI, and related controllers.

Important APIs/types/functions: exports devices such as `s3c_device_fb`, `s3c_device_hsmmc*`, `s3c_device_i2c*`, and platform-data setters including `s3c_fb_set_platdata()`, `s3c_sdhci*_set_platdata()`, and `s3c_i2c*_set_platdata()`.

Control flow: board code selects devices and calls setters to clone board platform data into static `platform_device` structures before registration. Default I2C data is used when callers pass NULL, and GPIO config callbacks are filled if missing.

State and persistence: static resources encode MMIO/IRQ/DMA masks; setter functions allocate/copy platform data into devices. No disk persistence.

Dependencies and integration points: integrates many Samsung legacy drivers with map/IRQ constants, GPIO mux helpers, and platform data headers.

Risks: platform-data copying and defaulting can hide missing board setup. Static resource definitions must match SoC variant and Kconfig-selected device availability.

Test signals: legacy board boot with each selected device probing, resource conflicts, I2C bus numbering, SDHCI card detection, framebuffer IRQs, and USB/keypad/PWM/SPI operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/devs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/devs.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/devs.h

Purpose: declarations for Samsung legacy static platform devices and platform-data setters.

Important APIs/types/functions: declares exported `platform_device` objects for S3C devices and setter functions for framebuffer, SDHCI, I2C, and other board-configurable peripherals.

Control flow: no local flow; board files include this to register devices and attach platform data.

State and persistence: declarations refer to static device state defined in `devs.c` and related device files.

Dependencies and integration points: ties board files to legacy platform devices and Kconfig-selected definitions.

Risks: declaration must stay conditional-compatible with Kconfig, or board files hit link failures.

Test signals: compile coverage for boards using every declared device and successful platform registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/devs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/fb.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/fb.h

Purpose: Samsung framebuffer platform-data helper declarations.

Important APIs/types/functions: declares `s3c_fb_set_platdata()` and framebuffer-related platform-data types used by legacy board setup.

Control flow: no local flow.

State and persistence: platform data configured through these declarations affects static framebuffer device state.

Dependencies and integration points: used by `devs.c`, board files, and the S3C framebuffer driver.

Risks: mismatched platform data can break display timing, DMA, or panel setup.

Test signals: framebuffer probe and panel mode operation on legacy boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/fb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/gpio-cfg-helpers.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/gpio-cfg-helpers.h

Purpose: small inline wrappers for Samsung GPIO configuration operations.

Important APIs/types/functions: `samsung_gpio_do_setcfg()` and `samsung_gpio_do_setpull()` call the active chip config callbacks.

Control flow: callers pass a `samsung_gpio_chip`, offset, and desired config/pull; helper dispatches through `chip->config`.

State and persistence: mutates GPIO configuration registers indirectly through callback implementations.

Dependencies and integration points: used by `gpio-samsung.c` public helpers and relies on `struct samsung_gpio_chip`/`struct samsung_gpio_cfg`.

Risks: assumes config callbacks are initialized; missing callbacks would crash or fail depending on caller setup.

Test signals: GPIO mux/pull changes through `s3c_gpio_cfgpin()` and `s3c_gpio_setpull()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/gpio-cfg-helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/gpio-cfg.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/gpio-cfg.h

Purpose: Samsung legacy GPIO configuration constants and public helper declarations.

Important APIs/types/functions: defines GPIO input/output/special-function encodings, pull values, `S3C_GPIO_SFN()`, `samsung_gpio_is_cfg_special()`, and prototypes such as `s3c_gpio_cfgpin()`, `s3c_gpio_cfgpin_range()`, `s3c_gpio_cfgall_range()`, and `s3c_gpio_setpull()`.

Control flow: no implementation here; callers build encoded configs and invoke functions implemented in `gpio-samsung.c`.

State and persistence: config values map to hardware pin mux and pull registers.

Dependencies and integration points: used by board files and device setup for audio, I2C, SDHCI, keypad, etc.

Risks: encoding differences between 2-bit and 4-bit banks are hidden behind callbacks; wrong special-function number can reroute pins incorrectly.

Test signals: pinmux for every legacy peripheral and invalid config rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/gpio-cfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/gpio-core.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/gpio-core.h

Purpose: core data structures and helper macros for Samsung legacy gpiolib.

Important APIs/types/functions: defines `struct samsung_gpio_chip`, `struct samsung_gpio_cfg`, PM helper types, locking helpers, `to_samsung_gpio()`, and chip lookup/tracking interfaces.

Control flow: no standalone flow; implementation in `gpio-samsung.c` and PM GPIO code uses these structures.

State and persistence: chip structures hold MMIO base, gpio_chip, lock, config callbacks, IRQ base, PM hooks, and interrupt bitmap.

Dependencies and integration points: bridges Linux gpiolib, Samsung config/pull APIs, and platform-specific GPIO bank arrays.

Risks: lock and base offset semantics differ across bank styles; bad structure initialization breaks all GPIO access for a bank.

Test signals: gpiochip registration, get/set/direction, config/pull operations, PM save/restore, and chip lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/gpio-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/gpio-samsung-s3c64xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/gpio-samsung-s3c64xx.h

Purpose: S3C64xx GPIO bank numbering and address macros.

Important APIs/types/functions: defines bank sizes, global GPIO numbers such as `S3C64XX_GPA(n)` through later banks, base addresses, and `S3C_GPIO_END`.

Control flow: no executable flow.

State and persistence: constants define the legacy global GPIO namespace and bank layout.

Dependencies and integration points: used by `gpio-samsung.c`, board headers, and peripheral setup files.

Risks: global numbering must remain consistent with registered gpio_chip bases. Off-by-one bank sizes cause lookup and IRQ mapping errors.

Test signals: gpiochip ranges in debugfs/sysfs, board GPIO constants, and IRQ mapping for GPN/GPL/GPM banks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/gpio-samsung-s3c64xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/gpio-samsung.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/gpio-samsung.c

Purpose: legacy Samsung S3C64xx GPIO controller implementation for non-DT platforms.

Important APIs/types/functions: implements config/pull helpers for 2-bit and 4-bit banks, gpiolib direction/get/set callbacks, chip registration helpers, IRQ mapping helpers, S3C64xx bank tables, `samsung_gpiolib_init()`, and exported APIs `s3c_gpio_cfgpin()`, `s3c_gpio_cfgpin_range()`, `s3c_gpio_cfgall_range()`, and `s3c_gpio_setpull()`.

Control flow: `core_initcall` skips if DT is populated, otherwise initializes config defaults and registers S3C64xx 2-bit, 4-bit, and split 4-bit banks. Runtime GPIO operations lock per chip, update data/control/pull registers, and optionally track global pin-to-chip mappings for config helpers.

State and persistence: static bank arrays describe every GPIO bank. Optional `s3c_gpios[]` tracks pin ownership. Hardware state lives in bank control/data/pull registers and sleep/PM hooks.

Dependencies and integration points: integrates Linux gpiolib, S3C IRQ constants, CPU ID helpers, Samsung PM GPIO code, and legacy board/platform device setup.

Risks: skipped on DT systems, so legacy callers must not expect it there. Register layouts vary by bank; split 4-bit base offset handling is fragile. `BUG_ON` in tracking can panic on bad ranges. PM hook absence logs errors but does not stop registration.

Test signals: non-DT gpiochip registration for all banks, direction/input/output, pull and special-function config, GPIO-to-IRQ for GPN/GPL/GPM, PM save/restore, and no registration when DT is populated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/gpio-samsung.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/gpio-samsung.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/gpio-samsung.h

Purpose: umbrella include for Samsung GPIO definitions.

Important APIs/types/functions: includes or exposes the platform-specific Samsung GPIO numbering/config declarations used by board code.

Control flow: no executable flow.

State and persistence: none directly.

Dependencies and integration points: used by S3C board headers and device setup to get GPIO constants and config APIs.

Risks: tiny forwarding header can mask include-order problems; changes affect many legacy board files.

Test signals: compile coverage for board files including this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/gpio-samsung.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/iic-core.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/iic-core.h

Purpose: Samsung I2C GPIO configuration declarations.

Important APIs/types/functions: declares I2C pin configuration helpers such as `s3c_i2c0_cfg_gpio()` and variant helpers for additional controllers.

Control flow: no local flow; I2C platform-data setters install these callbacks when board data lacks one.

State and persistence: callbacks mutate GPIO pinmux when I2C controllers probe.

Dependencies and integration points: used by `devs.c`, I2C setup files, and `s3c2410-i2c` platform data.

Risks: missing callback leaves I2C pins unconfigured on legacy boards.

Test signals: I2C bus probe and pinmux for bus 0/1 on S3C64xx boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/iic-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/init.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/init.c

Purpose: common Samsung legacy initialization helpers for CPU table matching and platform-data copying.

Important APIs/types/functions: implements `s3c_init_cpu()`-style CPU table selection and `s3c_set_platdata()` helper used by static platform devices.

Control flow: CPU init scans a table for a matching ID/mask, records the selected CPU, and calls map/init hooks. Platform-data helper allocates and copies caller data into a platform device.

State and persistence: maintains selected CPU initialization state and attaches allocated platform data to devices.

Dependencies and integration points: used by board/SoC init and `devs.c` setters.

Risks: unmatched CPU ID prevents SoC-specific init. Platform-data allocation failures can leave devices with missing configuration.

Test signals: CPU table match logs, map/init hook execution, and platform device data after setters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/irq-pm-s3c64xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/irq-pm-s3c64xx.c

Purpose: S3C64xx interrupt controller power-management save/restore support.

Important APIs/types/functions: defines suspend/resume helpers that snapshot and restore VIC/interrupt mask state around sleep.

Control flow: PM suspend records relevant interrupt controller registers; resume writes them back so wake-capable and masked interrupts return to pre-suspend state.

State and persistence: in-memory saved register arrays hold IRQ controller state across suspend; hardware VIC/mask registers are restored on resume.

Dependencies and integration points: used by Samsung PM code with S3C64xx IRQ register definitions and wake-mask handling.

Risks: missing a register can leave interrupts masked/unmasked incorrectly after resume. Wake source configuration must align with system PM policy.

Test signals: suspend/resume with UART/GPIO/RTC wake sources, interrupt mask comparison before/after suspend, and no lost interrupts after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/irq-pm-s3c64xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/irq-uart-s3c64xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/irq-uart-s3c64xx.h

Purpose: UART interrupt definitions for S3C64xx.

Important APIs/types/functions: declares or defines per-UART interrupt mapping helpers/macros used by Samsung serial IRQ setup.

Control flow: no local flow; included by UART IRQ/device setup code.

State and persistence: constants map UART subinterrupts to generic IRQ numbers.

Dependencies and integration points: integrates S3C64xx IRQ definitions with the Samsung serial driver and platform devices.

Risks: wrong UART IRQ mapping breaks console RX/TX/error handling.

Test signals: serial console interrupts, RX/TX under load, and all configured UART ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/irq-uart-s3c64xx.h -->
