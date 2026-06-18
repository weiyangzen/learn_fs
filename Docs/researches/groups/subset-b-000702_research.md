# subset-b-000702 Research

Grouped source research for the requested m68k ColdFire, ARAnyM NatFeat, and FPSP040 files. Each section is bounded for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/device.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/device.c

Purpose: common ColdFire SoC platform-device registration for UART, FEC Ethernet, QSPI, IMX I2C, eDMA, eSDHC, and FlexCAN blocks. It converts SoC header macros such as `MCFUART_BASE*`, `MCFFEC_BASE*`, `MCFI2C_BASE*`, `MCFEDMA_BASE`, and IRQ constants into Linux `platform_device` and `resource` records.

Important APIs and data: `mcf_uart_platform_data`, `mcf_uart`, optional `mcf_fec0/1`, `mcf_qspi`, `mcf_i2c0..5`, `mcf_edma`, `mcf_esdhc`, `mcf_flexcan0`, and `mcf_devices[]`. QSPI chip selects are driven by `mcf_cs_setup()`, `mcf_cs_teardown()`, `mcf_cs_select()`, and `mcf_cs_deselect()` through the GPIO API. `mcf_init_devices()` is the `arch_initcall()` that calls `mcf_uart_set_irq()` then `platform_add_devices()`.

Control flow and state: all hardware description is static init data selected by compile-time SoC macros. Runtime state is only platform-core registration plus GPIO ownership for QSPI CS pins; there is no persistent storage. eDMA adds a static `dma_slave_map` and 32-bit DMA mask.

Dependencies and integration: Linux platform bus, FEC, QSPI, I2C, DMA engine, SDHCI, CAN, GPIO, and ColdFire register headers. It integrates with SoC-specific `config_BSP()` pinmux files that must configure pins before the drivers bind.

Risks and test signals: wrong base/IRQ macros silently create unusable devices; QSPI setup has explicit unwind paths for GPIO request/direction failures; FEC naming differs for `CONFIG_M5441x` (`enet-fec`). Test by booting target configs and checking platform device enumeration, driver bind logs, IRQ delivery, QSPI CS transitions, and eDMA slave lookup names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/dma_timer.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/dma_timer.c

Purpose: exposes ColdFire DMA timer 0 as a free-running clocksource and `sched_clock()` provider. It is used on parts where the DMA timer gives a stable 32-bit counter independent of the regular tick timer.

Important APIs and functions: `cf_dt_get_cycles()` reads `DTCN0`; `clocksource_cf_dt` names the source `coldfire_dma_timer`; `init_cf_dt_clocksource()` programs `DTXMR0`, clears events, sets no reference reload, enables `DTMR0` with divide-by-16, and registers the clocksource at `DMA_FREQ`; `sched_clock()` reads the same counter and scales cycles to nanoseconds with `cycles2ns()`.

Control flow and state: `arch_initcall(init_cf_dt_clocksource)` initializes timer registers once. State is entirely hardware counter state plus static clocksource metadata. No persistence exists across reset or suspend unless hardware preserves the counter.

Dependencies and integration: Linux clocksource and scheduler clock interfaces, raw MMIO helpers, `MCF_CLK`, `MCF_IPSBAR`, and DMA timer register layout. It complements, rather than replaces, `hw_timer_init()` tick devices.

Risks and test signals: the fixed frequency calculation assumes `(MCF_CLK / 2) / 16`; bad clock constants cause time drift. The 32-bit counter wraps in minutes, which the clocksource mask handles but `sched_clock()` consumers must tolerate. Test by verifying clocksource registration, monotonic reads across wrap, scheduler timestamp sanity, and no conflict with another user of DMA timer 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/dma_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/entry.S -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/entry.S

Purpose: low-level ColdFire exception, interrupt, syscall, and context-switch entry code. It bridges m68k trap frames with Linux syscall dispatch, `do_IRQ()`, signal/reschedule handling, and task switching.

Important entry points: `system_call`, `ret_from_exception`, `inthandler`, and `resume`. Optional `sw_ksp`/`sw_usp` exist when `CONFIG_COLDFIRE_SW_A7` needs software stack-pointer shadows. The code relies on `SAVE_ALL_SYS`, `SAVE_ALL_INT`, `RESTORE_USER`, `SAVE_SWITCH_STACK`, `RESTORE_SWITCH_STACK`, `GET_CURRENT`, and `PT_OFF_*` offsets from architecture headers.

Control flow and state: `system_call` saves registers, enables interrupts, bounds-checks `NR_syscalls`, fetches `sys_call_table[d0]`, supports syscall trace entry/exit, writes the return value into `PT_OFF_D0`, then falls into `ret_from_exception`. `ret_from_exception` disables interrupts, separates kernel from user returns, handles preemption for kernel returns, and loops through reschedule/signal work for user returns. `inthandler` extracts the vector from the exception frame, pushes vector and pt_regs, and calls `do_IRQ`. `resume` saves previous thread SR/KSP/USP, restores next thread state, updates current on MMU builds, and returns.

Dependencies and integration: Linux scheduler, ptrace/syscall tracing, signal delivery, IRQ core, and m68k task/thread layout. No persistence beyond per-task saved register state.

Risks and test signals: offset or frame-layout drift is catastrophic. Test with syscall smoke tests, ptrace/seccomp tracing, interrupt storms, preemption-enabled kernels, signal delivery, and task switching under MMU and no-MMU ColdFire configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/entry.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/firebee.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/firebee.c

Purpose: FireBee board-specific NOR flash registration. It describes the board's 8 MiB physical flash at `0xe0000000` and partitions it for bootloader, FPGA image, and kernel/image storage.

Important APIs and data: `firebee_flash_parts[]` defines `dBUG`, `FPGA`, and `image` MTD partitions; `firebee_flash_data` passes width and partition table to the physmap driver; `firebee_flash_resource` covers the physical memory window; `firebee_flash` is a `physmap-flash` platform device. `init_firebee()` registers the device through `arch_initcall()`.

Control flow and state: no dynamic probing occurs. Boot-time init registers one platform device; MTD/physmap later maps and manages the flash. Persistent behavior belongs to NOR contents and MTD consumers, not this file.

Dependencies and integration: Linux platform bus, MTD physmap, ColdFire IO resource definitions, and FireBee board memory map. It depends on the selected board config matching the actual flash bus width and address decode.

Risks and test signals: partition offsets are hard-coded; an incorrect map can expose bootloader or FPGA storage for accidental erase/write. The resource end is `addr + size`, not `addr + size - 1`, which is a boundary detail worth auditing against resource conventions. Test by booting FireBee, inspecting `/proc/mtd`, verifying partition sizes/offsets, and performing read-only MTD probe checks before write tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/firebee.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/gpio.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/gpio.c

Purpose: generic ColdFire GPIO support, providing both legacy exported helpers and an optional gpiolib `gpio_chip`.

Important APIs and functions: exported `__mcfgpio_get_value()`, `__mcfgpio_set_value()`, `__mcfgpio_direction_input()`, `__mcfgpio_direction_output()`, `__mcfgpio_request()`, and `__mcfgpio_free()`. With `CONFIG_GPIOLIB`, wrappers populate `mcfgpio_chip` with direction, get/set, request/free, and `to_irq` callbacks, registered by `core_initcall(mcfgpio_sysinit)`.

Control flow and state: get reads the pin data register. Set and direction operations update MMIO registers under `local_irq_save()` for read-modify-write ports. GPIOs at or after `MCFGPIO_SCR_START` use set/clear registers instead of output data RMW. Request is a no-op; free returns the line to input. State is hardware direction/output latch state only.

Dependencies and integration: `asm/mcfgpio.h` supplies port address/bit mapping macros; Linux gpiolib consumers can request GPIOs and map selected pins to IRQs via `MCFGPIO_IRQ_VECBASE`. Board and SoC pinmux files must place pads in GPIO mode.

Risks and test signals: no ownership enforcement in `__mcfgpio_request()` means conflicts are possible. RMW locking only blocks local interrupts, not external bus masters. `to_irq` depends on compile-time min/max definitions. Test with gpiolib line toggles, input reads, set/clear register GPIOs, IRQ mapping boundaries, and concurrent users on the same port.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/head.S -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/head.S

Purpose: first ColdFire kernel entry code. It disables interrupts/cache, sets core base registers, discovers RAM, initializes cache/MMU basics, optionally relocates ROMFS, clears BSS, sets the initial stack/current task, then jumps to `start_kernel`.

Important symbols and macros: `_start`, `_rambase`, `_ramvec`, `_ramstart`, `_ramend`, optional `_init_sp`, `GET_MEM_SIZE`, and board-overridable `PLATFORM_SETUP`. The RAM-size macro has variants for fixed `CONFIG_RAMSIZE`, DMR-based parts, M5272, and M520x SDRAM registers.

Control flow and state: `_start` sets SR to mask interrupts, disables cache through CACR, saves U-Boot stack if enabled, programs MBAR when configured, runs platform setup, sets VBR to `CONFIG_VECTORBASE`, stores RAM base/vector/end globals, programs ACR cache regions, and enables cache. MMU builds set MMUBAR, clear TLBs, enable identity mapping, and jump to virtual space. ROMFS builds copy the ROM filesystem above BSS. It clears BSS, installs `init_thread_union` as stack, fills m68k CPU/MMU/FPU/machine globals for MMU builds, then calls `start_kernel`.

Dependencies and integration: linker symbols, ColdFire control registers, SoC memory-controller headers, Linux boot ABI, and later `vectors.c` trap setup. State stored before BSS clear is deliberately in `.data`.

Risks and test signals: RAM probing only works for supported SDRAM layouts and RAM at expected base. Cache/MMU register mistakes fail before console. Test with early boot on each config, RAM size reporting, ROMFS boot, U-Boot handoff, and MMU/no-MMU variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/intc-2.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/intc-2.c

Purpose: interrupt controller support for ColdFire parts with 56 programmable plus 7 fixed edge-port interrupts, optionally across two controllers.

Important APIs and data: `intc_irq_mask()`, `intc_irq_unmask()`, `intc_irq_ack()`, `intc_irq_startup()`, `intc_irq_set_type()`, `intc_irq_chip`, `intc_irq_chip_edge_port`, and `init_IRQ()`. `intc_intpri` assigns decreasing level/priority values to vectors when first started.

Control flow and state: `init_IRQ()` masks all sources by setting IMRL mask-all bit, then installs chips and level handlers for `MCFINT_VECBASE..NR_VECS`. Startup lazily programs an ICR byte if unset, configures edge-port lines as inputs and interrupt sources, and unmasks the IRQ. Edge-port ack writes the corresponding EPFR bit. Type changes program EPPAR and switch to `handle_edge_irq` for edge modes.

Dependencies and integration: Linux IRQ core, ColdFire INTC/edge-port registers, vector base definitions, and `do_IRQ()` from entry assembly. Hardware mask bits and priority registers are the only mutable state.

Risks and test signals: vector-to-controller arithmetic must match SoC layout. The shared `intc_intpri--` can underflow if many interrupts start, though priority uniqueness is the intent. Edge-port type writes assume IRQs in EINT range. Test by requesting internal and edge-port IRQs, toggling edge polarities, validating mask/unmask registers, and confirming no spurious mask-all behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/intc-2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/intc-5249.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/intc-5249.c

Purpose: second interrupt-controller GPIO IRQ support for MCF5249, focused on GPIO0-GPIO7 edge-style interrupt lines.

Important APIs and functions: `intc2_irq_gpio_mask()`, `intc2_irq_gpio_unmask()`, `intc2_irq_gpio_ack()`, `intc2_irq_gpio_chip`, and `mcf_intc2_init()` as an `arch_initcall()`.

Control flow and state: mask clears a bit in `MCFSIM2_GPIOINTENABLE`, unmask sets it, and ack writes the bit to `MCFSIM2_GPIOINTCLEAR`. Init installs the chip and `handle_edge_irq` for each GPIO IRQ in the fixed range.

Dependencies and integration: Linux IRQ core plus MCF5249 SIM2 GPIO interrupt registers. It complements the main legacy `intc.c` controller file in M5249 builds. State is the hardware enable/clear register and IRQ-core chip assignment.

Risks and test signals: no trigger-type callback is present, so edge polarity semantics are whatever hardware/default board setup provides. The clear-on-ack behavior should be verified for both pending and masked interrupts. Test by generating GPIO interrupts on all eight lines, checking enable register bits on mask/unmask, and verifying no missed edge after ack.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/intc-5249.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/intc-525x.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/intc-525x.c

Purpose: second interrupt-controller GPIO IRQ support for MCF525x, where rising and falling edge enables/clears occupy separate bit banks.

Important APIs and functions: `intc2_irq_gpio_mask()`, `intc2_irq_gpio_unmask()`, `intc2_irq_gpio_ack()`, `intc2_irq_gpio_set_type()`, `intc2_irq_gpio_chip`, and `mcf_intc2_init()`.

Control flow and state: `mcf_intc2_init()` writes `MCFINTC2_VECBASE` to `MCFINTC2_INTBASE`, then installs edge handlers for GPIO0-GPIO6. Mask/unmask/ack inspect `irqd_get_trigger_type()` and clear/set low bits for rising and high bits (`0x100 << irq`) for falling. `set_type` accepts only `IRQ_TYPE_EDGE_BOTH` subsets.

Dependencies and integration: Linux IRQ core, trigger-type metadata, and MCF525x SIM2/INTC2 registers. It runs alongside the primary ColdFire interrupt controller and gpiolib mapping.

Risks and test signals: if clients never call `irq_set_irq_type()`, the type mask may be zero and mask/unmask/ack do nothing. The callback validates but does not program a separate polarity register, implying GPIOINTENABLE itself selects edges. Test rising-only, falling-only, and both-edge GPIO interrupts, including ack behavior and vector-base setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/intc-525x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/intc-5272.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/intc-5272.c

Purpose: dedicated interrupt controller implementation for the unusual MCF5272 ICR-based controller.

Important APIs and data: `struct irqmap` maps each vector to an ICR register, bit index, and external-ack flag. `intc_irq_mask()`, `intc_irq_unmask()`, `intc_irq_ack()`, `intc_irq_set_type()`, `intc_external_irq()`, `intc_irq_chip`, and `init_IRQ()` implement Linux IRQ behavior.

Control flow and state: `init_IRQ()` masks all four ICR registers with `0x88888888`, then assigns each IRQ a chip and either `handle_level_irq` or custom `intc_external_irq` for external edge interrupts. Masking writes a level/mask nibble, unmasking writes active priority nibble `0xd`, ack handles only mapped external lines, and type changes update `MCFSIM_PITR` polarity bits.

Dependencies and integration: Linux IRQ core, ColdFire 5272 SIM registers, vector constants, and `entry.S` interrupt dispatch. Persistent state is only hardware ICR/PITR content and IRQ descriptors.

Risks and test signals: the map table is the critical contract; off-by-one in `MCFINT_VECBASE` or `MCFINT_VECMAX` affects all IRQs. `intc_external_irq()` uses `handle_simple_irq` after ack due to mask side effects. Test all mapped internal sources, external rising/falling polarity, masking side effects, and spurious vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/intc-5272.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/intc-simr.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/intc-simr.c

Purpose: interrupt-controller support for ColdFire parts with SIMR/CIMR mask/unmask registers, including M520x and M53xx-style one to three INTC units.

Important APIs and functions: `irq2ebit()`, `intc_irq_mask()`, `intc_irq_unmask()`, `intc_irq_ack()`, `intc_irq_startup()`, `intc_irq_set_type()`, `intc_irq_chip`, `intc_irq_chip_edge_port`, and `init_IRQ()`.

Control flow and state: mask/unmask choose controller 0, 1, or 2 by subtracting `MCFINT_VECBASE` and writing the local vector number to SIMR/CIMR. Startup enables edge-port lines when applicable, writes a priority value of 5 into the appropriate ICR byte, then unmasks. Type changes program edge-port polarity bits in EPPAR and switch edge IRQs to `handle_edge_irq`. Init masks all controllers, computes the IRQ span from available ICR bases, then installs chips and level handlers.

Dependencies and integration: Linux IRQ core and ColdFire INTC/edge-port register definitions. M520x has sparse edge-port mapping through `irqebitmap`; other parts map directly.

Risks and test signals: compile-time zero register addresses are used to optimize away absent controllers, so header accuracy matters. Edge-port range tests for M520x include compressed IRQ numbers, not physical line numbers. Test controller boundary IRQs at 63/64/127/128, edge-port IRQs, and type programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/intc-simr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/intc.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/intc.c

Purpose: legacy ColdFire interrupt-controller support for older parts using a single IMR and optional autovector register.

Important APIs and data: global `mcf_irq2imr[NR_IRQS]` maps Linux IRQs to IMR bit indexes. `mcf_setimr()`, `mcf_clrimr()`, `mcf_maskimr()`, `mcf_autovector()`, `intc_irq_mask()`, `intc_irq_unmask()`, and `init_IRQ()` are the core functions.

Control flow and state: build-time selection handles 16-bit versus 32-bit IMR access. `init_IRQ()` masks all interrupt sources and installs a simple level-high `CF-INTC` chip for every IRQ. Board/SoC setup code later calls `mcf_mapirq2imr()` elsewhere to populate `mcf_irq2imr`; mask/unmask are no-ops for unmapped IRQs. `mcf_autovector()` enables autovectoring for external IRQ levels in `MCFSIM_AVR` when available.

Dependencies and integration: Linux IRQ core, legacy SIM registers, board files such as `m5206.c`, `m5307.c`, `m5407.c`, and drivers that need autovector behavior.

Risks and test signals: missing `mcf_irq2imr` mappings leave interrupts unmaskable. IMR width selection must match silicon. The set-type callback returns success but programs nothing. Test with timer/UART/I2C/external IRQ mappings, autovectored devices, and mask/unmask register reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/intc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/m5206.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/m5206.c

Purpose: platform setup for MCF5206/5206e boards. It installs clock aliases, timer scheduling, optional I2C interrupt mapping, selected external interrupt mappings, and NETtel command-line handling.

Important APIs and data: `DEFINE_CLK(pll/sys)`, `m5206_clk_lookup[]`, `m5206_i2c_init()`, and `config_BSP()`.

Control flow and state: `config_BSP()` optionally copies a command line from flash for NETtel, assigns `mach_sched_init = hw_timer_init`, maps external interrupts 25, 28, and 31 to IMR bits, initializes I2C interrupt priority/autovector mapping when enabled, and registers the clkdev table. State is clock lookup registration plus IMR mapping table population.

Dependencies and integration: legacy `intc.c`, `timers.c`/selected timer provider, clkdev, ColdFire SIM headers, and board flash layout. There is no persistent state apart from using flash command-line bytes as boot input.

Risks and test signals: hard-coded flash command-line address and sparse external IRQ support are board assumptions. Test by booting M5206 configs, confirming clock lookup for timer/UART/I2C, timer tick, I2C IRQ, and external IRQ lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/m5206.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/m520x.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/m520x.c

Purpose: platform setup for MCF5207/5208-class parts with clock gating, pinmux for UART/FEC/QSPI/I2C, and scheduler timer selection.

Important APIs and data: numerous `DEFINE_CLK(0, ...)` definitions, `m520x_clk_lookup[]`, `enable_clks[]`, `disable_clks[]`, `m520x_clk_init()`, pin setup helpers, and `config_BSP()`.

Control flow and state: clock init marks core clocks enabled and unused peripheral clocks disabled, then registers clkdev lookups. `config_BSP()` sets `mach_sched_init`, initializes clocks, then configures UART, FEC, QSPI, and I2C pad registers according to enabled drivers.

Dependencies and integration: clkdev/ColdFire clock helpers, SIM GPIO pin assignment registers, common `device.c` platform devices, `intc-simr.c`, and PIT/timer support. State is hardware clock gating and pinmux register content.

Risks and test signals: disabling clocks for peripherals that board firmware or an early console expects can break devices if a driver fails to enable them. QSPI uses UART handshake pins as GPIO CS lines. Test with boot logs, UART console, FEC link, optional QSPI/I2C transfers, and clock enable/disable register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/m520x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/m523x.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/m523x.c

Purpose: platform setup for MCF523x boards, mostly clock alias registration and peripheral pinmux.

Important APIs and data: `m523x_clk_lookup[]`, `m523x_qspi_init()`, `m523x_i2c_init()`, `m523x_fec_init()`, and `config_BSP()`.

Control flow and state: `config_BSP()` assigns `hw_timer_init`, configures FEC pins, QSPI pins/CS timer pins when enabled, I2C pins when enabled, and registers clock lookup entries for PITs, UARTs, QSPI, FEC, and I2C. State is pin assignment registers plus clkdev table registration.

Dependencies and integration: common devices in `device.c`, `intc-2.c`, PIT/timer code, clkdev, and ColdFire GPIO/SIM register headers.

Risks and test signals: QSPI comments indicate chip-select GPIO reuse, so pinmux must stay consistent with `device.c` QSPI CS GPIO numbers. Test UART, FEC, QSPI, I2C, and PIT clock lookup on a 523x config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/m523x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/m5249.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/m5249.c

Purpose: platform setup for MCF5249 boards, including optional M5249C3 SMC91x Ethernet platform device and second-controller I2C/GPIO interrupt configuration.

Important APIs and data: `m5249_clk_lookup[]`, optional `m5249_smc91x_resources`/`m5249_smc91x`, `m5249_devices[]`, `m5249_qspi_init()`, `m5249_i2c_init()`, optional `m5249_smc91x_init()`, `config_BSP()`, and `init_BSP()`.

Control flow and state: `config_BSP()` sets timer scheduling, initializes board Ethernet IRQ if configured, programs QSPI/I2C interrupt priorities and IMR mappings, and registers clocks. `arch_initcall(init_BSP)` adds platform devices. State includes hardware interrupt priority registers, GPIO interrupt enable for SMC91x, clkdev records, and platform-device registrations.

Dependencies and integration: legacy `intc.c`, `intc-5249.c`, clkdev, SMC91x driver, and common QSPI/I2C devices.

Risks and test signals: M5249 has two different interrupt controllers and I2C1 priority programming differs from I2C0. Test SMC91x probe/IRQ on M5249C3, QSPI and both I2C interrupts, and clkdev lookups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/m5249.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/m525x.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/m525x.c

Purpose: platform setup for MCF525x processors, including clock aliases and QSPI/I2C interrupt/pin function setup.

Important APIs and data: `m525x_clk_lookup[]`, `m525x_qspi_init()`, `m525x_i2c_init()`, and `config_BSP()`.

Control flow and state: `config_BSP()` sets `mach_sched_init`, initializes QSPI chip-select GPIO function bits and QSPI interrupt mapping, initializes I2C0 legacy interrupt and I2C1 INTC2 priority, then registers clocks. State is SIM2 GPIO function register, priority registers, IMR mapping, and clkdev registration.

Dependencies and integration: legacy primary interrupt controller, `intc-525x.c`, common QSPI/I2C platform devices, and clkdev.

Risks and test signals: the file has a FIXME noting pinmux/pinctrl replacement for QSPI CS setup. I2C1 programming uses INTC2 macros while I2C0 uses old SIM ICR. Test QSPI chip select toggling, I2C0/I2C1 interrupts, and clock lookup for timers/UART/QSPI/I2C.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/m525x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/m5272.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/m5272.c

Purpose: platform setup for MCF5272 boards, including special reset handling, UART pin enable, clock aliases, and board command-line copy.

Important APIs and data: globals `ppdata` and `ledbank` for board GPIO shadow users, `m5272_clk_lookup[]`, `m5272_uarts_init()`, `m5272_cpu_reset()`, `config_BSP()`, and `init_BSP()`.

Control flow and state: `config_BSP()` optionally sets the peripheral interrupt vector base, copies command lines from board-specific flash offsets, assigns `mach_reset` to the watchdog reset path, and installs `hw_timer_init`. `arch_initcall(init_BSP)` configures UART pins and registers clkdev aliases. State includes watchdog reset registers, UART port control registers, clock lookup registration, and flash-derived boot parameters.

Dependencies and integration: special `intc-5272.c`, timer code, clkdev, and board configs such as NETtel, SCALES, CANCam, and MOD5272.

Risks and test signals: reset loops forever waiting for watchdog; command-line offsets are hard-coded. Test UART console, watchdog reset, timer tick, FEC/QSPI clock lookup, and board command-line import on each configured board.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/m5272.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/m527x.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/m527x.c

Purpose: platform setup for MCF5270/5271/5274/5275 parts, covering clock aliases and pinmux for UART, FEC, QSPI, and I2C.

Important APIs and data: `m527x_clk_lookup[]`, `m527x_qspi_init()`, `m527x_i2c_init()`, `m527x_uarts_init()`, `m527x_fec_init()`, and `config_BSP()`.

Control flow and state: `config_BSP()` sets `hw_timer_init`, configures UART pins, FEC pins, QSPI pins, I2C pins, and registers the clkdev table. Several helpers branch at compile time for M5271 versus M5275 pin assignment differences, including one- versus two-FEC setup.

Dependencies and integration: `intc-2.c`, common `device.c`, clkdev, PIT/timer code, and GPIO/SIM register headers.

Risks and test signals: SoC-specific pinmux branches are easy to mismatch with Kconfig. Dual FEC setup only applies to the non-M5271 path. Test all enabled UARTs, FEC0/FEC1 where present, QSPI CS GPIOs, I2C, and PIT clock lookup on both M5271 and M5275 configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/m527x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/m528x.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/m528x.c

Purpose: platform setup for MCF5280/5281/5282 boards, including pinmux, clock aliases, and optional WildFire halt support.

Important APIs and data: `m528x_clk_lookup[]`, `m528x_qspi_init()`, `m528x_i2c_init()`, `m528x_uarts_init()`, `m528x_fec_init()`, optional `wildfire_halt()`, optional `wildfiremod_halt()`, and `config_BSP()`.

Control flow and state: `config_BSP()` installs board-specific `mach_halt` if configured, sets `hw_timer_init`, configures UART/FEC/QSPI/I2C pin assignment registers, and registers clkdev aliases. WildFireMod halt toggles a GPIO after setting it to digital output.

Dependencies and integration: `intc-2.c`, common platform devices, clkdev, PIT/timer code, and board-specific halt wiring.

Risks and test signals: halt functions write fixed board addresses or GPIO bits and should only run on matching boards. QSPI and I2C pinmux modify shared PAS/PQS registers. Test halt behavior on WildFire boards, UART/FEC/QSPI/I2C function, and clock lookup registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/m528x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/m5307.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/m5307.c

Purpose: platform setup for MCF5307 boards, including legacy external IRQ mappings, optional flash command line, I2C interrupt setup, and BDM clock disable.

Important APIs and data: globals `ppdata` and `ledbank`, `m5307_clk_lookup[]`, `m5307_i2c_init()`, and `config_BSP()`.

Control flow and state: `config_BSP()` copies command-line text from flash for selected boards, sets `hw_timer_init`, maps external IRQ levels 25/27/29/31 to IMR bits, optionally disables BDM clocking via `wdebug()`, initializes I2C interrupt mapping, and registers clock aliases. State includes IMR mapping, clock table, and optional debug hardware control.

Dependencies and integration: legacy `intc.c`, timer code, clkdev, board configs NETtel/SecureEdgeMP3/CLEOPATRA, and MCF debug registers.

Risks and test signals: hard-coded command-line flash address and external IRQ selection are board-specific. Test boot command-line import, timer, I2C IRQ, external IRQs, and BDM-disable effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/m5307.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/m53xx.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/m53xx.c

Purpose: comprehensive platform and early board setup for ColdFire 53xx parts. It handles clock gating/lookup, peripheral pinmux, command-line import, optional BDM disable, and very early PLL/watchdog/SCM/FlexBus/SDRAM/GPIO initialization.

Important APIs and data: many `DEFINE_CLK()` entries and `m53xx_clk_lookup[]`; `enable_clks[]`/`disable_clks[]`; `m53xx_clk_init()`, QSPI/I2C/UART/FEC pin helpers; `config_BSP()`; early `sysinit()`; `wtm_init()`, `scm_init()`, `fbcs_init()`, `sdramc_init()`, `gpio_init()`, `clock_pll()`, `clock_limp()`, `clock_exit_limp()`, and `get_sys_clock()`.

Control flow and state: normal BSP setup registers clocks, sets timer scheduling, initializes pins, and optionally imports a flash command line. Early `sysinit()` programs PLL, disables watchdog, trusts bus masters, sets FlexBus chip selects, initializes SDRAM if not already refreshed, and prepares GPIO latch control. Clock routines enter/exit LIMP mode around PLL changes and preserve SDRAM via self-refresh.

Dependencies and integration: boot assembly may call `sysinit`, Linux clkdev, timer code, `intc-simr.c`, common devices, SDRAM/FBCS/CCM/PLL register headers, and board memory map.

Risks and test signals: this file directly controls memory and clock stability; wrong constants can hang before console or corrupt SDRAM. Test with hardware boot, RAM sizing, PLL frequency measurement, SDRAM stress, UART/FEC/QSPI/I2C operation, and suspend/reset paths if supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/m53xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/m5407.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/m5407.c

Purpose: platform setup for MCF5407 boards. It registers basic clock aliases, maps selected external interrupts, sets timer initialization, and optionally initializes I2C interrupt routing.

Important APIs and data: `m5407_clk_lookup[]`, `m5407_i2c_init()`, and `config_BSP()`.

Control flow and state: `config_BSP()` sets `mach_sched_init = hw_timer_init`, maps external IRQ levels 25, 27, 29, and 31 to legacy IMR bits, initializes I2C ICR/autovector mapping if enabled, and registers clkdev entries. State is IMR mapping and clock lookup registration.

Dependencies and integration: legacy `intc.c`, generic ColdFire timer code, clkdev, and old SIM interrupt registers.

Risks and test signals: only a subset of external interrupt levels is supported. I2C interrupt setup is conditional and uses legacy autovector priorities. Test timer tick, UART clocks, I2C IRQ, and external IRQ behavior on M5407 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/m5407.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/m5441x.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/m5441x.c

Purpose: platform setup for MCF5441x processors, dominated by a large clock-gating catalog plus UART/FEC pin setup.

Important APIs and data: `DEFINE_CLK()` entries across clock banks 0, 1, and 2; `m5411x_clk_lookup[]`; `enable_clks[]`; `disable_clks[]`; special SDHC-clock `clk_ops2`; `m5441x_clk_init()`, `m5441x_uarts_init()`, `m5441x_fec_init()`, and `config_BSP()`.

Control flow and state: `config_BSP()` initializes clocks, sets `hw_timer_init`, and programs UART/FEC pin assignment. Clock init enables required clocks, disables many unused peripherals, and registers lookup entries. `clk_ops2` toggles bits in `MCFSDHC_CLK` for the third clock bank.

Dependencies and integration: `intc-simr.c`, common `device.c` including eDMA/eSDHC/FlexCAN/FEC naming, clkdev, timer code, and M5441x SIM/GPIO headers.

Risks and test signals: the `disable_clks[]` list includes `fsl-dspi.0`, which also appears in `enable_clks[]`, so ordering leaves it disabled; this may be intentional for driver-controlled enable but is a review point. Test SDHC clock ops, UART console, FEC, eDMA, DSPI, and clock gating around driver probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/m5441x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/m54xx.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/m54xx.c

Purpose: platform setup for MCF54xx boards, including UART/I2C pinmux, clock aliases, scheduler timer, and watchdog-based reset.

Important APIs and data: `m54xx_clk_lookup[]`, `m54xx_uarts_init()`, `m54xx_i2c_init()`, `mcf54xx_reset()`, and `config_BSP()`.

Control flow and state: `config_BSP()` sets `mach_reset`, installs `hw_timer_init`, configures PSC pins for UARTs, configures FEC/I2C/IRQ pin assignment for I2C when enabled, and registers clocks. Reset disables interrupts and starts GPT0 watchdog/reset mode.

Dependencies and integration: `intc-2.c`, slice timer/GPT headers, clkdev, UART/I2C drivers, and M54xx MMU/memory architecture includes.

Risks and test signals: reset relies on GPT watchdog register programming and may not return. PSC pin modes vary per UART with RTS/CTS on selected ports. Test reset, serial ports, I2C pins/IRQ, SLT timer tick, and clock lookups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/m54xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/mcf8390.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/mcf8390.c

Purpose: simple platform-device registration for NE2000/8390-compatible Ethernet on ColdFire boards.

Important APIs and data: `mcf8390_resources[]` describes memory and IRQ resources from `asm/mcf8390.h`; `mcf8390_platform_init()` registers a `mcf8390` platform device with `platform_device_register_simple()` at `arch_initcall()`.

Control flow and state: boot-time init creates one platform device. Runtime state belongs to the platform bus and downstream network driver; this file has no persistent data.

Dependencies and integration: board headers must define `NE2000_ADDR`, `NE2000_ADDRSIZE`, and `NE2000_IRQ_VECTOR`. The `mcf8390` driver must match the device name.

Risks and test signals: address/IRQ macros are completely trusted and there is no error handling on registration. Test by verifying platform device creation, driver bind, IO resource range, IRQ delivery, and Ethernet packet RX/TX on boards selecting `CONFIG_MCF8390`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/mcf8390.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/nettel.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/nettel.c

Purpose: NETtel board Ethernet setup for two SMC9196/SMC91x interfaces, including early address remap and flash MAC loading.

Important APIs and data: fixed `NETTEL_SMC0/1_ADDR` and IRQs, `nettel_smc91x_0/1_resources`, `nettel_smc91x[]`, `nettel_macdefault[]`, `nettel_smc91x_setmac()`, `nettel_smc91x_init()`, and `init_nettel()`.

Control flow and state: `init_nettel()` calls board hardware setup then registers two `smc91x` platform devices. Setup toggles `MCFSIM_PADDR` and board parallel port data to move one Ethernet chip away from the shared reset address, adjusts chip-select timing, enables autovectoring for both IRQs, and writes MAC addresses into SMC registers from flash or default bytes.

Dependencies and integration: legacy interrupt autovector support, board `mcf_setppdata()` helpers, SMC91x driver, flash layout at `0xf0006000`, and ColdFire SIM chip-select registers.

Risks and test signals: register writes assume exact NETtel hardware and two SMC chips initially aliasing. `nettel_smc91x_setmac()` writes bank select using `NETTEL_SMC0_ADDR` even when programming `ioaddr`, a detail to verify. Test both NICs enumerate with distinct resources/MACs, IRQs fire, and flash-erased MAC fallback works.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/nettel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/pci.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/pci.c

Purpose: ColdFire PCI host-bridge setup, configuration-space access, IRQ mapping, and root-bus scan.

Important APIs and data: globals `rootbus` and `iospace`; host slot/SID table `mcf_host_slot2sid[]`; IRQ table `mcf_host_irq[]`; `mcf_mk_pcicar()`, `mcf_pci_readconfig()`, `mcf_pci_writeconfig()`, `mcf_pci_ops`, PCI memory/IO/bus resources, `mcf_pci_map_irq()`, and `mcf_pci_init()` as `subsys_initcall()`.

Control flow and state: init allocates a host bridge, resets the external PCI bus, requests memory/IO resources, configures arbiter, pinmux, local host controller config, initiator and target windows, maps IO/config space with `ioremap()`, releases reset after a delay, scans the root bus, sizes/assigns resources, and adds devices. Config reads/writes enable `PCICAR`, access the IO window at `where & 3`, then disable config mode.

Dependencies and integration: Linux PCI core, ColdFire M54xx PCI registers, MMIO resource tree, IRQ swizzling, and memory map constants.

Risks and test signals: bus 0 probing is filtered by a fixed slot table; unsupported slots read as all-ones. No `ioremap` cleanup is done on scan failure after mapping. Test PCI enumeration, config read/write sizes/endian conversion, BAR assignment, DMA to RAM target window, and IRQ mapping for each populated slot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/pit.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/pit.c

Purpose: Programmable Interrupt Timer clockevent and clocksource support for ColdFire parts with PIT hardware.

Important APIs and data: `cf_pit_set_periodic()`, `cf_pit_set_oneshot()`, `cf_pit_shutdown()`, `cf_pit_next_event()`, `cf_pit_clockevent`, `pit_tick()`, `pit_read_clk()`, `pit_clk`, and `hw_timer_init()`.

Control flow and state: `hw_timer_init()` configures clockevent timing parameters, registers the clockevent, requests `MCF_IRQ_PIT1`, and registers a 32-bit clocksource. Periodic mode reloads `PIT_CYCLES_PER_JIFFY`; oneshot mode enables interrupt without reload and `set_next_event` programs PMR. The IRQ handler clears PIF, advances `pit_cnt`, and calls the clockevent handler. Clocksource reads combine `pit_cnt` and the down-counter under local IRQ disable.

Dependencies and integration: Linux clockevents/clocksources, IRQ core, `mach_sched_init` assignment from SoC BSP files, and PIT register definitions.

Risks and test signals: frequency assumes `(MCF_CLK/2)/64`; oneshot minimum/maximum are 16-bit hardware limits. `pit_cnt` must remain coherent with IRQ clearing. Test periodic tick, oneshot high-res timers, clocksource monotonicity around interrupts, and failed IRQ request logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/pit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/reset.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/reset.c

Purpose: common ColdFire software reset setup for parts that can reset through `MCFSIM_SYPCR` or `MCF_RCR`.

Important APIs and functions: compile-time-selected `mcf_cpu_reset()` and `mcf_setup_reset()` as an `arch_initcall()`.

Control flow and state: reset disables local interrupts, then either programs SYPCR for watchdog soft reset and spins forever, or writes `MCF_RCR_SWRESET` to the reset-control register. Init assigns `mach_reset = mcf_cpu_reset`.

Dependencies and integration: Linux machine reset hook, ColdFire SIM/reset-control registers, and SoC-specific files that do not override reset. M5272 and 54xx have their own reset implementations and do not rely on this path.

Risks and test signals: the comments mention exceptions for 5272 and 547x; build selection must avoid duplicate `mcf_cpu_reset()` definitions and wrong reset method. Test reboot command on each supported SoC, verify interrupts disabled before reset, and confirm no return after reset register write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/sltimers.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/sltimers.c

Purpose: Slice Timer based system tick, clocksource, and optional high-frequency profiler for ColdFire parts with SLT hardware.

Important APIs and data: optional `mcfslt_profile_tick()` and `mcfslt_profile_init()` under `CONFIG_HIGHPROFILE`; `mcfslt_tick()`, `mcfslt_read_clk()`, `mcfslt_clk`, and `hw_timer_init()`.

Control flow and state: `hw_timer_init()` computes cycles per jiffy from `MCF_BUSCLK`, writes `STCNT` with `n - 1`, starts timer 0 with run/interrupt/timer enable bits, initializes `mcfslt_cnt`, requests the timer IRQ, registers the clocksource, and optionally starts timer 1 as profiler. The tick handler clears BE/TE status bits, advances `mcfslt_cnt`, and calls `legacy_timer_tick(1)`. Clock reads account for pending TE by adding one jiffy and rereading the down-counter.

Dependencies and integration: legacy m68k timer path, Linux clocksource/profile APIs, IRQ core, and slice timer registers. SoC BSPs assign this through `mach_sched_init`.

Risks and test signals: down-counter off-by-one handling is explicitly documented; changing it can skew time. Pending TE read logic is sensitive to races. Test jiffies rate, clocksource monotonicity across pending interrupts, profiler IRQ, and failed request_irq logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/sltimers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/stmark2.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/stmark2.c

Purpose: board support for the Sysam AMCORE/STMark2 board's DSPI controller and SPI NOR flash partitioning.

Important APIs and data: `stmark2_partitions[]`, `stmark2_spi_flash_data`, `stmark2_board_info[]`, `dspi_spi0_info`, `dspi_spi0_resource[]`, `dspi_spi0_device`, `stmark2_devices[]`, and `init_stmark2()` as a `device_initcall()`.

Control flow and state: init programs DSPI pin assignment registers, board GPIO/pad registers, CAN pads, adds the DSPI platform device, and registers SPI board info for an `m25p80`/`is25lp128` flash on bus 0 chip select 1. State includes pinmux registers and platform/SPI core registration; persistent data is flash partition contents.

Dependencies and integration: FSL DSPI platform driver, SPI NOR driver, MTD partitioning, eDMA DMA resources, and board pinmux.

Risks and test signals: the comment says proper pinmux is mandatory; wrong pad setup breaks SPI. Flash partition names/sizes assume a 16 MiB device and U-Boot/kernel layout. Test DSPI probe, DMA channels, SPI NOR JEDEC read, `/proc/mtd` partition layout, and CAN pad side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/stmark2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/timers.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/timers.c

Purpose: generic ColdFire hardware timer support using timer 1 for system tick/clocksource and optionally timer 2 for high-profile sampling.

Important APIs and data: `init_timer_irq()`, `mcftmr_tick()`, `mcftmr_read_clk()`, `mcftmr_clk`, `hw_timer_init()`, optional `coldfire_profile_tick()` and `coldfire_profile_init()`. `__raw_readtrr`/`__raw_writetrr` select 16-bit or 32-bit TRR access for newer parts.

Control flow and state: `hw_timer_init()` disables timer 1, computes cycles per jiffy from `MCF_BUSCLK/16`, writes TRR as `n - 1`, starts restart mode, registers the clocksource, programs interrupt priority/autovector mapping, requests the timer IRQ, and optionally initializes profiler timer 2. The tick handler clears TER flags, advances `mcftmr_cnt`, and calls `legacy_timer_tick(1)`. Clocksource reads `mcftmr_cnt + TCN`.

Dependencies and integration: legacy m68k timer path, IRQ core, clocksource API, old SIM interrupt registers, and BSP `mach_sched_init`.

Risks and test signals: timer width differs by SoC; wrong TRR access corrupts period. High-profile timer shares similar priority mapping. Test jiffy frequency, clocksource monotonicity, timer IRQ mapping, profiler IRQ, and 16/32-bit timer builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/timers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/vectors.c -->
# sources/distributed-fs/ceph-client/arch/m68k/coldfire/vectors.c

Purpose: high-level trap vector table setup for ColdFire after early startup has established `_ramvec`.

Important APIs and functions: optional `dbginterrupt_c()` under `TRAP_DBG_INTERRUPT`, assembler declarations `buserr`, `trap`, `system_call`, `inthandler`, and `trap_init()`.

Control flow and state: `trap_init()` fills vector entries 3-23 and 33-63 with `trap`, vectors 24-31 and 64-254 with `inthandler`, clears vector 255, installs `buserr` at vector 2 and `system_call` at vector 32, and optionally routes vector 12 to a debug interrupt handler. State is the RAM vector table pointed to by `_ramvec`.

Dependencies and integration: `head.S` sets VBR and `_ramvec`; `entry.S` implements system call and interrupt entry; generic m68k trap code supplies `trap` and `buserr`.

Risks and test signals: wrong vector ranges can route CPU exceptions as IRQs or vice versa. Debug handler halts the CPU after dumping. Test system calls, bus errors, illegal instruction traps, external interrupts, and vector table contents after boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/coldfire/vectors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/emu/Makefile -->
# sources/distributed-fs/ceph-client/arch/m68k/emu/Makefile

Purpose: kbuild manifest for m68k emulator/NatFeat support.

Important entries: `obj-y += natfeat.o` always builds base Native Features support for this directory, while `obj-$(CONFIG_NFBLOCK)`, `obj-$(CONFIG_NFCON)`, and `obj-$(CONFIG_NFETH)` conditionally build block, console, and Ethernet NatFeat drivers.

Control flow and state: kbuild uses these object lists to select compiled objects; no runtime state exists. The file defines integration boundaries for the ARAnyM emulator support stack.

Dependencies and integration: Linux kbuild, m68k architecture config symbols, and the source files in the same folder. `natfeat.o` must be present for optional drivers because they call `nf_get_id()`/`nf_call()`.

Risks and test signals: building optional drivers without base NatFeat support would fail, but unconditional `natfeat.o` prevents that. Test by building configs with each `CONFIG_NF*` option enabled/disabled and checking link inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/emu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/emu/natfeat.c -->
# sources/distributed-fs/ceph-client/arch/m68k/emu/natfeat.c

Purpose: ARAnyM Native Features base support. It discovers emulator-provided services, exports the call interface, prints to emulator stderr, and registers emulator poweroff.

Important APIs and functions: assembly stubs `nf_get_id_phys` and exported `nf_call`; `nf_get_id()` copies feature names to a physical-addressable stack buffer; `nfprint()` formats to a static buffer and calls `NF_STDERR`; `nf_poweroff()` calls `NF_SHUTDOWN`; `nf_init()` probes `NF_VERSION`/`NF_NAME` and registers poweroff.

Control flow and state: NatFeat opcodes `.short 0x7300` and `.short 0x7301` are wrapped with exception-table fallback to return zero when unsupported. `nf_init()` logs the emulator name/version only when features exist. State is minimal: no persistent storage, only a static print buffer and registered poweroff hook.

Dependencies and integration: ARAnyM emulator ABI, `virt_to_phys`, exception tables, Linux reboot/poweroff registration, and optional nfblock/nfcon/nfeth modules.

Risks and test signals: `nfprint()` uses a static buffer and is not reentrant. Feature names over 31 bytes return no ID. Test on ARAnyM with NatFeat enabled/disabled, verify exception fallback, feature lookup, stderr output, and poweroff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/emu/natfeat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/emu/nfblock.c -->
# sources/distributed-fs/ceph-client/arch/m68k/emu/nfblock.c

Purpose: ARAnyM NatFeat block driver exposing XHDI disks as Linux block devices.

Important APIs and data: `nfhd_read_write()`, `nfhd_get_capacity()`, `struct nfhd_device`, `nfhd_submit_bio()`, `nfhd_getgeo()`, `nfhd_ops`, `nfhd_init_one()`, `nfhd_init()`, and `nfhd_exit()`. `major_num` is a module parameter.

Control flow and state: init obtains NatFeat ID `XHDI`, registers a block major, scans emulated device IDs 8-23, queries capacity, allocates `nfhd_device` plus `gendisk`, sets capacity, adds disks, and links devices on `nfhd_list`. Bio submission iterates segments and calls XHDI read/write with physical segment addresses, then completes the bio. Exit removes disks and unregisters the major.

Dependencies and integration: NatFeat base, Linux block layer, bio physical address mapping, and ARAnyM XHDI ABI. Runtime state is the device list, gendisks, major number, and emulator-backed disk contents.

Risks and test signals: `nfhd_submit_bio()` ignores emulator read/write return errors and still ends I/O successfully. Segment length/sector shifting depends on power-of-two block size. Test disk scan, invalid block size rejection, read/write data integrity, error injection if emulator supports it, and unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/emu/nfblock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/emu/nfcon.c -->
# sources/distributed-fs/ceph-client/arch/m68k/emu/nfcon.c

Purpose: ARAnyM NatFeat console and tty driver writing to emulator stderr.

Important APIs and data: `stderr_id`, `nfcon_tty_port`, `nfcon_tty_driver`, `nfputs()`, console callbacks `nfcon_write()`/`nfcon_device()`, tty callbacks, `nf_debug_setup()` early parameter handler, `nfcon_init()`, and `nfcon_exit()`.

Control flow and state: `nfputs()` chunks output into a 68-byte stack buffer, null-terminates up to 64 bytes, and calls `NF_STDERR`. `debug=nfcon` can enable/register the console early. Module init obtains the stderr feature, allocates/registers a one-line raw tty driver, links a tty port, and registers the console if not already present. Exit unregisters console and tty resources.

Dependencies and integration: NatFeat base, Linux console and tty layers, early parameter parsing, and ARAnyM `NF_STDERR`.

Risks and test signals: output-only tty has no read path and `write_room()` is fixed at 64. Early console registration depends on NatFeat being callable early. Test `debug=nfcon`, `/dev/nfcon` writes, console handoff, module unload, and behavior when `NF_STDERR` is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/emu/nfcon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/emu/nfeth.c -->
# sources/distributed-fs/ceph-client/arch/m68k/emu/nfeth.c

Purpose: ARAnyM NatFeat Ethernet driver exposing up to eight emulated Ethernet interfaces to Linux networking.

Important APIs and data: NatFeat command enum (`XIF_*`), `struct nfeth_private`, `nfeth_open()`, `nfeth_stop()`, `recv_packet()`, `nfeth_interrupt()`, `nfeth_xmit()`, `nfeth_tx_timeout()`, `nfeth_netdev_ops`, `nfeth_probe()`, `nfeth_init()`, and `nfeth_cleanup()`.

Control flow and state: init gets `ETHERNET`, reads API version and interrupt level, requests a shared IRQ, then probes units by asking for MAC addresses. Open starts the emulator receiver and queue; stop stops both. IRQ handler obtains a unit bitmask, receives pending packets into skbs, acknowledges each unit bit, and passes packets to `netif_rx`. Transmit pads short Ethernet frames and calls `XIF_WRITEBLOCK`.

Dependencies and integration: NatFeat base, Linux netdevice/etherdevice APIs, physical buffer addressing, and ARAnyM Ethernet ABI.

Risks and test signals: RX/TX NatFeat return values are mostly ignored; malformed packet lengths can stress allocation; request_irq uses the handler address as `dev_id`. Test multiple units, ifup/ifdown, RX/TX packet counters, short-frame padding, interrupt masks, and cleanup after partial probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/emu/nfeth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/Makefile -->
# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/Makefile

Purpose: kbuild object list for the Motorola 68040 Floating Point Software Package (FPSP) used by m68k FPU exception emulation.

Important entries: `obj-y` includes conversion helpers (`bindec.o`, `binstr.o`, `decbin.o`), exception handlers (`gen_except.o`, `kernel_ex.o`, `x_*`), operand/result helpers (`get_op.o`, `res_func.o`, `round.o`, `sto_res.o`, `util.o`), transcendental implementations (`sacos.o`, `sasin.o`, etc.), and support/errata files (`bugfix.o`, `skeleton.o`).

Control flow and state: build-time only. It links all FPSP assembly objects into the m68k kernel image for 68040 FPU handling. Runtime state is managed in the individual assembly handlers' stack frames.

Dependencies and integration: Linux kbuild and 68040/FPSP assembly conventions. The listed objects depend on shared symbols and stack offsets from `fpsp.h`.

Risks and test signals: object omission or reordering can create unresolved labels or missing exception paths. Test by building a 68040/FPSP config and running floating-point exception/emulation test programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/bindec.S -->
# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/bindec.S

Purpose: FPSP routine converting an extended-precision binary floating-point input to packed BCD format for packed move-out operations.

Important APIs and labels: exports `bindec` and `sc_mul`; uses `fpsp.h` stack offsets, power-of-ten tables `PTENRN/PTENRM/PTENRP`, helper `binstr`, and integer conversion helper `sintdo`. Constants include `LOG2`, `LOG2UP1`, single-precision `FONE/FTWO/FTEN/F4933`, and rounding table `RBDTBL`.

Control flow and state: `bindec` saves D2-D7/A2 and FP0-FP2, normalizes denormal/unnormal inputs, computes an approximate decimal exponent `ILOG`, calculates display length from the k-factor, builds `10^ISCALE` in a directed rounding mode, scales the absolute input, forces round-to-zero for controlled inexact handling, uses `sintdo` to round to integer digits, adjusts if digit count is off, calls `binstr` for mantissa and exponent BCD digits, writes sign bits, clears transient FPSR inexact state, and restores registers.

Dependencies and integration: called by FPSP packed decimal store paths, shares local stack frame state through A6, and reports exceptions through `USER_FPSR`.

Risks and test signals: decimal conversion is highly rounding-sensitive, especially denormals, k-factor bounds, and exact/inexact propagation. Test packed decimal output for normal, denormal, zero, large/small exponent, all rounding modes, and positive/negative k-factors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/bindec.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/binstr.S -->
# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/binstr.S

Purpose: FPSP helper converting a 64-bit binary fraction in D2:D3 into packed BCD digits in memory.

Important API: exports `binstr`. Inputs are LEN in D0, fraction in D2:D3, and destination pointer in A0. It saves/restores D0-D7 and writes BCD bytes to the output string.

Control flow and state: the loop multiplies the 64-bit fraction by 10 using separate multiply-by-8 and multiply-by-2 shifts, adds the two products with carry, extracts the digit shifted out at the high end, packs two BCD digits per byte, and repeats for LEN digits. NOPs after arithmetic preserve historical 68040 errata timing/workaround behavior. There is no persistent state; all state is register and destination-memory local.

Dependencies and integration: called by `bindec.S` for mantissa and exponent decimal strings. It includes `fpsp.h` but mainly uses registers and memory pointer conventions.

Risks and test signals: off-by-one in LEN or byte packing corrupts packed decimal results. Carry propagation across D2:D3 and BCD nibble order are critical. Test with known binary fractions producing fixed digit strings, odd/even LEN values, maximum 17-digit paths, and integration through packed decimal store instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/binstr.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/bugfix.S -->
# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/bugfix.S

Purpose: Motorola FPSP workaround code for 68040 FPU bug 1238, repairing affected fsave frames/results before normal FPSP completion.

Important API and labels: exports `b1238_fix`; key labels include `op0`, `op0_xu`, `op0_xi`, `op0_xb`, `op2sgl`, `op2_xu`, `op2_xi`, `op2_com`, case labels, `finish`, and `fix_done`. It can jump to `fpsp_fmt_error` when a busy frame cannot be reconstructed safely.

Control flow and state: the routine inspects the FPSP fsave frame and command/register fields, branches by operand/result class, manipulates ETEMP/FPTEMP/WBTEMP bits and tag fields, reconstructs or adjusts exponent/mantissa/sign bits, handles FP register destinations, and returns when either no fix is required or the frame is corrected.

Dependencies and integration: uses `fpsp.h` frame offsets and is called from general exception cleanup paths before `fpsp_done` or real exception dispatch. It modifies only the FPSP local/fsave frame and saved user FPU state.

Risks and test signals: this is errata-specific and frame-format-specific; incorrect version/format interpretation can corrupt user floating-point state. Test with Motorola FPSP bug 1238 trigger cases, unsupported frame formats, FP0-FP3 destinations, and exception paths that continue to real F-line handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/bugfix.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/decbin.S -->
# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/decbin.S

Purpose: FPSP routine converting normalized packed BCD input in the FPSP frame to an exact or correctly rounded extended-precision value in FP0.

Important APIs and labels: exports `decbin`, `calc_e`, `calc_m`, `ap_st_z`, `ap_st_n`, `pwrten`, and `norm`. Uses `PTENRN/PTENRM/PTENRP`, rounding table `RTABLE`, and `fpsp.h` offsets such as `ETEMP`, `FP_SCR1`, and `USER_FPSR`.

Control flow and state: `decbin` copies packed BCD to scratch, converts exponent digits to binary with sign and a -16 adjustment, accumulates mantissa digits in FP0 by multiplying by 10 and adding each digit, applies mantissa sign, strips/appends zeros for large adjusted exponents to reduce power-of-ten error, computes `10^abs(exp)` under a directed rounding mode selected from user FPCR/sign bits, multiplies or divides FP0 by that factor, converts final INEX2 to INEX1/AIINEX in `USER_FPSR`, restores D2-D5, and returns.

Dependencies and integration: used by packed decimal input handling in the FPSP operand decode path. It operates entirely through the FPSP local frame and FPU registers.

Risks and test signals: decimal-to-binary conversion depends on exact digit extraction, exponent sign bits, and rounding-table choice. Test packed BCD inputs for zero/nonzero mantissas, positive/negative exponents, signs, large exponent reduction, all rounding modes, and inexact exception enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/decbin.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/do_func.S -->
# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/do_func.S

Purpose: FPSP dispatcher and special-case handler for unimplemented 68040 floating-point operations.

Important APIs and labels: exports `do_func`, `serror`, forced-result helpers (`snzrinx`, `szero`, `sinf`, `sone`, `spi_2`, `szr_inf`, `sopr_inf`), log special cases (`sslognp1`, `sslogn`, `sslog10`, `sslog2` and denormal variants), dyadic dispatchers `pmod`, `prem`, `pscale`, sincos special cases, and constant loaders `ld_ppi2`, `ld_mpi2`, `ld_pinf`, `ld_minf`, `ld_pone`, `ld_mone`, `ld_pzero`, `ld_mzero`.

Control flow and state: `do_func` clears `CU_ONLY`, detects `fmovecr` and jumps to `smovcr`, otherwise validates the opcode extension, combines opcode and source tag into an index into `tblpre`, points A0 at `ETEMP`, sanitizes FPCR, and jumps to the selected emulation routine. The rest of the file handles exceptional operand combinations for logs, mod/rem, scale, and sincos through tag jump tables, setting `USER_FPSR` condition/exception bits and returning results in FP0/FP1.

Dependencies and integration: shared FPSP tables and routines (`tblpre`, transcendental functions, `src_nan`, `dst_nan`, `t_operr`, `t_inx2`, `sto_cos`). State is the FPSP local frame and saved user status registers.

Risks and test signals: table index formation must match `tbldo` layout. Exceptional cases must exactly follow 68881/68040 semantics. Test unsupported opcodes, fmovecr, logs of negative/zero/one, mod/rem NaN/zero/inf combinations, fscale, fsincos, and FPSR flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/do_func.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/fpsp.h -->
# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/fpsp.h

Purpose: shared assembly equate header for the Motorola 68040 FPSP. It defines the stack frame, local variable, fsave frame, FPSR/FPCR, tag, and exception-vector offsets used by all FPSP assembly files.

Important definitions: `LOCAL_SIZE`, `USER_DA`, `USER_FP0..USER_FP3`, `USER_FPCR`, `USER_FPSR`, `USER_FPIAR`, scratch areas `FP_SCR*`/`L_SCR*`, flags such as `STORE_FLG`, `BINDEC_FLG`, `DNRM_FLG`, `CU_ONLY`, fsave offsets such as `WBTEMP`, `FPTEMP`, `ETEMP`, `CMDREG1B`, `CMDREG2B`, `STAG`, `DTAG`, exception frame offsets `EXC_SR/PC/VEC/EA`, FPSR masks, FPCR rounding/precision modes, tag constants, and fsave frame sizes/versions.

Control flow and state: no executable code. It specifies the memory contract established by FPSP handlers after `link a6,#-LOCAL_SIZE`, `fsave`, saving D/A and FP registers, and saving user FPCR/FPSR/FPIAR. All assembly routines read/write state through these offsets before restoring on exit.

Dependencies and integration: every file in `fpsp040` must agree with these offsets. It also encodes hardware frame formats and exception vector constants used when transforming fsave frames.

Risks and test signals: any offset change without coordinated assembly updates corrupts user registers or exception frames. Test by building all FPSP objects and running broad FPU exception suites that cover unimplemented, underflow, overflow, inexact, NaN, packed decimal, and store-result paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/fpsp040/fpsp.h -->
