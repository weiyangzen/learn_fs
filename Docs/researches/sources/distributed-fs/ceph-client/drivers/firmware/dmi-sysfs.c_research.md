# sources/distributed-fs/ceph-client/drivers/firmware/dmi-sysfs.c

## Purpose
This module exports raw SMBIOS/DMI table entries under `/sys/firmware/dmi/entries`. Each DMI structure is represented as `<type>-<instance>` with generic metadata and an admin-only `raw` binary file. Type 15 System Event Log entries also receive a specialized `system_event_log` child.

## Important APIs, Types, And Functions
`struct dmi_sysfs_entry` stores the copied DMI header, kobject, type instance, global position, list node, and optional child. `entry_list` tracks entries for cleanup under `entry_list_lock`.

Generic attributes are defined through `struct dmi_sysfs_attribute` and `DMI_SYSFS_ATTR()` for `length`, `handle`, `type`, `instance`, and `position`. Specialized mapped attributes use `struct dmi_sysfs_mapped_attribute`. `find_dmi_entry()` re-walks DMI tables by type and instance. `dmi_entry_length()` includes formatted bytes plus the trailing double-NUL string area.

Type 15 support defines `struct dmi_system_event_log`, decoded SEL fields, indexed I/O readers when `CONFIG_HAS_IOPORT` is available, physical-memory reading through `dmi_remap()`, and `raw_event_log_read()`.

## Control Flow
`dmi_sysfs_init()` checks `dmi_kobj`, creates the `entries` kset, walks DMI tables, and registers one kobject per entry via `dmi_sysfs_register_handle()`. Registration creates generic files, optional SEL child files, and the raw binary file. Errors trigger cleanup and kset unregister.

Generic sysfs reads require `CAP_SYS_ADMIN` and dispatch to show callbacks. Raw reads re-find the matching DMI entry and use `memory_read_from_buffer()`. SEL raw reads dispatch by access method: indexed I/O, physical memory, unsupported GPNV, or unknown method.

`dmi_sysfs_exit()` releases all entries and unregisters the kset.

## State And Persistence Behavior
Persistent state includes `dmi_kset`, init-only instance/position counters, and the global entry list. Entries keep only headers and identity metadata; full raw bytes are obtained by re-walking the DMI table. The module is read-only but SEL raw reads may perform hardware I/O or mapped physical reads.

## Dependencies And Integration Points
The file depends on the DMI core, sysfs/kobject/kset APIs, capabilities, binary sysfs attributes, `memory_read_from_buffer()`, I/O port accessors, and DMI remap helpers. Userspace integration is `/sys/firmware/dmi/entries/<type>-<instance>/`.

## Risks And Edge Cases
Risks include malformed firmware tables, kobject lifetime ordering, and firmware-provided SEL access descriptors that point to unavailable I/O or memory. Admin-only permissions are essential because raw DMI data can expose platform identifiers. Cleanup must tolerate partially initialized child kobjects after registration failures.

## Test Signals
Signals include successful creation of entry directories, correct metadata, admin-only raw reads, SEL child creation for type 15, graceful failure when `dmi_kobj` is absent, and clean module unload.
