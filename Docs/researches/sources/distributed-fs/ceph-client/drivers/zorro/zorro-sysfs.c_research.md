<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/zorro-sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/zorro/zorro-sysfs.c

## Purpose
`zorro-sysfs.c` exposes Zorro device configuration through sysfs attributes and a binary `config` file.

## Important APIs, types, and functions
It defines readonly attributes `id`, `type`, `serial`, `slotaddr`, `slotsize`, `resource`, and `modalias`, plus binary attribute `config`. The exported group array is `zorro_device_attribute_groups`.

## Control flow
The Zorro bus type attaches these groups to each registered device. Attribute reads format fields from `struct zorro_dev`; binary config reads construct a `struct ConfigDev` and return bytes via `memory_read_from_buffer`.

## State and persistence
No independent state. Sysfs exposes current boot-discovered `zorro_dev` fields.

## Dependencies and integration points
It depends on driver core attributes, endian helpers, Amiga `ConfigDev`, and Zorro resource helpers. It integrates with udev and module matching through `modalias`.

## Risks and test signals
Risks include endian mismatches, resource formatting errors, and binary config offset handling. Test signals include sysfs attribute reads, modalias matching, serial byte order, and partial reads of `config`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/zorro-sysfs.c -->
