# subset-b-000752 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/of.c -->
# sources/distributed-fs/ceph-client/arch/mips/ralink/of.c

Purpose: Ralink/MediaTek MIPS device-tree bootstrap glue. It remaps the system-controller and memory-controller nodes, establishes the I/O port base, parses the built-in FDT, discovers RAM, and registers platform buses for the selected SoC.

Important APIs and control flow: `mtmips_of_remap_node()` finds a matching DT node, converts its first address resource, claims the memory region, and returns an `ioremap()`. `ralink_of_remap()` stores the exported `rt_sysc_membase` and local `rt_memc_membase`. `plat_mem_setup()` calls `get_fdt()`, `__dt_setup_arch()`, then chooses memory from DT, SoC-specific `mem_detect`, fixed `mem_size`, or `detect_memory_region()`. `plat_of_setup()` uses `__dt_register_buses()` for `soc_info.compatible` and `palmbus`.

State, persistence, and integration: state is early global register mappings and memblock RAM entries. It depends on `soc_info` filled by the SoC-specific `prom_soc_init()`, matching DT compatible strings, `ralink_regs` helpers, and Linux OF/memblock initialization. Risks include hard panics for missing core DT nodes, resource leaks if `ioremap()` fails after `request_mem_region()`, and boot failure when `soc_info.compatible` is wrong. Test signals are early boot logs, successful sysc/memc mapping, visible RAM size, and palmbus child device creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/prom.c -->
# sources/distributed-fs/ceph-client/arch/mips/ralink/prom.c

Purpose: common Ralink PROM entry code. It owns the global `soc_info` and `ralink_soc` state, reports the system type, and imports bootloader command-line arguments into `arcs_cmdline`.

Important APIs and control flow: `prom_init()` calls the SoC-family implementation of `prom_soc_init(&soc_info)`, logs `get_system_type()`, and then runs `prom_init_cmdline()`. The command-line parser treats `fw_arg0` as argc and `fw_arg1` as a KSEG1 argv pointer, appending non-empty physical addresses to `arcs_cmdline`.

State, persistence, and integration: persistent boot state is the global SoC descriptor plus the final kernel command line. It depends on bootloader argument layout, `KSEG1ADDR()` conversion, and one selected SoC object file exporting `prom_soc_init()`. Risks include trusting firmware pointers and silent command truncation through `strlcat()`. Test signals include "SoC Type" logging, expected `/proc/cpuinfo` system type, and boot arguments appearing in `/proc/cmdline`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/prom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/reset.c -->
# sources/distributed-fs/ceph-client/arch/mips/ralink/reset.c

Purpose: Ralink restart support. It wires the generic MIPS `_machine_restart` hook to a system-controller reset sequence.

Important APIs and control flow: `mips_reboot_setup()` runs as an `arch_initcall()` and assigns `_machine_restart`. `ralink_restart()` optionally asserts the PCI reset bit, delays for 50 ms, disables local interrupts, writes `RSTCTL_RESET_SYSTEM` to `SYSC_REG_RESET_CTRL`, and never returns.

State, persistence, and integration: it mutates only sysc reset registers during shutdown. Dependencies include `rt_sysc_w32()` and `rt_sysc_m32()` having a valid system-controller mapping from `ralink_of_remap()`. Risks are reset failure if sysc was not remapped, PCI reset side effects when CONFIG_PCI is enabled, and no halt/poweroff implementation. Test signals are reboot behavior on supported boards and the absence of post-reset execution after the write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/rt288x.c -->
# sources/distributed-fs/ceph-client/arch/mips/ralink/rt288x.c

Purpose: RT2880 SoC identification and memory metadata. It validates chip-name registers, formats user-visible SoC strings, and registers a Linux `soc_device`.

Important APIs and control flow: raw sysc reads implement `rt2880_get_soc_name0/1()`, `rt2880_soc_valid()`, and ID/revision extractors. `prom_soc_init()` panics on unknown name registers, fills `soc_info->compatible`, `sys_type`, memory base/min/max, sets `ralink_soc = RT2880_SOC`, and saves the `soc_info` pointer. `rt2880_soc_dev_init()` allocates `soc_device_attribute` and registers family "Ralink".

State, persistence, and integration: state is early `soc_info`, exported `ralink_soc`, and a sysfs SoC device. Dependencies include RT2880 register constants and initcall ordering after `prom_init()`. Risks include strict chip-name matching, no fixed memory size, and `soc_device` reporting "invalid" if called without valid early state. Test signals are boot-time SoC type, sysfs SoC attributes, DT bus registration via `"ralink,r2880-soc"`, and detected RAM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/rt288x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/rt305x.c -->
# sources/distributed-fs/ceph-client/arch/mips/ralink/rt305x.c

Purpose: RT3050/RT3052/RT3350/RT3352/RT5350 SoC detection. It distinguishes related parts, derives memory sizing rules, and exposes SoC identity to Linux.

Important APIs and control flow: name-register helpers validate each chip family. `rt305x_get_soc_name()` sets `ralink_soc` and `soc_info->compatible`; RT3050 versus RT3052 is inferred from I-cache sets in CP0 config. `rt5350_get_mem_size()` decodes DRAM size from system config and panics on invalid encodings. `prom_soc_init()` builds `sys_type`, sets SDRAM base, and selects fixed or min/max memory detection by subtype. `rt305x_soc_dev_init()` registers a `soc_device`.

State, persistence, and integration: state feeds `plat_mem_setup()`, SoC feature macros, and sysfs SoC identity. Dependencies include CP0 config, sysc registers, and `rt305x.h` constants. Risks include heuristic RT3050/RT3052 detection, panic on unknown DRAM code, and hidden dependency that `soc_info_ptr` is initialized before `device_initcall()`. Test signals are correct compatible string, RAM size on RT5350, and sysfs `soc_id`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/rt305x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/rt3883.c -->
# sources/distributed-fs/ceph-client/arch/mips/ralink/rt3883.c

Purpose: RT3883 SoC identification and setup. It validates RT3883 chip ID registers, provides revision text, fills memory bounds, and registers SoC metadata.

Important APIs and control flow: `rt3883_get_soc_name0/1()` read the RT3883 chip ID registers. `rt3883_soc_valid()` gates `prom_soc_init()`, which sets `"ralink,rt3883-soc"`, formats version and ECO revision, sets SDRAM base/min/max, stores `ralink_soc = RT3883_SOC`, and saves `soc_info_ptr`. `rt3883_soc_dev_init()` publishes a `soc_device`.

State, persistence, and integration: persistent state is the shared Ralink SoC descriptor and sysfs SoC device. Dependencies include raw sysc access before OF remap, `ralink_regs`, and RT3883 constants. Risks include panic on ID mismatch and memory discovery relying on min/max probing rather than a register-derived size. Test signals are boot log text "Ralink RT3883", matching SoC sysfs data, and successful memory detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/rt3883.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/timer-gic.c -->
# sources/distributed-fs/ceph-client/arch/mips/ralink/timer-gic.c

Purpose: time initialization for Ralink systems using DT clocks and timer probing, typically with GIC-capable configurations.

Important APIs and control flow: `plat_time_init()` remaps core Ralink sysc/memc resources via `ralink_of_remap()`, initializes OF clocks with `of_clk_init(NULL)`, and invokes generic `timer_probe()` to bind the DT clocksource or clockevent providers.

State, persistence, and integration: it establishes early register mappings and clock providers before timer devices are probed. Dependencies include OF clock nodes, Ralink compatible sysc/memc nodes, and the generic clocksource framework. Risks include early panic from remap failure and no fallback if DT lacks usable timer clocks. Test signals are successful boot beyond time init, registered clocksource/clockevent devices, and no "Failed to remap core resources" panic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/timer-gic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/timer.c -->
# sources/distributed-fs/ceph-client/arch/mips/ralink/timer.c

Purpose: platform driver for the RT2880-style hardware timer. It binds from DT, maps timer registers, requests an IRQ, programs periodic mode, and keeps the timer interrupt acknowledged.

Important APIs and control flow: `struct rt_timer` tracks device, MMIO base, IRQ, clock-derived frequency, and divisor. `rt_timer_probe()` allocates state, gets IRQ/resource/clock, computes frequency after prescale, requests the IRQ, configures divisor 2, enables timer 0, and logs maximum frequency. The IRQ handler reloads `TMR0LOAD` and clears `TMRSTAT_TMR0INT`.

State, persistence, and integration: state is device-managed probe data plus hardware timer registers. Dependencies include a DT node compatible with `"ralink,rt2880-timer"`, a clock provider, and valid platform IRQ. Risks include ignoring errors from `rt_timer_request()` inside probe, no remove path, fixed periodic configuration, and divide behavior when clock rates are unexpectedly low. Test signals are driver bind logs, IRQ count increasing, and stable system ticks or timer interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ralink/timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/rb532/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/rb532/Makefile

Purpose: build rules for Mikrotik RB532 board support. It selects the board-specific interrupt, time, setup, PROM, GPIO, and platform-device objects, with an optional early serial object for 8250 console builds.

Important APIs and control flow: `obj-y` always includes `irq.o time.o setup.o prom.o gpio.o devices.o`. `serial.o` is included only under `CONFIG_SERIAL_8250_CONSOLE`.

State, persistence, and integration: it has no runtime state but controls which board hooks satisfy the MIPS architecture entry points. Dependencies include `CONFIG_SERIAL_8250_CONSOLE` and the rc32434 machine headers. Risks are link-time omission of early serial setup if console config changes and tight coupling among objects through globals such as `idt_cpu_freq` and exported latch helpers. Test signals are successful RB532 kernel link and expected object inclusion in build logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/rb532/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/rb532/devices.c -->
# sources/distributed-fs/ceph-client/arch/mips/rb532/devices.c

Purpose: registers RB532 platform devices for Ethernet, CompactFlash, NAND, LED, UART, watchdog, and button. It also manages the board latch used by NAND and LEDs.

Important APIs and control flow: `set_latch_u5()` and `get_latch_u5()` protect `dev3.state` with a spinlock and update the mapped latch byte. Static resources describe Korina Ethernet, CF, NAND, UART, and watchdog MMIO/IRQs. `rb532_cmd_ctrl()` drives NAND CLE/ALE latch bits. `plat_setup_devices()` probes CF availability from device-controller masks, maps DEV3, initializes NAND platform data, sets UART clock from `idt_cpu_freq`, registers GPIO lookup tables and platform devices, then creates property-backed NAND and button devices. `setup_kmac()` parses `kmac=`.

State, persistence, and integration: state includes latch value, platform device registrations, MTD partitions, MAC address, and GPIO software node metadata. Dependencies include `gpio.c` registering `gpio0`, rc32434 device controller registers, MTD NAND core, 8250 serial, Korina Ethernet, and gpiod lookup APIs. Risks include a likely index/comment mismatch when disabling CF (`rb532_devs[2]` is LED, not CF), direct MMIO assumptions, hard-coded NAND partitions, and MAC validation only logging failures. Test signals are platform device enumeration, NAND partitions, Ethernet MAC, CF presence, and working button GPIO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/rb532/devices.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/rb532/gpio.c -->
# sources/distributed-fs/ceph-client/arch/mips/rb532/gpio.c

Purpose: RB532 GPIO controller driver for 32 on-chip GPIOs. It exposes direction, value, IRQ mapping, interrupt level/status helpers, and alternate-function configuration.

Important APIs and control flow: `rb532_set_bit()` updates a bit in MMIO with local IRQs disabled. GPIO callbacks implement `get`, `set`, `direction_input`, `direction_output`, and `to_irq`. Exported `rb532_gpio_set_ilevel()`, `rb532_gpio_set_istat()`, and `rb532_gpio_set_func()` are used by IRQ and board code. `rb532_gpio_init()` maps the GPIO register block and registers the chip at arch init.

State, persistence, and integration: state is the mapped GPIO register base and registered `gpio_chip`. Dependencies include rc32434 register definitions, the IRQ controller's GPIO interrupt handling, and consumers using the `"gpio0"` label. Risks include no error handling around `gpiochip_add_data()`, global single-chip assumptions, and direct local IRQ masking instead of a lock. Test signals are `/sys/kernel/debug/gpio`, GPIO-backed CF/button/NAND ready lines, and correct GPIO interrupt polarity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/rb532/gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/rb532/irq.c -->
# sources/distributed-fs/ceph-client/arch/mips/rb532/irq.c

Purpose: interrupt controller support for the RC32434/RB532. It maps grouped interrupt pending/mask registers to Linux IRQs and dispatches CPU interrupt pins.

Important APIs and control flow: `intr_group[]` describes five interrupt groups with valid masks and KSEG1 register bases. `rb532_enable_irq()` and `rb532_disable_irq()` manipulate group masks and CPU IP bits; GPIO mapped interrupts clear GPIO status when disabled. `rb532_set_type()` supports high/low level GPIO IRQs. `arch_init_irq()` installs `rc32434_irq_type` for all RC32434 IRQs. `plat_irq_dispatch()` prioritizes CP0 timer IP7, then finds the highest pending grouped interrupt and calls `do_IRQ()`.

State, persistence, and integration: state lives in hardware interrupt mask registers and CP0 status/cause bits. It depends on GPIO helpers, MIPS IRQ descriptors, and rc32434 IRQ constants. Risks include fragile bit math around `fls()`, no locking around shared mask registers, and limited GPIO trigger type support. Test signals are boot-time IRQ initialization, timer interrupts, Ethernet/CF/GPIO IRQ delivery, and absence of spurious interrupt storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/rb532/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/rb532/prom.c -->
# sources/distributed-fs/ceph-client/arch/mips/rb532/prom.c

Purpose: RB532 PROM initialization. It parses firmware arguments, determines board variant and CPU frequency, maps DDR registers, and adds RAM to memblock.

Important APIs and control flow: `prom_setup_cmdline()` scans `fw_arg0/fw_arg1` argv, consumes `HZ=` for `idt_cpu_freq`, optionally filters `mem=`, sets `mips_machtype` from the board tag, and appends existing `arcs_cmdline`. `prom_init()` maps DDR registers, derives base and size from register field addresses, calls the command-line setup, and adds RAM excluding a small low and high reserved area.

State, persistence, and integration: state includes exported `idt_cpu_freq`, `mips_machtype`, `arcs_cmdline`, and memblock RAM. Dependencies include firmware tag syntax, rc32434 DDR structures, and later time/UART code using `idt_cpu_freq`. Risks include trusting raw firmware argv pointers, unusual DDR size calculation via register-address interpretation, and returning without memory setup if DDR mapping fails. Test signals are correct board name, CPU clock, command line, and usable RAM range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/rb532/prom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/rb532/serial.c -->
# sources/distributed-fs/ceph-client/arch/mips/rb532/serial.c

Purpose: early 8250 serial setup for RB532 console configurations.

Important APIs and control flow: a static `uart_port` describes UART0 at `REGBASE + UART0BASE`, KSEG1 mapped, with `UART0_IRQ`, memory I/O, and register shift 2. `setup_serial_port()` sets `uartclk` from exported `idt_cpu_freq` and calls `early_serial_setup()` as an `arch_initcall()`.

State, persistence, and integration: it registers one early serial port and depends on PROM parsing CPU frequency before arch initcalls. Integration is with the 8250 serial core and console support. Risks include duplicate registration with the platform `serial8250` device in `devices.c`, wrong baud if firmware frequency is absent or bad, and no failure logging. Test signals are early console output, ttyS0 registration, and correct baud behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/rb532/serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/rb532/setup.c -->
# sources/distributed-fs/ceph-client/arch/mips/rb532/setup.c

Purpose: RB532 platform setup, restart/halt hooks, PCI register mapping, and system type reporting.

Important APIs and control flow: `plat_mem_setup()` installs `_machine_restart`, `_machine_halt`, and `pm_power_off`, sets KSEG1 I/O base, maps PCI registers, clears a PCI control bit, optionally unmasks EPLD PCI interrupts, and clears wired TLB entries. `rb_machine_restart()` writes the reset register and jumps to the boot ROM vector. `get_system_type()` reports RB532A or RB532 from `mips_machtype`.

State, persistence, and integration: state includes exported `pci_reg`, global reboot hooks, and PCI controller register programming. Dependencies include PROM board detection, rc32434 PCI/EPLD symbols, and MIPS boot setup. Risks include a likely mask constant typo (`0xFFFFFF7`), halt as a tight loop, no recovery on PCI mapping failure beyond logging, and direct ROM jump reset. Test signals are PCI availability, reboot behavior, and correct `/proc/cpuinfo` machine string.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/rb532/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/rb532/time.c -->
# sources/distributed-fs/ceph-client/arch/mips/rb532/time.c

Purpose: RB532 timer frequency calibration. It sets the MIPS high-precision timer frequency from the firmware-provided CPU clock.

Important APIs and control flow: `cal_r4koff()` computes `mips_hpt_frequency = idt_cpu_freq * IDT_CLOCK_MULT / 2` and returns the per-HZ offset. `plat_time_init()` disables local interrupts, computes the offset, logs it and an estimated CPU frequency, then restores interrupts.

State, persistence, and integration: state is the global `mips_hpt_frequency` consumed by generic MIPS time code. It depends on `idt_cpu_freq` parsed by `prom.c` and the RC32434 counter running at half multiplied core speed. Risks include incorrect system time if firmware frequency is missing or malformed and no RTC fallback. Test signals are boot frequency log, stable jiffies, scheduler timing, and clock drift checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/rb532/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/Makefile

Purpose: build composition for SGI IP22/IP28 platform support. It always includes memory-controller, HPC, interrupt, timer, NVRAM, platform-device, reset, setup, and GIO bus code, with bus-error and EISA objects selected by config.

Important APIs and control flow: `obj-y` includes the core IP22 objects. `ip22-berr.o` is selected for `CONFIG_SGI_IP22`, `ip28-berr.o` for `CONFIG_SGI_IP28`, and `ip22-eisa.o` for `CONFIG_EISA`.

State, persistence, and integration: no runtime state is created by the Makefile, but it determines which `ip22_be_init()` implementation is linked. Dependencies include mutually appropriate SGI IP22/IP28 Kconfig choices. Risks include wrong bus-error handler for a machine variant and optional EISA code only present under config. Test signals are expected object inclusion and successful link for Indy, Indigo2, and IP28 builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-berr.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-berr.c

Purpose: IP22 bus-error handling for Indy/Indigo2. It captures SGI memory-controller, GIO, external I/O, and HPC3 error state, prints diagnostics, and converts fatal errors to SIGBUS or kernel die.

Important APIs and control flow: `save_and_clear_buserr()` snapshots MC/HPC/IOC registers and clears MC status. `print_buserr()` decodes CPU, GIO, HPC3, MC, and EISA error bits. `ip22_be_interrupt()` handles the bus-error IRQ path, logs EPC/RA from current IRQ regs, then calls `die_if_kernel()` and `force_sig(SIGBUS)`. `ip22_be_handler()` supports MIPS fixups and fatal exceptions. `ip22_be_init()` installs the handler.

State, persistence, and integration: state is last-error globals used during one diagnostic path. Dependencies include initialized `sgimc`, `sgioc`, `sgint`, and `hpc3c0`. Risks include destructive register reads, limited recovery, and assuming continuing after most bus errors is unsafe. Test signals are correct registration via `board_be_init`, decoded logs during induced bad PIO access, and successful exception-table fixups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-berr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-eisa.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-eisa.c

Purpose: minimal EISA support for SGI Indigo2. It probes EISA slots, initializes the EISA interface unit and 8259 IRQs, and bridges EISA interrupts into Linux.

Important APIs and control flow: `decode_eisa_sig()` reads and decodes the four-byte EISA vendor signature. `ip22_eisa_intr()` reads the EIU interrupt acknowledge byte, drains DMA status ports, dispatches valid IRQs, and resets PICs on out-of-range values. `ip22_eisa_init()` checks MC EISA-present status, scans four slots, programs EIU registers, resets external NMI/DMA state, calls `init_i8259_irqs()`, requests `SGI_EISA_IRQ`, and sets `EISA_bus = 1`.

State, persistence, and integration: state is hardware EISA configuration and global EISA bus presence. Dependencies include FullHouse/Indigo2 hardware, I/O port base setup, IOC/MC registers, and i8259 support. Risks include PIO-only support, comments noting missing DMA/ISA robustness, and out-of-range IRQ handling that only resets PICs. Test signals are EISA slot detection logs, successful IRQ request, and functioning low-end EISA devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-eisa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-gio.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-gio.c

Purpose: SGI GIO bus implementation and IP22 GIO slot probing. It exposes a Linux bus type for GIO devices and discovers graphics or expansion cards by safe bus-error-protected reads.

Important APIs and control flow: bus helpers implement device get/put, register/unregister, driver register/unregister, match, probe, remove, shutdown, sysfs attributes, and MODALIAS uevents. `gio_set_master()` and `ip22_gio_set_64bit()` update MC GIO arbitration flags. `ip22_gio_id()` uses `get_dbe()` on 32/16/8-bit reads to distinguish real IDs from pipelined phantom data. `ip22_check_gio()` detects GR2/GR3, Newport, and ID-table devices, allocates `gio_device`, assigns resource/IRQ, and registers it. `ip22_gio_init()` registers the bus and probes slots by chassis type.

State, persistence, and integration: state includes the global `gio` bus device, registered `gio_device` objects, and MC GIO mode bits. Dependencies include initialized `sgimc`, `hpc3c1`, board type, GIO headers, and exception-safe probing. Risks include direct probing of fragile hardware, manual reference handling, and hard-coded slot resources. Test signals are GIO probe logs, sysfs device attributes, driver autoload by `gio:<id>`, and working Newport/Impact/expansion devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-gio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-hpc.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-hpc.c

Purpose: initializes IP22 HPC3 and IOC register mappings and identifies Indy versus Indigo2 interrupt-controller layout.

Important APIs and control flow: `sgihpc_init()` maps both HPC3 chips, locates IOC through PBUS channel 6, configures the IOC PIO channel for 16-bit access, selects `sgint` from either PBUS channel 4 on FullHouse or IOC INT3 on Guiness, sets `system_type`, initializes software copies of write-only IOC reset/write registers, and writes them to hardware.

State, persistence, and integration: exported globals `hpc3c0`, `hpc3c1`, `sgioc`, `sgi_ioc_reset`, and `sgi_ioc_write` feed interrupt, reset, NVRAM, platform-device, and memory-controller code. Dependencies include IP22 board detection and fixed HPC3 physical addresses. Risks include assuming `ioremap()` cannot fail, write-only register shadow drift, and ordering requirement that HPC init precedes MC init. Test signals are correct system type, valid IOC/HPC-backed devices, and functioning interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-hpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-int.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-int.c

Purpose: IP22 INT2/INT3 interrupt setup and dispatch. It maps local interrupt status bits to Linux IRQs, handles cascaded mapped interrupts, bus errors, timers, and optional EISA initialization.

Important APIs and control flow: four `irq_chip` instances control local0/local1 and mapped local2/local3 masks. Dispatch helpers read `sgint->istat*`, `vmeistat`, and mask tables to pick the highest-priority IRQ, with a local0 workaround for a FIFO bug. `plat_irq_dispatch()` prioritizes R4k timer, local0, local1, bus error, and 8254 timer. `arch_init_irq()` builds mask-to-IRQ lookup tables, clears masks, initializes CPU IRQs, installs handlers for SGINT IRQ ranges, requests cascade IRQs, and optionally calls `ip22_eisa_init()`.

State, persistence, and integration: state includes lookup arrays and INT mask registers. Dependencies include `sgint` from `sgihpc_init()`, bus-error handler, MIPS CPU IRQ core, and optional EISA. Risks include fragile priority lookup tables, disabled LIO3 path, special non-shareable cascade requests, and hardware errata workaround behavior. Test signals are interrupt routing for serial, SCSI, Ethernet, GIO, panel, timer, and EISA devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-int.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-mc.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-mc.c

Purpose: SGI IP22 memory-controller initialization. It maps the MC, configures parity, write buffering, RPSS timing, GIO arbitration, and memory discovery.

Important APIs and control flow: bank helpers decode memory config base/size. `probe_memory()` is a no-op on IP28/32-bit builds where PROM owns usable memory, otherwise it adds valid banks above segment 1 to memblock. `sgimc_init()` maps `sgimc`, disables watchdog, clears error status, sets parity/check bits except on IP28, programs write-buffer depth and divider, builds GIO64 arbitration flags based on FullHouse/Guiness and board revision, writes `giopar`, and probes memory. IP28 also defines `prom_cleanup()` to switch ECC/WR_COL mode after ARCS is no longer needed.

State, persistence, and integration: exported `sgimc` and MC register configuration feed GIO, bus-error, timer, and platform code. Dependencies include `sgihpc_init()` having selected board type and IOC registers. Risks include direct hardware tuning, conditional memory discovery differences, and cache/ECC mode changes that can be hard to test. Test signals are MC revision log, correct memblock RAM, stable GIO DMA, and no parity/bus-error storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-mc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-nvram.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-nvram.c

Purpose: reads IP22 NVRAM or serial EEPROM values, primarily for MAC addresses and firmware environment-derived data.

Important APIs and control flow: bit-banged EEPROM macros control chip select, clock, data out, and protection bits. `eeprom_cmd()` shifts an 11-bit command/register sequence. `ip22_eeprom_read()` issues an EEPROM read and clocks out 16 bits. `ip22_nvram_read()` selects Microwire EEPROM on FullHouse or DS1386 BBRAM word reads on Indy.

State, persistence, and integration: no Linux state is stored, but reads persistent board EEPROM/BBRAM contents. Dependencies include initialized `hpc3c0`, board type, and stable early delay loops. Risks include busy-wait timing sensitivity, no locking for shared EEPROM control, read-only support, and direct raw access during early boot. Test signals are correct Ethernet MAC extraction and stable NVRAM values across boots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-nvram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-platform.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-platform.c

Purpose: registers IP22 platform devices for SCSI, Ethernet, audio, buttons, RTC, and Zilog serial.

Important APIs and control flow: device initcalls create `sgiwd93` SCSI devices with HPC register pointers, primary and optional secondary `sgiseeq` Ethernet devices with MAC addresses from NVRAM/EEPROM, `sgihal2`, optional `sgibtns`, `rtc-ds1286`, and `ip22zilog`. Secondary Ethernet is enabled only when a second HPC is present and after MC/HPC GIO settings are adjusted.

State, persistence, and integration: state is platform-device registration and platform data containing IRQs, register pointers, DMA masks, and MAC addresses. Dependencies include HPC/MC/NVRAM initialization, bus-error-safe detection, and platform drivers for SGI devices. Risks include using `IS_ERR()` on integer return values in simple-device helpers, hard-coded NVRAM offsets, and direct side effects on GIO arbitration for mezzanine Ethernet. Test signals are device enumeration, correct eth MACs, SCSI detection, RTC registration, and serial console availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-reset.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-reset.c

Purpose: IP22 restart, halt, power button, panic LED, and poweroff handling. It emulates IRIX-like front-panel shutdown behavior.

Important APIs and control flow: `_machine_restart`, `_machine_halt`, and `pm_power_off` are set in `reboot_setup()`. `panel_int()` handles front-panel interrupts, debounces power-button state, and calls `power_button()`. `power_button()` signals init through `kill_cad_pid(SIGINT, 1)`, starts LED blinking, and arms a forced poweroff timer. `panic_event()` switches to faster blinking. `sgi_machine_power_off()` programs RTC watchdog/alarm state and writes panel power bits in an infinite loop.

State, persistence, and integration: state includes timers, `machine_state`, IOC reset shadow bits, panic notifier registration, and front-panel IRQ ownership. Dependencies include `sgioc`, `sgint`, `hpc3c0`, DS1286 RTC registers, and MIPS reboot hooks. Risks include timer-driven poweroff races, no graceful halt if firmware unavailable, FullHouse LED caveat, and direct infinite loops. Test signals are reboot, halt to ARCS, power button shutdown, panic LED blink, and forced timeout poweroff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-setup.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-setup.c

Purpose: top-level IP22 memory/platform setup. It wires bus-error handling, initializes HPC and MC hardware, configures EISA I/O ports, and chooses the preferred console from ARCS variables.

Important APIs and control flow: `plat_mem_setup()` sets `board_be_init`, calls `sgihpc_init()` before `sgimc_init()`, optionally enables board cache, maps the EISA I/O port window, reads `console`, `ConsoleOut`, and `dbaud` ARCS variables, then selects ttyS or ARC console behavior.

State, persistence, and integration: state includes global platform hardware mappings, console preference, and `prom_flags`. Dependencies include ARCS firmware variables, SGI memory/HPC init ordering, and MIPS console setup. Risks include a fixed huge I/O remap range, reliance on firmware strings, and console selection corner cases when graphics lacks keyboard. Test signals are correct early console, successful MC/HPC logs, and boot on Indy/Indigo2 variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-time.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-time.c

Purpose: calibrates the R4k counter on IP22 using the SGI 8254-compatible timer and handles unexpected 8254 interrupts.

Important APIs and control flow: `dosample()` programs timer counter 2, samples CP0 count until the latched top byte reaches zero, stops the counter, and rounds the result. `plat_time_init()` primes caches, obtains two or three samples, averages if needed, logs the CPU rate, sets `mips_hpt_frequency`, and calls `setup_pit_timer()` on FullHouse. `indy_8254timer_irq()` logs unexpected 8254 interrupts and drops to ARC interactive mode.

State, persistence, and integration: state is `mips_hpt_frequency` and optional PIT timer setup. Dependencies include `sgint` timer registers and ARCS fallback. Risks include busy-wait calibration sensitivity, fatal handling of 8254 interrupts, and clock drift if samples are inconsistent. Test signals are calibration log, stable scheduler clock, and timer IRQ delivery through R4k compare.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip28-berr.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip28-berr.c

Purpose: enhanced IP28 bus-error handler. It captures MC/HPC/DMA/cache-tag state, distinguishes fatal errors from discardable speculative bus errors, and exposes counters for diagnostics.

Important APIs and control flow: `save_and_clear_buserr()` snapshots CPU/GIO/error registers, HPC3 DMA descriptors, Ethernet/SCSI/PBDMA state, and cache tags around the error address. `print_buserr()` decodes hardware status and cache tags. `check_microtlb()`, `check_vdma_memaddr()`, and `check_vdma_gioaddr()` correlate errors with virtual DMA translation. `ip28_be_interrupt()` rejects fatal causes, HPC/EISA errors, non-address memory errors, and DMA descriptor hits, otherwise discards likely speculative errors. `ip22_be_init()` installs `ip28_be_handler()`, and `ip28_debug_be` enables verbose discard logging.

State, persistence, and integration: state includes diagnostic counters, last hardware snapshots, and optional debug flag. Dependencies include R4k cache tag operations, MC/HPC/IOC globals, and MIPS bus-error semantics. Risks include complex hardware heuristics, infinite fatal behavior through `die_if_kernel()`/SIGBUS paths, and disabled locking around diagnostics. Test signals are counters from `ip28_show_be_info()`, successful exception-table fixups, and safe discard of known speculative bus errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip28-berr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/Kconfig -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/Kconfig

Purpose: IP27-specific configuration for SGI Origin/Onyx NUMA systems. It selects node addressing mode and optional mapped-kernel/text-replication support.

Important APIs and control flow: the "Node addressing mode" choice selects `SGI_SN_M_MODE` by default or `SGI_SN_N_MODE`. `MAPPED_KERNEL` changes kernel load mapping for NUMA text replication. `REPLICATE_KTEXT` selects `MAPPED_KERNEL` and enables per-node kernel text copies.

State, persistence, and integration: no runtime state is created directly, but these options determine address decoding, boot compatibility checks, and memory layout logic in IP27 code. Dependencies include hardware firmware mode matching the kernel config. Risks include boot-time panic if N/M mode is mismatched and memory cost or mapping bugs with text replication. Test signals are Kconfig selection, `plat_mem_setup()` mode log, and successful boot on the target Origin mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/Makefile

Purpose: build composition for SGI IP27 support. It links bus-error, IRQ, init, KL config, NUMA, memory, NMI, reset, timer, and Crosstalk code, with optional early console and SMP support.

Important APIs and control flow: `obj-y` lists the mandatory IP27 objects. `ip27-console.o` is selected by `CONFIG_EARLY_PRINTK`; `ip27-smp.o` is selected by `CONFIG_SMP`.

State, persistence, and integration: no runtime state is created, but object selection controls whether `ip27_smp_ops` and early `prom_putchar()` are available. Dependencies include IP27 architecture config and SMP/early-printk choices. Risks include missing SMP hooks in a multi-CPU kernel or no early console for firmware debugging. Test signals are successful link and expected symbols in the built image.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-berr.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-berr.c

Purpose: IP27 HUB bus-error handling. It decodes HUB error status registers for the local slice and installs the MIPS bus-error handler.

Important APIs and control flow: `dump_hub_information()` parses `PI_ERR_STATUS0/1` into address, command, supplemental field, RRB request, overrun, and error type. `ip27_be_handler()` allows exception-table fixups, otherwise logs slice, instruction/data type, pending error bits, dumps HUB information, registers, and TLBs, then loops forever before the unreachable SIGBUS path. `ip27_be_init()` installs the handler, clears pending errors, disables error stack, and enables SYSAD checks.

State, persistence, and integration: state is HUB error control registers and the global MIPS BE handler. Dependencies include local HUB access macros and `ip27-common.h` setup. Risks include fatal infinite loop on non-fixup errors, limited Bridge error initialization, and direct HUB register assumptions. Test signals are handler installation, successful fixup on safe probing, and detailed HUB logs on injected errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-berr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-common.h -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-common.h

Purpose: shared IP27 declarations for cross-file platform hooks.

Important APIs and control flow: it declares `master_nasid`, CPU/node probing, HUB RTC clockevent/source setup, NMI installation, IPI setup, bus-error init, reboot setup, SMP ops, first-free-node memory calculation, per-CPU init, and kernel text replication helpers.

State, persistence, and integration: it centralizes the IP27 internal interface between init, memory, SMP, IRQ, timer, NMI, and reset objects. Dependencies include SGI SN NASID types and `plat_smp_ops`. Risks are tight coupling through global functions and no type-level ownership boundaries for hardware state. Test signals are compile-time consistency and successful linking of IP27 objects under SMP and non-SMP configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-console.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-console.c

Purpose: early console output for IP27 through the IOC3 UART selected by firmware KL console information.

Important APIs and control flow: `console_uart()` chooses `master_nasid` if known or the current NASID, obtains `KL_CONFIG_CH_CONS_INFO(nasid)->memory_base`, casts it to IOC3, and returns UART A registers. `prom_putchar()` polls line-status THR-empty and writes one byte.

State, persistence, and integration: no durable state is stored; it reads KL config and IOC3 MMIO. Dependencies include early KL config validity, `master_nasid`, and IOC3 register layout. Risks include blocking forever if UART status never becomes empty and hard-coded UART A use. Test signals are working early printk output before full serial driver initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-console.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-init.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-init.c

Purpose: main IP27 boot initialization. It registers SMP operations, validates firmware node mode, initializes per-hub/per-CPU state, and starts PROM memory discovery.

Important APIs and control flow: `per_hub_init()` records CPUs on a hub, programs CRB timeout, initializes HUB RTC, copies exception vectors to nonzero nodes, and sets CALIAS size. `per_cpu_init()` masks interrupts, initializes the local hub, logs CPU speed, installs IPIs and NMI handler, and enables HUB pending IRQs. `plat_mem_setup()` registers SMP ops, sets reboot hooks, logs CPU presence, validates N/M mode against config, and sets I/O base. `prom_init()` imports command line and calls `prom_meminit()`.

State, persistence, and integration: state includes `master_nasid`, `sn_cpu_info`, hub CPU masks, HUB timeout/RTC registers, and MIPS I/O resource limits. Dependencies include firmware GDA/KL config, HUB registers, timer, SMP, reset, and memory code. Risks include panic on N/M mismatch, per-hub one-time mask assumptions, and early multi-node exception-vector copying. Test signals are node/CPU logs, successful per-CPU IRQ enablement, and completed `prom_meminit()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-irq.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-irq.c

Purpose: IP27 HUB interrupt-domain and dispatch implementation. It allocates HUB interrupt levels, manages per-CPU HUB masks, supports affinity, and handles pending HUB interrupts.

Important APIs and control flow: `alloc_level()` reserves a bit in `hub_irq_map`. `enable_hub_irq()` and `disable_hub_irq()` update per-CPU mask arrays and write slice mask registers. `setup_hub_mask()` chooses an online CPU in the target hub. `set_affinity_hub_irq()` retargets active IRQs. `hub_domain_alloc()` allocates chip data, assigns a hardware level, configures `handle_level_irq`, clears pending state, and sets descriptor node/affinity. Chained handlers process `PI_INT_PEND0/1`, handle SMP reschedule/call IPIs specially, or dispatch through `generic_handle_domain_irq()`. `arch_init_irq()` creates the default HUB domain and chains CPU IRQs.

State, persistence, and integration: state includes the HUB IRQ bitmap, per-CPU enable masks, irq-domain mappings, and hardware mask registers. Dependencies include hub CPU masks from memory/init code, generic IRQ domains, SMP IPI handlers, and SN IRQ allocation info. Risks include no freeing of reserved bitmap bits in `hub_domain_free()`, affinity fallback behavior, and masking complexity around recursive interrupts. Test signals are domain allocation, IPI delivery, device IRQ affinity, and no spurious HUB interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-klconfig.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-klconfig.c

Purpose: helper searches over SGI KL configuration boards and components.

Important APIs and control flow: `find_component()` returns the next component of a requested type after an optional current component, validating that the current pointer belongs to the board. `find_first_component()` is a convenience wrapper. `find_lboard()` scans linked boards for an exact board type. `find_lboard_class()` scans for a board with the same KL class.

State, persistence, and integration: it has no persistent state and reads firmware KL config structures in memory. Dependencies include KL macros such as `KLCF_NUM_COMPS`, `KLCF_COMP`, and `KLCF_NEXT`. Risks include trusting firmware-provided linked structures and returning NULL on pointer mismatch after logging only. Test signals are successful CPU, memory, router, and xbow discovery by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-klconfig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-klnuma.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-klnuma.c

Purpose: kernel text replication support for IP27 NUMA. It computes which nodes host replicated read-only text and records per-node kernel variable mappings.

Important APIs and control flow: `setup_replication_mask()` always marks node 0 and, under `CONFIG_REPLICATE_KTEXT`, marks all online nodes, then stores the mask in `GDA`. `set_ktext_source()` writes `kern_vars` with magic, read-only NASID, read-write NASID, and base addresses. `copy_kernel()` copies `_stext.._etext` to the destination node. `replicate_kernel_text()` assigns/copies sources for each online node. `node_getfirstfree()` returns the first free PFN accounting for mapped kernels, replicated text, or PROM stack areas.

State, persistence, and integration: state includes `ktext_repmask`, GDA pointer, per-hub `kern_vars`, and copied text pages. Dependencies include mapped-kernel address macros, online node map, and memory initialization. Risks include simplistic placement, memcpy instead of BTE, headless-node concerns noted in comments, and memory layout sensitivity. Test signals are replication logs, correct node first-free PFNs, and successful SMP boot with replicated text enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-klnuma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-memory.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-memory.c

Purpose: IP27 NUMA memory discovery and topology setup. It replaces bogus ARC memory data with KL config-derived node, router, and bank information.

Important APIs and control flow: `gen_region_mask()` builds HUB region presence. Router traversal computes `__node_distances` and dumps topology. `slot_psize_compute()` derives slot PFNs from KL memory bank sizes. `mlreset()` sets `master_nasid`, probes CPUs, initializes topology, region masks, replication mask, and per-node HUB region/CALIAS registers. `szmem()` adds node-local memblock ranges while avoiding configurations where memmap metadata would overrun slot 0. `node_mem_init()` places `node_data` and `hub_data` at the node's first free PFN and reserves that area. `prom_meminit()` orchestrates all of this and installs a null node for offline nodes.

State, persistence, and integration: state includes exported `__node_data`, `__node_distances`, memblock nodes, node maps, and HUB region registers. Dependencies include KL boards, GDA, SMP CPU probing, ktext replication, and Linux NUMA zones. Risks include complex firmware topology trust, hacky DIMM bank sizing, fixed assumptions about bootmem fitting in slot 0, and large platform-specific address math. Test signals are topology dump, memblock node ranges, NUMA distances, CPU masks per node, and successful zone initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-nmi.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-nmi.c

Purpose: IP27 NMI registration and crash dump support. It installs per-slice NMI callbacks and prints firmware-saved CPU register frames and HUB IRQ state for all nodes.

Important APIs and control flow: `install_cpu_nmi_handler()` writes the NMI magic and callback address into the per-node/slice NMI area if firmware has not already done so. `nmi_cpu_eframe_save()` formats saved GPRs, EPC, ErrorEPC, status, cause, BadVA, cache error, and NMI status. `nmi_dump_hub_irq()` prints per-slice mask and pending registers. `nmi_dump()` serializes through `nmi_lock`, waits for participating CPUs when real NMI signaling is disabled, saves all frames, and resets the local HUB port.

State, persistence, and integration: state includes NMI memory areas, an arch spinlock, and optional atomic participation count. Dependencies include SN NMI layout, online node map, HUB registers, and per-CPU slice mappings. Risks include disabled `REAL_NMI_SIGNAL` alternate code, potential indefinite wait for CPUs, and final local reset after dumping. Test signals are NMI handler installation, emergency register dumps on NMI, and system reset after dump.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-nmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-reset.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-reset.c

Purpose: reboot, halt, and poweroff hooks for SGI IP27 systems.

Important APIs and control flow: `ip27_reboot_setup()` assigns `_machine_restart`, `_machine_halt`, and `pm_power_off`. Restart logs the initiating CPU, stops SMP, and resets the local HUB port. Halt stops SMP, writes `PROMOP_RESTART` to each online node's PROMOP register, then resets the local HUB port. Poweroff is a stub infinite loop.

State, persistence, and integration: state is global machine hook registration and HUB/PROMOP register side effects. Dependencies include SMP stop support, online nodes, and SN HUB reset registers. Risks include no implemented poweroff, alternative reboot path disabled under `#if 0`, and reset relying on local port reset propagation. Test signals are reboot/halt behavior and expected "Reboot started" log.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-smp.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-smp.c

Purpose: IP27 SMP CPU discovery, IPI delivery, secondary launch, and SMP lifecycle hooks.

Important APIs and control flow: `cpu_node_probe()` clears node maps, walks GDA NASID table, marks nodes online/possible, and calls `node_scan_cpus()` to map enabled KL CPUs to logical CPUs, NASIDs, slices, and speeds. `intr_clear_all()` clears HUB masks and pending bits on secondary nodes. IPI functions send reschedule/call interrupts by writing HUB interrupt bits. `ip27_boot_secondary()` launches a CPU through PROM `LAUNCH_SLAVE()` with stack and thread-info pointers. `ip27_smp_setup()` clears interrupts on nonboot nodes, replicates kernel text, and maps boot CPU. The `ip27_smp_ops` structure plugs these into generic MIPS SMP.

State, persistence, and integration: state includes CPU possible maps, logical/physical mappings, `sn_cpu_info`, HUB pending registers, and replicated text. Dependencies include firmware KL CPU structures, GDA, HUB IPIs, timer init, and `per_cpu_init()`. Risks include `cpus_found` static mapping assumptions, NR_CPUS truncation, and firmware launch dependency. Test signals are discovered CPU count, secondary boot, scheduler and call-function IPIs, and per-CPU timer initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-timer.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-timer.c

Purpose: IP27 HUB real-time counter clocksource and per-CPU clockevent support.

Important APIs and control flow: `rt_next_event()` programs the slice-specific `PI_RT_COMPARE` register and reports late events. `hub_rt_counter_handler()` acknowledges the pending bit and calls the clockevent handler. `hub_rt_clock_event_init()` initializes a per-CPU one-shot clockevent at a fixed 800 ns cycle assumption. `hub_rt_clocksource_init()` registers a 52-bit continuous clocksource and sched_clock reader. `plat_time_init()` initializes source, global IRQ setup, and boot CPU event. `hub_rtc_init()` enables RT counters and clears pending state for the current node.

State, persistence, and integration: state includes per-CPU clockevent devices, names, HUB RT registers, and global clocksource. Dependencies include HUB timer IRQs, cputoslice/cputonasid mappings, and IRQ setup. Risks include hard-coded cycle time, cpuless-node skip behavior, and late-event handling under high interrupt latency. Test signals are registered `HUB-RT` clocksource, per-CPU `hub-rt` events, scheduler ticks, and no timer drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-xtalk.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-xtalk.c

Purpose: IP27 Crosstalk/Xtalk probing and Bridge platform-device creation. It discovers Bridge/XBridge widgets on each node and creates companion 1-Wire NIC and PCI bridge platform devices.

Important APIs and control flow: `bridge_platform_create()` allocates `sgi_w1` and `xtalk-bridge` platform devices, builds NIC/MMIO/IO resources, copies platform data, and unwinds on errors. `probe_one_port()` reads widget ID and creates Bridge devices for recognized Bridge/XBridge part numbers. `xbow_probe()` finds KL XBow data, elects the master HUB widget, and probes enabled I/O ports only on the owning NASID. `xtalk_probe_node()` checks the HUB LLP link, reads widget 0, then handles direct Bridge or XBow/XXBow. `xtalk_init()` runs for each online node at arch init.

State, persistence, and integration: state is platform-device registration and bridge resources per widget/NASID. Dependencies include KL config, HUB raw widget address macros, Bridge platform driver, and SGI 1-Wire driver. Risks include volatile raw widget reads, partial device creation on memory pressure, master-widget election assumptions, and no removal path. Test signals are `xtalk:n/w bridge widget` logs, PCI bridge enumeration, and NIC 1-Wire device creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip27/ip27-xtalk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/Makefile

Purpose: build rules for SGI IP30 Octane support. It links HEART interrupt, power, setup, timer, and Xtalk code, with optional early console and SMP.

Important APIs and control flow: `obj-y` includes `ip30-irq.o ip30-power.o ip30-setup.o ip30-timer.o ip30-xtalk.o`. `ip30-console.o` is conditional on `CONFIG_EARLY_PRINTK`; `ip30-smp.o` is conditional on `CONFIG_SMP`.

State, persistence, and integration: no runtime state, but object selection controls machine hooks, timer/IRQ setup, and SMP operations. Dependencies include SGI IP30 config and optional SMP/early-printk choices. Risks include missing early debugging if early printk is off and no SMP operations if config mismatches hardware. Test signals are successful link and expected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-common.h -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-common.h

Purpose: shared IP30 constants and declarations for HEART interrupt lines and SMP/per-CPU hooks.

Important APIs and control flow: it defines power, HEART L0/L1/L2/timer/error CPU IRQ numbers and declares `ip30_install_ipi()`, `ip30_smp_ops`, and `ip30_per_cpu_init()`.

State, persistence, and integration: no state is stored; it provides the internal contract between IP30 IRQ, setup, timer, and SMP code. Dependencies include HEART interrupt definitions and MIPS CPU IRQ base. Risks are hard-coded interrupt-line mapping and tight compile-time coupling. Test signals are compile-time consistency and correct IRQ numbers in boot logs/interrupt tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-console.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-console.c

Purpose: early IP30 console output through the BaseIO IOC3 UART.

Important APIs and control flow: `console_uart()` uses the fixed XKPHYS IOC3 address `0x900000001f600000` and returns UART A. `prom_putchar()` polls line-status THR-empty with `cpu_relax()` and writes the byte.

State, persistence, and integration: no persistent state; it performs direct MMIO writes before full device setup. Dependencies include the BaseIO IOC3 fixed address and early mapped access. Risks include blocking forever if IOC3 is absent or status never changes, and hard-coded UART A. Test signals are early printk characters on IP30 serial console.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-console.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-irq.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-irq.c

Purpose: SGI IP30 HEART interrupt-controller support. It creates a HEART irq-domain, handles normal/error cascades, supports affinity, and reserves special HEART bits.

Important APIs and control flow: `heart_alloc_int()` reserves interrupt bits. `ip30_normal_irq()` reads ISR/IMR, handles SMP reschedule/call IPIs specially, or dispatches the first pending bit through the irq-domain. `ip30_error_irq()` masks and acknowledges HEART L4 error interrupts, logs ISR/IMR/CAUSE and memory error address, then panics on cause. IRQ chip methods ack/mask/unmask bits in per-CPU IMRs, and affinity retargets chip data to another online CPU. `heart_domain_alloc()` creates level IRQ mappings. `ip30_install_ipi()` enables per-CPU IPI bits. `arch_init_irq()` masks/acks all HEART IRQs, enables error masks, reserves hardware/software bits, creates the domain, and chains CPU IRQ lines.

State, persistence, and integration: state includes `heart_irq_map`, per-CPU enable masks, irq-domain mappings, and HEART IMR/ISR registers. Dependencies include initialized `heart_regs`, CPU online masks, SMP IPI handlers, and generic IRQ domains. Risks include `heart_domain_alloc()` not setting an initial CPU explicitly, fatal panic on HEART cause, and affinity selecting an invalid CPU if no mask intersection exists. Test signals are HEART domain creation, IPIs, device IRQ delivery, error IRQ panic diagnostics, and interrupt affinity updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-power.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-power.c

Purpose: IP30 restart hook using HEART cold reset.

Important APIs and control flow: `ip30_reboot_setup()` installs `_machine_restart` at subsys init. `ip30_machine_restart()` sets `HM_COLD_RST` in the HEART mode register and never returns.

State, persistence, and integration: state is machine restart hook registration and a write to HEART mode. Dependencies include valid `heart_regs` from setup. Risks include no halt/poweroff implementation here and reset failure if HEART registers are inaccessible. Test signals are reboot triggering HEART cold reset and no return from restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-setup.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-setup.c

Purpose: IP30 platform setup for HEART mapping, memory discovery, CPU timer calibration, per-CPU initialization, and I/O base setup.

Important APIs and control flow: global `heart_regs` points at `HEART_XKPHYS_BASE`. `ip30_mem_init()` walks HEART memory-bank config registers, computes base/size, and frees RAM above the PROM-reported 1 GB window into memblock. `ip30_cpu_time_init()` compares CP0 count against HEART count over 0.1 seconds to derive `mips_hpt_frequency`. `ip30_per_cpu_init()` masks interrupts, calibrates CPU time, installs IPIs under SMP, and enables HEART chained IRQs. `plat_mem_setup()` runs memory init, sets `PROM_FLAG_DONT_FREE_TEMP`, registers SMP ops or initializes the boot CPU, and sets the I/O port base.

State, persistence, and integration: state includes HEART MMIO pointer, memblock additions, `mips_hpt_frequency`, per-CPU IRQ state, and MIPS I/O resources. Dependencies include HEART registers, ARCS memory limitations, SMP code, and IRQ setup. Risks include `memblock_phys_free()` assumptions about earlier reserved ranges, busy-wait calibration, and hard lock note if PROM temp memory is freed. Test signals are detected memory log, CPU MHz log, HEART IRQ enablement, and boot with memory above 1 GB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-smp.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-smp.c

Purpose: SMP support for SGI IP30. It enumerates CPUs from MPCONF, sends HEART IPIs, and launches secondary CPUs through firmware-visible structures.

Important APIs and control flow: `ip30_smp_setup()` scans two MPCONF slots for `MPCONF_MAGIC`, marks CPUs possible, sets logical maps, logs slot IDs, and sets coherent-on-write cache mode. IPI helpers write HEART set-ISR bits for reschedule or call-function actions. `ip30_smp_boot_secondary()` fills stack/thread pointers in the target `mpconf`, uses `mb()`, and writes `smp_bootstrap` to `launch`. Secondary init calls `ip30_per_cpu_init()`, and finish enables the CP0 compare IRQ and local interrupts.

State, persistence, and integration: state includes CPU possible/logical maps, MPCONF launch fields, HEART IPI bits, and CP0 cache mode. Dependencies include firmware MPCONF at a fixed address, HEART registers, generic MIPS SMP, and IP30 timer setup. Risks include only two physical CPUs supported, direct fixed-address firmware structure access, and reliance on cache coherency mode for R14000 stability. Test signals are detected CPU count, secondary CPU online, IPI operation, and no userland instruction bus errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-timer.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-timer.c

Purpose: IP30 timer support. It uses the MIPS CP0 compare interrupt for clock events and the HEART counter as a high-quality clocksource and sched_clock.

Important APIs and control flow: `ip30_heart_counter_read()` and `ip30_heart_read_sched_clock()` read `heart_regs->count`. `ip30_heart_clocksource_init()` registers a 52-bit HEART clocksource at `HEART_CYCLES_PER_SEC` and sched_clock. `plat_time_init()` installs the CP0 compare interrupt as a percpu clockevent, requests `c0_compare_interrupt`, enables it, and initializes HEART clocksource.

State, persistence, and integration: state includes `cp0_timer_irq_installed`, registered percpu IRQ, and the global `ip30_heart_clocksource`. Dependencies include initialized HEART registers and generic MIPS R4k clockevent. Risks include warning-only request failure, fixed HEART frequency, and needing per-CPU IRQ enablement during SMP finish. Test signals are HEART clocksource in `/sys/devices/system/clocksource`, timer IRQ counts, and stable sched_clock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-xtalk.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-xtalk.c

Purpose: IP30 XIO/Crosstalk widget probing. It discovers active XBow links and registers Bridge/XBridge PCI bridge and 1-Wire NIC platform devices.

Important APIs and control flow: `bridge_platform_create()` creates `sgi_w1` and `xtalk-bridge` platform devices with resources based on the widget's small-window address and HEART interrupt address. `xbow_widget_active()` reads XBow link status. `xtalk_init_widget()` reads widget ID and creates bridge devices for Bridge/XBridge parts. `ip30_xtalk_init()` walks widgets from BaseIO downward so BaseIO IOC3 becomes `eth0`.

State, persistence, and integration: state is platform-device registration and bridge platform data. Dependencies include fixed IP30 XBow/HEART widget IDs, Bridge platform driver, SGI 1-Wire driver, and raw XIO MMIO. Risks include direct reads from inactive widgets if link status is wrong, partial registration cleanup complexity, and hard-coded ordering to preserve network naming. Test signals are xtalk bridge logs, PCI bridge discovery, BaseIO IOC3 as eth0, and bridge NIC IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip30/ip30-xtalk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/Makefile

Purpose: build composition for SGI IP32/O2 platform support. It includes bus-error, interrupt, platform-device, setup, reset, CRIME, memory, and DMA translation code.

Important APIs and control flow: `obj-y` adds `ip32-berr.o ip32-irq.o ip32-platform.o ip32-setup.o ip32-reset.o crime.o ip32-memory.o ip32-dma.o`.

State, persistence, and integration: no runtime state is created, but this ensures CRIME/MACE globals, DMA translation, platform devices, and machine hooks are linked. Dependencies include SGI IP32 config. Risks are link-time platform completeness only, with no optional object guards here. Test signals are successful IP32 kernel link and presence of CRIME/MACE setup symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/crime.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/crime.c

Purpose: initializes CRIME and MACE register mappings for SGI O2 and handles CRIME memory/CPU error interrupts.

Important APIs and control flow: `crime_init()` maps the MACE PCI low I/O window, CRIME registers, and MACE registers, reads CRIME ID/revision, and logs it. `crime_memerr_intr()` decodes memory error status/address, ECC syndrome/check bits, fatal multiple/hard errors, access source fields, clears status, and panics on fatal errors. `crime_cpuerr_intr()` logs and clears CPU error status/address.

State, persistence, and integration: state includes global `crime` and exported `mace` MMIO pointers. Dependencies include fixed CRIME/MACE physical addresses, IP32 memory init calling `crime_init()`, and IRQ code requesting error IRQs. Risks include assuming `ioremap()` succeeds, panic on fatal memory errors, and direct MMIO clearing. Test signals are CRIME ID log, MACE-backed device operation, and error IRQ diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/crime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-berr.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-berr.c

Purpose: IP32 bus-error exception handling. It installs a fatal MIPS bus-error handler with fixup support.

Important APIs and control flow: `ip32_be_handler()` returns `MIPS_BE_FIXUP` for fixup-capable accesses. Otherwise it logs instruction/data bus-error type and EPC, dumps registers and all TLB entries, then loops forever before the unreachable SIGBUS path. `ip32_be_init()` installs this handler.

State, persistence, and integration: state is the global MIPS bus-error handler set through `board_be_init`. Dependencies include setup assigning `board_be_init = ip32_be_init` and MIPS trap code. Risks include fatal infinite loop for non-fixup errors and minimal CRIME-specific context compared with error IRQ handlers. Test signals are safe exception-table probing and verbose dumps on bad bus access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-berr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-common.h -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-common.h

Purpose: shared IP32 declarations for CRIME initialization, error IRQ handlers, bus-error setup, and poweroff preparation.

Important APIs and control flow: it declares `crime_init()`, `crime_memerr_intr()`, `crime_cpuerr_intr()`, `ip32_be_init()`, and `ip32_prepare_poweroff()`.

State, persistence, and integration: no state; it links CRIME, IRQ, setup, reset, memory, and platform-device code. Dependencies include Linux interrupt types. Risks are close coupling through globals and externally registered platform callbacks. Test signals are compile-time consistency and successful use of these functions across IP32 objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-dma.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-dma.c

Purpose: DMA address translation for SGI O2's split CPU/device memory view.

Important APIs and control flow: `phys_to_dma()` masks physical addresses to the low 1 GB window and adds `CRIME_HI_MEM_BASE` for non-PCI devices passed as `dev == NULL`. `dma_to_phys()` masks DMA addresses and maps addresses at or above 256 MB back into the high CRIME memory base.

State, persistence, and integration: no state; these are architecture DMA translation hooks used by DMA-direct. Dependencies include device callers distinguishing PCI devices from native MACE/CRIME devices by `dev` presence. Risks include subtle incorrect mappings if a non-PCI device passes a non-NULL device or if memory layout assumptions change. Test signals are successful PCI and MACE DMA to high memory, especially Ethernet/audio/SCSI transfers above 256 MB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-irq.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-irq.c

Purpose: IP32 CRIME/MACE interrupt controller implementation. It maps CRIME, MACE PCI, and MACE ISA interrupts to Linux IRQs and dispatches CP0 IRQ lines.

Important APIs and control flow: mask/unmask routines update `crime_mask`, `macepci_mask`, and `maceisa_mask`, flushing buses after posted writes. Separate irq_chips handle CRIME level, CRIME edge, MACE PCI, MACE ISA level/edge, and regular MACE interrupts. `ip32_irq0()` reads `crime->istat & crime_mask`, resolves daisy-chained MACE ISA interrupts from MACE ISTAT, and calls `do_IRQ()`. Unknown CPU IRQ lines dump extensive state and spin. `arch_init_irq()` clears CRIME/MACE state, initializes CPU IRQs, assigns handlers for every IP32 IRQ range, requests CRIME memory/CPU error IRQs, and enables CPU interrupt mask bits.

State, persistence, and integration: state includes CRIME/MACE masks, hardware interrupt registers, and Linux IRQ descriptors. Dependencies include `crime_init()` having mapped CRIME/MACE, error handlers from `crime.c`, and IP32 IRQ number definitions. Risks include 32-bit shifts against wider masks, fatal spin on unknown IRQs, comments about CRIME 1.1 interrupt delivery quirks, and careful edge clear ordering. Test signals are working serial, RTC, Ethernet, PCI, audio, and CRIME error IRQs plus stable interrupt masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-memory.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-memory.c

Purpose: IP32 memory discovery from CRIME memory-bank registers.

Important APIs and control flow: `prom_meminit()` calls `crime_init()`, iterates CRIME banks, derives base from `CRIME_MEM_BANK_CONTROL_ADDR`, skips zero-base nonzero banks, derives size as 32 or 128 MiB, adjusts banks crossing the 256 MiB split by adding `CRIME_HI_MEM_BASE`, logs each bank, and adds it to memblock.

State, persistence, and integration: state includes CRIME/MACE mappings and memblock RAM ranges. Dependencies include CRIME registers and O2 memory layout. Risks include bank zero special handling, fixed size encoding, and high-memory base adjustment assumptions. Test signals are CRIME MC bank logs, correct total RAM, and no overlapping memblock ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-platform.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-platform.c

Purpose: registers SGI O2 platform devices for serial, Ethernet, audio, buttons, and RTC.

Important APIs and control flow: static 8250 platform data describes two MACE ISA serial ports. Device initcalls register `serial8250`, allocate/add `meth`, allocate/add `sgio2audio`, register `sgibtns`, and register a `rtc-ds1685` device with IRQ/MMIO resources, padded register step, BCD mode, and `ip32_prepare_poweroff()` callback.

State, persistence, and integration: state is platform-device registration and RTC platform data. Dependencies include MACE base/IRQ constants, platform drivers, and reset code's exported `ip32_prepare_poweroff()`. Risks include no device resources for `meth` and audio, simple-device helper returning `IS_ERR()` as int, and RTC poweroff module dependency. Test signals are ttyS registration, MACE Ethernet, O2 audio, buttons, RTC, and poweroff callback operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-reset.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-reset.c

Purpose: SGI O2 restart, halt/poweroff, power-button shutdown preparation, and panic LED handling.

Important APIs and control flow: `ip32_poweroff()` dynamically obtains `ds1685_rtc_poweroff`, optionally requests the RTC module, invokes it with `ip32_rtc_device`, and never returns. `ip32_machine_restart()` writes `CRIME_CONTROL_HARD_RESET`. `ip32_prepare_poweroff()` handles power button shutdown, signals init, starts red LED blinking, and arms a forced poweroff timer. `panic_event()` turns off green LED and starts faster red blink. `ip32_reboot_setup()` initializes LEDs, installs restart/halt/poweroff hooks, sets up the blink timer, and registers panic notifier.

State, persistence, and integration: state includes timers, LED state via MACE misc register, panic/shutdown flags, machine hooks, panic notifier, and RTC poweroff callback linkage. Dependencies include CRIME/MACE mappings, RTC platform device, module symbol lookup, and `kill_cad_pid()`. Risks include dependency on RTC driver/module for actual poweroff, timer races, and dynamic symbol failure causing infinite spin. Test signals are hard reset, front-button shutdown, panic LED blinking, RTC poweroff, and forced timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-setup.c -->
# sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-setup.c

Purpose: IP32 basic setup and timer calibration. It installs bus-error handling, optionally captures the Ethernet MAC from ARCS, chooses serial console, and calibrates CP0 count against the CRIME timer.

Important APIs and control flow: optional `str2eaddr()` parses the ARCS `eaddr` string into `o2meth_eaddr`. `plat_time_init()` zeroes CP0 count and CRIME timer, waits 10 ms worth of CRIME master cycles, computes `mips_hpt_frequency`, and logs CPU MHz. `plat_mem_setup()` sets `board_be_init`, reads MAC/console ARCS variables under config guards, and adds a ttyS preferred console with optional `dbaud`.

State, persistence, and integration: state includes `board_be_init`, `mips_hpt_frequency`, optional Ethernet MAC buffer, and console preference. Dependencies include CRIME timer registers, ARCS variables, and CRIME/MACE memory setup having occurred before timer access. Risks include busy-wait calibration, no validation for missing `eaddr` before parsing, and firmware string assumptions. Test signals are CPU MHz log, correct MAC, preferred serial console, and bus-error handler installation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/Kconfig -->
# sources/distributed-fs/ceph-client/arch/mips/sibyte/Kconfig

Purpose: configuration matrix for Broadcom SiByte SB1250/BCM112x/BCM1x80 SoCs and related diagnostics.

Important APIs and control flow: SoC configs select clockevent/clocksource drivers, PCI, CPU IRQs, CFE firmware, SMP support, and common SiByte SoC support. A stepping choice selects SB1 pass/feature options such as prefetch. Additional options enable fatal cache-error policy, CFE console, bus-watcher statistics/trace, and ZBbus profiling.

State, persistence, and integration: no runtime state, but options select object directories and architecture capabilities. Dependencies include matching CPU/SoC stepping to actual hardware and avoiding incompatible tracing/profiling combinations. Risks include wrong pass option causing CPU feature/errata mismatch, bus trace interfering with profiling/JTAG as documented, and CFE console excluding other console strategies. Test signals are Kconfig dependencies, selected objects, and runtime SoC pass logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/sibyte/Makefile

Purpose: top-level SiByte platform build routing. It includes common, SB1250, BCM1480, and board-specific SWARM-family directories based on config.

Important APIs and control flow: BCM112x and SB1250 select `sb1250/` plus `common/`; BCM1x80 selects `bcm1480/` plus `common/`. Several board configs select the `swarm/` directory.

State, persistence, and integration: no runtime state; it controls which SoC and board hooks are linked. Dependencies include SoC Kconfig selections and board Kconfig symbols. Risks include missing common firmware code if SoC selections are inconsistent and duplicate directory inclusion controlled by mutually exclusive configs. Test signals are build object lists and successful link for each SiByte board.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/bcm1480/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/sibyte/bcm1480/Makefile

Purpose: build rules for BCM1480/BCM1x80 SoC support.

Important APIs and control flow: always builds `setup.o`, `irq.o`, and `time.o`; adds `smp.o` when `CONFIG_SMP` is enabled.

State, persistence, and integration: no runtime state; this selects SoC identification, interrupt routing, timer setup, and optional SMP operations. Dependencies include BCM1x80 Kconfig and common CFE support. Risks are no SMP secondary support if `smp.o` is omitted for SMP hardware. Test signals are expected object inclusion and symbols such as `bcm1480_smp_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/bcm1480/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/bcm1480/irq.c -->
# sources/distributed-fs/ceph-client/arch/mips/sibyte/bcm1480/irq.c

Purpose: BCM1480 interrupt mapper support. It initializes interrupt maps/masks, owns IRQ affinity, acknowledges LDT/HT interrupts, and dispatches CP0 interrupt pins.

Important APIs and control flow: `bcm1480_mask_irq()` and `bcm1480_unmask_irq()` update high/low IMR mask registers under a raw spinlock. SMP affinity retargets interrupt masks from the old physical CPU to the new one. `ack_bcm1480_irq()` clears LDT pending bits on all CPUs when needed, optionally writes HT EOI space, then masks the interrupt. `init_bcm1480_irqs()` installs one `irq_chip` for all BCM1480 IRQs. `arch_init_irq()` maps all interrupts to IP2, mailbox interrupts to IP3, clears mailboxes, masks everything except mailbox bits, and enables CP0 IP lines. `plat_irq_dispatch()` routes timer IP4, mailbox IP3, or IP2 through status registers.

State, persistence, and integration: state includes `bcm1480_irq_owner[]`, IMR mapping/mask/mailbox registers, and Linux IRQ descriptors. Dependencies include physical CPU maps, optional HT EOI space, SMP mailbox handler, and BCM1480 register definitions. Risks include global raw spinlock contention, possible off-by-one checks using `<= BCM1480_NR_IRQS`, dispatching only one pending interrupt, and HT assumptions. Test signals are timer IRQs, mailbox IPIs, PCI/LDT IRQ acknowledgement, affinity changes, and no stale mailbox interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/bcm1480/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/bcm1480/setup.c -->
# sources/distributed-fs/ceph-client/arch/mips/sibyte/bcm1480/setup.c

Purpose: BCM1480/BCM1x55 SoC identification and clock reporting. It decodes system revision registers and exports SoC revision metadata.

Important APIs and control flow: globals `sb1_pass`, `soc_pass`, `soc_type`, `periph_rev`, and `zbbus_mhz` capture CPU/SoC state. `setup_bcm1x80_bcm1x55()` maps revision values to pass strings and peripheral revision. `sys_rev_decode()` chooses SoC family/name from system revision and part type. `bcm1480_setup()` reads CP0 PRID, system revision, and PLL divisor, restarts on unknown chip, computes ZBbus frequency, and logs SoC/pass/board type.

State, persistence, and integration: exported SoC state informs drivers and diagnostics. Dependencies include SCD registers, CP0 PRID, reboot hook availability, and `get_system_type()`. Risks include forced restart on unknown parts, defaulting unknown revisions to periph rev 1, and fixed PLL formula. Test signals are "Broadcom SiByte ..." boot log, exported `soc_type`/`periph_rev`, and correct ZBbus MHz.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/bcm1480/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/bcm1480/smp.c -->
# sources/distributed-fs/ceph-client/arch/mips/sibyte/bcm1480/smp.c

Purpose: BCM1480 SMP support. It uses IMR mailboxes for IPIs and CFE calls to enumerate, stop, and start secondary CPUs.

Important APIs and control flow: mailbox register arrays address each CPU's mailbox set/clear/status registers. `bcm1480_smp_init()` sets CP0 interrupt mask bits. IPI helpers write the action in the high mailbox bits. `bcm1480_boot_secondary()` calls `cfe_cpu_start()` with `smp_bootstrap`, stack, and thread-info. `bcm1480_smp_setup()` initializes CPU maps and probes secondaries by calling `cfe_cpu_stop()`. `bcm1480_mailbox_interrupt()` reads/clears the mailbox, increments IRQ stats, and dispatches scheduler or call-function IPIs.

State, persistence, and integration: state includes CPU maps, mailbox registers, CFE CPU state, and `bcm1480_smp_ops`. Dependencies include CFE firmware, physical/logical CPU maps, clockevent init, and IRQ mapping of mailbox IP3. Risks include firmware start/stop failure, action bit packing limits, mailbox clearing correctness, and probing by stopping CPUs. Test signals are detected secondary count, successful CPU online, mailbox interrupt counts, scheduler IPIs, and call-function IPIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/bcm1480/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/bcm1480/time.c -->
# sources/distributed-fs/ceph-client/arch/mips/sibyte/bcm1480/time.c

Purpose: BCM1480 platform time initialization glue.

Important APIs and control flow: `plat_time_init()` calls external `sb1480_clocksource_init()` and `sb1480_clockevent_init()` in order.

State, persistence, and integration: state is created by the common BCM1480 clocksource/clockevent implementation outside this file. Dependencies include the selected `CEVT_BCM1480` and `CSRC_BCM1480` providers. Risks are limited to missing external clock functions or wrong init ordering. Test signals are registered BCM1480 clocksource/clockevent devices and functioning timer interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/bcm1480/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/common/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/sibyte/common/Makefile

Purpose: common SiByte support build rules.

Important APIs and control flow: always builds CFE firmware support. It conditionally adds SWIOTLB DMA setup, bus watcher, CFE console, and ZBbus profiling objects based on config symbols.

State, persistence, and integration: no runtime state; it controls inclusion of common boot, DMA, diagnostics, and console support. Dependencies include Kconfig selections such as `CONFIG_SWIOTLB`, `CONFIG_SIBYTE_BUS_WATCHER`, and `CONFIG_SIBYTE_CFE_CONSOLE`. Risks include omitting diagnostics or DMA bounce setup when required by board memory/device constraints. Test signals are object inclusion and boot logs for CFE and optional diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/common/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/common/bus_watcher.c -->
# sources/distributed-fs/ceph-client/arch/mips/sibyte/common/bus_watcher.c

Purpose: SiByte bus-watcher interrupt handling and statistics. It aggregates bus, ECC, and memory/IO error counters and optionally exposes them through `/proc/bus_watcher`.

Important APIs and control flow: `check_bus_watcher()` reads non-destructive status registers or falls back to last reaped values, then prints a summary. `sibyte_bw_int()` optionally freezes/dumps trace buffer data, destructively reads bus-error status, accumulates L2 and memory/IO error counters, clears hardware counters, and returns handled. `bw_proc_show()` formats cumulative stats and last signature. `sibyte_bus_watcher()` initializes stats, requests BAD_ECC/COR_ECC/IO_BUS IRQs with cleanup on failure, creates proc output, and optionally starts trace capture.

State, persistence, and integration: state is global `bw_stats`, requested IRQs, optional proc entry, and hardware trace/counter registers. Dependencies include SoC-specific bus error status addresses, IRQ numbers, procfs, and cache error handlers calling `check_bus_watcher()`. Risks include comments noting missing locking, destructive reads, counter saturation, trace interference with profiling/JTAG, and partial IRQ registration failure paths. Test signals are registered IRQs, `/proc/bus_watcher` output, accumulated counters after injected ECC/bus errors, and trace dumps when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/common/bus_watcher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/common/cfe.c -->
# sources/distributed-fs/ceph-client/arch/mips/sibyte/common/cfe.c

Purpose: common CFE firmware integration for SiByte boards. It initializes CFE, obtains console handles and command line, discovers memory, registers SMP ops, and implements restart/halt through firmware.

Important APIs and control flow: `_machine_restart`, `_machine_halt`, and `pm_power_off` call `cfe_linux_exit()` with warm/cold semantics, routing the exit to CPU0 if needed. `prom_meminit()` enumerates CFE memory blocks, filters by addressability, carves out initrd if present, subtracts prefetch padding, and adds memblock RAM; it also reserves initrd. `initrd_setup()` parses `size@addr`. `prom_init()` decodes old/new loader argument conventions, validates CFE entry seal, calls `cfe_init()`, gets console handle, obtains `LINUX_CMDLINE`, parses initrd, runs memory init, and registers SB1250 or BCM1480 SMP ops by config. `prom_putchar()` writes through CFE console.

State, persistence, and integration: state includes `cfe_cons_handle`, machine hooks, `arcs_cmdline`, initrd bounds, memblock RAM/reservations, and SMP ops. Dependencies include CFE API, loader ABI, firmware memory map, and SoC-specific SMP ops. Risks include spinning on invalid entry seal or missing command line, subtle MAX_RAM_SIZE clipping expression, prefetch padding reducing usable RAM, and firmware exit behavior on SMP. Test signals are CFE command line import, memory map correctness, initrd reservation, firmware console output, and restart/halt returning to CFE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/common/cfe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/common/cfe_console.c -->
# sources/distributed-fs/ceph-client/arch/mips/sibyte/common/cfe_console.c

Purpose: optional Linux console driver that writes through CFE firmware.

Important APIs and control flow: `cfe_console_write()` writes chunks to `cfe_cons_handle`, inserts carriage returns after newlines, and loops until all bytes are accepted. `cfe_console_setup()` reads `BOOT_CONSOLE` and validates it against configured SB1250 DUART or VGA console options, optionally setting board LEDs. `sb1250_cfe_console_init()` registers the `cfe` console with `CON_PRINTBUFFER`.

State, persistence, and integration: state is console registration using the global CFE console handle. Dependencies include `cfe.c` having initialized CFE, CFE environment variables, optional serial/VGA configs, and `setleds()`. Risks include loops on persistent negative write returns, no explicit locking, and console selection interactions with `console=`. Test signals are `cfe` console registration, buffered kernel logs appearing through firmware, and correct setup for `BOOT_CONSOLE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/common/cfe_console.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/common/dma.c -->
# sources/distributed-fs/ceph-client/arch/mips/sibyte/common/dma.c

Purpose: SWIOTLB setup hook for Broadcom SiByte platforms.

Important APIs and control flow: `plat_swiotlb_setup()` calls `swiotlb_init(true, SWIOTLB_VERBOSE)` during architecture DMA setup.

State, persistence, and integration: state is the allocated SWIOTLB bounce buffer pool managed by generic Linux DMA code. Dependencies include `CONFIG_SWIOTLB` and platform DMA constraints requiring bounce buffering. Risks include boot memory consumption and DMA failures if SWIOTLB is not selected on constrained devices. Test signals are verbose SWIOTLB boot log and successful DMA from devices with limited addressing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/sibyte/common/dma.c -->
