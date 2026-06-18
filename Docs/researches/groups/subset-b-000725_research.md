# subset-b-000725 Research

Grouped research for the requested source files. Each section title preserves the exact source path and is bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/octeon-irq.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/octeon-irq.c

Purpose: implements the Cavium Octeon MIPS interrupt subsystem across multiple controller generations: core CPU interrupt lines, CIU, CIU2, CIU3, GPIO interrupts, mailbox IPIs, watchdog interrupts, and CIB chained interrupt blocks. It is the board-level bridge between CP0 interrupt dispatch, device-tree interrupt domains, and Octeon CSR programming.

Important APIs, types, and functions: `arch_init_irq()` seeds default affinity and invokes `of_irq_init()` with Octeon controller match data; `plat_irq_dispatch()` loops over pending CP0 interrupt bits and calls the selected IP2/IP3/IP4 handlers; `octeon_irq_set_ip4_handler()` lets another subsystem install an IP4 handler. The key private state is `struct octeon_ciu_chip_data`, `struct octeon_core_chip_data`, `struct octeon_ciu3_info`, per-CPU CIU enable mirrors, per-CPU CIU3 IDT assignments, and the `octeon_irq_ciu_to_irq[8][64]` hardware-to-Linux IRQ map. CIU/CIU2/CIU3 mapping functions implement `irq_domain_ops`; exported `octeon_irq_get_block_domain()` exposes CIU3 block domains to other drivers.

Control flow: initialization selects a controller-specific path from device-tree compatible strings. CIU and CIU2 create domains, force legacy fixed mappings for work queues, timers, PCI INTx/MSI, mailboxes, and watchdogs, then enable CP0 IP2/IP3 and sometimes IP4. CIU3 allocates per-node `struct octeon_ciu3_info`, builds a default tree domain, routes interrupts through per-core IDTs, and dispatches by reading `DEST_PP_INT` and forwarding to `generic_handle_domain_irq()`. GPIO domains translate pin plus trigger specifiers into CIU line/bit mappings and program `GPIO_BIT_CFGX`.

State and persistence: the driver maintains per-CPU enable shadow masks for legacy CIU because interrupt handlers mask hardware summaries with software mirrors. CIU3 persists per-node domain arrays and per-CPU IDT selectors for the lifetime of the kernel. Mailbox state is per-core hardware ISC/CIU mailbox bits. There is no filesystem persistence; all state is boot-time hardware and irq-core registration state.

Dependencies and integration points: depends heavily on Linux generic IRQ (`irq_chip`, `irq_domain`, `handle_level_irq`, `handle_edge_irq`, `handle_percpu_irq`), Open Firmware interrupt parsing, SMP CPU masks, and Octeon CVMX CSR accessors. It integrates with `smp.c` through mailbox IRQs and `octeon_ciu3_mbox_send()`, with CPU hotplug through `irq_cpu_online/offline` and affinity migration, and with device-tree clients through interrupt-controller nodes.

Risks: interrupt enable shadow mirrors must remain synchronized with hardware, especially around CPU hotplug and affinity changes. Several paths choose a single CPU from affinity masks, so broad masks may not behave like generic IRQ balancing. CIU3 block-domain lookup assumes initialized node data. GPIO trigger translation accepts only known OF encodings and defaults invalid trigger logging to level low. Hardware errata paths, such as CN68XX CIU2 ACK behavior, are easy to regress.

Test signals: boot logs should show interrupt controllers probed without domain allocation errors; `/proc/interrupts` should show mailbox, timer, watchdog, PCI, GPIO, and device IRQs on expected CPUs; SMP IPI tests should exercise mailbox lines; CPU hotplug should not leave interrupts targeted at offline CPUs; GPIO edge/level tests should verify `irq_set_type()` behavior; CIU3 systems should validate per-node domain lookup and spurious interrupt handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/octeon-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/octeon-memcpy.S -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/octeon-memcpy.S

Purpose: provides an Octeon-tuned unified assembly implementation of `memcpy`, `memmove`, `__raw_copy_from_user`, and `__raw_copy_to_user` for 64-bit MIPS. It optimizes common aligned and unaligned copy paths while preserving user-copy exception semantics.

Important APIs and labels: exported symbols are `memcpy`, `memmove`, `__raw_copy_from_user`, and `__raw_copy_to_user`. Internal labels include `__memcpy`, `src_unaligned`, `copy_bytes`, `l_exc`, `l_exc_copy`, store exception fixups (`s_exc_p*`), and reverse-copy `__rmemcpy`. The `EXC()` macro emits exception-table entries for faultable loads and stores.

Control flow: `memcpy` returns the original destination in `v0` and falls into the shared copy engine. The engine prefetches for large copies, handles aligned 16-word, 8-word, 4-word, word, and byte tails, and has a separate unaligned-source path using MIPS left/right load instructions. User-copy failures enter exception handlers that compute remaining byte count in `len`; load failures copy known-good bytes first to avoid leaking stale destination data to user space. `memmove` checks overlap and either delegates to forward `__memcpy` or performs byte-wise reverse/upward copying.

State and persistence: no persistent state. Correctness depends on register conventions: `dst`, `src`, `len`, and `AT` must retain meanings described in the header comments, especially for user-copy exception recovery.

Dependencies and integration points: depends on MIPS ABI register definitions, exception table format, thread `THREAD_BUADDR`, and uaccess calling conventions. It overrides core memory primitives for Octeon builds and is referenced by optional L2 locking in Octeon setup.

Risks: the assembly is sensitive to delay slots, endianness macros, register clobbers, and exception-table target accuracy. Any change that updates `src` and `dst` asymmetrically can break the load-exception invariant and leak kernel data on copy-from-user faults. `memmove` reverse path is intentionally simple, so performance differs from forward copy for overlap.

Test signals: kernel selftests or boot smoke tests should cover aligned and unaligned copies, short lengths, long lengths over prefetch thresholds, overlap cases for `memmove`, and fault-injection/usercopy tests that verify the returned uncopied length and destination clearing behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/octeon-memcpy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/octeon-platform.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/octeon-platform.c

Purpose: publishes Octeon platform devices and mutates built-in or appended device trees so Linux sees only hardware actually present on a given Octeon board. It also initializes Octeon USB clock/reset sequences, RNG platform resources, MAC addresses, PHY bindings, fixed links, and bootbus-attached devices.

Important APIs and functions: USB code registers EHCI/OHCI platform data through `octeon_ehci_device_init()` and `octeon_ohci_device_init()`, with clock control in `octeon2_usb_clocks_start()` and `octeon2_usb_clocks_stop()`. `octeon_rng_device_init()` registers `octeon_rng`. Device-tree mutation flows through `octeon_fill_mac_addresses()`, `octeon_prune_device_tree()`, `octeon_fdt_set_phy()`, `octeon_fdt_set_mac_addr()`, `octeon_fdt_pip_iface()`, and `octeon_fdt_pip_port()`. `octeon_publish_devices()` calls `of_platform_populate()`.

Control flow: arch/device initcalls reset USB if necessary, attach USB platform data after OF devices exist, register RNG resources, and populate OF platform devices matching `simple-bus` and Octeon compatibles. During early boot, setup code calls FDT pruning and MAC filling: aliases are resolved, unavailable interfaces and buses are nopped out, PHY addresses are rewritten from board helper results, UART clock properties are updated, CompactFlash and LED bootbus ranges are repaired, and USB reference-clock properties are adjusted.

State and persistence: `octeon2_usb_clock_start_cnt` and its mutex refcount USB clock usage while EHCI/OHCI share the same UCTL. FDT changes happen in-place in `initial_boot_params` before unflattening, so the resulting live device tree persists for all later drivers but is not written back to storage.

Dependencies and integration points: uses libfdt, Linux OF platform population, USB platform driver pdata, CVMX board helpers, Octeon CSR definitions, `octeon_get_io_clock_rate()`, and `octeon_bootinfo`. It integrates with Ethernet drivers through corrected `local-mac-address`, `phy-handle`, `fixed-link`, and delay properties.

Risks: in-place FDT mutation requires properties to have compatible existing sizes for `fdt_setprop_inplace()`. Wrong board detection can delete live devices or expose absent devices. USB clock sequencing is hardware-specific and timing-sensitive. PHY alternate-handle replacement rewrites property names and assumes valid phandles and compatible property lengths.

Test signals: boot with internal, appended, and bootloader-passed DTBs; inspect `/proc/device-tree` for pruned nodes and MAC addresses; verify Ethernet PHY probing on affected boards; exercise EHCI/OHCI probe/remove and suspend-like power callbacks; confirm RNG platform resources register; check boot logs for FDT rename/property errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/octeon-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/octeon_boot.h -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/octeon_boot.h

Purpose: defines the small subset of Octeon bootloader data structures and fixed addresses needed by the Linux SMP and hotplug paths. It lets the kernel restart secondary cores through bootloader vectors without importing the full bootloader header set.

Important APIs and types: `struct boot_init_vector` describes per-core boot-vector entries: boot code address, app start function, saved `k0`, boot-info pointer, and flags. `struct linux_app_boot_info` mirrors bootloader state such as signature, available core mask, TLB initialization address, exception base, CompactFlash base addresses, and LED display base. Constants include `LABI_SIGNATURE`, `LABI_ADDR_IN_BOOTLOADER`, `BOOTLOADER_BOOT_VECTOR`, `LINUX_APP_BOOT_BLOCK_NAME`, and `AVAIL_COREMASK_OFFSET_IN_LINUX_APP_BOOT_BLOCK`.

Control flow and integration: `smp.c` reads `linux_app_boot_info` during hotplug capability detection, updates boot vectors before resetting or NMI-starting cores, and uses the available core mask to return dead cores to firmware control. The header has no executable control flow of its own.

State and persistence: the structures describe physical bootloader-resident state. Kernel writes to boot vectors and availability masks affect firmware-visible memory during the running boot, but not persistent storage.

Dependencies: depends on Linux fixed-width types and Octeon boot memory layout conventions. Endianness-specific field layout is used for `linux_app_boot_info`, so consumers rely on correct `__BIG_ENDIAN_BITFIELD` selection.

Risks: hardcoded offsets and addresses must match bootloader layout. A mismatch can corrupt firmware data or fail CPU hotplug. The bitfield ordering differences are subtle and should not be refactored without checking bootloader ABI.

Test signals: SMP boot should start all firmware-supplied cores; CPU hotplug should update available core masks and restart cores through the boot vector; boards without supported LABI data should log that hotplug is unsupported rather than crashing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/octeon_boot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/setup.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/setup.c

Purpose: performs Octeon early platform setup: imports bootloader descriptors, initializes CVMX system information, parses command-line and memory limits, sets reboot/halt/kexec hooks, creates memblock ranges from Octeon bootmem, initializes device tree selection, and registers late platform devices such as EDAC and dummy PCI I/O space.

Important APIs and functions: exported helpers include `octeon_is_simulation()`, `octeon_is_pci_host()`, `octeon_get_clock_rate()`, `octeon_get_io_clock_rate()`, `octeon_get_boot_coremask()`, `octeon_check_cpu_bist()`, `octeon_user_io_init()`, `prom_putchar()`, `octeon_bootinfo`, `octeon_bootbus_sem`, and `octeon_should_swizzle_table`. Core entry points are `prom_init()`, `fw_init_cmdline()`, `plat_get_fdt()`, `plat_mem_setup()`, `prom_free_prom_memory()`, and `device_tree_init()`.

Control flow: `prom_init()` receives the boot descriptor from `fw_arg3`, maps CVMX bootinfo, fills `cvmx_sysinfo`, sets I/O clock rate, installs multiplier save/restore snippets, initializes board LEDs, reserves optional low 32-bit memory, applies L2 locking options, parses `mem=` and `crashkernel=`, chooses console UART, initializes timers and SMP operations, and configures CP0 CVMMEMCTL. `plat_mem_setup()` converts CVMX bootmem allocations into memblock regions, excluding PCIe holes and crashkernel regions. `device_tree_init()` chooses appended, bootloader-passed, or internal DTB, optionally prunes it, fills MAC addresses, then unflattens and records system type.

State and persistence: persistent runtime state includes global boot descriptor and bootinfo pointers, selected UART, memory limit/reservation values, crashkernel reservation values, system type string, EDAC-disable flag, dummy I/O-space allocation, and exported bootbus semaphore. Hardware state includes watchdog disable/reset behavior, LED display messages, CVMMEMCTL settings, soft-BIST settings, and bootmem named-block allocation/free state.

Dependencies and integration points: depends on CVMX bootmem/sysinfo, Octeon model/feature macros, memblock, OF/FDT, MIPS reboot/kexec hooks, serial 8250 early printk, EDAC platform drivers, and optional PCI. It calls into `octeon-platform.c` for device-tree pruning and MAC filling and into `smp.c` for SMP registration.

Risks: early boot code is order-sensitive. Bad boot descriptors, bad FDT headers, bootmem allocation failures, or incorrect memory exclusion can panic or expose invalid memory. Kexec paths mutate bootmem named blocks and segment reservations; crashkernel parsing is explicitly old-style. String concatenation is bounded but still depends on bootloader arguments fitting `arcs_cmdline`.

Test signals: boot on simulator and hardware variants; verify parsed command line and console UART; confirm memblock map avoids crashkernel and PCIe hole pages; kexec and crash-kexec should boot or dump cleanly; EDAC devices should register unless disabled; `prom_putchar()` should work for early watchdog output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/smp.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/smp.c

Purpose: implements Octeon SMP startup, IPI delivery, CPU hotplug, and platform SMP operation registration. It supports legacy CIU mailbox IPIs and CIU3 mailbox IPIs used by CN78xx-class systems.

Important APIs and functions: `octeon_setup_smp()` registers either `octeon_smp_ops` or `octeon_78xx_smp_ops`. `octeon_send_ipi_single()` and `octeon_send_ipi_mask()` write CIU mailbox registers; `octeon_78xx_send_ipi_single()` uses `octeon_ciu3_mbox_send()`. Secondary startup uses globals `octeon_processor_boot`, `octeon_processor_sp`, `octeon_processor_gp`, and optional relocated entry. Hotplug uses `octeon_cpu_disable()`, `octeon_cpu_die()`, `play_dead()`, and `octeon_update_boot_vector()`.

Control flow: `octeon_smp_setup()` builds logical CPU maps from the CVMX core mask and optional bootloader hotplug data. `octeon_boot_secondary()` publishes stack and thread-info pointers then waits for the secondary to consume them. `octeon_init_secondary()` installs exception base, checks BIST, initializes count/timer state, and invokes the interrupt setup hook selected by `octeon-irq.c`. `octeon_prepare_cpus()` requests mailbox IRQs; the mailbox handler decodes action bits into reschedule, call-function, and I-cache flush handlers. CIU3 systems request separate per-mailbox IRQs.

State and persistence: shared boot globals form a one-at-a-time secondary CPU rendezvous. CPU hotplug state is tracked per CPU and also reflected into bootloader-resident availability masks and boot vectors. IPI delivery is transient hardware mailbox state.

Dependencies and integration points: depends on Linux `plat_smp_ops`, scheduler and generic SMP IPI handlers, Octeon interrupt setup callbacks, CVMX core numbering, bootloader data from `octeon_boot.h`, kexec support, and CPU hotplug state machine registration.

Risks: CPU numbering assumes bootloader and CVMX core masks are consistent. Boot-secondary timeout can leave partial shared state. Hotplug writes hardcoded bootloader structures and resets cores, so stale bootloader metadata is high risk. CIU3 and non-CIU3 mailbox numbering differ, requiring matching interrupt-controller setup.

Test signals: SMP boot should enumerate expected logical CPU mapping; IPIs should drive scheduler and call-function interrupts; `echo 0/1 > /sys/devices/system/cpu/cpuX/online` should offline/online cores where supported; CIU3 systems should show separate Scheduler/SMP-Call/ICache-Flush mailbox IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cobalt/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/cobalt/Makefile

Purpose: selects the Cobalt board-support objects for the MIPS kernel build.

Important build behavior: `obj-y` always includes buttons, IRQ, LCD, LED, MTD, reset, RTC, serial, setup, and time support. `pci.o` is included only when `CONFIG_PCI` is enabled.

Dependencies and integration: this file ties Cobalt-specific source files into the architecture build; those files then register platform devices and board hooks.

Risks and test signals: missing an object here silently removes board functionality. Build tests should cover Cobalt with and without `CONFIG_PCI` to verify conditional inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cobalt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cobalt/buttons.c -->
# sources/distributed-fs/ceph-client/arch/mips/cobalt/buttons.c

Purpose: registers the Cobalt front-panel buttons as a platform device.

Important APIs: `cobalt_add_buttons()` allocates a `"Cobalt buttons"` platform device, attaches one memory resource covering `0x1d000000..0x1d000003`, and registers it at `device_initcall` time.

Control flow and state: all state is static init data plus the platform device registered with the driver core. Failure paths release the allocated platform device.

Dependencies and integration: depends on a matching platform driver for `"Cobalt buttons"` and on the fixed Cobalt memory map. It integrates with the board setup through generic platform-device probing.

Risks and test signals: wrong address range breaks button input. Boot logs should show platform-device registration/probe; pressing hardware buttons should produce input events if the matching driver is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cobalt/buttons.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cobalt/irq.c -->
# sources/distributed-fs/ceph-client/arch/mips/cobalt/irq.c

Purpose: provides Cobalt interrupt initialization and CP0 interrupt dispatch.

Important APIs: `arch_init_irq()` initializes MIPS CPU IRQs, GT641xx interrupts, and i8259 interrupts, then requests cascade IRQs with `no_action`. `plat_irq_dispatch()` prioritizes GT641xx on IP2, i8259 on IP6, then CPU IRQs IP3/IP4/IP5/IP7, otherwise spurious.

Control flow and state: dispatch reads CP0 status/cause pending bits and forwards to `gt641xx_irq_dispatch()`, `i8259_irq()`, or `do_IRQ()`. There is no local persistent state beyond registered cascade descriptors.

Dependencies and integration: depends on GT64120/GT641xx and i8259 interrupt support plus Cobalt IRQ constants from `<irq.h>`.

Risks and test signals: cascade IRQ registration must match platform wiring. Boot should show no failed cascade requests; devices behind PCI/ISA should generate interrupts through the expected paths; spurious interrupt counters should remain low.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cobalt/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cobalt/lcd.c -->
# sources/distributed-fs/ceph-client/arch/mips/cobalt/lcd.c

Purpose: registers the Cobalt LCD memory window as a platform device.

Important APIs: `cobalt_lcd_add()` allocates `"cobalt-lcd"` with a single memory resource `0x1f000000..0x1f00001f` and runs as a `device_initcall`.

State and integration: no persistent local state after init; the resource is transferred to the platform device. A matching LCD driver consumes the fixed MMIO region.

Risks and test signals: incorrect resource size or address prevents LCD access. Verify platform-device probe and visible LCD updates on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cobalt/lcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cobalt/led.c -->
# sources/distributed-fs/ceph-client/arch/mips/cobalt/led.c

Purpose: registers the correct Cobalt LED platform device for Qube versus RaQ boards.

Important APIs: `cobalt_led_add()` checks `cobalt_board_id` and allocates `"cobalt-qube-leds"` for Qube1/Qube2 or `"cobalt-raq-leds"` otherwise. The resource is one MMIO byte at `0x1c000000`.

Control flow and state: board ID determines device name; registration failure releases the device. State persists only in the platform device.

Dependencies and integration: depends on `<cobalt.h>` board identification and matching LED drivers.

Risks and test signals: wrong board ID selects the wrong LED driver semantics. Boot should register one LED platform device; LED class entries should match board family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cobalt/led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cobalt/mtd.c -->
# sources/distributed-fs/ceph-client/arch/mips/cobalt/mtd.c

Purpose: registers Cobalt firmware flash as a `physmap-flash` platform device.

Important APIs and data: `cobalt_mtd_partitions` defines a single `"firmware"` partition of `0x80000` bytes. `cobalt_flash_data` sets bus width 1. `cobalt_mtd_resource` maps `0x1fc00000..0x1fc7ffff`. `cobalt_mtd_init()` registers the static platform device.

State and integration: partition and resource state are static and handed to MTD/physmap. There is no runtime mutation.

Risks and test signals: partition boundaries are fixed and must match firmware flash layout. Test by checking MTD device enumeration and read-only/read-write policy in the consuming driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cobalt/mtd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cobalt/pci.c -->
# sources/distributed-fs/ceph-client/arch/mips/cobalt/pci.c

Purpose: registers the Cobalt GT64120-backed PCI controller when PCI is enabled.

Important APIs and data: `cobalt_pci_controller` references external `gt64xxx_pci0_ops`, defines PCI memory and I/O resource windows, sets `io_offset`, and maps I/O via `CKSEG1ADDR(GT_DEF_PCI0_IO_BASE)`. `cobalt_pci_init()` registers the controller at `arch_initcall`.

State and integration: controller registration persists in the PCI core. It depends on GT64120 constants and PCI ops supplied elsewhere.

Risks and test signals: I/O offset and resource window mistakes break PCI config/resource assignment. Build with `CONFIG_PCI`; boot should enumerate PCI devices and assign resources inside the configured windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cobalt/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cobalt/reset.c -->
# sources/distributed-fs/ceph-client/arch/mips/cobalt/reset.c

Purpose: implements Cobalt halt and restart hooks plus a power-off LED trigger.

Important APIs: `ledtrig_power_off_init()` registers trigger `"power-off"`. `cobalt_machine_halt()` activates the trigger, disables local IRQs, and waits forever using `cpu_wait()` if available. `cobalt_machine_restart()` writes reset value `0x0f` to MMIO reset port `0x1c000000`, then falls back to halt.

State and integration: the LED trigger persists in the LED subsystem. Reboot hooks are installed from `setup.c`.

Risks and test signals: restart depends on the fixed reset port and value. Halt should light the configured LED on RaQ systems; reboot should not return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cobalt/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cobalt/rtc.c -->
# sources/distributed-fs/ceph-client/arch/mips/cobalt/rtc.c

Purpose: registers the Cobalt MC146818-compatible RTC.

Important APIs: `cobalt_rtc_add()` allocates `"rtc_cmos"`, adds I/O resource `0x70..0x77` and IRQ `RTC_IRQ`, then registers it at `device_initcall`.

State and integration: no mutable local state; RTC resources are owned by the platform device and consumed by the CMOS RTC driver.

Risks and test signals: IRQ/resource mismatch breaks clock reads or alarms. Verify `rtc_cmos` probe, `/dev/rtc*`, and persistent-clock reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cobalt/rtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cobalt/serial.c -->
# sources/distributed-fs/ceph-client/arch/mips/cobalt/serial.c

Purpose: registers the Cobalt 8250 UART as a platform serial device, except on Qube1 where no UART exists.

Important APIs and data: `cobalt_uart_resource` describes MMIO `0x1c800000..0x1c800007` and `SERIAL_IRQ`. `cobalt_serial8250_port` sets `uartclk` 18.432 MHz, `UPIO_MEM`, `UPF_IOREMAP`, `UPF_BOOT_AUTOCONF`, and `UPF_SKIP_TEST`. `cobalt_uart_add()` creates a `serial8250` platform device with `PLAT8250_DEV_PLATFORM`.

State and integration: board ID gates registration; serial pdata persists in the platform device.

Risks and test signals: Qube1 must not register a nonexistent UART. Other boards should expose ttyS with working interrupts and early console continuity from setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cobalt/serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cobalt/setup.c -->
# sources/distributed-fs/ceph-client/arch/mips/cobalt/setup.c

Purpose: installs Cobalt machine hooks, reserves unused legacy I/O ranges, initializes memory from firmware arguments, and sets up early serial printk.

Important APIs: `get_system_type()` maps `cobalt_board_id` to human-readable board names. `plat_mem_setup()` installs restart/halt/power-off hooks, sets GT64120 I/O port base, expands `ioport_resource`, and reserves DMA/keyboard resource ranges unused by Cobalt. `prom_init()` decodes memory size and argument count from `fw_arg0`, appends firmware arguments to `arcs_cmdline`, adds memblock RAM, and configures early 8250 printk.

State and integration: persistent state includes command line, memblock RAM, reserved I/O resources, reboot hooks, and early printk mapping.

Risks and test signals: `fw_arg0` packing must match firmware; wrong mem size can expose invalid RAM. Boot should report correct system type, memory size, command line, and early serial output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cobalt/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cobalt/time.c -->
# sources/distributed-fs/ceph-client/arch/mips/cobalt/time.c

Purpose: initializes Cobalt timer hardware and calibrates the MIPS high-precision timer against the GT641xx timer.

Important APIs: `plat_time_init()` calls `setup_pit_timer()`, sets the GT641xx base clock to 50 MHz, waits for timer0 state transitions, measures CP0 Count over 100 ms, and sets `mips_hpt_frequency`.

State and integration: writes global timer frequency for MIPS timekeeping and relies on PIT/GT641xx timer infrastructure.

Risks and test signals: busy-wait loops assume GT641xx timer state changes; a stuck timer hangs boot. Boot logs should show plausible MIPS counter frequency and stable timekeeping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cobalt/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/crypto/Kconfig -->
# sources/distributed-fs/ceph-client/arch/mips/crypto/Kconfig

Purpose: creates the MIPS CPU accelerated crypto algorithms menu.

Important behavior: the menu is currently empty between `menu "Accelerated Cryptographic Algorithms for CPU (mips)"` and `endmenu`, so it acts as a placeholder for future MIPS crypto options.

Dependencies and integration: sourced by the architecture Kconfig tree; no symbols are defined here.

Risks and test signals: low functional risk, but adding options here should include dependencies for CPU features and matching Makefile objects. Kconfig parsing should continue to include the empty menu without warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/crypto/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/crypto/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/crypto/Makefile

Purpose: placeholder Makefile for MIPS crypto implementation objects.

Important behavior: no objects are currently selected, matching the empty Kconfig menu.

Dependencies and integration: included by the MIPS build when crypto sources are considered. Future accelerated crypto files would be added here under config-specific `obj-*` assignments.

Risks and test signals: no runtime behavior. Build tests should remain unchanged; future additions must pair Kconfig symbols with object names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/crypto/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/dec/Makefile

Purpose: selects DECstation platform support objects for the MIPS build.

Important build behavior: always builds bus-error handlers, interrupt handler assembly, I/O ASIC IRQ support, KN02 CSR IRQ support, platform devices, reset, setup, and time. TurboChannel support `tc.o` depends on `CONFIG_TC`; write-buffer flushing support `wbflush.o` depends on `CONFIG_CPU_HAS_WB`.

Dependencies and integration: this Makefile binds architecture setup, PROM support, IRQ controllers, and optional buses to the kernel image.

Risks and test signals: omitting optional objects under the wrong config can break buses or required barriers. Build matrix should include DECstation with TurboChannel and write-buffer-capable CPU configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/ecc-berr.c -->
# sources/distributed-fs/ceph-client/arch/mips/dec/ecc-berr.c

Purpose: handles bus errors on DECstation systems with ECC logic, including KN02, KN03, KN05, and related DECsystem variants.

Important APIs: `dec_ecc_be_handler()` is installed as the MIPS bus-error exception handler; `dec_ecc_be_interrupt()` handles asynchronous bus error IRQs; `dec_ecc_be_init()` selects KN02 or KN03/KN05 register setup. Private helpers read error address/check syndrome registers, acknowledge errors, classify CPU/DMA events, and correct single-bit ECC reads by rewriting the affected word.

Control flow: the backend reads `ERRADDR` and `CHKSYN`, acknowledges non-ECC errors early, classifies CPU timeout, DMA overrun, memory read/write ECC, adjusts read addresses for pipeline behavior, and returns `MIPS_BE_FIXUP`, `MIPS_BE_DISCARD`, or fatal. Single-bit ECC errors are rewritten and discarded; double/multiple errors remain fatal. Interrupt context fatal errors call `die()`.

State and persistence: static volatile pointers hold model-specific error registers. KN02 and KN03 init routines program ECC correction/diagnostic bits and clear firmware leftovers. There is no persistent storage state.

Dependencies and integration: integrates with `dec/setup.c` bus-error initialization and interrupt request. Depends on DEC ECC/KNxx register definitions, MIPS trap bus-error action codes, ratelimited logging, and IRQ register access.

Risks and test signals: incorrect syndrome classification can mislabel or mishandle ECC. Fixup is allowed only for CPU errors; DMA errors remain fatal. Test with simulated or hardware ECC/parity errors, ensure corrected single-bit errors log and continue, and fatal paths report EPC/RA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/ecc-berr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/int-handler.S -->
# sources/distributed-fs/ceph-client/arch/mips/dec/int-handler.S

Purpose: DECstation low-level interrupt dispatch assembly. It maps CP0 pending interrupt bits and cascaded CSR/I/O ASIC interrupt-status bits to Linux IRQ numbers or secondary assembly dispatch helpers.

Important labels: `plat_irq_dispatch`, `kn02_io_int`, `kn02xa_io_int`, `kn03_io_int`, `cpu_all_int`, `kn02_all_int`, `asic_all_int`, `asic_dma_int`, `dec_intr_unimplemented`, and `asic_intr_unimplemented`. It consumes global priority tables `cpu_mask_nr_tbl` and `asic_mask_nr_tbl` initialized in `dec/setup.c`.

Control flow: dispatch reads CP0 Cause/Status, masks pending bits, immediately handles FPU interrupt where applicable, scans the CPU priority table for the first matching mask, then either dispatches a direct IRQ number or jumps to a helper address. Cascaded helpers read KN02 CSR or IOASIC SIR/SIMR, mask enabled bits, scan ASIC priority tables, and dispatch direct IRQs or helper routines. DMA and low-priority helpers use bit-search logic to pick the highest relevant IRQ.

State and integration: no local persistent state; it relies on global tables and hardware status registers. It calls `dec_irq_dispatch()` to enter generic IRQ handling and calls panic helpers for unimplemented vectors.

Risks and test signals: table contents and assembly pointer/integer union layout must match exactly. An uninitialized table entry can panic. Test boot on each DECstation machine type, exercise cascade, DMA, RTC, FPU, halt, and bus interrupts, and inspect priority ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/int-handler.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/ioasic-irq.c -->
# sources/distributed-fs/ceph-client/arch/mips/dec/ioasic-irq.c

Purpose: implements IRQ chip operations for DEC I/O ASIC interrupt lines and DMA interrupt subtypes.

Important APIs: `init_ioasic_irqs(int base)` masks all ASIC interrupts, assigns `ioasic_irq_type` to regular lines, assigns `ioasic_dma_irq_type` to DMA lines, and selects edge or fasteoi flow based on informational versus error DMA interrupt masks.

Control flow: mask/unmask manipulate the IOASIC SIMR enable register. Regular ack masks and flushes. DMA ack/eoi clears the SIR bit. Informational DMA interrupts are cleared early with `handle_edge_irq`; DMA error interrupts clear at EOI after handlers run.

State and integration: `ioasic_irq_base` records the Linux IRQ base. Hardware state is in SIMR/SIR registers. The dispatch assembly selects these IRQs based on `asic_mask_nr_tbl`.

Risks and test signals: DMA informational/error classification affects whether a device can resume DMA correctly. Test network, SCSI, SCC, and other IOASIC DMA users, including threaded handlers with `IRQF_ONESHOT` for error DMA lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/ioasic-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/kn01-berr.c -->
# sources/distributed-fs/ceph-client/arch/mips/dec/kn01-berr.c

Purpose: handles parity and timeout bus errors on KN01 DECstation 2100/3100 systems.

Important APIs: `dec_kn01_be_handler()` handles synchronous bus-error exceptions; `dec_kn01_be_interrupt()` handles bus-error IRQs; `dec_kn01_be_init()` initializes the cached CSR and enables parity detection. `cached_kn01_csr` is global because CSR low bits are write-only and must be preserved by software.

Control flow: the backend acknowledges errors early, determines whether the error came from exception or interrupt context, reconstructs the failing physical address for reads by inspecting the faulting instruction and TLB entry, classifies memory parity versus I/O timeout, and returns fixup or fatal. Interrupt context ignores video-shared false positives and dies for fatal errors.

State and integration: `cached_kn01_csr` plus a raw spinlock protect write-only CSR updates. The handler integrates with `dec/setup.c` bus-error selection and shares the bus interrupt on KN01.

Risks and test signals: address reconstruction is delicate for branch-delay and TLB state. Shared video/bus interrupt filtering is required. Test parity/timeout events, `get_dbe()` fixups, and video interrupt coexistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/kn01-berr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/kn02-irq.c -->
# sources/distributed-fs/ceph-client/arch/mips/dec/kn02-irq.c

Purpose: implements the KN02 Control and Status Register interrupt chip used by DECstation 5000/200.

Important APIs: `init_kn02_irqs(int base)` masks CSR interrupts, assigns `kn02_irq_type` to KN02 IRQ lines, and records the IRQ base. `cached_kn02_csr` stores write-only CSR bits.

Control flow: unmask and mask set or clear interrupt-enable bits at offset `irq - base + 16`, write the cached CSR to hardware, and ack by masking plus I/O barrier.

State and integration: `cached_kn02_csr` persists as the software copy of write-only CSR bits. Dispatch assembly reads CSR status/mask and maps enabled bits to Linux IRQs via `asic_mask_nr_tbl`.

Risks and test signals: stale cache bits can disable unrelated CSR functionality. Test SCSI, Lance, DZ11, TurboChannel, and cascade interrupts on KN02, and confirm mask/unmask updates are reflected in hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/kn02-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/kn02xa-berr.c -->
# sources/distributed-fs/ceph-client/arch/mips/dec/kn02xa-berr.c

Purpose: handles parity and timeout bus errors on KN02-BA/KN04-BA and KN02-CA/KN04-CA DECstation systems.

Important APIs: `dec_kn02xa_be_handler()`, `dec_kn02xa_be_interrupt()`, and `dec_kn02xa_be_init()`. The backend reads memory error register and error address register, classifies memory parity versus TurboChannel timeout, logs byte-lane status, and returns fixup or fatal.

Control flow: ack writes MER and memory-interrupt registers immediately. If the address is below 256 MB it is treated as memory parity; otherwise I/O/TurboChannel timeout. Fixup is honored for synchronous exception handling only; interrupt fatal paths call `die()`.

State and integration: no long-lived local state other than hardware registers. Init enables error reporting for R4000SC variants through the KN4K memory board CSR and clears leftover firmware errors.

Risks and test signals: byte-lane reporting depends on MER bits; fixing or suppressing the wrong error can hide data corruption. Test with protected bus probes, memory parity injection where possible, and asynchronous bus IRQ handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/kn02xa-berr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/platform.c -->
# sources/distributed-fs/ceph-client/arch/mips/dec/platform.c

Purpose: registers DECstation RTC as a platform device.

Important APIs and data: `dec_rtc_resources` is filled at init with `RTC_PORT(0)` through `RTC_PORT(0) + dec_kn_slot_size - 1`; `dec_rtc_info` marks no periodic frequency support and 64-byte address space; `dec_add_devices()` registers `rtc_cmos`.

State and integration: depends on `dec_kn_slot_size` and `dec_rtc_base` established by PROM identification. Platform-device state persists in the driver core.

Risks and test signals: if PROM identification has not set slot size correctly, the RTC resource spans the wrong MMIO window. Verify `rtc_cmos` probe and persistent time reads on each supported DECstation family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/prom/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/dec/prom/Makefile

Purpose: selects DECstation PROM support library objects.

Important build behavior: always includes init, memory, command-line, identify, and console helpers. Adds `locore.o` only for R3000 CPUs.

Dependencies and integration: these objects run before normal platform setup to establish PROM vectors, memory, machine type, and early console.

Risks and test signals: wrong CPU conditional can omit the early exception handler needed for PMAX memory probing. Build R3000 and R4x00 DEC configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/prom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/prom/cmdline.c -->
# sources/distributed-fs/ceph-client/arch/mips/dec/prom/cmdline.c

Purpose: imports the DEC PROM command line into `arcs_cmdline`.

Important API: `prom_init_cmdline(s32 argc, s32 *argv, u32 magic)` chooses the first argument index based on PROM type: non-REX starts at argument 1, REX starts at argument 2.

Control flow and state: appends each argument separated by spaces using `strcat()`. The resulting command line persists globally for normal boot parsing.

Dependencies and risks: depends on PROM argument pointer validity and `prom_is_rex()`. There is no explicit bounds checking here, so very long PROM argument strings would risk overflowing `arcs_cmdline` if not constrained elsewhere.

Test signals: boot with PROM arguments on REX and non-REX systems and verify `/proc/cmdline`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/prom/cmdline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/prom/console.c -->
# sources/distributed-fs/ceph-client/arch/mips/dec/prom/console.c

Purpose: provides an early boot console backed by DEC PROM `prom_printf`.

Important APIs: `register_prom_console()` registers a boot console named `"prom"`. `prom_console_write()` chunks output into an 80-character buffer, null terminates it, and prints with `prom_printf("%s", buf)`.

State and integration: console registration persists until normal consoles take over. It depends on PROM vector initialization having set `__prom_printf`.

Risks and test signals: PROM output routines may be slow or unavailable after firmware teardown, so this is init-only. Early boot messages should appear before the normal console is registered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/prom/console.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/prom/dectypes.h -->
# sources/distributed-fs/ceph-client/arch/mips/dec/prom/dectypes.h

Purpose: defines DEC PROM system-type numeric constants used during machine identification.

Important definitions: constants map DEC system IDs such as `DS2100_3100`, `DS5000_200`, `DS5000_1XX`, `DS5000_2X0`, `DS5800`, `DS5400`, `DS5000_XX`, `DS5500`, and `DS5100`.

Integration: consumed by `identify.c` to translate PROM `systype` values into Linux `mips_machtype` and model-specific initialization.

Risks and test signals: incorrect numeric mapping misidentifies the entire platform. Test by booting or emulating known PROM IDs and checking reported system type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/prom/dectypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/prom/identify.c -->
# sources/distributed-fs/ceph-client/arch/mips/dec/prom/identify.c

Purpose: identifies the DECstation model from PROM data and initializes essential per-model physical base addresses before broader platform setup.

Important APIs: `get_system_type()` returns a cached `"Digital ..."` string; `prom_identify_arch(u32 magic)` reads PROM `systype` or REX `sysid`, decodes fields, selects `mips_machtype`, and calls inline initializers. It exports `dec_rtc_base`.

Control flow: model-specific helpers set `dec_kn_slot_base`, `dec_kn_slot_size`, `dec_tc_bus`, `ioasic_base`, and `dec_rtc_base` for KN01, KN230, KN02, KN02XA, and KN03 families. DS5000/2x0 may be refined to DS5900 by inspecting IOASIC status.

State and integration: the selected machine type and base pointers are global platform state used by setup, RTC, TurboChannel, IRQ, and bus-error code.

Risks and test signals: bad PROM sysid or wrong IOASIC probe results cascade into wrong interrupt maps and resources. Boot logs should print the expected DEC model, and RTC/IOASIC/TurboChannel resources should match hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/prom/identify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/prom/init.c -->
# sources/distributed-fs/ceph-client/arch/mips/dec/prom/init.c

Purpose: initializes DEC PROM callback vectors and performs earliest platform discovery.

Important APIs and state: global function pointers include REX callbacks (`__rex_bootinit`, `__rex_getbitmap`, `__rex_getsysid`, etc.), generic PROM callbacks (`__prom_getchar`, `__prom_getenv`, `__prom_printf`), and PMAX file callbacks. `prom_init()` is the architecture firmware entry point.

Control flow: `which_prom()` checks the REX magic and either copies callbacks from the PROM vector or installs fixed PMAX PROM addresses. `prom_init()` optionally clears cache through REX, registers the PROM console, validates CPU type against kernel config, initializes memory, identifies architecture, and builds command line.

State and integration: PROM function pointers persist for init-time users. CPU mismatch paths halt through `dec_machine_halt()`.

Risks and test signals: wrong PROM vector interpretation breaks all early services. Test REX and non-REX boot paths, early console output, CPU config mismatch handling, memory map creation, and command-line import.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/prom/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/prom/locore.S -->
# sources/distributed-fs/ceph-client/arch/mips/dec/prom/locore.S

Purpose: provides a tiny early exception handler used while probing PMAX memory.

Important label: `genexcept_early` stores CP0 Status into global `mem_err`, advances EPC by four bytes to skip the faulting instruction, and returns with `rfe`.

Control flow and integration: `memory.c` copies this handler to the exception vector at `CKSEG0 + 0x80` during memory probing, then restores the old handler afterward.

State and risks: modifies `mem_err` as the probe signal. The code is R3000-era exception handling and must remain small enough for the copied vector slot. Test PMAX memory probing and restoration of the original exception vector.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/prom/locore.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/prom/memory.c -->
# sources/distributed-fs/ceph-client/arch/mips/dec/prom/memory.c

Purpose: discovers DECstation physical memory before normal memory management.

Important APIs: `prom_meminit(u32 magic)` selects PMAX probing or REX bitmap parsing. `prom_free_prom_memory()` frees unused low PROM memory after boot while optionally reserving Lance memory on IOASIC systems.

Control flow: non-REX PMAX probing installs `genexcept_early`, reads one byte at 4 MB increments in KSEG1 until an exception sets `mem_err`, restores the old handler, and adds RAM to memblock. REX path asks `rex_getbitmap()` for a bitmap and converts contiguous fully-available page runs into memblock ranges.

State and integration: `mem_err` is volatile probe state. Resulting memblock ranges become the platform RAM map.

Risks and test signals: PMAX probing assumes at least 4 MB and an upper bound below 480 MB. REX conversion ignores partial bitmap bytes. Test memory size reporting on PMAX and REX machines; verify low PROM memory is freed only after it is safe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/prom/memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/reset.c -->
# sources/distributed-fs/ceph-client/arch/mips/dec/reset.c

Purpose: implements DECstation restart, halt, power-off, and halt-button interrupt behavior by returning control to PROM.

Important APIs: `dec_machine_restart()`, `dec_machine_halt()`, and `dec_machine_power_off()` all call `back_to_prom()`, which jumps to ROM address `0x1fc00000` via KSEG1. `dec_intr_halt()` is an IRQ handler that halts the machine.

State and integration: reboot hooks are installed from `dec/setup.c`, and the halt interrupt may be requested if the machine exposes one.

Risks and test signals: DECstations lack software power-off, so power-off is equivalent to PROM return. Test halt button IRQ routing and reboot/halt paths on supported machines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/setup.c -->
# sources/distributed-fs/ceph-client/arch/mips/dec/setup.c

Purpose: central DECstation platform setup, especially interrupt routing, bus-error hook selection, write-buffer flushing, reboot hooks, and resource reservation.

Important APIs and state: exports `dec_kn_slot_base`, `dec_kn_slot_size`, `ioasic_ssr_lock`, `ioasic_base`, and `dec_interrupt[]`. Global priority tables `cpu_mask_nr_tbl` and `asic_mask_nr_tbl` are consumed by `int-handler.S`. `arch_init_irq()` selects per-model initialization and registers FPU, cascade, bus-error, and halt interrupts. `dec_irq_dispatch()` forwards selected IRQs to `do_IRQ()`.

Control flow: `plat_mem_setup()` installs bus-error init callback, write-buffer flush routine, reboot/power hooks, and reserves firmware working memory. Model-specific `dec_init_*()` functions copy IRQ route arrays and CPU/ASIC priority tables, then initialize CPU IRQs plus KN02 CSR or IOASIC IRQ chips as needed. `arch_init_irq()` selects the model path based on `mips_machtype`, adjusts FPU/halt routing for CPU features, and requests special interrupt lines.

State and persistence: route tables and `dec_interrupt[]` persist for all drivers. `busirq_handler` and flags are selected by `dec_be_init()`. Memblock reserves PROM working memory until later release.

Dependencies and integration: depends on PROM identification, DEC register headers, MIPS CPU IRQ core, IOASIC/KN02 IRQ chips, bus-error handlers, DS1287 time code, TurboChannel, and generic interrupt descriptors.

Risks and test signals: interrupt priority tables must align with assembly dispatcher expectations. Machine-type mistakes produce wrong IRQ maps. Test each supported DEC model class, verify `/proc/interrupts`, FPU exception/interrupt behavior, halt button, bus-error IRQ, and cascade routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/tc.c -->
# sources/distributed-fs/ceph-client/arch/mips/dec/tc.c

Purpose: provides DECstation TurboChannel bus callbacks.

Important APIs: `tc_preadb()` performs protected byte reads with `get_dbe()`; `tc_bus_get_info()` fills `struct tc_bus` from REX TC info and slot address; `tc_device_get_irq()` maps TC slot numbers to `dec_interrupt[]` entries.

Control flow and state: bus info is available only if `dec_tc_bus` was set by PROM identification. Slot count and extended slot geometry depend on `mips_machtype`. IRQ assignment switches on slot number, with DS5000/200 onboard slot quirks for slots 5 and 6.

Dependencies and integration: depends on REX PROM callbacks, DEC machine type, protected access helpers, and global IRQ mapping from setup.

Risks and test signals: protected reads must correctly survive empty slots. Test TC bus enumeration, option ROM reads, and IRQ assignment for TC slots on 3max/3min/maxine/3max+ systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/tc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/time.c -->
# sources/distributed-fs/ceph-client/arch/mips/dec/time.c

Purpose: handles DECstation persistent RTC time, RTC updates, and platform timer initialization.

Important APIs: `read_persistent_clock64()` reads DS1287/CMOS time plus DEC real-year storage. `update_persistent_clock64()` updates minutes/seconds safely using RTC set/divider-reset sequencing. `plat_time_init()` configures DS1287 periodic interrupts, optional IOASIC clocksource, CP0 Count calibration, and DS1287 clockevent.

Control flow: persistent read loops until seconds are stable, converts BCD if needed, and reconstructs year from `RTC_DEC_YEAR`. Timer init measures CP0 Count over DS1287 ticks when available; on R4k DECstations with count errata, it may use CP0 Count only as clocksource and clears `mips_hpt_frequency` if no IOASIC clock exists.

State and integration: updates global `mips_hpt_frequency`, RTC registers, DS1287 clockevent on `dec_interrupt[DEC_IRQ_RTC]`, and optional IOASIC clocksource state.

Risks and test signals: RTC year storage and half-hour correction logic are platform-specific. Timer errata handling affects scheduling precision. Test persistent clock read/write, RTC interrupt delivery, stable timekeeping, and systems with and without IOASIC clocksource.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/wbflush.c -->
# sources/distributed-fs/ceph-client/arch/mips/dec/wbflush.c

Purpose: selects and exports the correct DECstation write-buffer flush routine.

Important APIs: `wbflush_setup()` sets global function pointer `__wbflush`; exported `__wbflush` is used by generic MIPS barrier code. Private routines handle KN01/KN02 CP0 writeback buffer, DS5100 CP3 writeback buffer, or standard uncached-read flush through `__fast_iob()`.

Control flow and state: machine type selects a function pointer at init. KN210 temporarily enables CP3 in CP0 Status, waits on `bc3f`, then restores status.

Dependencies and integration: depends on `mips_machtype`, `CONFIG_CPU_HAS_WB`, and MIPS barrier semantics.

Risks and test signals: wrong flush routine can break MMIO ordering and data coherency. Test device I/O under load on each machine family, especially DS5100 and R2020/R3220 write-buffer systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/dec/wbflush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/econet/Kconfig -->
# sources/distributed-fs/ceph-client/arch/mips/econet/Kconfig

Purpose: defines EcoNet MIPS SoC and devicetree configuration choices.

Important symbols: under `if ECONET`, `SOC_ECONET_EN751221` selects common clock, EcoNet interrupt controller, PCI support, generic PCI drivers, MIPS CPU IRQs, SMP, SMP_UP, and SMP support. `DTB_ECONET_NONE` leaves no built-in DTB; `DTB_ECONET_SMARTFIBER_XP8421_B` depends on the EN751221 family and selects `BUILTIN_DTB`.

Control flow and integration: Kconfig choices drive which platform features and built-in DTB are compiled. The help text documents EN7512/RN7513/EN7521/EN7526 family assumptions and SmartFiber XP8421-B boot packaging.

Risks and test signals: selecting SMP/SMP_UP for single-core 34Kc systems is intentional but easy to misread. Kconfig tests should verify dependencies select required IRQ/clock/PCI support and built-in DTB inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/econet/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/econet/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/econet/Makefile

Purpose: builds EcoNet platform initialization.

Important behavior: unconditionally includes `init.o` for the EcoNet platform directory.

Dependencies and integration: tied to the top-level architecture platform selection; all runtime behavior lives in `init.c`.

Risks and test signals: minimal build risk. EcoNet platform builds should link `prom_init`, `plat_mem_setup`, IRQ, DT, and timer hooks from `init.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/econet/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/econet/init.c -->
# sources/distributed-fs/ceph-client/arch/mips/econet/init.c

Purpose: provides minimal EcoNet EN75xx platform bring-up: early UART, reset hook, device-tree memory discovery, IRQ chip initialization, SMP_UP registration, and timer setup.

Important APIs: `prom_init()` configures early 8250 printk at `0x1fbf0003` with register shift 2 and installs `_machine_restart`. `plat_mem_setup()` sets I/O port base, obtains the FDT via `get_fdt()`, calls `__dt_setup_arch()`, and scans memory. `device_tree_init()` unflattens the DT and registers UP SMP ops. `arch_init_irq()` calls `irqchip_init()`. `plat_time_init()` initializes OF clocks and probes timers. `get_system_type()` returns `"EcoNet-EN75xx"`.

State and integration: runtime state comes from the device tree and generic IRQ/timer/clock subsystems. Hardware reset writes bit 31 to AHB reset control at `0x1fb00040`.

Risks and test signals: boot requires a valid appended or supplied DTB; missing DTB panics. UART base uses byte offset `...0003`, so register mapping must match SoC endianness/stride. Test early console, DT memory map, IRQ controller probe, timer probe, and restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/econet/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/fw/arc/Makefile

Purpose: selects ARC PROM monitor library routines for MIPS firmware support.

Important build behavior: with `CONFIG_ARC_CMDLINE_ONLY`, only `cmdline.o` is built. Otherwise the core library includes command line, environment, file, identify, init, and misc helpers. Optional objects are selected by `CONFIG_ARC_MEMORY`, `CONFIG_ARC_CONSOLE`, and `CONFIG_ARC_PROMLIB`.

Dependencies and integration: this Makefile supports platforms using ARC firmware services for early command line, memory discovery, console, file access, and PROM library calls.

Risks and test signals: selecting command-line-only mode intentionally omits memory and console helpers, so platform code must not call them. Build test ARC configurations with each optional feature combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/Makefile -->
