# sources/distributed-fs/ceph-client/drivers/firmware/iscsi_ibft.c

Purpose: Parses the iSCSI Boot Firmware Table and exposes boot initiator, NIC, target, and ACPI table metadata through the iSCSI boot sysfs infrastructure.

Important APIs/types/functions: Packed table structs model iBFT control, initiator, NIC, and target records. Show/check callbacks include `ibft_attr_show_initiator()`, `ibft_attr_show_nic()`, `ibft_attr_show_target()`, `ibft_attr_show_acpitbl()`, and corresponding `ibft_check_*_for()` mode filters. `ibft_register_kobjects()` scans control offsets and creates iscsi boot kobjects.

Control flow: Module init finds the table via legacy ISA reservation or ACPI signatures, validates revision and checksum, creates an `iscsi_boot_kset`, scans control offsets, validates each supported record, creates initiator/NIC/target kobjects, and adds a NIC-to-PCI device sysfs link when possible. Exit removes NIC links and destroys the kset.

State and persistence behavior: Global `ibft_addr` points to firmware/ACPI table memory and `boot_kset` owns sysfs objects. The driver reads firmware boot configuration only; no persistent writes.

Dependencies and integration points: Depends on ACPI, optional legacy finder, PCI, iscsi_boot_sysfs, and network/iSCSI boot conventions. It consumes `ibft_phys_addr` exported by `iscsi_ibft_find.c` when enabled.

Risks and test signals: String offsets and lengths are firmware-controlled and need the existing table bounds checks to remain effective. CHAP secrets are exposed if present by design, so sysfs permissions matter. Test ACPI and legacy discovery, checksum failure, invalid control offsets, IPv4-mapped and IPv6 address formatting, PCI link creation, and teardown.
