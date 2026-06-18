# sources/distributed-fs/ceph-client/drivers/scsi/fnic/Makefile

## Purpose

`fnic/Makefile` defines Kbuild composition for the Cisco FNIC FCoE HBA driver. When `CONFIG_FCOE_FNIC` is enabled, Kbuild builds `fnic.o` from the listed FNIC, FDLS/FIP, vNIC, tracing, debugfs, and PCI subsystem ID objects.

## Important APIs, types, and functions

`obj-$(CONFIG_FCOE_FNIC) += fnic.o` gates the driver on configuration. `fnic-y` lists `fip.o`, `fnic_attrs.o`, `fnic_isr.o`, `fnic_main.o`, `fnic_res.o`, `fnic_fcs.o`, `fdls_disc.o`, `fnic_scsi.o`, `fnic_trace.o`, `fnic_debugfs.o`, `vnic_cq.o`, `vnic_dev.o`, `vnic_intr.o`, `vnic_rq.o`, `vnic_wq_copy.o`, `vnic_wq.o`, and `fnic_pci_subsys_devid.o`.

## Control flow

There is no runtime flow. Kbuild reads this file to link component objects into the final driver.

## State and persistence behavior

No runtime state is defined. Build output depends on `CONFIG_FCOE_FNIC` and the object list.

## Dependencies and integration points

The file integrates the FNIC directory into kernel Kbuild and links Cisco vNIC queue/device/interrupt support with FNIC SCSI, FIP/FDLS, tracing, and debugfs code.

## Risks and edge cases

Omitting an object can produce unresolved symbols or missing functionality. Object order can matter for linker-section behavior. The compact continuation style should remain Kbuild-compatible.

## Test signals

Build with `CONFIG_FCOE_FNIC=m` and `=y`, run modpost, and verify all listed objects compile and link.
