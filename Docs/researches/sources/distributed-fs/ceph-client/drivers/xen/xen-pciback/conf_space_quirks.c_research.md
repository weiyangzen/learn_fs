# sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/conf_space_quirks.c

## Purpose
`conf_space_quirks.c` manages dynamically registered pciback configuration-space quirks for devices needing additional writable or overridden fields.

## Important APIs, types, and functions
It defines global `xen_pcibk_quirks`, match helper `match_one_device`, lookup `xen_pcibk_find_quirk`, duplicate check `xen_pcibk_field_is_dup`, `xen_pcibk_config_quirks_add_field`, `xen_pcibk_config_quirks_init`, `xen_pcibk_config_field_free`, and `xen_pcibk_config_quirk_release`.

## Control flow
Per-device quirk initialization allocates a quirk descriptor containing the device's IDs and adds it to the global quirk list. Adding a quirk field fills default read/write callbacks according to field size and delegates to the config-space dispatcher. Release finds the matching quirk by PCI IDs, removes it from the list, and frees it.

## State and persistence
State is the global in-memory quirk list and any dynamically allocated config fields attached to devices. There is no durable persistence.

## Dependencies and integration points
It depends on Linux PCI ID matching, pciback device data, `conf_space.h`, and the shared `xen_pcibk_quirks` declaration in `pciback.h`. It integrates with sysfs or other pciback paths that add per-device quirk fields.

## Risks and test signals
Risks include broad ID matching removing the wrong quirk, duplicate field suppression hiding intended overrides, dynamic field cleanup, unsupported field sizes, and global list concurrency assumptions. Test signals include adding and removing quirks for multiple devices, duplicate offsets, byte/word/dword fields, release after device removal, and config reads/writes through dynamic fields.
