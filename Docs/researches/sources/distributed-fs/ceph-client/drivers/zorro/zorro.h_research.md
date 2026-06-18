<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/zorro.h -->
# sources/distributed-fs/ceph-client/drivers/zorro/zorro.h

## Purpose
`zorro.h` is the private Zorro bus header shared by the bus core, driver core, sysfs, and names code.

## Important APIs, types, and functions
It declares `zorro_bus_type`, `zorro_name_device`, and `zorro_device_attribute_groups`. When `CONFIG_ZORRO_NAMES` is disabled, `zorro_name_device` is an inline no-op.

## Control flow
No executable flow beyond the inline no-op. Including files use the declarations during bus registration and enumeration.

## State and persistence
No state is defined.

## Dependencies and integration points
It ties conditional name support and sysfs attribute groups to the rest of `drivers/zorro`.

## Risks and test signals
Risks are declaration/config mismatches. Test signals are compile-only across `CONFIG_ZORRO_NAMES` and sysfs-enabled device registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/zorro.h -->
