# sources/distributed-fs/ceph-client/drivers/iommu/riscv/iommu-platform.c

## Purpose
This file binds RISC-V IOMMU hardware exposed as a platform device through DT or ACPI. It maps registers, chooses MSI or wired-signaled interrupt delivery, programs MSI configuration table entries, and delegates common initialization to `iommu.c`.

## Important APIs, Types, And Functions
`riscv_iommu_write_msi_msg()` is the platform-MSI message writer; it masks MSI address bits to the hardware-supported field, writes address/data/control table entries, and unmasks the entry. `riscv_iommu_platform_probe()` allocates `struct riscv_iommu_device`, maps the register resource, reads capabilities/FCTL, selects interrupt mode from `CAPABILITIES.IGS`, configures OF or ACPI/IMSIC MSI domains, allocates platform MSI IRQs when possible, falls back to WSI if supported, sets or clears `FCTL.WSI`, and calls `riscv_iommu_init()`. Remove frees MSI IRQs when MSI mode was used after `riscv_iommu_remove()`. Shutdown calls `riscv_iommu_disable()`.

## Control Flow
Probe first determines the hardware interrupt-generation capability. For MSI or both, it attempts MSI-domain setup and vector allocation. If MSI fails and hardware supports only MSI, probe fails. If hardware supports both, it falls through to WSI setup. WSI setup counts platform IRQ resources, caps the count at the architectural interrupt count, records IRQs, and sets `FCTL.WSI`. The shared core then allocates queues, enables queues, configures the device directory, and registers with the IOMMU core.

## State And Persistence
State is stored in `struct riscv_iommu_device` in platform drvdata. MSI mode also creates platform MSI IRQ allocations and hardware MSI table entries. FCTL interrupt-mode state persists until remove or shutdown.

## Dependencies And Integration Points
The file integrates with OF platform probing, ACPI ID `RSCV0004`, IMSIC ACPI fwnode lookup, generic MSI domains, platform MSI allocation, and the shared RISC-V IOMMU core.

## Risks
MSI address truncation is warned but still programmed with a masked address, so platforms must ensure deliverable MSI addresses. ACPI MSI setup depends on IMSIC fwnode discovery. WSI fallback requires usable platform IRQ resources. Remove decides whether to free MSI IRQs from the post-init FCTL WSI bit, so FCTL state must reflect the selected mode.

## Test Signals
DT platform probe with MSI, ACPI platform probe with IMSIC MSI, forced MSI allocation failure with WSI fallback, WSI-only hardware, remove-time MSI free, and shutdown/kexec disable behavior.
