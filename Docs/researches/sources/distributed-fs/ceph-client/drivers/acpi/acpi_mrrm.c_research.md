# sources/distributed-fs/ceph-client/drivers/acpi/acpi_mrrm.c

## Purpose
`acpi_mrrm.c` parses the ACPI Memory Range and Region Mapping table and reports boot memory ranges, NUMA node association, and local/remote region IDs through sysfs.

## Important APIs, Types, And Functions
The exported helper is `acpi_mrrm_max_mem_region()`. Main state includes `max_mem_region`, `struct mrrm_mem_range_entry`, `mrrm_mem_range_entry`, and `mrrm_mem_entry_num`. Key functions are `get_node_num()`, `acpi_parse_mrrm()`, generated `RANGE_ATTR()` sysfs readers, `add_boot_memory_ranges()`, and `mrrm_init()`.

## Control Flow
`mrrm_init()` parses `ACPI_SIG_MRRM`. The parser rejects unsupported revisions and OS-assigned region mode, counts memory range entries, allocates internal entries, copies base/length, resolves the NUMA node by checking online populated zones for intersection, records valid local/remote region IDs or `-1`, and updates `max_mem_region`. Sysfs setup creates `/sys/firmware/acpi/memory_ranges/rangeN` kobjects with `base`, `length`, `node`, `local_region_id`, and `remote_region_id` attributes.

## State And Persistence
Parsed MRRM data is retained in memory and exposed through sysfs for the running boot. `max_mem_region` defaults to one region if parsing is absent or fails.

## Dependencies And Integration Points
It depends on ACPI table parsing, sysfs/kobject infrastructure, `acpi_kobj`, NUMA node/zone APIs, and potential resctrl consumers of `acpi_mrrm_max_mem_region()`.

## Risks
The parser walks entries by firmware-provided lengths without explicit per-entry length validation or a zero-length guard. `local_region_id` and `remote_region_id` are `u8` but assigned `-1`, which becomes 255 while displayed with `%d`. Cleanup in `add_boot_memory_ranges()` removes child kobjects but does not keep a parent pointer for later teardown because this is boot-time-only setup.

## Test Signals
Tests should cover no MRRM table, unsupported revision, OS-assignment flag, no ranges, malformed entry lengths, valid local/remote IDs, missing IDs, NUMA node matching, sysfs range attributes, and the exported max-region value.
