# subset-b-000656 Research

This grouped report covers the exact source files assigned to `subset-b-000656`. Each file section is bounded by reconciliation markers so it can be split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/ts78xx-setup.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/ts78xx-setup.c

Purpose: board support for the Technologic Systems TS-78xx Orion5x SBC. It maps the FPGA register window, configures Orion5x core peripherals, and dynamically exposes FPGA-attached devices: M48T86 RTC, platform NAND, and timer-IOMEM RNG.

Important APIs and functions: `ts78xx_map_io()` extends `orion5x_map_io()` with an FPGA `map_desc`; `ts78xx_init()` configures MPP pins, EHCI, Ethernet, SATA, UARTs, XOR, then initializes FPGA devices and sysfs. NAND callbacks `ts78xx_ts_nand_cmd_ctrl()`, `*_dev_ready()`, `*_write_buf()`, and `*_read_buf()` translate Linux NAND operations to FPGA control/data registers and optimize aligned longword transfers. The sysfs attribute `ts78xx_fpga` uses `ts78xx_fpga_show()` and `ts78xx_fpga_store()` to report or toggle online/offline state.

Control flow: boot enters the `MACHINE_START(TS78XX)` hooks, maps Orion and FPGA IO, then `ts78xx_init()` calls `ts78xx_fpga_devices_zero_init()` and `ts78xx_fpga_load()`. Loading reads the FPGA ID, derives supported devices in `ts78xx_fpga_supports()`, and calls individual platform-device register helpers. Unloading verifies the FPGA ID did not change before deleting devices.

State and persistence: `static struct ts78xx_fpga_data ts78xx_fpga` persists FPGA ID, online state, device-present flags, and once-registered `init` bits. NAND partition layout is fixed in static MTD partitions; no runtime persistence beyond registered platform devices and sysfs state.

Dependencies and integration: depends on Orion5x machine helpers, Marvell Ethernet/SATA platform data, MTD NAND core, RTC, timeriomem RNG, sysfs `firmware_kobj`, and TS-78xx FPGA constants. It is ATAGS-era board code, not DT.

Risks and test signals: sysfs offline/online can race external `/dev/mem` FPGA reprogramming; mismatched FPGA ID marks state negative and requires power cycle. Device registration failures clear presence flags and return `-EBUSY` from FPGA load. Test with TS78xx boot logs, `/sys/firmware/ts78xx_fpga`, MTD partition discovery, RTC registration, RNG registration, and NAND read/write alignment paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/ts78xx-setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/tsx09-common.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/tsx09-common.c

Purpose: common support code for QNAP TS-x09 Orion5x NAS boards. It provides PIC-mediated poweroff and discovery of the Ethernet MAC address from a flash-resident NAS configuration area.

Important APIs and functions: `qnap_tsx09_power_off()` reprograms UART1 to 19200 8N1 and writes the PIC command byte `A`. `qnap_tsx09_eth_data` exports `mv643xx_eth_platform_data` with PHY address 8. MAC parsing is split across `qnap_tsx09_parse_hex_nibble()`, `qnap_tsx09_parse_hex_byte()`, and `qnap_tsx09_check_mac_addr()`. `qnap_tsx09_find_mac_addr()` scans a memory range in 1 KiB increments using `ioremap()`.

Control flow: board code calls `qnap_tsx09_find_mac_addr(mem_base, size)` with the flash partition bounds. Each mapped page is checked for strict `xx:xx:xx:xx:xx:xx\n` format; the first match copies six bytes into `qnap_tsx09_eth_data.mac_addr`. Poweroff is called through board-level `pm_power_off` style integration.

State and persistence: the MAC lives persistently in flash, but this file only reads it at init and stores it in static Ethernet platform data. Poweroff is a one-way hardware command through UART1 registers.

Dependencies and integration: uses Orion5x UART virtual base and `orion5x_tclk`, Linux PCI/Ethernet headers, `serial_reg.h` register offsets, and `mv643xx_eth`. It is shared by board files that provide flash ranges and install poweroff.

Risks and test signals: MAC scanning assumes a plaintext ext2 file appears at a 1 KiB-aligned offset and validates only the first bytes of each page. UART1 is hijacked during poweroff, so any active serial use is intentionally overridden. Test with boot log `tsx09: found ethernet mac address`, expected `eth_data.mac_addr`, and actual PIC shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/tsx09-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/tsx09-common.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/tsx09-common.h

Purpose: declaration header for QNAP TS-x09 common board support.

Important APIs/types: declares `qnap_tsx09_power_off()`, `qnap_tsx09_find_mac_addr(u32 mem_base, u32 size)`, and the exported `struct mv643xx_eth_platform_data qnap_tsx09_eth_data`.

Control flow and integration: board-specific TS-x09 setup files include this header to reuse the shared UART PIC poweroff path and MAC scan logic before registering Orion Ethernet.

State and persistence: this header owns no state; it exposes the platform-data object whose `mac_addr` may be filled from flash by the C file.

Dependencies: includes no external headers directly in this file, so consumers must already have or indirectly receive `u32` and `struct mv643xx_eth_platform_data` declarations.

Risks and test signals: compile coverage should catch missing type includes in consumers. Runtime test signals come from the C implementation: MAC log output and successful board poweroff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/tsx09-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/Kconfig

Purpose: Kconfig menu for Intel/Marvell PXA2xx/PXA3xx ARM platforms. It selects common CPU, GPIO, timer, power, and platform support, and gates DT and legacy ATAGS boards.

Important symbols: `ARCH_PXA` depends on `ARCH_MULTI_V5` and little endian and selects `PLAT_PXA`, `GPIO_PXA`, clocksource, and suspend support. DT machine symbols are `MACH_PXA25X_DT`, `MACH_PXA27X_DT`, and `MACH_PXA3XX_DT`. Legacy board symbols under `ATAGS` include `ARCH_GUMSTIX`, `GUMSTIX_AM200EPD`, `GUMSTIX_AM300EPD`, `PXA_SHARPSL`, and Zaurus variants. Internal SoC symbols include `PXA25x`, `PXA27x`, `PXA3xx`, `CPU_PXA300`, `CPU_PXA310`, and `CPU_PXA320`.

Control flow: this file does not execute; it shapes compilation. The DT options select SoC support and `USE_OF`; legacy board options select board files and dependent subsystems. The CPU symbols are selected by machines rather than usually presented directly.

State and persistence: build configuration persists in `.config`; no runtime state.

Dependencies and integration: consumed by `arch/arm/mach-pxa/Makefile`, SoC init code, and board files. It also selects external subsystems such as I2C, SPI, HWMON, APM emulation, and Sharp-specific platform components.

Risks and test signals: wrong selects can omit required init objects or include incompatible legacy board code. Test with representative defconfigs for DT PXA25x/PXA27x/PXA3xx and legacy Gumstix/Zaurus, checking that expected objects build and machine descriptors are registered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/Makefile

Purpose: build manifest for PXA machine support objects.

Important entries: always links `devices.o generic.o irq.o reset.o`; adds `pm.o sleep.o standby.o` under `CONFIG_PM`; selects SoC-specific objects for `PXA25x`, `PXA27x`, `PXA3xx`, `CPU_PXA300`, and `CPU_PXA320`; adds `pxa-dt.o` for DT machine symbols; adds legacy Gumstix and EPD files for their config symbols.

Control flow: link ordering matters. Common support is explicitly linked before board-specific support, which matches comments in `generic.c` and SoC files that rely on early default initcalls.

State and persistence: build-only; no runtime state.

Dependencies and integration: maps Kconfig symbols to object files. Some objects such as `smemc.o`, `sleep.o`, and Sharp board files are outside this subset but are part of the same architecture build.

Risks and test signals: object ordering and duplicate inclusion matter for weak carrier initializers and shared MFP objects. Build tests should cover `CONFIG_PXA25x`, `CONFIG_PXA27x`, `CONFIG_PXA3xx`, DT-only builds, and legacy Gumstix carrier choices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/addr-map.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/addr-map.h

Purpose: central physical and virtual address map constants for PXA chip selects and internal peripheral regions.

Important definitions: chip selects `PXA_CS0_PHYS` through `PXA_CS5_PHYS`, PXA300/PXA3xx CS variants, `PERIPH_PHYS/VIRT/SIZE`, static memory controller mapping `SMEMC_VIRT`, dynamic memory controller `DMEMC_VIRT`, NAND DFI bus `NAND_VIRT`, and internal memory controller `IMEMC_VIRT`.

Control flow: no runtime code; included by mapping and SoC headers to feed `iotable_init()` descriptors and direct IO macros.

State and persistence: none, but these constants define the persistent virtual layout expected by low-level PXA code.

Dependencies and integration: consumed by `generic.c`, `pxa25x.c`, `pxa27x.c`, `pxa3xx.c`, and SoC headers. It assumes `IOMEM()` is available through ARM headers.

Risks and test signals: incorrect ranges break early MMIO mapping, reset, timers, NAND, and memory-controller access. Test by booting each SoC family and validating early console, timer, IRQ, and NAND/SMEMC access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/addr-map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/am200epd.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/am200epd.c

Purpose: Gumstix AM200 EPD carrier support for a Metronome display controller attached to PXA25x GPIO and framebuffer memory.

Important APIs and functions: exposes `am200_init()` as the carrier hook called by `gumstix.c`. It registers a `metronomefb` platform device populated with `struct metronome_board`. Board callbacks include GPIO setup/cleanup, framebuffer setup, reset/standby controls, IRQ setup, wait functions, and panel type query. `panel_type` module parameter selects 6-inch, 8-inch, or 9.7-inch timing.

Control flow: `am200_init()` registers an FB notifier, configures PXA2xx MFP pins, requests the `metronomefb` module, allocates/adds the platform device, and calls `am200_presetup_fb()`. The notifier captures the host `pxafb` framebuffer when its adjusted geometry matches. Later `metronomefb` calls `am200_setup_fb()` to split the shared framebuffer into command, waveform, image, and checksum regions.

State and persistence: static `am200_board` stores host framebuffer pointers, waveform size, and panel dimensions; GPIO ownership and IRQ registration persist while the platform device exists. No nonvolatile storage.

Dependencies and integration: depends on Gumstix PXA25x board init, `pxa_set_fb_info()`, Linux framebuffer notifier chain, `metronomefb`, GPIO APIs, and PXA GPIO IRQ translation.

Risks and test signals: the notifier-based framebuffer sharing is marked FIXME and is fragile if another FB has matching geometry or if notifier ordering changes. Cleanup always frees RDY IRQ, so setup failure ordering matters. Test with panel sizes, FB registration/unregistration, RDY IRQ wakeups, and visible EPD update via `metronomefb`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/am200epd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/am300epd.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/am300epd.c

Purpose: Gumstix AM300 EPD carrier support for a Broadsheet display controller on PXA25x GPIOs, including a bit-banged 16-bit host data bus.

Important APIs and functions: exposes `am300_init()` as a carrier hook. It registers `broadsheetfb` platform data through `struct broadsheet_board`. Callbacks include `am300_init_board()`, `am300_cleanup()`, `am300_set_hdb()`, `am300_get_hdb()`, `am300_set_ctl()`, `am300_wait_event()`, `am300_get_panel_type()`, and `am300_setup_irq()`.

Control flow: `am300_init()` configures MFP pins, requests `broadsheetfb`, allocates a platform device, attaches a copy of the board callback table, and adds the device. Driver probe then calls board init, which requests control GPIOs plus GPIO58-73 for the data bus, sets initial output/input directions, resets the controller, and waits for RDY. IRQ setup binds RDY GPIO to a rising-edge interrupt.

State and persistence: static `am300_device` and `am300_board` persist after init; GPIO ownership, IRQ binding, and panel type parameter are runtime state. Data bus values are transient GPIO levels.

Dependencies and integration: depends on Gumstix carrier dispatch, PXA2xx MFP macros, GPIO, PXA IRQ mapping, and `broadsheetfb`.

Risks and test signals: `am300_wait_event()` waits without timeout, so missing RDY can hang probe/control operations. The DB request error label reuses loop state and should be tested for partial failures. Test with GPIO request failure injection, RDY IRQ, panel type parameter, and read/write correctness on the 16-bit HDB bus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/am300epd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/devices.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/devices.c

Purpose: central legacy platform-device catalog and registration helpers for PXA machines.

Important APIs and objects: `pxa_register_device()` assigns platform data and registers a `platform_device`. Setup helpers include `pxa_set_mci_info()`, UART info setters, `pxa_set_fb_info()`, `pxa_set_i2c_info()`, `pxa_set_ohci_info()`, `pxa2xx_set_dmac_info()`, and `pxa_register_wdt()`. Exported device objects cover PMU, MMC, UDC variants, framebuffer, FFUART/BTUART/STUART/HWUART, I2C, I2S, ASoC SSP/PCM, RTC, PWM, SSP, OHCI, GPIO, and DMA.

Control flow: SoC init files add arrays of these platform devices for non-DT boots. Board files call setters to register optional devices with board-specific platform data. `pxa_set_mci_info()` uses `platform_device_register_full()` so platform data and properties can be copied atomically. `pxa_register_wdt()` registers a `sa1100_wdt` resource over the OS timer and passes reset status.

State and persistence: static resources, DMA masks, and platform devices persist for the life of the kernel. Setters mutate `.dev.platform_data` and sometimes parent pointers before registration.

Dependencies and integration: relies on PXA IRQ constants, fixed physical addresses, platform data headers for MMC/I2C/OHCI/fb/UDC, GPIO wake helpers, and DMAengine slave maps from SoC files.

Risks and test signals: legacy static platform devices can only be registered once; repeated setters may fail. `pxa_set_hwuart_info()` silently ignores non-PXA255 hardware. Test with non-DT PXA25x/PXA27x boot, device tree boot not registering duplicates, platform resource ranges, and driver probes for expected devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/devices.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/devices.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/devices.h

Purpose: declaration header for the PXA legacy platform-device catalog.

Important APIs/types: declares exported `struct platform_device` instances from `devices.c`, `pxa_register_device()`, `pxa2xx_set_dmac_info()`, `pxa_set_i2c_info()`, PXA27x/PXA3xx power-I2C setters under config guards, and `PDMA_FILTER_PARAM()` for DMA slave maps.

Control flow and integration: SoC and board files include this header to register predefined device objects or to pass platform data into helper registration paths.

State and persistence: no state directly, but declarations point to static device objects with persistent registration state.

Dependencies: assumes platform-device, software-node, I2C platform data, and MMP DMA types are visible through included C files. Uses `PXAD_PRIO_*` and `struct pxad_param` via the DMA platform headers.

Risks and test signals: config guards must match definitions in `devices.c`; otherwise builds fail for selected SoCs. Test with all PXA config combinations and link checks for referenced platform devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/devices.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/generic.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/generic.c

Purpose: common PXA machine code for reset status, timer/clock initialization, SMEMC helpers, and base IO mapping.

Important APIs: `clear_reset_status()` dispatches to PXA2xx RCSR or PXA3xx ARSR semantics. `pxa_timer_init()` initializes clocks per CPU family and starts the non-DT PXA timer. `pxa_smemc_set_pcmcia_timing()`, `pxa_smemc_set_pcmcia_socket()`, and `pxa_smemc_get_mdrefr()` are exported for PCMCIA/static-memory users. `pxa_map_io()` maps the common peripheral window and initializes debug IO.

Control flow: machine descriptors call `pxa_map_io()` through SoC-specific wrappers, then legacy init paths call `pxa_timer_init()`. SMEMC helpers are invoked later by drivers.

State and persistence: writes memory-controller registers `MCMEM`, `MCATT`, `MCIO`, `MECR`, and reset status registers. The common IO mapping remains permanent.

Dependencies and integration: uses CPU detection helpers, PXA clock init functions, `clocksource/pxa.h`, SMEMC register definitions, and address-map constants.

Risks and test signals: direct register writes assume the correct SoC family and mapped windows. Test early boot timer interrupts, clock registration, PCMCIA timing on boards using sockets, and reset-status clearing across reboot paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/generic.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/generic.h

Purpose: internal PXA machine declarations shared by SoC, IRQ, DT, reset, and board files.

Important APIs/macros: declares map, timer, IRQ init, SoC map/init functions, `pxa_restart()`, syscore objects for IRQ and MFP suspend, UART info setters, and `pxa2xx_clear_reset_status()`. Defines `ARRAY_AND_SIZE()`, `SET_BANK()`, and handle-IRQ aliases for PXA25x, PXA27x, and PXA3xx.

Control flow and integration: machine descriptors and initcalls use these prototypes to wire boot hooks; syscore declarations are registered by SoC init.

State and persistence: header only; it exposes persistent syscore structures and reset functions implemented elsewhere.

Dependencies: includes `linux/reboot.h` and relies on `struct irq_data`.

Risks and test signals: macro aliases must track actual interrupt controller handlers. Compile all SoC variants and boot both DT and ATAGS paths to validate declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/gumstix.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/gumstix.c

Purpose: legacy ATAGS board support for Gumstix PXA255 motherboards.

Important APIs/functions: `gumstix_init()` configures MFP pins, registers UARTs, initializes Bluetooth, UDC VBUS, MMC, flash, and carrier boards. `gumstix_mmc_init()` registers `pxa2xx-mci`; `gumstix_udc_init()` registers `gpio-vbus` properties; `gumstix_bluetooth_init()` starts the 32 kHz oscillator if needed and toggles BT reset. Weak `am200_init()` and `am300_init()` allow carrier EPD files to override.

Control flow: `MACHINE_START(GUMSTIX)` routes boot to PXA25x mapping, IRQ, timer, and `gumstix_init()`. The init path configures pins then uses device helpers from `devices.c`; carrier init is last.

State and persistence: static flash partitions define bootloader and rootfs layout. GPIO reset state for Bluetooth and registered platform devices persist at runtime.

Dependencies and integration: depends on PXA25x SoC support, MFP pin macros, MTD CFI flash, MMC platform data, `gpio-vbus`, clock/OSCC registers, and optional AM200/AM300 carrier code.

Risks and test signals: carrier boards are not detected programmatically; selected carrier code always runs when built. The Bluetooth clock workaround depends on OSCC status. Test with Gumstix boot, UART probe, flash partitions, MMC card detection, USB VBUS GPIO behavior, Bluetooth reset, and selected carrier initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/gumstix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/gumstix.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/gumstix.h

Purpose: Gumstix board GPIO and IRQ definition header.

Important definitions: GPIOs for Bluetooth reset, USB VBUS/pullup, SD/MMC write-protect and detect, SMC Ethernet reset/IRQ, CompactFlash status/reset lines, and carrier hook prototypes `am200_init()` and `am300_init()`.

Control flow and integration: included by Gumstix board and carrier files to translate fixed board wiring into PXA GPIO numbers and IRQs via `PXA_GPIO_TO_IRQ()`.

State and persistence: header only; no state.

Dependencies: includes `irqs.h` for GPIO-to-IRQ mapping and relies on legacy GPIO direction flag macros.

Risks and test signals: incorrect GPIO constants break board IO and carrier operation. Test through Gumstix peripherals: USB cable detect, MMC detect, Ethernet IRQs, CF lines, and Bluetooth reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/gumstix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/irq.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/irq.c

Purpose: generic PXA internal interrupt-controller support for legacy and device-tree boot paths.

Important APIs/functions: `pxa_mask_irq()` and `pxa_unmask_irq()` manipulate ICMR bank bits. `icip_handle_irq()` handles PXA25x-style pending IRQ scanning; `ichp_handle_irq()` handles CP6 ICHP priority register delivery. `pxa_init_irq()` initializes non-DT controllers, while `pxa_dt_irq_init()` maps an OF interrupt controller. `pxa_irq_syscore` saves/restores interrupt masks and priority registers across suspend.

Control flow: SoC init calls `pxa_init_irq_common()`, which creates a legacy IRQ domain, disables all IRQs, sets all as IRQ not FIQ, enables idle wake only for unmasked interrupts, and attaches an optional wake callback. IRQ entry loops until no pending unmasked interrupt remains.

State and persistence: persistent globals include `pxa_irq_base`, internal IRQ count, priority-support flag, IRQ domain, saved ICMR/IPR arrays under PM, and the mutable irq-chip wake callback.

Dependencies and integration: used by PXA25x/PXA27x/PXA3xx SoC files, Linux IRQ domain/chip APIs, OF address parsing, and ARM exception entry.

Risks and test signals: wrong IRQ count or base mapping breaks all interrupts. PXA25x lacks IPR, while later CPUs use it. Test timer IRQ, GPIO cascade, suspend/resume mask restoration, OF property `marvell,intc-nr-irqs`, and wake-enabled interrupt behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/irqs.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/irqs.h

Purpose: PXA interrupt number map and IRQ helper declarations.

Important definitions: `PXA_IRQ(x)` offsets internal IRQs after legacy IRQs; names cover SSP, USB, GPIO, PMU, audio, LCD, I2C, UARTs, MMC, DMA, OS timer, RTC, PXA3xx peripherals, wakeup IRQs, and GPIO IRQ base. `PXA_GPIO_TO_IRQ(x)` maps built-in GPIOs after internal IRQs; `PXA_NR_IRQS` ends at `IRQ_BOARD_START`.

Control flow and integration: used by platform-device resource tables, SoC wake functions, GPIO IRQ code, and machine descriptors. Declares mask/unmask and IRQ entry functions implemented in `irq.c`.

State and persistence: none; this is a static ABI-like numbering contract for legacy PXA.

Dependencies: includes `asm/irq.h` for `NR_IRQS_LEGACY`.

Risks and test signals: overlapping symbolic IRQs reflect different SoC meanings, so consumers must use correct CPU guards. Test with all SoC builds and peripheral IRQ delivery for devices registered in `devices.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/irqs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa25x.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa25x.h

Purpose: PXA25x-specific multi-function pin configuration macros built on the PXA2xx MFP encoding.

Important definitions: GPIO aliases for pins 2-8, reset input, clock outputs, chip selects, DMA request lines, bus-master pins, PC Card pins, FFUART/BTUART/STUART/HWUART, FICP, PWM, AC97, I2S, SSP1/SSP2, MMC, and LCD data/control pins. Provides aggregate LCD macros `GPIOxx_LCD_16BPP`, `GPIOxx_LCD_DSTN_16BPP`, and `GPIOxx_LCD_TFT_16BPP`.

Control flow and integration: board files pass these macros to `pxa2xx_mfp_config()` to program GAFR, GPDR, PGSR, and wake-related registers.

State and persistence: header only; macro values encode run-mode function, direction, and low-power state that become persistent register state after configuration.

Dependencies: includes `mfp-pxa2xx.h` for `MFP_CFG_IN()` and `MFP_CFG_OUT()`.

Risks and test signals: wrong AF or direction can drive board lines incorrectly, especially memory bus and LCD outputs. Test with Gumstix pin setup, serial ports, MMC, LCD/EPD carriers, and suspend pin levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa25x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa27x.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa27x.h

Purpose: PXA27x-specific pin multiplexing macro catalog for the PXA2xx MFP framework.

Important definitions: GPIO85-120, clock/timer pins, memory and PC Card signals, I2C, UARTs, FICP, PWM, AC97 including warm-reset workaround GPIO configs, I2S, SSP1-3, MMC, LCD, keypad matrix, USB P2/P3/host, QCI camera, USIM, MSL, Memory Stick, and aggregate LCD macros. Declares `keypad_set_wake()`.

Control flow and integration: SoC and board code pass macros to `pxa2xx_mfp_config()`. `pxa27x_configure_ac97reset()` in `pxa27x.c` specifically uses AC97 reset macros from this header.

State and persistence: macro values become GAFR/GPDR/PGSR/wake register programming. Header itself has no state.

Dependencies: includes `mfp-pxa2xx.h`.

Risks and test signals: PXA27x has bidirectional special-function pins and power-I2C override behavior on GPIO3/4; incorrect configuration can conflict with controllers. Test with UART, AC97 warm reset, keypad wake, LCD, MMC, USB, and suspend/resume pin restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa27x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa2xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa2xx.c

Purpose: runtime MFP/pinmux configuration and low-power GPIO handling for PXA25x/PXA27x.

Important APIs/functions: `pxa2xx_mfp_config()` applies arrays of encoded pin configs; `pxa2xx_mfp_set_lpm()` changes only low-power state; `gpio_set_wake()` programs GPIO/keypad wake routing; `keypad_set_wake()` handles PXA27x keypad matrix wake bits. `pxa2xx_mfp_syscore` saves and restores GAFR, GPDR, GPLR, and PGSR across suspend.

Control flow: postcore init validates CPU family, initializes valid/wakeup GPIO descriptors, clears PSSR RDH, and seeds low-power GPDR state. Configuration writes alternate function registers, direction, low-power output states, and wake validation under local IRQ disable. Suspend copies keep-output states into PGSR, drives sleep levels, and updates directions; resume restores saved run registers.

State and persistence: static `gpio_desc[]` records per-pin validity, wake masks, mux masks, direction inversion, and last config. `gpdr_lpm[]` and saved register arrays preserve low-power and suspend state.

Dependencies and integration: used by legacy board files and PXA27x AC97 workaround. Depends on GPIO helpers, CPU detection, PXA2xx power/gpio registers, and syscore PM.

Risks and test signals: wake mux conflicts return `-EBUSY`; invalid pins warn and skip. Keep-output logic can affect power rails. Test pin config on PXA25x/PXA27x boards, GPIO wake from suspend, keypad wake, and resume restoration of GAFR/GPDR/GPLR/PGSR.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa2xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa2xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa2xx.h

Purpose: PXA2xx MFP encoding helpers and common GPIO pin macros.

Important APIs/macros: defines PXA2xx-specific direction bit, wakeup bit, keep-output bit, wake edge aliases, `MFP_CFG_IN()`, `MFP_CFG_OUT()`, and common `GPIOx_GPIO` input configs. Declares `pxa2xx_mfp_config()`, `pxa2xx_mfp_set_lpm()`, and `gpio_set_wake()`.

Control flow and integration: PXA25x/PXA27x pin headers build on these macros; board files submit generated values to `mfp-pxa2xx.c`.

State and persistence: header only; encoded values drive persistent hardware register programming when applied.

Dependencies: includes generic PXA MFP definitions from `linux/soc/pxa/mfp.h`.

Risks and test signals: output pins must specify safe low-power state; misuse can increase power or cause bus contention. Compile all board pin arrays and test suspend pin levels on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa2xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa300.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa300.h

Purpose: PXA300/PXA310 pin-function macro catalog for the PXA3xx MFP framework.

Important definitions: GPIO overrides, chip selects, AC97, I2C with pull-high low-power state, camera, keypad, LCD/mini-LCD, MMC1/MMC2/MMC3, SSP1-4, UART1-3, USB host/P2/P3/UTMI/ULPI, PWM, CIR, one-wire, data-flash ready, clocks, smart-card/USIM, and PXA310-only additions.

Control flow and integration: board or platform code uses these macros with `pxa3xx_mfp_config()`/`mfp_config()`. `pxa300.c` installs the address map that makes these logical pins resolve to MFPR offsets.

State and persistence: macros encode AF, drive strength, and low-power settings; runtime state exists only after applying them to MFPR registers.

Dependencies: includes `mfp-pxa3xx.h`; some sections are guarded by `CONFIG_CPU_PXA300` or `CONFIG_CPU_PXA310`.

Risks and test signals: PXA300/PXA310 pin address maps differ, so using macros before `mfp_init_addr()` or with wrong CPU config misprograms pins. Test pinmux users for camera, MMC, USB, UART, and keypad on both PXA300 and PXA310.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa300.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa320.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa320.h

Purpose: PXA320-specific pin-function macro catalog for PXA3xx MFP users.

Important definitions: PXA320 GPIO overrides, chip selects, AC97, I2C, camera/QCI, CIR/ICP/timer clocks, keypad matrix, LCD and mini-LCD, MMC1/MMC2, one-wire, SSP1-4, UART1-3, USB 2.0 UTMI, USB host/P2/P3, PC Card-style signals, and PWM outputs.

Control flow and integration: used by board code through `pxa3xx_mfp_config()`. `pxa320.c` registers the PXA320 MFPR address map used by these pin IDs.

State and persistence: header only; macro values become MFPR register contents when configured.

Dependencies: includes `mfp-pxa3xx.h`.

Risks and test signals: many pins offer multiple aliases; wrong macro can silently select the wrong alternate function. Test with PXA320 board peripherals, especially wake-related keypad/MMC/USB pins and LCD signal integrity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa320.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa3xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa3xx.c

Purpose: PXA3xx syscore suspend/resume glue for the generic PXA MFP subsystem.

Important APIs/objects: defines `pxa3xx_mfp_syscore`, whose PM callbacks call `mfp_config_lpm()` on suspend and `mfp_config_run()` on resume. Resume also clears `ASCR_RDH` while preserving write-one-to-clear D-state bits.

Control flow: PXA3xx SoC init registers this syscore object. During system suspend, pin low-power configurations are applied; on resume, run configurations are restored before receivers are re-enabled.

State and persistence: no local arrays; state is maintained by the shared `linux/soc/pxa/mfp` subsystem and PXA3xx power registers.

Dependencies and integration: depends on `mfp-pxa3xx.h`, `pxa3xx-regs.h`, syscore PM, and PXA3xx SoC init.

Risks and test signals: low-power pin configuration may not be appropriate for all suspend states, as noted by the FIXME. Test suspend/resume with active-low chip selects, wake pins, and post-resume peripheral operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa3xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa3xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa3xx.h

Purpose: common PXA3xx MFP definitions and thin compatibility wrappers.

Important definitions: `MFPR_BASE` and common `GPIOx_GPIO` macros for GPIO0-127 plus secondary GPIO pins. Inline wrappers `pxa3xx_mfp_read()`, `pxa3xx_mfp_write()`, and `pxa3xx_mfp_config()` delegate to the generic MFP API.

Control flow and integration: PXA300/PXA320 headers extend this file; SoC init maps MFPR base and address tables before board pin configuration.

State and persistence: no local state; MFPR state is external hardware programmed through generic MFP calls.

Dependencies: includes `linux/soc/pxa/mfp.h`.

Risks and test signals: wrapper comments discourage direct read/write in favor of config arrays. Test by applying common GPIO configs and validating MFPR contents via MFP helpers on PXA3xx.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa3xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp.h

Purpose: local compatibility include for PXA MFP definitions.

Important APIs/types: simply includes `linux/soc/pxa/mfp.h` under the legacy architecture include guard.

Control flow and integration: source files expecting the historical mach-level `mfp.h` can include this and receive the common SoC MFP definitions.

State and persistence: none.

Dependencies: depends entirely on `linux/soc/pxa/mfp.h`.

Risks and test signals: low risk; compile coverage verifies include path compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pm.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pm.c

Purpose: generic PXA platform suspend operations that dispatch to SoC-specific PM function tables.

Important APIs/functions: global `pxa_cpu_pm_fns` points to SoC PM callbacks. `pxa_pm_enter()` handles iWMMXt disable, optional register save, checksum validation, low-level enter, and restore. `pxa_pm_prepare()` and `pxa_pm_finish()` call optional SoC hooks. `pxa_pm_init()` allocates the save buffer and installs `platform_suspend_ops`.

Control flow: SoC init assigns `pxa_cpu_pm_fns`; `device_initcall(pxa_pm_init)` verifies it, allocates `sleep_save`, and registers suspend ops. On suspend, state validity and enter are delegated to SoC code.

State and persistence: static `sleep_save` persists after init. Checksum failure loops indefinitely re-entering the low-power state, waiting for hardware reset.

Dependencies and integration: depends on `pm.h`, Linux suspend core, and SoC implementations in `pxa25x.c`, `pxa27x.c`, or `pxa3xx.c`.

Risks and test signals: if no SoC function table is installed before device init, PM registration fails. Checksum detects corrupted sleep-save memory but recovery is hard reset only. Test `mem` and `standby` suspend per SoC, iWMMXt builds, and error paths for missing PM hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pm.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pm.h

Purpose: internal PXA PM function-table interface and low-level suspend symbol declarations.

Important types/APIs: `struct pxa_cpu_pm_fns` contains save/restore/valid/enter/prepare/finish callbacks and `save_count`. Declares `pxa_cpu_pm_fns`, low-level assembly helpers `pxa25x_finish_suspend()`, `pxa27x_finish_suspend()`, `pxa3xx_finish_suspend()`, generic PM functions, and standby code address symbols.

Control flow and integration: SoC files fill the table; `pm.c` consumes it. Assembly suspend code and SRAM-copied standby code are linked through these declarations.

State and persistence: no state except exported pointer declaration.

Dependencies: includes `linux/suspend.h`.

Risks and test signals: callback contract must match `save_count` and allocated buffer size. Test suspend entry for each SoC family and link coverage for assembly symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa-dt.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa-dt.c

Purpose: device-tree machine descriptors for PXA25x, PXA27x, and PXA3xx.

Important objects: `DT_MACHINE_START(PXA25X_DT)`, `DT_MACHINE_START(PXA27X_DT)`, and `DT_MACHINE_START(PXA_DT)` set map IO, restart, and compatible strings (`marvell,pxa250`, `marvell,pxa270`, `marvell,pxa300`, `marvell,pxa310`, `marvell,pxa320`).

Control flow: when a matching root compatible is present, ARM machine selection uses these descriptors. Interrupt and timer init are supplied by irqchip/DT timer infrastructure rather than explicit legacy fields here.

State and persistence: no runtime state beyond selected machine descriptor.

Dependencies and integration: depends on SoC-specific `*_map_io()` and common `pxa_restart()`. Enabled by Kconfig DT machine symbols.

Risks and test signals: compatible strings must match DTS files; missing init fields rely on OF subsystems. Test DT boot for each compatible with timer, IRQ, GPIO, and restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa-dt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa-regs.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa-regs.h

Purpose: core PXA virtual/physical IO translation and register access macros.

Important definitions: `UNCACHED_PHYS_0`, `io_v2p(x)`, `io_p2v(x)`, `__REG(x)`, `__REG2(x,y)`, and `__PREG(x)`. Comments document the legacy PXA internal register virtual map.

Control flow and integration: headers use `__REG` and `io_p2v` to define volatile MMIO register lvalues; mapping is established by `generic.c`.

State and persistence: no state, but macros define how all legacy direct register accesses resolve.

Dependencies: assumes ARM `IOMEM()` and `u32` availability.

Risks and test signals: wrong translation breaks essentially all PXA MMIO. Test early boot, timer, IRQ, GPIO, reset, and suspend paths that use direct register macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa25x.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa25x.c

Purpose: PXA21x/25x/26x SoC-specific init, IRQ wake, PM, IO mapping, default platform devices, and DMA slave map.

Important APIs/functions: `pxa25x_init_irq()` installs a 32-IRQ controller and `icip_handle_irq`; `pxa25x_map_io()` maps SMEMC and uncached alias regions and initializes clock frequency; PM callbacks save/restore `PSTR`, set `PSPR` resume address, and enter sleep via `pxa25x_finish_suspend()`. `pxa25x_set_wake()` routes GPIO0-84 to GPIO wake and RTC alarm to `PWER_RTC`.

Control flow: `postcore_initcall(pxa25x_init)` checks `cpu_is_pxa25x()`, registers watchdog reset status, installs PM hooks, registers IRQ/MFP syscore ops, and for non-DT boots registers GPIO software node, DMA controller info, and platform devices.

State and persistence: persistent PM table assignment, syscore registrations, platform devices, DMA slave map, and watchdog reset-status platform data. Sleep state uses `PSPR` and PXA power registers.

Dependencies and integration: depends on PXA2xx registers, MFP syscore, DMAengine, GPIO, reset, PM, SMEMC, and `devices.c`.

Risks and test signals: non-DT gating prevents duplicate devices under DT. Wake support is limited to hardware-supported GPIOs and RTC. Test PXA25x boot, DMA clients, UDC/RTC/SSP/PWM probes, suspend/resume, RTC wake, and watchdog reset-status reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa25x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa25x.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa25x.h

Purpose: umbrella header for PXA25x board and SoC code.

Important contents: includes address map, PXA2xx registers, PXA25x MFP macros, and IRQ definitions.

Control flow and integration: board files such as Gumstix and AM200 include this to gain SoC register and pin definitions.

State and persistence: none.

Dependencies: depends on included headers.

Risks and test signals: compile coverage validates include ordering and macro availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa25x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa27x-udc.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa27x-udc.h

Purpose: PXA27x USB device controller register and bit definitions.

Important definitions: UDC control/status registers (`UDCCR`, `UDCICR*`, `UDCISR*`, `UDCFNR`, `UDCOTGICR`, `UP2OCR`, `UP3OCR`), endpoint status registers `UDCCSR*`, byte-count registers `UDCBCR*`, data registers `UDCDR*`, endpoint configuration registers `UDCCR*`, and bit masks for OTG, interrupts, FIFO, endpoint type/direction, packet status, and byte-count limits.

Control flow and integration: no executable code; UDC driver code includes these macros to perform direct MMIO register operations.

State and persistence: hardware register values persist in the UDC until reset or driver reconfiguration.

Dependencies: includes `pxa-regs.h` and forbids simultaneous inclusion with PXA25x UDC support.

Risks and test signals: direct `__REG` access requires the PXA IO mapping. Incorrect bit masks cause USB enumeration or endpoint failures. Test USB gadget enumeration, endpoint interrupts, FIFO handling, OTG events, and build guard conflict with PXA25x UDC headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa27x-udc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa27x.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa27x.c

Purpose: PXA27x SoC-specific support for PM, IRQs, IO mapping, power-I2C, platform devices, DMA, and AC97/OTG quirks.

Important APIs/functions: `pxa27x_clear_otgph()` clears OTG peripheral hold; `pxa27x_configure_ac97reset()` switches AC97 reset pin between GPIO high and AC97 alternate function; `pxa27x_init_irq()` installs a 34-IRQ controller using `ichp_handle_irq`; `pxa27x_set_i2c_power_info()` enables `PCFR_PI2CEN` and registers power I2C. PM callbacks save MDREFR/PCFR/PSTR, clear FVC/PEDR/RCSR, support standby and mem sleep, and handle iWMMXt accumulator preservation.

Control flow: `postcore_initcall(pxa27x_init)` gates on `cpu_is_pxa27x()`, registers watchdog status, installs PM hooks and syscore ops, and registers legacy platform devices and DMA only when no DT is populated.

State and persistence: static PM `pwrmode`, DMA slave map, platform device arrays, syscore registrations, and power registers. Resume restores memory and power configuration.

Dependencies and integration: depends on PXA2xx MFP, keypad wake helper, DMAengine, GPIO, I2C, OHCI, UDC, ASoC, and `devices.c`.

Risks and test signals: AC97 warm reset workaround is GPIO-specific; power-I2C register updates are interrupt-protected but global. Test PXA27x boot, standby and mem suspend, keypad/USB/RTC wake, AC97 warm reset, power I2C probe, and DMA mappings for camera/I2S/SSP/MMC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa27x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa27x.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa27x.h

Purpose: umbrella PXA27x header with SoC-specific register definitions.

Important definitions: includes PXA2xx registers, PXA27x MFP macros, IRQs, and defines `ARB_CNTRL` plus bus arbiter park/lock bit masks.

Control flow and integration: included by PXA27x board and SoC code that need pin definitions or arbiter register access.

State and persistence: no local state; `ARB_CNTRL` macro accesses persistent hardware register state.

Dependencies: includes `linux/suspend.h`, address map, registers, MFP, and IRQ headers.

Risks and test signals: direct arbiter bit usage must be SoC-specific. Compile and runtime tests for PXA27x-only users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa27x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa2xx-regs.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa2xx-regs.h

Purpose: PXA2xx power-manager, clock, reset, and power-mode register definitions.

Important definitions: power manager registers `PMCR`, `PSSR`, `PSPR`, `PWER`, `PRER`, `PFER`, `PEDR`, `PCFR`, `PGSR*`, `RCSR`, sleep/standby/voltage registers, `PCMD*` voltage command registers, status/config bit masks, GPIO wake masks, RTC wake bit, clock registers `CCCR`, `CCSR`, `CKEN`, `OSCC`, and PWRMODE values.

Control flow and integration: SoC PM, reset, Gumstix Bluetooth clock, MFP suspend, and wake code use these macros for direct MMIO.

State and persistence: hardware power/clock/reset registers persist across runtime and some low-power transitions.

Dependencies: includes `pxa-regs.h`.

Risks and test signals: register bits often have write-one-to-clear or write-once semantics. Test suspend/resume, wake sources, reset status clearing, OSCC 32 kHz startup, and clock users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa2xx-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa2xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa2xx.c

Purpose: small PXA2xx-specific helpers for reset status and SDRAM row detection.

Important APIs/functions: `pxa2xx_clear_reset_status(mask)` writes RCSR with the shared reset-status mask. `pxa2xx_smemc_get_sdram_rows()` reads `MDCNFG`, inspects enabled SDRAM banks and DRAC fields, caches, and returns row count as `1 << (11 + max(drac0, drac2))`.

Control flow: reset code calls clear helper through `generic.c`; SMEMC users query SDRAM row geometry lazily.

State and persistence: `sdram_rows` static cache persists after first calculation. RCSR writes clear hardware reset causes.

Dependencies and integration: depends on PXA2xx register and SMEMC definitions and CPU-independent reset status constants.

Risks and test signals: SDRAM row cache assumes memory configuration does not change after first read. Test reset-status reporting/clearing and SMEMC row calculation on PXA25x/PXA27x memory configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa2xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa300.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa300.c

Purpose: PXA300/PXA310 MFPR address-map initialization.

Important APIs/data: `pxa300_mfp_addr_map[]` maps GPIO ranges and data-flash pins to MFPR offsets. `pxa310_mfp_addr_map[]` overrides or extends selected ranges and ULPI pins for PXA310. `pxa300_init()` calls `mfp_init_base()` and `mfp_init_addr()` when CPU detection matches.

Control flow: `core_initcall(pxa300_init)` runs early; PXA300/PXA310 get the base address and common map, then PXA310 receives extra overrides.

State and persistence: the generic MFP subsystem stores address mappings initialized from these static arrays.

Dependencies and integration: depends on CPU detection, `MFPR_BASE`, `mfp_init_base()`, `mfp_init_addr()`, and PXA3xx pin headers.

Risks and test signals: wrong offsets misprogram pin mux for all board code. Test MFP configuration on PXA300 and PXA310, especially GPIO ranges, NAND/data-flash pins, and ULPI/MMC3 PXA310 pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa300.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa300.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa300.h

Purpose: umbrella include for PXA300/PXA310 code.

Important contents: includes `pxa3xx.h` and `mfp-pxa300.h`.

Control flow and integration: used by PXA300 init and board code needing PXA300 pin definitions plus base PXA3xx support.

State and persistence: none.

Dependencies: included headers provide all functionality.

Risks and test signals: compile coverage for PXA300/PXA310 configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa300.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa320.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa320.c

Purpose: PXA320 MFPR address-map initialization.

Important APIs/data: `pxa320_mfp_addr_map[]` maps GPIO ranges, secondary GPIOs, NAND/data-flash pins, byte-enable/chip-select pins, and bus control pins to MFPR offsets. `pxa320_init()` initializes the MFP base and address map for PXA320 CPUs.

Control flow: `core_initcall(pxa320_init)` runs early and performs mapping only when `cpu_is_pxa320()`.

State and persistence: generic MFP address mapping persists in the MFP subsystem.

Dependencies and integration: depends on CPU detection, `MFPR_BASE`, generic MFP init helpers, and PXA320 pin header.

Risks and test signals: incorrect MFPR offsets break all PXA320 pinmux. Test MFP config for GPIO ranges, NAND/data-flash, LCD, MMC, USB, and keypad on PXA320.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa320.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa320.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa320.h

Purpose: umbrella include for PXA320 code.

Important contents: includes `pxa3xx.h` and `mfp-pxa320.h`.

Control flow and integration: used by PXA320-specific init and board code.

State and persistence: none.

Dependencies: included headers provide the SoC and MFP definitions.

Risks and test signals: compile coverage for `CONFIG_CPU_PXA320`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa320.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa3xx-regs.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa3xx-regs.h

Purpose: PXA3xx register definitions for oscillator, power managers, wake, power modes, and application clocks.

Important definitions: `OSCC`, MPMU registers `PMCR/PSR/PSPR/PCFR/PWER/PWSR/PECR/DCDCSR/PVCR/PCMD`, application subsystem registers `ASCR/ARSR/AD*ER/AD*SR/AD*R`, wake-source bit masks `ADXER_*`, D-state config bits `ADXR_*`, PXA3xx power mode constants, and clock registers `ACCR/ACSR/AICSR/CKENA/CKENB/CKENC/AC97_DIV`.

Control flow and integration: PXA3xx PM, reset, MFP resume, IRQ wake, and clock init code use these direct register definitions.

State and persistence: hardware registers persist across runtime and low-power transitions; some bits are write-one-to-clear.

Dependencies: includes `pxa-regs.h`.

Risks and test signals: power/wake bits are central to suspend; incorrect masks can prevent wake or corrupt resume. Test PXA3xx standby/mem suspend, wake-source setup, RDH clearing, clock enable behavior, and reset status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa3xx-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa3xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa3xx.c

Purpose: PXA3xx SoC support for PM, external wake IRQs, IO mapping, reset/watchdog status, and shared PXA3xx initialization.

Important APIs/functions: PM code maps ISRAM, copies standby code into SRAM, programs AD* wake registers, sets OBM resume handoff, and calls `pxa3xx_finish_suspend()`. `pxa3xx_set_wake()` maps internal IRQs to ADXER wake bits. External wakeup IRQ chip methods ack/mask/unmask/type through PECR/PWER plus internal IRQ masking. `pxa3xx_init_irq()` enables CP6 access and initializes wake IRQs.

Control flow: DT or legacy IRQ init calls `__pxa3xx_init_irq()` then `pxa_dt_irq_init()` or `pxa_init_irq()`. `postcore_initcall(pxa3xx_init)` gates on CPU family, registers watchdog status from ARSR, clears ASCR RDH/D-state bits, disables NAND DFI arbitration, initializes PM, enables wake IRQs, and registers IRQ/MFP syscore ops.

State and persistence: static `sram` mapping and `wakeup_src` bitmask persist. Power manager, ASCR, NAND NDCR, and clock registers are mutated during init and suspend.

Dependencies and integration: depends on IRQ core, PM assembly, generic MFP syscore, PXA clocks, `devices.c`, NAND address map, and CPU detection.

Risks and test signals: suspend refuses if no wake sources are configured. Resume protocol depends on OBM expectation at SDRAM base and PSPR value. Test PXA300/PXA310/PXA320 boot, external wake IRQ0/1, mem/standby suspend, NAND clock/arbitration behavior, and DFI bus stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa3xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa3xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa3xx.h

Purpose: umbrella header for PXA3xx SoC code.

Important contents: includes address map, PXA3xx registers, and IRQ definitions.

Control flow and integration: included by PXA300/PXA320 headers and SoC files needing shared PXA3xx definitions.

State and persistence: none.

Dependencies: included headers provide MMIO and IRQ definitions.

Risks and test signals: compile coverage for PXA3xx variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa3xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/regs-ost.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/regs-ost.h

Purpose: OS timer and watchdog register definitions for PXA.

Important definitions: physical resource `OST_PHYS/OST_LEN`, match registers `OSMR0-4`, counters `OSCR/OSCR4`, `OMCR4`, status `OSSR`, watchdog enable `OWER`, interrupt enable `OIER`, match status bits, watchdog match enable, and interrupt-enable bits.

Control flow and integration: reset code uses channel 3 as watchdog reset source; `devices.c` exposes the timer range to `sa1100_wdt`; timer code uses these registers through clocksource support.

State and persistence: timer counters and watchdog registers are hardware state.

Dependencies: includes `pxa-regs.h` for `io_p2v`.

Risks and test signals: watchdog reset path loops after arming OSMR3, so wrong timer rate or register mapping can hang. Test watchdog device probe, hard restart, and OS timer interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/regs-ost.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/regs-rtc.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/regs-rtc.h

Purpose: PXA real-time clock register and status bit definitions.

Important definitions: `RCNR`, `RTAR`, `RTSR`, `RTTR`, `PIAR`, periodic interrupt enable/status bits, HZ interrupt enable/status, and alarm enable/status bits.

Control flow and integration: RTC platform devices in `devices.c` expose the same resource range; RTC drivers use these register macros where direct mach access is needed.

State and persistence: RTC count/alarm/trim/status are hardware state, potentially battery-backed depending on board.

Dependencies: includes `pxa-regs.h`.

Risks and test signals: alarm and HZ status bits may require correct write-clear semantics in users. Test RTC read/set, alarm wake, periodic interrupt behavior, and resource registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/regs-rtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/reset.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/reset.c

Purpose: PXA restart support through soft restart, GPIO reset, or OS-timer watchdog reset.

Important APIs/functions: `init_gpio_reset()` requests and configures a reset GPIO. `pxa_restart()` disables IRQ/FIQ, clears reset status, and dispatches on reboot mode. `do_gpio_reset()` pulses the registered GPIO then falls back to hardware reset. `do_hw_reset()` arms the OS timer watchdog for roughly 100 ms and continuously writes `MDREFR_SLFRSH` to avoid the PXA270 SDRAM watchdog-reset erratum.

Control flow: machine descriptors set `.restart = pxa_restart`. Reboot paths invoke it with mode. GPIO reset requires prior `init_gpio_reset()` by board code; otherwise only hard/soft reset paths are safe.

State and persistence: static `reset_gpio` stores the registered reset line. Hardware reset status is cleared before restart; watchdog/timer and SDRAM refresh registers are mutated.

Dependencies and integration: depends on GPIO, ARM `soft_restart()`, OS timer registers, SMEMC `MDREFR`, and `clear_reset_status()`.

Risks and test signals: `REBOOT_GPIO` without initialization triggers `BUG_ON`. Hard reset intentionally never returns. Test soft restart, hard watchdog reset, GPIO reset board wiring, and PXA270 erratum path by observing successful reboot without SDRAM hang.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/reset.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/reset.h

Purpose: reset-status constants and reset helper declarations for PXA.

Important definitions/APIs: reset status bits for hardware, watchdog, low-power exit, GPIO reset, and all reset bits. Declares `clear_reset_status()`, `pxa_register_wdt()`, and `init_gpio_reset()`.

Control flow and integration: SoC and reset code use these constants to pass reset causes into watchdog platform data and clear hardware status before reboot.

State and persistence: no state directly; constants map to hardware RCSR/ARSR bits.

Dependencies: no external include requirements beyond C type basics.

Risks and test signals: bit mapping must remain 1:1 with both PXA2xx RCSR and PXA3xx ARSR expectations. Test reset-cause reporting after hardware, watchdog, sleep-exit, and GPIO resets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/reset.h -->
