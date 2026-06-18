# sources/distributed-fs/ceph-client/drivers/pci/controller/Makefile

Purpose: maps PCI controller Kconfig symbols to controller object files and subdirectories.

Important build rules: conditionally enters `cadence/` for `CONFIG_PCIE_CADENCE`, builds individual controller objects for Aardvark, Hyper-V, MVEBU, Tegra, Renesas, generic host, Thunder, Xilinx, X-Gene, Versatile, iProc, Altera, Rockchip, MediaTek, VMD, Loongson, HiSilicon error, Apple, MT7621, and Aspeed. It always descends into `dwc/`, `mobiveil/`, and `plda/`, whose own Makefiles/Kconfigs gate contents. ACPI+quirk ARM64 blocks force-build Thunder/X-Gene quirk providers for generic ACPI roots without explicit controller options.

Control flow/state: no runtime state; build state controls which controller drivers and shared object modules are linked. Multi-object host/EP combinations such as R-Car are assembled by listing common plus mode-specific objects.

Dependencies/integration: consumes symbols from `controller/Kconfig`, Cadence/DWC/Mobiveil/PLDA submenus, ACPI, PCI quirks, and ARM64. Risks include object duplication when both normal and ACPI quirk paths select a file, missing shared object members for composite drivers, and always-descended subdirectories relying on internal guards. Test signals are per-controller build targets, allmodconfig link checks, and ACPI quirk coverage on ARM64.
