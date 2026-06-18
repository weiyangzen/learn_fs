# sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_sas_debugfs.c

## Purpose

`megaraid_sas_debugfs.c` provides the optional debugfs interface for MegaRAID SAS Fusion adapters. When `CONFIG_DEBUG_FS` is enabled, it creates a global `megaraid_sas` debugfs directory and per-adapter `scsi_hostN` directories. Each Fusion adapter gets a read-only `raidmap_dump` file that exposes the currently active driver RAID map buffer for inspection.

When debugfs is disabled, the same public functions compile to empty stubs so the base driver can call `megasas_init_debugfs()`, `megasas_exit_debugfs()`, `megasas_setup_debugfs()`, and `megasas_destroy_debugfs()` unconditionally.

## Important APIs, Types, and Functions

The file exports or defines four integration functions:

- `megasas_init_debugfs()`: creates the global `debugfs` root directory `megaraid_sas`.
- `megasas_exit_debugfs()`: recursively removes the global root.
- `megasas_setup_debugfs(struct megasas_instance *instance)`: creates a per-adapter directory and a read-only `raidmap_dump` file for Fusion adapters.
- `megasas_destroy_debugfs(struct megasas_instance *instance)`: removes a per-adapter debugfs subtree.

The debugfs file operations are `megasas_debugfs_raidmap_open()`, `megasas_debugfs_read()`, and `megasas_debugfs_release()`, registered in `megasas_debugfs_raidmap_fops`.

The relevant data type is `struct megasas_debugfs_buffer` from `megaraid_sas_fusion.h`. It stores a raw pointer and length for the data exposed through a debugfs file. The source also touches `struct megasas_instance`, `struct fusion_context`, and debugfs `struct dentry` handles stored on the instance.

## Control Flow

At module load, `megasas_init()` in the base file calls `megasas_init_debugfs()`. With debugfs enabled, the function creates `/sys/kernel/debug/megaraid_sas`. Failure is logged but not fatal.

During adapter probe, `megasas_probe_one()` calls `megasas_setup_debugfs(instance)` after SCSI attach and AEN startup. The function only creates files when `instance->ctrl_context` is non-NULL, so legacy MFI adapters do not get `raidmap_dump`. For Fusion adapters, it creates a directory named `scsi_host%d` under the global root and creates a read-only `raidmap_dump` file with `instance` as `inode->i_private`.

When user space opens `raidmap_dump`, `megasas_debugfs_raidmap_open()` retrieves the instance from `inode->i_private`, gets `fusion = instance->ctrl_context`, allocates a small `megasas_debugfs_buffer`, stores a pointer to `fusion->ld_drv_map[(instance->map_id & 1)]`, stores `fusion->drv_map_sz`, and places that wrapper in `file->private_data`.

Reads call `megasas_debugfs_read()`. It returns zero for missing state and otherwise delegates to `simple_read_from_buffer()` to copy from the RAID map into the user buffer using the supplied file offset. Release frees only the wrapper object, not the RAID map itself.

On adapter removal, `megasas_detach_one()` calls `megasas_destroy_debugfs(instance)` to remove the per-instance subtree. On module unload, `megasas_exit()` calls `megasas_exit_debugfs()` to remove the global root recursively.

## State and Persistence Behavior

The file does not persist data. It exposes live in-memory Fusion RAID map state through debugfs. The only allocated state is the per-open `megasas_debugfs_buffer` wrapper. That wrapper borrows the RAID map pointer owned by the Fusion context and must not free or modify it.

The global `megasas_debugfs_root` dentry persists for the lifetime of the module when debugfs initialization succeeds. Each instance may hold `instance->debugfs_root` and `instance->raidmap_dump` dentries until adapter teardown.

The RAID map snapshot is not copied at open time. It points directly at `fusion->ld_drv_map[instance->map_id & 1]`, so reads observe whichever map buffer was selected at open. If the map is updated or freed concurrently with a debugfs reader, correctness depends on broader driver lifetime and map synchronization.

## Dependencies and Integration Points

The file depends on `CONFIG_DEBUG_FS`, `<linux/debugfs.h>`, SCSI headers, `megaraid_sas_fusion.h`, and `megaraid_sas.h`. It is called by the base driver lifecycle functions and reads Fusion RAID map data maintained by the Fusion code and updated from firmware map-sync DCMDs.

User-space integration is a debug-only inspection path under debugfs, not a stable ioctl or sysfs ABI. The exposed file is read-only and intended for diagnostics of the driver RAID map.

## Risks and Edge Cases

`megasas_debugfs_release()` declares `struct megasas_debug_buffer *debug = file->private_data`, while open allocates `struct megasas_debugfs_buffer`. The searched source tree defines `struct megasas_debugfs_buffer` but not `struct megasas_debug_buffer`; with `CONFIG_DEBUG_FS=y`, this appears to be a build-breaking type-name mismatch unless another hidden typedef exists outside the searched files.

The debugfs read path exposes a borrowed RAID map pointer without taking a map lock or reference. Adapter removal uses `debugfs_remove_recursive()`, which prevents new opens, but concurrent readers still rely on debugfs teardown and broader driver lifetime rules to avoid use-after-free as Fusion maps are freed during detach.

`megasas_setup_debugfs()` removes `instance->debugfs_root` when `raidmap_dump` creation fails but does not clear `instance->debugfs_root`. A later destroy path calling `debugfs_remove_recursive(instance->debugfs_root)` should usually tolerate stale dentries through debugfs semantics, but clearing the pointer would reduce ambiguity.

The code treats a NULL return from `debugfs_create_dir()` or `debugfs_create_file()` as failure. Modern debugfs helpers can also encode errors depending on kernel version, so callers should be checked against the target tree's debugfs API conventions.

There is no explicit validation that `fusion->ld_drv_map[(instance->map_id & 1)]` is non-NULL before exposing it. If debugfs setup runs before map allocation or after map teardown due to a lifecycle regression, reads can return zero only if `debug->buf` is NULL; open itself still succeeds.

## Test Signals

Useful validation signals include a build with `CONFIG_DEBUG_FS=y` to catch the release-path type mismatch, a build with `CONFIG_DEBUG_FS=n` to verify stubs satisfy the base driver references, module load creating `/sys/kernel/debug/megaraid_sas`, Fusion adapter probe creating `scsi_hostN/raidmap_dump`, MFI adapter probe not creating per-adapter map files, reading `raidmap_dump` returning exactly `fusion->drv_map_sz` bytes with normal offset/short-read behavior, repeated open/read/close cycles without leaks, adapter removal while a reader is active, module unload cleaning the global root, and fault injection around debugfs creation failures.
