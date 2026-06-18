# sources/distributed-fs/ceph-client/drivers/scsi/fdomain_pci.c

## Purpose

`fdomain_pci.c` is the PCI wrapper for Future Domain TMC-3260/TMC-36C70 adapters. It matches the Future Domain PCI device ID, enables the device, reserves regions, validates BAR0, creates the shared `fdomain` SCSI host using BAR0 and PCI IRQ, and releases resources on remove.

## Important APIs, types, and functions

The key functions are `fdomain_pci_probe()` and `fdomain_pci_remove()`. `fdomain_pci_table[]` matches `PCI_VENDOR_ID_FD`/`PCI_DEVICE_ID_FD_36C70`. `fdomain_pci_driver` is registered through `module_pci_driver()` and uses shared `FDOMAIN_PM_OPS`.

## Control flow

Probe enables the PCI device, requests PCI regions, rejects zero-length BAR0, calls `fdomain_create(pci_resource_start(pdev, 0), pdev->irq, 7, &pdev->dev)`, and stores the returned host in drvdata. Failure unwinds regions and device enablement. Remove destroys the host, releases regions, and disables the PCI device.

## State and persistence behavior

The wrapper stores only the SCSI host pointer in PCI drvdata. PCI enablement and resource reservations last while bound; command/IRQ state is in the shared core.

## Dependencies and integration points

The file depends on Linux PCI core and `fdomain.h`. All SCSI protocol behavior is delegated to `fdomain.c`.

## Risks and edge cases

The wrapper assumes BAR0 is suitable for port I/O and validates only nonzero length. It intentionally does not call `pci_set_master()` because the core is PIO. Resource ownership must remain split between wrapper-owned PCI regions and core-owned IRQ/host state.

## Test signals

Compile with PCI support, bind/unbind a matching device, test BAR0 failure cleanup, verify IRQ behavior through the core, and exercise suspend/resume.
