# subset-b-000799 research

This grouped report covers PowerPC CHRP, embedded6xx, Freescale ULI1575, Microwatt, PA Semi PWRficient, and selected PowerMac platform files. Each source file has a delimited section for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/pci.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/pci.c

Purpose: CHRP PCI host-bridge discovery and config-space access glue. It supports Golden Gate II LongTrail direct config windows, RTAS config calls, Python, Grackle, Pegasos, CPC710, Hydra Mac I/O enablement, and board-specific PCI fixups.

Important APIs and control flow: `gg2_read_config`/`gg2_write_config` limit bus numbers to the GG2 512 KiB config aperture. `rtas_read_config`/`rtas_write_config` encode bus/devfn/offset/hose global number for RTAS. `setup_python`, `setup_peg2`, and `chrp_find_bridges` select controller ops from OF model data, allocate `pci_controller` structures, process OF ranges, and set `pci_dram_offset`. `hydra_init` maps `mac-io` and enables SCC/SCSI/MPIC feature bits. PCI fixups force Briq Winbond IDE native mode and Pegasos VIA IDE legacy mode.

State, dependencies, and risks: persistent state is global MMIO mapping `gg2_pci_config_base`, `Hydra`, PCI hose configuration, and `pci_dram_offset`. Dependencies include Open Firmware properties, RTAS tokens, indirect PCI helpers, MPIC/Hydra registers, and PCI quirk registration. Risks are firmware-model heuristics, unchecked ioremap assumptions in some paths, host-bridge address quirks, and fixups that mutate class/BAR state before normal PCI enumeration. Test signals are mainly boot-time enumeration logs, PCI device visibility, working IDE interrupts, and platform boot on LongTrail, Briq, Pegasos, and CPC710 systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/pegasos_eth.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/pegasos_eth.c

Purpose: registers legacy platform devices for Pegasos II Marvell MV6436x Ethernet, MDIO, and port 1 SRAM-backed queue resources.

Important APIs and control flow: static `resource`, `platform_device`, and `mv643xx_eth_platform_data` objects describe shared Ethernet registers, Orion MDIO window, IRQ 9, PHY address 7, and integrated SRAM queue layout. `Enable_SRAM` maps the Marvell register block, configures SRAM base/size registers, enables the SRAM window, and unmaps. `mv643xx_eth_add_pds` runs as a `device_initcall`, checks for the Marvell PCI device, adds platform devices, and disables SRAM fields if SRAM setup fails.

State, dependencies, and risks: state is the transient `mv643xx_reg_base` mapping and static platform data handed to network drivers. Dependencies include PCI device presence, Marvell register layout, `mv643xx_eth` platform bindings, and platform-device probing. Risks include hard-coded physical addresses and IRQ/PHY values, SRAM setup ordering after device registration, and fallback to non-SRAM queues only on setup failure. Test signals are platform-device creation, MDIO probe, Ethernet link on port 1, and absence of MMIO faults during SRAM programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/pegasos_eth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/setup.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/setup.c

Purpose: CHRP machine descriptor implementation. It classifies CHRP variants, initializes RTAS, interrupt controllers, fallback console behavior, RTC hooks, NVRAM late init, CPU info, and restart/power hooks.

Important APIs and control flow: `chrp_probe` accepts flat DT `device_type = "chrp"`, sets DMA mode constants, power-off, and fallback console selection. `chrp_setup_arch` identifies Pegasos/IBM/Motorola/Briq models, initializes RTAS, installs RTAS progress/time hooks, enables Pegasos L2 cache, fixes LongTrail Super I/O IRQ routing, and maps Briq reset. `chrp_find_openpic` and `chrp_find_8259` configure MPIC and optional i8259 cascade; `chrp_init_IRQ` selects SMP ops only when an MPIC exists. `define_machine(chrp)` wires PCI discovery, RTC, IRQ, restart, and `/proc/cpuinfo` callbacks.

State, dependencies, and risks: global state includes `_chrp_type`, `chrp_mpic`, Briq SPOR mapping, heartbeat timers, and `ppc_md` callbacks. Dependencies are OF model/properties, RTAS services, MPIC/i8259 domains, Hydra ADB NMI, and optional NVRAM. Risks include early-boot firmware assumptions, `request_region` without recovery, model-string dispatch, and Pegasos interrupt-tree workarounds. Test signals are successful CHRP boot, interrupt delivery from MPIC/i8259, RTAS time use where present, console fallback on Pegasos2, and CPU info output for LongTrail memory/cache data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/smp.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/smp.c

Purpose: SMP operations for CHRP systems using OpenPIC/MPIC and RTAS timebase transfer.

Important APIs and control flow: `smp_chrp_kick_cpu` writes the target CPU number to `KERNELBASE`, flushes that cache line, and returns success so secondary firmware/hold code can observe it. `smp_chrp_setup_cpu` calls `mpic_setup_this_cpu`. `chrp_smp_ops` delegates probing and IPIs to MPIC helpers and timebase handoff to `rtas_give_timebase`/`rtas_take_timebase`.

State, dependencies, and risks: state is the externally installed `smp_ops` table and the magic word at `KERNELBASE`. Dependencies include MPIC initialization, RTAS timebase services, and secondary CPU boot conventions. Risks are platform-specific secondary release semantics and invalid use on Pegasos systems without MPIC, which `setup.c` avoids. Test signals are secondary CPU bring-up, IPI delivery, synchronized timebase, and no crash when SMP is disabled or MPIC is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/time.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/time.c

Purpose: CHRP CMOS/RTC access fallback for systems not using RTAS time-of-day services.

Important APIs and control flow: `chrp_time_init` looks for `pnpPNP,b00` or `ds1385-rtc`, remaps default NVRAM index/data ports to the OF resource base, and leaves legacy ports otherwise. `chrp_cmos_clock_read`/`chrp_cmos_clock_write` drive the indexed RTC registers. `chrp_set_rtc_time` locks `rtc_lock`, sets `RTC_SET`, resets the prescaler, converts to BCD if needed, writes time/date fields, then restores control registers in DS12887-safe order. `chrp_get_rtc_time` loops until seconds are stable, converts from BCD, and normalizes post-2000 years.

State, dependencies, and risks: state is the selected RTC port triplet and shared `rtc_lock`. Dependencies include MC146818-compatible register semantics, OF RTC resources, BCD helpers, and PowerPC time hooks. Risks include two-digit year interpretation, port I/O ordering sensitivity, and reliance on stable seconds reads instead of UIP polling. Test signals are correct RTC read/write across reboot, no register corruption on DS12887 clones, and fallback behavior when no RTC node exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/Kconfig -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/Kconfig

Purpose: Kconfig menu for 32-bit embedded 6xx/7xx/7xxx board support, including Buffalo Linkstation, Iomega StorCenter, IBM Holly, MVME5100, Nintendo GameCube/Wii, bridge helpers, and USB Gecko debug console.

Important APIs and control flow: `EMBEDDED6xx` depends on `PPC_BOOK3S_32` and excludes SMP. Board options select required interrupt controllers, PCI forcing/indirect config, 16550 debug, FSL SoC support, or GameCube common support. `GAMECUBE_COMMON`, `TSI108_BRIDGE`, and `MPC10X_BRIDGE` are hidden dependency symbols; `USBGECKO_UDBG` is user-visible and depends on Nintendo common support.

State, dependencies, and risks: state is compile-time configuration only. Dependencies govern which platform files and helper subsystems are built. Risks are stale `BROKEN_ON_SMP` coverage, hidden bridge symbols being implied rather than required for some PCI builds, and old board help text that may not match tested hardware. Test signals are allmodconfig/defconfig coverage, dependency resolution for each board, and successful link of selected machine descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/Makefile

Purpose: build mapping from embedded6xx Kconfig symbols to board, interrupt, UART, and debug objects.

Important APIs and control flow: Linkstation builds `linkstation.o` and `ls_uart.o`; StorCenter, Holly, GameCube, Wii, and MVME5100 select their board files. `GAMECUBE_COMMON` always builds `flipper-pic.o`; Wii additionally builds `hlwd-pic.o`; `USBGECKO_UDBG` builds the EXI debug console.

State, dependencies, and risks: state is object inclusion order at build time. Dependencies are Kconfig symbols and link-time machine descriptor registration. Risks are missing common objects when symbols are misconfigured and board code depending on prototypes from `mpc10x.h` or PIC headers without matching object inclusion. Test signals are per-board kernel link success and absence of unresolved `flipper_*`, `hlwd_*`, or AVR UART symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/flipper-pic.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/flipper-pic.c

Purpose: interrupt-controller driver and reset-button helpers for the Nintendo GameCube/Wii Flipper PI interrupt block.

Important APIs and control flow: irq-chip callbacks mask, unmask, and ack bits in Flipper IMR/ICR registers. `flipper_pic_init` validates the parent `nintendo,flipper-pi` node, maps the parent register resource, quiesces all IRQs, and creates a linear 32-entry irq domain. `flipper_pic_probe` finds `nintendo,flipper-pic`, installs the domain as default, and `flipper_pic_get_irq` returns the first pending enabled interrupt mapping. `flipper_quiesce`, `flipper_platform_reset`, and `flipper_is_reset_button_pressed` expose chipset operations to board files.

State, dependencies, and risks: state is global `flipper_irq_host` and its MMIO base. Dependencies include OF compatible names, big-endian MMIO helpers, irqdomain, and board machine descriptors. Risks include `BUG_ON` if firmware lacks the node, no ioremap failure check in `flipper_pic_init`, and global state assumed valid by reset/quiesce helpers. Test signals are interrupt delivery, reset button state, clean shutdown quiesce, and GameCube/Wii reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/flipper-pic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/flipper-pic.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/flipper-pic.h

Purpose: local declarations for Flipper interrupt, quiesce, reset, and reset-button helpers used by GameCube and Wii board code.

Important APIs and control flow: declares `flipper_pic_get_irq`, `flipper_pic_probe`, `flipper_quiesce`, `flipper_platform_reset`, and `flipper_is_reset_button_pressed`. The header has no logic; inclusion binds board files to `flipper-pic.c`.

State, dependencies, and risks: state is external to the header and held by `flipper-pic.c`. Dependencies are `__init` annotations and local include ordering. Risks are build/link failures if `GAMECUBE_COMMON` is not selected with board files. Test signals are compile coverage and correct linkage for GameCube/Wii machine descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/flipper-pic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/gamecube.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/gamecube.c

Purpose: Nintendo GameCube machine descriptor and board-level reset, power, interrupt, debug, and OF platform-device population hooks.

Important APIs and control flow: `gamecube_probe` installs `pm_power_off` and initializes optional USB Gecko udbg. Restart disables interrupts, calls `flipper_platform_reset`, and spins; power-off only spins until external action. `define_machine(gamecube)` uses Flipper PIC init/get_irq and `udbg_progress`. A `machine_device_initcall` probes OF platform buses compatible with `nintendo,flipper`.

State, dependencies, and risks: state is `pm_power_off` plus Flipper and USB Gecko global state. Dependencies include the `nintendo,gamecube` compatible string, Flipper PIC, OF platform bus, and udbg hooks. Risks are intentional infinite spins for poweroff/halt, reliance on reset MMIO being mapped, and no fallback interrupt controller. Test signals are machine match, early debug output, device population, interrupt handling, and reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/gamecube.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/hlwd-pic.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/hlwd-pic.c

Purpose: interrupt-domain driver for the Nintendo Wii Hollywood interrupt controller, including cascade wiring behind another interrupt source.

Important APIs and control flow: irq-chip callbacks manipulate Broadway ICR/IMR and clear Starlet ownership on unmask. `hlwd_pic_init` maps the controller, quiesces all sources, and creates a linear 32-entry domain. `hlwd_pic_probe` scans `nintendo,hollywood-pic` nodes with `interrupts`, initializes a domain, maps the cascade IRQ, and installs `hlwd_pic_irq_cascade`. The cascade masks the parent level IRQ, dispatches one pending Hollywood hwirq through `generic_handle_domain_irq`, acks, and unmasks.

State, dependencies, and risks: state is global `hlwd_irq_host` and mapped MMIO. Dependencies include OF address/interrupt properties, irqdomain, chained IRQ handlers, and Wii board setup. Risks include only handling one pending hwirq per cascade entry, `BUG_ON` on failed init, assuming the child hwirq zero is never valid because zero is treated as no IRQ, and global quiesce requiring successful probe. Test signals are Wii secondary interrupt delivery, no Starlet conflict for unmasked lines, cascade mapping, and clean shutdown quiesce.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/hlwd-pic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/hlwd-pic.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/hlwd-pic.h

Purpose: local declarations for Hollywood PIC initialization, IRQ lookup, and quiesce operations used by Wii board code.

Important APIs and control flow: declares `hlwd_pic_get_irq`, `hlwd_pic_probe`, and `hlwd_quiesce`. There is no inline behavior.

State, dependencies, and risks: state is owned by `hlwd-pic.c`. Dependencies are `__init` annotations and Wii object inclusion. Risks are link failures if Wii board code is compiled without `hlwd-pic.o`. Test signals are compile/link coverage and successful Wii interrupt setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/hlwd-pic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/holly.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/holly.c

Purpose: IBM PPC750GX/CL Holly/Hickory board support using the TSI108 bridge, MPIC, PCI setup, restart path, and machine-check recovery.

Important APIs and control flow: `holly_remap_bridge` reprograms TSI108 processor/PCI LUTs, I/O, config, and memory windows. `holly_init_pci` calls `tsi108_setup_pci` and excludes root bridge device 0 from PCI probing. `holly_init_IRQ` allocates a TSI108 MPIC, assigns ISUs, optionally initializes the PCI interrupt router cascade, and routes MPIC outputs to CPU0. `holly_restart` maps the TSI bridge, sets BOOT routing, loads SRR0/SRR1, and uses `rfi` to jump to firmware. `ppc750_machine_check_exception` uses exception-table fixups to recover PCI config faults.

State, dependencies, and risks: state includes `tsi108_csr_vir_base`, `ppc_md.pci_exclude_device`, MPIC/cascade handlers, and bridge MMIO configuration. Dependencies include TSI108 register helpers, OF `pci`, `pic-router`, and `tsi-bridge` nodes, MPIC, and extable support. Risks are destructive bridge reprogramming, missing OF nodes causing partial IRQ setup, and restart relying on firmware vectors. Test signals are PCI enumeration, TSI108 interrupt routing, recoverable config-space machine checks, and successful firmware restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/holly.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/linkstation.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/linkstation.c

Purpose: Buffalo Linkstation/Kurobox machine descriptor for MPC8241 NAS boards.

Important APIs and control flow: `declare_of_platform_devices` probes `soc` and `simple-bus` children. `linkstation_setup_pci` finds `mpc10x-pci` host bridges and `linkstation_add_bridge` allocates indirect PCI controllers at hard-coded config addresses and processes OF ranges. `linkstation_init_IRQ` creates an EPIC/MPIC with ISUs for PCI, I2C, and DUART. Restart and power-off configure the AVR UART, send command `C` or `E`, then repeatedly send `G` kicks. `linkstation_probe` installs `pm_power_off`.

State, dependencies, and risks: state is machine callbacks plus AVR UART state owned by `ls_uart.c`. Dependencies include OF bridge nodes, MPIC, indirect PCI, MPC10x mapping, and an AVR power-management microcontroller. Risks are hard-coded PCI config addresses, infinite loops on failed AVR response, and limited tested hardware noted by Kconfig. Test signals are platform-device population, PCI enumeration, serial/AVR watchdog handling, and restart/poweroff behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/linkstation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/ls_uart.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/ls_uart.c

Purpose: Linkstation AVR UART helper used for watchdog disarm and board restart/poweroff commands.

Important APIs and control flow: `ls_uarts_init` locates `/soc10x/serial@80004500`, reads `clock-frequency`, maps the UART, initializes it, and schedules `wd_stop`. `avr_uart_configure` programs 8-bit serial with stop/parity settings and a 9600 baud divisor. `avr_uart_send` writes each command byte four times. `wd_stop` sends a fixed watchdog-disarm sequence in chunks when the transmitter is ready and prints any response bytes.

State, dependencies, and risks: state is global `avr_addr`, `avr_clock`, and delayed work. Dependencies include NS16550 register layout, OF serial node path, workqueues, and Linkstation board hooks. Risks include unchecked `of_get_property` dereference for `clock-frequency`, no synchronization around UART use after init, and command loops in restart/poweroff if AVR is absent. Test signals are watchdog disarm response, reboot/poweroff via AVR, and no serial conflict with `CONFIG_SERIAL_8250`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/ls_uart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/mpc10x.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/mpc10x.h

Purpose: shared constants and prototypes for Motorola/Freescale MPC106/8240/107 host bridge, memory maps, embedded utility block devices, and Linkstation AVR helpers.

Important APIs and control flow: defines bridge IDs, Map A/Map B PCI config/ISA/memory windows, DRAM offsets, interrupt acknowledge addresses, config register offsets, EUMB offsets, and `ppc_sys_devices` identifiers. Declares bridge initialization, memory-size query, store-gathering toggles, OpenPIC setup, and AVR UART functions.

State, dependencies, and risks: the header has no runtime state but encodes hardware address contracts used by board files and bridge code elsewhere. Dependencies include Linux PCI IDs and `pci_controller`. Risks are stale hard-coded windows for board variants and accidental mismatch between Map A/Map B selection and firmware-provided ranges. Test signals are compile coverage and correct PCI/ISA/EUMB behavior on Linkstation and StorCenter style MPC10x boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/mpc10x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/mvme5100.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/mvme5100.c

Purpose: Motorola/Emerson MVME5100 board support, including HAWK PCI host bridge, OpenPIC/i8259 interrupt setup, restart register mapping, and platform-device probing.

Important APIs and control flow: `mvme5100_add_bridge` creates an indirect PCI hose, processes ranges, validates the HAWK device ID, and reads the HAWK memory base used for MPIC access. `mvme5100_pic_init` allocates MPIC at `pci_membase`, assigns an ISU, initializes optional `chrp,iic` i8259 cascade, and reads the PCI intack property. `mvme5100_restart` sets MSR_IP and writes the module reset register. `probe_of_platform_devices` publishes `hawk-bridge` devices.

State, dependencies, and risks: state is `pci_membase`, `restart`, MPIC/i8259 handlers, and machine callbacks. Dependencies include OF `hawk-pci`, `open-pic`, `chrp,iic`, HAWK PCI config registers, and udbg. Risks include failure paths that log but continue with incomplete interrupt setup, physical board register constants, and restart relying on a successful early ioremap. Test signals are HAWK detection, MPIC plus legacy interrupt delivery, platform-device creation, and reset via board register.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/mvme5100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/storcenter.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/storcenter.c

Purpose: Iomega StorCenter board descriptor for MPC8241-based systems.

Important APIs and control flow: `storcenter_device_probe` publishes `soc` devices. `storcenter_setup_pci` scans `mpc10x-pci` nodes and `storcenter_add_bridge` creates an indirect PCI hose using MPC10x Map B config addresses. `storcenter_init_IRQ` allocates an OpenPIC/MPIC with serial and internal interrupt ISUs. `storcenter_restart` disables interrupts, sets MSR_IP to return toward firmware exception space, and spins.

State, dependencies, and risks: state is limited to machine callbacks and MPIC configuration. Dependencies include OF compatible `iomega,storcenter`, MPC10x bridge constants, indirect PCI, and MPIC. Risks include no real reset assertion beyond high exception prefix/spin, hard-coded Map B config access, and sparse error handling. Test signals are PCI enumeration, OF `soc` device creation, MPIC interrupt delivery, and expected restart behavior on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/storcenter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/usbgecko_udbg.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/usbgecko_udbg.c

Purpose: udbg console implementation for USB Gecko EXI adapters on GameCube/Wii, including optional very-early debug setup.

Important APIs and control flow: `ug_io_transaction` performs one EXI chip-select/read-write transaction. Probe sends an adapter identify command on memory-card slots A and B. `ug_putc`, `ug_getc`, and poll variants retry FIFO readiness and install `udbg_putc`, `udbg_getc`, and `udbg_getc_poll` when an adapter is present. `ug_udbg_init` maps the OF `nintendo,flipper-exi` node for final udbg. Under early debug, `udbg_init_usbgecko` uses the fixmap BAT area, probes EXI, installs hooks, and programs BAT 1 to preserve access after MMU init.

State, dependencies, and risks: global state is `ug_io_base`. Dependencies include EXI register layout, OF EXI node, fixmap/BAT setup, udbg globals, and platform-specific physical EXI bases. Risks include busy-wait loops, silent transmit drops after retry exhaustion, fragile early mapping assumptions, and bypassing the normal EXI layer. Test signals are early and final console output, input polling, adapter detection in both slots, and continued output after MMU transition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/usbgecko_udbg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/usbgecko_udbg.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/usbgecko_udbg.h

Purpose: declaration and configuration wrapper for USB Gecko udbg initialization.

Important APIs and control flow: when `CONFIG_USBGECKO_UDBG` is enabled, declares `ug_udbg_init`; otherwise provides an empty inline. Always declares `udbg_init_usbgecko` for early debug builds.

State, dependencies, and risks: state is owned by `usbgecko_udbg.c`; the header controls whether board code calls a real initializer. Dependencies are Kconfig selection and early-debug build paths. Risks are unresolved early-debug symbols if platform constraints are wrong and silent no-op final debug when the option is off. Test signals are compile coverage for enabled/disabled USB Gecko udbg and early debug configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/usbgecko_udbg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/wii.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/wii.c

Purpose: Nintendo Wii machine descriptor and board control for Hollywood MMIO, reset, poweroff, interrupt controller composition, and platform-device population.

Important APIs and control flow: `wii_setup_arch` maps Hollywood control and GPIO blocks and turns off slot LED and sensor bar. `wii_restart` clears the system reset bit in the control reset register; `wii_power_off` assigns the shutdown GPIO to the ARM side, makes it output, drives it high, and spins. `wii_pic_probe` initializes both Flipper and Hollywood PICs, while `define_machine(wii)` uses Flipper as top-level `get_irq`. Device probing populates `nintendo,hollywood` children.

State, dependencies, and risks: state is `hw_ctrl`, `hw_gpio`, `pm_power_off`, and Flipper/Hollywood PIC globals. Dependencies include OF Hollywood control/GPIO/PIC nodes, GPIO ownership semantics shared with Starlet, udbg, and OF platform population. Risks include missing MMIO nodes causing reset/power commands to degrade to spin-only, GPIO ownership assumptions, and separate PIC quiesce ordering at shutdown. Test signals are Wii machine match, LED/sensor-bar state, interrupt delivery through both PICs, platform devices, and reset/poweroff hardware behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/wii.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/fsl_uli1575.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/fsl_uli1575.c

Purpose: Freescale-board PCI fixups for the ALi/ULi M1575 southbridge and related bridge, SATA, PATA, RTC, interrupt-routing, and HPCD sideband quirks.

Important APIs and control flow: `is_quirk_valid` gates most fixups to specific Freescale machines. Early/header/final PCI fixups program PIRQ-to-8259 routing, device interrupt pins, SATA AHCI class, PATA native IRQs, i8259 trigger mode registers, RTC control/alarm masking, and dummy bridge reads needed for RTC access. HPCD-specific fixups disable INTx, enable sideband interrupts, change SATA programming interface, force PATA native mode, and remap SATA IRQ using raw OF interrupt parsing. `uli_init` detects `uli1575` under `fsl_pci_primary` and installs `uli_exclude_device` to hide modem and HD audio functions.

State, dependencies, and risks: state includes the PIRQ mapping table and `ppc_md.pci_exclude_device` override. Dependencies include PCI fixup ordering, machine descriptors, FSL primary PCI node, i8259/CMOS I/O ports, OF IRQ mapping, and ULi-specific config registers. Risks are board-specific magic registers, overlapping fixups for the same device IDs, direct CMOS/ELCR writes, and exclusion logic tied to bus offsets. Test signals are correct interrupt routing for USB/SATA/PATA/SMBus, RTC operation, hidden unsupported functions, and resume-time PATA fixup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/fsl_uli1575.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/microwatt/Kconfig -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/microwatt/Kconfig

Purpose: Kconfig symbol for FPGA-based Microwatt SoC support.

Important APIs and control flow: `PPC_MICROWATT` depends on 64-bit Book3S PowerPC and selects XICS native interrupt support, 16550 udbg, and common clock support. The help text identifies FPGA Microwatt implementations.

State, dependencies, and risks: state is compile-time selection. Dependencies control whether `setup.o`, `rng.o`, and optional SMP support can use XICS and DARN assumptions. Risks are under-specified platform dependencies for evolving Microwatt firmware/device trees. Test signals are defconfig selection, successful link with XICS/native ICP/ICS, and boot on a Microwatt SoC DT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/microwatt/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/microwatt/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/microwatt/Makefile

Purpose: object list for Microwatt platform support.

Important APIs and control flow: always builds `setup.o` and `rng.o`; builds `smp.o` only with `CONFIG_SMP`.

State, dependencies, and risks: state is build-time object inclusion. Dependencies are the `PPC_MICROWATT` Kconfig symbol and optional SMP. Risks are missing SMP release logic when SMP is enabled without `smp.o`, or dead code if RNG support is built for a CPU without usable DARN. Test signals are compile/link coverage for SMP and non-SMP Microwatt builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/microwatt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/microwatt/microwatt.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/microwatt/microwatt.h

Purpose: local Microwatt declarations shared between setup, RNG, and SMP code.

Important APIs and control flow: declares `microwatt_rng_init` and `microwatt_init_smp`; no inline logic is present.

State, dependencies, and risks: state is external to the header. Dependencies are object inclusion by Makefile and `__init` call ordering from `setup.c`. Risks are link failures if declarations and Kconfig object selection drift. Test signals are build coverage for Microwatt SMP and non-SMP configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/microwatt/microwatt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/microwatt/rng.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/microwatt/rng.c

Purpose: Microwatt random-seed provider using the Power ISA DARN instruction.

Important APIs and control flow: `microwatt_get_random_darn` executes `PPC_DARN` with `L=1` for a 64-bit conditioned random value, treats all-ones as failure, and returns success/failure. `microwatt_rng_init` tries up to ten reads and installs `ppc_md.get_random_seed` on the first successful result.

State, dependencies, and risks: state is the machine callback `ppc_md.get_random_seed`; no persistent device state is kept. Dependencies include DARN instruction support, archrandom macros, and Microwatt setup ordering. Risks are CPU/FPGA implementations without a functioning DARN source, no logging on failure, and reliance on all-ones as the only error sentinel. Test signals are boot-time callback installation, entropy reads not returning DARN_ERR, and no illegal-instruction fault on Microwatt builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/microwatt/rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/microwatt/setup.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/microwatt/setup.c

Purpose: Microwatt machine descriptor for interrupts, OF platform population, RNG setup, SMP release, and idle wait.

Important APIs and control flow: `microwatt_probe` always matches compatible `microwatt-soc` and calls `microwatt_init_smp` when SMP is enabled. `microwatt_init_IRQ` initializes XICS. A machine arch initcall runs `of_platform_default_populate`. `microwatt_setup_arch` initializes DARN RNG. `microwatt_idle` prepares for irqsoff idle and executes `wait`. `define_machine(microwatt)` wires progress, power-save, setup, and IRQ callbacks.

State, dependencies, and risks: state is `ppc_md` callbacks and any SMP/RNG state initialized by sibling files. Dependencies include XICS native support, OF compatible string, default platform bus population, udbg, and the CPU `wait` instruction. Risks include unconditional probe return for compatible systems, idle correctness around interrupt preparation, and SMP setup before full device-tree unflattening. Test signals are Microwatt boot, XICS interrupt handling, device population, idle wakeups, RNG callback, and SMP bring-up when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/microwatt/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/microwatt/smp.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/microwatt/smp.c

Purpose: SMP bring-up support for Microwatt FPGA systems.

Important APIs and control flow: `microwatt_init_smp` early-maps a hard-coded syscon block, reads CPU count from `SYSCON_CPU_CTRL`, installs `microwatt_smp_ops` when more than one CPU exists, writes secondary boot instructions at `KERNELBASE`, enables all CPUs through syscon, waits briefly for `__secondary_hold_acknowledge`, and unmaps. SMP ops use XICS probe/setup and generic CPU kick with muxed IPI handling.

State, dependencies, and risks: state is global `smp_ops`, code patched at physical/virtual `KERNELBASE`, and syscon CPU control bits. Dependencies include early_ioremap, raw PowerPC opcodes, XICS SMP helpers, secondary hold protocol, and a hard-coded syscon address noted as needing DT data. Risks are address mismatch on future Microwatt variants, timeout without error propagation, cache coherency of patched boot code, and booting more CPUs than assumed by bitmask width. Test signals are secondary CPU online, XICS per-CPU setup, time to acknowledge hold, and no regression on single-CPU systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/microwatt/smp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/Kconfig -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/Kconfig

Purpose: Kconfig options for PA Semi PWRficient SoC platforms, Nemo motherboard support, IOMMU behavior, and GPIO MDIO.

Important APIs and control flow: `PPC_PASEMI` depends on big-endian PPC64 Book3S and selects MPIC, forced PCI, udbg, hash MMU, and broken MPIC register-read handling. `PPC_PASEMI_NEMO` adds i8259 support for AmigaOne X1000/SB600. `PPC_PASEMI_IOMMU` and `PPC_PASEMI_IOMMU_DMA_FORCE` govern IOB translation and DMA-engine bypass behavior. `PPC_PASEMI_MDIO` builds a PHYLIB GPIO MDIO driver.

State, dependencies, and risks: state is compile-time feature inclusion. Dependencies determine machine descriptor capabilities, IOMMU setup, and southbridge workarounds. Risks include big-endian-only assumptions, optional IOMMU behavior changing DMA addressability, and MDIO default-y pulling platform code into builds with PHYLIB. Test signals are config dependency resolution, Nemo boot with i8259, IOMMU on/off boot, and PA Semi platform link coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/Makefile

Purpose: object list for PA Semi platform core, optional GPIO MDIO, and optional MSI support.

Important APIs and control flow: always builds setup, PCI, time, idle, powersave assembly, IOMMU, DMA library, and misc I2C registration. Adds `gpio_mdio.o` under `CONFIG_PPC_PASEMI_MDIO` and `msi.o` under `CONFIG_PCI_MSI`.

State, dependencies, and risks: state is link-time object inclusion and ordering. Dependencies include Kconfig symbols and exported functions from `dma_lib.c`/`pasemi.h`. Risks are building IOMMU object even when runtime disabled, and optional MSI/MDIO behavior changing PCI/PHY integration. Test signals are link success across MSI/MDIO/IOMMU/Nemo combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/dma_lib.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/dma_lib.c

Purpose: exported PA Semi DMA library for register access, channel allocation, descriptor rings, coherent buffers, flags/events, function engines, and DMA hardware initialization.

Important APIs and control flow: exported register helpers access IOB, MAC, and DMA MMIO windows. `pasemi_dma_init` is guarded by a spinlock, discovers IOB/DMA/MAC PCI functions, maps registers using OF or fallback addresses, maps DMA status memory, reads channel counts, initializes free bitmaps, disables and re-enables TX/RX sections, configures resource allocation, and clears flags. `pasemi_dma_alloc_chan` allocates TX/RX channels from bitmaps, maps IRQs from `base_hw_irq`, and returns an embedded `pasemi_dmachan`; free paths return channel bits and `kfree` the owning allocation. Ring/buffer helpers wrap coherent DMA allocation. Start/stop helpers program channel CMDSTA registers and wait for inactive state. Flag/function allocators use bitmaps and DMA flag registers.

State, dependencies, and risks: global state includes mapped IOB/DMA/MAC registers, DMA status mapping, channel/flag/function bitmaps, channel counts, IRQ base, and retained DMA PCI device. Dependencies include PA Semi PCI device IDs, OF register resources, `asm/pasemi_dma.h`, generic DMA API, irq mappings, and callers obeying initialization order. Risks include `BUG()` on missing devices, limited locking around allocation bitmaps, possible `MAX_FUN` allocator using `MAX_FLAGS` bounds, fallback hard-coded MMIO addresses, and stop timeouts. Test signals are one-time init logging, exported API use by network/crypto clients, channel exhaustion/free behavior, coherent ring DMA, interrupts per channel, and TX/RX stop/start under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/dma_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/gpio_mdio.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/gpio_mdio.c

Purpose: PHYLIB MDIO bus driver that bit-bangs MDIO/MDC over PA Semi GPIO registers.

Important APIs and control flow: GPIO helpers drive set/clear/direction/input registers. `bitbang_pre` sends a 40-bit preamble, start bits, opcode, PHY address, and register address. `gpio_mdio_read` tri-states MDIO for turnaround and samples 16 data bits; `gpio_mdio_write` emits turnaround and 16 data bits then tri-states. `gpio_mdio_probe` allocates `gpio_priv` and `mii_bus`, reads `reg`, `mdc-pin`, and `mdio-pin` from OF, registers with `of_mdiobus_register`, and stores drvdata. Module init maps a `1682m-gpio` or `pasemi,pwrficient-gpio` node before registering the platform driver.

State, dependencies, and risks: state includes global `gpio_regs`, per-bus pin numbers, and registered MII buses. Dependencies include OF GPIO/MDIO properties, PHYLIB, platform devices, and timing via `udelay(1)`. Risks include unchecked missing properties, a global GPIO mapping shared by all buses, manual MDIO timing without locking, and cleanup path using `kfree(new_bus)` instead of `mdiobus_free` on register failure. Test signals are MDIO scan, PHY reads/writes, module unload cleanup, and stable Ethernet PHY detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/gpio_mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/idle.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/idle.c

Purpose: PA6T idle-mode selection and system-reset wake handler for power-saving modes.

Important APIs and control flow: `modes` maps `spin` and `doze` to assembly entry points; early parameter `idle=` selects one. `pasemi_idle_init` installs `pasemi_system_reset_exception` and `ppc_md.power_save`, forcing spin when cpufreq support is absent. The reset exception detects wake causes from `SRR1_WAKEMASK`, redirects return IP to link when waking from power save, re-arms the decrementer for DEC wake, defers external interrupts, restores CPU astate, and marks the exception recoverable.

State, dependencies, and risks: state is `current_mode` and `ppc_md` callbacks. Dependencies include `powersave.S`, cpufreq astate helpers, system-reset exception semantics, and SMP processor IDs. Risks include incorrect return-IP handling for future sleep modes, power-saving disabled without cpufreq, and NMI-context restrictions for external wake. Test signals are idle parameter parsing, wake from decrementer/external interrupt, astate restoration, and no reset-loop on real system reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/idle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/iommu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/iommu.c

Purpose: PA Semi IOB IOMMU setup and DMA mapping integration for PCI devices.

Important APIs and control flow: `iob_init` allocates a 2 MiB low-memory L2 table, a dummy page for invalid entries, maps IOB registers, writes 64 L1 entries, selects a 2 GiB translation window, and enables address translation. `iobmap_build` writes valid L2 entries from physical pages and invalidates IOB TLB entries; `iobmap_free` replaces entries with the dummy-page value and invalidates. `iommu_table_iobmap_setup` initializes common `iommu_table` state and ops. PCI DMA setup lazily initializes the table and assigns it to devices, except the DMA engine bypasses translation outside LPAR unless force is configured. `iommu_init_early_pasemi` honors config and `/chosen/linux,iommu-off`, installs PCI controller DMA hooks, and sets `dma_iommu_ops`.

State, dependencies, and risks: global state includes IOB MMIO, L1/L2 empty values, L2 table base, `iommu_table_iobmap`, and initialization flag. Dependencies include memblock early allocation, firmware LPAR feature, PA IOB registers, generic IOMMU code, and PCI controller ops. Risks include fixed 2 GiB window, panic on allocation/map failures, dummy-page mapping for freed entries, and device-specific DMA-engine bypass differences. Test signals are boot with IOMMU enabled/disabled, DMA mappings for PCI devices, LPAR DMA-engine behavior, and no IOTLB stale translations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/misc.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/misc.c

Purpose: PA Semi miscellaneous device registration, currently I2C board-info population from PCI I2C controller child nodes.

Important APIs and control flow: under `CONFIG_I2C_BOARDINFO`, `find_i2c_driver` maps OF compatible `dallas,ds1338` to I2C type `ds1338`. `pasemi_register_i2c_devices` iterates PA Semi I2C PCI functions (`0xa003`), walks child OF nodes, validates 10-bit addresses from `reg`, maps optional IRQs, fills `i2c_board_info`, and registers it for the PCI function number.

State, dependencies, and risks: state is registered I2C board info. Dependencies include PCI device discovery, OF child nodes, I2C board-info support, and IRQ mapping. Risks include limited compatible table, leaked PCI references in iteration edge cases, address validation only by raw `reg`, and silent skip for unknown devices. Test signals are DS1338 RTC client creation, correct adapter numbering by PCI function, and warnings for invalid I2C child entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/msi.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/msi.c

Purpose: PA Semi MPIC-backed MSI allocation and PCI controller MSI callbacks.

Important APIs and control flow: the MSI chip combines PCI MSI masking with MPIC masking/unmasking and uses MPIC EOI/type/affinity operations. `pasemi_msi_setup_msi_irqs` allocates hardware interrupts in 16-vector chunks from the MPIC MSI bitmap, creates virq mappings, associates MSI descriptors, programs vector zero, sets edge-rising type, and writes an MSI message targeting address `0xfc080000` with data `hwirq - 0x200`. Teardown clears descriptors, disposes mappings, and frees chunks. `mpic_pasemi_msi_init` validates the MPIC compatible string, initializes the allocator, saves the MPIC, and installs callbacks on all PHBs.

State, dependencies, and risks: state is global `msi_mpic`, MPIC MSI bitmap allocations, and PHB controller callbacks. Dependencies include MPIC MSI allocator, PCI MSI core, irqdomain mapping, and PA Semi MSI address/data semantics. Risks include fixed 16-vector allocation granularity, MSI-X noted as untested, callback installation over existing hooks, and teardown freeing whole chunks per descriptor. Test signals are MSI allocation/free under PCI devices, interrupt delivery at the magic address, affinity grouping, and no bitmap leaks after driver removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/msi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/pasemi.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/pasemi.h

Purpose: shared PA Semi platform declarations for time, PCI, DMA setup, register mapping, idle assembly, cpufreq astate hooks, and PCI controller ops.

Important APIs and control flow: declares `pas_get_boot_time`, `pas_pci_init`, `pas_pci_dma_dev_setup`, `pasemi_pci_getcfgaddr`, `pasemi_map_registers`, `idle_spin`, `idle_doze`, and `pasemi_pci_controller_ops`. Provides no-op cpufreq helpers when `CONFIG_PPC_PASEMI_CPUFREQ` is absent so idle code avoids power-saving modes.

State, dependencies, and risks: state is external and spread across PA Semi source files. Dependencies include `struct pci_dev`, MMIO annotations, and optional cpufreq. Risks are mismatched declarations with objects and fallback cpufreq behavior intentionally preventing deeper idle. Test signals are compile coverage across cpufreq enabled/disabled and users of exported PA Semi helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/pasemi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/pci.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/pci.c

Purpose: PA Semi PXP PCI host bridge setup and config-space access operations, with root-port erratum and Nemo SB600 enumeration workaround.

Important APIs and control flow: config addresses are computed by bus/devfn/offset into a large ioremapped PXP window. `pa_pxp_offset_valid` allows 8 KiB only for bus 0 devfn 0, otherwise 4 KiB. `workaround_5945` handles selected root-port registers by writing a dummy register before read and restoring the full word. Nemo `sb600_set_flag` toggles IOB error config so SB600 bus scanning permits nonzero devices only on the SB600 bus. `pa_pxp_read_config`/`pa_pxp_write_config` perform endian-safe MMIO config accesses. `pas_add_bridge` allocates the PCI controller, installs `pasemi_pci_controller_ops`, processes OF ranges, and scans for early ISA bridges. `pas_pci_init` finds `pasemi,rootbus` and enables all PCIe device scanning.

State, dependencies, and risks: state includes hose config mapping, global controller ops, optional cached Nemo IOB mapping, and PCI flags. Dependencies include OF rootbus, PA PXP register layout, ISA bridge discovery, and PCI core access alignment. Risks include huge fixed config ioremap, root-port erratum special cases, Nemo bus-number assumptions, and scanning all PCIe devices increasing exposure to broken endpoints. Test signals are complete PCIe enumeration, config reads for root ports, SB600 devices on Nemo, and absence of machine checks during config scanning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/powersave.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/powersave.S

Purpose: low-level PA6T idle entry routines for spin/doze power-saving modes.

Important APIs and control flow: `idle_spin` simply returns. `idle_doze` loads `_doze` and branches to `sleep_common`. `sleep_common` saves LR/stack, optionally checks cpufreq astate and skips power saving unless astate is zero, disables DR/IR/ME/EE bits from MSR, calls the selected sleep opcode routine, restores MSR and stack state, and returns. `_doze` executes a pre-sleep sync/ptesync sequence and the raw DOZE opcode, then branches to itself if execution continues unexpectedly.

State, dependencies, and risks: state is CPU MSR, stack frame, and optional cpufreq astate. Dependencies include PA6T sleep opcodes, `check_astate`, exception wake handling in `idle.c`, and PowerPC assembly ABI. Risks include running with translation/interrupt bits disabled, wake path relying on system-reset exception repair, and raw opcodes for assembler compatibility. Test signals are idle entry/exit under timer and external interrupts, astate gating, and no stack/MSR corruption after wake.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/powersave.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/setup.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/setup.c

Purpose: PA Semi machine descriptor, platform setup, reset/poweroff, SMP timebase synchronization, MPIC/Nemo IRQ setup, machine-check diagnostics, OF device publication, and early probe.

Important APIs and control flow: `pas_probe` matches PA6T/PWRficient compatibles, applies Nemo poweroff/name changes, and initializes IOMMU early. `pas_setup_arch` installs SMP ops and maps the reset register. SMP timebase callbacks freeze/restart TB and transfer TB value through a spinlock. `pas_init_IRQ` locates OpenPIC, reads `/platform-open-pic`, allocates MPIC with optional MCK/NMI support, initializes ISU, prioritizes NMI, and calls Nemo i8259 cascade setup. `pas_setup_mce_regs` maps PCI config/status registers for later machine-check dumps. `pas_machine_check_handler` handles MPIC NMI by entering debugger or prints SRR/DSISR/BER/MER/IER/DER, SoC debug registers, and SLB contents for certain errors. Device initcall publishes localbus/SDC devices and optional Nemo RTC.

State, dependencies, and risks: state includes reset register mapping, MCE register table, NMI virq, optional Nemo shutdown mapping, SMP timebase lock/value, and `ppc_md` callbacks. Dependencies include OF compatibles/properties, MPIC, i8259 for Nemo, PCI config helper, debugger, SLB/MMU state, and platform devices. Risks include infinite reset/power loops, hard-coded reset/PLD addresses, MCE diagnostics in fragile contexts, partial IRQ setup if OpenPIC properties are missing, and fake boot time from `time.c`. Test signals are PA Semi/Nemo boot, restart/poweroff, SMP bring-up/timebase sync, NMI/debugger behavior, MCE register dumps, and platform-device creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/time.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/time.c

Purpose: PA Semi boot-time provider.

Important APIs and control flow: `pas_get_boot_time` returns a fixed `mktime64(2006, 1, 1, 12, 0, 0)` value and is installed by the PA Semi machine descriptor.

State, dependencies, and risks: there is no runtime state. Dependencies are generic time helpers and `ppc_md.get_boot_time`. Risks are obvious wall-clock inaccuracy until a real RTC/NTP source updates time; this may affect logs and filesystems early in boot. Test signals are machine boot without a real RTC path and subsequent correction by RTC platform devices or userspace time sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/Kconfig -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/Kconfig

Purpose: Kconfig definitions for Apple PowerMac support, 64-bit PowerMac extensions, and 32-bit PowerSurge SMP upgrade cards.

Important APIs and control flow: `PPC_PMAC` selects core PowerMac dependencies such as MPIC, forced PCI, indirect PCI/MPC106 on PPC32, hash MMU support, and optional CUDA reset. `PPC_PMAC64` selects U3 DART, MPIC U3 HT IRQ support, generic timebase sync, and 970 nap. `PPC_PMAC32_PSURGE` enables PowerSurge CPU-card SMP support with muxed IPIs and nomap IRQ domains.

State, dependencies, and risks: state is compile-time platform selection. Dependencies decide which PowerMac files and subsystems are built. Risks are broad default-y coverage, CPU endian/Book3S assumptions, and EXPERT-only SMP upgrade support being lightly tested. Test signals are 32-bit and 64-bit PowerMac build coverage, PowerSurge SMP configs, and correct dependency selection for PCI/MPIC/DART.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/Makefile

Purpose: PowerMac object list and special compiler flags for BootX early boot code.

Important APIs and control flow: `bootx_init.o` is built position-independent, without stack protector, without KASAN instrumentation, and with ftrace removed because it runs before normal runtime support. Core PowerMac objects include PIC, setup, time, feature, PCI, sleep, I2C, cache, platform functions, and udbg. Optional objects add backlight, NVRAM, BootX on PPC32, and SMP.

State, dependencies, and risks: state is build-time object inclusion and per-object instrumentation policy. Dependencies include Kconfig symbols and early-boot constraints. Risks are accidentally instrumenting `bootx_init.o`, NVRAM tristate coercion behavior, and missing optional objects under platform configs. Test signals are PowerMac 32/64 links, BootX boot path without instrumentation faults, and optional backlight/NVRAM/SMP symbols resolving.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/backlight.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/backlight.c

Purpose: shared PowerMac backlight coordination for keyboard/PMU brightness events and legacy 0-15 brightness APIs.

Important APIs and control flow: global `pmac_backlight` stores the active internal display backlight and `pmac_backlight_mutex` protects pointer use. `pmac_has_backlight_type` searches the OF `backlight-control` property. Interrupt-context functions queue work for key brightness changes or PMU legacy brightness setting. Workers check `kernel_backlight_disabled`, update `backlight_properties.brightness`, clamp to bounds, and call `backlight_update_status`. Legacy getters/setters scale between 0-15 and the driver's max brightness. Disable/enable use an atomic nesting counter.

State, dependencies, and risks: state includes work items, queued direction/brightness integers, atomic disable count, mutex, and exported backlight pointer. Dependencies include Linux backlight class, OF backlight node, PMU/ADB event producers, and driver-provided update_status. Risks include coalesced key events losing intermediate changes, disable counter imbalance, one global backlight assumption, and no protection for queued integer races by design. Test signals are brightness key handling, PMU legacy brightness mapping, module users respecting the mutex, and backlight grab/release behavior on old PowerBooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/backlight.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/bootx_init.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/bootx_init.c

Purpose: very-early PPC32 BootX bootloader adapter that validates BootX `boot_infos_t`, optionally displays text, converts the BootX device tree into a flattened device tree, reserves parameters/initrd memory, prepares display/BAT state, and jumps to the normal kernel entry.

Important APIs and control flow: `bootx_init` relocates the GOT, initializes BSS-like globals manually, normalizes old BootX versions, sets up btext display, validates compatibility and architecture, applies an old iMac USB shutdown workaround, computes parameter/ramdisk space, touches pages for old MMU-on BootX, calls `bootx_flatten_dt`, prepares display BAT/unmap, restores GOT, and calls `__start`. `bootx_flatten_dt` builds FDT header, reservation map, string block, and structure block. Tree scanners collect property names, skip `name`, replace `/chosen/bootargs`, add BootX/initrd/stdout/display properties, and sanitize node names with embedded NULs.

State, dependencies, and risks: state is `__initdata` string offsets, chosen node offset, BootX info pointer, and display path. Dependencies include BootX ABI, OF flattened tree format, btext, relocation helpers, page alignment, and pre-MMU memory layout. Risks are early code running without normal BSS/instrumentation, fixed property-size limit, manual FDT construction, compatibility hangs with only text feedback, and ancient firmware workarounds using raw MMIO. Test signals are BootX PPC32 boot, valid FDT seen by prom init, bootargs/initrd/stdout propagation, display console output, and no overlap with reserved parameter/ramdisk memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/bootx_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/cache.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/cache.S

Purpose: low-level PPC32 PowerMac cache flush/disable routines used for sleep, PMU CPU-frequency changes, and CPU offline paths.

Important APIs and control flow: `flush_disable_caches` returns immediately outside PPC Book3S 32-bit, otherwise dispatches by CPU feature to 745x, 75x/G3/G4 L2, or L1-only code. `flush_disable_75x` disables EE/DR, stops AltiVec streams and DPM, displacement-flushes L1/L2 via ROM or RAM workaround, disables/invalidates L1, disables and invalidates L2 using L2CR sequences that run from L1, restores HID0 and MSR. `flush_disable_745x` disables interrupts/data translation, stops prefetch, disables L2 prefetch, performs displacement and `dcbf` flushes, locks/unlocks L1 ways, uses hardware flush for L2 and optional L3, invalidates caches, disables L1 data cache, and restores MSR.

State, dependencies, and risks: state is CPU cache-control SPRs, MSR bits, and cache contents; no C-visible persistent state is kept. Dependencies include CPU feature fixups, HID0/L2CR/L3CR/MSSCR0/LDSTCR semantics, ROM at physical `0xfff00000`, assembler raw instructions, and careful alignment for code that must execute from L1. Risks are CPU-revision errata, data loss if flush ordering is wrong, running with translation disabled, and platform assumption about readable ROM. Test signals are reliable sleep/wake, cpufreq transitions, CPU offline/online, and stress tests detecting no data corruption on G3/G4/745x systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/cache.S -->
