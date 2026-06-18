# sources/distributed-fs/ceph-client/drivers/pci/controller/Kconfig

Purpose: PCI host/controller driver menu. It collects platform-specific root complex, endpoint, MSI, ECAM, bridge-emulation, and error-handling configuration for many SoC and firmware environments.

Important symbols: common support includes `PCI_HOST_COMMON` selecting `PCI_ECAM`; individual controllers include Aardvark, Altera, Apple, Aspeed, Broadcom STB/iProc, Cavium Thunder, Faraday, generic host, HiSilicon error, IXP4xx, VMD, Loongson, Marvell EBU, MediaTek, Hyper-V interface, Tegra, Renesas R-Car/RZ, Rockchip host/EP, V3, X-Gene, Xilinx variants, and sourced Cadence/DWC/Mobiveil/PLDA menus.

Control flow/state: Kconfig selections determine which controller objects are compiled by `controller/Makefile` and which shared infrastructure is enabled, especially MSI libraries, bridge emulation, ECAM, MFD syscon, endpoint support, and platform/OF dependencies.

Dependencies/integration: links architecture symbols, OF/ACPI availability, PCI core features, MSI infrastructure, endpoint framework, and compile-test coverage. Risks are dependency cycles, accidental hidden selects, allmodconfig build failures on compile-test paths, and controller options missing required shared infrastructure. Test signals include Kconfig warning-free resolution, cross-architecture compile tests, OF/ACPI combinations, and controller-specific boot probes.
