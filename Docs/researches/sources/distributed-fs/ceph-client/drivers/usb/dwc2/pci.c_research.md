# sources/distributed-fs/ceph-client/drivers/usb/dwc2/pci.c

## Purpose
`pci.c` is a PCI glue driver for DWC2. It binds supported PCI IDs, enables the PCI device, registers a generic USB PHY, creates a child platform device named `dwc2` with MMIO and IRQ resources, and lets the main DWC2 platform driver handle the actual controller.

## Important APIs, Types, And Functions
- Driver name: `dwc2-pci`.
- Glue state: `struct dwc2_pci_glue` stores the child DWC2 platform device and generic PHY platform device.
- Probe: `dwc2_pci_probe()` enables PCI, sets bus mastering, registers generic PHY, allocates and populates the `dwc2` platform device, attaches BAR0 and IRQ resources, and stores glue state with `pci_set_drvdata()`.
- Remove: `dwc2_pci_remove()` unregisters the child platform device and generic PHY.
- Module registration: `module_pci_driver(dwc2_pci_driver)` uses `dwc2_pci_ids` from `params.c`.

## Control Flow
When a supported PCI device appears, `pcim_enable_device()` enables it and managed PCI cleanup is established. The driver marks the device bus-master capable, registers a generic USB PHY, allocates a platform device, creates two resources from BAR0 and `pci->irq`, assigns the PCI device as parent, adds resources, adds the platform device, then stores the glue. On any failure after PHY registration, it unregisters the PHY and drops the platform device reference. Removal reverses successful probe by unregistering the platform child and PHY.

## State And Persistence Behavior
The only persistent runtime state is `struct dwc2_pci_glue` allocated with devm memory and referenced as PCI driver data. Hardware resource state is managed by PCI core, the generic PHY registration, and the child platform device. There is no file persistence.

## Dependencies And Integration Points
This file depends on `dwc2_pci_ids` exported by `params.c`, Linux PCI APIs, platform device APIs, and `usb_phy_generic_register()`. Its main integration point is `platform.c`: the child device name `dwc2` must match the platform driver, and its parent remains the PCI device so `dwc2_init_params()` can find PCI match data through `to_pci_dev(hsotg->dev->parent)`.

## Risks
- Error unwinding must avoid unregistering or putting invalid platform device pointers. The current `err` path handles both after allocation attempts, but future edits must keep order precise.
- The child platform device receives only BAR0 and one IRQ. Multi-resource variants would need explicit support.
- The code registers a generic PHY unconditionally for PCI devices. Platforms needing a more specific PHY model may require different glue.
- Parent-child relationship is semantically important for parameter matching and DMA/resource behavior.

## Test Signals
- Build with `CONFIG_USB_DWC2_PCI` and supported PCI IDs.
- Probe on Synopsys HAPS, STMicro, or Loongson DWC2 PCI devices and verify the child `dwc2` platform driver binds.
- Remove/unbind the PCI driver and check that the child platform device and generic PHY unregister cleanly.
- Validate BAR0 MMIO mapping and IRQ delivery through successful platform probe and host/gadget operation.
