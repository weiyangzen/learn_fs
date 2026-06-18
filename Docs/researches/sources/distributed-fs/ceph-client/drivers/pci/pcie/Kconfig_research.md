<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/Kconfig

## Purpose
This Kconfig file defines the PCI Express port bus and optional PCIe services built on top of it. It controls whether Linux exposes native PCIe port services such as hotplug, Advanced Error Reporting, error injection, ECRC policy control, ASPM, PME, Downstream Port Containment, Precision Time Measurement, and ACPI Error Disconnect Recover.

## Important APIs, Types, and Functions
There is no C API here, but the configuration symbols directly shape compilation and runtime behavior: `PCIEPORTBUS`, `HOTPLUG_PCI_PCIE`, `PCIEAER`, `PCIEAER_INJECT`, `PCIE_ECRC`, `PCIEASPM`, ASPM policy choices, `PCIE_PME`, `PCIE_DPC`, `PCIE_PTM`, and `PCIE_EDR`. Dependencies express service layering: AER depends on the port bus and selects RAS; AER injection depends on AER and selects generic IRQ injection; DPC depends on both port bus and AER; EDR depends on DPC and ACPI.

## Control Flow and State
The selected symbols determine which `pcie/*.c` objects are built and which inline stubs from `pci.h` are active. ASPM policy choice controls the initial `aspm_policy` compiled into `aspm.c`: BIOS default, performance, powersave, or powersupersave. `PCIE_PME` is a derived boolean enabled when `PCIEPORTBUS && PM` are true, so native PME service follows PM support.

## Dependencies and Integration Points
`PCIEPORTBUS` is the base service bus consumed by `portdrv.c` and `portdrv.h`. USB4 defaults pull in port bus and native hotplug because tunneled PCIe requires hotplug handling. AER integrates with RAS logging, DPC, EDR, CXL RAS, and PCI error recovery. ASPM integrates with power management and sysfs policy. PTM support backs endpoint and controller drivers that request timing support.

## Risks and Test Signals
Configuration risks include enabling a service without its required native control path, unexpected default behavior on USB4 systems, and build regressions under rare combinations such as `PCIEPORTBUS=n`, `PCIEASPM=y`, or `PCIE_DPC=y`. Test signals are randconfig/allmodconfig builds, boot tests verifying service registration, sysfs visibility for ASPM and AER, and runtime checks that disabled options compile to correct stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/Kconfig -->
