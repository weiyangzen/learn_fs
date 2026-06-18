# sources/distributed-fs/ceph-client/drivers/iommu/riscv/iommu-pci.c

## Purpose
This file binds RISC-V IOMMU hardware exposed as a PCI function. It performs PCI resource setup, MSI vector allocation, capability validation, and delegates common initialization/removal/shutdown to the shared RISC-V IOMMU core.

## Important APIs, Types, And Functions
`riscv_iommu_pci_probe()` enables the PCI device, validates BAR0 memory size, maps BAR0, allocates `struct riscv_iommu_device`, reads `CAPABILITIES` and `FCTL`, verifies MSI-capable interrupt generation, allocates MSI/MSI-X vectors, records Linux IRQ numbers, clears `FCTL.WSI` to select message-signaled mode, and calls `riscv_iommu_init()`. `riscv_iommu_pci_remove()` calls `riscv_iommu_remove()`. `riscv_iommu_pci_shutdown()` calls `riscv_iommu_disable()`. The PCI ID table includes QEMU Red Hat and Rivos device IDs.

## Control Flow
Probe is strictly staged: PCI enable, BAR validation/mapping, core struct allocation, capability read, interrupt-mode validation, vector allocation, FCTL programming, common core initialization. Remove unregisters and disables through shared core paths; shutdown performs best-effort translation disable without full teardown.

## State And Persistence
Per-device state is a `struct riscv_iommu_device` stored in PCI device drvdata. Register mappings are pcim-managed. IRQ vectors are allocated by PCI MSI APIs and stored in `iommu->irqs`.

## Dependencies And Integration Points
The file depends on PCI managed resource APIs, MSI APIs, RISC-V IOMMU bit definitions, and shared functions in `iommu.c`. It is built only when `CONFIG_RISCV_IOMMU_PCI` is true.

## Risks
The PCI path requires MSI or MSI-X; hardware exposing only WSI is rejected. It assumes BAR0 contains the complete RISC-V IOMMU register window. Interrupt count may be fewer than architectural causes, so core vector remapping must be correct. Shutdown only disables translation/queues and does not wait for all hardware state to quiesce.

## Test Signals
QEMU RISC-V IOMMU PCI probe, Rivos hardware probe, MSI and MSI-X vector allocation variants, BAR length failure tests, removal/unbind, and kexec/shutdown checks that translation is disabled.
