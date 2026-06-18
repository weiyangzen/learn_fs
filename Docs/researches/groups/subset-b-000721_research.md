# Research: subset-b-000721

Grouped research for the MIPS architecture Kconfig/Makefile and Alchemy board/common support files. Each section is wrapped for reconciliation into its mapped per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/Kconfig -->
# sources/distributed-fs/ceph-client/arch/mips/Kconfig

## Purpose
`arch/mips/Kconfig` is the root configuration contract for the Linux MIPS port in this source tree. It declares the architecture-wide `MIPS` symbol, selects generic kernel capabilities, exposes the machine and CPU selection menus, wires platform sub-Kconfig files, and defines the ABI, memory, timer, bus, power-management, device-tree, and virtualization options that control the rest of the MIPS build.

## Important APIs, Types, And Symbols
The file is declarative Kconfig, so its main "APIs" are configuration symbols consumed by Makefiles and C preprocessor checks. The root `config MIPS` selects core facilities such as cache alias handling, DMA ops, generic VDSO, tracing, perf, KASAN/KCSAN-adjacent hooks, module ELF relocation styles, queued locks, RTC support, and MIPS-specific syscall/compat support. Machine selectors include `MIPS_GENERIC_KERNEL`, `MIPS_ALCHEMY`, `ATH25`, `ATH79`, `BMIPS_GENERIC`, Broadcom, DECstation, Ingenic, Lantiq, Loongson, Malta, Mobileye EyeQ, Nintendo64, Ralink, Realtek, SGI, Sibyte, SNI, TX49xx, Mikrotik, and Octeon families. The Alchemy option selects `PHYS_ADDR_T_64BIT`, R4K clockevent/clocksource support, MIPS CPU IRQs, noncoherent DMA, GPIO, zboot support, and common clk.

Later menus expose support flags such as `DMA_NONCOHERENT`, `SYS_SUPPORTS_RELOCATABLE`, `CPU_BIG_ENDIAN`, `CPU_LITTLE_ENDIAN`, `MIPS_L1_CACHE_SHIFT`, firmware symbols, CPU-family symbols, `32BIT`/`64BIT`, highmem, NUMA, relocatable/kASLR, SMP, timer `HZ`, crash/kexec, appended DTB, command-line source, bus support, compat ABIs, hibernation/suspend, cpufreq/cpuidle, KVM, and vDSO. `source "arch/mips/alchemy/Kconfig"` and sibling `source` lines import platform-specific machine choices after the machine family choice.

## Control Flow
Kconfig evaluates this file top-down while resolving user choices and `select` dependencies. First, `MIPS` auto-enables architecture capabilities. The "Machine selection" choice selects exactly one primary system type, each of which selects CPU availability, firmware models, I/O and IRQ helpers, endian support, PCI style, boot format, and feature constraints. After that choice, platform-specific Kconfig fragments refine board-level choices. The CPU menu then offers only CPU families exposed by the selected machine symbols, and the kernel-type/menu options are constrained by the selected CPU and machine support flags.

The bottom sections compose derived behavior. For example `DMA_NONCOHERENT` selects DMA mapping hooks, `MIPS_CLOCK_VSYSCALL` follows clocksource choices, `HIGHMEM` depends on 32-bit kernels and known-safe cache/platform support, `RELOCATABLE` depends on supported CPUs and selects relocation metadata, and appended DTB/command-line choices only appear under `USE_OF`.

## State And Persistence
The persistent state is the generated `.config` and derived autoconf headers. This file does not execute runtime code, but its symbols shape compiled code, linker layout, generated boot images, selected platform directories, kernel ABI exposure, and driver availability. Several symbols also encode hardware promises, such as cache behavior, DMA coherency, supported endianness, interrupt controller type, and bootloader interface.

## Dependencies And Integration Points
The primary consumers are `arch/mips/Makefile`, `arch/mips/Kbuild.platforms`, platform Makefiles, assembly/C `#ifdef CONFIG_*` blocks, and generic kernel subsystems gated by architecture support symbols. `MIPS_ALCHEMY` integrates directly with `arch/mips/alchemy/Kconfig` and the Alchemy common files in this work item. `CPU_*`, `SYS_HAS_CPU_*`, and `SYS_SUPPORTS_*` symbols feed compiler flags, memory model decisions, and CPU feature code. `USE_OF`, appended DTB choices, and command-line policies integrate with early boot and device-tree parsing.

## Risks
The file has a high blast radius because `select` can force generic features without dependency prompts. Incorrect machine or CPU support selections can produce kernels that compile but boot with wrong endianness, DMA coherency, interrupt routing, or boot-image format. Adding a platform can accidentally expose incompatible CPU choices, ABI combinations, PCI behavior, or timer frequencies. The machine choice also gates platform Kconfig fragments, so moving `source` lines or dependency expressions can hide board options. Several historical erratum options are declarative and easy to misapply because they encode CPU revision assumptions.

## Test Signals
Useful validation includes `make ARCH=mips olddefconfig` for representative machines, all generic defconfig targets, and Alchemy-specific configurations such as `MIPS_ALCHEMY` plus each board choice. Kconfig warnings about unmet direct dependencies, invalid defaults, or recursive selects are strong failure signals. Build matrix coverage should include 32-bit/64-bit, both endian choices where supported, `USE_OF` appended-DTB variants, `RELOCATABLE`/`RANDOMIZE_BASE`, compat ABIs on 64-bit, and power-management menus. For this subset, verify that `MIPS_ALCHEMY` exposes `arch/mips/alchemy/Kconfig` and selects the common dependencies required by the Alchemy C files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/Makefile

## Purpose
`arch/mips/Makefile` is the architecture build driver for MIPS kernels. It chooses endian- and word-size-specific toolchain prefixes, compiler and assembler flags, linker emulations, boot-image targets, firmware and library directories, platform includes, generated helper tools, generic defconfig generation, install targets, and architecture help text.

## Important APIs, Types, And Variables
Important build variables include `KBUILD_DEFCONFIG`, `KBUILD_DTBS`, `tool-archpref`, `UTS_MACHINE`, `ld-emul`, `vmlinux-32`, `vmlinux-64`, `cflags-y`, `mips-cflags`, `KBUILD_AFLAGS`, `KBUILD_CFLAGS`, `KBUILD_CPPFLAGS`, `KBUILD_LDFLAGS`, `load-y`, `load-ld`, `entry-y`, `bootvars-y`, `libs-y`, `drivers-y`, `boot-y`, `bootz-y`, `generic_defconfigs`, and `BOARDS`. The `archscripts` target builds MIPS helper tools such as `elf-entry`, optional `loongson3-llsc-check`, and relocation tooling. The `gen_generic_defconfigs` and `describe_generic_defconfig` make functions synthesize generic MIPS defconfig targets from bitness, ISA revision, endian fragments, and board fragments.

## Control Flow
Make includes this file from the top-level kernel build. Early logic selects BFD formats, emulations, cross-compiler prefixes, and `UTS_MACHINE` based on `CONFIG_CPU_LITTLE_ENDIAN`, `CONFIG_32BIT`, and `CONFIG_64BIT`. It then appends ABI, no-PIC, soft-float, endian, CPU, erratum, and toolchain feature flags to `cflags-y`. Toolchain feature probes add defines such as `TOOLCHAIN_SUPPORTS_MSA`, `TOOLCHAIN_SUPPORTS_VIRT`, `TOOLCHAIN_SUPPORTS_XPA`, `TOOLCHAIN_SUPPORTS_CRC`, `TOOLCHAIN_SUPPORTS_DSP`, and `TOOLCHAIN_SUPPORTS_GINV`.

Firmware directories and platform-specific variables are added through `include $(srctree)/arch/mips/Kbuild.platforms`. The final compile/link flags are exported into Kbuild variables, boot variables are constructed from load and entry addresses, and boot targets recurse into `arch/mips/boot` or `arch/mips/boot/compressed`. The file also declares conversion rules for `vmlinux.32` and `vmlinux.64`, install rules, syscall header generation, and a dynamic set of generic defconfig targets.

## State And Persistence
The Makefile itself does not persist runtime state, but it determines generated artifacts: `vmlinux`, format-converted `vmlinux.32`/`vmlinux.64`, zboot images, U-Boot images, S-record/ECOFF/raw images, DTBs, generated arch tools, installed kernel/config/System.map files, and generated generic defconfig outputs. It also persists architecture assumptions into object code through compiler flags and preprocessor definitions.

## Dependencies And Integration Points
It depends on Kconfig symbols from `arch/mips/Kconfig`, `arch/mips/Kbuild.platforms` for platform-specific directories/load addresses, `arch/mips/tools`, `arch/mips/boot`, firmware directories, MIPS libraries, optional math emulation, PCI, crypto, and power directories. It integrates with top-level Kbuild variables, compiler feature probes, linker emulation names, objcopy, defconfig fragments under `arch/mips/configs/generic`, and install path conventions.

## Risks
Build flag changes can silently alter ABI, relocation behavior, exception table labels, or CPU erratum handling. The file deliberately disables PIC, abicalls, stack checking, asynchronous unwind tables, and assembler Loongson3 LLSC fixes for kernel correctness; removing these can cause subtle runtime failures. Load-address normalization differs for 32-bit and 64-bit links, and wrong `load-y` or `load-ld` values can create unbootable images. Generic defconfig synthesis depends on fragment naming conventions and `BOARDS` expansion. Platform includes can change boot targets and load addresses outside this file, so build regressions may appear platform-specific.

## Test Signals
Run representative `make ARCH=mips ..._defconfig` targets, including generated generic targets and legacy/platform defconfigs. Compile with GCC and Clang where supported, with 32-bit and 64-bit, big- and little-endian, microMIPS, MSA, XPA, relocatable, zboot, and Loongson workaround configurations. Validate that `archscripts` tools build before the kernel, `entry-y` is computed, boot images recurse with expected `bootvars-y`, and `make ARCH=mips help` lists generated generic and legacy defconfigs. For Alchemy, verify `Kbuild.platforms` selects the Alchemy platform Makefile and that `MIPS_FIXUP_BIGPHYS_ADDR` influences `setup.c` when PCI is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/Kconfig -->
# sources/distributed-fs/ceph-client/arch/mips/alchemy/Kconfig

## Purpose
`arch/mips/alchemy/Kconfig` provides the board-level machine choice for AMD/Alchemy Au1xxx systems after the top-level `MIPS_ALCHEMY` machine family is selected. It distinguishes MTX-1, DB/PB development boards, MyCable XXS1500, and Trapeze ITS GPR boards.

## Important APIs, Types, And Symbols
The file defines a `choice` prompt "Machine type" that depends on `MIPS_ALCHEMY` and defaults to `MIPS_DB1XXX`. `MIPS_MTX1`, `MIPS_DB1XXX`, `MIPS_XXS1500`, and `MIPS_GPR` are mutually exclusive board symbols. The selected board symbols choose capabilities such as `HAVE_PCI`, `HAVE_PATA_PLATFORM`, `GPIOLIB`, `SYS_SUPPORTS_LITTLE_ENDIAN`, and `SYS_HAS_EARLY_PRINTK`.

## Control Flow
Kconfig exposes this choice only when the top-level machine selection chose Alchemy. The selected board symbol controls which board object is compiled by `arch/mips/alchemy/Makefile` and which early board setup code supplies `board_setup()`, `get_system_type()`, reset/power hooks, and platform devices. The DB/PB option delegates board detection to other Alchemy development-board code outside this work item.

## State And Persistence
The persistent output is the chosen board symbol in `.config`. There is no runtime state in this file, but the board choice determines the platform device population, PCI availability, early printk availability, and expected endianness of the built kernel.

## Dependencies And Integration Points
This file is sourced by `arch/mips/Kconfig` inside the machine selection menu. Its symbols are consumed by `arch/mips/alchemy/Makefile`, board C files, and platform-specific build logic. The common Alchemy code depends on `MIPS_ALCHEMY` from the parent Kconfig for core CPU/clock/IRQ/DMA setup, while this file selects the board-specific object.

## Risks
Because the board options are mutually exclusive, building a kernel for the wrong board can register wrong flash maps, GPIO devices, reset behavior, PCI IRQ routing, or PCMCIA windows. `SYS_SUPPORTS_LITTLE_ENDIAN` limits exposed endian choices, so any board that actually needs big-endian support would require explicit Kconfig adjustment. Capability selections such as `HAVE_PCI` must match board wiring, or common PCI code may probe invalid hardware.

## Test Signals
Run `olddefconfig` with `MIPS_ALCHEMY=y` and each board option to ensure exactly one board symbol is selected. Build each board and confirm the matching object appears in `arch/mips/alchemy/Makefile` output. Runtime smoke tests should show the board-specific `get_system_type()` string and early printk path on UART0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/alchemy/Makefile

## Purpose
`arch/mips/alchemy/Makefile` maps Alchemy board Kconfig symbols to their board-specific support objects. It is the small board layer companion to the larger common Alchemy Makefile.

## Important APIs, Types, And Variables
The build rules are `obj-$(CONFIG_MIPS_GPR) += board-gpr.o`, `obj-$(CONFIG_MIPS_MTX1) += board-mtx1.o`, and `obj-$(CONFIG_MIPS_XXS1500) += board-xxs1500.o`. The DB/PB development-board path is handled elsewhere under the Alchemy tree, not by this file.

## Control Flow
During Kbuild object collection, the selected board symbol expands the matching `obj-y` entry. The compiled object supplies board-level symbols such as `board_setup()`, `get_system_type()`, and `prom_putchar()` that common Alchemy and MIPS boot code expects.

## State And Persistence
There is no runtime state. The persistent effect is which object is linked into the kernel image for the configured Alchemy board.

## Dependencies And Integration Points
It depends on `arch/mips/alchemy/Kconfig` board symbols and the surrounding `arch/mips/Kbuild.platforms`/platform Makefile inclusion. The object chosen here integrates with `setup.c` through `board_setup()` and with early console support through `prom_putchar()`.

## Risks
The Makefile must remain synchronized with Kconfig symbols. A missing mapping produces link failures for required board hooks or a kernel with no board-specific platform devices. Adding a new board in Kconfig without a matching object here would be incomplete unless another platform Makefile handles it.

## Test Signals
Build each of `CONFIG_MIPS_GPR`, `CONFIG_MIPS_MTX1`, and `CONFIG_MIPS_XXS1500` and inspect built objects or link map for the corresponding `board-*.o`. Kbuild should not attempt to link more than one mutually exclusive board object for a normal Alchemy configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/board-gpr.c -->
# sources/distributed-fs/ceph-client/arch/mips/alchemy/board-gpr.c

## Purpose
`board-gpr.c` contains board support for the Trapeze ITS GPR Au1550 platform. It provides the system-type string, early UART output, board setup, watchdog-based reset/power hooks, static flash layout, GPIO LED devices, bit-banged I2C with an LM83 sensor, and Alchemy PCI host platform data.

## Important APIs, Types, And Functions
`get_system_type()` returns `"GPR"`. `prom_putchar()` writes through `alchemy_uart_putchar()` on UART0. `board_setup()` installs `pm_power_off`, `_machine_halt`, and `_machine_restart`, enables UART1/UART3, and releases the UMTS-card reset GPIO. `gpr_reset()` drives LEDs orange, toggles GPIO1 to trigger an ADM6320 watchdog reset, disables local IRQs, and waits. `gpr_power_off()` waits forever.

Static data includes `gpr_wdt_device`, `gpr_mtd_partitions`, `gpr_flash_data`, `gpr_mtd_device`, `gpr_gpio_leds`, `gpr_led_devices`, `gpr_i2c_gpiod_table`, `gpr_i2c_data`, `gpr_i2c_device`, `gpr_i2c_info`, `alchemy_pci_host_res`, `gpr_pci_pd`, `gpr_pci_host_dev`, and `gpr_devices`. `gpr_map_pci_irq()` maps slot 0 INTA/INTB to Au1550 PCI IRQs. `gpr_pci_init()` is an `arch_initcall`, and `gpr_dev_init()` is a `device_initcall`.

## Control Flow
Early platform setup calls `board_setup()`, which configures restart/power hooks and minimal UART/UMTS GPIO state. Later, `gpr_pci_init()` registers the `"alchemy-pci"` host before MIPS PCI bus scanning, and `gpr_dev_init()` registers the GPIO descriptor lookup table, I2C board info, watchdog, physmap flash, I2C-GPIO adapter, and LEDs.

Reset control enters `gpr_reset()`: GPIOs 4 and 5 assert both active-low LED colors, local interrupts are disabled, GPIO1 is pulsed to reset the external watchdog circuit, and the CPU waits for the board reset. Normal power off has no board power controller and simply idles indefinitely.

## State And Persistence
The file persists hardware state through GPIO direction/value changes, UART enable registers, and PCI configuration bits. It registers platform devices that persist for driver binding. Flash partitions are fixed board policy and include read-only rootfs/yamon regions through `mask_flags`. The I2C GPIO lookup table persists in gpiolib so the `i2c-gpio` platform device can resolve SCL/SDA offsets on `"alchemy-gpio2"`.

## Dependencies And Integration Points
It depends on Alchemy GPIO/UART helpers, MIPS reboot hooks, platform device core, physmap MTD, GPIO LEDs, I2C-GPIO, gpiod lookup tables, PCI platform data, and Au1550 PCI IRQ definitions. It integrates with `setup.c` through `board_setup()`, with early printk through `prom_putchar()`, with `arch/mips/alchemy/Makefile` via `CONFIG_MIPS_GPR`, and with PCI scanning through the arch initcall ordering.

## Risks
GPIO numbers and active-low semantics are board-specific; wrong values can hold the UMTS card in reset, fail to trigger the watchdog, or invert LEDs. The watchdog reset path assumes the external ADM6320 circuit is wired to GPIO1 and resets after about 200 ms. Flash partition offsets overlap intentionally for aggregate views (`kernel+rootfs`) but can be dangerous if exposed writable. `gpr_map_pci_irq()` returns `0xff` for unsupported pins, so PCI devices outside the expected slot/pin wiring may fail. Endian-specific PCI config flags must match the CPU endian build.

## Test Signals
Build `CONFIG_MIPS_GPR=y` and confirm `board-gpr.o` links. Boot logs should include `"Trapeze ITS GPR board"` and `get_system_type()` should report `GPR`. Device enumeration should show `adm6320-wdt`, `physmap-flash` with six partitions, `leds-gpio`, `i2c-gpio`, and LM83 board info. PCI probe should see the Alchemy PCI host before bus scanning. Hardware tests should verify watchdog reset, UART1/UART3 enablement, UMTS reset release, LED polarity, I2C sensor probing, and PCI INT routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/board-gpr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/board-mtx1.c -->
# sources/distributed-fs/ceph-client/arch/mips/alchemy/board-mtx1.c

## Purpose
`board-mtx1.c` implements board support for the 4G Systems MTX-1 Au1500 platform. It sets board identity, early UART output, reset/power hooks, GPIO and pinmux defaults, flash partitions, PCI/CardBus helper behavior, GPIO LEDs, watchdog, button input, and Ethernet platform-data overrides.

## Important APIs, Types, And Functions
`get_system_type()` returns `"MTX-1"`, and `prom_putchar()` writes to UART0. `board_setup()` configures USB power if OHCI is enabled, sets `SYS_PINFUNC`, drives board GPIO defaults, sets LED state, and installs reboot/power hooks. `mtx1_reset()` jumps to reset vector `0xbfc00000`; `mtx1_power_off()` waits forever.

Device setup uses software nodes and property entries: `mtx1_gpiochip_node`, `mtx1_gpio_keys_node`, `mtx1_button_node`, `mtx1_gpio_leds_node`, `mtx1_green_led_node`, `mtx1_red_led_node`, and watchdog GPIO properties. Initializer helpers `mtx1_keys_init()`, `mtx1_wdt_init()`, and `mtx1_leds_init()` create `gpio-keys`, `mtx1-wdt`, and `leds-gpio` platform devices. `mtx1_mtd` exposes physmap flash partitions. PCI support uses `mtx1_pci_idsel()`, `mtx1_irqtab`, `mtx1_map_pci_irq()`, `mtx1_pci_pd`, and `mtx1_pci_host`. `mtx1_register_devices()` is an `arch_initcall`.

## Control Flow
`board_setup()` runs during early memory/platform setup and establishes power/reset behavior plus pin states. At arch initcall time, `mtx1_register_devices()` sets IRQ trigger types for GPIO/PCI-related lines, overrides MAC0 Ethernet platform data with `phy_search_highest_addr` and `phy1_search_mac0`, registers the `"alchemy-gpio2"` software node, registers PCI and MTD devices, then creates LED, watchdog, and key devices.

During PCI configuration, `mtx1_pci_idsel()` toggles GPIO1/EXT_IO3 to suppress IDSEL signals for a proprietary CardBus adapter except for device select 0, and `mtx1_map_pci_irq()` indexes a fixed slot/pin table. The reset path simply jumps to firmware reset, while power off is an infinite MIPS `wait` loop.

## State And Persistence
The file mutates pinmux, GPIO direction/value, board LEDs, USB power switch state, reboot hooks, platform-device registrations, software-node registrations, and MAC0 platform data before generic Alchemy Ethernet registration. Flash partition layout is fixed and includes read-only bootloader protection. IRQ trigger configuration persists in the interrupt controller for the lifetime of the boot unless changed later.

## Dependencies And Integration Points
It depends on Alchemy GPIO, `alchemy_wrsys()`, IRQ type APIs, platform device core, software node/property APIs, GPIO LEDs, GPIO keys, MTD physmap, Alchemy PCI platform data, and Au1000 Ethernet platform data. It integrates with `au1xxx_override_eth_cfg()` in `platform.c`, with `setup.c` via `board_setup()`, with early console via `prom_putchar()`, and with Kconfig/Makefile via `CONFIG_MIPS_MTX1`.

## Risks
`mtx1_map_pci_irq()` indexes `mtx1_irqtab[slot][pin]` without local bounds checks, relying on PCI core inputs matching expected IDSEL/pin ranges. GPIO setup is order-sensitive for PCI/CardBus, USB power, LED state, and PHY TX_ER. Software-node registration errors are logged but not always fatal, so missing LEDs/keys/watchdog may not stop boot. The reset-vector jump assumes boot flash/fardware is mapped at `0xbfc00000`. The watchdog error log says "gpio-keys" on watchdog registration failure, which can mislead diagnostics.

## Test Signals
Build and boot `CONFIG_MIPS_MTX1=y`; logs should include `"4G Systems MTX-1 Board"`. Confirm GPIO2 software node, `gpio-keys`, `leds-gpio`, `mtx1-wdt`, physmap flash, and Alchemy PCI host devices are registered. Check `au1000-eth` MAC0 probes with the overridden PHY search policy. Hardware tests should cover USB power switch, LED polarity, system button input, watchdog GPIO, flash partition protection, PCI/CardBus enumeration, and reset-vector reboot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/board-mtx1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/board-xxs1500.c -->
# sources/distributed-fs/ceph-client/arch/mips/alchemy/board-xxs1500.c

## Purpose
`board-xxs1500.c` provides board support for the MyCable XXS1500 Au1500 platform. It supplies board identity, early UART output, reset/power hooks, GPIO/pinmux setup for UART3 and USB power, PCMCIA resource registration, and fixed IRQ trigger setup for board GPIO lines.

## Important APIs, Types, And Functions
`get_system_type()` returns `"XXS1500"`. `prom_putchar()` writes to UART0. `board_setup()` installs `_machine_restart`, `_machine_halt`, and `pm_power_off`, enables GPIO input/GPIO2 support, selects UART3 pin function, enables UART3, and writes UART3 MCR bit 0 to power up USB. `xxs1500_reset()` jumps to `0xbfc00000`; `xxs1500_power_off()` executes an infinite MIPS `wait` loop. `xxs1500_pcmcia_res` and `xxs1500_pcmcia_dev` describe PCMCIA I/O, attribute, and memory windows. `xxs1500_dev_init()` sets IRQ types and registers the PCMCIA platform device.

## Control Flow
Early setup configures reboot/power behavior and essential board pin state. The device initcall later programs IRQ polarity/level for Au1500 GPIO204, GPIO201-205, GPIO207, and GPIO0-5, then adds the `"xxs1500_pcmcia"` platform device. Drivers for the board-specific PCMCIA platform can then bind to the three memory resources.

## State And Persistence
The file persists GPIO controller enablement, UART3 pinmux, UART3 enable state, UART MCR bit for USB power, reboot hooks, IRQ trigger types, and a registered PCMCIA platform device. It does not allocate dynamic state outside platform-device registration.

## Dependencies And Integration Points
It depends on Alchemy GPIO/UART helpers, Au1000/Au1500 PCMCIA physical address macros, MIPS reboot hooks, platform device core, and IRQ type APIs. It integrates with `setup.c` via `board_setup()`, early console through `prom_putchar()`, and `arch/mips/alchemy/Makefile` through `CONFIG_MIPS_XXS1500`.

## Risks
The UART3 MCR write is a board-specific side effect used as a USB power control; serial-driver changes or UART3 remapping can affect power behavior. Reset assumes firmware at `0xbfc00000`. IRQ trigger types are hard-coded and must match board wiring, especially the CF IRQ on GPIO4. PCMCIA windows are fixed-size and assume the platform driver expects these legacy physical ranges.

## Test Signals
Build `CONFIG_MIPS_XXS1500=y` and confirm `board-xxs1500.o` links. Boot should identify `XXS1500`, configure UART3, and register the `xxs1500_pcmcia` platform device. Hardware tests should cover USB power state, UART3 operation, CF/PCMCIA card detect/IRQ behavior, reset-vector reboot, and idle power-off behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/board-xxs1500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/alchemy/common/Makefile

## Purpose
`arch/mips/alchemy/common/Makefile` defines the always-built common support objects for Alchemy Au1xx0/Au1300 SoCs. It collects firmware/PROM, timer, clock, platform-device, power, GPIO, setup, sleep, DMA, descriptor DMA, voltage-scaling, IRQ, and USB control code into the Alchemy platform build.

## Important APIs, Types, And Variables
The only build variable is `obj-y`, which appends `prom.o time.o clock.o platform.o power.o gpiolib.o setup.o sleeper.o dma.o dbdma.o vss.o irq.o usb.o`.

## Control Flow
When the Alchemy platform directory is included by Kbuild, every listed object is linked into the kernel for Alchemy builds. Runtime initialization order is then controlled by each object's initcall level and architecture hook names, not by this Makefile.

## State And Persistence
There is no direct runtime state. The persistent effect is object inclusion: the Alchemy kernel image always contains common PROM parsing, clock registration, platform-device population, sleep support, DMA frameworks, GPIO, IRQ, and USB control support.

## Dependencies And Integration Points
It depends on the Alchemy platform being selected by the surrounding architecture build. The listed objects provide functions consumed across the architecture: `prom_init()`, `plat_mem_setup()`, `arch_init_irq()`, `au_sleep()`, DMA exports, clock framework registration, and platform devices. Board files rely on these common objects for GPIO, UART, PCI, Ethernet, and reboot behavior.

## Risks
Because all objects are unconditional for Alchemy builds, code inside each file must self-filter by CPU type when hardware is not present. Removing an object can cause missing architecture hooks or unresolved exports; adding a heavyweight object unconditionally can affect every Alchemy board. Initcall dependencies are implicit and need to remain compatible with board setup, PCI scanning, and driver probing.

## Test Signals
Build any `MIPS_ALCHEMY` configuration and inspect that all listed common objects compile. Boot smoke tests should show clocks, IRQs, GPIO, UARTs, and board devices initializing in expected order. Linker failures for architecture hooks or exported Alchemy helpers usually point to this Makefile or object-list regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/clock.c -->
# sources/distributed-fs/ceph-client/arch/mips/alchemy/common/clock.c

## Purpose
`clock.c` exposes the Alchemy SoC clock tree to the Linux common clock framework. It models the 12 MHz root crystal, CPU PLL, AUX PLLs, sysbus/peripheral/memory/LR clocks, six frequency generators, and internal clock-source muxes for different Au1xxx/Au1300 CPU variants.

## Important APIs, Types, And Functions
The main init entry is `alchemy_clk_init()` registered with `postcore_initcall()`. `alchemy_set_lpj()` computes `preset_lpj` from the CPU clock for early delay calibration. Clock operation groups include `alchemy_clkops_cpu`, `alchemy_clkops_aux`, `alchemy_clkops_fgenv1`, `alchemy_clkops_fgenv2`, and `alchemy_clkops_csrc`. Private clock types are `struct alchemy_auxpll_clk` and `struct alchemy_fgcs_clk`.

Setup helpers include `alchemy_clk_setup_cpu()`, `alchemy_clk_setup_aux()`, `alchemy_clk_setup_sysbus()`, `alchemy_clk_setup_periph()`, `alchemy_clk_setup_mem()`, `alchemy_clk_setup_lrclk()`, `alchemy_clk_init_fgens()`, and `alchemy_clk_setup_imux()`. Rate helpers include `alchemy_clk_cpu_recalc()`, `alchemy_clk_aux_recalc()`, `alchemy_clk_aux_setr()`, `alchemy_clk_aux_determine_rate()`, `alchemy_calc_div()`, and `alchemy_clk_fgcs_detr()`. Variant-specific internal clock names and aliases map legacy names such as `usbh_clk`, `usbd_clk`, `irda_clk`, and `psc*_intclk`.

## Control Flow
At postcore init, `alchemy_clk_init()` registers the fixed root clock, CPU clock, AUX PLL(s), fixed-factor sysbus/peripheral/memory/LR clocks, then registers six frequency generators and up to six internal clock muxes based on `alchemy_get_cputype()`. Au1300 receives AUXPLL2 and v2 frequency generators with a wider parent mux and flexible divider scale; older variants use v1 generators with CPU/AUXPLL parents and even dividers. Finally, aliases are added for CPU-specific shared clock names.

Clock consumers call common clock APIs. Recalc callbacks read system registers to compute rates. Set-rate and set-parent callbacks update `SYS_AUXPLL`, `SYS_FREQCTRL0/1`, or `SYS_CLKSRC` under spinlocks. Enable/disable callbacks either set explicit enable bits on older hardware or switch muxes to/from disabled states on Au1300 and internal sources.

## State And Persistence
Persistent state is both registered `struct clk` objects and hardware clock register contents. Allocated `clk_hw` wrappers and clkdev aliases remain for the lifetime of the kernel. The file tracks cached parent/enabled state for muxes whose hardware disabled state does not preserve the previous parent. Register writes persist until firmware, suspend/resume, or another clock consumer changes them.

## Dependencies And Integration Points
It depends on common clock framework APIs, clkdev aliases, Alchemy system/memory register helpers, CPU type detection, KSEG1 physical mapping, and clock name macros from Alchemy headers. `setup.c` calls `alchemy_set_lpj()` before normal clock registration is complete. `platform.c` consumes `ALCHEMY_PERIPH_CLK` for UART baud clocking. `power.c` saves/restores the same clock registers across sleep.

## Risks
Clock math and register bitfields are CPU-variant-specific; a wrong CPU type can program invalid mux/divider fields. Some PLL/register behavior is special, such as write-only early Au1000 CPU PLL handling and Au1300 disabled mux encodings. The code uses raw MMIO and spinlocks; missing barriers or lock coverage can corrupt shared clock-control registers. `alchemy_clk_fgcs_detr()` approximates active parent detection with `clk_hw_is_prepared()`, so rate selection can choose suboptimal or unexpectedly mutable parents. Failures during init abort with `-ENODEV`, potentially leaving consumers without required clocks.

## Test Signals
Boot an Alchemy configuration and check `"Alchemy clocktree installed"`. Use clk summary/debugfs, if available, to confirm root, CPU, AUXPLL, sysbus, peripheral, memory, LR, frequency generators, internal clocks, and aliases appear for the selected CPU. Exercise UART probing, USB clocks, PSC clocks, LCD clocks, and PCI clock outputs on relevant variants. Rate-change tests should verify divisor boundaries, AUX PLL min/max multipliers, Au1300 scale-bit behavior, and no register corruption under concurrent clock operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/dbdma.c -->
# sources/distributed-fs/ceph-client/arch/mips/alchemy/common/dbdma.c

## Purpose
`dbdma.c` implements the Descriptor Based DMA manager used by Au1550, Au1200, and Au1300 Alchemy SoCs. It maintains device ID tables, allocates DMA channels, allocates and initializes descriptor rings, queues source/destination buffers or whole descriptors, starts/stops/resets channels, handles DBDMA interrupts, and saves/restores DBDMA controller registers across syscore suspend.

## Important APIs, Types, And Functions
Exported APIs include `au1xxx_ddma_get_nextptr_virt()`, `au1xxx_ddma_add_device()`, `au1xxx_ddma_del_device()`, `au1xxx_dbdma_chan_alloc()`, `au1xxx_dbdma_set_devwidth()`, `au1xxx_dbdma_ring_alloc()`, `au1xxx_dbdma_put_source()`, `au1xxx_dbdma_put_dest()`, `au1xxx_dbdma_get_dest()`, `au1xxx_dbdma_stop()`, `au1xxx_dbdma_start()`, `au1xxx_dbdma_reset()`, `au1xxx_get_dma_residue()`, `au1xxx_dbdma_chan_free()`, `au1xxx_dbdma_dump()`, and `au1xxx_dbdma_put_dscr()`.

Important state includes `dbdma_gptr`, `dbdma_initialized`, `dbdev_tab`, `chan_tab_ptr[]`, `au1xxx_dbdma_spin_lock`, CPU-specific device tables for Au1550/Au1200/Au1300, `DBDEV_TAB_SIZE`, and `alchemy_dbdma_pm_data`. The init path is `alchemy_dbdma_init()` as a `subsys_initcall()`, which calls `dbdma_setup()` for supported CPU types.

## Control Flow
Initialization allocates a 64-entry device table, copies the first 32 built-in device descriptors for the selected CPU, marks the custom half free, disables/configures the DBDMA block, enables interrupts, requests the single DBDMA IRQ, and registers syscore suspend/resume ops. Drivers can add custom device IDs, allocate a channel for source/destination IDs, allocate a descriptor ring, queue buffers by setting descriptor addresses/counts/flags, and start the hardware. Doorbell writes notify the DMA engine after descriptors are made valid.

Interrupt handling reads the global interrupt status, selects the first set channel with `__ffs()`, clears that channel's interrupt, calls the optional channel callback, and advances `cur_ptr`. Stop disables the channel and waits for halt status. Reset rewinds get/put/current pointers and clears descriptor valid/software status bits. Channel free stops hardware, frees the descriptor allocation, clears device in-use bits, drops the channel table entry, and frees the channel metadata.

## State And Persistence
The file persists global device reservations, channel allocations, descriptor rings, hardware channel registers, callback pointers, and custom device table entries. Descriptor memory is allocated from DMA-capable memory and uses physical pointer fields for hardware. On noncoherent parts, buffer and descriptor cache maintenance is explicit before/after queueing. Suspend snapshots global config and each channel's six register words, halts channels, disables interrupts, and restores those registers on resume.

## Dependencies And Integration Points
It depends on Alchemy DBDMA register/header definitions, DMA coherency state from `dma_default_coherent`, cache maintenance helpers, IRQ core, syscore PM, KSEG1 MMIO mapping, and driver clients that use `au1xxx_dbdma_*` APIs. `platform.c` registers Ethernet MAC resources with MACDMA windows, and peripheral drivers use command IDs from the CPU-specific device tables.

## Risks
The channel ID ABI is a casted pointer-to-`chan_tab_ptr` entry stored in a 32-bit `u32`, which assumes 32-bit kernel address semantics. Several exported APIs trust `chanid` and descriptor pointers without validation. Channel allocation releases source/destination flags without a lock on one failure path, and queue functions assume only one producer per channel despite comments about multiple callers. `dbdma_interrupt()` handles only the first pending bit, so simultaneous channel interrupts depend on retriggering. Cache maintenance is manual and easy to get wrong for noncoherent or stale-data erratum parts. Suspend waits indefinitely for halt bits in syscore suspend, unlike `au1xxx_dbdma_stop()` which has a timeout.

## Test Signals
Build Au1550, Au1200, and Au1300 configurations and confirm DBDMA initializes and requests the expected IRQ. Driver-level tests should allocate channels for UART/PSC/SD/AES/MAC/custom devices, allocate rings with aligned descriptors, queue source and destination buffers, verify callbacks and residue, stop/reset/restart channels, and free channels without leaks. Stress tests should cover simultaneous channel interrupts, descriptor-ring-full returns, invalid device IDs, custom add/delete exhaustion, noncoherent cache paths, and suspend/resume while channels are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/dbdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/dma.c -->
# sources/distributed-fs/ceph-client/arch/mips/alchemy/common/dma.c

## Purpose
`dma.c` implements the older fixed-channel Au1000/Au1500/Au1100 DMA channel allocator. It loosely mirrors legacy `request_dma()`/`free_dma()` style APIs, maps device IDs to FIFO addresses and DMA modes, initializes channel IRQ numbers, and exports the channel table for classic Alchemy peripheral drivers.

## Important APIs, Types, And Functions
Exported symbols are `au1000_dma_table`, `request_au1000_dma()`, and `free_au1000_dma()`. `au1000_dma_read_proc()` formats a simple list of allocated channels for legacy proc use. `au1000_dma_init()` is an `arch_initcall()` that fills per-channel IRQ numbers based on CPU type. Static data includes `dma_dev_table` for primary devices, `dma_dev_table_bank2` for Au1100 SD controller devices, `DMA_CHANNEL_LEN`, and `au1000_dma_spin_lock`.

## Control Flow
Clients call `request_au1000_dma()` with a device ID, label, optional IRQ handler, IRQ flags, and IRQ cookie. The function validates the device ID against CPU capabilities, finds the first free `au1000_dma_table` entry, optionally requests the channel IRQ, fills channel MMIO base, device ID, label, FIFO address, mode flags, and initializes the hardware channel through `init_dma()`. `free_au1000_dma()` validates the channel, disables DMA, frees the IRQ if present, and marks the channel free.

At boot, `au1000_dma_init()` checks the CPU type, assigns the correct DMA interrupt base for Au1000/Au1500/Au1100, and logs initialization. Newer DBDMA-capable CPUs fall through without initializing this legacy table.

## State And Persistence
Persistent state is `au1000_dma_table[]`: device ownership, IRQ cookies, channel MMIO pointers, FIFO addresses, modes, labels, and IRQ numbers. Hardware channel registers are initialized/disabled through helper macros outside this file. Optional IRQ registrations persist until `free_au1000_dma()`.

## Dependencies And Integration Points
It depends on `asm/mach-au1x00/au1000_dma.h` for `struct dma_chan` and helper operations, Alchemy CPU type detection, fixed physical addresses for UART/AC97/USB/I2S/SD FIFOs, Linux IRQ APIs, and exported symbols consumed by legacy Alchemy drivers. It coexists with `dbdma.c` for later SoCs.

## Risks
The free-channel scan is not protected by `au1000_dma_spin_lock`, despite a global spinlock existing, so concurrent requests can race. Device IDs are normalized for bank2 before storing, which can obscure original Au1100 bank2 IDs. `request_au1000_dma()` requests the IRQ before fully initializing all channel fields, so handlers must not fire early. Unsupported CPU types silently skip IRQ setup; later requests on unsupported variants should be avoided by driver/platform selection. The legacy proc callback uses old procfs signature and direct `sprintf`.

## Test Signals
Build Au1000, Au1500, and Au1100 configs and confirm `"Alchemy DMA initialized"` appears only for supported fixed-DMA CPUs. Driver tests should request/free each device ID, verify IRQ base assignment, confirm FIFO/mode fields, exercise optional IRQ handlers, and check that all channels return `-ENODEV` when exhausted. Concurrency testing should look for duplicate channel allocation under parallel requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/gpiolib.c -->
# sources/distributed-fs/ceph-client/arch/mips/alchemy/common/gpiolib.c

## Purpose
`gpiolib.c` adapts Alchemy SoC GPIO controllers to the Linux gpiolib API. It registers one or two classic GPIO chips for Au1000/Au1100/Au15x0/Au12x0 variants, or a single GPIC-backed GPIO chip for Au1300.

## Important APIs, Types, And Functions
The classic GPIO callbacks are `gpio1_get()`, `gpio1_set()`, `gpio1_direction_input()`, `gpio1_direction_output()`, `gpio1_to_irq()`, and GPIO2 equivalents. `alchemy_gpio_chip[]` describes `"alchemy-gpio1"` and `"alchemy-gpio2"` with fixed global bases and counts. Au1300 callbacks are `alchemy_gpic_get()`, `alchemy_gpic_set()`, `alchemy_gpic_dir_input()`, `alchemy_gpic_dir_output()`, and `alchemy_gpic_gpio_to_irq()`, wrapped by `au1300_gpiochip` labeled `"alchemy-gpic"`. `alchemy_gpiochip_init()` is an `arch_initcall()`.

## Control Flow
At arch initcall, CPU type detection selects the correct GPIO registration path. Au1000 registers only GPIO1. Au1500 through Au1200 register GPIO1 and GPIO2. Au1300 registers the GPIC-backed GPIO chip. All callbacks translate gpiolib offsets into legacy global GPIO numbers by adding the chip base, then delegate to low-level Alchemy GPIO helpers.

## State And Persistence
The persistent state is the registered `gpio_chip` instances and the underlying hardware direction/value/IRQ mapping configured by low-level helpers. This file itself does not allocate dynamic memory or retain per-line state.

## Dependencies And Integration Points
It depends on `linux/gpio/driver.h`, `gpio-au1000.h`, `gpio-au1300.h`, and `alchemy_get_cputype()`. Board files use global GPIO numbers and, in MTX-1/GPR cases, software nodes or lookup tables that refer to `"alchemy-gpio2"`. IRQ integration relies on `to_irq` mapping to the interrupt setup in `irq.c`.

## Risks
The file uses fixed legacy global GPIO bases, which can conflict with newer dynamic GPIO numbering assumptions. The return value OR-ing when registering both GPIO1 and GPIO2 can lose exact failure causes and may leave one chip registered after the other fails. Board lookup tables depend on chip labels remaining stable. Au1300 shares GPIC GPIO and interrupt/pinmux state, so GPIO direction changes can affect device-function pins.

## Test Signals
Boot each CPU variant and confirm the expected GPIO chip labels and line counts appear. Board device probes should resolve `"alchemy-gpio2"` descriptors for MTX-1 and GPR. GPIO tests should read/write lines, switch direction, and map GPIO-to-IRQ for classic and Au1300 variants. Regression tests should verify Au1000 does not register GPIO2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/gpiolib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/irq.c -->
# sources/distributed-fs/ceph-client/arch/mips/alchemy/common/irq.c

## Purpose
`irq.c` initializes and manages Alchemy interrupt controllers. It supports the classic dual 32-source interrupt controllers used by Au1000 through Au1200 and the Au1300 GPIC, including IRQ type programming, masking/unmasking, wake controls, priority assignment, chained dispatch from MIPS CPU IRQ lines, GPIC pin-function helpers, and syscore suspend/resume state save.

## Important APIs, Types, And Functions
`struct alchemy_irqmap` maps Linux IRQ numbers to trigger type, priority, and Au1300 internal-source metadata. CPU-specific maps cover Au1000, Au1500, Au1100, Au1550, Au1200, and Au1300. Main architecture entry points are `arch_init_irq()` and `plat_irq_dispatch()`. Classic interrupt chip callbacks include `au1x_ic0_unmask()`, `au1x_ic1_unmask()`, `au1x_ic0_mask()`, `au1x_ic1_mask()`, `au1x_ic0_ack()`, `au1x_ic1_ack()`, `au1x_ic0_maskack()`, `au1x_ic1_maskack()`, `au1x_ic1_setwake()`, and `au1x_ic_settype()`.

Au1300 exported helpers include `au1300_pinfunc_to_gpio()`, `au1300_pinfunc_to_dev()`, `au1300_set_irq_priority()`, and `au1300_set_dbdma_gpio()`. GPIC callbacks include `au1300_gpic_mask()`, `au1300_gpic_unmask()`, `au1300_gpic_maskack()`, `au1300_gpic_ack()`, and `au1300_gpic_settype()`. Init helpers are `au1000_init_irq()` and `alchemy_gpic_init_irq()`.

## Control Flow
`arch_init_irq()` selects classic or GPIC initialization based on CPU type. Classic initialization resets both controllers to a safe state, registers syscore PM, initializes MIPS CPU IRQs, sets all 64 possible sources to `IRQ_TYPE_NONE`, applies the CPU-specific map with trigger type and priority assignment, then chains CPU IRQ lines 2-5 to request dispatchers. Each dispatcher reads a request register and forwards the first pending source to `generic_handle_irq()`.

Au1300 initialization disables and acknowledges all four GPIC banks, registers the GPIC syscore PM, initializes all GPIC IRQs to disabled/type none and priority 1, applies known on-chip source types/priorities, switches internal multifunction pins to device function, and chains CPU IRQ lines 2-5 to a priority encoder dispatcher. Runtime `irq_set_type()` calls update hardware trigger bits and handler names. `plat_irq_dispatch()` maps the first pending CPU interrupt bit to `do_IRQ()`.

## State And Persistence
Persistent state includes interrupt-controller configuration registers, masks, wake bits, source assignment, trigger type, priority, GPIC pin configuration, GPIC DMA trigger selection, and chained handler registrations. Syscore suspend snapshots classic IC config/source/assignment/wake/mask state or GPIC masks/DMASEL/pin configs, disables interrupts, and restores state on resume.

## Dependencies And Integration Points
It depends on the MIPS CPU interrupt controller, generic IRQ core, syscore PM, Alchemy register mappings, GPIO Au1300 pin helpers, and CPU type detection. Board files call `irq_set_irq_type()` for board GPIO lines after this file has registered chips. `gpiolib.c` maps GPIO lines to IRQs provided here. `power.c` and `sleeper.S` rely on wake-capable interrupt state around sleep.

## Risks
Dispatcher functions handle only the first set pending bit per chained interrupt; fairness and retriggering depend on controller behavior. `plat_irq_dispatch()` uses `__ffs(r & 0xff)` without an explicit zero check, assuming it is called only with a pending CPU interrupt. Trigger programming changes irq chip/handler while holding IRQ core locks and must stay consistent with hardware bits. Classic `irq_set_wake` only supports IC1 bits 0-7, so callers can receive `-EINVAL`. GPIC pinmux helpers can steal pins from devices or GPIO depending on use. Suspend/resume state arrays are shared for classic and GPIC modes and sized for both; indexing mistakes would be severe.

## Test Signals
Boot every supported Alchemy CPU type and verify `arch_init_irq()` selects the expected map. Use `/proc/interrupts` and IRQ debug data to confirm chip names, trigger handlers, and priorities. Exercise UART, timer, RTC, DMA, USB, MAC, PCI, GPIO edge/level, and Au1300 internal interrupts. Test `irq_set_irq_type()` transitions, wake enable/disable for supported GPIO lines, suspend/resume interrupt restoration, and GPIC multifunction pin switching. Inject spurious chained requests where possible to verify spurious handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/platform.c -->
# sources/distributed-fs/ceph-client/arch/mips/alchemy/common/platform.c

## Purpose
`platform.c` registers generic platform devices for Alchemy SoC peripherals: 8250 UARTs, OHCI/EHCI USB hosts, and Au1000 Ethernet MACs. It also provides board override support for Ethernet platform data and power callbacks for USB controllers.

## Important APIs, Types, And Functions
The main init entry is `au1xxx_platform_init()` as an `arch_initcall()`. UART support uses `alchemy_8250_pm()`, `PORT()`, `au1x00_uart_data`, `au1xx0_uart_device`, and `alchemy_setup_uarts()`. USB support uses `alchemy_ehci_power_on/off()`, `alchemy_ohci_power_on/off()`, `alchemy_ehci_pdata`, `alchemy_ohci_pdata`, `alchemy_ohci_data`, `alchemy_ehci_data`, `_new_usbres()`, and `alchemy_setup_usb()`. Ethernet support uses `MAC_RES()`, `au1xxx_eth0_resources`, `au1xxx_eth1_resources`, `au1xxx_eth*_platform_data`, `au1xxx_eth*_device`, `au1xxx_override_eth_cfg()`, and `alchemy_setup_macs()`.

## Control Flow
At arch initcall, CPU type detection drives UART, MAC, and USB setup. UART setup obtains and enables `ALCHEMY_PERIPH_CLK`, copies the CPU-specific port table into allocated platform data, fills `uartclk`, lets `au_platform_setup()` validate/setup each port, and registers one `serial8250` platform device. USB setup registers OHCI0 for every variant, EHCI0 for Au1200/Au1300, and OHCI1 for Au1300, each with memory/IRQ resources and power callbacks that call `alchemy_usb_control()`.

Ethernet setup first checks how many MACs the CPU exposes. It duplicates resource arrays for MAC0/MAC1, optionally fills MAC addresses from PROM `ethaddr`, registers MAC0, then registers MAC1 only if the CPU has a second MAC and the pin function register indicates MAC1 is enabled. Boards can call `au1xxx_override_eth_cfg()` before this initcall to customize PHY search or MAC data.

## State And Persistence
The file persists platform devices, allocated UART platform-data arrays, allocated USB platform_device/resource objects, duplicated Ethernet resource arrays, Ethernet MAC platform data, and USB power state as controlled by host drivers. `alchemy_8250_pm()` changes UART hardware enable state on serial power transitions.

## Dependencies And Integration Points
It depends on common clock framework, serial 8250 platform support, USB OHCI/EHCI platform drivers, Alchemy USB control helpers, PROM Ethernet address parsing, Alchemy CPU capability helpers (`alchemy_get_uarts()`, `alchemy_get_macs()`), and Ethernet platform data headers. Board files such as MTX-1 call `au1xxx_override_eth_cfg()` before this file registers MACs.

## Risks
Init ordering matters: board overrides must run before MAC registration, and clock registration must happen before UART setup. Some allocation failures only log and continue, potentially leaving partial device registration. UART platform data is dynamically allocated and assigned to a static platform device, so failed `au_platform_setup()` frees data and returns without registering UARTs. MAC1 registration depends on `SYS_PF_NI2` polarity, which must match hardware documentation. USB resources use a fixed 0x100 register size and shared DMA mask assumptions.

## Test Signals
Boot all Alchemy CPU types and confirm the expected count of UARTs, USB hosts, and Ethernet MACs. Serial tests should verify baud timing from `ALCHEMY_PERIPH_CLK` and suspend/resume PM enabling/disabling UART blocks. USB tests should bind OHCI/EHCI platform drivers and verify `alchemy_usb_control()` power callbacks. Ethernet tests should confirm PROM MAC parsing, board override application, MAC1 pinfunc gating, resource windows, IRQs, and DMA masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/power.c -->
# sources/distributed-fs/ceph-client/arch/mips/alchemy/common/power.c

## Purpose
`power.c` implements high-level Alchemy sleep entry support. It saves SoC core clock, pinmux, and static memory-controller registers, calls the CPU-family-specific assembly sleep routine, and restores the saved registers after wake.

## Important APIs, Types, And Functions
The public entry is `au_sleep()`. Private helpers are `save_core_regs()` and `restore_core_regs()`. Persistent save buffers are `sleep_sys_clocks[5]`, `sleep_sys_pinfunc`, and `sleep_static_memctlr[4][3]`. `au_sleep()` dispatches to assembly functions `alchemy_sleep_au1000()`, `alchemy_sleep_au1550()`, or `alchemy_sleep_au1300()` based on `alchemy_get_cputype()`.

## Control Flow
`au_sleep()` first snapshots frequency-control, clock-source, CPU PLL, AUX PLL, pin-function, and static-memory timing/address/config registers. It then calls the variant-specific low-level sleep code from `sleeper.S`, which handles CPU context, memory self-refresh, and wake handoff. After the assembly routine returns on wake, `restore_core_regs()` rewrites clocks, PLLs, pinmux, and static memory-controller configuration, avoiding CPU PLL restore on write-only early Au1000 parts.

## State And Persistence
The saved arrays persist only across one sleep cycle. Hardware state saved/restored includes clock generator registers, clock source muxes, CPU/AUX PLLs, pinmux, and four static memory banks. The function does not handle peripheral driver state; those are expected to be handled by driver PM or other syscore paths.

## Dependencies And Integration Points
It depends on Alchemy register access helpers, CPU type detection, `au1xxx_cpu_has_pll_wo()`, and the assembly routines in `sleeper.S`. IRQ and DBDMA syscore PM in other files save their own controller state around suspend. Board power-off hooks are separate from this sleep entry.

## Risks
Clock and memory-controller restoration order is hardware-sensitive; incorrect ordering can destabilize wake. The code assumes these register reads produce restorable values, except for write-only CPU PLL variants. Newer peripherals or memory-controller registers not listed here may need separate PM support. `au_sleep()` has no default error path for unknown CPU types; it simply saves and restores without entering a sleep routine.

## Test Signals
Suspend/resume tests on Au1000/Au1500/Au1100, Au1550/Au1200, and Au1300 should verify wake returns, clocks are correct, static bus devices still work, GPIO/pinmux state is preserved, and UART/USB/Ethernet recover through their own PM paths. Instrumentation can compare saved/restored register snapshots. Early Au1000 write-only PLL handling should be tested separately if hardware is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/prom.c -->
# sources/distributed-fs/ceph-client/arch/mips/alchemy/common/prom.c

## Purpose
`prom.c` handles early firmware/PROM initialization for Alchemy boards using YAMON- or U-Boot-style arguments. It captures firmware argc/argv/envp pointers, constructs the kernel command line, discovers RAM size, registers memory with memblock, reads firmware environment variables, and parses Ethernet MAC addresses.

## Important APIs, Types, And Functions
Global firmware argument state is `prom_argc`, `prom_argv`, and `prom_envp`. Public functions are `prom_init_cmdline()`, `prom_getenv()`, `prom_init()`, and `prom_get_ethernet_addr()`. Helpers `str2hexnum()` and `str2eaddr()` parse textual MAC bytes. The file uses `fw_arg0`, `fw_arg1`, `fw_arg2`, `arcs_cmdline`, and `memblock_add()`.

## Control Flow
`prom_init()` stores firmware arguments from CPU registers, calls `prom_init_cmdline()` to concatenate argv entries 1..N into `arcs_cmdline`, reads `memsize` from the firmware environment, defaults to 64 MiB if missing or invalid, and registers RAM from physical 0 through `memsize`. `prom_getenv()` detects YAMON name/value-pair environment format versus U-Boot `name=value` format, then scans for the requested key. `prom_get_ethernet_addr()` checks `ethaddr` in the environment first, falls back to `ethaddr=` in the command line, and parses the address.

## State And Persistence
The persistent early-boot state is the command line, memblock memory range, and retained pointers to firmware argument/environment arrays. Parsed Ethernet addresses are copied into caller buffers. The file does not allocate memory or preserve environment variables beyond the original firmware-provided strings.

## Dependencies And Integration Points
It depends on MIPS bootinfo firmware argument registers, `arcs_cmdline`, memblock, kernel string helpers, and Alchemy platform code. `platform.c` calls `prom_get_ethernet_addr()` to seed Ethernet MAC addresses. Board code provides `prom_putchar()` for early output, while this file handles firmware data.

## Risks
Firmware pointers must remain valid during early boot; malformed envp arrays can break scanning. `prom_init_cmdline()` appends argv strings without quoting and truncates only through `strlcat` behavior. `memsize` defaults to 64 MiB, which may underreport or overassume on unusual boards. `str2eaddr()` treats invalid hex characters as zero and does not validate separators or length, so malformed MAC strings can produce plausible but invalid addresses. `prom_get_ethernet_addr()` does not call `is_valid_ether_addr()`, leaving validation to callers.

## Test Signals
Boot with YAMON-style and U-Boot-style environments and verify command-line construction, `memsize` parsing, and fallback to 64 MiB on invalid input. Test `ethaddr` from env and command line using colon and dot separators. Confirm Ethernet platform code rejects invalid MACs if needed. Early boot should show the expected memblock region in boot logs or memory debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/prom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/setup.c -->
# sources/distributed-fs/ceph-client/arch/mips/alchemy/common/setup.c

## Purpose
`setup.c` provides Alchemy platform memory and I/O setup. It calibrates early delay loops, applies CPU erratum-related Config[OD] handling, sets default DMA coherency policy per CPU revision, calls board-specific setup, initializes global I/O resource ranges, and optionally fixes PCI big-physical address remapping.

## Important APIs, Types, And Functions
The architecture hook is `plat_mem_setup()`. `alchemy_dma_coherent()` returns the CPU/revision-specific default coherent DMA policy. Under `CONFIG_MIPS_FIXUP_BIGPHYS_ADDR`, exported `io_remap_pfn_range_pfn()` uses `fixup_bigphys_addr()` to translate 32-bit PCI memory window PFNs to the Au1500 PCI memory physical base.

## Control Flow
`plat_mem_setup()` calls `alchemy_set_lpj()`, sets or clears CP0 Config[OD] based on `au1xxx_cpu_needs_config_od()`, sets `dma_default_coherent` from `alchemy_dma_coherent()`, calls the board's `board_setup()`, and initializes `ioport_resource`/`iomem_resource` plus `set_io_port_base(0)`. The DMA coherency helper returns false for Au1000/Au1500/Au1100, false for Au1200 AB revision, and true for later/default variants.

The optional PCI fixup path leaves 36-bit physical addresses unchanged, maps addresses inside `ALCHEMY_PCI_MEMWIN_START..END` to `AU1500_PCI_MEM_PHYS_ADDR + phys_addr`, and otherwise returns the original address.

## State And Persistence
Persistent state includes CP0 Config[OD], global `dma_default_coherent`, board-level hardware state initialized by `board_setup()`, and global I/O resource ranges. The PCI PFN remap helper affects later mmap/remap behavior for PCI memory windows.

## Dependencies And Integration Points
It depends on CPU type/revision helpers, `alchemy_set_lpj()` from `clock.c`, board-provided `board_setup()`, DMA mapping globals, MIPS resource setup, CP0 register helpers, and PCI window constants. `MIPS_FIXUP_BIGPHYS_ADDR` is selected by top-level Kconfig for Alchemy PCI builds.

## Risks
Wrong DMA coherency policy causes data corruption, especially on Au1200 AB USB and older noncoherent cores. Config[OD] handling is tied to early SoC errata and performance; incorrect setting can either reintroduce errata or reduce bus performance. `board_setup()` runs before many drivers and must not depend on later platform devices. PCI address fixup assumes the configured PCI memory window constants and size are correct; otherwise userspace remaps can target wrong physical memory.

## Test Signals
Boot each CPU family and verify `dma_default_coherent` matches hardware expectations. Use DMA-heavy drivers on coherent and noncoherent variants, especially USB on Au1200 AB. Confirm board setup messages appear and I/O resource ranges match Alchemy constants. For PCI builds, mmap PCI BARs in the Alchemy PCI memory window and verify `io_remap_pfn_range_pfn()` maps to the expected physical base.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/sleeper.S -->
# sources/distributed-fs/ceph-client/arch/mips/alchemy/common/sleeper.S

## Purpose
`sleeper.S` contains the low-level MIPS assembly sleep and wake routines for Alchemy SoCs. It saves CPU register context, flushes caches, programs scratch registers for ROM wake return, places SDRAM/DDR into self-refresh or sleep mode, triggers processor sleep, and restores CPU context at the wake trampoline.

## Important APIs, Types, And Functions
Exported leaf routines are `alchemy_sleep_au1000`, `alchemy_sleep_au1550`, `alchemy_sleep_au1300`, and `alchemy_sleep_wakeup`. Macros `SETUP_SLEEP` and `DO_SLEEP` implement common context-save and sleep-trigger logic. The code references `__flush_cache_all` and calls `au1x00_fixup_config_od` on wake. It uses CP0 registers `STATUS`, `CONTEXT`, `PAGEMASK`, and `CONFIG`, stackframe offsets such as `PT_R*`, and fixed KSEG1 system/memory controller addresses.

## Control Flow
Each sleep routine begins with `SETUP_SLEEP`: reserve stackframe space, save selected GPRs and CP0 registers, flush caches, and write the saved stack pointer plus `alchemy_sleep_wakeup` address into system scratch registers. The CPU-specific body then caches the instructions that must execute while memory is being placed into low-power mode and sequences memory-controller commands. Au1000/Au1100/Au1500 issue precharge, auto-refresh, and sleep commands; Au1550/Au1200 issue precharge/self-refresh, wait for status, then disable SDRAM clocks; Au1300 disables DDR ports/ODT, precharges, auto-refreshes, blocks access, enters self-refresh, waits for status, and disables SDRAM clocks. `DO_SLEEP` writes `SYS_SLPPWR` and `SYS_SLEEP` to enter sleep.

On wake, firmware/ROM returns to `alchemy_sleep_wakeup` using scratch registers. The wake path restores CP0 state, calls `au1x00_fixup_config_od`, restores saved GPRs, and returns to the C caller in `power.c`.

## State And Persistence
The assembly routine persists CPU context on the current kernel stack and temporary wake metadata in system scratch registers. It mutates memory-controller state, SDRAM clocking, CP0 registers, and sleep-control registers. Higher-level `power.c` handles broader SoC register save/restore around this low-level transition.

## Dependencies And Integration Points
It depends on MIPS assembly conventions, stackframe layout from `asm/stackframe.h`, register definitions, cache flush symbol availability, Alchemy ROM wake behavior using `sys_scratch0/1`, and memory-controller register layouts for the three CPU families. `power.c` dispatches to these routines from `au_sleep()`.

## Risks
This code is extremely hardware- and timing-sensitive. Any stackframe layout mismatch, missing saved register, wrong fixed address, or incorrect memory-controller command can hang the system with RAM asleep. The code caches instructions before disabling memory access; changes that enlarge or move the critical region must preserve that behavior. `alchemy_sleep_wakeup` assumes the stack pointer saved in scratch registers is intact and that ROM jumps to the saved RA. CP0 restoration and Config[OD] fixup are required for early errata handling.

## Test Signals
Suspend/resume on each CPU-family path is the primary test: Au1000/Au1100/Au1500, Au1550/Au1200, and Au1300. Validation should include repeated sleep cycles, memory integrity checks after wake, IRQ wake sources, cache coherency checks, static bus device access, and clock restoration. Instrumented builds can confirm scratch registers are programmed and wake returns through `alchemy_sleep_wakeup`; hardware debug is often required for failures because bad sequencing may stop all logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/sleeper.S -->
