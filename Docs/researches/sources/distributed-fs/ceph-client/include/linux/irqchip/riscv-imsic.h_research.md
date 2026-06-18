# sources/distributed-fs/ceph-client/include/linux/irqchip/riscv-imsic.h

## Purpose
`riscv-imsic.h` defines the RISC-V Incoming MSI Controller register IDs, MMIO page layout, global/local configuration structures, and ACPI/firmware helper declarations.

## Important APIs, types, and functions
It defines IMSIC MMIO constants, interrupt ID ranges, CSR register numbers for delivery/threshold/pending/enable arrays, `struct imsic_local_config`, `struct imsic_global_config`, `imsic_get_global_config`, `imsic_platform_acpi_probe`, and `imsic_acpi_get_fwnode` stubs.

## Control flow
Firmware/probe code fills global target-address geometry and per-CPU MSI addresses. APLIC/MSI code queries `imsic_get_global_config` to generate MSI addresses and interrupt IDs. ACPI helpers provide fwnodes when both ACPI and IMSIC are enabled.

## State and persistence
State is runtime controller configuration: base address, guest/hart/group index widths, number of IDs and guest files, and per-CPU MSI physical/virtual addresses.

## Dependencies and integration points
It depends on devices, fwnodes, bitops, and RISC-V IMSIC config. It integrates APLIC MSI mode, irqdomains, ACPI probing, and per-CPU interrupt files.

## Risks and test signals
Risks include invalid address-geometry fields, ID range overflow, missing per-CPU local config, disabled-config NULL global config, and ACPI fwnode mismatch. Tests should cover DT and ACPI systems, per-CPU MSI delivery, guest interrupt files, boundary IDs, and disabled IMSIC builds.
