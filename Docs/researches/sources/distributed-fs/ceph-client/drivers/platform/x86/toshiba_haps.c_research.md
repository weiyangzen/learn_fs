# sources/distributed-fs/ceph-client/drivers/platform/x86/toshiba_haps.c

Purpose: Implements Toshiba HDD Active Protection Sensor support for ACPI device `TOS620A`. It sets a default disk protection sensitivity, exposes sysfs controls for protection level and reset, sends ACPI netlink events for firmware notifications, and disables/re-enables protection around suspend/resume.

Important APIs and types: `struct toshiba_haps_dev` stores the ACPI companion and cached `protection_level`. The singleton pointer `toshiba_haps` prevents multiple active devices. Firmware methods are `_STA` for availability, `PTLV` for protection level, and `RSSS` for reset. Sysfs attributes are `protection_level` and write-only `reset_protection`, grouped in `haps_attr_group`. PM hooks are `toshiba_haps_suspend` and `toshiba_haps_resume`.

Control flow: Probe rejects a second device, checks `_STA` because systems without HDDs or with SSD-only configurations may report unavailable, allocates managed state, sets default protection level 2 (medium) with `PTLV`, creates the sysfs group on the ACPI device, installs an ACPI notify handler, and assigns the singleton. `protection_level_store` accepts only 0 through 3 and writes `PTLV`; `reset_protection_store` accepts only value 1 and calls `RSSS`. Notify logs the event and forwards it through `acpi_bus_generate_netlink_event`. Suspend writes level 0 to disable protection; resume restores the cached level and resets the interface.

State and persistence: The selected protection level is cached in memory and restored after resume, but firmware owns the active disk-protection behavior. The singleton pointer is cleared on remove, while state allocation is devm-managed. Reset commands are transient. The default level is medium unless userspace changes it.

Dependencies and integration points: Depends on ACPI platform matching, sysfs attribute groups, ACPI notify/netlink, PM sleep callbacks, and platform-device drvdata. User-visible integration is under the ACPI device sysfs directory, with `protection_level` and `reset_protection`.

Risks: `_STA` failure is treated as unavailable because SSD-only machines can make the call fail; this avoids false-positive probing but hides detailed firmware errors. Resume overwrites the first `PTLV` return with the later `RSSS` return, so a failed protection-level restore followed by successful reset would be reported as success. Sysfs `show` uses cached protection level, not a firmware readback. Suspend disables protection, which is correct for power management but relies on resume completing successfully.

Test signals: Probe on `TOS620A` systems with HDD protection and on SSD-only systems; sysfs write validation for levels -1, 0-3, and 4; reset accepts only `1`; ACPI notifications produce netlink events; suspend sets level 0 and resume restores cached level plus reset; remove deletes sysfs and notify handler and clears singleton.
