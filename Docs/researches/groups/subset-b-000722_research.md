# Research Report: subset-b-000722

Grouped research for the requested MIPS platform source files. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/time.c -->
## sources/distributed-fs/ceph-client/arch/mips/alchemy/common/time.c

Purpose: implements Alchemy platform time initialization using the 32.768 kHz Counter1/RTC block as both a clocksource and a one-shot clock event source. If firmware did not enable the 32 kHz counter path or the counter registers do not become accessible, it falls back by disabling `cpu_wait`, forcing the kernel away from the wait-instruction idle path that depends on the low-power counter behavior.

Important APIs and functions: `plat_time_init()` is the exported architecture hook. It indexes `alchemy_m2inttab[]` by `alchemy_get_cputype()` and calls `alchemy_time_init()`. `au1x_counter1_read()` reads `AU1000_SYS_RTCREAD` for the clocksource. `au1x_rtcmatch2_set_next_event()` programs `AU1000_SYS_RTCMATCH2` after waiting for `SYS_CNTRL_M21` to clear. `au1x_rtcmatch2_irq()` dispatches the registered `clock_event_device` handler. The file defines static `clocksource` and `clock_event_device` descriptors with high ratings and 32-bit masks.

Control flow: initialization verifies `SYS_CNTRL_E0 | SYS_CNTRL_32S`, waits for trim/counter synchronization bits, writes `RTCTRIM` and `RTCWRITE`, registers the clocksource at 32768 Hz, computes clockevent mult/shift/min/max deltas, registers the device, and requests the CPU-specific RTC match2 interrupt with `IRQF_TIMER`.

State and persistence: state is hardware-register backed only. There is no filesystem persistence. The clockevent keeps its IRQ number and timing conversion fields in static kernel data. Counter register writes change SoC timing state until reset/suspend logic changes it.

Dependencies and integration: depends on Alchemy system register helpers, MIPS time hooks, Linux clocksource/clockevents, and CPU IDs from `au1000.h`. It integrates before normal timer use through `plat_time_init()` and with the interrupt subsystem through the match2 IRQ.

Risks: busy-wait loops can stall boot if register-ready bits are misreported; the code handles this by timeout except in match programming, which waits without timeout. Incorrect CPU type indexing would use the wrong RTC match interrupt. Firmware may report the 32 kHz-detected bit even if the clock is not actually reliable, which the comments explicitly warn about.

Test signals: boot logs should include `Alchemy clocksource installed` on working boards. Timer interrupt request failures emit an error. Functional tests are stable jiffies/clocksource selection, working one-shot timer events, and idle behavior without hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/usb.c -->
## sources/distributed-fs/ceph-client/arch/mips/alchemy/common/usb.c

Purpose: provides the Alchemy USB block power, clock, PHY, coherency, and suspend/resume abstraction for several CPU families. It hides differences between Au1000/Au1500/Au1100/Au1550 OHCI-only controllers, Au1200 combined OHCI/EHCI/UDC/OTG control, and Au1300 DWC-style USB control registers.

Important APIs and functions: `alchemy_usb_control(int block, int enable)` is exported and serializes all block changes with `alchemy_usb_lock`. CPU-specific helpers include `au1000_usb_init()`, `__au1xx0_ohci_control()`, `au1200_usb_control()`, `au1300_usb_control()`, and per-block Au1300 helpers for OHCI0/OHCI1/EHCI/UDC/OTG. `alchemy_usb_init()` is an `arch_initcall()` that initializes the relevant controller state and registers `syscore` PM operations. `alchemy_usb_suspend()` and `alchemy_usb_resume()` save and restore hardware routing/configuration.

Control flow: early init switches on `alchemy_get_cputype()`. Older chips validate a 48 MHz `usbh_clk`, set coherency/endian bits, and leave OHCI disabled until requested. Au1200 writes an all-access/coherent `USBCFG_INIT_AU1200` default. Au1300 disables interrupts/clocks, clears errors/status, and enables coherent SBUS access. Runtime control switches by USB block enum and sets clocks, enables PHYs, and masks/unmasks interrupt sources in documented order.

State and persistence: static `alchemy_usb_pmdata[2]` stores a small amount of register state across suspend. Hardware state persists until reset or PM restore. There is no durable storage.

Dependencies and integration: depends on Linux clock APIs, raw MMIO, syscore PM, Alchemy CPU IDs and physical address constants, and exported USB block IDs. USB host/device drivers call the exported control API before using controller MMIO.

Risks: most routines manipulate undocumented or timing-sensitive bits; missing barriers or delays would break enumeration. The older OHCI reset-done wait has no timeout. Au1300 port 2 routing is intentionally not autodetected, so boot firmware or board code must configure it. Shared PHY shutdown depends on correctly observing active clocks.

Test signals: successful init returns from `arch_initcall` and allows USB controller drivers to probe. Suspend/resume should preserve Au1200/Au1300 port routing. Runtime block enable/disable can be validated by OHCI/EHCI/UDC probe, disconnect/reconnect, and no AHB faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/vss.c -->
## sources/distributed-fs/ceph-client/arch/mips/alchemy/common/vss.c

Purpose: controls Au1300 media block power gating through VSS gate, clock/reset, and footer registers. The file is a temporary explicit power-management hook until the clock framework can own these transitions transparently.

Important APIs and functions: `au1300_vss_block_control(int block, int enable)` is exported. Internally `__enable_block()` and `__disable_block()` implement the databook-defined sequence for one block at a time. `VSS_ADDR(blk)` maps a block number to KSEG1 MMIO under `AU1300_VSS_PHYS_ADDR`.

Control flow: the public function returns immediately for non-Au1300 CPUs. On Au1300 it acquires `au1300_vss_lock`, then either enables the clock while reset is asserted, programs maximum gate setup time, enables footers in stages, starts the FSM, deasserts reset, and enables isolation cells; or reverses the process by disabling isolation cells, stopping the FSM, asserting reset, disabling clock, and clearing footers.

State and persistence: state is entirely in VSS hardware registers. The lock is static runtime state used for serialization; it is not persistent.

Dependencies and integration: depends on Alchemy CPU detection and raw MMIO access. Media drivers or platform code can call the exported symbol to power media blocks.

Risks: the sequence is order-sensitive and uses raw writes plus barriers without status polling, so incorrect block IDs or undocumented timing differences can leave a block inaccessible. The API silently no-ops on non-Au1300, which is convenient but can hide misrouted callers. There is no range validation for `block`.

Test signals: media block probe/use should succeed only after enabling the block. Suspend/resume or repeated enable/disable cycles should not wedge clocks or trigger bus errors. Kernel logs are absent, so tests must observe device behavior or register state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/common/vss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/Makefile

Purpose: selects the Alchemy development board support objects for the MIPS build. It always builds the shared CPLD, platform, and board-family setup files, and conditionally includes suspend support when `CONFIG_PM` is enabled.

Important build entries: `obj-y += bcsr.o platform.o db1000.o db1200.o db1300.o db1550.o db1xxx.o` ensures the board detection and device registration code is linked into the platform. `obj-$(CONFIG_PM) += pm.o` gates the DB1x suspend userspace interface.

Control flow: as a makefile, it has no runtime flow. Its ordering ensures `db1xxx.o` and the per-board implementations are linked together so `board_setup()`, `arch_initcall()`, and `device_initcall()` hooks from those objects are present.

State and persistence: none directly. It controls which object code contributes runtime global state.

Dependencies and integration: depends on Kbuild, the parent Alchemy machine selection, and `CONFIG_PM`. The listed objects integrate with arch setup, platform devices, PCI setup, PM, and CPLD helpers.

Risks: adding board files without updating this list would leave init functions unlinked. Removing `pm.o` from the PM gate would expose suspend sysfs without PM support, while missing `bcsr.o` would break almost all board files.

Test signals: a configured Alchemy devboard kernel should contain the expected init symbols and boot to board-specific device registration. PM builds should create the `/sys/power/db1x` interface from `pm.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/bcsr.c -->
## sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/bcsr.c

Purpose: abstracts DB/PB1xxx board CPLD registers, known as BCSR, and provides a cascaded CPLD interrupt controller for boards with interrupt-capable CPLDs. BCSR registers are 16-bit registers spaced on 32-bit boundaries and can reside in two physical windows.

Important APIs and functions: `bcsr_init()` maps register IDs to KSEG1 virtual addresses and initializes per-register spinlocks. `bcsr_read()`, `bcsr_write()`, and `bcsr_mod()` are exported for board files and drivers. `bcsr_init_irq()` installs a chained IRQ handler and maps a range of Linux IRQs to CPLD interrupt bits. Internal IRQ methods are `bcsr_irq_mask()`, `bcsr_irq_maskack()`, `bcsr_irq_unmask()`, and `bcsr_csc_handler()`.

Control flow: board setup calls `bcsr_init()` with board-specific BCSR physical base addresses. Later, DB1200/DB1300-style boards call `bcsr_init_irq()`, which masks/enables/acks all CPLD IRQs, assigns the `CPLD` irq chip to each cascaded line, and chains the parent GPIO IRQ to `bcsr_csc_handler()`. The handler reads `BCSR_REG_INTSTAT`, dispatches the first set bit with `generic_handle_irq()`, and exits the chained IRQ.

State and persistence: static `bcsr_regs[]` stores register addresses and locks. `bcsr_virt` and `bcsr_csc_base` record the active CPLD mapping and IRQ base. Hardware register changes persist until board reset.

Dependencies and integration: depends on `asm/mach-db1x00/bcsr.h`, raw I/O, Linux IRQ core, chained IRQ helpers, and board-specific setup files.

Risks: no bounds checks protect `enum bcsr_id`; callers must pass valid IDs. The chained handler dispatches only the lowest pending bit per parent interrupt entry. Wrong BCSR base addresses can corrupt unrelated external bus registers. IRQ ack/mask order is hardware-specific.

Test signals: BCSR read/write should identify the board through `BCSR_WHOAMI`; LEDs, resets, power bits, and card-detect signals should respond. Cascaded IRQ tests include MMC/card/PCMCIA insert and no stuck interrupt storm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/bcsr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/db1000.c -->
## sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/db1000.c

Purpose: supports DBAu1000/1500/1100 and PBAu1100/1500 boards. It detects the board through BCSR, sets up PCI on DB/PB1500, registers audio/LCD/MMC/SPI devices where applicable, configures PCMCIA sockets, and registers NOR flash.

Important APIs and functions: `db1000_board_setup()` initializes BCSR and validates `BCSR_WHOAMI`. `db1500_pci_setup()` registers an `alchemy-pci` platform device using `db1500_map_pci_irq()`. `db1000_dev_setup()` is the main device registration path. MMC support is behind `CONFIG_MMC_AU1X` and provides card-detect, readonly, power, and LED callbacks for two slots. DB1100 touchscreen SPI is registered through `spi_gpio` with software-node GPIO properties.

Control flow: device setup reads the board ID and selects IRQ/GPIO mappings, flash size, and socket count. DB1100 additionally requests SD card GPIOs, pinmuxes SSI0 pins as GPIOs, registers ADS7846 SPI info, adjusts the LCD clock parent to AUXPLL, and adds LCD/MMC devices. PB boards set special GPIO interrupt types and reduce to one PCMCIA socket. Shared audio devices are registered at the end, followed by NOR flash registration.

State and persistence: static platform device/resource tables describe hardware. BCSR bits control power, LEDs, and board resets. No durable filesystem state is written.

Dependencies and integration: depends on BCSR helpers, Alchemy GPIO/clock APIs, platform device core, PCMCIA/NOR helpers from `platform.c`, Au1100 MMC, SPI GPIO, AC97, LCD, and PCI platform drivers.

Risks: board ID branches carry many hard-coded GPIO/IRQ assumptions. The PB1500/PB1100 memory comments are informational only; unregistered devices may need separate support. MMC write-protect polarity differs between slots/boards. Several `gpio_request()` and device registration errors are not fatal or are only logged.

Test signals: boot log should identify the exact board. PCI probing on DB/PB1500, MMC insertion/removal, PCMCIA card interrupts, AC97 codec registration, LCD on DB1100/PB1100, SPI touchscreen, and MTD partitions are the main validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/db1000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/db1200.c -->
## sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/db1200.c

Purpose: supports DBAu1200 and PBAu1200 boards, including board detection, CPLD IRQ muxing, NAND/NOR/IDE/Ethernet/MMC/LCD/I2C/SPI/audio device registration, and switch-selected peripheral muxing.

Important APIs and functions: `db1200_board_setup()` calls `db1200_detect_board()` and prints CPLD/board/daughtercard IDs. `db1200_dev_setup()` configures IRQs, pinmux, clocks, board devices, PCMCIA sockets, and flash. NAND callbacks are `au1200_nand_cmd_ctrl()` and `au1200_nand_device_ready()`. MMC card-detect logic uses threaded IRQ pairs in `db1200_mmc_cd_setup()` and `pb1200_mmc1_cd_setup()`. `pb1200_res_fixup()` rewrites physical resource addresses for PB1200.

Control flow: detection first tries DB1200 BCSR, toggling HEXLEDs to prove the mapping, then tries PB1200. Device setup handles PB resource differences and rejects old PB CPLD revisions. It chains the CPLD interrupt line from GPIO7, marks insert/eject IRQs `IRQ_NOAUTOEN`, registers I2C/SPI board info, sets GPIO215 OTG VBUS according to PSC0 mode, chooses PSC0 I2C or SPI from DIP switch 8, chooses PSC1 I2S or AC97 from DIP switch 7 plus PSC0 mode, registers PCMCIA sockets, NOR flash, base DB devices, and optional PB second MMC.

State and persistence: static resource tables are mutated for PB1200 and for selected device names. BCSR controls power, LEDs, reset muxes, card status, and switch state. No persistent storage is modified beyond exposed MTD devices.

Dependencies and integration: uses BCSR/BCSR IRQ, Alchemy PSC, MMC, MTD NAND/physmap, SMC91x Ethernet, PATA platform, Au1200 framebuffer, I2C/SPI board info, and shared `db1x_register_*()` helpers.

Risks: DIP-switch driven muxing can make OTG unavailable in SPI mode by design. The CPLD insert/eject lines are known to be noisy, so the code relies on alternating IRQ enablement. Resource fixups mutate global tables before registration and must happen once. Old PB CPLDs are explicitly unreliable.

Test signals: boot should report board/CPLD IDs and selected PSC/audio modes. Validate CPLD IRQ cascade with SD/PCMCIA events, NAND partitions, SMC91x Ethernet, PATA probe, LCD power, I2C/SPI device discovery, and NOR partition order under swapboot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/db1200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/db1300.c -->
## sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/db1300.c

Purpose: initializes and registers devices for the NetLogic/Alchemy DBAu1300 development platform. It covers pin function setup, FPGA/CPLD interrupt muxing, NAND/Ethernet/IDE/MMC/LCD/audio/I2C/input devices, AC97 touchscreen pen IRQ support, PCMCIA/NOR flash, and USB power bits.

Important APIs and functions: `db1300_board_setup()` initializes BCSR, validates `BCSR_WHOAMI_DB1300`, configures multifunction pins, prints board metadata, and enables UARTs. `db1300_dev_setup()` sets up the CPLD IRQ cascade and registers platform devices. `db1300_gpio_config()` assigns pin groups to device or GPIO mode. NAND callbacks mirror the other devboards. MMC logic uses threaded insert/eject IRQs. `db1300_wm97xx_probe()` registers WM97xx touchscreen machine ops when enabled.

Control flow: board setup runs before device setup and creates pinmux prerequisites. Device setup maps the CPLD interrupt parent from `AU1300_PIN_EXTCLK1`, marks noisy insert/eject interrupts no-auto-enable, loads Ethernet MAC from PROM, registers I2C devices, registers the touchscreen helper driver, programs PSC1/PSC2 external codec clocks and PSC3 internal clock, enables USB host/OTG power in BCSR, registers one CF/PCMCIA socket, registers 64 MiB NOR flash with swapboot awareness, and adds the device array.

State and persistence: static device/resource tables describe peripherals. BCSR bits hold board power/reset/mux/LED/card status. The WM97xx driver registration is runtime state. No durable state is written.

Dependencies and integration: depends on Au1300 GPIO/pinmux, BCSR and BCSR IRQ support, platform devices, SMSC911x, PATA, MTD NAND, Au1x MMC, Au1200 framebuffer, PSC audio/I2C, WM97xx, PROM Ethernet address helper, and shared platform helpers.

Risks: pin assignment is large and hardware-specific; wrong ownership can break UART, LCD, PSC, SD, or PCMCIA. The moviNAND slot is explicitly disabled with `card_inserted` always false. AC97 touchscreen support depends on optional config and a platform driver side registration. Insert/eject IRQ storms are mitigated but still board-sensitive.

Test signals: board boot should print DB1300 IDs and expose UART0/1/2/3 as expected. Validate Ethernet MAC/probe, SD1 insertion, disabled SD0/moviNAND behavior, LCD panel index 9 with inverted power bits, five-way GPIO keys, audio devices, CF/PCMCIA, USB power, and NOR/NAND registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/db1300.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/db1550.c -->
## sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/db1550.c

Purpose: supports DBAu1550 and PBAu1550 boards. It detects BCSR layout, performs early pin and AC97 reset setup, registers NAND/SPI/I2C/audio/PCI/PCMCIA/NOR devices, and differentiates DB versus PB resource behavior.

Important APIs and functions: `db1550_board_setup()` detects DB1550 versus PB1550 SDR/DDR and reinitializes BCSR for the PB hex LED offset. `db1550_hw_setup()` configures PSC pin functions and asserts AC97 reset. `db1550_pci_setup(int id)` registers the PCI host and chooses `db1550_map_pci_irq()` or `pb1550_map_pci_irq()`. `db1550_dev_setup()` registers board devices. `pb1550_nand_setup()` derives NAND width from memory/BCSR boot-swap state.

Control flow: board setup initializes BCSR, validates board ID, prints IDs, and calls hardware setup. An `arch_initcall()` from `db1xxx.c` invokes PCI setup before MIPS PCI bus scanning. Device setup registers I2C/SPI board info, configures PSC clocks, selects DB or PB PCMCIA/NAND path, registers NOR flash with board-specific swapboot bit, and adds common PSC/audio devices. DB uses generic NAND and two sockets with separate card IRQs; PB uses shared GPIO201-205 card IRQs and the Au1550 NAND controller.

State and persistence: platform device/resource tables and board-specific platform data are static. `pb1550_nand_pd.devwidth` is fixed up at runtime. BCSR and GPIO state controls muxes, LEDs, flash bank order, and card IRQs.

Dependencies and integration: depends on Alchemy GPIO/PSC/DBDMA/PCI/NAND, BCSR, MTD, SPI flash, I2C board info, AC97/I2S platform audio, and shared PCMCIA/NOR helpers.

Risks: PSC clock setup has comments noting missing platform data and codec-supplied clocks. PB PCMCIA shares a line and intentionally ignores status-change IRQs. NAND width detection is based on boot strap combinations. PCI IRQ maps are slot/pin-specific and easy to regress.

Test signals: boot should identify DB1550 or PB1550, PCI devices should map correct INTx lines, SPI flash/temp sensor and I2C devices should probe, AC97 reset should be sufficient for codec registration, PCMCIA sockets should raise card IRQs, and NOR/NAND partition/device width should match the board.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/db1550.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/db1xxx.c -->
## sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/db1xxx.c

Purpose: central dispatcher for Alchemy DB/PB1xxx development boards. It maps CPU type and BCSR board ID to the correct per-board setup, PCI setup, and device registration functions, and supplies the machine name string.

Important APIs and functions: `board_setup()` is the early board initialization hook. `get_system_type()` returns the string from `board_type_str()`. `db1xxx_arch_init()` is an `arch_initcall()` that registers PCI for DB/PB1500 and DB/PB1550 variants. `db1xxx_dev_init()` is a `device_initcall()` that sets the MIPS machine name and calls the correct per-board device setup function.

Control flow: `board_setup()` switches on `alchemy_get_cputype()` and calls `db1000_board_setup()`, `db1550_board_setup()`, `db1200_board_setup()`, or `db1300_board_setup()`. Any failure panics because the board support package cannot safely continue without BCSR and board identification. Later initcalls read `BCSR_WHOAMI` and branch by board ID for PCI and platform-device registration.

State and persistence: this file owns no persistent state. It relies on BCSR state initialized by per-board setup and sets global kernel machine name through `mips_set_machine_name()`.

Dependencies and integration: depends on every per-board C file, BCSR IDs, Alchemy CPU detection, PROM declarations, and MIPS initcall ordering. It is the glue that makes object files listed in the Makefile participate in architecture boot.

Risks: unsupported or misdetected CPU/board IDs panic or skip device setup. `board_type_str()` depends on BCSR being initialized before `get_system_type()` is used. PCI setup must remain at `arch_initcall()` because MIPS PCI scanning happens during `subsys_initcall()`.

Test signals: boot should print the board name and set the machine name. PCI should appear only on supported DB/PB1500/1550 boards. Device init should call exactly one board-specific setup path, visible through registered platform devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/db1xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/platform.c -->
## sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/platform.c

Purpose: provides shared DB/PB1xxx platform utilities: early console character output, board power-off/reset hooks, RTC device registration, PCMCIA socket platform-device creation, and NOR flash/partition registration.

Important APIs and functions: `prom_putchar()` writes to UART2 on Au1300 and UART0 otherwise. `db1x_late_setup()` installs `_machine_restart`, `_machine_halt`, and `pm_power_off` callbacks and registers `rtc-au1xxx`. `db1x_register_pcmcia_socket()` allocates a `db1xxx_pcmcia` platform device with memory and IRQ resources. `db1x_register_norflash()` allocates a `physmap-flash` device and a five-partition layout around YAMON, raw kernel, and environment regions.

Control flow: late device init installs power/reset behavior and RTC. Board files call the PCMCIA helper with physical ranges and card/insert/status/eject IRQs; the helper conditionally adds optional resources and registers the device. NOR registration calculates a flash window ending at `0x20000000`, builds partitions differently depending on swapboot, fills `physmap_flash_data`, and registers the platform device.

State and persistence: allocations for resources, partitions, and platform data are intentionally retained after successful platform registration. BCSR writes in reset/power-off alter board hardware state. MTD partitions expose persistent flash regions but this code only describes them.

Dependencies and integration: depends on BCSR, Alchemy UART, MTD physmap, platform device core, MIPS reboot hooks, and board-specific calls from DB1000/1200/1300/1550 setup.

Risks: allocation failure paths must free partially allocated objects; successful paths intentionally leak to device lifetime. NOR partition math assumes YAMON placement and a minimum 8 MiB flash. Power-off loops in `cpu_wait()` indefinitely after BCSR writes.

Test signals: early printk should appear on the expected UART. `rtc-au1xxx`, `db1xxx_pcmcia`, and `physmap-flash` devices should register. MTD partition names/order should reflect swapboot, and poweroff/restart should assert the CPLD reset/system bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/platform.h -->
## sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/platform.h

Purpose: declares shared helper functions used by the Alchemy devboard source files. It keeps PCMCIA and NOR flash registration prototypes in one local header.

Important APIs and types: `db1x_register_pcmcia_socket()` takes attribute, memory, and I/O physical ranges plus card-detect/card/status/eject IRQs and a socket ID. `db1x_register_norflash()` takes total flash size, bus width, and swapboot state. Both are marked `__init`, matching their implementation and call sites.

Control flow: none in the header. It enables per-board setup files to call helpers implemented in `platform.c`.

State and persistence: none directly. The declared helpers create platform devices and MTD partition descriptors at runtime.

Dependencies and integration: includes `linux/init.h` for `__init` and relies on `phys_addr_t` being available through included kernel headers at call sites. It is included by DB1000/1200/1300/1550 platform setup code.

Risks: the prototype parameter name for `pcmcia_attr_end` is written as `pcmcia_attr_len`, while the implementation treats it as an end address. This is naming-only but can mislead future callers. Any signature drift from `platform.c` would break all board files at compile time.

Test signals: compile coverage is the primary signal. Runtime validation comes indirectly from PCMCIA and NOR flash platform devices registered by board files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/pm.c -->
## sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/pm.c

Purpose: provides an example suspend-to-RAM userspace interface for Alchemy development boards under `/sys/power/db1x`. It lets userspace enable GPIO and timer wake sources, configure a TOYMATCH2 wake timeout, and read the last wake source.

Important APIs and functions: `pm_init()` is a `late_initcall()` that initializes TOY trim/wake registers, installs `platform_suspend_ops`, and creates the sysfs attribute group. Suspend callbacks are `db1x_pm_begin()`, `db1x_pm_enter()`, and `db1x_pm_end()`. Sysfs uses `db1x_pmattr_show()` and `db1x_pmattr_store()` for `gpio0`-`gpio7`, `timer`, `timer_timeout`, `wakesrc`, and `wakemsk`.

Control flow: begin rejects suspend if no wake source is active. Enter saves BCSR registers, turns off HEX LEDs, enables GPIO1 input wake, clears/programs `SYS_WAKEMSK` and `SYS_WAKESRC`, waits for TOYMATCH2 access, programs the wake timeout from `SYS_TOYREAD + db1x_pm_sleep_secs`, calls `au_sleep()`, then restores BCSR and interrupt registers and LEDs. End records and clears the wake source.

State and persistence: static globals store sleep seconds, wake mask, and last wake source. Sysfs changes persist only until reboot. Hardware wake and BCSR state is saved/restored across one suspend.

Dependencies and integration: depends on CONFIG_PM build inclusion, BCSR, Alchemy system and GPIO helpers, kernel suspend core, `power_kobj`, and `au_sleep()`.

Risks: sysfs stores are minimally parsed; binary attributes are toggled by first character being `0` or not. `wakemsk` is masked to six bits despite attributes for GPIO0-7, which may reflect hardware mask width but is a risk for expectation mismatch. The suspend path assumes BCSR register ranges and interrupt-capable board detection by board ID.

Test signals: `/sys/power/db1x` should appear on PM builds. Writing a wake source should allow `mem` suspend, timer wake should resume after the configured timeout, `wakesrc` should report the cause, and BCSR-controlled LEDs/devices should return to pre-suspend state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/alchemy/devboards/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath25/Kconfig -->
## sources/distributed-fs/ceph-client/arch/mips/ath25/Kconfig

Purpose: defines build-time options for Atheros ATH25 SoC support. It splits support between AR5312/AR2312-class and AR2315-class SoCs and optionally enables the AR2315 PCI controller.

Important symbols: `SOC_AR5312` enables AR5312/AR2312+ support and depends on `ATH25`. `SOC_AR2315` enables AR2315+ support and depends on `ATH25`. `PCI_AR2315` depends on `SOC_AR2315`, selects `ARCH_HAS_PHYS_TO_DMA` and `FORCE_PCI`, and defaults on.

Control flow: none at runtime. These symbols control which C files are compiled and which code paths are available in headers through `#ifdef CONFIG_SOC_*`.

State and persistence: none directly. The selected symbols shape the kernel image.

Dependencies and integration: integrates with the parent ATH25 platform Kconfig and the local Makefile. PCI selection pulls in architecture DMA translation and PCI core support for AR2315 host mode.

Risks: both SoC families default on, so dead code or wrong runtime dispatch can remain hidden until boot on specific hardware. Forcing PCI for AR2315 may be inappropriate for stripped-down images unless the option is manually disabled.

Test signals: build configurations should include the expected objects. Boot tests on AR5312/AR2312 and AR2315/16/17/18 hardware validate that the Kconfig mix matches runtime CPU detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath25/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath25/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/ath25/Makefile

Purpose: controls compilation of ATH25 platform objects. It always includes shared board, PROM, and device registration code, then conditionally includes early printk and SoC-family implementations.

Important build entries: `obj-y += board.o prom.o devices.o` provides core platform hooks. `obj-$(CONFIG_EARLY_PRINTK) += early_printk.o` adds early UART output. `obj-$(CONFIG_SOC_AR5312) += ar5312.o` and `obj-$(CONFIG_SOC_AR2315) += ar2315.o` link the family-specific setup.

Control flow: none at runtime. Build selection determines whether the inline stubs in `ar5312.h`/`ar2315.h` are replaced by real implementations.

State and persistence: none directly.

Dependencies and integration: depends on Kbuild and local Kconfig symbols. It integrates with MIPS architecture boot through `plat_mem_setup`, `arch_init_irq`, `plat_time_init`, initcalls, and early printk objects supplied by the compiled files.

Risks: disabling one SoC family while booting that hardware leaves the dispatch path with no-op stubs or missing setup. Shared code still selects runtime behavior by CPU type, so build coverage should match target hardware.

Test signals: compile all selected combinations, check linked symbols for target SoCs, and boot with/without `CONFIG_EARLY_PRINTK` to verify console behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath25/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath25/ar2315.c -->
## sources/distributed-fs/ceph-client/arch/mips/ath25/ar2315.c

Purpose: implements platform setup for AR2315/AR2316/AR2317/AR2318-class ATH25 SoCs. It handles reset-controller access, memory sizing, IRQ dispatch and misc IRQ domain, AHB fatal error handling, clock frequency derivation, serial setup, WMAC registration, restart, and optional PCI host initialization.

Important APIs and functions: exported-to-board hooks are `ar2315_plat_mem_setup()`, `ar2315_arch_init_irq()`, `ar2315_plat_time_init()`, `ar2315_init_devices()`, and `ar2315_arch_init()`. Internal helpers include reset register read/write/mask functions, `ar2315_misc_irq_handler()`, `ar2315_irq_dispatch()`, `ar2315_sys_clk()`, and `ar2315_restart()`.

Control flow: memory setup maps SDRAM control, computes memory size from data/column/row width fields, adds memblock RAM, maps reset registers, classifies SoC from `SREV`, clears AHB/watchdog state, and installs restart. IRQ init creates a linear domain for misc IRQs, requests the AHB error IRQ, chains `AR2315_IRQ_MISC`, and sets `ath25_irq_dispatch`. Device init scans SPI flash for ATH25 board/radio config and registers WMAC0. Arch init maps UART0 misc IRQ, sets up the 8250 console, and if configured and on AR2315, resets/configures PCI and registers `ar2315-pci`.

State and persistence: static `ar2315_rst_base` and `ar2315_misc_irq_domain` hold mapped reset registers and IRQ mapping. Global `ath25_soc` and `ath25_board.devid` are set. Hardware reset, endian, PCI, and watchdog registers are changed.

Dependencies and integration: depends on ATH25 shared devices, AR2315 register definitions, IRQ domains, memblock, MIPS CP0, serial setup, board config scanner, and optional PCI platform driver.

Risks: memory size calculation trusts SDRAM registers. AHB error handling restarts immediately. `ar2315_restart()` notes an unimplemented GPIO reset workaround and falls back to the reset vector. PCI is only initialized for `ATH25_SOC_AR2315`, excluding later AR231x variants.

Test signals: boot should detect memory and system type, install UART, register WMAC0, and optionally create `ar2315-pci`. AHB error IRQ should log and restart. Clock-derived `mips_hpt_frequency` should match expected CPU/2 timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath25/ar2315.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath25/ar2315.h -->
## sources/distributed-fs/ceph-client/arch/mips/ath25/ar2315.h

Purpose: declares the AR2315-family setup entry points and provides no-op inline stubs when `CONFIG_SOC_AR2315` is disabled.

Important APIs: `ar2315_arch_init_irq()`, `ar2315_init_devices()`, `ar2315_plat_time_init()`, `ar2315_plat_mem_setup()`, and `ar2315_arch_init()` correspond to the major MIPS platform phases used by `board.c` and `devices.c`.

Control flow: no runtime flow in the header. Compile-time selection chooses real prototypes or inline empty functions. Shared code can call these names unconditionally after runtime CPU-family checks.

State and persistence: none directly.

Dependencies and integration: tied to `CONFIG_SOC_AR2315` from Kconfig and the implementation in `ar2315.c`. It allows `board.c` and `devices.c` to remain small and generic.

Risks: if the build excludes `SOC_AR2315` but runtime detection reaches the AR2315 path, the stubs silently do nothing, causing missing memory/IRQ/time/device setup rather than a compile-time failure. This makes configuration validation important.

Test signals: compile with and without `CONFIG_SOC_AR2315`. On enabled builds, symbol resolution should bind to `ar2315.c`; disabled builds should not link AR2315 code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath25/ar2315.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath25/ar2315_regs.h -->
## sources/distributed-fs/ceph-client/arch/mips/ath25/ar2315_regs.h

Purpose: defines AR2315+ interrupt numbers, physical address map, reset/control register offsets, bitfields, PLL fields, SDRAM fields, and local bus register constants used by `ar2315.c` and related platform code.

Important definitions: CPU IRQ assignments include `AR2315_IRQ_MISC`, `AR2315_IRQ_WLAN0`, and `AR2315_IRQ_LCBUS_PCI`. Misc IRQ hardware numbers include UART, SPI, AHB/APB, timer, GPIO, and watchdog. Address constants define SPI flash, WMAC, PCI, SDRAM, reset, UART, and PCI external windows. Register fields cover cold/warm resets, AHB arbitration, endian control, interface control, interrupt status/mask, watchdog, AHB error reports, PLL/CPU/AMBA clocks, SDRAM geometry, and local bus DMA/status.

Control flow: none; consumers use these macros for MMIO calculations, bit extraction, and IRQ mapping.

State and persistence: none directly. The constants name persistent hardware registers.

Dependencies and integration: included by `ar2315.c`, `early_printk.c`, and any AR2315 low-level code. It pairs with the `ATH25_REG_MS()` bitfield helper from `devices.h`.

Risks: typo risk is significant in register headers. One macro, `AR2315_RESET_SYSTEM`, references `RESET_COLD_*` names rather than the local `AR2315_RESET_COLD_*` names, although the implementation uses `AR2317_RESET_SYSTEM` for reset. Duplicate or stale hardware comments could mislead future driver work.

Test signals: compile coverage for all referenced macros, plus runtime validation of memory detection, clock frequency, PCI, UART, and interrupt dispatch. Register-level tests are hardware boot/probe behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath25/ar2315_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath25/ar5312.c -->
## sources/distributed-fs/ceph-client/arch/mips/ath25/ar5312.c

Purpose: implements platform setup for AR5312/AR2312/AR2313-class ATH25 SoCs. It provides memory sizing, reset-controller access, misc IRQ domain/chained dispatch, fatal AHB error handling, flash controller setup, board/radio data discovery, WMAC registration, clock derivation, restart, and serial setup.

Important APIs and functions: platform hooks are `ar5312_plat_mem_setup()`, `ar5312_arch_init_irq()`, `ar5312_plat_time_init()`, `ar5312_init_devices()`, and `ar5312_arch_init()`. Important internals are `ar5312_flash_init()`, `ar5312_cpu_frequency()`, `ar5312_misc_irq_handler()`, and `ar5312_ahb_err_handler()`.

Control flow: memory setup reads SDRAM bank address-check fields, computes RAM size, maps reset registers, records the device ID, clears prior AHB errors, disables watchdog, and installs restart. IRQ init creates a misc IRQ domain, maps and requests the AHB processor error interrupt, chains `AR5312_IRQ_MISC`, and sets global dispatch. Device init configures flash width/timing, finds board/radio config in flash, determines exact SoC using CPU revision and board flags, registers physmap flash, and adds WMACs according to board config flags. Arch init maps UART0 and calls shared serial setup.

State and persistence: static reset base and misc IRQ domain are runtime state. Global `ath25_soc` and `ath25_board` are updated. Flash controller registers are reprogrammed and other flash banks disabled.

Dependencies and integration: uses AR5312 register macros, ATH25 board config scanner, memblock, MTD physmap, IRQ domains, MIPS CP0, serial 8250 setup, and platform devices.

Risks: flash init assumes an 8 MiB window and aliases smaller flash. SoC identification depends on board config being found. WMAC registration returns early if radio data is absent. AHB errors are treated as catastrophic and restart the machine.

Test signals: boot should show flash and radio config discovery, correct system type, working UART, physmap flash, and WMAC0/WMAC1 only when board flags allow. Timer frequency should equal CPU/2, and watchdog should not reset spontaneously.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath25/ar5312.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath25/ar5312.h -->
## sources/distributed-fs/ceph-client/arch/mips/ath25/ar5312.h

Purpose: declares AR5312-family setup functions and provides empty inline stubs when `CONFIG_SOC_AR5312` is disabled.

Important APIs: `ar5312_arch_init_irq()`, `ar5312_init_devices()`, `ar5312_plat_time_init()`, `ar5312_plat_mem_setup()`, and `ar5312_arch_init()` are called from shared ATH25 boot and initcall code.

Control flow: compile-time conditional only. Runtime control is in callers that choose AR5312 versus AR2315 based on CPU type.

State and persistence: none.

Dependencies and integration: depends on `CONFIG_SOC_AR5312` and implementation in `ar5312.c`. It is included by `board.c`, `devices.c`, and any shared code needing the family hooks.

Risks: disabled builds expose no-op stubs. If the resulting kernel is booted on AR5312-family hardware, memory, clock, IRQ, and device setup can be skipped silently after runtime dispatch.

Test signals: build matrix with and without the symbol. Enabled builds should link real functions; disabled builds should not include `ar5312.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath25/ar5312.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath25/ar5312_regs.h -->
## sources/distributed-fs/ceph-client/arch/mips/ath25/ar5312_regs.h

Purpose: defines the AR5312/AR2312/AR2313 hardware interface: CPU interrupt lines, misc interrupt numbers, MMIO address map, reset/timer register offsets, reset bits, enable bits, revision fields, clock control fields, flash controller fields, and SDRAM sizing fields.

Important definitions: CPU IRQs include WLAN0, ENET0, ENET1, WLAN1, and MISC. Misc IRQs cover timer, AHB processor/DMA errors, GPIO, UART, watchdog, local bus, and SPI. Address constants define WMAC, Ethernet, SDRAM, flash controller, UART, GPIO, reset, and flash windows. Clock macros split AR5312/AR2312 and AR2313 multiplier/predivider bit layouts. Flash macros describe width, wait states, address check sizes, and enable/write protect bits.

Control flow: none. It is consumed by C code to configure hardware and decode revision/clock state.

State and persistence: none directly.

Dependencies and integration: included by `ar5312.c` and ATH25 early printk. It works with `ATH25_REG_MS()` from `devices.h` for bit extraction.

Risks: register headers are high-impact because incorrect masks or shifts affect memory size, clocks, and flash access. The AR5312 clock macros are duplicated in the file, which is harmless to the preprocessor but a maintenance smell.

Test signals: compile warnings for duplicate/inconsistent macros, plus boot validation for RAM sizing, flash width/timing, UART base, IRQ routing, and SoC revision classification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath25/ar5312_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath25/board.c -->
## sources/distributed-fs/ceph-client/arch/mips/ath25/board.c

Purpose: provides shared ATH25 boot hooks, board/radio configuration discovery in flash, platform memory/time/IRQ dispatch selection, and halt behavior.

Important APIs and functions: `ath25_find_config()` scans mapped flash for board and radio configuration and populates `ath25_board`. `plat_mem_setup()`, `plat_irq_dispatch()`, `plat_time_init()`, `get_c0_compare_int()`, and `arch_init_irq()` are MIPS platform hooks. Helpers `find_board_config()`, `find_radio_config()`, `check_board_data()`, and `check_radio_magic()` implement the flash heuristics.

Control flow: `plat_mem_setup()` installs halt/poweroff, selects AR5312 or AR2315 memory setup, then disables watchpoints. `ath25_find_config()` maps the flash window, searches backward near the end for board data magic, optionally accepts broken board data using nearby radio magic, copies board config into RAM, searches forward for radio config, copies radio data into the same buffer with offset preservation, and patches blank radio MAC from board data. IRQ/time hooks dispatch to family-specific implementations.

State and persistence: global `ath25_board.config` and `.radio` point to allocated RAM copies. Broken board data may get randomized in-memory MACs, but flash is not written. `_machine_halt` and `pm_power_off` are set.

Dependencies and integration: depends on ATH25 platform data structures, AR5312/AR2315 hooks, memblock setup, MIPS IRQ/time, flash ioremap, and Ethernet address helpers.

Risks: flash scanning intentionally searches a possibly larger region than physical flash, relying on aliasing. Broken board data fixups are temporary RAM-only. Missing board/radio config causes warnings and `-ENODEV`, which can suppress wireless registration. `ath25_halt()` disables IRQs and calls `unreachable()`.

Test signals: boot should log radio config offset or warnings. WMAC MAC addresses should be valid. Platform hooks should select the correct family on CPU type, and CP0 compare IRQ should be legacy compare.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath25/board.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath25/devices.c -->
## sources/distributed-fs/ceph-client/arch/mips/ath25/devices.c

Purpose: owns ATH25 global board/SoC state, shared WMAC platform devices, system type strings, early serial setup, and late device/arch initcall dispatch.

Important APIs and functions: globals `ath25_board` and `ath25_soc` are exported through declarations in `devices.h`. `get_system_type()` maps `ath25_soc` to a printable string. `ath25_serial_setup()` installs an 8250 console port when `CONFIG_SERIAL_8250_CONSOLE` is enabled. `ath25_add_wmac()` fills resources and registers `ar231x-wmac` platform devices. Initcalls `ath25_register_devices()` and `ath25_arch_init()` call family-specific device and arch setup.

Control flow: family-specific code sets `ath25_soc` and board config first. Device init calls AR5312 or AR2315 device registration based on `is_ar5312()`. Arch init later sets up serial and optional PCI through the family hooks. WMAC registration updates resource start/end pairs for memory and IRQ before platform registration.

State and persistence: `ath25_board` contains pointers to copied board/radio data and the device ID. `ath25_soc` controls system type reporting. Static platform devices are reused for WMAC0 and WMAC1. No durable state is written.

Dependencies and integration: depends on Linux platform device core, serial 8250, ATH25 platform structures, AR5312/AR2315 hooks, and CPU type helpers.

Risks: `ath25_add_wmac()` assumes `nr` is 0 or 1. `get_system_type()` reports unknown if `ath25_soc` is not set before use. Serial setup is compiled out without 8250 console support, so early/console behavior differs by config.

Test signals: registered `ar231x-wmac` devices should have correct MMIO/IRQ resources and platform data. `get_system_type()` should match detected SoC. Serial console should work when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath25/devices.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath25/devices.h -->
## sources/distributed-fs/ceph-client/arch/mips/ath25/devices.h

Purpose: shared ATH25 declarations and helpers for SoC family dispatch, bitfield extraction, global board/SoC state, and common device-registration APIs.

Important APIs and types: `ATH25_REG_MS()` extracts masked/shifted fields by macro naming convention. `ATH25_IRQ_CPU_CLOCK` defines the CP0 timer interrupt. `enum ath25_soc_type` enumerates AR2312/13/5312 and AR2315/16/17/18 plus unknown. Externs expose `ath25_soc`, `ath25_board`, and `ath25_irq_dispatch`. Function prototypes cover config scanning, serial setup, and WMAC registration. `is_ar2315()` checks `current_cpu_data.cputype == CPU_4KEC`; `is_ar5312()` is its negation.

Control flow: none beyond inline CPU-family predicates. Callers use these predicates during boot and initcalls.

State and persistence: none directly; declares global runtime state stored in `devices.c` and `board.c`.

Dependencies and integration: includes `linux/cpu.h`, ATH25 platform structures, and MIPS CPU data. It is included by every ATH25 C file.

Risks: CPU type is the only family discriminator, so unsupported compatible CPUs may be routed incorrectly. `ATH25_REG_MS()` requires fields to provide `_M` and `_S` macros exactly.

Test signals: compile all consumers and boot both CPU families to verify `is_ar2315()` branch selection. WMAC and serial setup depend on these declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath25/devices.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath25/early_printk.c -->
## sources/distributed-fs/ceph-client/arch/mips/ath25/early_printk.c

Purpose: implements `prom_putchar()` for ATH25 early printk by writing directly to the family-appropriate UART0 MMIO base.

Important APIs and functions: `prom_putchar(char ch)` lazily selects the UART base from `AR2315_UART0_BASE` or `AR5312_UART0_BASE` using `is_ar2315()`. `prom_uart_rr()` and `prom_uart_wr()` perform 32-bit raw UART register reads/writes with 4-byte register spacing.

Control flow: on first call, `prom_putchar()` caches the KSEG1 UART base. It spins until `UART_LSR_THRE` is set, writes the byte to `UART_TX`, and waits again for transmitter holding register empty.

State and persistence: static cached `base` is runtime-only. It changes no persistent state beyond UART transmit FIFO/registers.

Dependencies and integration: depends on `CONFIG_EARLY_PRINTK`, serial register definitions, ATH25 family detection, and AR2315/AR5312 UART base constants. It integrates with MIPS early printk through the standard `prom_putchar()` symbol.

Risks: if CPU family detection is wrong, writes go to the wrong MMIO address. The busy waits have no timeout, so a disabled or clock-gated UART can hang early output. It assumes MEM32 UART access with regshift 2.

Test signals: characters should appear very early on the serial console before normal 8250 setup. Boot with early printk disabled should omit this object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath25/early_printk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath25/prom.c -->
## sources/distributed-fs/ceph-client/arch/mips/ath25/prom.c

Purpose: provides the ATH25 PROM initialization hook. In this source version `prom_init()` is intentionally empty.

Important APIs and functions: `prom_init()` is marked `__init` and satisfies the MIPS platform firmware initialization interface.

Control flow: no operations are performed. ATH25 setup is handled by later platform hooks in `board.c` and family-specific files rather than parsing firmware data here.

State and persistence: none.

Dependencies and integration: includes `linux/init.h` and `asm/bootinfo.h`. The file is always linked by the ATH25 Makefile.

Risks: any bootloader argument, environment, or memory information not handled elsewhere will be ignored. This is acceptable only because ATH25 code determines memory and board configuration from hardware/flash.

Test signals: boot should proceed to `plat_mem_setup()` without requiring PROM data. There are no direct log messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath25/prom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath79/Kconfig -->
## sources/distributed-fs/ceph-client/arch/mips/ath79/Kconfig

Purpose: defines SoC-family configuration symbols for the ATH79 platform and PCI support selection for families that have PCI.

Important symbols: under `if ATH79`, `SOC_AR71XX`, `SOC_AR724X`, `SOC_AR913X`, `SOC_AR933X`, `SOC_AR934X`, and `SOC_QCA955X` are boolean symbols defaulting to `n`. AR71xx/AR724x/AR934x/QCA955x select `HAVE_PCI`, and AR724x/AR934x/QCA955x select `PCI_AR724X` when PCI is enabled. `PCI_AR724X` is an internal default-off symbol.

Control flow: no runtime flow. These symbols control availability of platform and PCI code elsewhere in the tree.

State and persistence: none directly.

Dependencies and integration: depends on the parent `ATH79` selection. PCI symbols integrate with the AR724x-compatible PCI host driver.

Risks: SoC symbols default off, so board/device tree selections must enable the right family. Missing symbols can compile out required PCI support despite common setup code being built.

Test signals: configuration checks should confirm the target SoC symbol and any needed PCI symbol are selected. Runtime validation is successful boot and PCI enumeration on supported chips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath79/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath79/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/ath79/Makefile

Purpose: builds the common ATH79 platform objects.

Important build entries: `obj-y := prom.o setup.o common.o clock.o` always includes firmware command-line parsing, platform setup, shared reset/DDR helpers, and clock registration. `obj-$(CONFIG_EARLY_PRINTK) += early_printk.o` optionally adds early UART output.

Control flow: none at runtime. The included objects provide MIPS platform hooks, clock providers, reset helpers, and early console support.

State and persistence: none directly.

Dependencies and integration: uses Kbuild and `CONFIG_EARLY_PRINTK`. The object list assumes device-tree-based board descriptions will drive devices while these files provide common low-level services.

Risks: omitting `clock.o` or `setup.o` would break timer initialization and SoC detection. Early printk support is optional and not available in non-early builds.

Test signals: built kernels should expose `prom_init`, `plat_mem_setup`, `plat_time_init`, `arch_init_irq`, ATH79 reset helpers, and DT clock provider declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath79/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath79/clock.c -->
## sources/distributed-fs/ceph-client/arch/mips/ath79/clock.c

Purpose: implements ATH79 clock provider setup for AR71xx, AR724x/AR913x, AR933x, AR934x, QCA953x, QCA955x, and QCA956x-compatible PLL blocks. It registers CPU, DDR, AHB, reference, and MDIO clocks for device tree consumers and MIPS timer setup.

Important APIs and functions: `ath79_clocks_init_dt()` is registered through multiple `CLK_OF_DECLARE()` compatible strings. Helpers `ath79_set_clk()` and `ath79_set_ff_clk()` create fixed-rate/fixed-factor clocks and clkdev aliases. SoC-specific functions decode PLL registers, including `ar71xx_clocks_init()`, `ar724x_clocks_init()`, `ar933x_clocks_init()`, `ar934x_clocks_init()`, `qca953x_clocks_init()`, `qca955x_clocks_init()`, and `qca956x_clocks_init()`. `ar934x_get_pll_freq()` handles fractional PLL math with 64-bit division.

Control flow: DT clock initialization optionally accepts an external ref clock from phandle index 0, maps PLL registers, selects decoder by compatible string, creates CPU/DDR/AHB clocks, defaults MDIO to ref if not explicitly set, then registers a onecell OF provider. Some families read bootstrap bits through `ath79_reset_rr()` to choose 25 or 40 MHz reference clocks. QCA956x also enables the MIPS SI timer interrupt workaround before clocks are finalized.

State and persistence: static `clks[]` and `clk_data` hold registered clock pointers. Hardware PLL registers are read, not generally written, except QCA956x misc interrupt enable through reset registers.

Dependencies and integration: depends on Linux common clock framework, OF clock/address APIs, dt-bindings clock IDs, ATH79 reset helpers, and AR71xx register definitions. `setup.c` calls `of_clk_init()` and later obtains the CPU clock.

Risks: PLL formulas are family-specific and easy to regress. Some functions do not check `ioremap()` failures for secondary SRIF maps. A missing compatible leaves clocks unset with little direct error handling. Divide fields of zero must be interpreted carefully by family.

Test signals: boot should log a plausible CPU clock in `plat_time_init()`. DT consumers should resolve `cpu`, `ddr`, `ahb`, `ref`, and `mdio` clocks. Timer rate, UART baud, Ethernet MDIO, and PCI behavior are practical validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath79/clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath79/common.c -->
## sources/distributed-fs/ceph-client/arch/mips/ath79/common.c

Purpose: provides shared ATH79 global SoC state, DDR controller helpers, PCI window setup, DDR write-buffer flushing, and serialized reset-module bit control.

Important APIs and functions: exported globals include `ath79_cpu_freq`, `ath79_ahb_freq`, `ath79_ddr_freq`, `ath79_reset_base`, `ath79_soc`, and `ath79_soc_rev`. `ath79_ddr_ctrl_init()` maps the DDR controller and selects write-buffer flush and PCI window offsets by SoC family. `ath79_ddr_wb_flush()` performs the documented two-pass flush. `ath79_ddr_set_pci_windows()` writes PCI window offsets. `ath79_device_reset_set()` and `ath79_device_reset_clear()` choose the reset-module register for the current SoC and update bits under `ath79_device_reset_lock`.

Control flow: setup code calls DDR init after SoC detection. Drivers can call exported DDR/reset helpers later. Reset set/clear choose register offsets using `soc_is_*()` predicates and BUG on unknown SoC, then do read-modify-write under IRQ-safe spinlock.

State and persistence: static mapped bases track DDR subregisters. Reset register writes persist in hardware until changed/reset. Global SoC and frequency variables are runtime state exported to modules.

Dependencies and integration: depends on ATH79 SoC predicates, reset read/write helpers from public machine headers, Linux spinlocks, raw MMIO, and PCI constants. PCI and device drivers use these helpers.

Risks: `ath79_ddr_wb_flush()` assumes `ath79_ddr_ctrl_init()` has run. `ath79_ddr_set_pci_windows()` BUGs if no PCI window base is available. Unknown SoC families BUG in reset helpers, so all supported SoCs must be represented.

Test signals: DDR flush should complete without hanging; PCI devices should DMA correctly after window setup; device reset calls should toggle hardware and not race under concurrent drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath79/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath79/common.h -->
## sources/distributed-fs/ceph-client/arch/mips/ath79/common.h

Purpose: small local header for ATH79 common definitions shared by setup and common code.

Important APIs and definitions: `ATH79_MEM_SIZE_MIN` is 2 MiB and `ATH79_MEM_SIZE_MAX` is 256 MiB, used as scan bounds for memory detection. `ath79_ddr_ctrl_init()` is declared for setup code.

Control flow: none.

State and persistence: none directly.

Dependencies and integration: includes `linux/types.h` and is used by `setup.c`, `common.c`, `clock.c`, and `prom.c` as a local interface. The memory bounds feed `detect_memory_region()`.

Risks: incorrect memory bounds would truncate or over-scan RAM detection across all ATH79 boards. The header intentionally exposes only a minimal subset; other globals are declared in public machine headers.

Test signals: boot memory size detection should fall within these bounds. Compile coverage verifies the DDR init declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath79/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath79/early_printk.c -->
## sources/distributed-fs/ceph-client/arch/mips/ath79/early_printk.c

Purpose: implements early `prom_putchar()` for ATH79 SoCs, selecting between classic 16550-style UART and AR933x UART register layouts and enabling UART pinmux bits where supported.

Important APIs and functions: `prom_putchar()` lazily initializes `_prom_putchar`. `prom_putchar_ar71xx()` writes to `AR71XX_UART_BASE` using standard UART registers with 4-byte spacing. `prom_putchar_ar933x()` writes to `AR933X_UART_BASE` using `AR933X_UART_DATA_REG`. `prom_enable_uart()` sets the GPIO function UART enable bit based on revision ID. `prom_putchar_init()` reads `AR71XX_RESET_REG_REV_ID` and selects the backend or a dummy function.

Control flow: first character read maps reset base through KSEG1, decodes major revision, selects AR71xx-style backend for most SoCs, AR933x backend for AR9330/9331, dummy for unknown, enables UART pinmux where implemented, then subsequent calls go directly through `_prom_putchar`.

State and persistence: static function pointer caches the selected output backend. GPIO function writes change pinmux state until reset or later configuration.

Dependencies and integration: depends on early printk config, raw MMIO, serial register constants, ATH79 revision macros, AR933x UART definitions, and the standard MIPS `prom_putchar()` early console path.

Risks: QCA953x/QCA955x/QCA956x use the AR71xx UART backend but `prom_enable_uart()` only handles older families and AR933x; pinmux may need firmware preconfiguration on newer chips. Busy waits have no timeout. Unknown SoC IDs silently discard early output.

Test signals: early boot text should appear before normal console setup on each supported UART type. AR933x should use its special TX CSR path, while other SoCs should use standard LSR/TX registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath79/early_printk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath79/prom.c -->
## sources/distributed-fs/ceph-client/arch/mips/ath79/prom.c

Purpose: initializes ATH79 firmware-provided command-line data and optional initrd placement.

Important APIs and functions: `prom_init()` calls `fw_init_cmdline()`. When `CONFIG_BLK_DEV_INITRD` is enabled, it reads `initrd_start` and `initrd_size` from firmware environment variables using `fw_getenvl()`, converts the start address through `KSEG0ADDR()`, and fills `initrd_start`/`initrd_end`.

Control flow: command-line initialization always runs. Initrd setup runs only when configured and only if `initrd_start` is nonzero.

State and persistence: updates global boot command line and initrd address variables for this boot only. No persistent storage is changed.

Dependencies and integration: depends on MIPS firmware helper APIs, bootinfo, initrd globals, and `common.h`. `setup.c` later reads firmware `fdt_start` separately.

Risks: firmware environment values are trusted. A wrong physical initrd address or size can point into invalid memory. If `initrd_start` is absent, no initrd is registered.

Test signals: kernel command line should reflect firmware arguments. Initrd-enabled boots should find the initrd at the expected converted address and mount/unpack it successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath79/prom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath79/setup.c -->
## sources/distributed-fs/ceph-client/arch/mips/ath79/setup.c

Purpose: implements core ATH79 platform setup: SoC identification, FDT setup, reset/PLL mapping, DDR controller init, memory detection, halt/poweroff hooks, timer frequency initialization, and irqchip initialization.

Important APIs and functions: `plat_mem_setup()` is the early setup entry. `ath79_detect_sys_type()` decodes `AR71XX_RESET_REG_REV_ID`, sets `ath79_soc`/`ath79_soc_rev`, formats `ath79_sys_type`, and prints it. `get_system_type()` returns the formatted string. `plat_time_init()` initializes OF clocks, obtains CPU node clock 0, logs CPU MHz, and sets `mips_hpt_frequency`. `arch_init_irq()` calls `irqchip_init()`. `get_c0_compare_int()` returns the legacy CP0 compare IRQ.

Control flow: memory setup sets I/O port base, locates the FDT from firmware `fdt_start` or built-in `get_fdt()`, calls `__dt_setup_arch()`, maps reset and PLL bases, detects SoC, initializes DDR controller bases, scans memory between 2 and 256 MiB, and installs halt/poweroff. Time init runs OF clock declarations, fetches the CPU clock, and derives the high-precision timer from CPU/2.

State and persistence: global `ath79_reset_base`, `ath79_pll_base`, `ath79_soc`, `ath79_soc_rev`, and static `ath79_sys_type` are set for this boot. No durable storage is written.

Dependencies and integration: depends on firmware helpers, OF/FDT, common clock framework, irqchip DT, MIPS time/reboot, ATH79 register macros, and DDR helpers from `common.c`.

Risks: unknown revision IDs panic. Missing CPU node or clock leaves timer setup incomplete after logging an error. Memory detection uses broad bounds and assumes low memory starts at 0. `ath79_halt()` loops in `cpu_wait()` forever.

Test signals: boot log should show exact SoC string and CPU clock. `/proc/cpuinfo` system type should match. IRQ controllers should initialize from DT, timers should tick at the correct rate, and detected RAM should match hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/ath79/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm47xx/Kconfig -->
## sources/distributed-fs/ceph-client/arch/mips/bcm47xx/Kconfig

Purpose: defines BCM47XX bus-family support options for old SSB-based and newer BCMA-based Broadcom router SoCs.

Important symbols: `BCM47XX_SSB` selects BMIPS32 3300 CPU support, SSB host/embedded/MIPS/extif/GPIO support, and optional SSB PCI host/bridge pieces when PCI is enabled. `BCM47XX_BCMA` selects MIPS32 R2/highmem/vector IRQ support, BCMA host/MIPS/GPIO support, and optional BCMA PCI hostmode. Both default to `y` under `BCM47XX`.

Control flow: none directly. These options control which bus framework and CPU/IRQ capabilities are available to the platform.

State and persistence: none.

Dependencies and integration: integrates with parent `BCM47XX`, SSB, BCMA, PCI, CPU, and IRQ subsystem Kconfig symbols. The runtime code in this subset, especially `irq.c`, branches on `CONFIG_BCM47XX_BCMA`.

Risks: both default on for broad images, increasing binary surface. Selecting the wrong bus support for a board can remove required bus setup, GPIO, PCI, or IRQ behavior. BCMA changes `cp0_compare_irq` routing in `irq.c`.

Test signals: SSB and BCMA target builds should include their bus drivers and boot on representative routers. PCI enumeration and GPIO-backed buttons/LEDs validate the selected support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm47xx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm47xx/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/bcm47xx/Makefile

Purpose: builds the BCM47XX platform support objects.

Important build entries: always includes `irq.o prom.o serial.o setup.o time.o` and `board.o buttons.o leds.o workarounds.o`. This subset covers `irq.o`, `board.o`, and `buttons.o`; the other objects provide the remaining platform boot, console, time, LED, and workaround behavior.

Control flow: none in the Makefile. Object inclusion exposes the platform hooks and init routines expected by BCM47XX boot.

State and persistence: none directly.

Dependencies and integration: uses Kbuild under BCM47XX platform selection. The object list assumes board detection, button and LED registration, bus setup, and workaround init are all part of the platform image.

Risks: no conditional gating is present in this file, so code must internally handle SSB versus BCMA and supported board differences. Removing an object can silently drop platform features.

Test signals: built image should contain IRQ dispatch, PROM/setup/time, serial, board detection, buttons, LEDs, and workaround symbols. Boot should call the appropriate init paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm47xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm47xx/bcm47xx_private.h -->
## sources/distributed-fs/ceph-client/arch/mips/bcm47xx/bcm47xx_private.h

Purpose: private BCM47XX platform header for local function declarations and a consistent `pr_fmt()`.

Important APIs and definitions: defines `pr_fmt(fmt)` as `bcm47xx: ` when not already set. Declares init functions from local platform files: `bcm47xx_prom_highmem_init()`, `bcm47xx_buttons_register()`, `bcm47xx_leds_register()`, `bcm47xx_bus_setup()`, and `bcm47xx_workarounds()`.

Control flow: none.

State and persistence: none.

Dependencies and integration: included by local BCM47XX files such as `buttons.c` and `irq.c`. It keeps cross-file init prototypes out of public headers.

Risks: declarations must match implementations in other files; otherwise build/link failures or incorrect init attributes can occur. The header only declares a subset of local functions, so new cross-file calls require updates.

Test signals: compile coverage and log prefix consistency. Runtime signal is successful registration of bus/buttons/LEDs/workarounds through callers that use these declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm47xx/bcm47xx_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm47xx/board.c -->
## sources/distributed-fs/ceph-client/arch/mips/bcm47xx/board.c

Purpose: detects the specific BCM47XX router board model from NVRAM variables and exposes the detected board enum and name.

Important APIs and functions: `bcm47xx_board_detect()` initializes detection once. `bcm47xx_board_get()` and `bcm47xx_board_get_name()` are exported. `bcm47xx_board_get_nvram()` checks multiple key patterns and returns a `bcm47xx_board_type`. Static tables map NVRAM keys such as `model_name`, `hardware_version`, `productid`, `ModelId`, `melco_id`/`buf1falo_id`, `boot_hw_model` plus `boot_hw_ver`, `board_id`, `boardtype`/`boardnum`/`boardrev`, and ad hoc key/value pairs to board enums and readable names.

Control flow: detection first avoids rerun if already set. It probes `boardtype` to see whether NVRAM is available; `-ENXIO` means too early and returns without setting a final board. Otherwise it scans the NVRAM matching tables in priority order, defaults to unknown, copies the enum and name into static storage, and later callers retrieve them.

State and persistence: static `bcm47xx_board` stores detected board and name for this boot. NVRAM is read only; no persistent data is modified.

Dependencies and integration: depends on `bcm47xx_nvram_getenv()`, board enum definitions, string helpers, and exported symbol consumers such as buttons/LEDs/setup code.

Risks: matching priority matters and can misidentify boards with overlapping NVRAM strings. One hardware-version plus boardnum condition uses `!strstarts(buf1, e2->value1) && !strcmp(...)`, which appears counterintuitive because most other matches require positive string matching. Buffer sizes are small but bounded. Unknown boards lose model-specific buttons/LEDs.

Test signals: boot logs/consumers should report the expected board name. Validate representative NVRAM sets for each table, unknown fallback, and retry behavior when NVRAM initially returns `-ENXIO`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm47xx/board.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm47xx/buttons.c -->
## sources/distributed-fs/ceph-client/arch/mips/bcm47xx/buttons.c

Purpose: maps detected BCM47XX board models to GPIO-backed input buttons and registers a `gpio-keys` platform device. It covers many Asus, Belkin, Buffalo, Dell, D-Link, Huawei, Linksys, Luxul, Microsoft, Motorola, Netgear, and SimpleTech boards.

Important APIs and functions: `bcm47xx_buttons_register()` is the board-specific registration entry. `bcm47xx_buttons_copy()` duplicates `__initconst` button arrays into normal memory with `kmemdup()`. Macros `BCM47XX_GPIO_KEY()` and `BCM47XX_GPIO_KEY_H()` define active-low and active-high `gpio_keys_button` entries. Static arrays encode GPIO numbers and Linux input key codes such as `KEY_RESTART`, `KEY_WPS_BUTTON`, `KEY_RFKILL`, `BTN_0`, and `KEY_POWER`.

Control flow: registration reads `bcm47xx_board_get()`, switches on the enum, copies the matching static button array into `bcm47xx_button_pdata`, and registers `bcm47xx_buttons_gpio_keys`. Unsupported boards log debug and return `-ENOTSUPP`; allocation failure returns `-ENOMEM`; platform device registration errors are logged and returned.

State and persistence: copied button data is retained for the lifetime of the platform device. GPIO input events are runtime-only. No persistent storage is written.

Dependencies and integration: depends on board detection from `board.c`, Linux `gpio-keys`, input key codes, platform device core, and BCM47XX GPIO providers from SSB/BCMA support.

Risks: the switch table must stay synchronized with board detection enums. Wrong active polarity or GPIO numbers can cause stuck keys or missing reset/WPS behavior. Some arrays lack `__initconst` annotations while most have them, which is not functional but inconsistent. No cleanup path frees copied data if platform registration fails after allocation.

Test signals: `/proc/bus/input/devices` or evdev should show gpio-keys on supported boards. Pressing reset/WPS/RF kill/mode buttons should emit expected key codes and polarity. Unsupported boards should fail gracefully without a bogus gpio-keys device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm47xx/buttons.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm47xx/irq.c -->
## sources/distributed-fs/ceph-client/arch/mips/bcm47xx/irq.c

Purpose: implements BCM47XX CPU interrupt dispatch and initialization, including BCMA-specific timer interrupt routing and optional MIPS vectored interrupt setup.

Important APIs and functions: `plat_irq_dispatch()` reads CP0 cause/status, masks to pending interrupt bits, clears those bits from CP0 status, and calls `do_IRQ()` for IP7, then IP2 through IP6. `arch_init_irq()` completes bus setup through `bcm47xx_bus_setup()`, applies BCMA MIPS74K interrupt mask and `cp0_compare_irq` fixup when needed, initializes CPU IRQs, and installs vectored handlers if `cpu_has_vint`. Macro `DEFINE_HWx_IRQDISPATCH()` creates simple handlers for hardware IRQs 2 through 7.

Control flow: architecture IRQ init is the first callback after `mm_init`, so it finalizes bus initialization when allocation is available. On BCMA, it routes the timer to IRQ7 because hardware/register reporting would otherwise suggest IRQ5. Then `mips_cpu_irq_init()` sets up CPU IRQ lines. If vectored interrupts are supported, each vector directly dispatches its matching IRQ number; otherwise `plat_irq_dispatch()` handles pending bits in priority order.

State and persistence: may update global `cp0_compare_irq` and BCMA core interrupt mask register. CP0 status is modified during dispatch.

Dependencies and integration: depends on BCM47XX bus globals, BCMA APIs under config, MIPS CPU IRQ core, vectored interrupt support, and local bus setup declaration.

Risks: clearing all pending cause/status bits from status before dispatch can affect nested/level interrupt timing. Dispatch uses independent `if` statements, so multiple pending IRQs can be serviced in one entry. BCMA timer routing is hardware-specific and must align with time code.

Test signals: timer interrupts should arrive on IRQ7 for BCMA and scheduling should progress. SSB/BCMA device interrupts should reach their handlers. Boot should log vectored interrupt setup on CPUs with VINT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/bcm47xx/irq.c -->
