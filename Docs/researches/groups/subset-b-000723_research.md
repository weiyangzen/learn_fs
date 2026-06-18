# subset-b-000723 Research

Grouped research report for the requested Ceph client Linux MIPS architecture source subset. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm47xx/leds.c -->
# sources/distributed-fs/ceph-client/arch/mips/bcm47xx/leds.c

Purpose: Broadcom BCM47xx board LED database and registration glue. It maps detected `enum bcm47xx_board` values to `struct gpio_led` arrays for many consumer router models, then exposes them through the kernel `leds-gpio` platform device.

Important APIs and functions: the `BCM47XX_GPIO_LED` and `BCM47XX_GPIO_LED_TRIGGER` macros build consistent LED names, GPIO numbers, active-low polarity, default state, and optional triggers. `bcm47xx_leds_register()` switches on `bcm47xx_board.board`, selects board-specific LED arrays with `bcm47xx_set_pdata()` or `_extra()`, and registers `bcm47xx_gpio_leds` when a matching table exists.

Control flow: initialization is data driven. Each board family contributes static `__initconst` LED tables; the final switch populates `gpio_led_platform_data` and conditionally calls `platform_device_register`. No runtime probing happens beyond consuming the global board detector result.

State and persistence: LED state is transient GPIO output state owned by the LED subsystem after registration. The static board tables are discarded after init; no NVRAM or filesystem persistence is performed.

Dependencies and integration points: depends on `bcm47xx_board` identification, Linux GPIO LED platform data, and board-private setup code calling `bcm47xx_leds_register()` from the BCM47xx bus/device setup path. It integrates with user space through normal LED class devices and trigger names.

Risks and test signals: correctness depends on hard-coded board/GPIO/polarity data. A wrong mapping can invert power LEDs, leave LEDs unavailable, or drive pins used by other hardware. Test signals are boot logs, presence of `/sys/class/leds/bcm47xx:*`, LED trigger behavior, and board-specific manual GPIO validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm47xx/leds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm47xx/prom.c -->
# sources/distributed-fs/ceph-client/arch/mips/bcm47xx/prom.c

Purpose: BCM47xx early PROM and memory setup. It identifies the system type, imports bootloader command-line data, adds RAM regions, and handles high-memory TLB preparation for some BMIPS configurations.

Important APIs and functions: `get_system_type()` returns the selected system string. `bcm47xx_set_system_type()` formats chip IDs into a Broadcom system name. `prom_init_mem()` adds the low memory region, including a fallback for CFE-less boot. `prom_init()` handles CFE presence, boot argument parsing, board detection, and memory setup. `early_tlb_init()` and `bcm47xx_prom_highmem_init()` install fixed TLB mappings for high memory when compiled for BMIPS highmem support.

Control flow: MIPS early boot calls `prom_init`; it records firmware parameters, initializes CFE access when available, discovers the board, appends boot arguments, and calls memory setup. Highmem setup runs later but still during early architecture initialization.

State and persistence: mutates global boot state such as `arcs_cmdline`, board metadata, memblock memory regions, and fixed TLB entries. Nothing persists after reboot.

Dependencies and integration points: relies on CFE conventions, SSB chipcommon UART address constants, MIPS memblock/TLB APIs, BMIPS helpers, and `bcm47xx_board_detect()`. It feeds later platform setup, CPU info, and the physical memory allocator.

Risks and test signals: early-boot failures are severe: wrong memory bounds or TLB mappings can crash before console is stable. Test signals include early console output, `/proc/cmdline`, `/proc/iomem`, detected system type, highmem visibility, and successful boot on both CFE and non-CFE BCM47xx devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm47xx/prom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm47xx/serial.c -->
# sources/distributed-fs/ceph-client/arch/mips/bcm47xx/serial.c

Purpose: registers early 8250 UART platform data for BCM47xx SoCs using either SSB or BCMA bus discovery.

Important APIs and functions: `uart8250_init_ssb()` and `uart8250_init_bcma()` fill a `plat_serial8250_port` array from the chipcommon UART descriptors and register the `serial8250` platform device. `uart8250_init()` dispatches based on `bcm47xx_bus_type` and is wired as a device initcall.

Control flow: after the SoC bus is available, the initcall chooses SSB or BCMA, converts bus-specific UART metadata into standard 8250 fields, terminates the array with an empty entry, and registers the platform device.

State and persistence: creates a platform device and immutable UART resource/clock descriptions for the serial core. There is no persistent state.

Dependencies and integration points: depends on global `bcm47xx_bus`, Linux 8250 platform driver, SSB/BCMA chipcommon UART inventory, and the BCM47xx bus setup path.

Risks and test signals: incorrect clock, memory base, or IRQ values break console/login serial. Test by booting with serial console, checking registered ttyS devices, and confirming both SSB and BCMA boards enumerate the expected UART count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm47xx/serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm47xx/setup.c -->
# sources/distributed-fs/ceph-client/arch/mips/bcm47xx/setup.c

Purpose: BCM47xx platform setup for reboot, halt, bus registration, Ethernet defaults, fixed PHYs, LED/buttons/workarounds, and CPU quirks.

Important APIs and functions: `plat_mem_setup()` installs restart/halt callbacks, initializes CFE, chooses idle behavior, and registers SSB or BCMA buses. `bcm47xx_bus_setup()` performs post-bus board setup including SPROM, Ethernet MAC/MDIO defaults, fixed PHY registration, LED/button registration, workarounds, and optional mtd initialization. `bcm47xx_cpu_fixes()` applies BMIPS quirks, while `bcm47xx_register_bus_complete()` finalizes bus registration late.

Control flow: platform setup runs in layers: memory/reboot setup first, bus probing next, board-specific devices after the bus is available, and late bus completion via initcall. Restart writes watchdog or chipcommon reset registers; halt loops after disabling interrupts.

State and persistence: changes global machine callbacks, bus state, fixed PHY registration, board platform devices, and chip registers. It reads firmware/SPROM data but does not persist changes.

Dependencies and integration points: integrates CFE, SSB/BCMA, BMIPS, fixed PHY, MTD, LED/button/workaround helpers, and MIPS platform hooks.

Risks and test signals: bus-type assumptions and reset register handling are board-sensitive. Test signals are clean reboot/halt, bus enumeration, Ethernet MAC/PHY availability, LED/button devices, MTD registration, and absence of CPU quirk regressions on BMIPS devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm47xx/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm47xx/time.c -->
# sources/distributed-fs/ceph-client/arch/mips/bcm47xx/time.c

Purpose: computes and registers the BCM47xx MIPS CPU clock for timer calibration.

Important APIs and functions: `plat_time_init()` selects clock source data from SSB or BCMA chipcommon, handles board-specific clock overrides such as Huawei E970 and SSB extif, and calls `mips_hpt_frequency = hz / 2` for the CP0 counter.

Control flow: MIPS time initialization asks this platform hook for the CPU frequency after bus detection. The function branches by `bcm47xx_bus_type`, reads the current bus/chipcommon clock, applies known corrections, and publishes the high precision timer frequency.

State and persistence: writes the global `mips_hpt_frequency`; no persistent state.

Dependencies and integration points: depends on BCM47xx board detection, SSB/BCMA clock APIs, and MIPS timekeeping.

Risks and test signals: wrong clock causes scheduler and delay timing drift. Test by comparing kernel-reported BogoMIPS/timer frequency, serial timestamps, network timing, and board-specific boot behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm47xx/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm47xx/workarounds.c -->
# sources/distributed-fs/ceph-client/arch/mips/bcm47xx/workarounds.c

Purpose: applies small BCM47xx board-specific hardware workarounds not represented as normal devices.

Important APIs and functions: `bcm47xx_workarounds_enable_usb_power()` requests a GPIO and drives it high for USB power. `bcm47xx_workarounds()` switches on detected board IDs and enables USB power GPIOs for known models.

Control flow: called from BCM47xx board setup after board detection. Only listed boards take action; others return immediately.

State and persistence: requests GPIO ownership and changes pin output state for the current boot only.

Dependencies and integration points: depends on `bcm47xx_board.board`, Linux GPIO request helpers, and the platform setup path.

Risks and test signals: wrong GPIO data can keep USB ports unpowered or conflict with another signal. Test by checking GPIO request success, USB VBUS availability, and device enumeration on affected boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm47xx/workarounds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/Kconfig -->
# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/Kconfig

Purpose: Kconfig menu for `sources/distributed-fs/ceph-client/arch/mips/bcm63xx/Kconfig`, exposing architecture configuration options for this MIPS platform area.

Important APIs and functions: declarative symbols include BCM63XX_CPU_3368, BCM63XX_CPU_6328, BCM63XX_CPU_6338, BCM63XX_CPU_6345, BCM63XX_CPU_6348, BCM63XX_CPU_6358, BCM63XX_CPU_6362, BCM63XX_CPU_6368. Notable selected dependencies include SYS_HAS_CPU_BMIPS4350, HAVE_PCI, SYS_HAS_CPU_BMIPS32_3300.

Control flow: `menuconfig` or defconfig resolution evaluates these symbols before build. Selected CPU/board/feature options control which source files, CPU support, and platform drivers Kbuild includes.

State and persistence: no runtime state. Values persist only in kernel `.config` and derived build artifacts.

Dependencies and integration points: integrates with top-level MIPS Kconfig, CPU capability symbols, board support choices, and Makefile `obj-$()` rules.

Risks and test signals: wrong dependencies can produce invalid builds or omit required CPU/platform support. Test by building representative defconfigs, checking symbol dependencies with `scripts/config` or `menuconfig`, and confirming selected objects match intended hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/Makefile

Purpose: Kbuild manifest controlling which objects or boot artifacts are built for `sources/distributed-fs/ceph-client/arch/mips/bcm63xx/Makefile`.

Important APIs and functions: declarative build entries include `obj-y		+= clk.o cpu.o cs.o gpio.o irq.o nvram.o prom.o reset.o \; obj-$(CONFIG_EARLY_PRINTK)	+= early_printk.o; obj-y		+= boards/`. It does not define runtime APIs.

Control flow: Kbuild evaluates the assignments according to enabled `CONFIG_*` symbols and compiles or links the selected objects into the MIPS kernel, compressed image, host tools, or platform subdirectories.

State and persistence: no runtime state. Its only persistent effect is generated build output under the kernel build tree.

Dependencies and integration points: integrates this directory with the parent architecture Makefiles, host tool build rules, and relevant platform Kconfig symbols.

Risks and test signals: incorrect object selection causes missing platform hooks or broken boot artifacts. Test through configured kernel builds, `make V=1` command inspection, and ensuring expected objects/DTBs/host tools are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/boards/Kconfig -->
# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/boards/Kconfig

Purpose: Kconfig menu for `sources/distributed-fs/ceph-client/arch/mips/bcm63xx/boards/Kconfig`, exposing architecture configuration options for this MIPS platform area.

Important APIs and functions: declarative symbols include BOARD_BCM963XX. Notable selected dependencies include SSB.

Control flow: `menuconfig` or defconfig resolution evaluates these symbols before build. Selected CPU/board/feature options control which source files, CPU support, and platform drivers Kbuild includes.

State and persistence: no runtime state. Values persist only in kernel `.config` and derived build artifacts.

Dependencies and integration points: integrates with top-level MIPS Kconfig, CPU capability symbols, board support choices, and Makefile `obj-$()` rules.

Risks and test signals: wrong dependencies can produce invalid builds or omit required CPU/platform support. Test by building representative defconfigs, checking symbol dependencies with `scripts/config` or `menuconfig`, and confirming selected objects match intended hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/boards/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/boards/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/boards/Makefile

Purpose: Kbuild manifest controlling which objects or boot artifacts are built for `sources/distributed-fs/ceph-client/arch/mips/bcm63xx/boards/Makefile`.

Important APIs and functions: declarative build entries include `obj-$(CONFIG_BOARD_BCM963XX)		+= board_bcm963xx.o`. It does not define runtime APIs.

Control flow: Kbuild evaluates the assignments according to enabled `CONFIG_*` symbols and compiles or links the selected objects into the MIPS kernel, compressed image, host tools, or platform subdirectories.

State and persistence: no runtime state. Its only persistent effect is generated build output under the kernel build tree.

Dependencies and integration points: integrates this directory with the parent architecture Makefiles, host tool build rules, and relevant platform Kconfig symbols.

Risks and test signals: incorrect object selection causes missing platform hooks or broken boot artifacts. Test through configured kernel builds, `make V=1` command inspection, and ensuring expected objects/DTBs/host tools are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/boards/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/boards/board_bcm963xx.c -->
# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/boards/board_bcm963xx.c

Purpose: board database and staged board initialization for legacy Broadcom 963xx/BCM63xx reference and ISP router boards.

Important APIs and functions: static `struct board_info` records board names, expected CPU IDs, UART/PCI/PCMCIA/USB/Ethernet flags, LED tables, and optional reset GPIOs. `board_prom_init()` reads boot flash/CFE/NVRAM or HCS board names, selects a board descriptor, initializes PCI and pinmux hints, and copies the selected descriptor out of `__initdata`. `board_setup()` validates a board was found and that the CPU ID matches. `board_register_devices()` registers UART, PCMCIA, Ethernet, USB device, SSB fallback SPROM, SPI/HSSPI, flash, GPIO LEDs, and optional EPHY reset GPIO. `board_get_name()` exposes the selected board name.

Control flow: boot proceeds in three stages: early PROM board identification, second-stage validation once early printk is available, and later platform-device registration. Device registration is conditional on fields in the selected `board_info` and MAC address allocation from NVRAM.

State and persistence: the global `board` struct is the durable in-kernel copy for the boot. It reads CFE version, NVRAM board name, MAC addresses, and PSI metadata from flash, but writes only kernel platform-device state and GPIO/pinmux registers.

Dependencies and integration points: integrates CFE/NVRAM layout, BCM63xx CPU helpers, GPIO mode registers, PCI enable state, Ethernet/flash/UART/SPI/HSSPI/PCMCIA/USBD registration helpers, GPIO LED subsystem, and SSB fallback SPROM for PCI WLAN.

Risks and test signals: board matching uses 16-byte names and hard-coded descriptors, so unknown or mistyped boards panic later or miss devices. MAC allocation failure suppresses Ethernet registration. Test signals include CFE version log, `board name` log, registered platform devices, correct LEDs, Ethernet MAC uniqueness, PCI WLAN SPROM behavior, and successful boot on each CPU family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/boards/board_bcm963xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/clk.c -->
# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/clk.c

Purpose: BCM63xx legacy clock framework provider for peripheral gates and fixed rates.

Important APIs and functions: `struct clk` instances describe named clocks and optional `set` callbacks. `clk_enable()` and `clk_disable()` serialize access with `clocks_mutex`, maintain reference counts, and call CPU-specific gate helpers such as `enetx_set`, `ephy_set`, `pcm_set`, `usbh_set`, `usbd_set`, `spi_set`, `hsspi_set`, `xtm_set`, `ipsec_set`, and `pcie_set`. `clk_get_rate()` returns fixed or computed rates, including HSSPI PLL rates. `bcm63xx_clk_init()` registers lookup aliases for platform drivers.

Control flow: drivers acquire clocks by lookup name, enable them around hardware use, and the set helpers manipulate PERF or reset registers according to detected CPU. Parent/rate mutators are mostly stubs because these clocks are simple gates or fixed-rate sources.

State and persistence: per-clock `usage` counters and hardware gate bits are runtime state only. Register writes affect peripherals until reset or later disable.

Dependencies and integration points: depends on BCM63xx CPU detection, PERF/GPIO/reset registers, Linux clkdev, and platform drivers for Ethernet, USB, SPI, HSSPI, PCM, PCIe, SAR/XTM, and IPsec.

Risks and test signals: wrong CPU mask or unbalanced clock users can leave peripherals dead or powered unnecessarily. Test signals include clock lookup success, paired enable/disable under driver probe/remove, working peripheral I/O, and register traces on each CPU variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/cpu.c -->
# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/cpu.c

Purpose: detects BCM63xx CPU identity, revision, clock frequency, memory size, and CPU-specific register layout used by the rest of the platform.

Important APIs and functions: `bcm63xx_get_cpu_rev()`, `bcm63xx_get_cpu_freq()`, and `bcm63xx_get_memory_size()` expose detected state. `detect_cpu_clock()` decodes PLL and strap registers for supported SoCs. `detect_memory_size()` reads memory controller registers. `bcm63xx_cpu_init()` matches PRID/chip ID, sets `bcm63xx_cpu_id`, revision, frequency, memory size, and exported register/IRQ tables.

Control flow: early platform code calls `bcm63xx_cpu_init()` before device registration. The function handles supported CPU families with compile-time conditionals, then logs or panics for unsupported combinations.

State and persistence: stores CPU ID, revision, frequency, memory size, and register table pointers in globals for this boot. No persistent writes.

Dependencies and integration points: used by nearly every BCM63xx file through `BCMCPU_IS_*` predicates and base/IRQ lookup helpers. Depends on MIPS CP0 PRID and BCM63xx memory-mapped registers.

Risks and test signals: incorrect detection cascades into wrong MMIO bases, IRQs, clocks, and resets. Test via boot logs, `/proc/cpuinfo`, memory size, platform-device resources, and peripheral operation on each enabled SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/cs.c -->
# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/cs.c

Purpose: BCM63xx chip-select control helpers for external memory/peripheral windows.

Important APIs and functions: `bcm63xx_set_cs_base()` validates chip-select number and power-of-two size, writes base/size encoding, and is exported. `bcm63xx_set_cs_param()` updates timing/parameter registers. `bcm63xx_set_cs_status()` enables or disables a CS line. A spinlock serializes register updates.

Control flow: board/device code calls these helpers before using external devices such as PCMCIA or flash windows. Each helper validates CS range and writes CPU-specific MPI registers.

State and persistence: mutates chip-select hardware registers for the current boot only.

Dependencies and integration points: depends on BCM63xx CPU helpers, MPI register definitions, `ilog2`, and external bus consumers.

Risks and test signals: invalid base/size encodings can alias memory windows or hang the bus. Test with flash/PCMCIA access, register dumps, and error paths for unsupported CS indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-enet.c -->
# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-enet.c

Purpose: BCM63xx platform-device registration for the `enet` hardware block.

Important APIs and functions: exported/init functions include register_shared. The file declares resources such as MMIO ranges, IRQs, DMA masks, or platform data, then registers a named `platform_device` for the corresponding driver.

Control flow: board or initcall code invokes the register helper when the selected board/SoC supports the block. The helper fills CPU-specific resource addresses via BCM63xx base/IRQ helpers and calls `platform_device_register`.

State and persistence: creates kernel platform-device state for this boot and may copy caller-supplied platform data. It performs no persistent storage.

Dependencies and integration points: depends on `bcm63xx_cpu` resource lookup, BCM63xx register definitions, and the Linux platform driver for `enet`. Includes indicate integration with linux/init.h, linux/kernel.h, linux/platform_device.h, linux/export.h, bcm63xx_dev_enet.h, bcm63xx_io.h, bcm63xx_regs.h.

Risks and test signals: wrong resource selection, IRQ count, DMA mask, or platform data prevents the child driver from probing. Test by checking platform device resources, driver probe logs, and functional I/O for the `enet` block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-enet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-flash.c -->
# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-flash.c

Purpose: BCM63xx platform-device registration for the `flash` hardware block.

Important APIs and functions: exported/init functions include bcm63xx_detect_flash_type, bcm63xx_flash_register. The file declares resources such as MMIO ranges, IRQs, DMA masks, or platform data, then registers a named `platform_device` for the corresponding driver.

Control flow: board or initcall code invokes the register helper when the selected board/SoC supports the block. The helper fills CPU-specific resource addresses via BCM63xx base/IRQ helpers and calls `platform_device_register`.

State and persistence: creates kernel platform-device state for this boot and may copy caller-supplied platform data. It performs no persistent storage.

Dependencies and integration points: depends on `bcm63xx_cpu` resource lookup, BCM63xx register definitions, and the Linux platform driver for `flash`. Includes indicate integration with linux/init.h, linux/kernel.h, linux/platform_device.h, linux/mtd/mtd.h, linux/mtd/partitions.h, linux/mtd/physmap.h, bcm63xx_cpu.h, bcm63xx_dev_flash.h.

Risks and test signals: wrong resource selection, IRQ count, DMA mask, or platform data prevents the child driver from probing. Test by checking platform device resources, driver probe logs, and functional I/O for the `flash` block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-flash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-hsspi.c -->
# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-hsspi.c

Purpose: BCM63xx platform-device registration for the `hsspi` hardware block.

Important APIs and functions: exported/init functions include bcm63xx_hsspi_register. The file declares resources such as MMIO ranges, IRQs, DMA masks, or platform data, then registers a named `platform_device` for the corresponding driver.

Control flow: board or initcall code invokes the register helper when the selected board/SoC supports the block. The helper fills CPU-specific resource addresses via BCM63xx base/IRQ helpers and calls `platform_device_register`.

State and persistence: creates kernel platform-device state for this boot and may copy caller-supplied platform data. It performs no persistent storage.

Dependencies and integration points: depends on `bcm63xx_cpu` resource lookup, BCM63xx register definitions, and the Linux platform driver for `hsspi`. Includes indicate integration with linux/init.h, linux/kernel.h, linux/platform_device.h, bcm63xx_cpu.h, bcm63xx_dev_hsspi.h, bcm63xx_regs.h.

Risks and test signals: wrong resource selection, IRQ count, DMA mask, or platform data prevents the child driver from probing. Test by checking platform device resources, driver probe logs, and functional I/O for the `hsspi` block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-hsspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-pcmcia.c -->
# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-pcmcia.c

Purpose: BCM63xx platform-device registration for the `pcmcia` hardware block.

Important APIs and functions: exported/init functions include bcm63xx_pcmcia_register. The file declares resources such as MMIO ranges, IRQs, DMA masks, or platform data, then registers a named `platform_device` for the corresponding driver.

Control flow: board or initcall code invokes the register helper when the selected board/SoC supports the block. The helper fills CPU-specific resource addresses via BCM63xx base/IRQ helpers and calls `platform_device_register`.

State and persistence: creates kernel platform-device state for this boot and may copy caller-supplied platform data. It performs no persistent storage.

Dependencies and integration points: depends on `bcm63xx_cpu` resource lookup, BCM63xx register definitions, and the Linux platform driver for `pcmcia`. Includes indicate integration with linux/init.h, linux/kernel.h, asm/bootinfo.h, linux/platform_device.h, bcm63xx_cs.h, bcm63xx_cpu.h, bcm63xx_dev_pcmcia.h, bcm63xx_io.h.

Risks and test signals: wrong resource selection, IRQ count, DMA mask, or platform data prevents the child driver from probing. Test by checking platform device resources, driver probe logs, and functional I/O for the `pcmcia` block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-pcmcia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-rng.c -->
# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-rng.c

Purpose: BCM63xx platform-device registration for the `rng` hardware block.

Important APIs and functions: exported/init functions include bcm63xx_rng_register. The file declares resources such as MMIO ranges, IRQs, DMA masks, or platform data, then registers a named `platform_device` for the corresponding driver.

Control flow: board or initcall code invokes the register helper when the selected board/SoC supports the block. The helper fills CPU-specific resource addresses via BCM63xx base/IRQ helpers and calls `platform_device_register`.

State and persistence: creates kernel platform-device state for this boot and may copy caller-supplied platform data. It performs no persistent storage.

Dependencies and integration points: depends on `bcm63xx_cpu` resource lookup, BCM63xx register definitions, and the Linux platform driver for `rng`. Includes indicate integration with linux/init.h, linux/kernel.h, linux/platform_device.h, bcm63xx_cpu.h.

Risks and test signals: wrong resource selection, IRQ count, DMA mask, or platform data prevents the child driver from probing. Test by checking platform device resources, driver probe logs, and functional I/O for the `rng` block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-spi.c -->
# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-spi.c

Purpose: BCM63xx platform-device registration for the `spi` hardware block.

Important APIs and functions: exported/init functions include bcm63xx_spi_register. The file declares resources such as MMIO ranges, IRQs, DMA masks, or platform data, then registers a named `platform_device` for the corresponding driver.

Control flow: board or initcall code invokes the register helper when the selected board/SoC supports the block. The helper fills CPU-specific resource addresses via BCM63xx base/IRQ helpers and calls `platform_device_register`.

State and persistence: creates kernel platform-device state for this boot and may copy caller-supplied platform data. It performs no persistent storage.

Dependencies and integration points: depends on `bcm63xx_cpu` resource lookup, BCM63xx register definitions, and the Linux platform driver for `spi`. Includes indicate integration with linux/init.h, linux/kernel.h, linux/export.h, linux/platform_device.h, linux/err.h, linux/clk.h, bcm63xx_cpu.h, bcm63xx_dev_spi.h.

Risks and test signals: wrong resource selection, IRQ count, DMA mask, or platform data prevents the child driver from probing. Test by checking platform device resources, driver probe logs, and functional I/O for the `spi` block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-uart.c -->
# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-uart.c

Purpose: BCM63xx platform-device registration for the `uart` hardware block.

Important APIs and functions: exported/init functions include bcm63xx_uart_register. The file declares resources such as MMIO ranges, IRQs, DMA masks, or platform data, then registers a named `platform_device` for the corresponding driver.

Control flow: board or initcall code invokes the register helper when the selected board/SoC supports the block. The helper fills CPU-specific resource addresses via BCM63xx base/IRQ helpers and calls `platform_device_register`.

State and persistence: creates kernel platform-device state for this boot and may copy caller-supplied platform data. It performs no persistent storage.

Dependencies and integration points: depends on `bcm63xx_cpu` resource lookup, BCM63xx register definitions, and the Linux platform driver for `uart`. Includes indicate integration with linux/init.h, linux/kernel.h, linux/platform_device.h, bcm63xx_cpu.h, bcm63xx_dev_uart.h.

Risks and test signals: wrong resource selection, IRQ count, DMA mask, or platform data prevents the child driver from probing. Test by checking platform device resources, driver probe logs, and functional I/O for the `uart` block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-uart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-usb-usbd.c -->
# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-usb-usbd.c

Purpose: BCM63xx platform-device registration for the `usb-usbd` hardware block.

Important APIs and functions: exported/init functions include bcm63xx_usbd_register. The file declares resources such as MMIO ranges, IRQs, DMA masks, or platform data, then registers a named `platform_device` for the corresponding driver.

Control flow: board or initcall code invokes the register helper when the selected board/SoC supports the block. The helper fills CPU-specific resource addresses via BCM63xx base/IRQ helpers and calls `platform_device_register`.

State and persistence: creates kernel platform-device state for this boot and may copy caller-supplied platform data. It performs no persistent storage.

Dependencies and integration points: depends on `bcm63xx_cpu` resource lookup, BCM63xx register definitions, and the Linux platform driver for `usb-usbd`. Includes indicate integration with linux/init.h, linux/kernel.h, linux/platform_device.h, linux/dma-mapping.h, bcm63xx_cpu.h, bcm63xx_dev_usb_usbd.h.

Risks and test signals: wrong resource selection, IRQ count, DMA mask, or platform data prevents the child driver from probing. Test by checking platform device resources, driver probe logs, and functional I/O for the `usb-usbd` block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-usb-usbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-wdt.c -->
# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-wdt.c

Purpose: BCM63xx platform-device registration for the `wdt` hardware block.

Important APIs and functions: exported/init functions include bcm63xx_wdt_register. The file declares resources such as MMIO ranges, IRQs, DMA masks, or platform data, then registers a named `platform_device` for the corresponding driver.

Control flow: board or initcall code invokes the register helper when the selected board/SoC supports the block. The helper fills CPU-specific resource addresses via BCM63xx base/IRQ helpers and calls `platform_device_register`.

State and persistence: creates kernel platform-device state for this boot and may copy caller-supplied platform data. It performs no persistent storage.

Dependencies and integration points: depends on `bcm63xx_cpu` resource lookup, BCM63xx register definitions, and the Linux platform driver for `wdt`. Includes indicate integration with linux/init.h, linux/kernel.h, linux/platform_device.h, linux/platform_data/bcm7038_wdt.h, bcm63xx_cpu.h.

Risks and test signals: wrong resource selection, IRQ count, DMA mask, or platform data prevents the child driver from probing. Test by checking platform device resources, driver probe logs, and functional I/O for the `wdt` block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/dev-wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/early_printk.c -->
# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/early_printk.c

Purpose: early printk backend that writes characters directly to the BCM63xx UART FIFO before the serial driver is ready.

Important APIs and functions: key functions include wait_xfered, prom_putchar. These functions expose early architecture services or small platform controllers to the rest of the BCM63xx port.

Control flow: called from MIPS platform hooks, board initialization, or generic kernel subsystems depending on boot stage. Hardware access is direct MMIO through BCM63xx register helpers.

State and persistence: maintains only boot/runtime kernel state such as global parsed NVRAM data, GPIO/chip-select/timer register state, platform callbacks, or early-console output. Flash contents are read but not rewritten here unless the underlying hardware state is explicitly toggled.

Dependencies and integration points: includes bcm63xx_io.h, linux/serial_bcm63xx.h, asm/setup.h; integration is with BCM63xx CPU detection, register maps, generic MIPS boot hooks, GPIO/IRQ/timer/serial subsystems, and board code.

Risks and test signals: these files sit early in boot, so bad register offsets or CPU-family assumptions can hang before full logging. Test with early console, boot logs, `/proc/iomem`, GPIO/chip-select behavior, board detection, and subsystem-specific smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/early_printk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/gpio.c -->
# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/gpio.c

Purpose: implements the BCM63xx GPIO controller as a Linux `gpio_chip`.

Important APIs and functions: `bcm63xx_gpio_init()` initializes CPU-specific direction defaults and registers the chip. `bcm63xx_gpio_set()`, `bcm63xx_gpio_get()`, and direction callbacks update GPIO data/direction registers under a spinlock. `bcm63xx_gpio_out_low_reg_init()` handles CPUs with split output-low registers.

Control flow: platform setup initializes the controller before board devices request LEDs or reset GPIOs. Generic GPIO consumers call the chip callbacks.

State and persistence: GPIO direction and output bits are hardware runtime state only.

Dependencies and integration points: integrates with Linux gpiolib, BCM63xx CPU/register helpers, LED devices, board reset GPIOs, and any platform consumer using GPIO numbers.

Risks and test signals: wrong register split or direction handling affects every GPIO consumer. Test LEDs, reset pins, input buttons where present, and gpiolib debugfs/state inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/irq.c -->
# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/irq.c

Purpose: BCM63xx interrupt controller setup and dispatch for internal and external IRQ lines, including CPU-family-specific IPIC/EPIC register widths.

Important APIs and functions: generated IPIC helpers provide internal IRQ mask/unmask and dispatch variants. `plat_irq_dispatch()` decodes MIPS pending interrupt bits and routes timer, internal, and external interrupts. `bcm63xx_internal_irq_mask/unmask()` and external counterparts update controller registers under spinlocks. `bcm63xx_init_irq()` installs irq_chip handlers. `arch_init_irq()` initializes MIPS CPU IRQs and BCM63xx controller state.

Control flow: architecture IRQ init selects the correct dispatch/mask implementations, configures each IRQ descriptor, and unmasks CPU-level interrupt lines. Runtime dispatch reads pending status and calls generic IRQ handling for active bits.

State and persistence: maintains mask state in interrupt controller registers and spinlock-protected updates. No storage survives reset.

Dependencies and integration points: integrates MIPS CPU interrupt lines, BCM63xx PERF/IRQ registers, generic IRQ core, SMP affinity conditionals, and platform-device IRQ resources.

Risks and test signals: wrong width, pending-bit mapping, or external IRQ clear behavior can lose or storm interrupts. Test signals include timer ticks, UART/Ethernet/SPI interrupts, external GPIO IRQs, `/proc/interrupts`, SMP affinity behavior where supported, and no spurious interrupt floods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/nvram.c -->
# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/nvram.c

Purpose: parses Broadcom 963xx NVRAM from boot flash into a safe in-kernel copy.

Important APIs and functions: `bcm63xx_nvram_init()` copies the NVRAM block, checks CRC32, and reports validity. `bcm63xx_nvram_get_name()` returns the board name. `bcm63xx_nvram_get_mac_address()` hands out sequential MAC addresses from the base address while avoiding invalid data. `bcm63xx_nvram_get_psi_size()` returns configured PSI size or a default.

Control flow: board PROM init calls the parser with a flash address. Later board registration asks for board name and device MACs.

State and persistence: keeps a static copy of NVRAM and a runtime MAC counter. It reads flash data but does not write flash.

Dependencies and integration points: integrates CFE/NVRAM layout, board detection, Ethernet registration, and kernel CRC/MAC validation helpers.

Risks and test signals: bad CRC or invalid MAC data can suppress device registration or generate wrong addresses. Test boot logs, board-name detection, MAC uniqueness, and fallback PSI behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/nvram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/prom.c -->
# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/prom.c

Purpose: BCM63xx PROM entry point that initializes CPU detection, memory regions, command line, board PROM data, and SMP operations.

Important APIs and functions: key functions include prom_init. These functions expose early architecture services or small platform controllers to the rest of the BCM63xx port.

Control flow: called from MIPS platform hooks, board initialization, or generic kernel subsystems depending on boot stage. Hardware access is direct MMIO through BCM63xx register helpers.

State and persistence: maintains only boot/runtime kernel state such as global parsed NVRAM data, GPIO/chip-select/timer register state, platform callbacks, or early-console output. Flash contents are read but not rewritten here unless the underlying hardware state is explicitly toggled.

Dependencies and integration points: includes linux/init.h, linux/memblock.h, linux/smp.h, asm/bootinfo.h, asm/bmips.h, asm/smp-ops.h, asm/mipsregs.h, bcm63xx_board.h, bcm63xx_cpu.h, bcm63xx_io.h; integration is with BCM63xx CPU detection, register maps, generic MIPS boot hooks, GPIO/IRQ/timer/serial subsystems, and board code.

Risks and test signals: these files sit early in boot, so bad register offsets or CPU-family assumptions can hang before full logging. Test with early console, boot logs, `/proc/iomem`, GPIO/chip-select behavior, board detection, and subsystem-specific smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/prom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/reset.c -->
# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/reset.c

Purpose: maps generic BCM63xx reset IDs to CPU-specific soft-reset register bits and exposes reset assertion/deassertion helpers.

Important APIs and functions: macro-generated reset tables define bit positions for SPI, Ethernet, USBH, USBD, DSL, SAR, EPHY, ENETSW, PCM, MPI, PCIe, and PCIe external resets by CPU. `bcm63xx_core_set_reset()` writes the appropriate soft-reset bit with locking and optional delay. `bcm63xx_core_assert()` and `bcm63xx_core_deassert()` are exported wrappers.

Control flow: callers pass a logical reset enum. The helper selects the active CPU reset table, rejects unsupported zero-bit entries, and toggles the soft-reset register.

State and persistence: soft-reset hardware bits are runtime SoC state only. The mutex serializes register updates.

Dependencies and integration points: used by clock and device drivers that must reset BCM63xx peripheral blocks. Depends on CPU detection and PERF soft-reset register definitions.

Risks and test signals: zero-bit unsupported reset entries and CPU-specific mappings are easy to misuse. Test by exercising probe/remove or reset paths for each peripheral, checking register writes, and confirming devices recover after reset toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/setup.c -->
# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/setup.c

Purpose: BCM63xx architecture setup hook for machine restart/halt, memory setup, board setup, device registration, and core platform init.

Important APIs and functions: key functions include bcm63xx_machine_halt, bcm6348_a1_reboot, bcm63xx_machine_reboot, __bcm63xx_machine_reboot, plat_time_init, plat_mem_setup, bcm63xx_register_devices. These functions expose early architecture services or small platform controllers to the rest of the BCM63xx port.

Control flow: called from MIPS platform hooks, board initialization, or generic kernel subsystems depending on boot stage. Hardware access is direct MMIO through BCM63xx register helpers.

State and persistence: maintains only boot/runtime kernel state such as global parsed NVRAM data, GPIO/chip-select/timer register state, platform callbacks, or early-console output. Flash contents are read but not rewritten here unless the underlying hardware state is explicitly toggled.

Dependencies and integration points: includes linux/init.h, linux/kernel.h, linux/delay.h, linux/memblock.h, linux/ioport.h, linux/pm.h, asm/bmips.h, asm/bootinfo.h, asm/time.h, asm/reboot.h; integration is with BCM63xx CPU detection, register maps, generic MIPS boot hooks, GPIO/IRQ/timer/serial subsystems, and board code.

Risks and test signals: these files sit early in boot, so bad register offsets or CPU-family assumptions can hang before full logging. Test with early console, boot logs, `/proc/iomem`, GPIO/chip-select behavior, board detection, and subsystem-specific smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/timer.c -->
# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/timer.c

Purpose: low-level BCM63xx hardware timer helper implementation.

Important APIs and functions: exports timer count, compare, enable/disable, and interrupt mask helpers around BCM63xx timer registers. Callers use logical timer IDs rather than raw offsets.

Control flow: platform or driver code configures a timer by setting count/compare values, enabling interrupt generation, and starting/stopping the timer through these helpers.

State and persistence: hardware timer counters, compare registers, and interrupt masks are runtime-only state.

Dependencies and integration points: depends on BCM63xx CPU/register helpers and integrates with MIPS timer users or peripheral drivers needing SoC timers.

Risks and test signals: invalid timer IDs or wrong register offsets cause missed timeouts or interrupt storms. Test by exercising users of these timer helpers and inspecting timer IRQ behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm63xx/timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bmips/Kconfig -->
# sources/distributed-fs/ceph-client/arch/mips/bmips/Kconfig

Purpose: Kconfig menu for `sources/distributed-fs/ceph-client/arch/mips/bmips/Kconfig`, exposing architecture configuration options for this MIPS platform area.

Important APIs and functions: declarative symbols include DT_NONE, DT_BCM93384WVG, DT_BCM93384WVG_VIPER, DT_BCM96368MVWG, DT_BCM9EJTAGPRB, DT_BCM97125CBMB, DT_BCM97346DBSMB, DT_BCM97358SVMB, DT_BCM97360SVMB, DT_BCM97362SVMB, DT_BCM97420C, DT_BCM97425SVMB, DT_BCM97435SVMB, DT_COMTREND_VR3032U, DT_NETGEAR_CVG834G, DT_SFR_NEUFBOX4_SERCOMM, DT_SFR_NEUFBOX6_SERCOMM. Notable selected dependencies include BUILTIN_DTB.

Control flow: `menuconfig` or defconfig resolution evaluates these symbols before build. Selected CPU/board/feature options control which source files, CPU support, and platform drivers Kbuild includes.

State and persistence: no runtime state. Values persist only in kernel `.config` and derived build artifacts.

Dependencies and integration points: integrates with top-level MIPS Kconfig, CPU capability symbols, board support choices, and Makefile `obj-$()` rules.

Risks and test signals: wrong dependencies can produce invalid builds or omit required CPU/platform support. Test by building representative defconfigs, checking symbol dependencies with `scripts/config` or `menuconfig`, and confirming selected objects match intended hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bmips/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bmips/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/bmips/Makefile

Purpose: Kbuild manifest controlling which objects or boot artifacts are built for `sources/distributed-fs/ceph-client/arch/mips/bmips/Makefile`.

Important APIs and functions: declarative build entries include `obj-y		+= setup.o irq.o dma.o`. It does not define runtime APIs.

Control flow: Kbuild evaluates the assignments according to enabled `CONFIG_*` symbols and compiles or links the selected objects into the MIPS kernel, compressed image, host tools, or platform subdirectories.

State and persistence: no runtime state. Its only persistent effect is generated build output under the kernel build tree.

Dependencies and integration points: integrates this directory with the parent architecture Makefiles, host tool build rules, and relevant platform Kconfig symbols.

Risks and test signals: incorrect object selection causes missing platform hooks or broken boot artifacts. Test through configured kernel builds, `make V=1` command inspection, and ensuring expected objects/DTBs/host tools are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bmips/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bmips/dma.c -->
# sources/distributed-fs/ceph-client/arch/mips/bmips/dma.c

Purpose: BMIPS DMA range and remapping setup for device-tree-described Broadcom systems.

Important APIs and functions: architecture DMA setup code inspects DT DMA ranges and configures direct mapping offsets or fallbacks used by DMA API translations.

Control flow: early platform setup parses memory/DMA constraints before devices probe, then generic DMA mapping uses the established offsets.

State and persistence: boot-time DMA address policy only.

Dependencies and integration points: integrates devicetree, memblock, DMA direct mapping, and BMIPS device population.

Risks and test signals: bad DMA windows corrupt I/O or break devices above 32-bit address limits. Test network/storage DMA workloads and DT variants with different ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bmips/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bmips/irq.c -->
# sources/distributed-fs/ceph-client/arch/mips/bmips/irq.c

Purpose: BMIPS interrupt controller and IRQ-domain setup for Broadcom DT systems.

Important APIs and functions: initializes CPU/SoC interrupt routing, maps device-tree interrupts, and installs dispatch handlers for BMIPS platforms.

Control flow: `arch_init_irq`-style setup runs during boot, then runtime interrupts are dispatched through generic IRQ handling.

State and persistence: interrupt masks, domains, and descriptor state for current boot only.

Dependencies and integration points: integrates MIPS CPU IRQs, irqchip/irqdomain code, devicetree interrupt specifiers, and platform devices.

Risks and test signals: mapping mistakes show as missing UART/timer/network interrupts. Test `/proc/interrupts`, DT boot logs, and driver interrupt activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bmips/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bmips/setup.c -->
# sources/distributed-fs/ceph-client/arch/mips/bmips/setup.c

Purpose: BMIPS platform setup for DT-based Broadcom SoCs.

Important APIs and functions: setup hooks parse DT compatibility, configure restart/poweroff behavior, initialize SoC quirks, and populate platform devices.

Control flow: MIPS platform setup runs before device probing; it establishes machine callbacks and then lets OF platform population instantiate devices.

State and persistence: boot-only machine callback and device state.

Dependencies and integration points: depends on devicetree, BMIPS CPU support, OF platform, SMP/cache helpers, and reset/reboot registers.

Risks and test signals: wrong compatibility matching can select bad reboot or quirk paths. Test with BMIPS DTBs, reboot behavior, CPU info, and platform-device enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bmips/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/boot/Makefile

Purpose: Kbuild manifest controlling which objects or boot artifacts are built for `sources/distributed-fs/ceph-client/arch/mips/boot/Makefile`.

Important APIs and functions: declarative build entries include `hostprogs := elf2ecoff; suffix-y			:= bin; suffix-$(CONFIG_KERNEL_BZIP2)	:= bz2; suffix-$(CONFIG_KERNEL_GZIP)	:= gz; suffix-$(CONFIG_KERNEL_LZMA)	:= lzma; suffix-$(CONFIG_KERNEL_LZO)	:= lzo; targets := vmlinux.ecoff; targets += vmlinux.bin; targets += vmlinux.srec; targets += vmlinux.bin.bz2`. It does not define runtime APIs.

Control flow: Kbuild evaluates the assignments according to enabled `CONFIG_*` symbols and compiles or links the selected objects into the MIPS kernel, compressed image, host tools, or platform subdirectories.

State and persistence: no runtime state. Its only persistent effect is generated build output under the kernel build tree.

Dependencies and integration points: integrates this directory with the parent architecture Makefiles, host tool build rules, and relevant platform Kconfig symbols.

Risks and test signals: incorrect object selection causes missing platform hooks or broken boot artifacts. Test through configured kernel builds, `make V=1` command inspection, and ensuring expected objects/DTBs/host tools are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/boot/compressed/Makefile

Purpose: Kbuild manifest controlling which objects or boot artifacts are built for `sources/distributed-fs/ceph-client/arch/mips/boot/compressed/Makefile`.

Important APIs and functions: declarative build entries include `KBUILD_CFLAGS := $(filter-out $(CC_FLAGS_FTRACE), $(KBUILD_CFLAGS)); KBUILD_CFLAGS := $(filter-out -fstack-protector, $(KBUILD_CFLAGS)); KBUILD_CFLAGS := $(filter-out -march=loongson3a, $(KBUILD_CFLAGS)) -march=mips64r2; KBUILD_CFLAGS := $(KBUILD_CFLAGS) -D__KERNEL__ -D__DISABLE_EXPORTS \; KBUILD_AFLAGS := $(KBUILD_AFLAGS) -D__ASSEMBLY__ \; targets := $(notdir $(vmlinuzobjs-y)); targets += vmlinux.bin; OBJCOPYFLAGS_vmlinux.bin := $(OBJCOPYFLAGS) -O binary -R .comment -S; targets += vmlinux.bin.z; targets += piggy.o dummy.o`. It does not define runtime APIs.

Control flow: Kbuild evaluates the assignments according to enabled `CONFIG_*` symbols and compiles or links the selected objects into the MIPS kernel, compressed image, host tools, or platform subdirectories.

State and persistence: no runtime state. Its only persistent effect is generated build output under the kernel build tree.

Dependencies and integration points: integrates this directory with the parent architecture Makefiles, host tool build rules, and relevant platform Kconfig symbols.

Risks and test signals: incorrect object selection causes missing platform hooks or broken boot artifacts. Test through configured kernel builds, `make V=1` command inspection, and ensuring expected objects/DTBs/host tools are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/ashldi3.c -->
# sources/distributed-fs/ceph-client/arch/mips/boot/compressed/ashldi3.c

Purpose: MIPS compressed-kernel boot support file `ashldi3.c`. It provides either decompressor build rules, tiny C runtime helpers, UART debug output, or low-level entry code needed before the full kernel is decompressed.

Important APIs and functions: visible functions or entry points include assembly entry/build-time declarations. The file is compiled into the self-extracting boot image with minimal library support.

Control flow: firmware jumps into the compressed image entry code, the decompressor runtime initializes enough state for debug I/O and memory operations, calls the selected decompression backend, then jumps to the decompressed kernel address.

State and persistence: uses only early boot memory, scratch buffers, UART registers, and linker-provided symbols. No persistent state.

Dependencies and integration points: depends on the compressed boot Makefile, linker script symbols, optional debug UART backends, architecture byte-order/libgcc replacement helpers, and kernel decompressor interfaces.

Risks and test signals: failures are usually pre-kernel and hard to diagnose. Test by building all compression modes, enabling early compressed boot debug where supported, checking image load addresses, and booting on boards that use each UART/debug path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/ashldi3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/bswapdi.c -->
# sources/distributed-fs/ceph-client/arch/mips/boot/compressed/bswapdi.c

Purpose: MIPS compressed-kernel boot support file `bswapdi.c`. It provides either decompressor build rules, tiny C runtime helpers, UART debug output, or low-level entry code needed before the full kernel is decompressed.

Important APIs and functions: visible functions or entry points include assembly entry/build-time declarations. The file is compiled into the self-extracting boot image with minimal library support.

Control flow: firmware jumps into the compressed image entry code, the decompressor runtime initializes enough state for debug I/O and memory operations, calls the selected decompression backend, then jumps to the decompressed kernel address.

State and persistence: uses only early boot memory, scratch buffers, UART registers, and linker-provided symbols. No persistent state.

Dependencies and integration points: depends on the compressed boot Makefile, linker script symbols, optional debug UART backends, architecture byte-order/libgcc replacement helpers, and kernel decompressor interfaces.

Risks and test signals: failures are usually pre-kernel and hard to diagnose. Test by building all compression modes, enabling early compressed boot debug where supported, checking image load addresses, and booting on boards that use each UART/debug path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/bswapdi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/bswapsi.c -->
# sources/distributed-fs/ceph-client/arch/mips/boot/compressed/bswapsi.c

Purpose: MIPS compressed-kernel boot support file `bswapsi.c`. It provides either decompressor build rules, tiny C runtime helpers, UART debug output, or low-level entry code needed before the full kernel is decompressed.

Important APIs and functions: visible functions or entry points include assembly entry/build-time declarations. The file is compiled into the self-extracting boot image with minimal library support.

Control flow: firmware jumps into the compressed image entry code, the decompressor runtime initializes enough state for debug I/O and memory operations, calls the selected decompression backend, then jumps to the decompressed kernel address.

State and persistence: uses only early boot memory, scratch buffers, UART registers, and linker-provided symbols. No persistent state.

Dependencies and integration points: depends on the compressed boot Makefile, linker script symbols, optional debug UART backends, architecture byte-order/libgcc replacement helpers, and kernel decompressor interfaces.

Risks and test signals: failures are usually pre-kernel and hard to diagnose. Test by building all compression modes, enabling early compressed boot debug where supported, checking image load addresses, and booting on boards that use each UART/debug path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/bswapsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/calc_vmlinuz_load_addr.c -->
# sources/distributed-fs/ceph-client/arch/mips/boot/compressed/calc_vmlinuz_load_addr.c

Purpose: MIPS compressed-kernel boot support file `calc_vmlinuz_load_addr.c`. It provides either decompressor build rules, tiny C runtime helpers, UART debug output, or low-level entry code needed before the full kernel is decompressed.

Important APIs and functions: visible functions or entry points include main. The file is compiled into the self-extracting boot image with minimal library support.

Control flow: firmware jumps into the compressed image entry code, the decompressor runtime initializes enough state for debug I/O and memory operations, calls the selected decompression backend, then jumps to the decompressed kernel address.

State and persistence: uses only early boot memory, scratch buffers, UART registers, and linker-provided symbols. No persistent state.

Dependencies and integration points: depends on the compressed boot Makefile, linker script symbols, optional debug UART backends, architecture byte-order/libgcc replacement helpers, and kernel decompressor interfaces.

Risks and test signals: failures are usually pre-kernel and hard to diagnose. Test by building all compression modes, enabling early compressed boot debug where supported, checking image load addresses, and booting on boards that use each UART/debug path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/calc_vmlinuz_load_addr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/clz_ctz.c -->
# sources/distributed-fs/ceph-client/arch/mips/boot/compressed/clz_ctz.c

Purpose: MIPS compressed-kernel boot support file `clz_ctz.c`. It provides either decompressor build rules, tiny C runtime helpers, UART debug output, or low-level entry code needed before the full kernel is decompressed.

Important APIs and functions: visible functions or entry points include assembly entry/build-time declarations. The file is compiled into the self-extracting boot image with minimal library support.

Control flow: firmware jumps into the compressed image entry code, the decompressor runtime initializes enough state for debug I/O and memory operations, calls the selected decompression backend, then jumps to the decompressed kernel address.

State and persistence: uses only early boot memory, scratch buffers, UART registers, and linker-provided symbols. No persistent state.

Dependencies and integration points: depends on the compressed boot Makefile, linker script symbols, optional debug UART backends, architecture byte-order/libgcc replacement helpers, and kernel decompressor interfaces.

Risks and test signals: failures are usually pre-kernel and hard to diagnose. Test by building all compression modes, enabling early compressed boot debug where supported, checking image load addresses, and booting on boards that use each UART/debug path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/clz_ctz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/dbg.c -->
# sources/distributed-fs/ceph-client/arch/mips/boot/compressed/dbg.c

Purpose: MIPS compressed-kernel boot support file `dbg.c`. It provides either decompressor build rules, tiny C runtime helpers, UART debug output, or low-level entry code needed before the full kernel is decompressed.

Important APIs and functions: visible functions or entry points include putc, puts, puthex. The file is compiled into the self-extracting boot image with minimal library support.

Control flow: firmware jumps into the compressed image entry code, the decompressor runtime initializes enough state for debug I/O and memory operations, calls the selected decompression backend, then jumps to the decompressed kernel address.

State and persistence: uses only early boot memory, scratch buffers, UART registers, and linker-provided symbols. No persistent state.

Dependencies and integration points: depends on the compressed boot Makefile, linker script symbols, optional debug UART backends, architecture byte-order/libgcc replacement helpers, and kernel decompressor interfaces.

Risks and test signals: failures are usually pre-kernel and hard to diagnose. Test by building all compression modes, enabling early compressed boot debug where supported, checking image load addresses, and booting on boards that use each UART/debug path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/dbg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/decompress.c -->
# sources/distributed-fs/ceph-client/arch/mips/boot/compressed/decompress.c

Purpose: MIPS compressed-kernel boot support file `decompress.c`. It provides either decompressor build rules, tiny C runtime helpers, UART debug output, or low-level entry code needed before the full kernel is decompressed.

Important APIs and functions: visible functions or entry points include error, __stack_chk_fail, decompress_kernel. The file is compiled into the self-extracting boot image with minimal library support.

Control flow: firmware jumps into the compressed image entry code, the decompressor runtime initializes enough state for debug I/O and memory operations, calls the selected decompression backend, then jumps to the decompressed kernel address.

State and persistence: uses only early boot memory, scratch buffers, UART registers, and linker-provided symbols. No persistent state.

Dependencies and integration points: depends on the compressed boot Makefile, linker script symbols, optional debug UART backends, architecture byte-order/libgcc replacement helpers, and kernel decompressor interfaces.

Risks and test signals: failures are usually pre-kernel and hard to diagnose. Test by building all compression modes, enabling early compressed boot debug where supported, checking image load addresses, and booting on boards that use each UART/debug path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/decompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/decompress.h -->
# sources/distributed-fs/ceph-client/arch/mips/boot/compressed/decompress.h

Purpose: MIPS compressed-kernel boot support file `decompress.h`. It provides either decompressor build rules, tiny C runtime helpers, UART debug output, or low-level entry code needed before the full kernel is decompressed.

Important APIs and functions: visible functions or entry points include error, decompress_kernel. The file is compiled into the self-extracting boot image with minimal library support.

Control flow: firmware jumps into the compressed image entry code, the decompressor runtime initializes enough state for debug I/O and memory operations, calls the selected decompression backend, then jumps to the decompressed kernel address.

State and persistence: uses only early boot memory, scratch buffers, UART registers, and linker-provided symbols. No persistent state.

Dependencies and integration points: depends on the compressed boot Makefile, linker script symbols, optional debug UART backends, architecture byte-order/libgcc replacement helpers, and kernel decompressor interfaces.

Risks and test signals: failures are usually pre-kernel and hard to diagnose. Test by building all compression modes, enabling early compressed boot debug where supported, checking image load addresses, and booting on boards that use each UART/debug path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/decompress.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/dummy.c -->
# sources/distributed-fs/ceph-client/arch/mips/boot/compressed/dummy.c

Purpose: MIPS compressed-kernel boot support file `dummy.c`. It provides either decompressor build rules, tiny C runtime helpers, UART debug output, or low-level entry code needed before the full kernel is decompressed.

Important APIs and functions: visible functions or entry points include main. The file is compiled into the self-extracting boot image with minimal library support.

Control flow: firmware jumps into the compressed image entry code, the decompressor runtime initializes enough state for debug I/O and memory operations, calls the selected decompression backend, then jumps to the decompressed kernel address.

State and persistence: uses only early boot memory, scratch buffers, UART registers, and linker-provided symbols. No persistent state.

Dependencies and integration points: depends on the compressed boot Makefile, linker script symbols, optional debug UART backends, architecture byte-order/libgcc replacement helpers, and kernel decompressor interfaces.

Risks and test signals: failures are usually pre-kernel and hard to diagnose. Test by building all compression modes, enabling early compressed boot debug where supported, checking image load addresses, and booting on boards that use each UART/debug path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/dummy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/head.S -->
# sources/distributed-fs/ceph-client/arch/mips/boot/compressed/head.S

Purpose: MIPS compressed-kernel boot support file `head.S`. It provides either decompressor build rules, tiny C runtime helpers, UART debug output, or low-level entry code needed before the full kernel is decompressed.

Important APIs and functions: visible functions or entry points include assembly entry/build-time declarations. The file is compiled into the self-extracting boot image with minimal library support.

Control flow: firmware jumps into the compressed image entry code, the decompressor runtime initializes enough state for debug I/O and memory operations, calls the selected decompression backend, then jumps to the decompressed kernel address.

State and persistence: uses only early boot memory, scratch buffers, UART registers, and linker-provided symbols. No persistent state.

Dependencies and integration points: depends on the compressed boot Makefile, linker script symbols, optional debug UART backends, architecture byte-order/libgcc replacement helpers, and kernel decompressor interfaces.

Risks and test signals: failures are usually pre-kernel and hard to diagnose. Test by building all compression modes, enabling early compressed boot debug where supported, checking image load addresses, and booting on boards that use each UART/debug path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/string.c -->
# sources/distributed-fs/ceph-client/arch/mips/boot/compressed/string.c

Purpose: MIPS compressed-kernel boot support file `string.c`. It provides either decompressor build rules, tiny C runtime helpers, UART debug output, or low-level entry code needed before the full kernel is decompressed.

Important APIs and functions: visible functions or entry points include memmove. The file is compiled into the self-extracting boot image with minimal library support.

Control flow: firmware jumps into the compressed image entry code, the decompressor runtime initializes enough state for debug I/O and memory operations, calls the selected decompression backend, then jumps to the decompressed kernel address.

State and persistence: uses only early boot memory, scratch buffers, UART registers, and linker-provided symbols. No persistent state.

Dependencies and integration points: depends on the compressed boot Makefile, linker script symbols, optional debug UART backends, architecture byte-order/libgcc replacement helpers, and kernel decompressor interfaces.

Risks and test signals: failures are usually pre-kernel and hard to diagnose. Test by building all compression modes, enabling early compressed boot debug where supported, checking image load addresses, and booting on boards that use each UART/debug path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/string.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/uart-16550.c -->
# sources/distributed-fs/ceph-client/arch/mips/boot/compressed/uart-16550.c

Purpose: MIPS compressed-kernel boot support file `uart-16550.c`. It provides either decompressor build rules, tiny C runtime helpers, UART debug output, or low-level entry code needed before the full kernel is decompressed.

Important APIs and functions: visible functions or entry points include serial_in, serial_out, putc. The file is compiled into the self-extracting boot image with minimal library support.

Control flow: firmware jumps into the compressed image entry code, the decompressor runtime initializes enough state for debug I/O and memory operations, calls the selected decompression backend, then jumps to the decompressed kernel address.

State and persistence: uses only early boot memory, scratch buffers, UART registers, and linker-provided symbols. No persistent state.

Dependencies and integration points: depends on the compressed boot Makefile, linker script symbols, optional debug UART backends, architecture byte-order/libgcc replacement helpers, and kernel decompressor interfaces.

Risks and test signals: failures are usually pre-kernel and hard to diagnose. Test by building all compression modes, enabling early compressed boot debug where supported, checking image load addresses, and booting on boards that use each UART/debug path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/uart-16550.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/uart-alchemy.c -->
# sources/distributed-fs/ceph-client/arch/mips/boot/compressed/uart-alchemy.c

Purpose: MIPS compressed-kernel boot support file `uart-alchemy.c`. It provides either decompressor build rules, tiny C runtime helpers, UART debug output, or low-level entry code needed before the full kernel is decompressed.

Important APIs and functions: visible functions or entry points include putc. The file is compiled into the self-extracting boot image with minimal library support.

Control flow: firmware jumps into the compressed image entry code, the decompressor runtime initializes enough state for debug I/O and memory operations, calls the selected decompression backend, then jumps to the decompressed kernel address.

State and persistence: uses only early boot memory, scratch buffers, UART registers, and linker-provided symbols. No persistent state.

Dependencies and integration points: depends on the compressed boot Makefile, linker script symbols, optional debug UART backends, architecture byte-order/libgcc replacement helpers, and kernel decompressor interfaces.

Risks and test signals: failures are usually pre-kernel and hard to diagnose. Test by building all compression modes, enabling early compressed boot debug where supported, checking image load addresses, and booting on boards that use each UART/debug path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/uart-alchemy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/uart-ath79.c -->
# sources/distributed-fs/ceph-client/arch/mips/boot/compressed/uart-ath79.c

Purpose: MIPS compressed-kernel boot support file `uart-ath79.c`. It provides either decompressor build rules, tiny C runtime helpers, UART debug output, or low-level entry code needed before the full kernel is decompressed.

Important APIs and functions: visible functions or entry points include assembly entry/build-time declarations. The file is compiled into the self-extracting boot image with minimal library support.

Control flow: firmware jumps into the compressed image entry code, the decompressor runtime initializes enough state for debug I/O and memory operations, calls the selected decompression backend, then jumps to the decompressed kernel address.

State and persistence: uses only early boot memory, scratch buffers, UART registers, and linker-provided symbols. No persistent state.

Dependencies and integration points: depends on the compressed boot Makefile, linker script symbols, optional debug UART backends, architecture byte-order/libgcc replacement helpers, and kernel decompressor interfaces.

Risks and test signals: failures are usually pre-kernel and hard to diagnose. Test by building all compression modes, enabling early compressed boot debug where supported, checking image load addresses, and booting on boards that use each UART/debug path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/uart-ath79.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/uart-prom.c -->
# sources/distributed-fs/ceph-client/arch/mips/boot/compressed/uart-prom.c

Purpose: MIPS compressed-kernel boot support file `uart-prom.c`. It provides either decompressor build rules, tiny C runtime helpers, UART debug output, or low-level entry code needed before the full kernel is decompressed.

Important APIs and functions: visible functions or entry points include putc. The file is compiled into the self-extracting boot image with minimal library support.

Control flow: firmware jumps into the compressed image entry code, the decompressor runtime initializes enough state for debug I/O and memory operations, calls the selected decompression backend, then jumps to the decompressed kernel address.

State and persistence: uses only early boot memory, scratch buffers, UART registers, and linker-provided symbols. No persistent state.

Dependencies and integration points: depends on the compressed boot Makefile, linker script symbols, optional debug UART backends, architecture byte-order/libgcc replacement helpers, and kernel decompressor interfaces.

Risks and test signals: failures are usually pre-kernel and hard to diagnose. Test by building all compression modes, enabling early compressed boot debug where supported, checking image load addresses, and booting on boards that use each UART/debug path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/compressed/uart-prom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/boot/dts/Makefile

Purpose: device-tree build manifest for the `dts` MIPS platform family. It tells Kbuild which DTB artifacts to build when the corresponding platform Kconfig symbols are enabled.

Important APIs and functions: this is declarative Kbuild data, not C code. Key entries are `subdir-y	+= brcm; subdir-y	+= cavium-octeon; subdir-y	+= econet; subdir-y	+= mobileye; subdir-y	+= img; subdir-y	+= ingenic; subdir-y	+= lantiq; subdir-y	+= loongson`.

Control flow: during a kernel build, `arch/mips/boot/dts/Makefile` descends into this directory and Kbuild expands the `dtb-$()` assignments for enabled configs. The resulting `.dtb` files are compiled from sibling DTS sources and may be packaged into images by higher-level boot rules.

State and persistence: no runtime state. It only affects generated build artifacts. Listed DTBs include the platform DTBs selected by the Makefile.

Dependencies and integration points: depends on Kconfig symbols, DTS source files in the same vendor directory, the device-tree compiler, and the MIPS boot image build.

Risks and test signals: a missing or mis-gated DTB prevents board images from containing the expected hardware description. Test with `make dtbs`, build logs for enabled symbols, and booting the resulting DTB on matching hardware or QEMU where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/brcm/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/boot/dts/brcm/Makefile

Purpose: device-tree build manifest for the `brcm` MIPS platform family. It tells Kbuild which DTB artifacts to build when the corresponding platform Kconfig symbols are enabled.

Important APIs and functions: this is declarative Kbuild data, not C code. Key entries are `dtb-$(CONFIG_DT_BCM93384WVG)		+= bcm93384wvg.dtb; dtb-$(CONFIG_DT_BCM93384WVG_VIPER)	+= bcm93384wvg_viper.dtb; dtb-$(CONFIG_DT_BCM96368MVWG)		+= bcm96368mvwg.dtb; dtb-$(CONFIG_DT_BCM9EJTAGPRB)		+= bcm9ejtagprb.dtb; dtb-$(CONFIG_DT_BCM97125CBMB)		+= bcm97125cbmb.dtb; dtb-$(CONFIG_DT_BCM97346DBSMB)		+= bcm97346dbsmb.dtb; dtb-$(CONFIG_DT_BCM97358SVMB)		+= bcm97358svmb.dtb; dtb-$(CONFIG_DT_BCM97360SVMB)		+= bcm97360svmb.dtb`.

Control flow: during a kernel build, `arch/mips/boot/dts/Makefile` descends into this directory and Kbuild expands the `dtb-$()` assignments for enabled configs. The resulting `.dtb` files are compiled from sibling DTS sources and may be packaged into images by higher-level boot rules.

State and persistence: no runtime state. It only affects generated build artifacts. Listed DTBs include bcm93384wvg.dtb, bcm93384wvg_viper.dtb, bcm96368mvwg.dtb, bcm9ejtagprb.dtb, bcm97125cbmb.dtb, bcm97346dbsmb.dtb, bcm97358svmb.dtb, bcm97360svmb.dtb, bcm97362svmb.dtb, bcm97420c.dtb, bcm97425svmb.dtb, bcm97435svmb.dtb.

Dependencies and integration points: depends on Kconfig symbols, DTS source files in the same vendor directory, the device-tree compiler, and the MIPS boot image build.

Risks and test signals: a missing or mis-gated DTB prevents board images from containing the expected hardware description. Test with `make dtbs`, build logs for enabled symbols, and booting the resulting DTB on matching hardware or QEMU where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/brcm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/cavium-octeon/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/boot/dts/cavium-octeon/Makefile

Purpose: device-tree build manifest for the `cavium-octeon` MIPS platform family. It tells Kbuild which DTB artifacts to build when the corresponding platform Kconfig symbols are enabled.

Important APIs and functions: this is declarative Kbuild data, not C code. Key entries are `dtb-$(CONFIG_CAVIUM_OCTEON_SOC)	+= octeon_3xxx.dtb octeon_68xx.dtb`.

Control flow: during a kernel build, `arch/mips/boot/dts/Makefile` descends into this directory and Kbuild expands the `dtb-$()` assignments for enabled configs. The resulting `.dtb` files are compiled from sibling DTS sources and may be packaged into images by higher-level boot rules.

State and persistence: no runtime state. It only affects generated build artifacts. Listed DTBs include octeon_3xxx.dtb, octeon_68xx.dtb.

Dependencies and integration points: depends on Kconfig symbols, DTS source files in the same vendor directory, the device-tree compiler, and the MIPS boot image build.

Risks and test signals: a missing or mis-gated DTB prevents board images from containing the expected hardware description. Test with `make dtbs`, build logs for enabled symbols, and booting the resulting DTB on matching hardware or QEMU where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/cavium-octeon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/econet/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/boot/dts/econet/Makefile

Purpose: device-tree build manifest for the `econet` MIPS platform family. It tells Kbuild which DTB artifacts to build when the corresponding platform Kconfig symbols are enabled.

Important APIs and functions: this is declarative Kbuild data, not C code. Key entries are `dtb-$(CONFIG_DTB_ECONET_SMARTFIBER_XP8421_B)	+= en751221_smartfiber_xp8421-b.dtb`.

Control flow: during a kernel build, `arch/mips/boot/dts/Makefile` descends into this directory and Kbuild expands the `dtb-$()` assignments for enabled configs. The resulting `.dtb` files are compiled from sibling DTS sources and may be packaged into images by higher-level boot rules.

State and persistence: no runtime state. It only affects generated build artifacts. Listed DTBs include en751221_smartfiber_xp8421-b.dtb.

Dependencies and integration points: depends on Kconfig symbols, DTS source files in the same vendor directory, the device-tree compiler, and the MIPS boot image build.

Risks and test signals: a missing or mis-gated DTB prevents board images from containing the expected hardware description. Test with `make dtbs`, build logs for enabled symbols, and booting the resulting DTB on matching hardware or QEMU where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/econet/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/img/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/boot/dts/img/Makefile

Purpose: device-tree build manifest for the `img` MIPS platform family. It tells Kbuild which DTB artifacts to build when the corresponding platform Kconfig symbols are enabled.

Important APIs and functions: this is declarative Kbuild data, not C code. Key entries are `dtb-$(CONFIG_FIT_IMAGE_FDT_BOSTON)	+= boston.dtb; dtb-$(CONFIG_FIT_IMAGE_FDT_MARDUK)	+= pistachio_marduk.dtb`.

Control flow: during a kernel build, `arch/mips/boot/dts/Makefile` descends into this directory and Kbuild expands the `dtb-$()` assignments for enabled configs. The resulting `.dtb` files are compiled from sibling DTS sources and may be packaged into images by higher-level boot rules.

State and persistence: no runtime state. It only affects generated build artifacts. Listed DTBs include boston.dtb, pistachio_marduk.dtb.

Dependencies and integration points: depends on Kconfig symbols, DTS source files in the same vendor directory, the device-tree compiler, and the MIPS boot image build.

Risks and test signals: a missing or mis-gated DTB prevents board images from containing the expected hardware description. Test with `make dtbs`, build logs for enabled symbols, and booting the resulting DTB on matching hardware or QEMU where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/img/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/ingenic/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/boot/dts/ingenic/Makefile

Purpose: device-tree build manifest for the `ingenic` MIPS platform family. It tells Kbuild which DTB artifacts to build when the corresponding platform Kconfig symbols are enabled.

Important APIs and functions: this is declarative Kbuild data, not C code. Key entries are `dtb-$(CONFIG_JZ4740_QI_LB60)	+= qi_lb60.dtb; dtb-$(CONFIG_JZ4740_RS90)	+= rs90.dtb; dtb-$(CONFIG_JZ4770_GCW0)	+= gcw0.dtb; dtb-$(CONFIG_JZ4780_CI20)	+= ci20.dtb; dtb-$(CONFIG_X1000_CU1000_NEO)	+= cu1000-neo.dtb; dtb-$(CONFIG_X1830_CU1830_NEO)	+= cu1830-neo.dtb`.

Control flow: during a kernel build, `arch/mips/boot/dts/Makefile` descends into this directory and Kbuild expands the `dtb-$()` assignments for enabled configs. The resulting `.dtb` files are compiled from sibling DTS sources and may be packaged into images by higher-level boot rules.

State and persistence: no runtime state. It only affects generated build artifacts. Listed DTBs include qi_lb60.dtb, rs90.dtb, gcw0.dtb, ci20.dtb, cu1000-neo.dtb, cu1830-neo.dtb.

Dependencies and integration points: depends on Kconfig symbols, DTS source files in the same vendor directory, the device-tree compiler, and the MIPS boot image build.

Risks and test signals: a missing or mis-gated DTB prevents board images from containing the expected hardware description. Test with `make dtbs`, build logs for enabled symbols, and booting the resulting DTB on matching hardware or QEMU where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/ingenic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/lantiq/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/boot/dts/lantiq/Makefile

Purpose: device-tree build manifest for the `lantiq` MIPS platform family. It tells Kbuild which DTB artifacts to build when the corresponding platform Kconfig symbols are enabled.

Important APIs and functions: this is declarative Kbuild data, not C code. Key entries are `dtb-$(CONFIG_DT_EASY50712)	+= danube_easy50712.dtb`.

Control flow: during a kernel build, `arch/mips/boot/dts/Makefile` descends into this directory and Kbuild expands the `dtb-$()` assignments for enabled configs. The resulting `.dtb` files are compiled from sibling DTS sources and may be packaged into images by higher-level boot rules.

State and persistence: no runtime state. It only affects generated build artifacts. Listed DTBs include danube_easy50712.dtb.

Dependencies and integration points: depends on Kconfig symbols, DTS source files in the same vendor directory, the device-tree compiler, and the MIPS boot image build.

Risks and test signals: a missing or mis-gated DTB prevents board images from containing the expected hardware description. Test with `make dtbs`, build logs for enabled symbols, and booting the resulting DTB on matching hardware or QEMU where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/lantiq/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/loongson/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/boot/dts/loongson/Makefile

Purpose: device-tree build manifest for the `loongson` MIPS platform family. It tells Kbuild which DTB artifacts to build when the corresponding platform Kconfig symbols are enabled.

Important APIs and functions: this is declarative Kbuild data, not C code. Key entries are `ifneq ($(CONFIG_BUILTIN_DTB_NAME),); dtb-y	:= $(addsuffix .dtb, $(CONFIG_BUILTIN_DTB_NAME)); else; dtb-$(CONFIG_MACH_LOONGSON64)	+= loongson64_2core_2k1000.dtb; dtb-$(CONFIG_MACH_LOONGSON64)	+= loongson64c_4core_ls7a.dtb; dtb-$(CONFIG_MACH_LOONGSON64)	+= loongson64c_4core_rs780e.dtb; dtb-$(CONFIG_MACH_LOONGSON64)	+= loongson64c_8core_rs780e.dtb; dtb-$(CONFIG_MACH_LOONGSON64)	+= loongson64g_4core_ls7a.dtb`.

Control flow: during a kernel build, `arch/mips/boot/dts/Makefile` descends into this directory and Kbuild expands the `dtb-$()` assignments for enabled configs. The resulting `.dtb` files are compiled from sibling DTS sources and may be packaged into images by higher-level boot rules.

State and persistence: no runtime state. It only affects generated build artifacts. Listed DTBs include loongson64_2core_2k1000.dtb, loongson64c_4core_ls7a.dtb, loongson64c_4core_rs780e.dtb, loongson64c_8core_rs780e.dtb, loongson64g_4core_ls7a.dtb, loongson64v_4core_virtio.dtb, cq-t300b.dtb, ls1b-demo.dtb, lsgz_1b_dev.dtb, smartloong-1c.dtb.

Dependencies and integration points: depends on Kconfig symbols, DTS source files in the same vendor directory, the device-tree compiler, and the MIPS boot image build.

Risks and test signals: a missing or mis-gated DTB prevents board images from containing the expected hardware description. Test with `make dtbs`, build logs for enabled symbols, and booting the resulting DTB on matching hardware or QEMU where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/loongson/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/mobileye/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/boot/dts/mobileye/Makefile

Purpose: device-tree build manifest for the `mobileye` MIPS platform family. It tells Kbuild which DTB artifacts to build when the corresponding platform Kconfig symbols are enabled.

Important APIs and functions: this is declarative Kbuild data, not C code. Key entries are `dtb-$(CONFIG_MACH_EYEQ5)		+= eyeq5-epm5.dtb; dtb-$(CONFIG_MACH_EYEQ6H)		+= eyeq6h-epm6.dtb; dtb-$(CONFIG_MACH_EYEQ6LPLUS)		+= eyeq6lplus-epm6.dtb`.

Control flow: during a kernel build, `arch/mips/boot/dts/Makefile` descends into this directory and Kbuild expands the `dtb-$()` assignments for enabled configs. The resulting `.dtb` files are compiled from sibling DTS sources and may be packaged into images by higher-level boot rules.

State and persistence: no runtime state. It only affects generated build artifacts. Listed DTBs include eyeq5-epm5.dtb, eyeq6h-epm6.dtb, eyeq6lplus-epm6.dtb.

Dependencies and integration points: depends on Kconfig symbols, DTS source files in the same vendor directory, the device-tree compiler, and the MIPS boot image build.

Risks and test signals: a missing or mis-gated DTB prevents board images from containing the expected hardware description. Test with `make dtbs`, build logs for enabled symbols, and booting the resulting DTB on matching hardware or QEMU where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/mobileye/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/mscc/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/boot/dts/mscc/Makefile

Purpose: device-tree build manifest for the `mscc` MIPS platform family. It tells Kbuild which DTB artifacts to build when the corresponding platform Kconfig symbols are enabled.

Important APIs and functions: this is declarative Kbuild data, not C code. Key entries are `dtb-$(CONFIG_SOC_VCOREIII)	+= \; jaguar2_pcb110.dtb \; jaguar2_pcb111.dtb \; jaguar2_pcb118.dtb \; luton_pcb091.dtb \; ocelot_pcb120.dtb \; ocelot_pcb123.dtb \; serval_pcb105.dtb \`.

Control flow: during a kernel build, `arch/mips/boot/dts/Makefile` descends into this directory and Kbuild expands the `dtb-$()` assignments for enabled configs. The resulting `.dtb` files are compiled from sibling DTS sources and may be packaged into images by higher-level boot rules.

State and persistence: no runtime state. It only affects generated build artifacts. Listed DTBs include jaguar2_pcb110.dtb, jaguar2_pcb111.dtb, jaguar2_pcb118.dtb, luton_pcb091.dtb, ocelot_pcb120.dtb, ocelot_pcb123.dtb, serval_pcb105.dtb, serval_pcb106.dtb.

Dependencies and integration points: depends on Kconfig symbols, DTS source files in the same vendor directory, the device-tree compiler, and the MIPS boot image build.

Risks and test signals: a missing or mis-gated DTB prevents board images from containing the expected hardware description. Test with `make dtbs`, build logs for enabled symbols, and booting the resulting DTB on matching hardware or QEMU where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/mscc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/mti/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/boot/dts/mti/Makefile

Purpose: device-tree build manifest for the `mti` MIPS platform family. It tells Kbuild which DTB artifacts to build when the corresponding platform Kconfig symbols are enabled.

Important APIs and functions: this is declarative Kbuild data, not C code. Key entries are `dtb-$(CONFIG_MIPS_MALTA)	+= malta.dtb; dtb-$(CONFIG_LEGACY_BOARD_SEAD3)	+= sead3.dtb`.

Control flow: during a kernel build, `arch/mips/boot/dts/Makefile` descends into this directory and Kbuild expands the `dtb-$()` assignments for enabled configs. The resulting `.dtb` files are compiled from sibling DTS sources and may be packaged into images by higher-level boot rules.

State and persistence: no runtime state. It only affects generated build artifacts. Listed DTBs include malta.dtb, sead3.dtb.

Dependencies and integration points: depends on Kconfig symbols, DTS source files in the same vendor directory, the device-tree compiler, and the MIPS boot image build.

Risks and test signals: a missing or mis-gated DTB prevents board images from containing the expected hardware description. Test with `make dtbs`, build logs for enabled symbols, and booting the resulting DTB on matching hardware or QEMU where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/mti/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/ni/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/boot/dts/ni/Makefile

Purpose: device-tree build manifest for the `ni` MIPS platform family. It tells Kbuild which DTB artifacts to build when the corresponding platform Kconfig symbols are enabled.

Important APIs and functions: this is declarative Kbuild data, not C code. Key entries are `dtb-$(CONFIG_FIT_IMAGE_FDT_NI169445)	+= 169445.dtb`.

Control flow: during a kernel build, `arch/mips/boot/dts/Makefile` descends into this directory and Kbuild expands the `dtb-$()` assignments for enabled configs. The resulting `.dtb` files are compiled from sibling DTS sources and may be packaged into images by higher-level boot rules.

State and persistence: no runtime state. It only affects generated build artifacts. Listed DTBs include 169445.dtb.

Dependencies and integration points: depends on Kconfig symbols, DTS source files in the same vendor directory, the device-tree compiler, and the MIPS boot image build.

Risks and test signals: a missing or mis-gated DTB prevents board images from containing the expected hardware description. Test with `make dtbs`, build logs for enabled symbols, and booting the resulting DTB on matching hardware or QEMU where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/ni/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/pic32/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/boot/dts/pic32/Makefile

Purpose: device-tree build manifest for the `pic32` MIPS platform family. It tells Kbuild which DTB artifacts to build when the corresponding platform Kconfig symbols are enabled.

Important APIs and functions: this is declarative Kbuild data, not C code. Key entries are `dtb-$(CONFIG_DTB_PIC32_MZDA_SK)		+= pic32mzda_sk.dtb; dtb-$(CONFIG_DTB_PIC32_NONE)		+= \; pic32mzda_sk.dtb`.

Control flow: during a kernel build, `arch/mips/boot/dts/Makefile` descends into this directory and Kbuild expands the `dtb-$()` assignments for enabled configs. The resulting `.dtb` files are compiled from sibling DTS sources and may be packaged into images by higher-level boot rules.

State and persistence: no runtime state. It only affects generated build artifacts. Listed DTBs include pic32mzda_sk.dtb, pic32mzda_sk.dtb.

Dependencies and integration points: depends on Kconfig symbols, DTS source files in the same vendor directory, the device-tree compiler, and the MIPS boot image build.

Risks and test signals: a missing or mis-gated DTB prevents board images from containing the expected hardware description. Test with `make dtbs`, build logs for enabled symbols, and booting the resulting DTB on matching hardware or QEMU where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/pic32/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/qca/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/boot/dts/qca/Makefile

Purpose: device-tree build manifest for the `qca` MIPS platform family. It tells Kbuild which DTB artifacts to build when the corresponding platform Kconfig symbols are enabled.

Important APIs and functions: this is declarative Kbuild data, not C code. Key entries are `dtb-$(CONFIG_ATH79)			+= ar9132_tl_wr1043nd_v1.dtb; dtb-$(CONFIG_ATH79)			+= ar9331_dpt_module.dtb; dtb-$(CONFIG_ATH79)			+= ar9331_dragino_ms14.dtb; dtb-$(CONFIG_ATH79)			+= ar9331_omega.dtb; dtb-$(CONFIG_ATH79)			+= ar9331_openembed_som9331_board.dtb; dtb-$(CONFIG_ATH79)			+= ar9331_tl_mr3020.dtb`.

Control flow: during a kernel build, `arch/mips/boot/dts/Makefile` descends into this directory and Kbuild expands the `dtb-$()` assignments for enabled configs. The resulting `.dtb` files are compiled from sibling DTS sources and may be packaged into images by higher-level boot rules.

State and persistence: no runtime state. It only affects generated build artifacts. Listed DTBs include ar9132_tl_wr1043nd_v1.dtb, ar9331_dpt_module.dtb, ar9331_dragino_ms14.dtb, ar9331_omega.dtb, ar9331_openembed_som9331_board.dtb, ar9331_tl_mr3020.dtb.

Dependencies and integration points: depends on Kconfig symbols, DTS source files in the same vendor directory, the device-tree compiler, and the MIPS boot image build.

Risks and test signals: a missing or mis-gated DTB prevents board images from containing the expected hardware description. Test with `make dtbs`, build logs for enabled symbols, and booting the resulting DTB on matching hardware or QEMU where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/qca/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/ralink/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/boot/dts/ralink/Makefile

Purpose: device-tree build manifest for the `ralink` MIPS platform family. It tells Kbuild which DTB artifacts to build when the corresponding platform Kconfig symbols are enabled.

Important APIs and functions: this is declarative Kbuild data, not C code. Key entries are `dtb-$(CONFIG_DTB_RT2880_EVAL)	+= rt2880_eval.dtb; dtb-$(CONFIG_DTB_RT305X_EVAL)	+= rt3052_eval.dtb; dtb-$(CONFIG_DTB_RT3883_EVAL)	+= rt3883_eval.dtb; dtb-$(CONFIG_DTB_MT7620A_EVAL)	+= mt7620a_eval.dtb; dtb-$(CONFIG_DTB_OMEGA2P)	+= omega2p.dtb; dtb-$(CONFIG_DTB_VOCORE2)	+= vocore2.dtb; dtb-$(CONFIG_SOC_MT7621) += \; mt7621-gnubee-gb-pc1.dtb \`.

Control flow: during a kernel build, `arch/mips/boot/dts/Makefile` descends into this directory and Kbuild expands the `dtb-$()` assignments for enabled configs. The resulting `.dtb` files are compiled from sibling DTS sources and may be packaged into images by higher-level boot rules.

State and persistence: no runtime state. It only affects generated build artifacts. Listed DTBs include rt2880_eval.dtb, rt3052_eval.dtb, rt3883_eval.dtb, mt7620a_eval.dtb, omega2p.dtb, vocore2.dtb, mt7621-gnubee-gb-pc1.dtb, mt7621-gnubee-gb-pc2.dtb, mt7621-tplink-hc220-g5-v1.dtb.

Dependencies and integration points: depends on Kconfig symbols, DTS source files in the same vendor directory, the device-tree compiler, and the MIPS boot image build.

Risks and test signals: a missing or mis-gated DTB prevents board images from containing the expected hardware description. Test with `make dtbs`, build logs for enabled symbols, and booting the resulting DTB on matching hardware or QEMU where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/ralink/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/realtek/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/boot/dts/realtek/Makefile

Purpose: device-tree build manifest for the `realtek` MIPS platform family. It tells Kbuild which DTB artifacts to build when the corresponding platform Kconfig symbols are enabled.

Important APIs and functions: this is declarative Kbuild data, not C code. Key entries are `dtb-$(CONFIG_MACH_REALTEK_RTL)	+= cisco_sg220-26.dtb; dtb-$(CONFIG_MACH_REALTEK_RTL)	+= cameo-rtl9302c-2x-rtl8224-2xge.dtb`.

Control flow: during a kernel build, `arch/mips/boot/dts/Makefile` descends into this directory and Kbuild expands the `dtb-$()` assignments for enabled configs. The resulting `.dtb` files are compiled from sibling DTS sources and may be packaged into images by higher-level boot rules.

State and persistence: no runtime state. It only affects generated build artifacts. Listed DTBs include cisco_sg220-26.dtb, cameo-rtl9302c-2x-rtl8224-2xge.dtb.

Dependencies and integration points: depends on Kconfig symbols, DTS source files in the same vendor directory, the device-tree compiler, and the MIPS boot image build.

Risks and test signals: a missing or mis-gated DTB prevents board images from containing the expected hardware description. Test with `make dtbs`, build logs for enabled symbols, and booting the resulting DTB on matching hardware or QEMU where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/realtek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/xilfpga/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/boot/dts/xilfpga/Makefile

Purpose: device-tree build manifest for the `xilfpga` MIPS platform family. It tells Kbuild which DTB artifacts to build when the corresponding platform Kconfig symbols are enabled.

Important APIs and functions: this is declarative Kbuild data, not C code. Key entries are `dtb-$(CONFIG_FIT_IMAGE_FDT_XILFPGA)	+= nexys4ddr.dtb`.

Control flow: during a kernel build, `arch/mips/boot/dts/Makefile` descends into this directory and Kbuild expands the `dtb-$()` assignments for enabled configs. The resulting `.dtb` files are compiled from sibling DTS sources and may be packaged into images by higher-level boot rules.

State and persistence: no runtime state. It only affects generated build artifacts. Listed DTBs include nexys4ddr.dtb.

Dependencies and integration points: depends on Kconfig symbols, DTS source files in the same vendor directory, the device-tree compiler, and the MIPS boot image build.

Risks and test signals: a missing or mis-gated DTB prevents board images from containing the expected hardware description. Test with `make dtbs`, build logs for enabled symbols, and booting the resulting DTB on matching hardware or QEMU where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/dts/xilfpga/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/ecoff.h -->
# sources/distributed-fs/ceph-client/arch/mips/boot/ecoff.h

Purpose: local ECOFF format definitions used by the MIPS `elf2ecoff` host conversion tool.

Important APIs and types: defines `FILHDR`, `SCNHDR`, and `AOUTHDR` structures plus ECOFF magic numbers, header sizes, section rounding, and offset macros such as `N_TXTOFF` and `N_DATOFF`.

Control flow: no executable control flow. `elf2ecoff.c` includes this header when constructing ECOFF headers from ELF load segments.

State and persistence: no runtime state; it describes on-disk binary layout emitted by the conversion utility.

Dependencies and integration points: depends on fixed-width integer types and historical MIPS ECOFF conventions.

Risks and test signals: structure layout or offset macro errors corrupt generated ECOFF images. Test by converting known ELF images, inspecting header fields, and booting firmware that consumes ECOFF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/ecoff.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/elf2ecoff.c -->
# sources/distributed-fs/ceph-client/arch/mips/boot/elf2ecoff.c

Purpose: host utility that converts a MIPS ELF kernel image into ECOFF format for firmware or boot paths that require ECOFF.

Important APIs and functions: `copy()` transfers file ranges. `combine()` merges adjacent/overlapping ELF load segments. `phcmp()` sorts program headers by virtual address. `saveRead()` reads checked file regions. Endian conversion helpers adjust ELF and ECOFF headers. `main()` parses input/output arguments, reads ELF headers/program headers, filters loadable segments plus MIPS metadata, computes ECOFF section/a.out headers, and writes the converted image.

Control flow: the tool opens the ELF, validates header shape, sorts program headers, combines text/data regions with padding/alignment, emits ECOFF file/header/section records, then copies segment payloads to their ECOFF offsets.

State and persistence: reads one input file and writes one output file. All conversion state is in process memory.

Dependencies and integration points: built as a host-side MIPS boot tool and depends on standard C/POSIX APIs, `<elf.h>`, network byte-order helpers, and local `ecoff.h` structures.

Risks and test signals: malformed ELF inputs, endian mismatch, segment overlap, and 32-bit size truncation can produce unbootable images. Test with known kernel ELF fixtures, `readelf`/hexdump inspection, firmware boot tests, and both big- and little-endian MIPS builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/elf2ecoff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/tools/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/boot/tools/Makefile

Purpose: Kbuild manifest controlling which objects or boot artifacts are built for `sources/distributed-fs/ceph-client/arch/mips/boot/tools/Makefile`.

Important APIs and functions: declarative build entries include `hostprogs	+= relocs; relocs-objs	+= relocs_32.o; relocs-objs	+= relocs_64.o; relocs-objs	+= relocs_main.o`. It does not define runtime APIs.

Control flow: Kbuild evaluates the assignments according to enabled `CONFIG_*` symbols and compiles or links the selected objects into the MIPS kernel, compressed image, host tools, or platform subdirectories.

State and persistence: no runtime state. Its only persistent effect is generated build output under the kernel build tree.

Dependencies and integration points: integrates this directory with the parent architecture Makefiles, host tool build rules, and relevant platform Kconfig symbols.

Risks and test signals: incorrect object selection causes missing platform hooks or broken boot artifacts. Test through configured kernel builds, `make V=1` command inspection, and ensuring expected objects/DTBs/host tools are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/tools/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/tools/relocs.c -->
# sources/distributed-fs/ceph-client/arch/mips/boot/tools/relocs.c

Purpose: shared implementation for the host `relocs` tool that scans MIPS ELF relocation sections, filters relocations relevant to kernel relocation, optionally removes relocation sections, and emits relocation offsets as text or binary.

Important APIs and functions: `regex_init()` builds skip filters, `read_ehdr/read_shdrs/read_strtabs/read_symtabs/read_relocs()` parse ELF metadata, `walk_relocs()` iterates relocation records with symbol context, `add_reloc()` stores accepted offsets, `emit_relocs()` writes sorted relocation entries, `do_reloc_info()` prints diagnostic information, and `remove_relocs()` rewrites relocation section headers out of the image. Byte-order macros and `ElfW` indirection make the file reusable for 32- and 64-bit builds.

Control flow: wrapper files define ELF width/type macros and include this file. The main program opens an ELF, reads all required sections, walks relocation sections, filters by relocation type and symbol, then either prints information, writes relocation offsets, or strips relocation sections.

State and persistence: maintains in-memory section, symbol, string table, and relocation lists; may modify the input/output ELF when stripping relocation sections depending on invocation flags.

Dependencies and integration points: included by `relocs_32.c` and `relocs_64.c`, driven by `relocs_main.c`, and used in MIPS compressed/relocatable kernel build tooling.

Risks and test signals: architecture-specific relocation encodings are subtle, especially MIPS64 RELA packed fields and endian conversion. Test by comparing emitted relocation tables for known 32/64-bit kernels, running `--reloc-info`, and booting relocated compressed kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/tools/relocs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/tools/relocs.h -->
# sources/distributed-fs/ceph-client/arch/mips/boot/tools/relocs.h

Purpose: host-side MIPS boot relocation tool component `relocs.h`.

Important APIs and functions: visible functions or definitions include die. The file helps build the `relocs` host program.

Control flow: Kbuild compiles the host tool, wrapper files select 32-bit or 64-bit ELF behavior, and `relocs_main.c` drives option parsing and relocation scanning/emission.

State and persistence: host process state only, except for generated relocation output or modified image files requested by the tool.

Dependencies and integration points: depends on host libc, `<elf.h>`, endian helpers, regex support, and the MIPS boot build pipeline.

Risks and test signals: broken host-tool parsing causes bad relocation tables and unbootable relocatable kernels. Test with 32/64-bit MIPS kernel images and compare emitted relocation lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/tools/relocs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/tools/relocs_32.c -->
# sources/distributed-fs/ceph-client/arch/mips/boot/tools/relocs_32.c

Purpose: host-side MIPS boot relocation tool component `relocs_32.c`.

Important APIs and functions: visible functions or definitions include ELF width macros and shared declarations. The file helps build the `relocs` host program.

Control flow: Kbuild compiles the host tool, wrapper files select 32-bit or 64-bit ELF behavior, and `relocs_main.c` drives option parsing and relocation scanning/emission.

State and persistence: host process state only, except for generated relocation output or modified image files requested by the tool.

Dependencies and integration points: depends on host libc, `<elf.h>`, endian helpers, regex support, and the MIPS boot build pipeline.

Risks and test signals: broken host-tool parsing causes bad relocation tables and unbootable relocatable kernels. Test with 32/64-bit MIPS kernel images and compare emitted relocation lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/tools/relocs_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/tools/relocs_64.c -->
# sources/distributed-fs/ceph-client/arch/mips/boot/tools/relocs_64.c

Purpose: host-side MIPS boot relocation tool component `relocs_64.c`.

Important APIs and functions: visible functions or definitions include ELF width macros and shared declarations. The file helps build the `relocs` host program.

Control flow: Kbuild compiles the host tool, wrapper files select 32-bit or 64-bit ELF behavior, and `relocs_main.c` drives option parsing and relocation scanning/emission.

State and persistence: host process state only, except for generated relocation output or modified image files requested by the tool.

Dependencies and integration points: depends on host libc, `<elf.h>`, endian helpers, regex support, and the MIPS boot build pipeline.

Risks and test signals: broken host-tool parsing causes bad relocation tables and unbootable relocatable kernels. Test with 32/64-bit MIPS kernel images and compare emitted relocation lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/tools/relocs_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/tools/relocs_main.c -->
# sources/distributed-fs/ceph-client/arch/mips/boot/tools/relocs_main.c

Purpose: host-side MIPS boot relocation tool component `relocs_main.c`.

Important APIs and functions: visible functions or definitions include die, usage, main. The file helps build the `relocs` host program.

Control flow: Kbuild compiles the host tool, wrapper files select 32-bit or 64-bit ELF behavior, and `relocs_main.c` drives option parsing and relocation scanning/emission.

State and persistence: host process state only, except for generated relocation output or modified image files requested by the tool.

Dependencies and integration points: depends on host libc, `<elf.h>`, endian helpers, regex support, and the MIPS boot build pipeline.

Risks and test signals: broken host-tool parsing causes bad relocation tables and unbootable relocatable kernels. Test with 32/64-bit MIPS kernel images and compare emitted relocation lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/boot/tools/relocs_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/Kconfig -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/Kconfig

Purpose: Kconfig menu for `sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/Kconfig`, exposing architecture configuration options for this MIPS platform area.

Important APIs and functions: declarative symbols include CAVIUM_CN63XXP1, CAVIUM_OCTEON_CVMSEG_SIZE, CAVIUM_OCTEON_LOCK_L2, CAVIUM_OCTEON_LOCK_L2_TLB, CAVIUM_OCTEON_LOCK_L2_EXCEPTION, CAVIUM_OCTEON_LOCK_L2_LOW_LEVEL_INTERRUPT, CAVIUM_OCTEON_LOCK_L2_INTERRUPT, CAVIUM_OCTEON_LOCK_L2_MEMCPY, CAVIUM_RESERVE32, OCTEON_ILM. Notable selected dependencies include none.

Control flow: `menuconfig` or defconfig resolution evaluates these symbols before build. Selected CPU/board/feature options control which source files, CPU support, and platform drivers Kbuild includes.

State and persistence: no runtime state. Values persist only in kernel `.config` and derived build artifacts.

Dependencies and integration points: integrates with top-level MIPS Kconfig, CPU capability symbols, board support choices, and Makefile `obj-$()` rules.

Risks and test signals: wrong dependencies can produce invalid builds or omit required CPU/platform support. Test by building representative defconfigs, checking symbol dependencies with `scripts/config` or `menuconfig`, and confirming selected objects match intended hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/Makefile

Purpose: Kbuild manifest controlling which objects or boot artifacts are built for `sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/Makefile`.

Important APIs and functions: declarative build entries include `obj-y := cpu.o setup.o octeon-platform.o octeon-irq.o csrc-octeon.o; obj-y += dma-octeon.o; obj-y += octeon-crypto.o; obj-y += octeon-memcpy.o; obj-y += executive/; obj-$(CONFIG_MTD)		      += flash_setup.o; obj-$(CONFIG_SMP)		      += smp.o; obj-$(CONFIG_OCTEON_ILM)	      += oct_ilm.o`. It does not define runtime APIs.

Control flow: Kbuild evaluates the assignments according to enabled `CONFIG_*` symbols and compiles or links the selected objects into the MIPS kernel, compressed image, host tools, or platform subdirectories.

State and persistence: no runtime state. Its only persistent effect is generated build output under the kernel build tree.

Dependencies and integration points: integrates this directory with the parent architecture Makefiles, host tool build rules, and relevant platform Kconfig symbols.

Risks and test signals: incorrect object selection causes missing platform hooks or broken boot artifacts. Test through configured kernel builds, `make V=1` command inspection, and ensuring expected objects/DTBs/host tools are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/cpu.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/cpu.c

Purpose: Cavium Octeon platform source `cpu.c`.

Important APIs and functions: key functions include cnmips_cu2_setup. It provides Octeon-specific CPU, timing, DMA, or executive services.

Control flow: selected by Octeon Kconfig/Makefile entries and invoked from MIPS architecture hooks or Octeon executive callers during boot and runtime.

State and persistence: modifies boot/runtime architecture state only: coprocessor notifier registration, timing constants, DMA translation callbacks, or bootmem-resident executive structures depending on the file.

Dependencies and integration points: includes/integrates with linux/init.h, linux/irqflags.h, linux/notifier.h, linux/prefetch.h, linux/ptrace.h, linux/sched.h, linux/sched/task_stack.h, asm/cop2.h, asm/current.h, asm/mipsregs.h; wider integration is with Octeon firmware data, CP0 registers, PCI/DMA, clocksource, SMP, and executive helper libraries.

Risks and test signals: hardware-generation assumptions are central. Test with Octeon defconfigs, SMP boot, clocksource stability, PCI/DMA I/O, and firmware bootmem behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/csrc-octeon.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/csrc-octeon.c

Purpose: Cavium Octeon clocksource, sched_clock, delay-loop, and CP0 CVMCOUNT setup.

Important APIs and functions: `octeon_setup_delays()` derives delay constants from the IO clock. `octeon_init_cvmcount()` synchronizes or initializes the per-core counter. `octeon_cvmcount_read()` feeds the clocksource. `sched_clock()` returns nanoseconds from CVMCOUNT. `plat_time_init()` registers the clocksource and MIPS clockevent frequency. `__udelay()`, `__ndelay()`, `__delay()`, and `octeon_io_clk_delay()` implement calibrated busy waits.

Control flow: platform time init establishes counter frequency, registers the continuous counter clocksource, and publishes delay calibration. Runtime reads are direct CP0 counter access with scaling.

State and persistence: updates global timing constants and the clocksource registration for the current boot. No persistent state.

Dependencies and integration points: depends on Octeon model/sysinfo data, CP0 CVMCOUNT, MIPS timekeeping, clocksource core, scheduler clock, and SMP synchronization.

Risks and test signals: frequency or synchronization errors break scheduler time, delay loops, and device timing. Test via clocksource selection logs, monotonic time checks across CPUs, delay calibration, network/storage timing, and suspend-free long-running uptime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/csrc-octeon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/dma-octeon.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/dma-octeon.c

Purpose: Octeon physical-to-DMA address translation and SWIOTLB setup for PCI generations and large memory layouts.

Important APIs and functions: `octeon_hole_phys_to_dma()` and `_dma_to_phys()` handle the platform memory hole. `octeon_gen1_*`, `octeon_gen2_*`, and `octeon_big_*` implement generation-specific DMA translation. `octeon_pci_dma_init()` selects translation mode from PCI type and memory layout. Exported `phys_to_dma()` and `dma_to_phys()` call the selected function pointers. `plat_swiotlb_setup()` reserves/initializes bounce buffering when needed.

Control flow: early boot chooses DMA translation callbacks based on Octeon PCI host mode and memory arrangement. Later DMA mapping code calls the exported translation hooks for devices.

State and persistence: global function pointers and SWIOTLB memory reservation are boot-time state. No disk persistence.

Dependencies and integration points: integrates Linux DMA direct mapping, memblock, SWIOTLB, PCI host setup, and Octeon NPI/PCI register definitions.

Risks and test signals: wrong translation corrupts DMA or makes PCI devices unusable above address windows. Test with PCI storage/network devices, high-memory DMA, SWIOTLB bounce stats, and data-integrity workloads under memory pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/dma-octeon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/Makefile

Purpose: Kbuild manifest controlling which objects or boot artifacts are built for `sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/Makefile`.

Important APIs and functions: declarative build entries include `obj-y += cvmx-bootmem.o cvmx-l2c.o cvmx-sysinfo.o octeon-model.o; obj-y += cvmx-pko.o cvmx-spi.o cvmx-cmd-queue.o \; obj-y += cvmx-helper-errata.o cvmx-helper-jtag.o cvmx-boot-vector.o`. It does not define runtime APIs.

Control flow: Kbuild evaluates the assignments according to enabled `CONFIG_*` symbols and compiles or links the selected objects into the MIPS kernel, compressed image, host tools, or platform subdirectories.

State and persistence: no runtime state. Its only persistent effect is generated build output under the kernel build tree.

Dependencies and integration points: integrates this directory with the parent architecture Makefiles, host tool build rules, and relevant platform Kconfig symbols.

Risks and test signals: incorrect object selection causes missing platform hooks or broken boot artifacts. Test through configured kernel builds, `make V=1` command inspection, and ensuring expected objects/DTBs/host tools are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-boot-vector.c -->
# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-boot-vector.c

Purpose: manages the Octeon boot vector table used to start secondary cores or provide firmware-visible boot entries.

Important APIs and functions: `cvmx_boot_vector_init()` initializes a 1024-entry vector table with code/data fields expected by Octeon firmware. `cvmx_boot_vector_get()` locates an existing named bootmem allocation or allocates/initializes one, then returns a typed pointer to the table.

Control flow: callers request the table lazily. The function first searches bootmem for the reserved block, allocates it with required alignment/size if absent, initializes entries, and returns the mapped pointer.

State and persistence: the vector table lives in Octeon bootmem for the current boot and may be shared with firmware/other CPUs. It is not persisted across power cycles.

Dependencies and integration points: depends on Octeon executive bootmem APIs and `cvmx_boot_vector` ABI structures. It integrates with SMP boot and low-level Octeon firmware handoff.

Risks and test signals: allocation failure or ABI mismatches can prevent secondary CPU startup. Test by verifying bootmem allocation logs, SMP bring-up, vector table contents, and behavior on systems with preexisting firmware-allocated tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-boot-vector.c -->
