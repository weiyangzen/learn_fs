# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_pci_subsys_devid.c

Purpose: this file maps Cisco PCI subsystem device IDs to human-readable adapter family and model strings. It is used during probe to log the adapter model and populate the FDMI model description stored in `fnic->subsys_desc`.

Important APIs and data: `fnic_pcie_device_table[]` is a static table of `{device, desc, subsystem_device, subsys_desc}` records covering Sereno, Cruz, Bodega, and Beverly generations and many VIC model names. `fnic_get_desc_by_devid(struct pci_dev *pdev, char **desc, char **subsys_desc)` is the only function; it validates the PCI device ID and searches by subsystem device.

Control flow: `fnic_probe()` calls `fnic_get_desc_by_devid()` before enabling the PCI device. The helper rejects non-`PCI_DEVICE_ID_CISCO_VIC_FC` device IDs, walks until the sentinel `{0,}`, compares `pdev->subsystem_device` against table entries, and returns model strings on success or `1` with null outputs on failure.

State and persistence: the mapping is compile-time static state. Probe copies the selected `subsys_desc` into `fnic->subsys_desc` with length clamping for later FDMI reporting. There is no runtime mutation or persistence.

Dependencies and integration: the file includes `fnic.h` for PCI ID constants and `struct fnic_pcie_device`. The output feeds logging and fabric device-management identity rather than queue operation.

Risks: the search ignores table `device` after checking the top-level PCI device, so if multiple Cisco FC device IDs ever share subsystem IDs this helper would need extension. It uses `memcmp()` on little-endian in-memory `unsigned short` subsystem IDs instead of direct comparison; this works for equal host values but is unnecessarily indirect. Unknown models fall back cleanly. Test signals include probing every supported subsystem ID, unknown subsystem ID logging, FDMI model string length clamping, and ensuring newly added IDs are reflected in the table.
