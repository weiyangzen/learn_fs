# sources/distributed-fs/ceph-client/drivers/rapidio/rio-sysfs.c

## Purpose
Provides RapidIO bus, device, and mport sysfs exposure. It publishes identity/topology attributes, a binary config-space accessor, a bus-level scan trigger, and master-port attributes.

## Important APIs, types, and functions
The `rio_config_attr()` macro defines read-only device attributes for DID/VID/revision/assembly/destID/hopcount fields. `routes_show()`, `lprev_show()`, and `lnext_show()` expose switch route cache and topology links. `modalias_show()` emits RapidIO modalias strings for driver matching. `rio_read_config()` and `rio_write_config()` implement the `config` bin_attribute using aligned 8/16/32-bit RapidIO config accesses. `scan_store()` parses a bus attribute write and calls `rio_init_mports()` or `rio_mport_scan()`. Exported arrays `rio_dev_groups`, `rio_bus_groups`, and `rio_mport_groups` plug into the RapidIO device model.

## Control flow
When a RapidIO device is registered, its attribute group is attached. `rio_dev_is_attr_visible()` hides switch-only attributes from endpoints. Config reads cap non-admin callers at 0x100 bytes because some chips lock up on undefined maintenance-space reads; CAP_SYS_ADMIN may read the full `RIO_MAINT_SPACE_SZ`. Both read and write paths trim requests to maintenance-space limits, consume unaligned leading bytes, then handle aligned words, tails, and return the adjusted byte count. Writing the bus `scan` attribute with `-1` scans all mports; otherwise a validated mport number scans one port.

## State and persistence
The sysfs files are views over live `struct rio_dev` and `struct rio_mport` state plus hardware config space. Writes to the `config` bin file persist only in target device CSRs/registers; this file keeps no private persistent state.

## Dependencies and integration
Depends on Linux sysfs/device APIs, capability checks, RapidIO object conversion helpers, and core scan functions declared in `rio.h`. The config bin attribute depends on mport-specific maintenance read/write methods underneath `rio_read_config_*` and `rio_write_config_*`.

## Risks
Config writes are privileged only by sysfs mode (`S_IWUSR`) and can change hardware state broadly. The route/topology text attributes assume `rdev->rswitch` and route cache validity when visible. `sprintf()` is used for attribute formatting, so unusually large route output relies on sysfs buffer size constraints rather than explicit bounds.

## Test signals
Check endpoint versus switch visibility, modalias content, admin/non-admin config read size behavior, unaligned config reads and writes, out-of-range scan requests, successful scan return count semantics, and mport `port_destid`/`sys_size` output after enumeration and discovery.
