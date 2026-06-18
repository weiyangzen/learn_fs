# Research Group subset-b-000747

Source-tree-aligned grouped research for subset B work item `subset-b-000747`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_ohci.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_ohci.c

Purpose: Virtualizes the AMD CS5536 OHCI PCI function by translating 32-bit PCI config-space reads and writes into CS5536 model-specific register accesses. It lets generic PCI enumeration see OHCI as a normal PCI 2.2 device while the real state lives in USB, GLCP, GLIU, DIVIL, and southbridge MSRs.

Important APIs/types/functions: `pci_ohci_write_reg(int reg, u32 value)` handles command bits, status clearing, BAR programming, and interrupt routing. `pci_ohci_read_reg(int reg)` synthesizes vendor/device ID, command/status, class/revision, BAR sizing, subsystem IDs, ROM/capability pointers, interrupt line, and a CS5536-specific interrupt-enable register.

Control flow: Writes switch on config dword offset. `PCI_COMMAND` mirrors bus-master and memory-enable bits into `USB_MSR_REG(USB_OHCI)` high bits. `PCI_BAR0_REG` either returns range sizing via `SOFT_BAR_OHCI_FLAG` or stores the BAR and configures `GLIU_P2D_BM3`. Reads reverse that mapping and clear the soft BAR sizing flag after returning the mask.

State and persistence: State is persistent hardware/MSR state, not kernel heap state. The soft BAR flag in `GLCP_SOFT_COM` is a transient handshake for PCI sizing. Interrupt enable is encoded in `PIC_YSEL_LOW`.

Dependencies and integration: Depends on `cs5536.h` and `cs5536_pci.h` register constants and `_rdmsr/_wrmsr`. Called through the VSM dispatch table in `cs5536_pci.c` for function 4.

Risks: Incorrect BAR masking or GLIU window construction can make OHCI MMIO unreachable or overlap other devices. The status write path only clears parity when the southbridge error bit is present. Interrupt routing assumes `CS5536_USB_INTR` and PIC shift constants match board wiring.

Test signals: PCI enumeration should show the CS5536 OHCI vendor/device/class, BAR sizing should report `CS5536_OHCI_RANGE`, OHCI MMIO should probe after BAR assignment, and USB interrupts should appear only when `PCI_OHCI_INT_REG` enables the PIC route.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_ohci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_pci.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_pci.c

Purpose: Provides the CS5536 virtual PCI config-space dispatcher. It maps a CS5536 multifunction PCI function number to a per-function VSM read/write implementation that emulates config accesses with MSR operations.

Important APIs/types/functions: `cs5536_pci_conf_write4(function, reg, value)` validates a 32-bit aligned config offset and invokes `pci_isa/ide/acc/ohci/ehci_write_reg`. `cs5536_pci_conf_read4(function, reg)` validates offsets, returns `0xffffffff` for out-of-range high config reads, and calls the matching read hook.

Control flow: Static arrays indexed by local function enum hold function pointers. The reserved function intentionally maps to `NULL`, so accesses become no-ops or zero reads. Invalid function numbers and unaligned registers are rejected before dispatch.

State and persistence: This file stores no hardware state itself; it funnels operations to VSM modules that update CS5536 MSRs.

Dependencies and integration: Included by the Loongson2EF PCI ops path when firmware or config cycles target the CS5536 device. Depends on `cs5536_vsm.h` declarations for each function backend.

Risks: Function index values must match the hardware-visible multifunction layout. Returning zero for valid but unimplemented reads differs from real PCI config all-ones behavior and can hide errors.

Test signals: Config dword reads for each CS5536 function should hit the proper backend; unaligned and invalid accesses should not mutate MSRs; reads beyond 0x100 should return all ones.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/cs5536/cs5536_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/env.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/env.c

Purpose: Initializes Loongson2E/2F early environment variables from PMON firmware and CPU revision defaults.

Important APIs/types/functions: Exports `cpu_clock_freq`; `prom_init_env()` reads `cpuclock`, `memsize`, and `highmemsize` with `fw_getenvl()`.

Control flow: Firmware values are accepted first. Missing `memsize` defaults to 256 MiB. Missing `cpuclock` falls back by `processor_id` revision: 533.08 MHz for 2E, 797 MHz for 2F, and 100 MHz otherwise.

State and persistence: Populates global boot-time state `cpu_clock_freq`, `memsize`, and `highmemsize`. Values persist for timer setup and memory initialization.

Dependencies and integration: Called from `prom_init()` before memory and timer setup. Consumers include `time.c` and `mem.c`.

Risks: Firmware values are trusted without range validation. Wrong CPU frequency skews the R4K timer and scheduler clock.

Test signals: Boot logs should print expected `memsize`, `highmemsize`, and `CpuClock`; timer rate should match wall-clock behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/env.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/init.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/init.c

Purpose: Implements the Loongson2EF `prom_init()` boot hook and NMI vector setup.

Important APIs/types/functions: `_loongson_addrwincfg_base` stores optional address-window config mapping. `mips_nmi_setup()` copies `except_vec_nmi` to `CAC_BASE + 0x380`. `prom_init()` initializes command line, machine type, environment, IO space, memory, UART base, and board NMI hook.

Control flow: Optional `LOONGSON_ADDRWINCFG_BASE` is ioremapped first. Firmware command line and machine type are parsed before environment and memory, then PCI IO is mapped and early serial base is initialized.

State and persistence: Establishes early global mappings and registers `board_nmi_handler_setup`. No dynamic teardown exists.

Dependencies and integration: Calls common firmware helpers plus Loongson local `prom_init_machtype`, `prom_init_env`, `prom_init_memory`, and `prom_init_uart_base`.

Risks: Early ioremap failures are not checked. UART and memory initialization depend on prior machtype and env parsing.

Test signals: Early console should work, memblock should contain firmware memory, and NMI setup should install a copied vector at the expected cacheable address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/irq.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/irq.c

Purpose: Provides common first-level interrupt setup and Bonito interrupt dispatch for Loongson2EF boards.

Important APIs/types/functions: `bonito_irqdispatch()` handles pending Bonito sources. `plat_irq_dispatch()` passes MIPS pending bits to board-specific `mach_irq_dispatch()`. `arch_init_irq()` clears MIPS interrupt state and delegates board controller setup.

Control flow: Bonito dispatch first waits while DMA-related bit 10 is set, then masks pending sources with `LOONGSON_INTEN`, selects the lowest pending bit with `__ffs`, and calls `do_IRQ(LOONGSON_IRQ_BASE + i)`.

State and persistence: Programs interrupt steer/enable registers and relies on board code to initialize cascades.

Dependencies and integration: Board-specific Fuloong and Lemote interrupt files supply `mach_irq_dispatch()` and `mach_init_irq()`.

Risks: The DMA wait loop can stall if bit 10 never clears. Only one Bonito interrupt is dispatched per entry. Board-specific cascade wiring must match pending bit routing.

Test signals: Boot should clear stale interrupts; Bonito device IRQs should map to `LOONGSON_IRQ_BASE`; spurious IRQ logs should remain rare under device load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/machtype.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/machtype.c

Purpose: Determines and exposes the Loongson2EF machine type string used by board selection, serial setup, reset, suspend, and platform drivers.

Important APIs/types/functions: `get_system_type()` returns `system_types[mips_machtype]`. Weak `mach_prom_init_machtype()` lets board code infer machine type. `prom_init_machtype()` parses `machtype=` from `arcs_cmdline`.

Control flow: Starts from `LOONGSON_MACHTYPE`, optionally lets board code refine it, then if `machtype=` is present compares the argument as a substring against supported system type names.

State and persistence: Writes global `mips_machtype` once during early boot.

Dependencies and integration: `serial.c`, `uart_base.c`, `lemote-2f/reset.c`, and suspend logic switch on `mips_machtype`.

Risks: Substring matching can accept ambiguous fragments. `get_system_type()` assumes the machine type index is in range.

Test signals: Passing `machtype=` should select the expected board; boot logs and `/proc/cpuinfo` system type should match hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/machtype.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/mem.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/mem.c

Purpose: Adds Loongson2EF physical memory ranges to memblock and configures optional CPU address windows.

Important APIs/types/functions: Exports globals `memsize` and `highmemsize`; `prom_init_memory()` adds low memory and optional high memory.

Control flow: Low memory starts at physical zero and spans `memsize << 20`. With address-window support, it computes a power-of-two size for total memory and maps CPU window 3 from 2G to DDR. On 64-bit builds high memory is added at `LOONGSON_HIGHMEM_START`.

State and persistence: Memblock regions define early boot memory layout and survive into the normal memory allocator.

Dependencies and integration: Consumes values initialized in `env.c`; called from `prom_init()`.

Risks: The address-window size calculation depends on `memsize + highmemsize`; non-power-of-two or zero values can misprogram windows. Highmem is ignored on non-64-bit builds.

Test signals: Memblock debug output should show low and high ranges; memory size reported by the kernel should match PMON arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/pci.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/pci.c

Purpose: Sets up Loongson2EF PCI memory/IO resources, CPU-to-PCI mappings, and PCI-DMA hit windows.

Important APIs/types/functions: `setup_pcimap()` writes Loongson PCI map, base, hit selector, arbitration, and optional address-window registers. `loongson2ef_pcibios_init()` registers the `pci_controller`.

Control flow: Initializes CPU windows for PCI memory, maps PCI DMA from 2G to low memory, disables unused hit windows, applies deadlock/arbitration workarounds, sets `PCIBIOS_MIN_IO`, assigns `io_map_base`, and registers the controller.

State and persistence: Programs chipset registers and static `struct resource`/`pci_controller` state for the generic MIPS PCI layer.

Dependencies and integration: Uses `loongson_pci_ops` from platform PCI code and is called by `plat_mem_setup()`.

Risks: Hard-coded PCI window layout can conflict with unexpected firmware/device ranges. Legacy ISA IO starts at zero but allocation is protected only by `PCIBIOS_MIN_IO`.

Test signals: PCI bus enumeration should succeed, legacy IDE should retain ISA ports, and DMA-capable PCI devices should access low memory through the programmed hit window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/platform.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/platform.c

Purpose: Registers the Loongson2 CPUFreq platform device on CPUs that support it.

Important APIs/types/functions: `loongson2_cpufreq_device` has name `loongson2_cpufreq`; `loongson2_cpufreq_init()` is an `arch_initcall`.

Control flow: Reads `current_cpu_data.processor_id`; Loongson2F and later revisions register the platform device, older 2E returns `-ENODEV`.

State and persistence: Adds one platform device for the cpufreq driver to bind.

Dependencies and integration: Pairs with cpufreq support and the Lemote 2F clock control implementation.

Risks: CPU revision comparison assumes future revisions remain compatible with the 2F frequency-control interface.

Test signals: 2F systems should expose a `loongson2_cpufreq` device and cpufreq table; 2E systems should not.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/pm.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/pm.c

Purpose: Implements generic Loongson2EF suspend support and interrupt masking around wait-mode sleep.

Important APIs/types/functions: `arch_suspend_disable_irqs()`, `arch_suspend_enable_irqs()`, weak `setup_wakeup_events()`, weak `wakeup_loongson()`, weak `mach_suspend()`/`mach_resume()`, and `loongson_pm_ops`.

Control flow: Suspend masks local, i8259, and Bonito interrupts, lets board code enable wake sources, stops Loongson perf counters, clears CPU frequency bits to enter wait mode, polls board wakeup logic, restores chip config, and runs board resume hooks.

State and persistence: Caches PIC and Bonito masks and the chip configuration register across suspend. Registers platform suspend operations at arch init.

Dependencies and integration: Board-specific Lemote PM overrides wakeup and MFGPT handling. Uses `LOONGSON_CHIPCFG`, i8259 IO ports, and Linux suspend core.

Risks: Polling wake events can loop forever if board wake detection is broken. Interrupt mask restore ordering may lose wake events if hardware status is not latched.

Test signals: `PM_SUSPEND_MEM` and standby should enter/leave wait mode, wake only on configured events, and restore timer/peripheral interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/reset.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/reset.c

Purpose: Hooks Linux reboot, halt, and poweroff operations for Loongson2EF.

Important APIs/types/functions: `loongson_reboot()` jumps to `LOONGSON_BOOT_BASE`; `loongson_restart()`, `loongson_poweroff()`, `loongson_halt()`, and `mips_reboot_setup()`.

Control flow: Restart runs board `mach_prepare_reboot()` then jumps to boot ROM, optionally using inline assembly for CPU jump workarounds. Poweroff delegates to `mach_prepare_shutdown()` and returns to generic hang delay. Halt prints a notice and loops on `cpu_wait`.

State and persistence: Assigns global reboot hooks `_machine_restart`, `_machine_halt`, and `pm_power_off`.

Dependencies and integration: Board-specific reset files supply `mach_prepare_reboot()` and `mach_prepare_shutdown()`.

Risks: Ioremapping only 4 bytes at the boot base and executing it assumes firmware reset vector semantics. If board shutdown fails, power remains on and generic hang loop follows.

Test signals: `reboot`, `halt`, and `poweroff` should route through board-specific GPIO/EC preparation and either restart firmware or enter the expected halt state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/rtc.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/rtc.c

Purpose: Registers a CMOS RTC platform device for Loongson2EF platforms.

Important APIs/types/functions: `loongson_rtc_resources` describes CMOS IO ports and `RTC_IRQ`; `loongson_rtc_platform_init()` registers `rtc_cmos`.

Control flow: A `device_initcall` unconditionally registers the platform device with IO and IRQ resources.

State and persistence: Creates a platform device consumed by the generic `rtc_cmos` driver.

Dependencies and integration: Depends on `mc146818rtc` constants and platform device core.

Risks: Assumes PC-compatible CMOS ports and IRQ are present on every supported board.

Test signals: `/dev/rtc` or `rtc_cmos` should bind, and reads should match MC146818 CMOS time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/rtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/serial.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/serial.c

Purpose: Registers board-specific 8250 serial port data after machtype and UART base detection.

Important APIs/types/functions: `PORT` and `PORT_M` macros build `plat_serial8250_port` entries. `serial_init()` fills IO or memory base and registers `serial8250`; `serial_exit()` unregisters it.

Control flow: Selects one table entry by `mips_machtype`. Memory-mapped UARTs use `loongson_uart_base` and `_loongson_uart_base`; port-mapped UARTs compute `iobase` relative to `LOONGSON_PCIIO_BASE`. The following table entry is zeroed as the 8250 terminator.

State and persistence: Registers a platform serial device and mutates the selected table entry with the detected base.

Dependencies and integration: Depends on `uart_base.c` for early base selection and on the 8250 platform driver.

Risks: Out-of-range `mips_machtype` would index the table incorrectly. Clock rates and IRQs are hard-coded per board.

Test signals: Console and ttyS device should appear with the expected IO type, IRQ, and UART clock for each machine type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/setup.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/setup.c

Purpose: Supplies Loongson2EF memory setup and write-buffer flush hook.

Important APIs/types/functions: `wbflush_loongson()` issues a MIPS3 `sync`; exported `__wbflush` points to it. `plat_mem_setup()` calls `loongson2ef_pcibios_init()`.

Control flow: At platform memory setup, PCI resources and mappings are initialized. The write-buffer flush pointer is initialized statically.

State and persistence: Exports a global function pointer used by MIPS write-buffer flush paths.

Dependencies and integration: Integrates Loongson PCI setup with the generic MIPS platform setup sequence.

Risks: The inline assembly mode changes must be accepted by all configured assemblers/CPUs.

Test signals: PCI initialization should happen during `plat_mem_setup`; drivers using `wbflush()` should execute a sync without fault.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/time.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/time.c

Purpose: Initializes Loongson2EF timers and reads persistent CMOS time.

Important APIs/types/functions: `plat_time_init()` sets `mips_hpt_frequency` and calls `setup_mfgpt0_timer()`. `read_persistent_clock64()` returns MC146818 CMOS seconds.

Control flow: The R4K counter is assumed to run at half `cpu_clock_freq`; CS5536 MFGPT0 is set up as an additional timer source.

State and persistence: Sets global timer frequency used by the MIPS time subsystem.

Dependencies and integration: Consumes `cpu_clock_freq` from env initialization and CS5536 MFGPT support.

Risks: Wrong CPU clock halves cause timer drift. CMOS reads provide only second precision.

Test signals: Kernel jiffies and clocksource output should match real time; persistent clock should report CMOS time at boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/uart_base.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/uart_base.c

Purpose: Chooses raw and uncached UART base addresses for early printk and later serial platform registration.

Important APIs/types/functions: Exports `loongson_uart_base` and `_loongson_uart_base`; `prom_init_loongson_uart_base()` switches on `mips_machtype`.

Control flow: Fuloong 2E uses PCI IO 0x3f8, Fuloong/Lynloong 2F use PCI IO 0x2f8, and netbook/NAS-style machines use CPU LPC at `LOONGSON_LIO1_BASE + 0x3f8`. The uncached address is passed to `setup_8250_early_printk_port()`.

State and persistence: Stores early serial bases in globals used by `serial.c`.

Dependencies and integration: Called from `prom_init()` after machine type initialization.

Risks: Wrong machtype gives a silent console or corrupts unrelated IO. Early printk assumes a 1024 baud divisor parameter is appropriate.

Test signals: Early boot output should appear before platform serial registration and should continue on the same UART after 8250 binds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/uart_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/fuloong-2e/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/fuloong-2e/Makefile

Purpose: Builds the Fuloong 2E board support objects.

Important APIs/types/functions: Adds `irq.o`, `reset.o`, and `dma.o` to `obj-y`.

Control flow: Kernel build always includes these board files when the Fuloong 2E directory is selected.

State and persistence: No runtime state; controls object inclusion.

Dependencies and integration: Provides board hooks consumed by Loongson2EF common code.

Risks: Missing any object leaves weak/default hooks or DMA translation unsuitable for the board.

Test signals: A Fuloong 2E build should include board IRQ, reset, and DMA symbols with no unresolved references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/fuloong-2e/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/fuloong-2e/dma.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/fuloong-2e/dma.c

Purpose: Implements simple Fuloong 2E physical/DMA address translation.

Important APIs/types/functions: `phys_to_dma()` ORs bit 31; `dma_to_phys()` clears bit 31.

Control flow: Translation is stateless and symmetric for the low 2 GiB window.

State and persistence: No stored state.

Dependencies and integration: Overrides architecture DMA direct translation hooks for devices on this board.

Risks: Addresses above the assumed window are truncated on reverse translation.

Test signals: PCI DMA mappings should produce bus addresses with the 0x80000000 bit set and should map back to the original low physical address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/fuloong-2e/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/fuloong-2e/irq.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/fuloong-2e/irq.c

Purpose: Supplies Fuloong 2E-specific MIPS pending-bit dispatch and interrupt-controller cascade setup.

Important APIs/types/functions: `mach_irq_dispatch()` routes timer IP7, ignores perf IP6, dispatches i8259 on IP5, and Bonito on IP2. `mach_init_irq()` initializes CPU, i8259, and Bonito IRQs and registers cascade handlers.

Control flow: Pending bits are tested in priority order. Board init sets Bonito edge behavior for error/mailbox sources, initializes controllers, and requests no-thread cascade IRQs for IP2 and IP5.

State and persistence: Programs `LOONGSON_INTEDGE` and installs cascade IRQ descriptors.

Dependencies and integration: Common `plat_irq_dispatch()` calls this board hook.

Risks: IP6 perf counter overflow is silently returned. Incorrect edge/level setup can lose device interrupts.

Test signals: Timer, i8259, and Bonito interrupts should route through distinct pending bits; cascade request failures should be visible in boot logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/fuloong-2e/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/fuloong-2e/reset.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/fuloong-2e/reset.c

Purpose: Provides Fuloong 2E board preparation hooks for reboot and shutdown.

Important APIs/types/functions: `mach_prepare_reboot()` toggles bit 2 in `LOONGSON_GENCFG`; `mach_prepare_shutdown()` is empty.

Control flow: Reboot clears and sets the reset-related GENCFG bit before common code jumps to boot firmware.

State and persistence: Mutates chipset GENCFG only during restart.

Dependencies and integration: Called by common `loongson_restart()` and `loongson_poweroff()`.

Risks: Shutdown has no power-control action, so poweroff relies on generic halt behavior.

Test signals: Reboot should reset board logic and return to firmware; poweroff should not claim to cut power.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/fuloong-2e/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/Makefile

Purpose: Builds Lemote Loongson2F family board support.

Important APIs/types/functions: Always includes `clock.o`, `machtype.o`, `irq.o`, `reset.o`, `dma.o`, and `ec_kb3310b.o`; conditionally includes `pm.o` for `CONFIG_SUSPEND`.

Control flow: Build-time object selection wires the common Loongson2EF hooks to Lemote 2F implementations.

State and persistence: No runtime state; controls compilation.

Dependencies and integration: Supplies machine-type, EC, reset, DMA, IRQ, and optional suspend support.

Risks: Suspend hooks are absent unless `CONFIG_SUSPEND` is enabled.

Test signals: Lemote 2F builds should resolve EC and board hook symbols; suspend builds should include `pm.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/clock.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/clock.c

Purpose: Exposes Loongson2F CPU clock modulation states and implements frequency-rate programming.

Important APIs/types/functions: Exports `loongson2_clockmod_table` and `loongson2_cpu_set_rate(rate_khz)`.

Control flow: The setter searches valid cpufreq table entries for the requested frequency, then writes `(driver_data - 1)` into low 3 bits of `LOONGSON_CHIPCFG`.

State and persistence: CPU duty-cycle state is stored in `LOONGSON_CHIPCFG`.

Dependencies and integration: Used by Loongson2 cpufreq platform driver registered by common platform code.

Risks: Table entries with zero frequency must be filled by the cpufreq driver before use. Unsupported rates return `-ENOTSUPP`.

Test signals: Requested cpufreq levels should change low chipcfg bits and reject rates not present in the table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/dma.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/dma.c

Purpose: Implements Lemote 2F DMA address translation with a special high-address pass-through case.

Important APIs/types/functions: `phys_to_dma()` ORs 0x80000000. `dma_to_phys()` returns DMA addresses above 0x8fffffff unchanged, otherwise masks to low 28 bits.

Control flow: Translation is stateless; reverse mapping preserves some high bus addresses and strips the board DMA window for lower ones.

State and persistence: No stored state.

Dependencies and integration: Used by direct DMA mapping for Lemote 2F devices.

Risks: The threshold and 28-bit mask encode board-specific windows; devices outside these assumptions can map incorrectly.

Test signals: Network/storage DMA should work across low-memory buffers and any board-specific high DMA range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/ec_kb3310b.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/ec_kb3310b.c

Purpose: Provides low-level KB3310B embedded-controller access for YeeLoong/related Lemote 2F machines.

Important APIs/types/functions: `ec_read()`, `ec_write()`, `ec_query_seq()`, `ec_query_event_num()`, and `ec_get_event_num()` are exported. Two spinlocks serialize indexed register access and command/status port access.

Control flow: Indexed reads/writes output high and low address bytes then read/write data port. Command queries write to `EC_CMD_PORT`, poll status bit 1 until the EC accepts the command, then event retrieval waits for status bit 0 and reads `EC_DAT_PORT`.

State and persistence: EC state is external hardware state. Kernel state is limited to spinlocks.

Dependencies and integration: Used by Lemote PM/reset/laptop code and constants from `ec_kb3310b.h`.

Risks: Polling timeouts return `-EINVAL`; excessive printk on command success can be noisy. Port access assumes x86-style IO ports exist and are reserved.

Test signals: EC register reads should return battery/lid/fan values; SCI event queries should time out cleanly when EC is unresponsive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/ec_kb3310b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/ec_kb3310b.h -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/ec_kb3310b.h

Purpose: Defines the KB3310B EC public interface, IO ports, commands, register map, bit flags, and SCI event numbers.

Important APIs/types/functions: Declares EC access functions and `sci_handler`; exports `yeeloong_report_lid_status` hook. Constants cover fan, battery, audio, USB, lid, CRT, display, reset, LED, camera, WLAN, and SCI events.

Control flow: Header-only definitions are consumed by EC users to form command sequences and interpret event/register values.

State and persistence: No state; constants describe persistent EC firmware registers.

Dependencies and integration: Included by EC implementation, suspend wake logic, and reset logic.

Risks: Register addresses and bit meanings are firmware-specific. A wrong constant can power off devices, misreport battery status, or reset the machine.

Test signals: Drivers using the header should decode EC events like `EVENT_LID` and registers like `REG_LID_DETECT` consistently with real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/ec_kb3310b.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/irq.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/irq.c

Purpose: Implements Lemote 2F interrupt dispatch and controller setup, including a custom i8259 query path.

Important APIs/types/functions: `mach_i8259_irq()` reads PIC ISR/IMR under `i8259A_lock`; `mach_irq_dispatch()` routes timer, northbridge/Bonito, CPU UART, and southbridge/i8259; `mach_init_irq()` initializes cascades.

Control flow: The i8259 path first checks Loongson INT0 pending, then reads master/slave ISR masked by IMR and handles IRQ7 spurious detection. Board dispatch sends IP6 to Bonito, IP3 to CPU UART, and IP2 to i8259.

State and persistence: Programs `LOONGSON_INTPOL` and `LOONGSON_INTEDGE`; registers IP6 and IP2 cascade handlers.

Dependencies and integration: `wakeup_loongson()` in PM calls `mach_i8259_irq()` during suspend polling.

Risks: Uses ISR rather than generic `i8259_irq()` to avoid boot hangs, so PIC behavior must be carefully matched. Shared IP6 action is a dummy handler.

Test signals: Keyboard, SCI, Bonito, CPU UART, and timer interrupts should dispatch on expected pending bits; spurious IRQ7 should be filtered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/machtype.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/machtype.c

Purpose: Infers Lemote 2F family machine type from PMON version when `machtype=` is absent.

Important APIs/types/functions: `mach_prom_init_machtype()` inspects `arcs_cmdline` for `PMON_VER=LM...`.

Control flow: LM8 maps to Yeeloong 8.9, LM6 to Fuloong 2F, LM9 to Lynloong, and other LM versions to NAS. It appends a `machtype=` argument with `get_system_type()`.

State and persistence: Mutates `mips_machtype` and appends to `arcs_cmdline`.

Dependencies and integration: Weak hook called by common machtype initialization.

Risks: `strcat()` assumes enough command-line buffer space. Version-prefix inference can misidentify future PMON strings.

Test signals: Old PMON boots without explicit `machtype=` should select the correct board and show the appended machtype in the command line.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/machtype.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/pm.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/pm.c

Purpose: Adds Lemote 2F suspend wakeup behavior for keyboard and Yeeloong EC lid SCI events.

Important APIs/types/functions: `setup_wakeup_events()`, `wakeup_loongson()`, weak `mach_suspend()`/`mach_resume()` overriding common defaults, `i8042_enable_kbd_port()`, delayed lid work, and exported `yeeloong_report_lid_status`.

Control flow: Netbook machtypes unmask keyboard and SCI IRQs, enable the i8042 keyboard port, and during wake polling query the actual i8259 IRQ. Keyboard IRQ wakes immediately; SCI IRQ queries EC event number and only wakes on lid-open status, scheduling delayed lid reporting after resume.

State and persistence: Caches i8042 control byte, lazily initializes delayed work, and toggles MFGPT0 counter across suspend/resume.

Dependencies and integration: Uses `mach_i8259_irq()`, EC accessors, i8042 core, PIC registers, and common PM weak hooks.

Risks: Scheduling work from suspend path is delayed deliberately but depends on `initialized` race avoidance. EC or i8042 command timeouts can prevent wake. Only selected machtypes configure wake sources.

Test signals: On Yeeloong/Mengloong, keyboard and lid-open should wake from suspend; MFGPT0 should be disabled during suspend and reenabled on resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/reset.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/reset.c

Purpose: Implements board-specific reboot and shutdown sequences for Lemote 2F desktops, netbooks, NAS, and Lynloong machines.

Important APIs/types/functions: `reset_cpu()`, `fl2f_reboot()`, `fl2f_shutdown()`, `ml2f_reboot()`, `ml2f_shutdown()`, `yl2f89_shutdown()`, `mach_prepare_reboot()`, and `mach_prepare_shutdown()`.

Control flow: Reboot first restores full CPU speed. Fuloong/NAS/Lynloong reset via CS5536 soft reset MSR; laptops reset via EC `REG_RESET`. Shutdown varies by machine: CS5536 GPIO13 low for desktops, special EC shutdown ports for Mengloong, CPU GPIO0 low for Yeeloong.

State and persistence: Mutates chipcfg, CS5536 GPIO/MSR state, EC reset/shutdown registers, or CPU GPIO state.

Dependencies and integration: Called by common Loongson restart/poweroff hooks and uses EC constants.

Risks: Hardware-specific sequences can fail silently; comments note rtl8169 reset problems with PM enabled. GPIO bit operations assume firmware did not reassign pins.

Test signals: Each machtype should reboot or power off using its designated path; CPU frequency should be full speed before reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson32/Kconfig -->
# sources/distributed-fs/ceph-client/arch/mips/loongson32/Kconfig

Purpose: Defines the Loongson32 built-in DTB source-name configuration.

Important APIs/types/functions: `BUILTIN_DTB_NAME` is a string option depending on `BUILTIN_DTB`.

Control flow: Kconfig prompts for a DTS basename relative to `arch/mips/boot/dts/loongson` when built-in DTB support is enabled.

State and persistence: Build configuration only.

Dependencies and integration: Used by MIPS DTB build rules.

Risks: Incorrect basename prevents the desired DTB from being linked.

Test signals: Enabling built-in DTB should build the selected Loongson DTS into the kernel image.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson32/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson32/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/loongson32/Makefile

Purpose: Placeholder Makefile for Loongson32 platform directory.

Important APIs/types/functions: Contains only SPDX metadata and no object rules.

Control flow: No objects are built directly from this directory by this file.

State and persistence: Build metadata only.

Dependencies and integration: Platform support may be elsewhere or driven by generic rules.

Risks: Adding Loongson32 objects without updating this file would leave them unbuilt.

Test signals: Loongson32 builds should not expect object files from this Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson32/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/Kconfig -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/Kconfig

Purpose: Defines Loongson64-specific configuration for the RS780/SBX00 HPET timer.

Important APIs/types/functions: `RS780_HPET` is a bool under `MACH_LOONGSON64`, depends on `BROKEN`, and selects `MIPS_EXTERNAL_TIMER`.

Control flow: The option is hidden from normal use because of `BROKEN`; help warns that the driver performs dangerous hacks and should be enabled only on RS780E systems.

State and persistence: Build configuration only.

Dependencies and integration: Enables `hpet.o` through the Loongson64 Makefile.

Risks: The option manipulates chipset registers before PCI init; enabling it on wrong hardware is unsafe.

Test signals: With the option enabled manually, `setup_hpet_timer()` and HPET clocksource registration should compile and run on RS780E.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/Makefile

Purpose: Selects Loongson-3/Loongson64 platform objects.

Important APIs/types/functions: Core `MACH_LOONGSON64` objects include CP2 exception handling, DMA, setup, init, env, time, and reset. Optional objects include SMP, NUMA, HPET, suspend sleeper, PCI quirks, CPUCFG emulation, and sysfs boardinfo.

Control flow: Object inclusion follows kernel config symbols such as `CONFIG_SMP`, `CONFIG_NUMA`, `CONFIG_RS780_HPET`, and `CONFIG_SYSFS`.

State and persistence: Build metadata only.

Dependencies and integration: Wires platform-specific boot, firmware, power, and exception code into the MIPS kernel build.

Risks: Missing config dependencies can leave required hooks absent, especially suspend requiring both `pm.o` and `sleeper.o`.

Test signals: Loongson64 defconfigs should link all selected platform hooks without unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/boardinfo.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/boardinfo.c

Purpose: Exposes Loongson64 board and BIOS information under firmware sysfs.

Important APIs/types/functions: `boardinfo_show()` formats data from `eboard`, `einter`, and `especial`; `boardinfo_init()` creates `/sys/firmware/lefi/boardinfo`.

Control flow: Late init creates a `lefi` kobject under `firmware_kobj` and adds a read-only `boardinfo` attribute.

State and persistence: Sysfs kobject and attribute persist until shutdown. It reads firmware table globals initialized by `env.c`.

Dependencies and integration: Requires LEFI-style boot parameter structures in `boot_param.h` and `CONFIG_SYSFS`.

Risks: Assumes firmware pointers are valid and strings contain dash-separated vendor/manufacturer parts. No cleanup path is needed for late init but partial creation failure only returns an error.

Test signals: `/sys/firmware/lefi/boardinfo` should show board manufacturer/name, BIOS vendor/version, and release date on LEFI systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/boardinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/cop2-ex.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/cop2-ex.c

Purpose: Handles Loongson-3 COP2 exceptions, enabling CU2/FPU state and emulating Loongson overridden unaligned load/store instructions.

Important APIs/types/functions: `loongson_cu2_call()` is registered by `loongson_cu2_setup()` with `cu2_notifier()`. It handles `CU2_EXCEPTION`, `CU2_LWC2_OP`, `CU2_SWC2_OP`, `CU2_LDC2_OP`, and `CU2_SDC2_OP`.

Control flow: CU2 unusable exceptions enable CU1/CU2 and restore/init FPU context if necessary. LWC2/SWC2 emulate paired 64-bit GPR/FPR loads and stores. LDC2/SDC2 decode `opcode1` for halfword/word/dword GPR and word/dword FPR unaligned accesses, validate `access_ok()`, perform `Load*`/`Store*`, and advance EPC.

State and persistence: Mutates current task FPU state, CP0 status bits, GPRs/FPRs, and EPC. On faults it restores return address/EPC before fixup or signal delivery.

Dependencies and integration: Uses MIPS COP2 notifier framework, FPU ownership helpers, unaligned emulation macros, branch EPC helpers, and signal/fixup paths.

Risks: FPU ownership transitions around faulting memory operations are delicate; errors can leave stale FPU state. Kernel unaligned FP access deliberately dies. User faults map to SIGSEGV or SIGBUS depending on access failure.

Test signals: Loongson-specific unaligned gsl/gss instructions should complete in userspace, fault addresses should signal correctly, and CU2 unusable exceptions should not fall through to the default notifier.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/cop2-ex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/cpucfg-emul.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/cpucfg-emul.c

Purpose: Synthesizes Loongson CPUCFG feature words for Loongson processors lacking hardware CPUCFG and advertises CPUCFG to userspace when usable.

Important APIs/types/functions: `loongson3_cpucfg_synthesize_data(struct cpuinfo_mips *c)`, plus helpers `is_loongson()`, `cpu_has_uca()`, `probe_uca()`, `decode_loongson_config6()`, and `patch_cpucfg_sel1/2/3()`.

Control flow: Non-Loongson CPUs return. CPUs with hardware CPUCFG skip synthesis but still set HWCAP. Known Loongson revisions build selector 1-3 feature words from PRID, Config6, UCAC probing, ASE flags, FPU revision, and CPU options, then patch dynamic features.

State and persistence: Writes `c->loongson3_cpucfg_data[]` and global `elf_hwcap`.

Dependencies and integration: Uses Loongson PRID/config register definitions and MIPS ELF hwcap exposure.

Risks: Briefly toggles diagnostic UCAC bit to probe capability. Unknown future Loongson CPUs without CPUCFG get no emulation, intentionally conservative.

Test signals: Userspace `HWCAP_LOONGSON_CPUCFG` should appear on supported cores, and emulated CPUCFG selectors should match documented revision features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/cpucfg-emul.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/dma.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/dma.c

Purpose: Implements Loongson-3 DMA/physical address conversion and initializes SWIOTLB.

Important APIs/types/functions: `phys_to_dma()`, `dma_to_phys()`, and `plat_swiotlb_setup()`.

Control flow: Conversion extracts two node-id bits from physical bit 44-45 and embeds them at firmware/bridge-selected `node_id_offset` in the DMA address; reverse conversion extracts from DMA and restores physical node bits. SWIOTLB is initialized verbose and forced.

State and persistence: Depends on global `node_id_offset` set by early bridge config.

Dependencies and integration: Used by Linux direct DMA mapping; early config comes from `init.c` and firmware bridge detection in `env.c`.

Risks: Wrong `node_id_offset` breaks DMA on multi-node systems. The XOR/or expression assumes only two node bits are used.

Test signals: DMA mappings for buffers on different nodes should encode and decode node IDs correctly; SWIOTLB should initialize during boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/env.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/env.c

Purpose: Parses Loongson64 firmware environment, selects/fixes a DTB, initializes system configuration, and records firmware table pointers.

Important APIs/types/functions: Exports `cpu_clock_freq`, `loongson_memmap`, `loongson_sysconf`, firmware table pointers, chip control address arrays, and `smp_group[]`. `prom_dtb_init_env()` handles DTB boot, `prom_lefi_init_env()` handles LEFI boot, and `lefi_fixup_fdt()` patches UART clock-frequency properties.

Control flow: DTB mode accepts `fw_arg2` as FDT when plausible or falls back to built-in 2K1000 DTB. LEFI mode walks boot parameter offsets, fills CPU/node counts, DMA coherency, reset/suspend/VBIOS addresses, bridge type, workarounds, SMP mailbox bases, chipcfg/temp/frequency-control bases, and chooses a built-in DTB by PRID and bridge. UART entries from firmware update the chosen FDT.

State and persistence: Populates global platform configuration used by memory, DMA, SMP, reset, PM, time, sysfs, and PCI quirks. The fixed-up FDT buffer is static initdata.

Dependencies and integration: Uses LEFI boot structures, libfdt, built-in DTB symbols, PCI vendor IDs, Loongson PRID constants, and bridge early-config callbacks.

Risks: Firmware offsets and strings are trusted. The 16 KiB FDT fixup buffer can be too small. Unknown bridge defaults to virtual DTB and may not describe real hardware.

Test signals: Boot logs should report DMA coherency, CPU clock, and bridge type; `/proc/device-tree` UART clocks should match firmware; SMP group and reset addresses should match board firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/env.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/hpet.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/hpet.c

Purpose: Provides a Loongson-3 RS780/SBX00 HPET clock event and clocksource setup path.

Important APIs/types/functions: MMIO helpers for SMBus and HPET registers, `setup_hpet_timer()`, `hpet_irq_handler()`, clock-event state callbacks, `hpet_next_event()`, and `init_hpet_clocksource()`.

Control flow: `hpet_setup()` writes HPET base into SMBus PCI config space, enables HPET MMIO decoding and IRQ. Timer setup initializes per-CPU timer0 clockevent, registers it, and requests `HPET_T0_IRQ`. Clocksource init registers a 32-bit continuous HPET counter.

State and persistence: Uses global `hpet_lock` and per-CPU `hpet_clockevent_device`; programs chipset and HPET registers.

Dependencies and integration: Enabled only by `CONFIG_RS780_HPET`; depends on `loongson_sysconf.ht_control_base`, MIPS clockevent/clocksource core, and HPET register constants.

Risks: Kconfig marks this broken/dangerous. It writes host bridge/SMBus registers before normal PCI setup. `hpet_next_event()` races against a near counter and returns `-ETIME` if too close.

Test signals: HPET IRQ should fire and call the clockevent handler; clocksource should register with rating 300; suspend/resume should re-run setup and restart the counter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/hpet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/init.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/init.c

Purpose: Implements Loongson64 early boot initialization, memory discovery entry points, early bridge configuration, legacy ISA PIO reservation, IRQ init, and NMI setup.

Important APIs/types/functions: `prom_init()`, `szmem(node)`, `ls7a_early_config()`, `rs780e_early_config()`, `virtual_early_config()`, `reserve_pio_range()`, `arch_init_irq()`, and `arch_dynirq_lower_bound()`.

Control flow: `prom_init()` initializes command line, selects DTB vs LEFI env parsing, sets IO base, runs bridge early config to compute `node_id_offset`, initializes NUMA or node-0 memory, sets early 8250 UART by CPU type, registers Loongson SMP ops, and installs the NMI setup hook. IRQ init reserves ISA IO ranges from device tree then calls `irqchip_init()`.

State and persistence: Writes `node_id_offset`, memblock regions/reservations, logic PIO ranges, early serial config, and SMP ops.

Dependencies and integration: Calls `prom_lefi_init_env()`/`prom_dtb_init_env()`, `prom_init_numa_memory()`, `szmem()`, `logic_pio_register_range()`, and OF range parsing.

Risks: LEFI memory parsing is skipped in DTB mode. Legacy ISA mapping requires IO range start zero. Early UART address is hard-coded by CPU implementation.

Test signals: DTB and LEFI boots should both populate memory; ISA IO ranges should appear in logic PIO; dynamic IRQ lower bound should not overlap legacy IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/numa.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/numa.c

Purpose: Initializes Loongson64 NUMA node topology, node memory data, CPU masks, and zone limits.

Important APIs/types/functions: Exports `__node_distances` and `__node_cpumask`; functions include `cpu_node_probe()`, `init_topology_matrix()`, `node_mem_init()`, `prom_meminit()`, `arch_zone_limits_init()`, `pcibus_to_node()`, and `prom_init_numa_memory()`.

Control flow: Discovers nodes from `loongson_sysconf.nr_nodes`, computes local/same-package/remote distances, calls `szmem()` for each node, allocates node data, reserves kernel and low gaps on node 0, and maps non-reserved CPUs into per-node cpumasks.

State and persistence: Populates node online/possible maps, memblock node assignments, `NODE_DATA`, `max_low_pfn`, zone PFN limits, and node CPU masks.

Dependencies and integration: Relies on `loongson_sysconf`, firmware memory map parsing in `szmem()`, and generic Linux NUMA/mm initialization.

Risks: CPU numbering uses active logical CPU order after reserved physical cores, which must match SMP maps. RS780E GPU reservation is hard-coded to top 32 MiB when node 0 reaches 4G.

Test signals: Boot logs should show nodes, PFN ranges, and CPU masks; `/sys/devices/system/node` should reflect expected topology; PCI buses should all map to node 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/numa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/pm.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/pm.c

Purpose: Registers firmware-assisted suspend-to-RAM for Loongson64 LEFI systems.

Important APIs/types/functions: `loongson_lefi_sleep()` assembly entry, `lefi_pm_enter()`, `lefi_pm_valid_state()`, and `loongson_pm_init()`.

Control flow: Only `PM_SUSPEND_MEM` is valid, and only when firmware provided `loongson_sysconf.suspend_addr`. Enter marks suspend via firmware, calls the firmware sleep routine with that address, marks resume via firmware, and returns.

State and persistence: Installs platform suspend ops when `fw_interface == LOONGSON_LEFI`.

Dependencies and integration: Requires `sleeper.S` and firmware reset/suspend table parsing in `env.c`.

Risks: Firmware suspend address is trusted executable code. DTB-only systems get no suspend ops from this file.

Test signals: `/sys/power/state` should offer mem only when suspend address exists; entering mem should call firmware and return through `loongson_lefi_sleep`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/reset.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/reset.c

Purpose: Registers firmware restart/poweroff handlers and Loongson64 kexec/crash-shutdown preparation.

Important APIs/types/functions: `firmware_restart()`, `firmware_poweroff()`, `loongson_kexec_prepare()`, `loongson_kexec_shutdown()`, `loongson_crash_shutdown()`, and `mips_reboot_setup()`.

Control flow: Init registers firmware sys-off handlers when firmware addresses exist. With kexec, it allocates argument/environment buffers, parses a `kexec` command-line segment into firmware-style argv, pins the control code page, brings offline CPUs online before kexec shutdown, and copies argv/envp to firmware argument addresses.

State and persistence: Stores kexec/kdump argc and argv buffers, copies firmware envp, writes global MIPS kexec function pointers and firmware argument globals.

Dependencies and integration: Consumes `loongson_sysconf.restart_addr/poweroff_addr`, `fw_arg1/fw_arg2`, MIPS kexec hooks, and optional SMP `secondary_kexec_args`.

Risks: Fixed physical control/argv addresses must be safe. Kexec command-line parsing is bounded but assumes segment buffer contains a string beginning with `kexec`. Firmware function pointers are trusted.

Test signals: `reboot` and `poweroff` should call firmware sys-off handlers; kexec should pass argv/envp to the next kernel and bring secondary CPUs to the reboot buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/setup.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/setup.c

Purpose: Performs Loongson64 platform memory setup from the selected FDT blob.

Important APIs/types/functions: Global `loongson_fdt_blob`; `plat_mem_setup()` calls `__dt_setup_arch()` when the blob is present.

Control flow: The FDT blob is selected during firmware env init; memory setup hands it to the OF/DT architecture setup code.

State and persistence: Publishes the device tree to the generic kernel DT subsystem.

Dependencies and integration: Depends on `env.c` selecting or fixing `loongson_fdt_blob`.

Risks: If no blob is selected, DT setup is skipped and later OF drivers may lack hardware descriptions.

Test signals: `/proc/device-tree` should exist on successful boot and reflect the selected Loongson64 built-in or firmware DTB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/sleeper.S -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/sleeper.S

Purpose: Implements the assembly trampoline for LEFI firmware suspend/resume.

Important APIs/types/functions: `loongson_lefi_sleep(unsigned long sleep_addr)` saves suspend CPU state, calls firmware with wake label and stack pointer, restores SMP slave setup, and returns through resume register restoration.

Control flow: `SUSPEND_SAVE` preserves context, `t9` holds firmware sleep function, `a0` receives wake label, `a1` receives stack pointer, and firmware returns to `wake`.

State and persistence: Saves/restores CPU register state around firmware sleep.

Dependencies and integration: Called by `pm.c`; uses MIPS suspend macros and `kernel-entry-init.h`.

Risks: Firmware must honor the wake callback ABI. Incorrect register preservation would corrupt resume.

Test signals: Suspend-to-RAM should resume through the `wake` label and return to C code without register corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/sleeper.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/smp.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/smp.c

Purpose: Implements Loongson-3 SMP bring-up, IPI delivery, secondary CPU initialization, CPU hotplug play-dead loops, and kexec handoff integration.

Important APIs/types/functions: `loongson3_smp_ops`, CSR and legacy IPI helpers, `loongson3_send_ipi_single/mask()`, `loongson3_ipi_interrupt()`, `loongson3_smp_setup()`, `loongson3_prepare_cpus()`, `loongson3_boot_secondary()`, and hotplug hooks `loongson3_cpu_disable/die()` plus `play_dead()`.

Control flow: Setup maps physical CPUs to logical CPUs while skipping reserved cores, probes CSR IPI support, initializes legacy mailbox register arrays from `smp_group[]`, enables CPU0 IPI, and records core/package IDs. Secondary boot writes start PC/SP/thread-info into CSR mailboxes or MMIO buffers. IPI interrupt clears action bits and runs scheduler or call-function handlers. Hotplug disables interrupts/TLB, waits for CPU_DEAD, and uses revision-specific CKSEG1 assembly loops to flush caches and wait for mailbox restart.

State and persistence: Uses per-CPU `cpu_state`, logical/physical CPU maps, IPI register pointer arrays, mailbox buffers, chip clock-control registers, and CPU hotplug state registration.

Dependencies and integration: Consumes `smp_group`, `loongson_sysconf`, chipcfg/freqctrl arrays from `env.c`, and MIPS SMP/core hotplug APIs.

Risks: CPU numbering, mailbox addresses, and node/package math must match firmware. Inline assembly is revision-specific and can hang a CPU if cache/mailbox assumptions are wrong. Workaround flags gate clock disable.

Test signals: Secondary CPUs should come online, reschedule/call-function IPIs should be delivered, CPU offline/online cycles should not hang, and kexec should park nonboot CPUs correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/smp.h -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/smp.h

Purpose: Defines Loongson-3 legacy SMP mailbox/IPI register base macros and offsets.

Important APIs/types/functions: Declares `smp_group[4]`; defines group bases, core offsets, and offsets for status, enable, set, clear, mask, and mailbox buffer registers.

Control flow: Header constants are used by `smp.c` to construct per-core MMIO pointers.

State and persistence: No state; references global firmware-initialized `smp_group`.

Dependencies and integration: Coupled to Loongson-3 legacy IPI register layout.

Risks: Offsets assume four cores per group and at most four groups.

Test signals: Legacy IPI path should compute addresses matching firmware-documented mailbox registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/time.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/time.c

Purpose: Initializes Loongson64 CPU counter frequency and optional HPET timer.

Important APIs/types/functions: `plat_time_init()` handles DTB clock lookup and timer frequency setup.

Control flow: DTB firmware mode initializes OF clocks, gets CPU0 clock, stores `cpu_clock_freq`, and releases the clock. Then the MIPS high-precision timer frequency is set to half CPU clock. Optional HPET setup runs when configured.

State and persistence: Sets global `mips_hpt_frequency` and possibly `cpu_clock_freq`.

Dependencies and integration: Depends on `loongson_sysconf.fw_interface`, OF clock bindings, and optional `setup_hpet_timer()`.

Risks: Missing CPU node or clock leaves the old CPU frequency in place. Assumes counter runs at CPU/2.

Test signals: DTB boot logs should not show CPU clock errors; scheduler clock should match real time; HPET should register when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/vbios_quirk.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/vbios_quirk.c

Purpose: Supplies a PCI fixup for ATI VGA devices whose ROM is shadowed by Loongson firmware rather than exposed in the PCI ROM BAR.

Important APIs/types/functions: `pci_fixup_video(struct pci_dev *pdev)` and `DECLARE_PCI_FIXUP_CLASS_HEADER()` for ATI device 0x9615 VGA class.

Control flow: If the ROM resource is empty and firmware provided `vgabios_addr`, disables PCI ROM decoding, releases any parent resource, and fills the ROM resource with the physical shadowed VBIOS address, fixed 256 KiB size, and fixed/shadow flags.

State and persistence: Mutates the PCI device ROM resource during header fixup.

Dependencies and integration: Uses `loongson_sysconf.vgabios_addr` from LEFI parsing and generic PCI quirk infrastructure.

Risks: Assumes shadowed VBIOS size is 256 KiB and address is valid. Only covers one ATI device ID.

Test signals: Affected VGA device should log a shadowed ROM resource and userspace should be able to read the ROM through PCI sysfs/resource paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/vbios_quirk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/Makefile

Purpose: Builds the Linux/MIPS software FPU emulator and IEEE754 helper library objects.

Important APIs/types/functions: `obj-y` includes `cp1emu.o`, IEEE754 core, double/single arithmetic, conversion, compare, fused multiply-add, class/min/max, and delay-slot emulation. `lib-y` includes helpers used as library code such as sqrt and long conversions. `me-debugfs.o` is conditional on `CONFIG_DEBUG_FS`.

Control flow: Build rules ensure the emulator and arithmetic helpers are always available for MIPS math emulation.

State and persistence: Build metadata only.

Dependencies and integration: Links with MIPS exception handling and FPU emulator entry points.

Risks: Removing an arithmetic object can break instruction cases in `cp1emu.c`.

Test signals: Kernel builds with FPU emulation should link all `ieee754*` references and optional debugfs stats when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/cp1emu.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/cp1emu.c

Purpose: Implements the MIPS COP1/FPU instruction emulator, including microMIPS translation, FPU branch/delay-slot handling, register transfer, memory access, arithmetic dispatch, COP1X operations, R6 comparisons, and exception signaling.

Important APIs/types/functions: Public entry `fpu_emulator_cop1Handler()` loops over emulatable FPU instructions. Core helpers include `microMIPS32_to_MIPS32()`, `isBranchInstr()`, `cop1_64bit()`, `cop1_cfc()`, `cop1_ctc()`, `cop1Emulate()`, `fpux_emu()`, and `fpu_emu()`. Register macros handle 32-bit, 64-bit, and hybrid FPR layouts.

Control flow: The handler initializes/saves FPU context, decodes current and next instruction for MIPS or microMIPS, skips NOPs, and calls `cop1Emulate()`. `cop1Emulate()` resolves delay slots, translates microMIPS FPU ops, handles loads/stores/control moves/branches, and delegates arithmetic to `fpu_emu()` or COP1X indexed/FMA operations to `fpux_emu()`. Arithmetic maps instruction function codes to IEEE754 single/double helpers, updates FCSR exception cause/sticky bits, raises SIGFPE when enabled, and writes results only after exception checks.

State and persistence: Mutates `pt_regs` EPC/GPRs, current thread FPU register file, `ctx->fcr31`, emulator stats, and optional fault address. Looping continues only for software-only FPU mode and stops on signals, non-FPU instruction, hardware-FPU boundary, or ISA mode switch.

Dependencies and integration: Uses MIPS branch/delay-slot emulation, user access helpers, perf software events, IEEE754 helpers, CPU feature macros, FPU ownership/context helpers, and debug stat macros.

Risks: Delay-slot and microMIPS translation correctness is critical for precise exceptions. User memory access must return SIGBUS for invalid access and SIGSEGV for page faults. FCSR exception masking must prevent result writeback when SIGFPE is required. Hybrid FPR layouts make register indexing error-prone.

Test signals: Floating-point programs on no-FPU systems should execute through the emulator; denormal/NaN edge cases on hardware-FPU systems should emulate one instruction; R6 compare/branch and microMIPS FPU encodings should produce correct EPC, result, and signal behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/cp1emu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_2008class.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_2008class.c

Purpose: Implements IEEE754-2008 `CLASS.D` classification for double precision values.

Important APIs/types/functions: `ieee754dp_2008class(union ieee754dp x)` returns the 10-bit MIPS class mask.

Control flow: Decodes the operand class and sign, then maps sNaN, qNaN, negative/positive infinity, normal, denormal, and zero to the specified mask bits.

State and persistence: No persistent state; uses decode macros and may log unknown classes.

Dependencies and integration: Called by `cp1emu.c` for R6 `CLASS.D`.

Risks: Unexpected class values return zero after `pr_err`, which would silently report no class.

Test signals: Known bit patterns for NaN, infinities, signed zeros, normals, and denormals should produce the MIPS-defined class mask.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_2008class.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_add.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_add.c

Purpose: Adds two IEEE754 double precision values with MIPS exception and rounding semantics.

Important APIs/types/functions: `ieee754dp_add(x, y)`.

Control flow: Clears exception state, flushes denormals as configured, handles NaN/infinity/zero class pairs, normalizes denormals, aligns exponents with guard/round/sticky bits, adds or subtracts mantissas by sign, normalizes cancellation, and formats the rounded result.

State and persistence: Uses global `ieee754_csr` exception and rounding state.

Dependencies and integration: Used by FPU emulator arithmetic, sqrt refinement, and legacy abs/neg paths.

Risks: Signed zero depends on rounding mode and operand signs. Mantissa alignment and sticky shifts are precision-sensitive.

Test signals: IEEE add vectors should cover NaNs, inf-inf invalid, signed zeros, denormals, cancellation, overflow, underflow, and all rounding modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_add.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_cmp.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_cmp.c

Purpose: Compares two IEEE754 double precision values for MIPS compare predicates.

Important APIs/types/functions: `ieee754dp_cmp(x, y, cmp, sig)` tests comparison bitmasks such as unordered, equal, less-than, and greater-than.

Control flow: Clears exceptions, flushes denormals, sets invalid for signaling comparisons or sNaNs, returns unordered predicate for NaNs, otherwise transforms signed bit patterns into comparable signed magnitudes and tests requested predicate bits.

State and persistence: Updates `ieee754_csr` invalid operation when required.

Dependencies and integration: Used by `cp1emu.c` for old and R6 double compare instructions.

Risks: Signed zero equality and negative ordering depend on the bit transformation.

Test signals: Compare tests should include qNaN/sNaN with quiet/signaling predicates, -0 vs +0, negative ordering, and unordered predicates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_cmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_div.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_div.c

Purpose: Divides IEEE754 double precision operands.

Important APIs/types/functions: `ieee754dp_div(x, y)`.

Control flow: Handles NaNs, infinities, zeros, zero-divide and invalid cases, normalizes denormals, then performs bitwise long division with rounding space and sticky remainder before formatting.

State and persistence: Updates `ieee754_csr` for invalid, divide-by-zero, inexact, overflow, or underflow through helper formatting.

Dependencies and integration: Used by FPU `DIV.D`, reciprocal/rsqrt helpers, and sqrt iterations.

Risks: Long division loop and sticky remainder determine correct rounding. Zero divided by zero and infinity divided by infinity must raise invalid.

Test signals: Vectors should include divide by zero, zero dividend, infinities, NaNs, denormals, exact divisions, inexact divisions, and sign combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_div.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_fint.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_fint.c

Purpose: Converts a signed 32-bit integer to IEEE754 double precision.

Important APIs/types/functions: `ieee754dp_fint(int x)`.

Control flow: Fast paths zero, one, and ten; records sign, handles minimum negative integer without undefined negation, normalizes mantissa, and builds a double directly.

State and persistence: Clears `ieee754_csr`; conversion is exact and should not set inexact/overflow.

Dependencies and integration: Used by `cp1emu.c` for `CVT.D.W`.

Risks: Minimum integer handling must avoid signed overflow.

Test signals: Convert 0, +/-1, +/-10, INT_MIN, INT_MAX, and random integers exactly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_fint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_flong.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_flong.c

Purpose: Converts a signed 64-bit integer to IEEE754 double precision.

Important APIs/types/functions: `ieee754dp_flong(s64 x)`.

Control flow: Fast paths zero, one, and ten; handles INT64_MIN safely; normalizes or right-shifts with sticky bits when more than double precision; formats with rounding.

State and persistence: Clears and updates `ieee754_csr` via formatting, including inexact for unrepresentable 64-bit integers.

Dependencies and integration: Used by `cp1emu.c` for `CVT.D.L` and by `dp_rint.c` to rebuild rounded integral doubles.

Risks: High-bit normalization and sticky shifts govern correct rounding near 2^53 and INT64 limits.

Test signals: Convert exact values below 2^53, inexact values above it, INT64_MIN/MAX, and all rounding modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_flong.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_fmax.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_fmax.c

Purpose: Implements double precision maximum and maximum-by-absolute-value operations for MIPS R6.

Important APIs/types/functions: `ieee754dp_fmax(x, y)` and `ieee754dp_fmaxa(x, y)`.

Control flow: Handles sNaN/qNaN precedence, prefers numeric operands over qNaNs, handles infinities and signed zeros, normalizes denormals, then compares signs, exponents, and mantissas. `fmaxa` compares magnitude and resolves ties by sign.

State and persistence: Clears and updates `ieee754_csr` for NaN exceptions.

Dependencies and integration: Called by `cp1emu.c` for `MAX.D` and `MAXA.D`.

Risks: Signed-zero and NaN selection differ from simple greater-than comparisons. File comments mention MIN/MINA wording despite implementing MAX/MAXA.

Test signals: Cover qNaN/sNaN, numeric-vs-NaN, +/-0, +/-inf, equal magnitude opposite signs, denormals, and normal ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_fmax.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_fmin.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_fmin.c

Purpose: Implements double precision minimum and minimum-by-absolute-value operations for MIPS R6.

Important APIs/types/functions: `ieee754dp_fmin(x, y)` and `ieee754dp_fmina(x, y)`.

Control flow: Mirrors fmax structure for NaN handling, infinity/zero special cases, denormal normalization, sign/exponent/mantissa comparison, and magnitude-based comparison for MINA.

State and persistence: Clears and updates `ieee754_csr` for NaN exceptions.

Dependencies and integration: Called by `cp1emu.c` for `MIN.D` and `MINA.D`.

Risks: Correct signed-zero result is subtle: min returns negative zero when either zero is negative. Magnitude ties have sign-specific behavior.

Test signals: Same class coverage as fmax, with emphasis on negative values and signed zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_fmin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_fsp.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_fsp.c

Purpose: Converts IEEE754 single precision values to double precision.

Important APIs/types/functions: `ieee754dp_fsp(union ieee754sp x)` and helper `ieee754dp_nan_fsp()`.

Control flow: Decodes the single, clears exceptions, flushes denormals as configured, preserves NaN payload/sign into double width, maps infinities and zeros, normalizes denormals, drops the hidden bit, and builds a double with widened mantissa.

State and persistence: Updates `ieee754_csr` for signaling NaN through `ieee754dp_nanxcpt()`.

Dependencies and integration: Used by `cp1emu.c` for `CVT.D.S`.

Risks: NaN payload widening and denormal normalization must preserve architecture semantics.

Test signals: Convert all special classes plus representative exact single values; sNaN should set invalid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_fsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_maddf.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_maddf.c

Purpose: Implements double precision fused multiply-add/subtract variants for MIPS R6 and MAC-style operations.

Important APIs/types/functions: Internal `srl128()` performs sticky 128-bit right shifts; `_dp_maddf(z, x, y, flags)` does the fused computation; wrappers include `ieee754dp_maddf`, `msubf`, `madd`, `msub`, `nmadd`, and `nmsub`.

Control flow: Handles NaN precedence across z/x/y, applies product/addition negation flags, resolves invalid infinity/zero products and opposite-signed infinities, multiplies normalized mantissas into 128 bits, aligns addend/product exponents, adds or subtracts 128-bit values, normalizes cancellation, shifts to double rounding precision, and formats once.

State and persistence: Clears and updates `ieee754_csr` through exception and formatting helpers.

Dependencies and integration: Used by `cp1emu.c` for fused R6 `MADDF/MSUBF` and MIPS4-style multiply-add operations.

Risks: Fused semantics require single final rounding; replacing with separate multiply/add changes results. Wrapper flag combinations encode subtle operation differences.

Test signals: FMA tests should compare against known fused results, including cancellation, inf*0 invalid, z infinity conflicts, NaN precedence, and all sign variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_maddf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_mul.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_mul.c

Purpose: Multiplies two IEEE754 double precision values.

Important APIs/types/functions: `ieee754dp_mul(x, y)`.

Control flow: Handles NaNs, infinity-zero invalid, infinities, zeros, denormal normalization, computes sign/exponent, multiplies 53-bit mantissas through 32-bit partial products into high/low 64-bit state, applies sticky rounding reduction, and formats.

State and persistence: Updates `ieee754_csr` through exception and formatting helpers.

Dependencies and integration: Used by `cp1emu.c`, sqrt, and non-fused multiply-add emulation.

Risks: Partial-product carry propagation and sticky bit construction are precision-critical.

Test signals: Cover special classes, sign combinations, exact powers of two, denormals, overflow, underflow, and inexact products.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_mul.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_rint.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_rint.c

Purpose: Rounds a double precision value to an integral-valued double according to current rounding mode.

Important APIs/types/functions: `ieee754dp_rint(x)`.

Control flow: Special classes return or signal as appropriate. Values already integral return unchanged. Fractional mantissa bits are split into residue/round/sticky/odd, rounding mode adjusts the integer mantissa, inexact is set if needed, and the result is rebuilt with original sign.

State and persistence: Reads `ieee754_csr.rm` and sets `IEEE754_INEXACT`.

Dependencies and integration: Used by `cp1emu.c` for R6 `RINT.D`.

Risks: Tie-to-even and sign-directed modes must be exact around half values and very small magnitudes.

Test signals: Test +/-0.5, +/-1.5, just-below/above integers, large integral values, NaNs, infinities, and all rounding modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_rint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_simple.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_simple.c

Purpose: Implements double precision absolute value and negation operations.

Important APIs/types/functions: `ieee754dp_neg(x)` and `ieee754dp_abs(x)`.

Control flow: In IEEE754-2008 ABS/NEG mode, directly toggles or clears the sign bit. In legacy mode, temporarily forces round-down and computes zero-minus-x or zero-plus-x via arithmetic helpers.

State and persistence: Temporarily mutates `ieee754_csr.rm` in legacy mode and restores it.

Dependencies and integration: Used by `cp1emu.c` for ABS.D and NEG.D and by non-fused multiply-add emulation.

Risks: Legacy arithmetic path can raise exceptions differently than sign-bit operations; saving/restoring rounding mode is required.

Test signals: Check NaNs, signed zeros, infinities, normals, and both `abs2008` modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_simple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_sqrt.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_sqrt.c

Purpose: Computes correctly rounded IEEE754 double precision square root.

Important APIs/types/functions: `ieee754dp_sqrt(x)` plus an initial approximation lookup table.

Control flow: Handles NaN, zero, infinity, negative invalid, and denormal normalization. It saves CSR, forces round-to-nearest and masks inexact, scales extreme exponents, builds an approximation, refines with division/multiply/add/subtract steps, verifies with a chopped quotient, adjusts for final rounding mode, restores CSR, and rescales.

State and persistence: Temporarily overrides `ieee754_csr` and merges inexact into saved status when required.

Dependencies and integration: Used by `cp1emu.c` for SQRT.D and reciprocal-square-root helper.

Risks: CSR save/restore and final ulp twiddle are delicate. Negative inputs must raise invalid except negative NaNs handled earlier.

Test signals: Validate perfect squares, non-squares under all rounding modes, subnormals, huge/small scaling, negative inputs, infinities, zeros, and NaNs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_sqrt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_sub.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_sub.c

Purpose: Subtracts IEEE754 double precision operands with MIPS rounding and exception behavior.

Important APIs/types/functions: `ieee754dp_sub(x, y)`.

Control flow: Handles class pairs for NaN, infinity, and zero, flips y sign for normal arithmetic, aligns exponents with guard/round/sticky bits, adds or subtracts mantissas by resulting signs, normalizes cancellation, selects signed zero by rounding mode, and formats.

State and persistence: Uses and updates `ieee754_csr`.

Dependencies and integration: Used by FPU `SUB.D`, sqrt, and legacy sign operations.

Risks: Infinity subtraction invalid cases and signed-zero results are subtle. Mantissa cancellation can underflow if normalization is wrong.

Test signals: Cover x-x, +0/-0 combinations, inf-inf same sign invalid, denormals, cancellation, and all rounding modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_sub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_tint.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_tint.c

Purpose: Converts double precision values to signed 32-bit integers according to current rounding mode.

Important APIs/types/functions: `ieee754dp_tint(x)`.

Control flow: NaNs and infinities raise invalid and return indefinite/overflow values. Normal/denormal values shift mantissa according to exponent, compute residue/round/sticky/odd bits, apply rounding mode, detect overflow including post-rounding overflow, set inexact, and apply sign.

State and persistence: Reads `ieee754_csr.rm` and sets invalid/inexact exception bits.

Dependencies and integration: Used by `cp1emu.c` for `CVT.W.D` and rounded/trunc/ceil/floor word conversions.

Risks: The valid `0x80000000` negative corner case is special. Shifts around exponent -1 and 31 are edge-sensitive.

Test signals: Test NaNs, infinities, +/-0, fractions around half, INT_MIN/INT_MAX boundaries, overflow after rounding, and all rounding modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_tint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_tlong.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_tlong.c

Purpose: Converts double precision values to signed 64-bit integers according to current rounding mode.

Important APIs/types/functions: `ieee754dp_tlong(x)`.

Control flow: Special classes raise invalid or return zero. For normals/denormals, exponent >=63 is overflow except exact negative INT64_MIN. Smaller values shift mantissa, compute rounding bits without undefined 64-bit shifts, apply rounding mode, detect post-round overflow, set inexact, and apply sign.

State and persistence: Reads and updates `ieee754_csr`.

Dependencies and integration: Used by `cp1emu.c` for `CVT.L.D` and long rounded/trunc/ceil/floor conversions.

Risks: Exact INT64_MIN handling and shift-by-64 avoidance are critical. Rounding can overflow after an initially in-range value.

Test signals: Test INT64_MIN exact, INT64_MAX boundary, huge overflow, +/-0.5, denormals, NaNs/infinities, and all rounding modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_tlong.c -->
