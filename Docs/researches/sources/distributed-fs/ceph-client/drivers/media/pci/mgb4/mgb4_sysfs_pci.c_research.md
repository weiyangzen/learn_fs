# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_sysfs_pci.c

- Purpose: PCI-device sysfs attributes exposing module type/version, firmware type/version, and serial number.
- Important APIs/types/functions: Show handlers for `module_version`, `module_type`, `fw_version`, `fw_type`, `serial_number`; `mgb4_pci_attrs`.
- Control flow: Handlers read `mgbdev` from device driver data and return cached module/serial values or video register 0xC4 fields.
- State and persistence: Serial number is read once from MTD by core; firmware/module fields reflect detected hardware or live FPGA register.
- Dependencies and integration points: Added by `mgb4_core.c` to the PCI device.
- Risks: If no module is present, values may remain zero/unknown but attributes still exist. Serial formatting assumes a four-byte packed decimal-ish value.
- Test signals: Read sysfs files after probe, no-module mode, and failed serial MTD read.
