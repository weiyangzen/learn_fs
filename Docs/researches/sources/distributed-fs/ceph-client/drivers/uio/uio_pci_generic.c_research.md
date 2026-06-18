# sources/distributed-fs/ceph-client/drivers/uio/uio_pci_generic.c

## Purpose
`uio_pci_generic.c` is a dynamic-ID generic UIO driver for PCI 2.3 and PCIe devices. It exposes memory BARs to userspace and uses the PCI interrupt disable bit to safely mask INTx interrupts after each event.

## Important APIs, Types, And Functions
- `struct uio_pci_generic_dev` embeds `struct uio_info` and stores the bound `struct pci_dev`.
- `release()` calls `pci_clear_master()` when the UIO fd is closed.
- `irqhandler()` calls `pci_check_and_mask_intx()` and returns `IRQ_HANDLED` only for this device.
- `probe()` uses `pcim_enable_device()`, validates `pci_intx_mask_supported()`, fills memory maps from `pdev->resource[]`, and registers with `devm_uio_register_device()`.
- `uio_pci_driver.id_table = NULL` means users must add IDs through sysfs `new_id`.

## Control Flow
Userspace or admin policy adds a PCI vendor/device ID to the driver. Probe enables the device through managed PCI helpers, refuses interrupt-capable devices without INTx masking support, allocates driver state, sets UIO open/release and optional IRQ handler fields, and scans resources for memory BARs exactly matching `IORESOURCE_SIZEALIGN | IORESOURCE_MEM`. Each mapped BAR is page-aligned with `addr`, `offs`, and rounded `size`. On an interrupt, the handler masks INTx and lets the UIO core wake userspace.

## State And Persistence Behavior
The driver maintains no hardware-specific state beyond UIO memory descriptions, IRQ metadata, and the `pdev` pointer. On close, bus mastering is cleared to reduce lingering DMA exposure. Dynamic IDs remain in driver sysfs state only for the loaded module lifetime unless external policy recreates them.

## Dependencies And Integration Points
It depends on PCI core managed device enablement, UIO core, PCI resource tables, and INTx mask support. It is commonly integrated by unbinding a kernel driver and binding this UIO driver so userspace can implement device logic.

## Risks And Edge Cases
The header comment explicitly notes DMA insecurity: userspace BAR access plus bus mastering can compromise memory if no IOMMU or isolation exists. The resource flag equality check is strict and can skip resources with additional flags. MSI/MSI-X are not supported here. Devices with no IRQ still bind with a warning, leaving polling-only userspace. Clearing bus master on release can wedge some devices until reset.

## Test Signals
Add a dynamic ID, bind a PCIe device with memory BARs, and verify UIO maps expose page offsets correctly. Trigger INTx and confirm interrupts are masked until userspace reenables them through PCI config or device handling. Close the UIO fd and verify bus mastering clears. Exercise no-IRQ devices to confirm polling mode registration.
