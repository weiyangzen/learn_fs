# File Research: sources/block-storage/linux-dm/drivers/md/dm-ioctl.c

## Purpose
Implements the `/dev/mapper/control` ioctl interface for Device Mapper. It creates, removes, renames, suspends, resumes, loads tables, reports status/dependencies, sends messages, lists devices/target versions, supports polling, and provides early-boot DM creation.

## Main Interfaces
- Control file operations: `dm_open()`, `dm_release()`, `dm_poll()`, `dm_ctl_ioctl()`.
- Device hash management: `dm_hash_insert()`, `dm_hash_rename()`, `dm_hash_remove_all()`, `dm_deferred_remove()`.
- Device commands: `dev_create()`, `dev_remove()`, `dev_rename()`, `dev_suspend()`, `dev_status()`, `dev_wait()`.
- Table commands: `table_load()`, `table_clear()`, `table_deps()`, `table_status()`.
- Message/version/list commands: `target_message()`, `list_devices()`, `list_versions()`, `get_target_version()`.
- Interface setup: `dm_interface_init()`, `dm_interface_exit()`.
- Utilities exported/early: `dm_copy_name_and_uuid()`, `dm_early_create()`.

## Control Flow
`ctl_ioctl()` checks `CAP_SYS_ADMIN`, validates the ioctl type and DM interface version, looks up the command handler, copies and validates the user parameter block, runs the selected handler, optionally issues a global event, copies results back, and wipes secure buffers when requested.

Mapped devices are indexed by name and UUID rb-trees, each entry holding the `mapped_device` and an optional inactive table. Create allocates a DM device and inserts a hash cell. Table load builds a new inactive `dm_table`, validates queue type/immutable target constraints, measures it for IMA, and stages it in the hash cell. Resume swaps the inactive table into the live table, updates read-only state, resumes the device, destroys the old table, and emits uevents.

Status and dependency queries retrieve either the live or inactive table under SRCU and serialize target data into the ioctl result buffer. Target messages with `@` prefixes are handled by DM core; other messages are routed to the target covering the supplied sector.

## State And Synchronization
Global name and UUID rb-trees are protected by `_hash_lock`. `dm_hash_cells_mutex` protects mdptr-to-hash-cell name/UUID access. Live tables are protected by DM’s SRCU table access rules. Device queue type changes are serialized with `dm_lock_md_type()`. Per-open `struct dm_file` stores the global event number used by poll.

## Integration Points
This file bridges user space and DM core: mapped device allocation/destruction, table construction, target type registry, stats messages, IMA measurement, uevents, misc device registration, compat ioctl handling, and global event polling.

## Notable Behaviors
- Lookup accepts exactly one identifier: UUID, name, or device number; UUID wins only when supplied alone.
- `DM_SECURE_DATA_FLAG` causes the user buffer and kernel copy to be wiped.
- `DM_DEFERRED_REMOVE` can mark busy devices for later removal.
- `DM_QUERY_INACTIVE_TABLE_FLAG` switches status/dependency queries to the staged inactive table.
- Remove-all loops until no more progress is possible because mapped devices can depend on other mapped devices.
- Early boot creation bypasses normal ioctl serialization by receiving target specs and parameter strings directly.

## Risks And Review Focus
- User-buffer sizing and alignment are security-sensitive, especially variable-length status, dependency, and list responses.
- The `_hash_lock` and SRCU table lifetime comments are important; destroying tables while a live-table reference is held can deadlock.
- Rename and UUID-setting paths mutate hash-cell strings under mixed rwsem/mutex protection.
- Resume error paths must correctly destroy or preserve inactive/live tables.
- Target messages can return data through the ioctl buffer, so buffer-full detection must be honored.
