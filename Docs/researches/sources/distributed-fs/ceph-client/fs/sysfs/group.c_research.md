# sources/distributed-fs/ceph-client/fs/sysfs/group.c

## Purpose
This file manages sysfs attribute groups: creating, updating, removing, merging, adding links to groups, and changing group ownership.

## Important APIs, Types, and Functions
Public helpers include `sysfs_create_group()`, `sysfs_create_groups()`, `sysfs_update_group()`, `sysfs_update_groups()`, `sysfs_remove_group()`, `sysfs_remove_groups()`, `sysfs_merge_group()`, `sysfs_unmerge_group()`, `sysfs_add_link_to_group()`, `sysfs_remove_link_from_group()`, `compat_only_sysfs_link_entry_to_kobj()`, `sysfs_group_change_owner()`, and `sysfs_groups_change_owner()`. Internal helpers are `create_files()`, `remove_files()`, `internal_create_group()`, and ownership walkers.

## Control Flow and State
Group creation optionally creates a named subdirectory, with visibility decided by the first visible attribute and group callbacks. `create_files()` iterates text and binary attributes, evaluates per-attribute visibility and binary size callbacks, masks permissions to allowed sysfs bits, and creates kernfs files. On error it unwinds previously added files. Update mode removes existing files first, recalculates visibility/mode, and can remove the group directory if it becomes invisible.

Merging adds extra attributes to an existing named group with rollback on partial failure. Link helpers resolve the group directory and call sysfs symlink functions. Ownership changes update the group node and each visible member's kernfs attributes.

## Persistence, Dependencies, and Integration
Group state mirrors `struct attribute_group` declarations used throughout driver core and subsystem code. It depends on file.c helpers, symlink.c helpers, kernfs, kobject ownership, and visibility callbacks.

## Risks and Test Signals
Risks include partial group creation, visibility callbacks changing between update and removal, invalid permissions, missing named groups during merge/unmerge, and target kobject removal during compatibility symlink creation. Test signals include default group creation/unwind tests, dynamic visibility updates, binary attribute size callbacks, ownership propagation tests, and duplicate-name warnings.
