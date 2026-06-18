# sources/distributed-fs/ceph-client/drivers/pci/pci-pf-stub.c

## Purpose
Implements a minimal whitelist PCI driver for SR-IOV physical functions that need SR-IOV support but no functional device driver. It claims selected PF devices and delegates SR-IOV configuration to the simple PCI core helper.

## APIs, Types, And Functions
Defines `pci_pf_stub_whitelist`, `pci_pf_stub_probe()`, and `pf_stub_driver`. The driver table currently includes Amazon vendor device `0x0053`, exports a PCI module device table, and uses `pci_sriov_configure_simple` as `.sriov_configure`.

## Control Flow
Module PCI driver registration binds only devices in the whitelist. Probe logs that the device is claimed and returns success. SR-IOV sysfs configuration is handled by the generic simple helper.

## State And Persistence
No private state is allocated. Binding state is maintained by the PCI driver core and SR-IOV state by generic PCI infrastructure.

## Dependencies And Integration
Depends on the PCI module-driver framework and SR-IOV core helper. It integrates with sysfs SR-IOV controls for whitelisted PFs.

## Risks And Test Signals
Risks are limited but include accidental binding to an ID that later needs a real driver, missing IDs, and SR-IOV helper behavior changes. Test signals include module autoload/match table behavior, PF binding, `sriov_numvfs` enable/disable, and unbind/rebind.
