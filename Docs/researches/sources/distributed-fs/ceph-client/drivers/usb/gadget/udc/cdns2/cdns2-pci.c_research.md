# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/cdns2/cdns2-pci.c

## Purpose

`cdns2-pci.c` is the PCI glue layer for the Cadence CDNS2 USBHS device controller. It discovers a Cadence PCI USB device-function, maps BAR0, fills platform-specific fields in `struct cdns2_device`, delegates controller setup to the CDNS2 gadget core, and wires system sleep callbacks to gadget suspend/resume.

## Important APIs And Functions

`cdns2_pci_probe()` validates function/class, enables the PCI device with managed PCI helpers, sets bus mastering, allocates `struct cdns2_device`, requests and maps BAR0, stores the IRQ, hard-codes the supported endpoint bitmap and on-chip buffer sizes, then calls `cdns2_gadget_init(priv_dev)`. On success it stores private data, enables wakeup, and adjusts runtime PM usage if the device can run-wake.

`cdns2_pci_remove()` handles runtime wake reference restoration and calls `cdns2_gadget_remove()`. `cdns2_pci_suspend()` and `cdns2_pci_resume()` delegate to `cdns2_gadget_suspend()` and `cdns2_gadget_resume(priv_dev, 1)`. The PCI match table binds Cadence vendor/device IDs with USB device class, and `module_pci_driver()` registers the driver.

## Control Flow And State

Probe is linear and mostly devm-managed. It refuses unexpected PCI functions/classes before touching hardware. After `pcim_enable_device()` and `pci_set_master()`, all durable state for the CDNS2 gadget implementation is stored in the allocated `struct cdns2_device`: `regs`, `irq`, `dev`, `eps_supported`, `onchip_tx_buf`, and `onchip_rx_buf`. The real UDC state machine starts only after `cdns2_gadget_init()`.

Removal does not manually unmap BARs or free memory because those are managed by devres/pcim. Runtime/system power state is shallow in this file; controller-specific sequencing is delegated to the gadget layer.

## Dependencies And Integration Points

The file depends on Linux PCI, PM runtime, devres, and the private CDNS2 gadget header. It integrates with module autoloading through `MODULE_DEVICE_TABLE(pci, cdns2_pci_ids)` and `MODULE_ALIAS("pci:cdns2")`.

## Risks

The endpoint support and on-chip buffer sizing are hard-coded. If future Cadence PCI variants expose different endpoint counts or buffers, this glue could over-advertise or under-utilize hardware. The class check is strict. The driver assumes `pdev->irq` is valid and that BAR0 contains the expected full CDNS2 register aperture.

## Test Signals

Positive signals are successful PCI bind, BAR0 mapping, `cdns2_gadget_init()` success, UDC appearance under `/sys/class/udc`, and gadget enumeration after binding a gadget function. Suspend/resume tests should confirm endpoint and EP0 state restoration. Wake tests should verify runtime PM references are balanced.
