# sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp_sysfs.c

## Purpose
Despite its filename, implements debugfs diagnostics for the Compaq hotplug driver. It exposes one read-only debugfs file per controller showing free controller resources and resources assigned to devices in each slot.

## Important APIs, Types, and Functions
Important pieces are `cpqphp_mutex`, `show_ctrl()`, `show_dev()`, `spew_debug_info()`, `struct ctrl_dbg`, `MAX_OUTPUT`, file operations `open()`, `lseek()`, `read()`, `release()`, `debug_ops`, and public lifecycle functions `cpqhp_initialize_debugfs()`, `cpqhp_shutdown_debugfs()`, `cpqhp_create_debugfs_files()`, and `cpqhp_remove_debugfs_files()`.

## Control Flow
Module init creates `/sys/kernel/debug/cpqhp`. Controller probe calls `cpqhp_create_debugfs_files()` with a file named after the PCI device. On open, the file allocates a `ctrl_dbg` buffer, snapshots formatted controller and per-slot resource data under a mutex, and stores it in `file->private_data`. Read uses `simple_read_from_buffer()`, lseek uses `fixed_size_llseek()`, and release frees the snapshot. Controller cleanup removes the file; module cleanup removes the root dentry.

## State and Persistence Behavior
Debug output is generated as an open-time snapshot into a `4 * PAGE_SIZE` heap buffer. It does not persist resource state or update live while the file is held open. Each controller stores its created dentry in `ctrl->dentry`; `root` is module-global.

## Dependencies and Integration Points
Depends on debugfs, file operations, controller/resource structures from `cpqphp.h`, `cpqhp_slot_find()` from the control file, and probe/cleanup calls from `cpqphp_core.c`.

## Risks
Formatting uses `sprintf()` into a fixed buffer and caps each list at eleven entries, so large resource lists can be truncated and the buffer relies on implicit size sufficiency. The global mutex protects snapshot allocation/formatting but does not lock controller resource mutation comprehensively. `debugfs_remove(root)` is nonrecursive compared with `debugfs_remove_recursive()`, so children must be removed first.

## Test Signals
Debugfs root creation/removal, per-controller file creation/removal, open/read/lseek/release behavior, output for free and assigned resources, truncation behavior with many resource nodes, concurrent hotplug while reading, and cleanup while files are not open are useful signals.
