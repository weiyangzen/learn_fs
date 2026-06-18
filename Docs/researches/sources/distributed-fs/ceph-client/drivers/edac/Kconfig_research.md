# sources/distributed-fs/ceph-client/drivers/edac/Kconfig Research

## Purpose
This Kconfig file defines the Linux EDAC subsystem configuration surface and all memory-controller, cache, PCI, firmware-first, scrub, ECS, memory-repair, and SoC-specific EDAC driver options under `drivers/edac`. It is the policy layer that decides which EDAC core features and hardware drivers can be selected for a build.

## Important APIs, Types, and Functions
The file is declarative Kconfig rather than C code. The key exported symbols are `EDAC`, `EDAC_DEBUG`, `EDAC_DECODE_MCE`, `EDAC_GHES`, `EDAC_SCRUB`, `EDAC_ECS`, `EDAC_MEM_REPAIR`, and the hardware driver symbols consumed by the Makefile, including `EDAC_AMD64`, `EDAC_AL_MC`, `EDAC_AMD76X`, `EDAC_ALTERA`, `EDAC_ALTERA_*`, and `EDAC_CORTEX_A72`. `EDAC_ATOMIC_SCRUB` and `EDAC_SUPPORT` are helper booleans used by architecture/platform code.

## Control Flow
Kconfig processing first requires `HAS_IOMEM`, `EDAC_SUPPORT`, and `RAS` before exposing the `EDAC` menu. When `EDAC` is enabled, feature booleans and driver tristates/bools become available subject to architecture, bus, and subsystem dependencies. Driver symbols gate compilation through `drivers/edac/Makefile`.

## State and Persistence
The persistent output is kernel build configuration in `.config`. At runtime, this file has no state, but its selected symbols determine whether EDAC sysfs, debugfs, scrub, ECS, memory repair, MCE decoding, firmware-first GHES reporting, and hardware drivers exist in the built kernel or modules.

## Dependencies and Integration Points
The top-level EDAC menu integrates with RAS, architecture support for I/O memory, ACPI/GHES, PCI, x86 MCE decoding, ARM64, LoongArch, PowerPC, SoC platform symbols, and many peripheral subsystem symbols such as `CACHE_L2X0`, `SRAM`, `GENERIC_ALLOCATOR`, `MTD_NAND_DENALI`, `PL330_DMA`, `USB_DWC2`, `SPI_CADENCE_QUADSPI`, and `MMC_DW`. The AMD64 option depends on `AMD_NB`, `AMD_NODE`, and `EDAC_DECODE_MCE`, and implies `AMD_ATL` for normalized-address translation on newer AMD systems.

## Risks and Edge Cases
Configuration mismatches are the main risk. Enabling GHES may suppress native hardware-driven reporting in firmware-first systems. Several Altera options are bool-only and depend on `EDAC=y`, so they are not module-friendly. Platform dependencies can hide drivers during compile testing if `COMPILE_TEST` is absent. Incorrect dependency changes can either expose unbuildable drivers or hide valid EDAC support.

## Test Signals
Useful tests are `make olddefconfig`, `make menuconfig`, and targeted builds with representative symbols enabled. Cross-architecture build tests should confirm each enabled config reaches the expected object in the Makefile. Runtime signals include EDAC devices under `/sys/devices/system/edac`, GHES/EDAC ownership behavior, and debugfs/sysfs feature files when the corresponding feature symbols are enabled.
