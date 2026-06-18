# Research: subset-b-000796

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/clock-commonclk.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/clock-commonclk.c

## Purpose
`clock-commonclk.c` is the MPC512x common clock provider. It translates CCM reset/configuration registers and device-tree oscillator/bus-frequency data into Linux common-clock objects for MPC5121, MPC5123, and MPC5125 variants, then exposes public clock IDs from `dt-bindings/clock/mpc512x-clock.h`.

## Important APIs, Types, and Functions
The public entry point is `mpc5121_clk_init()`. It maps the `"fsl,mpc5121-clock"` registers, determines the SoC variant, creates fixed/factor/divider/gate/mux clocks, registers an OF onecell provider, and installs fallback `clkdev` aliases. Helpers such as `get_spmf_mult()`, `get_sys_div_x2()`, and `get_cpmf_mult_x2()` decode PLL fields. `mpc512x_clk_setup_clock_tree()` builds the hierarchy from `ref` through `sys`, `csb`, `ips`, and peripheral leaves. `mpc512x_clk_setup_mclk()` handles PSC, MSCAN, SPDIF, and output-clock MCLK subtrees.

## Control Flow, State, and Persistence
State is global boot-time state: `clks[]`, `clk_data`, mapped `clkregs`, `clklock`, and cached `soc`. Missing clocks are preset to `ERR_PTR(-ENODEV)`. The code pre-enables critical internal clocks, console PSC MCLK, and selected compatibility clocks so late clock cleanup does not disable boot-critical hardware.

## Dependencies and Integration Points
It integrates OF clock nodes, MPC512x CCM layout, the common clock framework, `clkdev` migration aliases, legacy DT properties such as `bus-frequency`, and `mpc512x_select_psc_compat()` from shared platform code. Peripheral drivers consume the resulting OF clocks or fallback aliases.

## Risks and Test Signals
Risks include register-field decode errors, variant-specific clock availability, fallback alias mismatches, the apparent SPDIF RX/TX slot overwrite in the external-clock setup, and unsupported MPC5125 NFC timing. Useful tests are boot logs on old and new DTBs, clock summary inspection, PSC serial console stability, PCI/DIU/FEC/USB probe behavior, and rate-change tests for SDHC, DIU, and MCLK users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/clock-commonclk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc5121_ads.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc5121_ads.c

## Purpose
`mpc5121_ads.c` registers the Freescale MPC5121 ADS board machine description and wires board-specific early setup, PCI discovery, interrupt initialization, restart, and common MPC512x initialization.

## Important APIs, Types, and Functions
`mpc5121_ads_setup_arch()` maps CPLD registers early and calls `mpc512x_setup_arch()`. `mpc5121_ads_setup_pci()` scans `"fsl,mpc5121-pci"` nodes and adds MPC83xx-style PCI bridges when PCI is enabled. `mpc5121_ads_init_IRQ()` initializes the MPC512x IPIC and cascaded CPLD PIC. `mpc5121_ads_probe()` calls `mpc512x_init_early()` before the flattened tree is fully available.

## Control Flow, State, and Persistence
The file itself persists no state. It sequences persistent mappings owned by shared MPC512x code and `mpc5121_ads_cpld.c`, then stores board hooks in `define_machine(mpc5121_ads)`.

## Dependencies and Integration Points
It depends on `mpc512x.h`, `mpc5121_ads.h`, IPIC, OF compatible `"fsl,mpc5121ads"`, and FSL PCI bridge support. It is the integration point between common SoC setup and ADS-only CPLD interrupt routing.

## Risks and Test Signals
Risks are mostly ordering-sensitive: CPLD mapping must happen before CPLD IRQ setup, PCI is initialized before the common clock provider is available, and probe returns true after early setup. Tests are ADS boot, PCI enumeration, CPLD interrupt delivery, serial console continuity, and restart behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc5121_ads.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc5121_ads.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc5121_ads.h

## Purpose
`mpc5121_ads.h` is a small board-private header for MPC5121 ADS CPLD support.

## Important APIs, Types, and Functions
It declares `mpc5121_ads_cpld_map()` and `mpc5121_ads_cpld_pic_init()`, both marked `__init`, for use by the ADS machine file.

## Control Flow, State, and Persistence
The header owns no state. It enforces a narrow interface from board setup to the CPLD interrupt implementation.

## Dependencies and Integration Points
It is included by `mpc5121_ads.c` and `mpc5121_ads_cpld.c`. The calls are sequenced so register mapping happens during architecture setup and IRQ-domain setup happens during interrupt initialization.

## Risks and Test Signals
The main risk is interface drift if CPLD initialization gains dependencies not reflected in this header. Build coverage for `CONFIG_MPC5121_ADS` and boot-time CPLD IRQ tests are sufficient signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc5121_ads.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc5121_ads_cpld.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc5121_ads_cpld.c

## Purpose
`mpc5121_ads_cpld.c` implements the ADS board cascaded CPLD interrupt controller. The CPLD exposes PCI and miscellaneous interrupt status/mask registers behind one upstream interrupt.

## Important APIs, Types, and Functions
`mpc5121_ads_cpld_map()` locates and maps `"fsl,mpc5121ads-cpld-pic"`. `mpc5121_ads_cpld_pic_init()` configures routing/masks, creates a 16-entry linear irq domain, and attaches `cpld_pic_cascade()` as the chained handler. The `cpld_pic` irq chip masks, unmasks, and acks by modifying PCI or misc mask bytes. `cpld_pic_get_irq()` picks the first unmasked active-low status bit after ignore masks.

## Control Flow, State, and Persistence
Persistent state consists of `cpld_regs`, `cpld_pic_node`, and `cpld_pic_host`. Interrupt handling first checks PCI status bits, then misc status bits, and dispatches the first pending hwirq to the domain.

## Dependencies and Integration Points
It depends on OF address/IRQ parsing, generic irq domains, chained irq handlers, and the ADS board file. Touchscreen pendown is explicitly ignored because it is routed directly to IPIC IRQ1.

## Risks and Test Signals
Risks include active-low bit assumptions, only servicing one pending CPLD interrupt per cascade entry, missing cleanup for permanent init-time mappings, and route/mask values tied to board wiring. Test signals include PCI slot IRQs, miscellaneous CPLD IRQs, touchscreen direct IRQ behavior, and logs for missing node, failed cascade mapping, or failed irq-domain allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc5121_ads_cpld.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc512x.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc512x.h

## Purpose
`mpc512x.h` declares the common MPC512x platform services shared by board files and drivers.

## Important APIs, Types, and Functions
It exposes `mpc512x_init_early()`, `mpc512x_init_IRQ()`, `mpc512x_setup_arch()`, `mpc512x_init()`, `mpc512x_restart()`, `mpc5121_clk_init()`, `mpc512x_select_psc_compat()`, and `mpc512x_cs_config()`.

## Control Flow, State, and Persistence
The header owns no data but defines call ordering: early reset/DIU preservation, architecture setup, clock/device/FIFO initialization, IRQ setup, and restart support.

## Dependencies and Integration Points
It is consumed by MPC5121 ADS, generic MPC512x, PDM360NG, the clock provider, and shared code. `mpc512x_cs_config()` is exported for LocalPlus Bus clients.

## Risks and Test Signals
Risks are ABI-like: board files rely on these function names and semantics. Build coverage across all MPC512x board configs and boot coverage on MPC5121 and MPC5125-like DTs validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc512x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc512x_generic.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc512x_generic.c

## Purpose
`mpc512x_generic.c` registers a generic MPC512x machine for boards that can rely on shared SoC support with no board-specific setup.

## Important APIs, Types, and Functions
`mpc512x_generic_probe()` performs early common initialization and returns true only for `"fsl,mpc5121"`, `"fsl,mpc5123"`, or `"fsl,mpc5125"` machines that are not `"fsl,mpc5121ads"` or `"ifm,ac14xx"`. The `define_machine(mpc512x_generic)` hooks shared setup, init, IRQ, `ipic_get_irq`, and restart callbacks.

## Control Flow, State, and Persistence
No file-local state is persisted. The probe-time exclusion list prevents a generic machine from stealing boards with custom setup requirements.

## Dependencies and Integration Points
It integrates OF machine compatible matching, shared MPC512x initialization, IPIC interrupt handling, and the common clock/device population path.

## Risks and Test Signals
Risks include generic matching a board that actually needs board-specific GPIO, CPLD, or power setup, and omission of future custom boards from the exclusion list. Test signals are successful generic DT boots, no duplicate machine match for ADS/PDM360NG, device population, and restart behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc512x_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc512x_lpbfifo.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc512x_lpbfifo.c

## Purpose
`mpc512x_lpbfifo.c` is the platform driver for the MPC512x LocalPlus Bus FIFO/SCLPC block. It lets clients submit one DMA-backed transfer between RAM and a LocalPlus Bus device.

## Important APIs, Types, and Functions
The exported API is `mpc512x_lpbfifo_submit(struct mpc512x_lpbfifo_request *req)`. `mpc512x_lpbfifo_probe()` maps registers, requests DMA channel `"rx-tx"`, parses LocalPlus chip-select ranges, maps the IRQ, and requests the handler. `mpc512x_lpbfifo_kick()` validates alignment, chooses bytes-per-transaction, resolves chip select, maps RAM for DMA, configures DMA slave parameters, resets/configures FIFO registers, starts SCLPC, and submits the DMA descriptor. Completion is coordinated by `mpc512x_lpbfifo_irq()` and `mpc512x_lpbfifo_callback()`.

## Control Flow, State, and Persistence
All runtime state lives in the global `lpbfifo` struct protected by a spinlock. Only one request can be active. Writes wait for both the LPBFIFO success IRQ and DMA callback; reads skip the LPBFIFO success IRQ to avoid disabling DMA reads and complete on DMA callback.

## Dependencies and Integration Points
It depends on the DMAengine slave API, OF platform matching `"fsl,mpc512x-lpbfifo"`, LocalPlus `"ranges"` parsing from `"fsl,mpc5121-localbus"`, MPC512x SCLPC register definitions, and external request producers.

## Risks and Test Signals
Risks include singleton global state, no request queueing, strict alignment/port-size behavior, reliance on localbus ranges with zero bus base, completion races, and read-path IRQ suppression. Tests should cover write and read transfers, invalid alignment, chip-select range rejection, concurrent submit returning `-EBUSY`, DMA mapping failures, module removal during idle/active states, and hardware FIFO error interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc512x_lpbfifo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc512x_shared.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc512x_shared.c

## Purpose
`mpc512x_shared.c` contains common MPC512x SoC support: restart mapping, DIU framebuffer handoff, IPIC setup, platform-device population, PSC FIFO sizing, chip-select configuration, and board-shared init sequencing.

## Important APIs, Types, and Functions
`mpc512x_restart()` resets through the reset module. `mpc512x_init_early()` maps restart support and preserves pre-initialized DIU state when enabled. `mpc512x_init()` initializes clocks, populates OF devices, and configures PSC FIFO slices. `mpc512x_setup_arch()` installs DIU callbacks. `mpc512x_init_IRQ()` initializes IPIC and default priorities. `mpc512x_select_psc_compat()` chooses PSC compatible strings, and exported `mpc512x_cs_config()` writes LocalPlus chip-select config.

## Control Flow, State, and Persistence
Persistent boot state includes `reset_module_base`, `diu_shared_fb`, and a cached LPC mapping in `mpc512x_cs_config()`. DIU preservation copies area descriptor/gamma data, reserves the existing framebuffer with memblock, and releases those pages when fbdev opens.

## Dependencies and Integration Points
It integrates the common clock provider, OF platform bus probing, FSL DIU framebuffer hooks, memblock, IPIC, PSC FIFO hardware layout, and LocalPlus Bus clients.

## Risks and Test Signals
Risks include bootloader-dependent DIU handoff, permanent mappings, FIFO space exhaustion across PSC nodes, integer/pointer casts in `FIFOC`, missing reset nodes, and static LPC mapping lifetime. Test signals include display continuity during boot, memblock release on fbdev open, PSC serial/FIFO operation, LocalPlus chip-select writes, OF device population, and restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc512x_shared.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/pdm360ng.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/pdm360ng.c

## Purpose
`pdm360ng.c` registers the IFM PDM360NG/AC14xx MPC512x board and provides board glue for the ADS7846 touchscreen pendown GPIO.

## Important APIs, Types, and Functions
`pdm360ng_probe()` excludes non-`"ifm,ac14xx"` systems and calls `mpc512x_init_early()`. `pdm360ng_init()` runs common MPC512x init and touchscreen setup. When `CONFIG_TOUCHSCREEN_ADS7846` is enabled, `pdm360ng_touchscreen_init()` maps `"fsl,mpc5121-gpio"`, registers an SPI bus notifier, and injects `ads7846_platform_data` for `spi32766.1`.

## Control Flow, State, and Persistence
The file keeps a permanent GPIO mapping in `pdm360ng_gpio_base` for pendown reads and a notifier block in the SPI bus notifier chain. The pendown callback tests GPIO bit 29 from the simple GPIO input register area.

## Dependencies and Integration Points
It integrates shared MPC512x setup, OF compatible `"ifm,ac14xx"`, the SPI bus notifier path, ADS7846 platform data, and board-specific GPIO wiring.

## Risks and Test Signals
Risks include hard-coded SPI device name `"spi32766.1"`, permanent GPIO mapping, fragile GPIO offset/bit assumptions, and no notifier unregister path for init-only board code. Test signals are touchscreen probe receiving platform data, pendown interrupt/value correctness, generic MPC512x machine not matching AC14xx, and normal shared device population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/pdm360ng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/Kconfig -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/Kconfig

## Purpose
`52xx/Kconfig` defines build-time platform options for MPC52xx/MPC5200 boards and board-specific quirks.

## Important APIs, Types, and Functions
The main symbol `PPC_MPC52xx` depends on 32-bit Book3S and selects common clock and PCI capability. Board symbols include `PPC_MPC5200_SIMPLE`, `PPC_EFIKA`, `PPC_LITE5200`, and `PPC_MEDIA5200`. `PPC_MPC5200_BUGFIX` enables original MPC5200 errata workarounds.

## Control Flow, State, and Persistence
No runtime state is present. The file controls which board files, PM files, and PCI code are compiled through the corresponding Makefile.

## Dependencies and Integration Points
It integrates with `arch/powerpc` platform selection, Makefile objects, RTAS and native hash MMU requirements for Efika, and firmware assumptions for simple boards.

## Risks and Test Signals
Risks include selecting generic support for boards whose firmware does not initialize GPIO/CDM/PCI safely, and enabling bugfix paths that affect PCI config access. Test signals are Kconfig dependency resolution and build coverage for each board option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/Makefile

## Purpose
`52xx/Makefile` maps MPC52xx Kconfig symbols to common and board-specific object files.

## Important APIs, Types, and Functions
It always builds `mpc52xx_pic.o`, `mpc52xx_common.o`, and `mpc52xx_gpt.o`. PCI adds `mpc52xx_pci.o`. Board options add `mpc5200_simple.o`, `efika.o`, `lite5200.o`, and `media5200.o`. PM adds generic sleep/PM objects, and Lite5200 PM adds board-specific sleep/PM objects.

## Control Flow, State, and Persistence
This is build-time control only. Object inclusion determines which `define_machine()` instances and suspend implementations exist in the final kernel.

## Dependencies and Integration Points
It integrates Kconfig symbols with the PowerPC platform build and makes GPT/PIC/common code baseline for every MPC52xx build.

## Risks and Test Signals
Risks are incorrect object gating, especially PM object combinations and always-on GPT driver inclusion. Test signals are allyesconfig/allmodconfig-style builds and targeted builds for simple, Efika, Lite5200, and Media5200.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/efika.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/efika.c

## Purpose
`efika.c` supports the bPlan Efika 5K2 MPC5200B computer, including RTAS-backed PCI config access, power management hooks, CPU info, and machine registration.

## Important APIs, Types, and Functions
When PCI is enabled, `rtas_read_config()` and `rtas_write_config()` implement `pci_ops` through RTAS tokens. `efika_pcisetup()` finds the root PCI node, allocates a controller, sets bus ranges, and processes OF ranges. `efika_probe()` identifies model `"EFIKA5K2"`, adjusts DMA mode constants, and sets `pm_power_off`. `efika_setup_arch()` initializes RTAS, maps common MPC52xx devices, and installs standby wakeup setup.

## Control Flow, State, and Persistence
The file persists machine hooks and global RTAS power-off/restart integration. PM state is delegated to common MPC52xx suspend with board wakeup GPIO configured on GPIO_WKUP_4.

## Dependencies and Integration Points
It depends on RTAS, OF root properties, MPC52xx common mapping, the generic MPC52xx PIC, and optional common PM code.

## Risks and Test Signals
Risks include RTAS token availability, root PCI node assumptions, DMA mode global changes, and wakeup wiring comments being board-specific. Test signals are Efika model detection, PCI config reads/writes through RTAS, `/proc/cpuinfo` fields, power-off/restart, and suspend/resume via the IRDA connector wake line.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/efika.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/lite5200.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/lite5200.c

## Purpose
`lite5200.c` provides Freescale Lite5200/Lite5200B board support and firmware-fixup code for clock and GPIO port configuration.

## Important APIs, Types, and Functions
`lite5200_fix_clock_config()` configures the CDM 48 MHz source and frequency divider counters. `lite5200_fix_port_config()` adjusts GPIO port muxing for internal 48 MHz, USB differential mode, and ATA chip selects. PM hooks `lite5200_suspend_prepare()` and `lite5200_resume_finish()` configure a wakeup GPIO and USB power. `lite5200_setup_arch()` maps common devices, configures XLB arbitration, applies fixups, and installs Lite5200 PM ops.

## Control Flow, State, and Persistence
Register writes persist in CDM/GPIO hardware for the boot session. PM callback pointers are stored in the global `mpc52xx_suspend` struct, and the machine definition installs MPC52xx PCI/PIC/restart hooks.

## Dependencies and Integration Points
It integrates common MPC52xx mapping, XLB setup, generic PCI, generic PIC, and Lite5200-specific PM implementation in `lite5200_pm.c`.

## Risks and Test Signals
Risks include Linux compensating for firmware configuration, hard-coded register-bit assumptions, USB power sequencing before OHCI suspend, and differences between Lite5200 and Lite5200B. Test signals are USB/ATA operation, serial console, XLB stability, suspend-to-standby and suspend-to-RAM, resume USB power, and successful boot on both compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/lite5200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/lite5200_pm.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/lite5200_pm.c

## Purpose
`lite5200_pm.c` implements Lite5200 platform suspend operations. It delegates standby to generic MPC52xx deep sleep and implements suspend-to-RAM with Lite5200-specific register save/restore and assembly low-power entry.

## Important APIs, Types, and Functions
`lite5200_pm_init()` installs `lite5200_pm_ops`. `lite5200_pm_begin()` records target state. `lite5200_pm_prepare()` maps IMMR and derives CDM, PIC, GPIO, PCI, SDMA, XLB, SRAM, and MBAR pointers for `PM_SUSPEND_MEM`. `lite5200_save_regs()` and `lite5200_restore_regs()` preserve hardware blocks not bound to normal devices. `lite5200_pm_enter()` saves state, enables FP state preservation, calls `lite5200_low_power()`, restores state, and unmaps registers.

## Control Flow, State, and Persistence
Global mapped pointers, saved register structs, `spci`, and `lite5200_pm_target_state` hold suspend state across low-power entry. SRAM contents are saved in `saved_sram` from generic PM code.

## Dependencies and Integration Points
It depends on `lite5200_sleep.S`, common MPC52xx PM helpers, IMMR layout, BestComm/SDMA registers, and PowerPC FP context handling.

## Risks and Test Signals
Risks include incomplete register save/restore, fixed IMMR offsets, ioremap failures, no cleanup on some prepare failures, and subtle FP/SRAM interactions. Test signals are repeated standby and mem suspend cycles, PCI/BestComm/GPIO functionality after resume, wake event behavior, and no SRAM corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/lite5200_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/lite5200_sleep.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/lite5200_sleep.S

## Purpose
`lite5200_sleep.S` contains the low-level Lite5200 suspend-to-RAM assembly path used by `lite5200_pm.c`.

## Important APIs, Types, and Functions
The exported entry is `lite5200_low_power(sram, mbar)`. The file saves and restores core registers, BATs, segment registers, SPRGs, debug registers, and timebase state through local helper routines. It programs SDRAM self-refresh, wakeup behavior for the helper MCU/U-Boot path, cache state, and resumes back into the C restore path.

## Control Flow, State, and Persistence
It stores CPU state in a static `registers` area and executes critical code with MMU/cache assumptions tailored to MPC5200. It temporarily relies on SRAM/MBAR mappings supplied by the C PM layer.

## Dependencies and Integration Points
It depends on MPC5200 SDRAM/CDM/GPIO register offsets, PowerPC SPR names, `CONFIG_KERNEL_START`, and the C-side saved SRAM/register buffers.

## Risks and Test Signals
Risks are high because register ordering, cache flushing, BAT restoration, and wake-vector setup must be exact. Test signals are reliable resume from `PM_SUSPEND_MEM`, restored timebase and debug registers, stable MMU mappings after resume, and no corruption of early RAM/SRAM contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/lite5200_sleep.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/media5200.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/media5200.c

## Purpose
`media5200.c` supports Freescale Media5200 boards and their FPGA cascaded interrupt controller for external IRQs, especially PCI interrupts.

## Important APIs, Types, and Functions
`media5200_init_irq()` initializes the standard MPC52xx PIC, maps `"fsl,media5200-fpga"`, disables FPGA IRQs, creates a six-entry irq domain, and installs `media5200_irq_cascade()`. The `media5200_irq_chip` masks/unmasks FPGA enable bits. `media5200_setup_arch()` maps common devices, configures XLB arbitration, and adjusts GPIO port config for ATA chip selects.

## Control Flow, State, and Persistence
Global `media5200_irq` holds mapped FPGA registers, lock, and irq domain. The cascade masks the upstream interrupt, computes pending enabled FPGA IRQs, dispatches one child IRQ, then acks/unmasks upstream.

## Dependencies and Integration Points
It depends on MPC52xx PIC support, OF IRQ/address parsing, GPIO register layout, generic MPC52xx PCI/restart, and board FPGA interrupt semantics.

## Risks and Test Signals
Risks include possible confusion of status/enable variable names, one-child-per-cascade dispatch, missing FPGA causing PCI interrupt loss, and board-specific GPIO writes. Test signals are PCI IRQ delivery through FPGA, each of six child IRQs, no interrupt storm after mask/ack, and boot logs for missing FPGA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/media5200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc5200_simple.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc5200_simple.c

## Purpose
`mpc5200_simple.c` provides a generic MPC5200 machine for boards whose firmware correctly configures GPIO, clocks, watchdog safety, and optional PCI.

## Important APIs, Types, and Functions
`mpc5200_simple_setup_arch()` maps common MPC52xx devices and configures XLB arbitration. The `board[]` compatible list covers several vendors and boards. `define_machine(mpc5200_simple_platform)` wires shared PCI, OF device population, PIC, IRQ, and restart hooks.

## Control Flow, State, and Persistence
The file itself persists no state. Runtime state is in shared MPC52xx common/PIC/PCI code.

## Dependencies and Integration Points
It integrates with OF compatible matching, `mpc52xx_map_common_devices()`, `mpc5200_setup_xlb_arbiter()`, generic PCI setup, and standard MPC52xx interrupt/restart handling.

## Risks and Test Signals
Risks are firmware assumptions: the generic platform will not correct board-specific muxing or clock mistakes. Test signals are boots for every compatible, watchdog reset only when DT marks a safe GPT, PCI enumeration when a PCI node exists, and device probing from OF population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc5200_simple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc52xx_common.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc52xx_common.c

## Purpose
`mpc52xx_common.c` provides common MPC52xx services for device mapping, OF platform population, XLB arbitration, PSC clock divisors, watchdog restart, and AC97 GPIO reset.

## Important APIs, Types, and Functions
`mpc52xx_map_common_devices()` permanently maps watchdog GPT, CDM, simple GPIO, and wakeup GPIO. `mpc5200_setup_xlb_arbiter()` sets XLB priorities and applies original MPC5200 pipelining erratum handling. `mpc52xx_declare_of_platform_devices()` populates supported bus nodes. Exported `mpc52xx_set_psc_clkdiv()` programs PSC MCLK dividers. `mpc52xx_restart()` resets through GPT watchdog. Exported `mpc5200_psc_ac97_gpio_reset()` bit-bangs AC97 cold reset through GPIO.

## Control Flow, State, and Persistence
Global mappings `mpc52xx_wdt`, `mpc52xx_cdm`, `simple_gpio`, and `wkup_gpio` persist for restart and exported helper use. Spinlocks protect CDM and GPIO register updates.

## Dependencies and Integration Points
It depends on OF match tables, MPC52xx register structs, gpt `fsl,has-wdt` properties, platform bus population, and AC97/PSC clients.

## Risks and Test Signals
Risks include permanent mappings, missing watchdog preventing restart, PSC ID restrictions, bootloader-dependent XLB state, and temporary GPIO mux changes during AC97 reset. Test signals are restart, PSC audio clocking, AC97 cold reset on PSC1/PSC2, OF device registration, and erratum behavior on MPC5200 versus MPC5200B.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc52xx_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc52xx_gpt.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc52xx_gpt.c

## Purpose
`mpc52xx_gpt.c` is the driver for MPC5200 General Purpose Timers as GPIO controllers, cascaded IRQ controllers, timer APIs, and optionally GPT0 watchdog.

## Important APIs, Types, and Functions
The driver registers as `mpc52xx-gpt` at `subsys_initcall`. `mpc52xx_gpt_probe()` maps registers, records bus frequency, sets up GPIO and IRQ domains from DT properties, adds the timer to a global list, and configures watchdog capability. Exported APIs include `mpc52xx_gpt_from_irq()`, `mpc52xx_gpt_start_timer()`, `mpc52xx_gpt_stop_timer()`, and `mpc52xx_gpt_timer_period()`. Watchdog support registers `/dev/watchdog` when `CONFIG_MPC5200_WDT` is enabled.

## Control Flow, State, and Persistence
Each GPT has `mpc52xx_gpt_priv` with register mapping, raw spinlock, irq domain, bus frequency, GPIO chip, and watchdog mode bits. A global list is protected by `mpc52xx_gpt_list_mutex`. Watchdog mode blocks normal timer operations while active.

## Dependencies and Integration Points
It integrates platform devices from OF, gpiolib, irq domains, misc watchdog ABI, IPB bus-frequency helpers, and DT properties `gpio-controller`, `interrupt-controller`, `fsl,has-wdt`, and `fsl,wdt-on-boot`.

## Risks and Test Signals
Risks include multiplexing one hardware pin as GPIO and IRQ, watchdog `NOWAYOUT` semantics, period calculation limits, no remove path, and DT-encoded IRQ flags. Test signals are GPIO get/set/direction, edge IRQ delivery, timer period accuracy, watchdog open/ioctl/release behavior, GPT0 busy rejection, and early availability before dependent drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc52xx_gpt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc52xx_pci.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc52xx_pci.c

## Purpose
`mpc52xx_pci.c` implements the MPC52xx PCI host bridge setup, config-space accessors, inbound/outbound windows, and resource fixups.

## Important APIs, Types, and Functions
`mpc52xx_setup_pci()` finds a matching PCI node and calls `mpc52xx_add_bridge()`. `mpc52xx_add_bridge()` allocates a PCI controller, sets bus ranges and ops, maps PCI registers, processes OF ranges, and calls `mpc52xx_pci_setup()`. Config accessors use CAR and cfg-data windows with optional original MPC5200 bugfix paths for type-1 cycles. `mpc52xx_pci_fixup_resources()` forces resource reassignment and hides the host bridge's fixed 1 GiB prefetch BAR.

## Control Flow, State, and Persistence
The PCI controller and mapped registers persist after setup. Hardware window registers are programmed for memory and I/O resources from DT.

## Dependencies and Integration Points
It depends on OF PCI nodes, `pci_process_bridge_OF_ranges()`, `pcibios_alloc_controller()`, PowerPC PCI hooks, and `CONFIG_PPC_MPC5200_BUGFIX`.

## Risks and Test Signals
Risks include incorrect endian/width config accesses, erratum path regressions, missing bus-range fallback assumptions, resource window translation errors, and intentionally not resetting external PCI bus. Test signals are PCI enumeration, config read/write on bus 0 and subordinate buses, resource reassignment, host-bridge BAR suppression, and device operation on original MPC5200.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc52xx_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc52xx_pic.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc52xx_pic.c

## Purpose
`mpc52xx_pic.c` implements the MPC5200 interrupt controller and its Linux irq-domain mapping for critical, main, peripheral, and synthetic BestComm/SDMA task interrupts.

## Important APIs, Types, and Functions
`mpc52xx_init_irq()` maps PIC and SDMA registers, disables/masks sources, sets default priorities, creates a linear irq domain, and installs it as default. `mpc52xx_get_irq()` decodes encoded interrupt status and maps hardware IRQs to virqs. Separate irq chips handle external IRQs, main, peripheral, and SDMA sources. `mpc52xx_irqhost_xlate()` translates three-cell DT interrupt specs.

## Control Flow, State, and Persistence
Global `intr`, `sdma`, and `mpc52xx_irqhost` persist for all interrupt handling. External IRQ sense types are programmed through PIC `ctrl`; internal interrupts are level-handled and mask/unmask hardware groups.

## Dependencies and Integration Points
It integrates OF PIC and BestComm nodes, generic irq domains, the PowerPC `ppc_md.get_irq` hook, SDMA task interrupt demultiplexing, and external IRQ DT bindings.

## Risks and Test Signals
Risks include unsupported critical IRQs other than IRQ0, BestComm pending-bit decoding, sense-type translation errors, and panic on missing PIC/SDMA mappings. Test signals are external IRQ edge/level behavior, peripheral IRQs, SDMA task IRQs, no spurious interrupts after initialization, and correct `interrupts = <l1 l2 sense>` mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc52xx_pic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc52xx_pm.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc52xx_pm.c

## Purpose
`mpc52xx_pm.c` implements generic MPC52xx standby/deep-sleep suspend and board callback hooks for wakeup and resume finishing.

## Important APIs, Types, and Functions
`mpc52xx_pm_init()` installs `mpc52xx_pm_ops`. `mpc52xx_pm_prepare()` maps IMMR, derives SDRAM/CDM/PIC/GPIO/SRAM pointers, and calls board `board_suspend_prepare`. `mpc52xx_set_wakeup_gpio()` configures a wakeup GPIO input and interrupt level. `mpc52xx_pm_enter()` saves SRAM and a temporary low-memory IRQ handler, copies `mpc52xx_ds_sram` into SRAM, configures sleep clocks, enters `mpc52xx_deep_sleep()`, then restores state. `mpc52xx_pm_finish()` calls board resume callback and unmaps IMMR.

## Control Flow, State, and Persistence
Global pointers and `saved_sram` hold suspend state. Board callbacks are stored in exported `mpc52xx_suspend`. The code temporarily overwrites code at `CONFIG_KERNEL_START + 0x500` with the cached wake handler and restores it after wake.

## Dependencies and Integration Points
It depends on `mpc52xx_sleep.S`, board files assigning wake callbacks, PowerPC timebase/HID0/MSR control, and fixed MPC5200 IMMR offsets.

## Risks and Test Signals
Risks include invasive low-memory handler replacement, SRAM size assumptions, missing board wake callback, cache/icache coherency, and interrupt masking restoration. Test signals are standby suspend/resume, wake GPIO behavior, restored SRAM contents, stable interrupts after resume, and repeated cycles on Lite5200/Efika.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc52xx_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc52xx_sleep.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc52xx_sleep.S

## Purpose
`mpc52xx_sleep.S` contains the low-level generic MPC52xx deep-sleep code copied into SRAM and the cached wake interrupt handler.

## Important APIs, Types, and Functions
`mpc52xx_deep_sleep(sram, sdram, cdm, intr)` enables interrupts, emulates a timer interrupt to prime the cached handler, locks icache, branches to SRAM code, and returns after wake. `mpc52xx_ds_sram` puts SDRAM into self-refresh, disables the SDRAM clock, sets `MSR_POW`, then restores clocks and SDRAM. `mpc52xx_ds_cached` is the wake handler that disables emulated interrupt, acknowledges wakeup, sets a flag, and returns from interrupt. Size symbols expose copy lengths.

## Control Flow, State, and Persistence
The C PM code copies SRAM and cached sections into special execution locations. The assembly uses registers as a wake flag protocol and directly touches IMMR offsets.

## Dependencies and Integration Points
It depends on `mpc52xx_pm.c`, MPC5200 SDRAM/CDM/PIC register layout, PowerPC cache/HID0/MSR behavior, and `CONFIG_KERNEL_START`.

## Risks and Test Signals
Risks include executing from wrong memory, stale instruction cache, wake handler size exceeding saved buffer, SDRAM self-refresh sequencing, and assumptions about timer interrupt emulation. Test signals are successful wake from standby, no data corruption, restored code at low vector area, and no interrupt-controller deadlock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc52xx_sleep.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/82xx/Kconfig -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/82xx/Kconfig

## Purpose
`82xx/Kconfig` defines PowerQUICC II/82xx board support options.

## Important APIs, Types, and Functions
`PPC_82xx` depends on 32-bit Book3S and selects `FSL_SOC`. `EP8248E` selects CPM2, indirect PCI when PCI is enabled, PHYLIB, and MDIO bit-bang support. `MGCOGE` selects CPM2 and optional indirect PCI.

## Control Flow, State, and Persistence
The file has build-time effects only. It controls whether common PQ2 restart code and board-specific EP8248E/KM82xx files are compiled.

## Dependencies and Integration Points
It integrates with `82xx/Makefile`, CPM2 support, PHY/MDIO stacks, and board device-tree compatibles.

## Risks and Test Signals
Risks include missing selects for board-required subsystems and accidental builds without CPM2 or MDIO support. Test signals are configuration dependency checks and targeted builds for EP8248E and MGCOGE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/82xx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/82xx/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/82xx/Makefile

## Purpose
`82xx/Makefile` maps PQ2/82xx config symbols to object files.

## Important APIs, Types, and Functions
`pq2.o` is built with `CONFIG_CPM2`, `ep8248e.o` with `CONFIG_EP8248E`, and `km82xx.o` with `CONFIG_MGCOGE`.

## Control Flow, State, and Persistence
This is build-time state only. The common restart implementation is tied to CPM2 availability, while each board object contributes its own machine definition.

## Dependencies and Integration Points
It integrates Kconfig board symbols with the PowerPC platform build and the shared CPM2/PQ2 support.

## Risks and Test Signals
Risks are minimal but include omitting common PQ2 code for a board that needs `pq2_restart()`. Test signals are successful targeted board builds and link resolution for machine hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/82xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/82xx/ep8248e.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/82xx/ep8248e.c

## Purpose
`ep8248e.c` supports the Embedded Planet EP8248E/QUICCStart MPC8248 board, including CPM2 pin/clock setup, BCSR-controlled PHY/USB/MDIO wiring, cascaded CPM2 PIC, and machine registration.

## Important APIs, Types, and Functions
`ep8248e_setup_arch()` resets CPM2, applies SIU18 workaround by clearing `MPC82XX_BCR_PLDP`, maps BCSR, enables SCC2 and PHY power, and calls `init_ioports()`. `ep8248e_pic_init()` initializes `"fsl,pq2-pic"`. The MDIO bit-bang ops manipulate BCSR8 bits; `ep8248e_mdio_probe()` registers an OF MDIO bus. `declare_of_platform_devices()` probes simple-bus and BCSR children and registers the MDIO driver when enabled.

## Control Flow, State, and Persistence
Global `ep8248e_bcsr` and `ep8248e_bcsr_node` persist after setup. Pinmux and clock assignments are static board policy. MDIO uses shared `ep8248e_mdio_ctrl`.

## Dependencies and Integration Points
It depends on CPM2 IO/clock helpers, CPM2 PIC, OF platform bus, MDIO bit-bang, PHYLIB, BCSR DT nodes, and `pq2_restart()`.

## Risks and Test Signals
Risks include BCSR mapping failure disabling board features, MDIO parent-node checks, hardware-specific pin tables, and SIU18 workaround side effects. Test signals are Ethernet PHY detection over bit-bang MDIO, CPM2 serial/Ethernet/USB operation, CPM2 interrupt delivery, and restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/82xx/ep8248e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/82xx/km82xx.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/82xx/km82xx.c

## Purpose
`km82xx.c` supports Keymile MGCOGE/KM82xx boards with CPM2 pinmux, clock routing, CPM2 PIC, and machine registration.

## Important APIs, Types, and Functions
`km82xx_pic_init()` finds `"fsl,pq2-pic"` and initializes CPM2 PIC. `init_ioports()` applies the board `km82xx_pins` table with `cpm2_set_pin()`, configures SMC/SCC/FCC clocks, and sets USB full-speed/slave-related IO data bits. `km82xx_setup_arch()` resets CPM2, applies the SIU18 snooping workaround, and initializes IO ports.

## Control Flow, State, and Persistence
The file persists no custom mappings; hardware state is programmed into CPM2 IO and clock registers during setup. The machine definition registers shared `pq2_restart()` and `cpm2_get_irq`.

## Dependencies and Integration Points
It depends on CPM2 core support, CPM2 PIC, OF `simple-bus` population, Keymile compatible `"keymile,km82xx"`, and `udbg_progress`.

## Risks and Test Signals
Risks include static pin tables not matching board revisions, CPM clock misrouting, and USB bit assumptions. Test signals are serial ports, SCC/FCC Ethernet, USB mode, CPM2 interrupts, simple-bus device creation, and restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/82xx/km82xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/82xx/pq2.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/82xx/pq2.c

## Purpose
`pq2.c` provides common PowerQUICC II restart support.

## Important APIs, Types, and Functions
`pq2_restart(char *cmd)` disables local interrupts, sets the checkstop reset-enable bit in the CPM2 reset module, clears MSR machine-check, external-interrupt, instruction-translation, and data-translation bits, reads reset space to trigger the reset path, and panics if restart fails. It is marked `NOKPROBE_SYMBOL`.

## Control Flow, State, and Persistence
The function mutates reset-control hardware and never returns. It relies on globally mapped `cpm2_immr`.

## Dependencies and Integration Points
It is used by EP8248E and KM82xx machine definitions and depends on CPM2 IMMR structures and PowerPC MSR manipulation.

## Risks and Test Signals
Risks include triggering checkstop rather than orderly reset if hardware wiring differs, and lack of fallback after panic. Test signals are board restart/reset behavior and no kprobe instrumentation on the restart path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/82xx/pq2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/82xx/pq2.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/82xx/pq2.h

## Purpose
`pq2.h` declares common PowerQUICC II platform helpers for 82xx board files.

## Important APIs, Types, and Functions
It declares `pq2_restart()`. When PCI is enabled it declares `pq2ads_pci_init_irq()` and `pq2_init_pci()`; otherwise it provides no-op inline stubs.

## Control Flow, State, and Persistence
The header owns no state. The stubs allow board code to compile without PCI conditionals around helper calls.

## Dependencies and Integration Points
It integrates common PQ2 code with board support and optional PCI support that may live elsewhere in the platform tree.

## Risks and Test Signals
Risks include unused or externally defined PCI declarations drifting from implementation. Test signals are PCI and non-PCI board builds, and link coverage for `pq2_restart()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/82xx/pq2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/Kconfig -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/Kconfig

## Purpose
`83xx/Kconfig` defines Freescale 83xx board options and hidden SoC-family helper symbols.

## Important APIs, Types, and Functions
`PPC_83xx` depends on 32-bit Book3S and selects UDBG 16550, PCI capability, FSL PCI/SOC support, and IPIC. Board symbols cover MPC830x/831x/832x/834x/836x/837x RDB/ITX/RDK, ASP834x, and Keymile KMETER1. Hidden symbols `PPC_MPC831x`, `PPC_MPC832x`, `PPC_MPC834x`, and `PPC_MPC837x` gate USB/GPIO/math-emu helper objects.

## Control Flow, State, and Persistence
This file controls compile-time inclusion only.

## Dependencies and Integration Points
It feeds `83xx/Makefile`, selecting common `misc.o`, optional suspend code, board files, and USB mux helpers.

## Risks and Test Signals
Risks include missing hidden symbol selects causing board setup to omit needed USB helper code, and incorrect dependency on PCI/FSL subsystems. Test signals are defconfig and targeted board builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/Makefile

## Purpose
`83xx/Makefile` maps 83xx platform config symbols to common, suspend, board, and USB setup objects.

## Important APIs, Types, and Functions
`misc.o` is always built. `CONFIG_SUSPEND` adds `suspend.o` and `suspend-asm.o`. Board symbols add their respective machine files. SoC-family symbols add `usb_831x.o`, `usb_834x.o`, and `usb_837x.o`.

## Control Flow, State, and Persistence
Build-time object composition determines which machine descriptions and setup helpers are available.

## Dependencies and Integration Points
It integrates Kconfig with the PowerPC build and keeps USB helper inclusion separate from board machine files.

## Risks and Test Signals
Risks include missing USB helper linkage for board setup and unintended suspend code inclusion/exclusion. Test signals are all listed board builds with and without `CONFIG_SUSPEND`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/asp834x.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/asp834x.c

## Purpose
`asp834x.c` registers the Analogue & Micro ASP8347E board, derived from MPC834x ITX setup.

## Important APIs, Types, and Functions
`asp834x_setup_arch()` calls common `mpc83xx_setup_arch()` and configures MPC834x USB with `mpc834x_usb_cfg()`. The machine definition uses compatible `"analogue-and-micro,asp8347e"` and shared PCI, IPIC, restart, time, and progress hooks.

## Control Flow, State, and Persistence
The file persists no local state. Board setup mutates IMMR USB mux/clock registers through the USB helper.

## Dependencies and Integration Points
It depends on common 83xx setup, FSL PCI, IPIC, UDBG progress, and OF platform device declaration via `machine_device_initcall`.

## Risks and Test Signals
Risks are limited to USB mux assumptions and generic 83xx behavior. Test signals are board-compatible matching, USB controller mode, PCI bridge discovery, IPIC interrupts, and restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/asp834x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/km83xx.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/km83xx.c

## Purpose
`km83xx.c` supports Keymile KMETER1 and related 83xx boards, including QUICC Engine par_io setup and MPC8360E QE_ENET10 erratum handling.

## Important APIs, Types, and Functions
`mpc83xx_km_setup_arch()` runs common setup and, when QUICC Engine is enabled, initializes `par_io`, applies OF pin configuration for SPI and UCC nodes, and invokes `quirk_mpc8360e_qe_enet10()` when a `ucc_geth` network node exists. The erratum helper maps `par_io` registers and adjusts UCC delay bits depending on SVR revision. `mpc83xx_km_probe()` matches Keymile compatibles before the normal machine selection.

## Control Flow, State, and Persistence
Hardware state is persisted in par_io delay and pinmux registers. No local C state remains after init.

## Dependencies and Integration Points
It depends on QUICC Engine, OF par_io/spi/ucc nodes, FSL PCI/SOC helpers, IPIC, and common 83xx restart/time setup.

## Risks and Test Signals
Risks include revision-specific erratum bit programming, missing par_io nodes, and broad node-name scans. Test signals are UCC Ethernet RGMII stability, SPI pin function, board matching for both compatibles, PCI setup, and IPIC interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/km83xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mcu_mpc8349emitx.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mcu_mpc8349emitx.c

## Purpose
`mcu_mpc8349emitx.c` is an I2C driver for the MCU on MPC8349E-mITX-compatible boards, providing power-management, shutdown, GPIO expander, and status sysfs functions.

## Important APIs, Types, and Functions
The driver binds to I2C ID `"mcu-mpc8349emitx"` and OF compatible `"fsl,mcu-mpc8349emitx"`. Probe allocates an MCU state object, initializes GPIO-chip support, exposes a `status` device attribute, starts a shutdown-monitor thread, and may install `pm_power_off`. Remove stops the thread, removes sysfs, clears global power-off state if owned, unregisters GPIOs, and frees memory.

## Control Flow, State, and Persistence
Persistent state includes the per-client `struct mcu`, global `glob_mcu`, global `shutdown_thread`, and `pm_power_off` hook. MCU register state lives on the external I2C device.

## Dependencies and Integration Points
It integrates I2C core, optional gpiolib-style expander support, sysfs, kernel thread/freezer behavior, and board power-off handling.

## Risks and Test Signals
Risks include global singleton behavior, shutdown thread lifetime, I2C errors during poweroff/status reads, and GPIO numbering/semantics. Test signals are driver bind/unbind, sysfs status reads, GPIO line operation, clean remove, shutdown/poweroff action, and thread stop under module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mcu_mpc8349emitx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/misc.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/misc.c

## Purpose
`misc.c` provides shared MPC83xx platform functions: restart, time init, IPIC init, OF device declaration, PCI setup, IMMR BAT mapping, and watchdog machine-check handling.

## Important APIs, Types, and Functions
`mpc83xx_restart_init()` maps the reset control register from `"fsl,modulo-reboot"` and is registered as an `arch_initcall`. `mpc83xx_restart()` disables interrupts and writes the reset request. `mpc83xx_time_init()` reads bus frequency for decrementer calibration. `mpc83xx_ipic_init_IRQ()` initializes IPIC. `mpc83xx_declare_of_platform_devices()` populates simple/FSL buses. `mpc83xx_setup_pci()` scans PCI nodes and calls `mpc83xx_add_bridge()`. `mpc83xx_setup_arch()` creates a BAT mapping for IMMR. `machine_check_83xx()` handles watchdog MCP machine checks specially.

## Control Flow, State, and Persistence
The reset register mapping persists in `restart_reg_base`. The IMMR BAT mapping is global CPU MMU state. OF platform population creates device state under the platform bus.

## Dependencies and Integration Points
It depends on FSL SOC frequency helpers, IPIC, FSL PCI, OF platform bus, fixed IMMR mapping, and PowerPC machine-check infrastructure.

## Risks and Test Signals
Risks include missing reboot node causing restart hang, invalid bus-frequency data, BAT size alignment assumptions, PCI node scan ordering, and watchdog MCP classification. Test signals are restart, timer/decrementer calibration, IPIC interrupts, PCI enumeration, OF device probing, and watchdog NMI reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mpc830x_rdb.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mpc830x_rdb.c

## Purpose
`mpc830x_rdb.c` registers Freescale MPC8308 RDB and derivative boards.

## Important APIs, Types, and Functions
`mpc830x_rdb_setup_arch()` calls common `mpc83xx_setup_arch()` and configures 831x-style USB via `mpc831x_usb_cfg()`. The compatible list includes `"MPC8308RDB"`, `"fsl,mpc8308rdb"`, and `"denx,mpc8308_p1m"`. The machine definition installs shared PCI, IPIC, restart, and time hooks.

## Control Flow, State, and Persistence
No local state is retained. Hardware mutations are delegated to common setup and USB helper code.

## Dependencies and Integration Points
It depends on FSL PCI/SOC, IPIC, UDBG, hidden `PPC_MPC831x` USB helper selection, and OF platform device declaration.

## Risks and Test Signals
Risks include USB helper matching MPC8308/8315 IMMR differences and generic PCI assumptions. Test signals are board matching, USB PHY/mux setup, PCI discovery, IPIC interrupts, and reboot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mpc830x_rdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mpc831x_rdb.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mpc831x_rdb.c

## Purpose
`mpc831x_rdb.c` registers Freescale MPC8313/8315 RDB boards.

## Important APIs, Types, and Functions
`mpc831x_rdb_setup_arch()` calls `mpc83xx_setup_arch()` and `mpc831x_usb_cfg()`. The board compatible list includes `"MPC8313ERDB"` and `"fsl,mpc8315erdb"`. The machine definition uses shared PCI, IPIC, restart, time, and UDBG hooks.

## Control Flow, State, and Persistence
The file has no local persistent state. Setup affects IMMR USB mux/clock registers through the helper.

## Dependencies and Integration Points
It integrates common 83xx setup, FSL PCI, IPIC, OF platform population, and USB PHY configuration.

## Risks and Test Signals
Risks are USB PHY type handling and PCI/FSL bridge assumptions. Test signals are USB DR operation, PCI enumeration, interrupt delivery, and compatible matching on both boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mpc831x_rdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mpc832x_rdb.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mpc832x_rdb.c

## Purpose
`mpc832x_rdb.c` registers the MPC832x RDB board and contains legacy QUICC Engine SPI/MMC setup for boards without an `mmc-spi-slot` DT node.

## Important APIs, Types, and Functions
With QUICC Engine enabled, `mpc832x_spi_init()` configures par_io pins for SPI and SD-card signals, skips legacy setup if DT already has `mmc-spi-slot`, and registers an `mmc_spi` board-info entry through `fsl_spi_init()`. `of_fsl_spi_probe()` instantiates `mpc83xx_spi` platform devices from OF resources and IRQs. `mpc832x_rdb_setup_arch()` runs common setup and applies OF par_io config for UCC nodes.

## Control Flow, State, and Persistence
Legacy SPI platform devices and board-info registration persist after `machine_device_initcall`. Pinmux state is programmed into par_io hardware.

## Dependencies and Integration Points
It depends on QUICC Engine, par_io helpers, FSL SPI platform data, SPI/MMC core, OF address/IRQ resources, and shared 83xx PCI/IPIC hooks.

## Risks and Test Signals
Risks include duplicate legacy and DT-based MMC setup, hard-coded bus number `0x4c0`, chip-select GPIO pin assumptions, and fallback sysclk selection. Test signals are MMC-over-SPI detection, no duplicate device when `mmc-spi-slot` exists, UCC pin config, and board boot with PCI/IPIC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mpc832x_rdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mpc834x_itx.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mpc834x_itx.c

## Purpose
`mpc834x_itx.c` registers the Freescale MPC834x ITX board and adds localbus platform-device probing.

## Important APIs, Types, and Functions
`mpc834x_itx_declare_of_platform_devices()` runs common 83xx platform population and probes `"fsl,pq2pro-localbus"`. `mpc834x_itx_setup_arch()` calls common setup and `mpc834x_usb_cfg()`. The machine uses compatible `"MPC834xMITX"` and shared PCI, IPIC, restart, and time hooks.

## Control Flow, State, and Persistence
No file-local runtime state is retained. Localbus devices are registered by OF probing; USB mux/clock state is written to IMMR.

## Dependencies and Integration Points
It depends on common 83xx setup, OF platform bus, FSL PCI, IPIC, and the MPC834x USB helper.

## Risks and Test Signals
Risks include bootloader responsibility for PCI initialization, localbus DT compatibility, and USB port conflict handling. Test signals are localbus child probing, USB DR/MPH behavior, PCI presence, and interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mpc834x_itx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mpc836x_rdk.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mpc836x_rdk.c

## Purpose
`mpc836x_rdk.c` registers the Freescale/Logic MPC8360 RDK board.

## Important APIs, Types, and Functions
`mpc836x_rdk_setup_arch()` calls common `mpc83xx_setup_arch()`. The machine definition uses compatible `"fsl,mpc8360rdk"` and common PCI, IPIC, restart, time, and UDBG hooks. `machine_device_initcall()` registers common OF platform devices.

## Control Flow, State, and Persistence
The file keeps no local state. Common setup creates IMMR BAT mapping and platform devices.

## Dependencies and Integration Points
It depends on FSL PCI/SOC support, IPIC, and OF platform population. Kconfig also selects GTM/LBC support for this board.

## Risks and Test Signals
Risks are low in this file but include reliance on common setup for all board needs and no explicit QUICC Engine pin initialization. Test signals are board-compatible matching, PCI enumeration, localbus/GTM devices, interrupt delivery, and restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mpc836x_rdk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mpc837x_rdb.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mpc837x_rdb.c

## Purpose
`mpc837x_rdb.c` registers MPC837x RDB/WLAN boards and configures board-specific USB/SD pinmux.

## Important APIs, Types, and Functions
`mpc837x_rdb_setup_arch()` runs common setup, configures USB through `mpc837x_usb_cfg()`, and calls `mpc837x_rdb_sd_cfg()`. The SD helper maps IMMR and muxes USBB/SPI pins to SD-card function. The compatible list covers MPC8377/8378/8379 RDB and MPC8377 WLAN boards.

## Control Flow, State, and Persistence
No C state persists. IMMR SICRL/SICRH pinmux writes persist in hardware for the boot session.

## Dependencies and Integration Points
It depends on common 83xx setup, MPC837x USB helper, FSL PCI/SOC, IPIC, OF platform population, and board DT compatible matching.

## Risks and Test Signals
Risks include muxing USBB pins away from USB for SD, which is safe only for RDB-style boards, and fixed IMMR mapping assumptions. Test signals are SD-card operation, USB DR behavior, no conflict on WLAN variants, PCI enumeration, and interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mpc837x_rdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mpc83xx.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mpc83xx.h

## Purpose
`mpc83xx.h` is the shared 83xx platform header for USB clock/pinmux constants and common function prototypes.

## Important APIs, Types, and Functions
It defines SCCR/SICRL/SICRH masks for MPC831x, MPC8315, MPC834x, MPC837x, and MPC8308 USB configuration, USB controller register offsets and control bits, and function declarations for restart, time init, IPIC init, PCI setup, platform-device declaration, common arch setup, and USB helpers.

## Control Flow, State, and Persistence
The header owns no runtime state. Its macros encode hardware register contracts used by USB helper files and board setup.

## Dependencies and Integration Points
It is included by nearly every 83xx board file, `misc.c`, and USB configuration files. It conditionally makes `mpc83xx_setup_pci` `NULL` when PCI is disabled for machine definitions.

## Risks and Test Signals
Risks include incorrect bit masks causing board-wide USB/pinmux failures and hidden coupling between Kconfig family symbols and helper availability. Test signals are compile coverage and USB mode validation on 831x, 834x, and 837x boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/mpc83xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/suspend-asm.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/suspend-asm.S

## Purpose
`suspend-asm.S` implements the low-level MPC83xx deep-sleep transition and resume path used by the PMC suspend driver.

## Important APIs, Types, and Functions
The exported entry `mpc83xx_enter_deep_sleep(phys_addr_t immrbase)` saves the first RAM words, CPU HID/debug/MMU/timebase/general register state into `mpc83xx_sleep_save_area`, writes the bootloader resume magic and physical `mpc83xx_deep_resume` address, disables MMU paths, maps current/default IMMR with BATs, moves IMMR back to the reset location, configures flash mapping, sets sleep mode and `MSR_POW`, then resumes by restoring RAM words, CPU state, BATs, segment registers, timebase, and registers before `rfi`.

## Control Flow, State, and Persistence
Static data holds the save area and IMMR base. The routine intentionally modifies low RAM words as a firmware contract and later restores them.

## Dependencies and Integration Points
It depends on `suspend.c`, boot firmware recognizing the magic/resume pointer, PowerPC 6xx/e300 SPRs, IMMR reset address rules, and cache-management helpers.

## Risks and Test Signals
Risks are severe: wrong BATs, cache state, flash mapping, resume magic, or save-area layout can brick resume. Test signals are deep-sleep/resume on supported PMC types, restored low RAM contents, correct timebase/decrementer after resume, and operation across low-boot/high-boot flash configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/suspend-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/suspend.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/suspend.c

## Purpose
`suspend.c` is the MPC83xx Power Management Controller driver. It provides standby and deep-sleep suspend operations, PCI-agent power-management handling, wake event interrupt handling, and exports deep-sleep state to other drivers.

## Important APIs, Types, and Functions
`pmc_probe()` binds `"fsl,mpc8313-pmc"` or `"fsl,mpc8349-pmc"`, maps PMC/clock/SYSCR registers, requests the PMC IRQ, detects PCI host/agent role, optionally starts a PCI power-management kthread, and installs `mpc83xx_suspend_ops`. `mpc83xx_suspend_enter()` configures low-power mode, masks wake events, saves/restores SICR/SCCR for deep sleep, calls `mpc83xx_enter_deep_sleep()` or `mpc6xx_enter_standby()`, and handles PME enable. `fsl_deep_sleep()` exports whether the system is entering deep sleep.

## Control Flow, State, and Persistence
Global state tracks deep-sleep capability, current deep-sleep flag, PMC IRQ, mapped registers, saved registers, PCI-agent flags, IMMR base, PCI PM state, and a wait queue. PCI-agent state transitions wake a kernel thread that calls `pm_suspend()`.

## Dependencies and Integration Points
It integrates OF platform probing, PowerPC suspend core, PMC IRQs, FSL SOC IMMR helpers, low-level assembly, PCI power-management state, freezer-aware kthreads, and drivers that query `fsl_deep_sleep()`.

## Risks and Test Signals
Risks include PCI-agent races noted in comments, global singleton PMC state, wake mask errors, deep-sleep register restore gaps, and resource leaks on partial probe. Test signals are standby and mem suspend, wake by GPIO/PCI/USB/timer events, PCI-agent D-state transitions, `fsl_deep_sleep()` behavior during suspend, and repeated suspend cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/suspend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/usb_831x.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/usb_831x.c

## Purpose
`usb_831x.c` configures MPC831x/MPC8308/MPC8315 USB clocking, pinmux, and PHY control before USB controller drivers probe.

## Important APIs, Types, and Functions
`mpc831x_usb_cfg()` finds `"fsl-usb2-dr"`, reads `phy_type`, maps IMMR, chooses SCCR USB clock settings based on parent IMMR compatible, programs ULPI pinmux bits when needed, maps USB controller registers, and writes the USB control register for UTMI, ULPI, and optional OTG mode.

## Control Flow, State, and Persistence
It performs one-shot IMMR and USB register writes; no local state persists. OF node references and mappings are released before return.

## Dependencies and Integration Points
It depends on `mpc83xx.h` bit definitions, OF USB nodes/properties, `get_immrbase()`, optional `CONFIG_USB_OTG`, and board setup functions that call it.

## Risks and Test Signals
Risks include parent-node lifetime after early `of_node_put`, unsupported PHY strings, 8308 special-case behavior, and mismatched ULPI/UTMI muxing. Test signals are USB DR probe, PHY clock selection, OTG mode on supported boards, and warning-free setup for each 831x-family SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/usb_831x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/usb_834x.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/usb_834x.c

## Purpose
`usb_834x.c` configures MPC834x USB DR and MPH clock/pinmux routing.

## Important APIs, Types, and Functions
`mpc834x_usb_cfg()` maps IMMR, reads current SCCR/SICRL/SICRH values, scans `"fsl-usb2-dr"` for `phy_type` and `dr_mode`, marks whether DR owns port0/port1, scans `"fsl-usb2-mph"` for `port0`/`port1`, warns on port conflicts, and writes back final clock and mux registers.

## Control Flow, State, and Persistence
No local state persists. The hardware SCCR/SICR bits persist for the boot session.

## Dependencies and Integration Points
It depends on OF USB nodes/properties, MPC834x bit definitions in `mpc83xx.h`, and board setup files such as ASP834x and MPC834x ITX.

## Risks and Test Signals
Risks include conflicting DR/MPH port declarations, unsupported PHY types, and writing shared USB clock settings for both controllers. Test signals are DR and MPH controller probe, correct port ownership, expected warnings on conflicting DT, and functional UTMI/serial/ULPI modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/usb_834x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/usb_837x.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/usb_837x.c

## Purpose
`usb_837x.c` configures MPC837x USB DR clock and pinmux for ULPI or serial PHY modes.

## Important APIs, Types, and Functions
`mpc837x_usb_cfg()` finds an available `"fsl-usb2-dr"` node, validates `phy_type` as `"ulpi"` or `"serial"`, maps IMMR, programs SCCR USB clock bits, and muxes USB pins through SICRL.

## Control Flow, State, and Persistence
It writes IMMR registers once during board setup and releases mappings/node references.

## Dependencies and Integration Points
It depends on `mpc83xx.h`, OF USB properties, `get_immrbase()`, and MPC837x board setup such as `mpc837x_rdb.c`.

## Risks and Test Signals
Risks include rejecting DTs without expected `phy_type`, pinmux conflicts with SD/USBB usage, and fixed clock ratio assumptions. Test signals are USB DR probe on ULPI and serial boards, proper interaction with RDB SD muxing, and no warnings for supported DTs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/usb_837x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/Kconfig -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/Kconfig

## Purpose
`85xx/Kconfig` defines Freescale Book-E/e500 machine type support and the board options for the 85xx platform family.

## Important APIs, Types, and Functions
`FSL_SOC_BOOKE` depends on `PPC_E500`, selects FSL SOC support, UDBG 16550, MPIC, PCI capability, serial options, and CoreNet RCPM when appropriate. The visible board options include BSC9131 RDB, BSC9132 QDS, many MPC85xx/P10xx/P20xx boards, QEMU e500, CoreNet generic, and vendor boards. The listed BSC symbols select `DEFAULT_UIMAGE`.

## Control Flow, State, and Persistence
This file only affects build-time configuration and object inclusion.

## Dependencies and Integration Points
It integrates with `85xx/Makefile`, MPIC/FSL PCI/SOC support, SMP/PM helper selection, and 32-bit versus CoreNet board families.

## Risks and Test Signals
Risks include broad default selection for Book-E, board options missing required selects, and accidentally enabling incompatible board code. Test signals are defconfig coverage, menu dependency checks, and targeted BSC913x builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/Makefile

## Purpose
`85xx/Makefile` maps Freescale 85xx/e500 platform symbols to common, SMP/PM, and board-specific objects.

## Important APIs, Types, and Functions
It builds `common.o` unconditionally for the platform family, conditionally includes SMP and PM helpers, and maps board symbols to files including `bsc913x_rdb.o` and `bsc913x_qds.o`. It also composes I8259 helper objects for boards that need legacy interrupt support.

## Control Flow, State, and Persistence
This is build-time composition only. It determines which `define_machine()` records and common publish-device hooks are linked.

## Dependencies and Integration Points
It integrates Kconfig symbols with board files, common 85xx platform support, FSL PCI, MPIC, CoreNet, DIU, and vendor-specific support objects.

## Risks and Test Signals
Risks include missing helper objects for board-selected features and SMP/PM object conflicts with CoreNet RCPM. Test signals are all targeted board builds and link validation for common publish, SMP, PCI, and interrupt hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/bsc913x_qds.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/bsc913x_qds.c

## Purpose
`bsc913x_qds.c` registers the Freescale BSC9132 QDS board.

## Important APIs, Types, and Functions
`bsc913x_qds_pic_init()` allocates and initializes a big-endian single-destination MPIC with 256 interrupts. `bsc913x_qds_setup_arch()` emits progress, initializes MPC85xx SMP support when enabled, assigns the primary FSL PCI controller, and logs board identity. The machine definition uses compatible `"fsl,bsc9132qds"`, common device publication, optional FSL PCI bus fixup, MPIC IRQ retrieval, and UDBG progress.

## Control Flow, State, and Persistence
No file-local state persists. MPIC and common platform devices persist through shared subsystems initialized by hooks.

## Dependencies and Integration Points
It depends on MPC85xx common publish devices, MPIC, optional SMP, FSL PCI assignment/fixup, and BSC9132 QDS DT compatibility.

## Risks and Test Signals
Risks include MPIC allocation failure, missing SMP init on multicore systems, and PCI primary assignment assumptions. Test signals are board boot, MPIC interrupts, SMP bring-up, PCI enumeration/fixups, and platform device publication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/bsc913x_qds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/bsc913x_rdb.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/bsc913x_rdb.c

## Purpose
`bsc913x_rdb.c` registers the Freescale BSC9131 RDB board.

## Important APIs, Types, and Functions
`bsc913x_rdb_pic_init()` allocates and initializes a big-endian single-destination MPIC with 256 interrupts. `bsc913x_rdb_setup_arch()` emits progress and logs the board identity. The machine definition uses compatible `"fsl,bsc9131rdb"`, common MPC85xx device publication, `mpic_get_irq`, and UDBG progress.

## Control Flow, State, and Persistence
No local state persists. MPIC state and platform devices are owned by common subsystems.

## Dependencies and Integration Points
It depends on MPIC, MPC85xx common publish devices, BSC9131 RDB DT compatibility, and generic 85xx platform infrastructure.

## Risks and Test Signals
Risks include MPIC allocation failure and minimal setup omitting board-specific PCI/SMP handling that may be expected by future variants. Test signals are board-compatible matching, interrupt delivery, common platform-device publication, and successful boot logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/85xx/bsc913x_rdb.c -->
