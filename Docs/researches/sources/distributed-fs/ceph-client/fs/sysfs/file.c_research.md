# sources/distributed-fs/ceph-client/fs/sysfs/file.c

## Purpose
This file implements sysfs regular text attributes, binary attributes, notifications, ownership/mode changes, active-protection helpers, and safe emit helpers.

## Important APIs, Types, and Functions
Public APIs include `sysfs_create_file_ns()`, `sysfs_create_files()`, `sysfs_add_file_to_group()`, `sysfs_chmod_file()`, `sysfs_break_active_protection()`, `sysfs_unbreak_active_protection()`, `sysfs_remove_file_ns()`, `sysfs_remove_file_self()`, `sysfs_remove_files()`, `sysfs_remove_file_from_group()`, `sysfs_create_bin_file()`, `sysfs_remove_bin_file()`, `sysfs_link_change_owner()`, `sysfs_file_change_owner()`, `sysfs_change_owner()`, `sysfs_emit()`, `sysfs_emit_at()`, `sysfs_bin_attr_simple_read()`, and `sysfs_notify()`. Internal kernfs callbacks adapt `sysfs_ops->show/store` and `bin_attribute` read/write/mmap/llseek.

## Control Flow and State
Regular text reads normally use seq_file through `sysfs_kf_seq_show()`, which allocates a page-sized buffer and calls `ops->show(kobj, attr, buf)`. Preallocated attributes instead call `sysfs_kf_read()` directly into kernfs' prealloc buffer. Writes call `ops->store()`. Binary files enforce optional size bounds and delegate read/write/mmap/llseek/open to `bin_attribute` callbacks.

`sysfs_add_file_mode_ns()` selects kernfs ops based on available show/store and `SYSFS_PREALLOC`; `sysfs_add_bin_file_mode_ns()` selects binary ops based on callback capabilities. Removal uses `kernfs_remove_by_name[_ns]`. Ownership changes look up kernfs nodes and call `kernfs_setattr()`, with `sysfs_change_owner()` also propagating to default groups.

## Persistence, Dependencies, and Integration
Sysfs file contents are generated from live kernel state, not stored on disk. Dependencies include kobject `ktype->sysfs_ops`, kernfs active protection, lockdep keys in attributes, seq_file, and driver-core default groups.

## Risks and Test Signals
Risk points are invalid `show()` lengths, missing `sysfs_ops`, attributes disappearing during self-removal, binary bounds mistakes, lockdep class mistakes, and exposing mutable subsystem state without proper subsystem locking. Tests should include sysfs read/write ABI checks, self-deleting attributes, binary file bounds/mmap paths, `sysfs_notify()` polling, ownership propagation, and lockdep-enabled sysfs stress.
