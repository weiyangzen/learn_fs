# subset-b-000659 Research

Grouped source research for subset B work item `subset-b-000659`. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/SA-1100.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/SA-1100.h

## Purpose
This is the central SA-1100 hardware register and bit-field header. It maps the StrongARM SA-1100 on-chip peripheral registers, interrupt controller, GPIO, serial ports, OS timer, power manager, memory controller, DMA, and LCD controller into kernel C macros used by legacy board files and low-level drivers.

## Important APIs, Types, and Functions
- Register/constant macro families: `GPIO`(60), `PPCR`(50), `MDCNFG`(37), `IC`(35), `PWER`(31), `LCD`(28), `PPC`(23), `MSC`(22); examples: `SA1100_CS0_PHYS`, `SA1100_CS1_PHYS`, `SA1100_CS2_PHYS`, `SA1100_CS3_PHYS`, `SA1100_CS4_PHYS`, `SA1100_CS5_PHYS`, `PCMCIAPrtSp`, `PCMCIASp`, `PCMCIAIOSp`, `PCMCIAAttrSp`, `PCMCIAMemSp`, `PCMCIA0Sp`, `PCMCIA0IOSp`, `PCMCIA0AttrSp`, `PCMCIA0MemSp`, `PCMCIA1Sp`, plus 863 more.

## Control Flow
There is no runtime control flow in this header. Including C files expand its macros into direct memory-mapped register accesses, IRQ-number calculations, board tests, and timing constants at compile time.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly; static kernel data records board resources, register bases, cached flags, or callback tables; suspend paths persist resume vectors and controller state across low-power entry; in-memory locks serialize access to shared controller state. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `bitfield.h`.
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.
- Integrates with gpiolib lookup tables, GPIO chips, or board GPIO bit definitions.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.
- Integrates with kernel PM suspend callbacks, CPU suspend/resume assembly, and low-power hardware registers.
- Integrates with clocksource/clock framework setup during early platform initialization.
- Integrates with AMBA PL080/PL08x DMA platform data and request-signal muxing.

## Risks
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.
- DMA request mux conflicts can silently route a peripheral to the wrong request line.
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.
- Exercise suspend/resume or CPU hotplug repeatedly while checking serial console logs, wake sources, and cache/coherency-sensitive workloads.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.
- Run DMA-using peripheral transfers and check that request-line allocation/release pairs do not conflict under concurrent users.

## Research Notes
- Read coverage: full file (97933 bytes, 1799 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/SA-1100.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/assabet.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/assabet.h

## Purpose
This SA-1100 machine header collects board or SoC constants for `assabet` users: GPIO assignments, IRQ lines, register offsets, memory windows, and helper declarations consumed by legacy board files and companion drivers.

## Important APIs, Types, and Functions
- Register/constant macro families: `ASSABET`(53), `machine`(2), `__AS`(1); examples: `__ASM_ARCH_ASSABET_H`, `ASSABET_SCR_SDRAM_LOW`, `ASSABET_SCR_SDRAM_HIGH`, `ASSABET_SCR_FLASH_LOW`, `ASSABET_SCR_FLASH_HIGH`, `ASSABET_SCR_GFX`, `ASSABET_SCR_SA1111`, `ASSABET_SCR_INIT`, `machine_has_neponset`, `ASSABET_BCR_BASE`, `ASSABET_BCR`, `ASSABET_BCR_CF_PWR`, `ASSABET_BCR_CF_RST`, `ASSABET_BCR_NGFX_RST`, `ASSABET_BCR_NCODEC_RST`, `ASSABET_BCR_IRDA_FSEL`, plus 39 more.

## Control Flow
There is no runtime control flow in this header. Including C files expand its macros into direct memory-mapped register accesses, IRQ-number calculations, board tests, and timing constants at compile time.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: in-memory locks serialize access to shared controller state. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.
- Integrates with gpiolib lookup tables, GPIO chips, or board GPIO bit definitions.
- Integrates with clocksource/clock framework setup during early platform initialization.

## Risks
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.

## Research Notes
- Read coverage: full file (4172 bytes, 100 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/assabet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/bitfield.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/bitfield.h

## Purpose
This header defines the bit-field construction/extraction macros used by SA-1100 register definitions. It provides compile-time field width/shift encodings and helpers for setting, testing, and extracting register fields.

## Important APIs, Types, and Functions
- Register/constant macro families: `UData`(2), `F1stBit`(1), `FAlnMsk`(1), `FExtr`(1), `FInsrt`(1), `FMsk`(1), `FShft`(1), `FSize`(1); examples: `__BITFIELD_H`, `UData`, `Fld`, `FSize`, `FShft`, `FMsk`, `FAlnMsk`, `F1stBit`, `FInsrt`, `FExtr`.

## Control Flow
There is no runtime control flow in this header. Including C files expand its macros into direct memory-mapped register accesses, IRQ-number calculations, board tests, and timing constants at compile time.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Dependencies are limited to compile-time inclusion by adjacent platform code.

## Risks
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.

## Research Notes
- Read coverage: full file (2835 bytes, 114 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/bitfield.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/collie.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/collie.h

## Purpose
This SA-1100 machine header collects board or SoC constants for `collie` users: GPIO assignments, IRQ lines, register offsets, memory windows, and helper declarations consumed by legacy board files and companion drivers.

## Important APIs, Types, and Functions
- Register/constant macro families: `COLLIE`(52), `_COL`(8), `__AS`(1); examples: `__ASM_ARCH_COLLIE_H`, `COLLIE_SCOOP_GPIO_BASE`, `COLLIE_GPIO_CHARGE_ON`, `COLLIE_SCP_DIAG_BOOT1`, `COLLIE_SCP_DIAG_BOOT2`, `COLLIE_SCP_MUTE_L`, `COLLIE_SCP_MUTE_R`, `COLLIE_SCP_5VON`, `COLLIE_SCP_AMP_ON`, `COLLIE_GPIO_VPEN`, `COLLIE_SCP_LB_VOL_CHG`, `COLLIE_SCOOP_IO_DIR`, `COLLIE_SCOOP_IO_OUT`, `COLLIE_GPIO_ON_KEY`, `COLLIE_GPIO_AC_IN`, `COLLIE_GPIO_SDIO_INT`, plus 45 more.

## Control Flow
There is no runtime control flow in this header. Including C files expand its macros into direct memory-mapped register accesses, IRQ-number calculations, board tests, and timing constants at compile time.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `hardware.h`.
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.
- Integrates with gpiolib lookup tables, GPIO chips, or board GPIO bit definitions.
- Integrates with clocksource/clock framework setup during early platform initialization.

## Risks
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.

## Research Notes
- Read coverage: full file (3434 bytes, 95 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/collie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/generic.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/generic.h

## Purpose
This compatibility header is intentionally minimal and only preserves an include path expected by legacy SA-1100 code.

## Important APIs, Types, and Functions
- This file intentionally exposes no callable API; its value is in build selection, declarations, or a compatibility include path.

## Control Flow
There is no runtime control flow in this header. Including C files expand its macros into direct memory-mapped register accesses, IRQ-number calculations, board tests, and timing constants at compile time.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `../../generic.h`.

## Risks
- main risk is accidental removal or build exclusion of a legacy compatibility file that still has include-path users.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.

## Research Notes
- Read coverage: full file (27 bytes, 2 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/h3xxx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/h3xxx.h

## Purpose
This SA-1100 machine header collects board or SoC constants for `h3xxx` users: GPIO assignments, IRQ lines, register offsets, memory windows, and helper declarations consumed by legacy board files and companion drivers.

## Important APIs, Types, and Functions
- Register/constant macro families: `H3XXX`(20), `H3600`(19), `H3100`(7), `_INC`(1); examples: `_INCLUDE_H3XXX_H_`, `H3600_EGPIO_PHYS`, `H3600_BANK_2_PHYS`, `H3600_BANK_4_PHYS`, `H3600_EGPIO_VIRT`, `H3600_BANK_2_VIRT`, `H3600_BANK_4_VIRT`, `H3XXX_GPIO_PWR_BUTTON`, `H3XXX_GPIO_PCMCIA_CD1`, `H3XXX_GPIO_PCMCIA_IRQ1`, `H3XXX_GPIO_PCMCIA_CD0`, `H3XXX_GPIO_ACTION_BUTTON`, `H3XXX_GPIO_SYS_CLK`, `H3XXX_GPIO_PCMCIA_IRQ0`, `H3XXX_GPIO_COM_DCD`, `H3XXX_GPIO_OPTION`, plus 31 more.

## Control Flow
There is no runtime control flow in this header. Including C files expand its macros into direct memory-mapped register accesses, IRQ-number calculations, board tests, and timing constants at compile time.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: in-memory locks serialize access to shared controller state. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `hardware.h`.
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.
- Integrates with gpiolib lookup tables, GPIO chips, or board GPIO bit definitions.
- Integrates with clocksource/clock framework setup during early platform initialization.

## Risks
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.

## Research Notes
- Read coverage: full file (3369 bytes, 82 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/h3xxx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/hardware.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/hardware.h

## Purpose
This machine hardware header wires SA-1100 platform code to the core register map and machine-type predicates, including Assabet-specific helpers when that board is configured.

## Important APIs, Types, and Functions
- Register/constant macro families: `VIO`(2), `io`(2), `PIO`(1), `UNCACHEABLE`(1), `__AS`(1), `__MR`(1); examples: `__ASM_ARCH_HARDWARE_H`, `UNCACHEABLE_ADDR`, `VIO_BASE`, `VIO_SHIFT`, `PIO_START`, `io_p2v`, `io_v2p`, `__MREG`.

## Control Flow
There is no runtime control flow in this header. Including C files expand its macros into direct memory-mapped register accesses, IRQ-number calculations, board tests, and timing constants at compile time.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `SA-1100.h`.

## Risks
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.

## Research Notes
- Read coverage: full file (1388 bytes, 57 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/hardware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/irqs.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/irqs.h

## Purpose
This header defines the SA-1100 IRQ namespace, translating on-chip interrupt bits and board/companion chip IRQ ranges into Linux IRQ numbers.

## Important APIs, Types, and Functions
- Register/constant macro families: `IRQ`(62), `NR`(3), `SA1100`(1); examples: `IRQ_GPIO0_SC`, `IRQ_GPIO1_SC`, `IRQ_GPIO2_SC`, `IRQ_GPIO3_SC`, `IRQ_GPIO4_SC`, `IRQ_GPIO5_SC`, `IRQ_GPIO6_SC`, `IRQ_GPIO7_SC`, `IRQ_GPIO8_SC`, `IRQ_GPIO9_SC`, `IRQ_GPIO10_SC`, `IRQ_GPIO11_27`, `IRQ_LCD`, `IRQ_Ser0UDC`, `IRQ_Ser1SDLC`, `IRQ_Ser1UART`, plus 49 more.

## Control Flow
There is no runtime control flow in this header. Including C files expand its macros into direct memory-mapped register accesses, IRQ-number calculations, board tests, and timing constants at compile time.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: in-memory locks serialize access to shared controller state; runtime allocations or mappings must remain valid for later callbacks. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.
- Integrates with gpiolib lookup tables, GPIO chips, or board GPIO bit definitions.
- Integrates with AMBA PL080/PL08x DMA platform data and request-signal muxing.

## Risks
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.
- DMA request mux conflicts can silently route a peripheral to the wrong request line.
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.
- Run DMA-using peripheral transfers and check that request-line allocation/release pairs do not conflict under concurrent users.

## Research Notes
- Read coverage: full file (3143 bytes, 102 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/irqs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/jornada720.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/jornada720.h

## Purpose
This SA-1100 machine header collects board or SoC constants for `jornada720` users: GPIO assignments, IRQ lines, register offsets, memory windows, and helper declarations consumed by legacy board files and companion drivers.

## Important APIs, Types, and Functions
- Register/constant macro families: `BRIGHTNESSOFF`(1), `CONTRASTOFF`(1), `ERRORCODE`(1), `GETBATTERYDATA`(1), `GETBRIGHTNESS`(1), `GETCONTRAST`(1), `GETSCANKEYCODE`(1), `GETTOUCHSAMPLES`(1); examples: `GETBATTERYDATA`, `GETSCANKEYCODE`, `GETTOUCHSAMPLES`, `GETCONTRAST`, `SETCONTRAST`, `GETBRIGHTNESS`, `SETBRIGHTNESS`, `CONTRASTOFF`, `BRIGHTNESSOFF`, `PWMOFF`, `TXDUMMY`, `ERRORCODE`.

## Control Flow
There is no runtime control flow in this header. Including C files expand its macros into direct memory-mapped register accesses, IRQ-number calculations, board tests, and timing constants at compile time.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Dependencies are limited to compile-time inclusion by adjacent platform code.

## Risks
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.

## Research Notes
- Read coverage: full file (810 bytes, 29 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/jornada720.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/memory.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/memory.h

## Purpose
This header supplies the SA-1100 physical memory base used by ARM memory layout setup.

## Important APIs, Types, and Functions
- Register/constant macro families: `FLUSH`(3), `MAX`(1), `SECTION`(1), `__AS`(1); examples: `__ASM_ARCH_MEMORY_H`, `MAX_PHYSMEM_BITS`, `SECTION_SIZE_BITS`, `FLUSH_BASE_PHYS`, `FLUSH_BASE`, `FLUSH_BASE_MINICACHE`.

## Control Flow
There is no runtime control flow in this header. Including C files expand its macros into direct memory-mapped register accesses, IRQ-number calculations, board tests, and timing constants at compile time.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/sizes.h`.

## Risks
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.

## Research Notes
- Read coverage: full file (1061 bytes, 38 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/memory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/mtd-xip.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/mtd-xip.h

## Purpose
This header provides execute-in-place flash timing hooks for MTD, using the SA-1100 OS timer to delay while code may be executing directly from flash.

## Important APIs, Types, and Functions
- Register/constant macro families: `xip`(3), `__AR`(1); examples: `__ARCH_SA1100_MTD_XIP_H__`, `xip_irqpending`, `xip_currtime`, `xip_elapsed_since`.

## Control Flow
There is no runtime control flow in this header. Including C files expand its macros into direct memory-mapped register accesses, IRQ-number calculations, board tests, and timing constants at compile time.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `mach/hardware.h`.
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.

## Risks
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.

## Research Notes
- Read coverage: full file (669 bytes, 24 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/mtd-xip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/neponset.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/neponset.h

## Purpose
This SA-1100 machine header collects board or SoC constants for `neponset` users: GPIO assignments, IRQ lines, register offsets, memory windows, and helper declarations consumed by legacy board files and companion drivers.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `neponset_ncr_frob`.
- Register/constant macro families: `NCR`(7), `neponset`(2), `__AS`(1); examples: `__ASM_ARCH_NEPONSET_H`, `NCR_GP01_OFF`, `NCR_TP_PWR_EN`, `NCR_MS_PWR_EN`, `NCR_ENET_OSC_EN`, `NCR_SPI_KB_WK_UP`, `NCR_A0VPP`, `NCR_A1VPP`, `neponset_ncr_set`, `neponset_ncr_clear`.

## Control Flow
There is no runtime control flow in this header. Including C files expand its macros into direct memory-mapped register accesses, IRQ-number calculations, board tests, and timing constants at compile time.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Dependencies are limited to compile-time inclusion by adjacent platform code.

## Risks
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.

## Research Notes
- Read coverage: full file (834 bytes, 32 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/neponset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/reset.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/reset.h

## Purpose
This header defines the SA-1100 reset hook by programming the reset controller register and falling back to a spin loop.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `clear_reset_status`.
- Register/constant macro families: `RESET`(5), `__AS`(1); examples: `__ASM_ARCH_RESET_H`, `RESET_STATUS_HARDWARE`, `RESET_STATUS_WATCHDOG`, `RESET_STATUS_LOWPOWER`, `RESET_STATUS_GPIO`, `RESET_STATUS_ALL`.

## Control Flow
There is no runtime control flow in this header. Including C files expand its macros into direct memory-mapped register accesses, IRQ-number calculations, board tests, and timing constants at compile time.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: suspend paths persist resume vectors and controller state across low-power entry. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `hardware.h`.
- Integrates with gpiolib lookup tables, GPIO chips, or board GPIO bit definitions.
- Integrates with kernel PM suspend callbacks, CPU suspend/resume assembly, and low-power hardware registers.

## Risks
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.
- Exercise suspend/resume or CPU hotplug repeatedly while checking serial console logs, wake sources, and cache/coherency-sensitive workloads.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.

## Research Notes
- Read coverage: full file (500 bytes, 19 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/uncompress.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/uncompress.h

## Purpose
This low-level decompressor header implements early debug UART output for SA-1100 boot before the normal console and driver model are available.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `putc`, `flush`.
- Register/constant macro families: `IOMEM`(1), `UART`(1), `arch`(1); examples: `IOMEM`, `UART`, `arch_decomp_setup`.

## Control Flow
There is no runtime control flow in this header. Including C files expand its macros into direct memory-mapped register accesses, IRQ-number calculations, board tests, and timing constants at compile time.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `hardware.h`.

## Risks
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.

## Research Notes
- Read coverage: full file (1115 bytes, 53 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/uncompress.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/jornada720.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/jornada720.c

## Purpose
This board file registers the HP Jornada 720 machine: static memory mappings, SA1111 companion resources, Epson S1D13xxx framebuffer platform data, flash partitions, GPIO lookups, serial policy, and machine descriptor callbacks.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `jornada720_set_vpp`, `JORNADA720 (HP Jornada 720)`.
- Initcall hooks: `jornada720_init`.
- Static data/types: `s1d13xxxfb_regval s1d13xxxfb_initregs`, `s1d13xxxfb_pdata s1d13xxxfb_data`, `resource s1d13xxxfb_resources`, `platform_device s1d13xxxfb_device`, `gpiod_lookup_table jornada_pcmcia_gpiod_table`, `resource sa1111_resources`, `sa1111_platform_data sa1111_info`, `platform_device sa1111_device`, `platform_device jornada_ssp_device`, `resource jornada_kbd_resources`, `platform_device jornada_kbd_device`, `gpiod_lookup_table jornada_ts_gpiod_table`, `platform_device jornada_ts_device`, `map_desc jornada720_io_desc`, plus 3 more.
- Register/constant macro families: `EPSONFBLEN`(1), `EPSONFBSTART`(1), `EPSONREGLEN`(1), `EPSONREGSTART`(1), `SA1111REGLEN`(1), `SA1111REGSTART`(1), `TUCR`(1); examples: `TUCR_VAL`, `SA1111REGSTART`, `SA1111REGLEN`, `EPSONREGSTART`, `EPSONREGLEN`, `EPSONFBSTART`, `EPSONFBLEN`.

## Control Flow
Boot control flow is descriptor-driven: machine matching calls map/init/timer callbacks, static platform data is registered, DT children are populated where applicable, and late init or arch initcalls finish board-specific devices after core subsystems are ready.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: static kernel data records board resources, register bases, cached flags, or callback tables; persistent hardware description is encoded as machine descriptors, platform devices, resources, and DT compatibles; in-memory locks serialize access to shared controller state. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/init.h`, `linux/kernel.h`, `linux/tty.h`, `linux/delay.h`, `linux/gpio/machine.h`, `linux/platform_data/sa11x0-serial.h`, `linux/platform_device.h`, `linux/ioport.h`, `linux/mtd/mtd.h`, `linux/mtd/partitions.h`, `video/s1d13xxxfb.h`, `asm/hardware/sa1111.h`, `asm/page.h`, `asm/mach-types.h`, `asm/setup.h`, `asm/mach/arch.h`, `asm/mach/flash.h`, `asm/mach/map.h`, plus 3 more.
- Integrates with platform-device/resource registration and legacy board data handoff.
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.
- Integrates with gpiolib lookup tables, GPIO chips, or board GPIO bit definitions.
- Integrates with AMBA PL080/PL08x DMA platform data and request-signal muxing.

## Risks
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.
- DMA request mux conflicts can silently route a peripheral to the wrong request line.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `jornada720.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.
- Run DMA-using peripheral transfers and check that request-line allocation/release pairs do not conflict under concurrent users.

## Research Notes
- Read coverage: full file (12822 bytes, 381 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/jornada720.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/jornada720_ssp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/jornada720_ssp.c

## Purpose
This file implements Jornada 720-specific SSP helpers used to communicate with board-attached peripherals through the SA-1100 synchronous serial port.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `jornada_ssp_byte`, `jornada_ssp_inout`, `jornada_ssp_start`, `jornada_ssp_end`, `jornada_ssp_probe`, `jornada_ssp_remove`.
- Exported symbols: `jornada_ssp_reverse`, `jornada_ssp_byte`, `jornada_ssp_inout`, `jornada_ssp_start`, `jornada_ssp_end`.
- Static data/types: `platform_driver jornadassp_driver`.

## Control Flow
Boot control flow is descriptor-driven: machine matching calls map/init/timer callbacks, static platform data is registered, DT children are populated where applicable, and late init or arch initcalls finish board-specific devices after core subsystems are ready.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: static kernel data records board resources, register bases, cached flags, or callback tables; persistent hardware description is encoded as machine descriptors, platform devices, resources, and DT compatibles; in-memory locks serialize access to shared controller state. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/delay.h`, `linux/errno.h`, `linux/init.h`, `linux/kernel.h`, `linux/module.h`, `linux/platform_device.h`, `linux/sched.h`, `linux/io.h`, `mach/hardware.h`, `mach/jornada720.h`, `asm/hardware/ssp.h`.
- Integrates with platform-device/resource registration and legacy board data handoff.
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.
- Integrates with gpiolib lookup tables, GPIO chips, or board GPIO bit definitions.

## Risks
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `jornada720_ssp.c`.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.

## Research Notes
- Read coverage: full file (4490 bytes, 203 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/jornada720_ssp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/neponset.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/neponset.c

## Purpose
This file is the platform driver for the Neponset expansion board used with Assabet-class SA-1100 systems. It maps expansion registers, exposes GPIOs, cascades Neponset interrupts, registers child devices, and handles suspend/resume state.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `neponset_ncr_frob`, `neponset_irq_handler`, `nochip_noop`, `neponset_init_gpio`, `neponset_probe`, `neponset_remove`, `neponset_resume`.
- Exported symbols: `neponset_ncr_frob`.
- Static data/types: `gpiod_lookup_table neponset_uart1_gpio_table`, `gpiod_lookup_table neponset_uart3_gpio_table`, `gpiod_lookup_table neponset_pcmcia_table`, `irq_chip nochip`, `sa1111_platform_data sa1111_info`, `platform_driver neponset_device_driver`.
- Register/constant macro families: `IRR`(4), `MDM`(4), `NEP`(4), `AUD`(2), `KP`(2), `NCR`(2), `PM`(2), `LEDS`(1); examples: `NEP_IRQ_SMC91X`, `NEP_IRQ_USAR`, `NEP_IRQ_SA1111`, `NEP_IRQ_NR`, `WHOAMI`, `LEDS`, `SWPK`, `IRR`, `KP_Y_IN`, `KP_X_OUT`, `NCR_0`, `MDM_CTL_0`, `MDM_CTL_1`, `AUD_CTL`, `IRR_ETHERNET`, `IRR_USAR`, plus 7 more.

## Control Flow
Boot control flow is descriptor-driven: machine matching calls map/init/timer callbacks, static platform data is registered, DT children are populated where applicable, and late init or arch initcalls finish board-specific devices after core subsystems are ready.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly; static kernel data records board resources, register bases, cached flags, or callback tables; persistent hardware description is encoded as machine descriptors, platform devices, resources, and DT compatibles; suspend paths persist resume vectors and controller state across low-power entry; runtime allocations or mappings must remain valid for later callbacks. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/err.h`, `linux/gpio/driver.h`, `linux/gpio/gpio-reg.h`, `linux/gpio/machine.h`, `linux/init.h`, `linux/ioport.h`, `linux/irq.h`, `linux/kernel.h`, `linux/module.h`, `linux/platform_device.h`, `linux/pm.h`, `linux/serial_core.h`, `linux/slab.h`, `linux/smc91x.h`, `asm/mach-types.h`, `asm/mach/map.h`, `asm/hardware/sa1111.h`, `linux/sizes.h`, plus 4 more.
- Integrates with platform-device/resource registration and legacy board data handoff.
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.
- Integrates with gpiolib lookup tables, GPIO chips, or board GPIO bit definitions.
- Integrates with kernel PM suspend callbacks, CPU suspend/resume assembly, and low-power hardware registers.
- Integrates with AMBA PL080/PL08x DMA platform data and request-signal muxing.

## Risks
- poll loops around hardware status can hang or add boot/suspend latency if clocks, reset bits, or DT register bases are wrong.
- missing DT nodes, failed mappings, or resource conflicts leave platform devices partially unavailable.
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.
- DMA request mux conflicts can silently route a peripheral to the wrong request line.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `neponset.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.
- Exercise suspend/resume or CPU hotplug repeatedly while checking serial console logs, wake sources, and cache/coherency-sensitive workloads.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.
- Run DMA-using peripheral transfers and check that request-line allocation/release pairs do not conflict under concurrent users.

## Research Notes
- Read coverage: full file (11534 bytes, 439 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/neponset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/pm.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/pm.c

## Purpose
This file implements SA-1100 suspend/resume support, including CPU context save/restore coordination and power-manager register programming around the assembly sleep path.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `sa11x0_pm_enter`.
- Register/constant macro families: `RESTORE`(1), `SAVE`(1); examples: `SAVE`, `RESTORE`.

## Control Flow
Suspend control flow registers platform suspend operations at init time. On suspend, the code prepares resume vectors and controller state, enters `cpu_suspend()` or a platform low-power path, and on wake restores cache/coherency or controller state before returning to generic PM.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: static kernel data records board resources, register bases, cached flags, or callback tables; suspend paths persist resume vectors and controller state across low-power entry; runtime allocations or mappings must remain valid for later callbacks. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/init.h`, `linux/io.h`, `linux/suspend.h`, `linux/errno.h`, `linux/time.h`, `mach/hardware.h`, `asm/page.h`, `asm/suspend.h`, `asm/mach/time.h`, `generic.h`.
- Integrates with gpiolib lookup tables, GPIO chips, or board GPIO bit definitions.
- Integrates with kernel PM suspend callbacks, CPU suspend/resume assembly, and low-power hardware registers.

## Risks
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `pm.c`.
- Exercise suspend/resume or CPU hotplug repeatedly while checking serial console logs, wake sources, and cache/coherency-sensitive workloads.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.

## Research Notes
- Read coverage: full file (2668 bytes, 129 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/sleep.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/sleep.S

## Purpose
This ARM assembly file is the SA-1100 low-power entry/resume trampoline. It saves CPU state, programs SDRAM/power state, enters sleep, and restores execution after wakeup.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `sa1100_finish_suspend`.

## Control Flow
Control flow is entered from C suspend code, runs with tight constraints, touches physical controller registers directly, waits or executes WFI, and returns to the caller with hardware state restored enough for C resume code to continue.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: suspend paths persist resume vectors and controller state across low-power entry; in-memory locks serialize access to shared controller state. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/linkage.h`, `asm/assembler.h`, `mach/hardware.h`.
- Integrates with kernel PM suspend callbacks, CPU suspend/resume assembly, and low-power hardware registers.

## Risks
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.

## Test Signals
- Build with the relevant SMP or suspend option enabled to assemble the entry code, then boot/suspend on hardware or a board model capable of exercising the path.
- Exercise suspend/resume or CPU hotplug repeatedly while checking serial console logs, wake sources, and cache/coherency-sensitive workloads.

## Research Notes
- Read coverage: full file (2898 bytes, 144 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/sleep.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/ssp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/ssp.c

## Purpose
This file provides the shared SA-1100 SSP access layer with open/close, transmit/receive, flush, and control helpers for board code that needs synchronous serial transactions.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `ssp_write_word`, `ssp_read_word`, `ssp_flush`, `ssp_enable`, `ssp_disable`, `ssp_save_state`, `ssp_restore_state`, `ssp_init`, `ssp_exit`.
- Exported symbols: `ssp_write_word`, `ssp_read_word`, `ssp_flush`, `ssp_enable`, `ssp_disable`, `ssp_save_state`, `ssp_restore_state`, `ssp_init`, `ssp_exit`.
- Register/constant macro families: `TIMEOUT`(1); examples: `TIMEOUT`.

## Control Flow
Runtime control flow is called from adjacent platform init code or driver callbacks. It generally maps hardware registers, updates control bits, registers platform data, then returns errors upward when required resources are absent.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly; suspend paths persist resume vectors and controller state across low-power entry; in-memory locks serialize access to shared controller state. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/module.h`, `linux/kernel.h`, `linux/sched.h`, `linux/errno.h`, `linux/interrupt.h`, `linux/ioport.h`, `linux/init.h`, `linux/io.h`, `mach/hardware.h`, `mach/irqs.h`, `asm/hardware/ssp.h`.
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.
- Integrates with kernel PM suspend callbacks, CPU suspend/resume assembly, and low-power hardware registers.

## Risks
- missing DT nodes, failed mappings, or resource conflicts leave platform devices partially unavailable.
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `ssp.c`.
- Exercise suspend/resume or CPU hotplug repeatedly while checking serial console logs, wake sources, and cache/coherency-sensitive workloads.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.

## Research Notes
- Read coverage: full file (4743 bytes, 241 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/ssp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/Kconfig

## Purpose
This Kconfig fragment selects the generic Renesas shmobile ARM platform support used by DT-only Renesas ARM SoCs in this tree.

## Important APIs, Types, and Functions
- Kconfig symbols: `ARCH_RENESAS`.

## Control Flow
Kconfig evaluation is declarative: selecting the platform symbol pulls in architecture, timer, clock, SMP, hotplug, and PM dependencies. No runtime code executes from this file, but the resulting `.config` decides which adjacent objects are compiled.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Integrates with AMBA PL080/PL08x DMA platform data and request-signal muxing.

## Risks
- DMA request mux conflicts can silently route a peripheral to the wrong request line.

## Test Signals
- Build configuration smoke test: enable the relevant platform symbols and run `make ARCH=arm olddefconfig` plus a build that descends into `sources/distributed-fs/ceph-client/arch/arm/mach-shmobile`.
- Run DMA-using peripheral transfers and check that request-line allocation/release pairs do not conflict under concurrent users.

## Research Notes
- Read coverage: full file (177 bytes, 8 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/Makefile

## Purpose
This Makefile defines which Renesas shmobile platform objects are built for SMP, suspend, timer, setup, and regulator quirk support.

## Important APIs, Types, and Functions
- Build rules: `obj-y -> timer.o`, `obj-$(CONFIG_ARCH_SH73A0) -> setup-sh73a0.o`, `obj-$(CONFIG_ARCH_R8A73A4) -> setup-r8a73a4.o`, `obj-$(CONFIG_ARCH_R8A7740) -> setup-r8a7740.o`, `obj-$(CONFIG_ARCH_R8A7778) -> setup-r8a7778.o`, `obj-$(CONFIG_ARCH_R8A7779) -> setup-r8a7779.o`, `obj-$(CONFIG_ARCH_EMEV2) -> setup-emev2.o`, `obj-$(CONFIG_ARCH_R7S72100) -> setup-r7s72100.o`, `obj-$(CONFIG_ARCH_R7S9210) -> setup-r7s9210.o`, `obj-$(CONFIG_ARCH_RCAR_GEN2) -> setup-rcar-gen2.o platsmp-apmu.o $(cpu-y)`, `obj-$(CONFIG_ARCH_R8A7790) -> regulator-quirk-rcar-gen2.o`, `obj-$(CONFIG_ARCH_R8A7791) -> regulator-quirk-rcar-gen2.o`.

## Control Flow
Build control flow is make-driven. Configuration symbols expand object lists, so later boot-time behavior appears only when the corresponding `obj-*` rule includes the source file in `built-in.a`.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: suspend paths persist resume vectors and controller state across low-power entry. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.
- Integrates with kernel PM suspend callbacks, CPU suspend/resume assembly, and low-power hardware registers.

## Risks
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.

## Test Signals
- Build configuration smoke test: enable the relevant platform symbols and run `make ARCH=arm olddefconfig` plus a build that descends into `sources/distributed-fs/ceph-client/arch/arm/mach-shmobile`.
- Exercise suspend/resume or CPU hotplug repeatedly while checking serial console logs, wake sources, and cache/coherency-sensitive workloads.

## Research Notes
- Read coverage: full file (1320 bytes, 42 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/common.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/common.h

## Purpose
This private shmobile header declares the shared SMP, suspend, timer, and setup hooks used across the Renesas platform files.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `shmobile_suspend_init`, `shmobile_smp_apmu_suspend_init`.
- Register/constant macro families: `__AR`(1); examples: `__ARCH_MACH_COMMON_H`.

## Control Flow
Runtime control flow is called from adjacent platform init code or driver callbacks. It generally maps hardware registers, updates control bits, registers platform data, then returns errors upward when required resources are absent.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: suspend paths persist resume vectors and controller state across low-power entry. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.
- Integrates with kernel PM suspend callbacks, CPU suspend/resume assembly, and low-power hardware registers.

## Risks
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.
- Exercise suspend/resume or CPU hotplug repeatedly while checking serial console logs, wake sources, and cache/coherency-sensitive workloads.

## Research Notes
- Read coverage: full file (1360 bytes, 40 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/emev2.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/emev2.h

## Purpose
This private platform header exposes declarations or constants shared by the adjacent `mach-shmobile` platform code.

## Important APIs, Types, and Functions
- Register/constant macro families: `__AS`(1); examples: `__ASM_EMEV2_H__`.

## Control Flow
Runtime control flow is called from adjacent platform init code or driver callbacks. It generally maps hardware registers, updates control bits, registers platform data, then returns errors upward when required resources are absent.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.

## Risks
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.

## Research Notes
- Read coverage: full file (168 bytes, 8 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/emev2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/headsmp-apmu.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/headsmp-apmu.S

## Purpose
This assembly file contains the APMU-specific secondary CPU entry symbol that immediately branches into the common ARM secondary startup path.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `shmobile_boot_apmu`.

## Control Flow
Control flow begins when platform C code releases a secondary CPU or installs a boot vector. The assembly entry loads the expected physical target or branch address, performs any required endian/address fixups, then branches to common ARM secondary startup code.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/linkage.h`, `asm/assembler.h`.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.

## Risks
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.

## Test Signals
- Build with the relevant SMP or suspend option enabled to assemble the entry code, then boot/suspend on hardware or a board model capable of exercising the path.

## Research Notes
- Read coverage: full file (316 bytes, 15 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/headsmp-apmu.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/headsmp-scu.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/headsmp-scu.S

## Purpose
This assembly file contains the SCU-specific secondary CPU entry path used after platform code releases a secondary core.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `shmobile_boot_scu`.

## Control Flow
Control flow begins when platform C code releases a secondary CPU or installs a boot vector. The assembly entry loads the expected physical target or branch address, performs any required endian/address fixups, then branches to common ARM secondary startup code.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/linkage.h`, `linux/init.h`, `asm/page.h`.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.

## Risks
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.

## Test Signals
- Build with the relevant SMP or suspend option enabled to assemble the entry code, then boot/suspend on hardware or a board model capable of exercising the path.

## Research Notes
- Read coverage: full file (806 bytes, 32 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/headsmp-scu.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/headsmp.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/headsmp.S

## Purpose
This assembly file implements shared shmobile SMP boot/sleep/reset helper code and boot-vector handoff used by Renesas CPU bring-up paths.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `shmobile_boot_vector`, `shmobile_boot_vector_gen2`, `shmobile_smp_boot`, `shmobile_smp_sleep`.
- Register/constant macro families: `RWTCSRA`(2), `BOOTROM`(1), `SCTLR`(1); examples: `SCTLR_MMU`, `BOOTROM_ADDRESS`, `RWTCSRA_ADDRESS`, `RWTCSRA_WOVF`.

## Control Flow
Control flow begins when platform C code releases a secondary CPU or installs a boot vector. The assembly entry loads the expected physical target or branch address, performs any required endian/address fixups, then branches to common ARM secondary startup code.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: suspend paths persist resume vectors and controller state across low-power entry. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/init.h`, `linux/linkage.h`, `linux/threads.h`, `asm/assembler.h`, `asm/page.h`.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.
- Integrates with kernel PM suspend callbacks, CPU suspend/resume assembly, and low-power hardware registers.

## Risks
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.

## Test Signals
- Build with the relevant SMP or suspend option enabled to assemble the entry code, then boot/suspend on hardware or a board model capable of exercising the path.
- Exercise suspend/resume or CPU hotplug repeatedly while checking serial console logs, wake sources, and cache/coherency-sensitive workloads.

## Research Notes
- Read coverage: full file (3094 bytes, 149 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/headsmp.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/platsmp-apmu.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/platsmp-apmu.c

## Purpose
This file implements Renesas APMU-backed SMP support: parsing APMU DT nodes, mapping per-CPU power controller registers, powering CPUs on/off, hotplug shutdown, and suspend integration.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `cpu_enter_lowpower_a15`, `shmobile_smp_apmu_cpu_shutdown`, `shmobile_smp_apmu_cpu_die`, `shmobile_smp_apmu_cpu_kill`, `shmobile_smp_apmu_do_suspend`, `cpu_leave_lowpower`, `shmobile_smp_apmu_enter_suspend`, `apmu_init_cpu`, `apmu_parse_dt`, `shmobile_smp_apmu_boot_secondary`.
- Static data/types: `smp_operations apmu_smp_ops`.
- Device-tree compatible strings: `renesas,apmu`.
- Register/constant macro families: `CPUST`(2), `CPUNCR`(1), `CPUNST`(1), `DBGCPUNREN`(1), `DBGCPUPREN`(1), `DBGCPUREN`(1), `DBGRCR`(1), `PSTR`(1); examples: `WUPCR_OFFS`, `PSTR_OFFS`, `CPUNCR_OFFS`, `DBGRCR_OFFS`, `CPUNST`, `CPUST_RUN`, `CPUST_STANDBY`, `DBGCPUREN`, `DBGCPUNREN`, `DBGCPUPREN`.

## Control Flow
The SMP path maps controller registers during early init, installs boot vectors or reset hooks for a target CPU, releases that CPU from reset or standby, waits for the common secondary startup path to report online, and optionally powers the CPU back down during hotplug or suspend.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly; static kernel data records board resources, register bases, cached flags, or callback tables; suspend paths persist resume vectors and controller state across low-power entry; runtime allocations or mappings must remain valid for later callbacks. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/cpu_pm.h`, `linux/delay.h`, `linux/init.h`, `linux/io.h`, `linux/ioport.h`, `linux/of.h`, `linux/of_address.h`, `linux/smp.h`, `linux/suspend.h`, `linux/threads.h`, `asm/cacheflush.h`, `asm/cp15.h`, `asm/proc-fns.h`, `asm/smp_plat.h`, `asm/suspend.h`, `common.h`, `rcar-gen2.h`.
- Integrates with device tree matching, `of_*` helpers, and `of_platform_populate()`/machine descriptors where present.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.
- Integrates with kernel PM suspend callbacks, CPU suspend/resume assembly, and low-power hardware registers.

## Risks
- poll loops around hardware status can hang or add boot/suspend latency if clocks, reset bits, or DT register bases are wrong.
- missing DT nodes, failed mappings, or resource conflicts leave platform devices partially unavailable.
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.
- compatible-string drift between DTS and machine/setup code prevents the intended initialization path from running.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `platsmp-apmu.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.
- Exercise suspend/resume or CPU hotplug repeatedly while checking serial console logs, wake sources, and cache/coherency-sensitive workloads.

## Research Notes
- Read coverage: full file (6867 bytes, 283 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/platsmp-apmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/platsmp-scu.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/platsmp-scu.c

## Purpose
This file implements Renesas SCU-backed SMP support for SoCs that use a Cortex-A9 SCU and a platform boot vector instead of APMU registers.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `shmobile_scu_cpu_prepare`, `shmobile_smp_scu_cpu_die`, `shmobile_smp_scu_psr_core_disabled`, `shmobile_smp_scu_cpu_kill`.

## Control Flow
The SMP path maps controller registers during early init, installs boot vectors or reset hooks for a target CPU, releases that CPU from reset or standby, waits for the common secondary startup path to report online, and optionally powers the CPU back down during hotplug or suspend.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly; static kernel data records board resources, register bases, cached flags, or callback tables; suspend paths persist resume vectors and controller state across low-power entry; runtime allocations or mappings must remain valid for later callbacks. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/cpu.h`, `linux/delay.h`, `linux/init.h`, `linux/io.h`, `linux/smp.h`, `asm/cacheflush.h`, `asm/smp_plat.h`, `asm/smp_scu.h`, `common.h`.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.
- Integrates with kernel PM suspend callbacks, CPU suspend/resume assembly, and low-power hardware registers.

## Risks
- poll loops around hardware status can hang or add boot/suspend latency if clocks, reset bits, or DT register bases are wrong.
- missing DT nodes, failed mappings, or resource conflicts leave platform devices partially unavailable.
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `platsmp-scu.c`.
- Exercise suspend/resume or CPU hotplug repeatedly while checking serial console logs, wake sources, and cache/coherency-sensitive workloads.

## Research Notes
- Read coverage: full file (2215 bytes, 91 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/platsmp-scu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/platsmp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/platsmp.c

## Purpose
This file contains shared shmobile SMP glue for DT CPU enable-method probing and registration of platform SMP operations.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `shmobile_smp_hook`, `shmobile_smp_cpu_can_disable`.

## Control Flow
The SMP path maps controller registers during early init, installs boot vectors or reset hooks for a target CPU, releases that CPU from reset or standby, waits for the common secondary startup path to report online, and optionally powers the CPU back down during hotplug or suspend.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/init.h`, `asm/cacheflush.h`, `asm/smp_plat.h`, `common.h`.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.

## Risks
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `platsmp.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.

## Research Notes
- Read coverage: full file (851 bytes, 36 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/platsmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/pm-rcar-gen2.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/pm-rcar-gen2.c

## Purpose
This file installs R-Car Gen2 power-management hooks, especially suspend-to-RAM preparation around SYSC and CPU resume paths.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `phys_to_sbar`.
- Register/constant macro families: `CA15RESCNT`(3), `CA7RESCNT`(3), `CA15BAR`(1), `CA7BAR`(1), `ICRAM1`(1), `RST`(1), `SBAR`(1); examples: `RST`, `CA15BAR`, `CA7BAR`, `CA15RESCNT`, `CA7RESCNT`, `SBAR_BAREN`, `CA15RESCNT_CODE`, `CA15RESCNT_CPUS`, `CA7RESCNT_CODE`, `CA7RESCNT_CPUS`, `ICRAM1`.

## Control Flow
Suspend control flow registers platform suspend operations at init time. On suspend, the code prepares resume vectors and controller state, enters `cpu_suspend()` or a platform low-power path, and on wake restores cache/coherency or controller state before returning to generic PM.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly; suspend paths persist resume vectors and controller state across low-power entry; runtime allocations or mappings must remain valid for later callbacks. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/kernel.h`, `linux/ioport.h`, `linux/of.h`, `linux/of_address.h`, `linux/smp.h`, `asm/io.h`, `asm/cputype.h`, `common.h`, `rcar-gen2.h`.
- Integrates with device tree matching, `of_*` helpers, and `of_platform_populate()`/machine descriptors where present.
- Integrates with platform-device/resource registration and legacy board data handoff.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.
- Integrates with kernel PM suspend callbacks, CPU suspend/resume assembly, and low-power hardware registers.

## Risks
- missing DT nodes, failed mappings, or resource conflicts leave platform devices partially unavailable.
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.
- compatible-string drift between DTS and machine/setup code prevents the intended initialization path from running.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `pm-rcar-gen2.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.
- Exercise suspend/resume or CPU hotplug repeatedly while checking serial console logs, wake sources, and cache/coherency-sensitive workloads.

## Research Notes
- Read coverage: full file (3285 bytes, 131 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/pm-rcar-gen2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/r8a7779.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/r8a7779.h

## Purpose
This private platform header exposes declarations or constants shared by the adjacent `mach-shmobile` platform code.

## Important APIs, Types, and Functions
- Register/constant macro families: `__AS`(1); examples: `__ASM_R8A7779_H__`.

## Control Flow
Runtime control flow is called from adjacent platform init code or driver callbacks. It generally maps hardware registers, updates control bits, registers platform data, then returns errors upward when required resources are absent.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.

## Risks
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.

## Research Notes
- Read coverage: full file (176 bytes, 8 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/r8a7779.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/rcar-gen2.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/rcar-gen2.h

## Purpose
This private platform header exposes declarations or constants shared by the adjacent `mach-shmobile` platform code.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `rcar_gen2_pm_init`.
- Register/constant macro families: `__AS`(1); examples: `__ASM_RCAR_GEN2_H__`.

## Control Flow
Runtime control flow is called from adjacent platform init code or driver callbacks. It generally maps hardware registers, updates control bits, registers platform data, then returns errors upward when required resources are absent.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Integrates with kernel PM suspend callbacks, CPU suspend/resume assembly, and low-power hardware registers.

## Risks
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.

## Research Notes
- Read coverage: full file (160 bytes, 8 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/rcar-gen2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/regulator-quirk-rcar-gen2.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/regulator-quirk-rcar-gen2.c

## Purpose
This file applies an early regulator/I2C quirk for R-Car Gen2 boards so CPU voltage regulators can be located and used before ordinary device probing has completed.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `regulator_quirk_notify`.
- Initcall hooks: `rcar_gen2_regulator_quirk`.
- Static data/types: `i2c_msg da9063_msg`, `i2c_msg da9210_msg`, `notifier_block regulator_quirk_nb`.
- Device-tree compatible strings: `dlg,da9063`, `dlg,da9063l`, `dlg,da9210`.
- Register/constant macro families: `IRQC`(2), `DA9210`(1), `REGULATOR`(1); examples: `IRQC_BASE`, `IRQC_MONITOR`, `REGULATOR_IRQ_MASK`, `DA9210_REG_MASK_A`.

## Control Flow
The quirk runs early, scans DT/I2C nodes for known regulator layouts, creates lookup glue before normal probe order would make it available, and exits after the board-specific workaround is installed.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly; static kernel data records board resources, register bases, cached flags, or callback tables; in-memory locks serialize access to shared controller state; runtime allocations or mappings must remain valid for later callbacks. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/device.h`, `linux/i2c.h`, `linux/init.h`, `linux/io.h`, `linux/list.h`, `linux/notifier.h`, `linux/of.h`, `linux/of_irq.h`, `linux/mfd/da9063/registers.h`.
- Integrates with device tree matching, `of_*` helpers, and `of_platform_populate()`/machine descriptors where present.
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.

## Risks
- missing DT nodes, failed mappings, or resource conflicts leave platform devices partially unavailable.
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.
- compatible-string drift between DTS and machine/setup code prevents the intended initialization path from running.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `regulator-quirk-rcar-gen2.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.

## Research Notes
- Read coverage: full file (5868 bytes, 230 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/regulator-quirk-rcar-gen2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/setup-emev2.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/setup-emev2.c

## Purpose
This Renesas shmobile setup file declares the DT machine descriptor for `emev2` and connects the SoC compatible string to the common shmobile init, timer, and optional SMP/power hooks.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `EMEV2_DT (Generic Emma Mobile EV2 (Flattened Device Tree))`.

## Control Flow
Boot control flow enters through the `DT_MACHINE_START` descriptor after device-tree compatible matching. The descriptor selects common init callbacks such as timer setup, `init_late`, SMP ops, and `init_machine`, which then populate devices from DT or install SoC quirks.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: static kernel data records board resources, register bases, cached flags, or callback tables; persistent hardware description is encoded as machine descriptors, platform devices, resources, and DT compatibles. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/kernel.h`, `linux/init.h`, `linux/mm.h`, `asm/mach-types.h`, `asm/mach/arch.h`, `asm/mach/map.h`, `common.h`, `emev2.h`.
- Integrates with device tree matching, `of_*` helpers, and `of_platform_populate()`/machine descriptors where present.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.

## Risks
- compatible-string drift between DTS and machine/setup code prevents the intended initialization path from running.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `setup-emev2.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.

## Research Notes
- Read coverage: full file (637 bytes, 28 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/setup-emev2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/setup-r7s72100.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/setup-r7s72100.c

## Purpose
This Renesas shmobile setup file declares the DT machine descriptor for `r7s72100` and connects the SoC compatible string to the common shmobile init, timer, and optional SMP/power hooks.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `R7S72100_DT (Generic R7S72100 (Flattened Device Tree))`.

## Control Flow
Boot control flow enters through the `DT_MACHINE_START` descriptor after device-tree compatible matching. The descriptor selects common init callbacks such as timer setup, `init_late`, SMP ops, and `init_machine`, which then populate devices from DT or install SoC quirks.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: static kernel data records board resources, register bases, cached flags, or callback tables; persistent hardware description is encoded as machine descriptors, platform devices, resources, and DT compatibles. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/kernel.h`, `asm/mach/arch.h`, `common.h`.
- Integrates with device tree matching, `of_*` helpers, and `of_platform_populate()`/machine descriptors where present.

## Risks
- compatible-string drift between DTS and machine/setup code prevents the intended initialization path from running.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `setup-r7s72100.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.

## Research Notes
- Read coverage: full file (577 bytes, 27 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/setup-r7s72100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/setup-r7s9210.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/setup-r7s9210.c

## Purpose
This Renesas shmobile setup file declares the DT machine descriptor for `r7s9210` and connects the SoC compatible string to the common shmobile init, timer, and optional SMP/power hooks.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `R7S72100_DT (Generic R7S9210 (Flattened Device Tree))`.

## Control Flow
Boot control flow enters through the `DT_MACHINE_START` descriptor after device-tree compatible matching. The descriptor selects common init callbacks such as timer setup, `init_late`, SMP ops, and `init_machine`, which then populate devices from DT or install SoC quirks.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: static kernel data records board resources, register bases, cached flags, or callback tables; persistent hardware description is encoded as machine descriptors, platform devices, resources, and DT compatibles. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/kernel.h`, `asm/mach/arch.h`, `common.h`.
- Integrates with device tree matching, `of_*` helpers, and `of_platform_populate()`/machine descriptors where present.

## Risks
- compatible-string drift between DTS and machine/setup code prevents the intended initialization path from running.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `setup-r7s9210.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.

## Research Notes
- Read coverage: full file (584 bytes, 28 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/setup-r7s9210.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/setup-r8a73a4.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/setup-r8a73a4.c

## Purpose
This Renesas shmobile setup file declares the DT machine descriptor for `r8a73a4` and connects the SoC compatible string to the common shmobile init, timer, and optional SMP/power hooks.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `R8A73A4_DT (Generic R8A73A4 (Flattened Device Tree))`.

## Control Flow
Boot control flow enters through the `DT_MACHINE_START` descriptor after device-tree compatible matching. The descriptor selects common init callbacks such as timer setup, `init_late`, SMP ops, and `init_machine`, which then populate devices from DT or install SoC quirks.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: static kernel data records board resources, register bases, cached flags, or callback tables; persistent hardware description is encoded as machine descriptors, platform devices, resources, and DT compatibles. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/init.h`, `asm/mach/arch.h`, `common.h`.
- Integrates with device tree matching, `of_*` helpers, and `of_platform_populate()`/machine descriptors where present.

## Risks
- compatible-string drift between DTS and machine/setup code prevents the intended initialization path from running.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `setup-r8a73a4.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.

## Research Notes
- Read coverage: full file (488 bytes, 24 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/setup-r8a73a4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/setup-r8a7740.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/setup-r8a7740.c

## Purpose
This Renesas shmobile setup file declares the DT machine descriptor for `r8a7740` and connects the SoC compatible string to the common shmobile init, timer, and optional SMP/power hooks.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `R8A7740_DT (Generic R8A7740 (Flattened Device Tree))`.
- Register/constant macro families: `MEBUFCNTR`(1); examples: `MEBUFCNTR`.

## Control Flow
Boot control flow enters through the `DT_MACHINE_START` descriptor after device-tree compatible matching. The descriptor selects common init callbacks such as timer setup, `init_late`, SMP ops, and `init_machine`, which then populate devices from DT or install SoC quirks.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly; static kernel data records board resources, register bases, cached flags, or callback tables; persistent hardware description is encoded as machine descriptors, platform devices, resources, and DT compatibles; runtime allocations or mappings must remain valid for later callbacks. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/kernel.h`, `linux/init.h`, `linux/io.h`, `linux/irqchip.h`, `linux/irqchip/arm-gic.h`, `asm/mach/map.h`, `asm/mach/arch.h`, `asm/mach/time.h`, `common.h`.
- Integrates with device tree matching, `of_*` helpers, and `of_platform_populate()`/machine descriptors where present.
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.

## Risks
- missing DT nodes, failed mappings, or resource conflicts leave platform devices partially unavailable.
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.
- compatible-string drift between DTS and machine/setup code prevents the intended initialization path from running.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `setup-r8a7740.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.

## Research Notes
- Read coverage: full file (2119 bytes, 87 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/setup-r8a7740.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/setup-r8a7778.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/setup-r8a7778.c

## Purpose
This Renesas shmobile setup file declares the DT machine descriptor for `r8a7778` and connects the SoC compatible string to the common shmobile init, timer, and optional SMP/power hooks.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `R8A7778_DT (Generic R8A7778 (Flattened Device Tree))`.
- Register/constant macro families: `HPBREG`(1), `INT2NTSR0`(1), `INT2NTSR1`(1), `INT2SMSKCR0`(1), `INT2SMSKCR1`(1); examples: `HPBREG_BASE`, `INT2SMSKCR0`, `INT2SMSKCR1`, `INT2NTSR0`, `INT2NTSR1`.

## Control Flow
Boot control flow enters through the `DT_MACHINE_START` descriptor after device-tree compatible matching. The descriptor selects common init callbacks such as timer setup, `init_late`, SMP ops, and `init_machine`, which then populate devices from DT or install SoC quirks.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly; static kernel data records board resources, register bases, cached flags, or callback tables; persistent hardware description is encoded as machine descriptors, platform devices, resources, and DT compatibles; runtime allocations or mappings must remain valid for later callbacks. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/io.h`, `linux/irqchip.h`, `asm/mach/arch.h`, `common.h`.
- Integrates with device tree matching, `of_*` helpers, and `of_platform_populate()`/machine descriptors where present.
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.

## Risks
- missing DT nodes, failed mappings, or resource conflicts leave platform devices partially unavailable.
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.
- compatible-string drift between DTS and machine/setup code prevents the intended initialization path from running.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `setup-r8a7778.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.

## Research Notes
- Read coverage: full file (1265 bytes, 55 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/setup-r8a7778.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/setup-r8a7779.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/setup-r8a7779.c

## Purpose
This Renesas shmobile setup file declares the DT machine descriptor for `r8a7779` and connects the SoC compatible string to the common shmobile init, timer, and optional SMP/power hooks.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `R8A7779_DT (Generic R8A7779 (Flattened Device Tree))`.
- Register/constant macro families: `HPBREG`(1), `INT2NTSR0`(1), `INT2NTSR1`(1), `INT2SMSKCR0`(1), `INT2SMSKCR1`(1), `INT2SMSKCR2`(1), `INT2SMSKCR3`(1), `INT2SMSKCR4`(1); examples: `HPBREG_BASE`, `INT2SMSKCR0`, `INT2SMSKCR1`, `INT2SMSKCR2`, `INT2SMSKCR3`, `INT2SMSKCR4`, `INT2NTSR0`, `INT2NTSR1`.

## Control Flow
Boot control flow enters through the `DT_MACHINE_START` descriptor after device-tree compatible matching. The descriptor selects common init callbacks such as timer setup, `init_late`, SMP ops, and `init_machine`, which then populate devices from DT or install SoC quirks.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly; static kernel data records board resources, register bases, cached flags, or callback tables; persistent hardware description is encoded as machine descriptors, platform devices, resources, and DT compatibles; runtime allocations or mappings must remain valid for later callbacks. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/init.h`, `linux/irqchip.h`, `asm/mach/arch.h`, `asm/mach/map.h`, `common.h`, `r8a7779.h`.
- Integrates with device tree matching, `of_*` helpers, and `of_platform_populate()`/machine descriptors where present.
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.

## Risks
- missing DT nodes, failed mappings, or resource conflicts leave platform devices partially unavailable.
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.
- compatible-string drift between DTS and machine/setup code prevents the intended initialization path from running.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `setup-r8a7779.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.

## Research Notes
- Read coverage: full file (1708 bytes, 61 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/setup-r8a7779.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/setup-rcar-gen2.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/setup-rcar-gen2.c

## Purpose
This Renesas shmobile setup file declares the DT machine descriptor for `rcar-gen2` and connects the SoC compatible string to the common shmobile init, timer, and optional SMP/power hooks.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `RCAR_GEN2_DT (Generic R-Car Gen2 (Flattened Device Tree))`, `RZ_G1_DT (Generic RZ/G1 (Flattened Device Tree))`.
- Device-tree compatible strings: `renesas,r8a7742-cpg-mssr`, `renesas,r8a7743-cpg-mssr`, `renesas,r8a7744-cpg-mssr`, `renesas,r8a7790-cpg-mssr`, `renesas,r8a7791-cpg-mssr`, `renesas,r8a7793-cpg-mssr`.
- Register/constant macro families: `CNTCR`(1), `CNTFID0`(1); examples: `CNTCR`, `CNTFID0`.

## Control Flow
Boot control flow enters through the `DT_MACHINE_START` descriptor after device-tree compatible matching. The descriptor selects common init callbacks such as timer setup, `init_late`, SMP ops, and `init_machine`, which then populate devices from DT or install SoC quirks.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly; static kernel data records board resources, register bases, cached flags, or callback tables; persistent hardware description is encoded as machine descriptors, platform devices, resources, and DT compatibles; in-memory locks serialize access to shared controller state; runtime allocations or mappings must remain valid for later callbacks. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/clocksource.h`, `linux/io.h`, `linux/kernel.h`, `linux/memblock.h`, `linux/of.h`, `linux/of_clk.h`, `linux/psci.h`, `asm/mach/arch.h`, `asm/secure_cntvoff.h`, `common.h`.
- Integrates with device tree matching, `of_*` helpers, and `of_platform_populate()`/machine descriptors where present.
- Integrates with clocksource/clock framework setup during early platform initialization.

## Risks
- missing DT nodes, failed mappings, or resource conflicts leave platform devices partially unavailable.
- compatible-string drift between DTS and machine/setup code prevents the intended initialization path from running.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `setup-rcar-gen2.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.

## Research Notes
- Read coverage: full file (4032 bytes, 150 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/setup-rcar-gen2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/setup-sh73a0.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/setup-sh73a0.c

## Purpose
This Renesas shmobile setup file declares the DT machine descriptor for `sh73a0` and connects the SoC compatible string to the common shmobile init, timer, and optional SMP/power hooks.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `SH73A0_DT (Generic SH73A0 (Flattened Device Tree))`.

## Control Flow
Boot control flow enters through the `DT_MACHINE_START` descriptor after device-tree compatible matching. The descriptor selects common init callbacks such as timer setup, `init_late`, SMP ops, and `init_machine`, which then populate devices from DT or install SoC quirks.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly; static kernel data records board resources, register bases, cached flags, or callback tables; persistent hardware description is encoded as machine descriptors, platform devices, resources, and DT compatibles; runtime allocations or mappings must remain valid for later callbacks. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/kernel.h`, `linux/init.h`, `linux/interrupt.h`, `linux/irq.h`, `linux/delay.h`, `linux/input.h`, `linux/io.h`, `asm/hardware/cache-l2x0.h`, `asm/mach/map.h`, `asm/mach/arch.h`, `asm/mach/time.h`, `common.h`, `sh73a0.h`.
- Integrates with device tree matching, `of_*` helpers, and `of_platform_populate()`/machine descriptors where present.
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.

## Risks
- missing DT nodes, failed mappings, or resource conflicts leave platform devices partially unavailable.
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.
- compatible-string drift between DTS and machine/setup code prevents the intended initialization path from running.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `setup-sh73a0.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.

## Research Notes
- Read coverage: full file (1045 bytes, 44 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/setup-sh73a0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/sh73a0.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/sh73a0.h

## Purpose
This private platform header exposes declarations or constants shared by the adjacent `mach-shmobile` platform code.

## Important APIs, Types, and Functions
- Register/constant macro families: `__AS`(1); examples: `__ASM_SH73A0_H__`.

## Control Flow
Runtime control flow is called from adjacent platform init code or driver callbacks. It generally maps hardware registers, updates control bits, registers platform data, then returns errors upward when required resources are absent.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.

## Risks
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.

## Research Notes
- Read coverage: full file (172 bytes, 8 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/sh73a0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/smp-emev2.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/smp-emev2.c

## Purpose
This Renesas shmobile SMP file provides SoC-specific CPU bring-up hooks for `emev2`, bridging the generic shmobile SMP layer to that SoC's boot address, reset, or power controller registers.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `emev2_boot_secondary`.
- Register/constant macro families: `EMEV2`(2), `SMU`(1); examples: `EMEV2_SCU_BASE`, `EMEV2_SMU_BASE`, `SMU_GENERAL_REG0`.

## Control Flow
The SMP path maps controller registers during early init, installs boot vectors or reset hooks for a target CPU, releases that CPU from reset or standby, waits for the common secondary startup path to report online, and optionally powers the CPU back down during hotplug or suspend.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly; static kernel data records board resources, register bases, cached flags, or callback tables; in-memory locks serialize access to shared controller state; runtime allocations or mappings must remain valid for later callbacks. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/kernel.h`, `linux/init.h`, `linux/smp.h`, `linux/spinlock.h`, `linux/io.h`, `linux/delay.h`, `asm/smp_plat.h`, `asm/smp_scu.h`, `common.h`, `emev2.h`.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.

## Risks
- missing DT nodes, failed mappings, or resource conflicts leave platform devices partially unavailable.
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `smp-emev2.c`.

## Research Notes
- Read coverage: full file (1189 bytes, 49 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/smp-emev2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/smp-r8a7779.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/smp-r8a7779.c

## Purpose
This Renesas shmobile SMP file provides SoC-specific CPU bring-up hooks for `r8a7779`, bridging the generic shmobile SMP layer to that SoC's boot address, reset, or power controller registers.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `r8a7779_boot_secondary`, `r8a7779_platform_cpu_kill`, `r8a7779_cpu_kill`.
- Register/constant macro families: `AVECR`(1), `HPBREG`(1), `R8A7779`(1); examples: `HPBREG_BASE`, `AVECR`, `R8A7779_SCU_BASE`.

## Control Flow
The SMP path maps controller registers during early init, installs boot vectors or reset hooks for a target CPU, releases that CPU from reset or standby, waits for the common secondary startup path to report online, and optionally powers the CPU back down during hotplug or suspend.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly; static kernel data records board resources, register bases, cached flags, or callback tables; in-memory locks serialize access to shared controller state; runtime allocations or mappings must remain valid for later callbacks. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/kernel.h`, `linux/init.h`, `linux/smp.h`, `linux/spinlock.h`, `linux/io.h`, `linux/delay.h`, `linux/soc/renesas/rcar-sysc.h`, `asm/cacheflush.h`, `asm/smp_plat.h`, `asm/smp_scu.h`, `common.h`, `r8a7779.h`.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.

## Risks
- missing DT nodes, failed mappings, or resource conflicts leave platform devices partially unavailable.
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `smp-r8a7779.c`.

## Research Notes
- Read coverage: full file (1930 bytes, 88 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/smp-r8a7779.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/smp-sh73a0.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/smp-sh73a0.c

## Purpose
This Renesas shmobile SMP file provides SoC-specific CPU bring-up hooks for `sh73a0`, bridging the generic shmobile SMP layer to that SoC's boot address, reset, or power controller registers.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `sh73a0_boot_secondary`.
- Register/constant macro families: `AP`(1), `APARMBAREA`(1), `CPG`(1), `PSTR`(1), `SBAR`(1), `SH73A0`(1), `SRESCR`(1), `SYSC`(1); examples: `CPG_BASE2`, `WUPCR`, `SRESCR`, `PSTR`, `SYSC_BASE`, `SBAR`, `AP_BASE`, `APARMBAREA`, `SH73A0_SCU_BASE`.

## Control Flow
The SMP path maps controller registers during early init, installs boot vectors or reset hooks for a target CPU, releases that CPU from reset or standby, waits for the common secondary startup path to report online, and optionally powers the CPU back down during hotplug or suspend.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly; static kernel data records board resources, register bases, cached flags, or callback tables; runtime allocations or mappings must remain valid for later callbacks. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/kernel.h`, `linux/init.h`, `linux/smp.h`, `linux/io.h`, `linux/delay.h`, `asm/smp_plat.h`, `common.h`, `sh73a0.h`.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.

## Risks
- missing DT nodes, failed mappings, or resource conflicts leave platform devices partially unavailable.
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `smp-sh73a0.c`.

## Research Notes
- Read coverage: full file (2017 bytes, 75 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/smp-sh73a0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/suspend.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/suspend.c

## Purpose
This file defines the shared shmobile suspend operations object and validity policy that SoC-specific code populates.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `shmobile_suspend_default_enter`, `shmobile_suspend_begin`, `shmobile_suspend_end`.
- Static data/types: `platform_suspend_ops shmobile_suspend_ops`.

## Control Flow
Suspend control flow registers platform suspend operations at init time. On suspend, the code prepares resume vectors and controller state, enters `cpu_suspend()` or a platform low-power path, and on wake restores cache/coherency or controller state before returning to generic PM.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: static kernel data records board resources, register bases, cached flags, or callback tables; suspend paths persist resume vectors and controller state across low-power entry. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/pm.h`, `linux/suspend.h`, `linux/module.h`, `linux/err.h`, `linux/cpu.h`, `asm/io.h`, `asm/system_misc.h`, `common.h`.
- Integrates with kernel PM suspend callbacks, CPU suspend/resume assembly, and low-power hardware registers.

## Risks
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `suspend.c`.
- Exercise suspend/resume or CPU hotplug repeatedly while checking serial console logs, wake sources, and cache/coherency-sensitive workloads.

## Research Notes
- Read coverage: full file (897 bytes, 48 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/suspend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/timer.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/timer.c

## Purpose
This file initializes Renesas shmobile timers from device tree and hooks them into ARM machine descriptors.

## Important APIs, Types, and Functions
- This file intentionally exposes no callable API; its value is in build selection, declarations, or a compatibility include path.

## Control Flow
Runtime control flow is called from adjacent platform init code or driver callbacks. It generally maps hardware registers, updates control bits, registers platform data, then returns errors upward when required resources are absent.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: persistent hardware description is encoded as machine descriptors, platform devices, resources, and DT compatibles; in-memory locks serialize access to shared controller state. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/platform_device.h`, `linux/clocksource.h`, `linux/delay.h`, `linux/of_address.h`, `common.h`.
- Integrates with device tree matching, `of_*` helpers, and `of_platform_populate()`/machine descriptors where present.
- Integrates with platform-device/resource registration and legacy board data handoff.
- Integrates with clocksource/clock framework setup during early platform initialization.

## Risks
- main risk is accidental removal or build exclusion of a legacy compatibility file that still has include-path users.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `timer.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.

## Research Notes
- Read coverage: full file (853 bytes, 42 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-shmobile/timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/Kconfig

## Purpose
This Kconfig fragment defines Intel/Altera SoCFPGA ARM platform selection and optional suspend support.

## Important APIs, Types, and Functions
- Kconfig symbols: `ARCH_INTEL_SOCFPGA`, `SOCFPGA_SUSPEND`.

## Control Flow
Kconfig evaluation is declarative: selecting the platform symbol pulls in architecture, timer, clock, SMP, hotplug, and PM dependencies. No runtime code executes from this file, but the resulting `.config` decides which adjacent objects are compiled.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: suspend paths persist resume vectors and controller state across low-power entry. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Integrates with gpiolib lookup tables, GPIO chips, or board GPIO bit definitions.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.
- Integrates with kernel PM suspend callbacks, CPU suspend/resume assembly, and low-power hardware registers.

## Risks
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.

## Test Signals
- Build configuration smoke test: enable the relevant platform symbols and run `make ARCH=arm olddefconfig` plus a build that descends into `sources/distributed-fs/ceph-client/arch/arm/mach-socfpga`.
- Exercise suspend/resume or CPU hotplug repeatedly while checking serial console logs, wake sources, and cache/coherency-sensitive workloads.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.

## Research Notes
- Read coverage: full file (734 bytes, 30 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/Makefile

## Purpose
This Makefile selects SoCFPGA platform, SMP, suspend, and ECC helper objects based on kernel configuration.

## Important APIs, Types, and Functions
- Build rules: `obj-y -> socfpga.o`, `obj-$(CONFIG_SMP) -> headsmp.o platsmp.o`, `obj-$(CONFIG_SOCFPGA_SUSPEND) -> pm.o self-refresh.o`, `obj-$(CONFIG_EDAC_ALTERA_L2C) -> l2_cache.o`, `obj-$(CONFIG_EDAC_ALTERA_OCRAM) -> ocram.o`.

## Control Flow
Build control flow is make-driven. Configuration symbols expand object lists, so later boot-time behavior appears only when the corresponding `obj-*` rule includes the source file in `built-in.a`.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: suspend paths persist resume vectors and controller state across low-power entry. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.
- Integrates with kernel PM suspend callbacks, CPU suspend/resume assembly, and low-power hardware registers.

## Risks
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.

## Test Signals
- Build configuration smoke test: enable the relevant platform symbols and run `make ARCH=arm olddefconfig` plus a build that descends into `sources/distributed-fs/ceph-client/arch/arm/mach-socfpga`.
- Exercise suspend/resume or CPU hotplug repeatedly while checking serial console logs, wake sources, and cache/coherency-sensitive workloads.

## Research Notes
- Read coverage: full file (277 bytes, 11 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/core.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/core.h

## Purpose
This private SoCFPGA header declares reset-manager offsets, reset bits, OCRAM/SDRAM globals, ECC init functions, and SMP trampoline symbols shared by the platform files.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `socfpga_init_l2_ecc`, `socfpga_init_ocram_ecc`, `socfpga_init_arria10_l2_ecc`, `socfpga_init_arria10_ocram_ecc`, `socfpga_sdram_self_refresh`.
- Register/constant macro families: `SOCFPGA`(7), `RSTMGR`(3), `__MA`(1); examples: `__MACH_CORE_H`, `SOCFPGA_RSTMGR_CTRL`, `SOCFPGA_RSTMGR_MODMPURST`, `SOCFPGA_RSTMGR_MODPERRST`, `SOCFPGA_RSTMGR_BRGMODRST`, `SOCFPGA_A10_RSTMGR_CTRL`, `SOCFPGA_A10_RSTMGR_MODMPURST`, `RSTMGR_CTRL_SWCOLDRSTREQ`, `RSTMGR_CTRL_SWWARMRSTREQ`, `RSTMGR_MPUMODRST_CPU1`, `SOCFPGA_SCU_VIRT_BASE`.

## Control Flow
Runtime control flow is called from adjacent platform init code or driver callbacks. It generally maps hardware registers, updates control bits, registers platform data, then returns errors upward when required resources are absent.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly; suspend paths persist resume vectors and controller state across low-power entry. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.

## Risks
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.
- Exercise suspend/resume or CPU hotplug repeatedly while checking serial console logs, wake sources, and cache/coherency-sensitive workloads.

## Research Notes
- Read coverage: full file (1154 bytes, 43 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/headsmp.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/headsmp.S

## Purpose
This assembly file provides the SoCFPGA secondary CPU trampoline that waits for a physical boot address and jumps to the common ARM secondary startup path.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `secondary_trampoline`, `secondary_trampoline_end`.

## Control Flow
Control flow begins when platform C code releases a secondary CPU or installs a boot vector. The assembly entry loads the expected physical target or branch address, performs any required endian/address fixups, then branches to common ARM secondary startup code.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/linkage.h`, `linux/init.h`, `asm/page.h`, `asm/assembler.h`.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.

## Risks
- main risk is accidental removal or build exclusion of a legacy compatibility file that still has include-path users.

## Test Signals
- Build with the relevant SMP or suspend option enabled to assemble the entry code, then boot/suspend on hardware or a board model capable of exercising the path.

## Research Notes
- Read coverage: full file (800 bytes, 34 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/headsmp.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/l2_cache.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/l2_cache.c

## Purpose
This file enables and clears L2 cache ECC for Cyclone/Arria SoCFPGA variants by mapping DT-described system manager or MPU control registers.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `socfpga_init_l2_ecc`, `socfpga_init_arria10_l2_ecc`.
- Register/constant macro families: `A10`(6); examples: `A10_MPU_CTRL_L2_ECC_OFST`, `A10_MPU_CTRL_L2_ECC_EN`, `A10_SYSMGR_ECC_INTMASK_CLR_OFST`, `A10_SYSMGR_ECC_INTMASK_CLR_L2`, `A10_SYSMGR_MPU_CLEAR_L2_ECC_OFST`, `A10_SYSMGR_MPU_CLEAR_L2_ECC`.

## Control Flow
Runtime control flow is called from adjacent platform init code or driver callbacks. It generally maps hardware registers, updates control bits, registers platform data, then returns errors upward when required resources are absent.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/io.h`, `linux/of.h`, `linux/of_address.h`, `core.h`.
- Integrates with device tree matching, `of_*` helpers, and `of_platform_populate()`/machine descriptors where present.
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.

## Risks
- missing DT nodes, failed mappings, or resource conflicts leave platform devices partially unavailable.
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.
- compatible-string drift between DTS and machine/setup code prevents the intended initialization path from running.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `l2_cache.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.

## Research Notes
- Read coverage: full file (2073 bytes, 80 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/l2_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/ocram.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/ocram.c

## Purpose
This file initializes OCRAM ECC for SoCFPGA by finding DT SRAM/sysmgr resources, mapping control registers, and enabling/clearing ECC status.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `socfpga_init_ocram_ecc`, `ecc_set_bits`, `ecc_clear_bits`, `ecc_test_bits`, `altr_init_memory_port`, `socfpga_init_arria10_ocram_ecc`.
- Register/constant macro families: `ALTR`(15), `A10`(3); examples: `ALTR_OCRAM_CLEAR_ECC`, `ALTR_OCRAM_ECC_EN`, `ALTR_A10_ECC_CTRL_OFST`, `ALTR_A10_OCRAM_ECC_EN_CTL`, `ALTR_A10_ECC_INITA`, `ALTR_A10_ECC_INITSTAT_OFST`, `ALTR_A10_ECC_INITCOMPLETEA`, `ALTR_A10_ECC_INITCOMPLETEB`, `ALTR_A10_ECC_ERRINTEN_OFST`, `ALTR_A10_ECC_SERRINTEN`, `ALTR_A10_ECC_INTSTAT_OFST`, `ALTR_A10_ECC_SERRPENA`, `ALTR_A10_ECC_DERRPENA`, `ALTR_A10_ECC_ERRPENA_MASK`, `A10_SYSMGR_ECC_INTMASK_SET_OFST`, `A10_SYSMGR_ECC_INTMASK_CLR_OFST`, plus 2 more.

## Control Flow
Runtime control flow is called from adjacent platform init code or driver callbacks. It generally maps hardware registers, updates control bits, registers platform data, then returns errors upward when required resources are absent.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly; static kernel data records board resources, register bases, cached flags, or callback tables; in-memory locks serialize access to shared controller state. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/delay.h`, `linux/io.h`, `linux/of.h`, `linux/of_address.h`, `core.h`.
- Integrates with device tree matching, `of_*` helpers, and `of_platform_populate()`/machine descriptors where present.

## Risks
- poll loops around hardware status can hang or add boot/suspend latency if clocks, reset bits, or DT register bases are wrong.
- missing DT nodes, failed mappings, or resource conflicts leave platform devices partially unavailable.
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.
- compatible-string drift between DTS and machine/setup code prevents the intended initialization path from running.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `ocram.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.

## Research Notes
- Read coverage: full file (4395 bytes, 170 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/ocram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/platsmp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/platsmp.c

## Purpose
This file implements SoCFPGA SMP bring-up, including mapping the reset manager, writing the secondary trampoline address, releasing CPU1 from reset, and registering SMP operations.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `socfpga_boot_secondary`, `socfpga_a10_boot_secondary`, `socfpga_cpu_die`, `socfpga_cpu_kill`.

## Control Flow
The SMP path maps controller registers during early init, installs boot vectors or reset hooks for a target CPU, releases that CPU from reset or standby, waits for the common secondary startup path to report online, and optionally powers the CPU back down during hotplug or suspend.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly; static kernel data records board resources, register bases, cached flags, or callback tables. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/delay.h`, `linux/init.h`, `linux/smp.h`, `linux/io.h`, `linux/of.h`, `linux/of_address.h`, `asm/cacheflush.h`, `asm/smp_scu.h`, `asm/smp_plat.h`, `core.h`.
- Integrates with device tree matching, `of_*` helpers, and `of_platform_populate()`/machine descriptors where present.
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.

## Risks
- poll loops around hardware status can hang or add boot/suspend latency if clocks, reset bits, or DT register bases are wrong.
- missing DT nodes, failed mappings, or resource conflicts leave platform devices partially unavailable.
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `platsmp.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.

## Research Notes
- Read coverage: full file (3496 bytes, 131 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/platsmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/pm.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/pm.c

## Purpose
This file implements SoCFPGA suspend-to-RAM support by copying a DDR self-refresh routine into OCRAM and invoking it from cpu_suspend while outer cache is disabled.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `socfpga_setup_ocram_self_refresh`, `socfpga_pm_suspend`, `socfpga_pm_enter`.
- Initcall hooks: `socfpga_pm_init`.

## Control Flow
Suspend control flow registers platform suspend operations at init time. On suspend, the code prepares resume vectors and controller state, enters `cpu_suspend()` or a platform low-power path, and on wake restores cache/coherency or controller state before returning to generic PM.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly; static kernel data records board resources, register bases, cached flags, or callback tables; persistent hardware description is encoded as machine descriptors, platform devices, resources, and DT compatibles; suspend paths persist resume vectors and controller state across low-power entry; runtime allocations or mappings must remain valid for later callbacks. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/bitops.h`, `linux/genalloc.h`, `linux/init.h`, `linux/io.h`, `linux/of.h`, `linux/of_platform.h`, `linux/platform_device.h`, `linux/suspend.h`, `asm/suspend.h`, `asm/fncpy.h`, `core.h`.
- Integrates with device tree matching, `of_*` helpers, and `of_platform_populate()`/machine descriptors where present.
- Integrates with platform-device/resource registration and legacy board data handoff.
- Integrates with kernel PM suspend callbacks, CPU suspend/resume assembly, and low-power hardware registers.

## Risks
- missing DT nodes, failed mappings, or resource conflicts leave platform devices partially unavailable.
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.
- compatible-string drift between DTS and machine/setup code prevents the intended initialization path from running.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `pm.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.
- Exercise suspend/resume or CPU hotplug repeatedly while checking serial console logs, wake sources, and cache/coherency-sensitive workloads.

## Research Notes
- Read coverage: full file (3196 bytes, 142 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/self-refresh.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/self-refresh.S

## Purpose
This assembly routine runs from OCRAM during suspend to request SDRAM self-refresh, poll acknowledgements, execute WFI, then clear self-refresh on resume.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `socfpga_sdram_self_refresh`, `socfpga_sdram_self_refresh_sz`.
- Register/constant macro families: `SDR`(2), `SELFRFSHACK`(2), `SELFRSHREQ`(2), `MAX`(1); examples: `MAX_LOOP_COUNT`, `SDR_CTRLGRP_LOWPWREQ_ADDR`, `SDR_CTRLGRP_LOWPWRACK_ADDR`, `SELFRSHREQ_POS`, `SELFRSHREQ_MASK`, `SELFRFSHACK_POS`, `SELFRFSHACK_MASK`.

## Control Flow
Control flow is entered from C suspend code, runs with tight constraints, touches physical controller registers directly, waits or executes WFI, and returns to the caller with hardware state restored enough for C resume code to continue.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: suspend paths persist resume vectors and controller state across low-power entry; in-memory locks serialize access to shared controller state. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/linkage.h`, `asm/assembler.h`.
- Integrates with clocksource/clock framework setup during early platform initialization.

## Risks
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.

## Test Signals
- Build with the relevant SMP or suspend option enabled to assemble the entry code, then boot/suspend on hardware or a board model capable of exercising the path.
- Exercise suspend/resume or CPU hotplug repeatedly while checking serial console logs, wake sources, and cache/coherency-sensitive workloads.

## Research Notes
- Read coverage: full file (3134 bytes, 126 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/self-refresh.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/socfpga.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/socfpga.c

## Purpose
This file is the DT machine setup for SoCFPGA platforms, including reset-manager lookup, system manager/SDRAM base discovery, restart handling, and machine descriptors.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `socfpga_cyclone5_restart`, `socfpga_arria10_restart`, `SOCFPGA (Altera SOCFPGA)`, `SOCFPGA_A10 (Altera SOCFPGA Arria10)`.

## Control Flow
Boot control flow is descriptor-driven: machine matching calls map/init/timer callbacks, static platform data is registered, DT children are populated where applicable, and late init or arch initcalls finish board-specific devices after core subsystems are ready.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly; static kernel data records board resources, register bases, cached flags, or callback tables; persistent hardware description is encoded as machine descriptors, platform devices, resources, and DT compatibles. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/irqchip.h`, `linux/of.h`, `linux/of_address.h`, `linux/reboot.h`, `linux/reset/socfpga.h`, `asm/mach/arch.h`, `asm/mach/map.h`, `asm/cacheflush.h`, `core.h`.
- Integrates with device tree matching, `of_*` helpers, and `of_platform_populate()`/machine descriptors where present.
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.

## Risks
- missing DT nodes, failed mappings, or resource conflicts leave platform devices partially unavailable.
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.
- compatible-string drift between DTS and machine/setup code prevents the intended initialization path from running.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `socfpga.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.

## Research Notes
- Read coverage: full file (2857 bytes, 119 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/socfpga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-spear/Kconfig

## Purpose
This Kconfig fragment describes ST SPEAr3xx and SPEAr13xx ARM platform options, SMP/hotplug dependencies, and machine selections.

## Important APIs, Types, and Functions
- Kconfig symbols: `PLAT_SPEAR`, `ARCH_SPEAR13XX`, `MACH_SPEAR1310`, `MACH_SPEAR1340`, `ARCH_SPEAR3XX`, `MACH_SPEAR300`, `MACH_SPEAR310`, `MACH_SPEAR320`, `ARCH_SPEAR6XX`, `ARCH_SPEAR_AUTO`.

## Control Flow
Kconfig evaluation is declarative: selecting the platform symbol pulls in architecture, timer, clock, SMP, hotplug, and PM dependencies. No runtime code executes from this file, but the resulting `.config` decides which adjacent objects are compiled.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Integrates with gpiolib lookup tables, GPIO chips, or board GPIO bit definitions.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.
- Integrates with clocksource/clock framework setup during early platform initialization.

## Risks
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.

## Test Signals
- Build configuration smoke test: enable the relevant platform symbols and run `make ARCH=arm olddefconfig` plus a build that descends into `sources/distributed-fs/ceph-client/arch/arm/mach-spear`.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.

## Research Notes
- Read coverage: full file (1909 bytes, 91 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-spear/Makefile

## Purpose
This Makefile selects SPEAr platform, clock/timer, DMA, restart, SMP, hotplug, and per-SoC board objects based on configuration.

## Important APIs, Types, and Functions
- Build rules: `obj-y -> restart.o time.o`, `obj-$(CONFIG_ARCH_SPEAR13XX) -> spear13xx.o $(smp-y)`, `obj-$(CONFIG_MACH_SPEAR1310) -> spear1310.o`, `obj-$(CONFIG_MACH_SPEAR1340) -> spear1340.o`, `obj-$(CONFIG_ARCH_SPEAR3XX) -> spear3xx.o`, `obj-$(CONFIG_ARCH_SPEAR3XX) -> pl080.o`, `obj-$(CONFIG_MACH_SPEAR300) -> spear300.o`, `obj-$(CONFIG_MACH_SPEAR310) -> spear310.o`, `obj-$(CONFIG_MACH_SPEAR320) -> spear320.o`, `obj-$(CONFIG_ARCH_SPEAR6XX) -> spear6xx.o`, `obj-$(CONFIG_ARCH_SPEAR6XX) -> pl080.o`.

## Control Flow
Build control flow is make-driven. Configuration symbols expand object lists, so later boot-time behavior appears only when the corresponding `obj-*` rule includes the source file in `built-in.a`.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.
- Integrates with AMBA PL080/PL08x DMA platform data and request-signal muxing.

## Risks
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.
- DMA request mux conflicts can silently route a peripheral to the wrong request line.

## Test Signals
- Build configuration smoke test: enable the relevant platform symbols and run `make ARCH=arm olddefconfig` plus a build that descends into `sources/distributed-fs/ceph-client/arch/arm/mach-spear`.
- Run DMA-using peripheral transfers and check that request-line allocation/release pairs do not conflict under concurrent users.

## Research Notes
- Read coverage: full file (669 bytes, 26 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/generic.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-spear/generic.h

## Purpose
This private SPEAr header declares timer, map_io, L2 cache, restart, SMP startup, CPU hotplug, and DMA platform hooks shared by SPEAr platform files.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `spear_restart`, `spear13xx_secondary_startup`, `spear13xx_cpu_die`.
- Register/constant macro families: `__MA`(1); examples: `__MACH_GENERIC_H`.

## Control Flow
Runtime control flow is called from adjacent platform init code or driver callbacks. It generally maps hardware registers, updates control bits, registers platform data, then returns errors upward when required resources are absent.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/dmaengine.h`, `linux/amba/pl08x.h`, `linux/init.h`, `linux/reboot.h`, `asm/mach/time.h`.
- Integrates with device tree matching, `of_*` helpers, and `of_platform_populate()`/machine descriptors where present.
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.
- Integrates with AMBA PL080/PL08x DMA platform data and request-signal muxing.

## Risks
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.
- DMA request mux conflicts can silently route a peripheral to the wrong request line.
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.
- Run DMA-using peripheral transfers and check that request-line allocation/release pairs do not conflict under concurrent users.

## Research Notes
- Read coverage: full file (1049 bytes, 41 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/headsmp.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-spear/headsmp.S

## Purpose
This assembly file provides the SPEAr13xx secondary CPU holding pen and jump to `secondary_startup` during SMP bring-up.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `spear13xx_secondary_startup`.

## Control Flow
Control flow begins when platform C code releases a secondary CPU or installs a boot vector. The assembly entry loads the expected physical target or branch address, performs any required endian/address fixups, then branches to common ARM secondary startup code.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/linkage.h`, `linux/init.h`.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.

## Risks
- main risk is accidental removal or build exclusion of a legacy compatibility file that still has include-path users.

## Test Signals
- Build with the relevant SMP or suspend option enabled to assemble the entry code, then boot/suspend on hardware or a board model capable of exercising the path.

## Research Notes
- Read coverage: full file (978 bytes, 45 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/headsmp.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/hotplug.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-spear/hotplug.c

## Purpose
This file implements SPEAr13xx CPU hotplug shutdown by disabling coherency/cache state, executing WFI, and reporting spurious wakeups.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `cpu_enter_lowpower`, `cpu_leave_lowpower`, `spear13xx_do_lowpower`, `spear13xx_cpu_die`.

## Control Flow
The SMP path maps controller registers during early init, installs boot vectors or reset hooks for a target CPU, releases that CPU from reset or standby, waits for the common secondary startup path to report online, and optionally powers the CPU back down during hotplug or suspend.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/kernel.h`, `linux/errno.h`, `linux/smp.h`, `asm/cp15.h`, `asm/smp_plat.h`, `generic.h`.
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.

## Risks
- poll loops around hardware status can hang or add boot/suspend latency if clocks, reset bits, or DT register bases are wrong.
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `hotplug.c`.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.

## Research Notes
- Read coverage: full file (1952 bytes, 101 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/hotplug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/misc_regs.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-spear/misc_regs.h

## Purpose
This header defines miscellaneous SPEAr system-register offsets used by platform code, especially the DMA request mux register.

## Important APIs, Types, and Functions
- Register/constant macro families: `DMA`(1), `MISC`(1), `__MA`(1); examples: `__MACH_MISC_REGS_H`, `MISC_BASE`, `DMA_CHN_CFG`.

## Control Flow
Runtime control flow is called from adjacent platform init code or driver callbacks. It generally maps hardware registers, updates control bits, registers platform data, then returns errors upward when required resources are absent.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `spear.h`.
- Integrates with AMBA PL080/PL08x DMA platform data and request-signal muxing.

## Risks
- DMA request mux conflicts can silently route a peripheral to the wrong request line.
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.
- Run DMA-using peripheral transfers and check that request-line allocation/release pairs do not conflict under concurrent users.

## Research Notes
- Read coverage: full file (399 bytes, 18 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/misc_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/pl080.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-spear/pl080.c

## Purpose
This file implements SPEAr PL080 DMA request-signal mux allocation and release with a spinlock-protected in-kernel owner table.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `pl080_get_signal`, `pl080_put_signal`.

## Control Flow
Runtime control flow is called from adjacent platform init code or driver callbacks. It generally maps hardware registers, updates control bits, registers platform data, then returns errors upward when required resources are absent.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly; static kernel data records board resources, register bases, cached flags, or callback tables; in-memory locks serialize access to shared controller state. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/amba/pl08x.h`, `linux/amba/bus.h`, `linux/bug.h`, `linux/err.h`, `linux/io.h`, `linux/spinlock_types.h`, `spear.h`, `misc_regs.h`, `pl080.h`.
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.
- Integrates with AMBA PL080/PL08x DMA platform data and request-signal muxing.

## Risks
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.
- DMA request mux conflicts can silently route a peripheral to the wrong request line.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `pl080.c`.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.
- Run DMA-using peripheral transfers and check that request-line allocation/release pairs do not conflict under concurrent users.

## Research Notes
- Read coverage: full file (1684 bytes, 77 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/pl080.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/pl080.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-spear/pl080.h

## Purpose
This header declares the SPEAr PL080 mux helper API used by DMA platform data.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `pl080_get_signal`, `pl080_put_signal`.
- Register/constant macro families: `__PL`(1); examples: `__PLAT_PL080_H`.

## Control Flow
Runtime control flow is called from adjacent platform init code or driver callbacks. It generally maps hardware registers, updates control bits, registers platform data, then returns errors upward when required resources are absent.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Integrates with AMBA PL080/PL08x DMA platform data and request-signal muxing.

## Risks
- DMA request mux conflicts can silently route a peripheral to the wrong request line.
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.
- Run DMA-using peripheral transfers and check that request-line allocation/release pairs do not conflict under concurrent users.

## Research Notes
- Read coverage: full file (460 bytes, 19 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/pl080.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/platsmp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-spear/platsmp.c

## Purpose
This file implements SPEAr13xx SMP startup, including SCU enablement, boot address programming, secondary CPU wakeup, and SMP ops registration.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `spear_write_pen_release`, `spear13xx_secondary_init`, `spear13xx_boot_secondary`.

## Control Flow
The SMP path maps controller registers during early init, installs boot vectors or reset hooks for a target CPU, releases that CPU from reset or standby, waits for the common secondary startup path to report online, and optionally powers the CPU back down during hotplug or suspend.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly; static kernel data records board resources, register bases, cached flags, or callback tables; in-memory locks serialize access to shared controller state. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/delay.h`, `linux/jiffies.h`, `linux/io.h`, `linux/smp.h`, `asm/cacheflush.h`, `asm/smp_scu.h`, `spear.h`, `generic.h`.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.

## Risks
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `platsmp.c`.

## Research Notes
- Read coverage: full file (3391 bytes, 134 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/platsmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/restart.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-spear/restart.c

## Purpose
This file implements SPEAr restart by requesting a software reset through the miscellaneous system reset control register.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `spear_restart`.
- Register/constant macro families: `SPEAR13XX`(1); examples: `SPEAR13XX_SYS_SW_RES`.

## Control Flow
Runtime control flow is called from adjacent platform init code or driver callbacks. It generally maps hardware registers, updates control bits, registers platform data, then returns errors upward when required resources are absent.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/io.h`, `linux/amba/sp810.h`, `linux/reboot.h`, `asm/system_misc.h`, `spear.h`, `generic.h`.

## Risks
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `restart.c`.

## Research Notes
- Read coverage: full file (857 bytes, 33 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/restart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/spear.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-spear/spear.h

## Purpose
This header centralizes SPEAr physical/virtual address constants, IO mappings, DMA definitions, and platform device declarations shared across SPEAr SoC files.

## Important APIs, Types, and Functions
- Register/constant macro families: `VA`(18), `SPEAR`(10), `A9SM`(2), `MCIF`(2), `PERIP`(2), `L2CC`(1), `MISC`(1), `SPEAR1310`(1); examples: `__MACH_SPEAR_H`, `SPEAR_ICM1_2_BASE`, `VA_SPEAR_ICM1_2_BASE`, `SPEAR_ICM1_UART_BASE`, `VA_SPEAR_ICM1_UART_BASE`, `SPEAR3XX_ICM1_SSP_BASE`, `SPEAR_ICM3_ML1_2_BASE`, `VA_SPEAR6XX_ML_CPU_BASE`, `SPEAR_ICM3_SMI_CTRL_BASE`, `VA_SPEAR_ICM3_SMI_CTRL_BASE`, `SPEAR_ICM3_DMA_BASE`, `SPEAR_ICM3_SYS_CTRL_BASE`, `VA_SPEAR_ICM3_SYS_CTRL_BASE`, `SPEAR_ICM3_MISC_REG_BASE`, `VA_SPEAR_ICM3_MISC_REG_BASE`, `SPEAR_DBG_UART_BASE`, plus 27 more.

## Control Flow
Runtime control flow is called from adjacent platform init code or driver callbacks. It generally maps hardware registers, updates control bits, registers platform data, then returns errors upward when required resources are absent.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `asm/page.h`.
- Integrates with AMBA PL080/PL08x DMA platform data and request-signal muxing.

## Risks
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.
- DMA request mux conflicts can silently route a peripheral to the wrong request line.
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.
- Run DMA-using peripheral transfers and check that request-line allocation/release pairs do not conflict under concurrent users.

## Research Notes
- Read coverage: full file (3021 bytes, 89 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/spear.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/spear1310.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-spear/spear1310.c

## Purpose
This platform source file implements board or SoC initialization glue for `mach-spear`, wiring machine descriptors, device-tree compatibles, memory mappings, interrupt/power helpers, and platform devices into the ARM kernel boot path.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `SPEAR1310_DT (ST SPEAr1310 SoC with Flattened Device Tree)`.
- Static data/types: `map_desc spear1310_io_desc`.
- Register/constant macro families: `SPEAR1310`(1), `VA`(1), `pr`(1); examples: `pr_fmt`, `SPEAR1310_RAS_GRP1_BASE`, `VA_SPEAR1310_RAS_GRP1_BASE`.

## Control Flow
Boot control flow is descriptor-driven: machine matching calls map/init/timer callbacks, static platform data is registered, DT children are populated where applicable, and late init or arch initcalls finish board-specific devices after core subsystems are ready.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: static kernel data records board resources, register bases, cached flags, or callback tables; persistent hardware description is encoded as machine descriptors, platform devices, resources, and DT compatibles. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/amba/pl022.h`, `linux/pata_arasan_cf_data.h`, `asm/mach/arch.h`, `asm/mach/map.h`, `generic.h`, `spear.h`.
- Integrates with device tree matching, `of_*` helpers, and `of_platform_populate()`/machine descriptors where present.
- Integrates with platform-device/resource registration and legacy board data handoff.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.

## Risks
- missing DT nodes, failed mappings, or resource conflicts leave platform devices partially unavailable.
- compatible-string drift between DTS and machine/setup code prevents the intended initialization path from running.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `spear1310.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.

## Research Notes
- Read coverage: full file (1498 bytes, 63 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/spear1310.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/spear1340.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-spear/spear1340.c

## Purpose
This platform source file implements board or SoC initialization glue for `mach-spear`, wiring machine descriptors, device-tree compatibles, memory mappings, interrupt/power helpers, and platform devices into the ARM kernel boot path.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `SPEAR1340_DT (ST SPEAr1340 SoC with Flattened Device Tree)`.
- Register/constant macro families: `pr`(1); examples: `pr_fmt`.

## Control Flow
Boot control flow is descriptor-driven: machine matching calls map/init/timer callbacks, static platform data is registered, DT children are populated where applicable, and late init or arch initcalls finish board-specific devices after core subsystems are ready.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: static kernel data records board resources, register bases, cached flags, or callback tables; persistent hardware description is encoded as machine descriptors, platform devices, resources, and DT compatibles. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/platform_device.h`, `asm/mach/arch.h`, `generic.h`.
- Integrates with device tree matching, `of_*` helpers, and `of_platform_populate()`/machine descriptors where present.
- Integrates with platform-device/resource registration and legacy board data handoff.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.

## Risks
- missing DT nodes, failed mappings, or resource conflicts leave platform devices partially unavailable.
- compatible-string drift between DTS and machine/setup code prevents the intended initialization path from running.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `spear1340.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.

## Research Notes
- Read coverage: full file (845 bytes, 36 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/spear1340.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/spear13xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-spear/spear13xx.c

## Purpose
This file contains common SPEAr13xx setup: L2 cache initialization, static IO mappings, clock/timer setup, and DT clock-source registration.

## Important APIs, Types, and Functions
- Static data/types: `map_desc spear13xx_io_desc`.
- Register/constant macro families: `pr`(1); examples: `pr_fmt`.

## Control Flow
Boot control flow is descriptor-driven: machine matching calls map/init/timer callbacks, static platform data is registered, DT children are populated where applicable, and late init or arch initcalls finish board-specific devices after core subsystems are ready.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly; static kernel data records board resources, register bases, cached flags, or callback tables; in-memory locks serialize access to shared controller state; runtime allocations or mappings must remain valid for later callbacks. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/amba/pl022.h`, `linux/clk.h`, `linux/clk/spear.h`, `linux/clocksource.h`, `linux/err.h`, `linux/of.h`, `asm/hardware/cache-l2x0.h`, `asm/mach/map.h`, `spear.h`, `generic.h`.
- Integrates with device tree matching, `of_*` helpers, and `of_platform_populate()`/machine descriptors where present.
- Integrates with clocksource/clock framework setup during early platform initialization.

## Risks
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.
- compatible-string drift between DTS and machine/setup code prevents the intended initialization path from running.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `spear13xx.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.

## Research Notes
- Read coverage: full file (3102 bytes, 127 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/spear13xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/spear300.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-spear/spear300.c

## Purpose
This file describes the SPEAr300 DT machine, including DMA request mappings, compatible strings, and machine descriptor callbacks.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `SPEAR300_DT (ST SPEAr300 SoC with Flattened Device Tree)`.
- Static data/types: `pl08x_channel_data spear300_dma_info`, `of_dev_auxdata spear300_auxdata_lookup`.
- Register/constant macro families: `pr`(1); examples: `pr_fmt`.

## Control Flow
Boot control flow is descriptor-driven: machine matching calls map/init/timer callbacks, static platform data is registered, DT children are populated where applicable, and late init or arch initcalls finish board-specific devices after core subsystems are ready.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: static kernel data records board resources, register bases, cached flags, or callback tables; persistent hardware description is encoded as machine descriptors, platform devices, resources, and DT compatibles. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/amba/pl08x.h`, `linux/of_platform.h`, `asm/mach/arch.h`, `generic.h`, `spear.h`.
- Integrates with device tree matching, `of_*` helpers, and `of_platform_populate()`/machine descriptors where present.
- Integrates with AMBA PL080/PL08x DMA platform data and request-signal muxing.

## Risks
- compatible-string drift between DTS and machine/setup code prevents the intended initialization path from running.
- DMA request mux conflicts can silently route a peripheral to the wrong request line.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `spear300.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.
- Run DMA-using peripheral transfers and check that request-line allocation/release pairs do not conflict under concurrent users.

## Research Notes
- Read coverage: full file (4347 bytes, 215 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/spear300.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/spear310.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-spear/spear310.c

## Purpose
This file describes the SPEAr310 DT machine and its extended DMA request mappings for multiple UART/RAS peripherals plus AMBA serial resources.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `SPEAR310_DT (ST SPEAr310 SoC with Flattened Device Tree)`.
- Static data/types: `pl08x_channel_data spear310_dma_info`, `amba_pl011_data spear310_uart_data`, `of_dev_auxdata spear310_auxdata_lookup`.
- Register/constant macro families: `SPEAR310`(5), `pr`(1); examples: `pr_fmt`, `SPEAR310_UART1_BASE`, `SPEAR310_UART2_BASE`, `SPEAR310_UART3_BASE`, `SPEAR310_UART4_BASE`, `SPEAR310_UART5_BASE`.

## Control Flow
Boot control flow is descriptor-driven: machine matching calls map/init/timer callbacks, static platform data is registered, DT children are populated where applicable, and late init or arch initcalls finish board-specific devices after core subsystems are ready.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: static kernel data records board resources, register bases, cached flags, or callback tables; persistent hardware description is encoded as machine descriptors, platform devices, resources, and DT compatibles. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/amba/pl08x.h`, `linux/amba/serial.h`, `linux/of_platform.h`, `asm/mach/arch.h`, `generic.h`, `spear.h`.
- Integrates with device tree matching, `of_*` helpers, and `of_platform_populate()`/machine descriptors where present.
- Integrates with AMBA PL080/PL08x DMA platform data and request-signal muxing.

## Risks
- compatible-string drift between DTS and machine/setup code prevents the intended initialization path from running.
- DMA request mux conflicts can silently route a peripheral to the wrong request line.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `spear310.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.
- Run DMA-using peripheral transfers and check that request-line allocation/release pairs do not conflict under concurrent users.

## Research Notes
- Read coverage: full file (5613 bytes, 257 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-spear/spear310.c -->
