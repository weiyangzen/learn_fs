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
