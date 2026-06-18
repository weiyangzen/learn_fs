# sources/distributed-fs/ceph-client/include/linux/iscsi_boot_sysfs.h

## Purpose
`iscsi_boot_sysfs.h` defines the common sysfs object model for exporting firmware-discovered iSCSI boot information, including Ethernet, target, initiator, and ACPI table attributes.

## Important APIs, types, and functions
It defines property enums for Ethernet, target, initiator, and ACPI table attributes; `struct iscsi_boot_kobj` with kobject, attribute group, driver data, show/visibility/release callbacks; `struct iscsi_boot_kset`; and create/destroy APIs for ksets and per-object kobjects.

## Control flow
Low-level firmware/table parsers create a boot kset, create indexed Ethernet/target/initiator/ACPI kobjects with callbacks, expose readable attributes depending on `is_visible`, and destroy the kset on teardown. Release callbacks free driver-specific data when the kobject is released.

## State and persistence
State is runtime sysfs kobjects/ksets plus driver-owned parsed boot data. The exported values originate from firmware and are not modified persistently by this API.

## Dependencies and integration points
It integrates with the kernel kobject/sysfs model, iBFT and other boot-firmware parsers, SCSI/iSCSI boot consumers, and host-number-specific sysfs trees.

## Risks and test signals
Risks include kobject lifetime leaks, exposing secrets such as CHAP keys with wrong permissions, callback type mismatches, and destroy while sysfs files are open. Tests should cover attribute visibility, release callback execution, multiple NIC/target entries, host kset naming, and secret permission policy.
