<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/elan-i2c-ids.h -->
# sources/distributed-fs/ceph-client/include/linux/input/elan-i2c-ids.h

Purpose: Provides the ACPI device-id whitelist shared by Elan I2C/SMBus touchpad drivers.

Important APIs/types/functions: Static `elan_acpi_id[]` lists supported ACPI HID strings from `ELAN0000`, `ELAN0100`, many `ELAN06xx` devices, and `ELAN1000`, terminated by an empty entry. One known-bad `ELAN061B` entry is intentionally commented out.

Control flow: Driver ACPI matching uses the table to bind supported touchpads.

State/persistence: The match table is static const metadata and may be exported through module device tables by users.

Dependencies/integration: Depends on `linux/mod_devicetable.h` and ACPI/I2C input driver matching.

Risks: Adding/removing ids changes hardware binding; known-bad ids should remain excluded unless validated.

Test signals: ACPI modalias matching, affected laptop probe, non-matching device rejection, and module autoload behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/elan-i2c-ids.h -->
