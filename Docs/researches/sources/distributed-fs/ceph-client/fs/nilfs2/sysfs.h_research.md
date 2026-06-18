# sources/distributed-fs/ceph-client/fs/nilfs2/sysfs.h

## Purpose
This header declares the NILFS2 sysfs support data structures and attribute-definition macros used by `sysfs.c`. It centralizes the sysfs root name, per-device subgroup kobjects, and strongly-typed attribute wrapper structures for feature, device, subgroup, and snapshot sysfs files.

## Important APIs, Types, And Functions
`NILFS_ROOT_GROUP_NAME` defines the root sysfs directory name `nilfs2`. `struct nilfs_sysfs_dev_subgroups` embeds kobjects and unregister completions for `superblock`, `segctor`, `mounted_snapshots`, `checkpoints`, and `segments`. Macro families `NILFS_KOBJ_ATTR_STRUCT`, `NILFS_DEV_ATTR_STRUCT`, and `NILFS_CP_ATTR_STRUCT` define attribute structs with matching callback signatures. `NILFS_RO_ATTR`, `NILFS_RW_ATTR`, and the group-specific wrappers instantiate `__ATTR()` records, while `*_ATTR_LIST()` macros feed attribute arrays.

## Control Flow
The header has no executable control flow; it shapes compile-time code generation. `sysfs.c` uses the macros by defining concrete show/store functions first, then expanding macros such as `NILFS_SUPERBLOCK_RW_ATTR(sb_update_frequency)` and placing their `struct attribute` members into `ATTRIBUTE_GROUPS()` arrays.

## State, Persistence, And Dependencies
State is embedded into `struct the_nilfs` through `ns_dev_subgroups` and into `struct nilfs_root` through snapshot kobjects declared in `the_nilfs.h`. Dependencies are Linux sysfs, kobject, and completion infrastructure plus forward declarations supplied by NILFS headers.

## Integration Points
The declarations are tightly coupled to `sysfs.c` naming conventions: callback names must match `nilfs_<type>_<name>_show` and optional `_store`. The subgroup structure layout is also used by generated release functions through `container_of()`, so field names and macro arguments must remain synchronized.

## Risks
The macro layer reduces repetition but hides type relationships. A mismatched macro argument can generate code that compiles against the wrong field or callback signature. `NILFS_SEGMENTS_RW_ATTR` expands to `NILFS_RW_ATTR(segs_info, name)`, which is suspicious because the file defines `struct nilfs_segments_attr`, not `nilfs_segs_info_attr`; it is currently unused, but using it would likely break compilation.

## Test Signals
Compile coverage is the primary signal. Adding a temporary read/write attribute for each macro family, building with `W=1`, and checking generated sysfs mode bits verifies the header. Runtime tests should confirm every declared subgroup appears under `/sys/fs/nilfs2/<device>`.
