<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/mnt_idmapping.c -->
# sources/distributed-fs/ceph-client/fs/mnt_idmapping.c

## Purpose
`mnt_idmapping.c` implements mount idmapping objects and UID/GID translation helpers for idmapped mounts. It maps filesystem `kuid_t`/`kgid_t` values to VFS-facing `vfsuid_t`/`vfsgid_t` values and back, allocates immutable mount idmap copies from user namespaces, reference-counts them, and renders idmap state for mount stat reporting.

## Important APIs, Types, and Functions
`struct mnt_idmap` contains copied `uid_gid_map` instances and a refcount. Two global exported singleton maps exist: `nop_mnt_idmap` for identity mapping and `invalid_mnt_idmap` for forced invalid mapping. `make_vfsuid()` and `make_vfsgid()` map filesystem IDs into the mount idmap for reporting. `from_vfsuid()` and `from_vfsgid()` map VFS IDs back into a filesystem user namespace for inode writes. `vfsgid_in_group_p()` checks group membership. `alloc_mnt_idmap()`, `mnt_idmap_get()`, and `mnt_idmap_put()` manage dynamic idmap lifetime. `statmount_mnt_idmap()` prints UID or GID extents relative to the caller's current user namespace.

## Control Flow
Fast paths return immediately for `nop_mnt_idmap` and `invalid_mnt_idmap`. Otherwise, `make_vfsuid()`/`make_vfsgid()` first translate the kernel ID out of the filesystem namespace with `from_kuid()`/`from_kgid()` unless the filesystem namespace is initial, then map the raw ID down through the mount idmap. Reverse conversion maps up through the mount idmap and constructs a kernel ID in the filesystem namespace. Allocation copies both UID and GID maps from the mount user namespace, duplicating dynamically allocated extent arrays when the map has more than the inline extent capacity. Put frees those arrays when the refcount reaches zero.

## State and Persistence Behavior
Mount idmaps are in-memory kernel objects associated with mounts; they are not themselves persistent filesystem state. They do, however, control whether persisted inode UID/GID writes are allowed and how IDs are presented to userspace. Copied maps are immutable after creation, relying on user namespace map immutability once `nr_extents` is non-zero. The statmount path emits NUL-separated mapping triplets and skips extents that cannot be resolved in the caller's idmap.

## Dependencies and Integration Points
This file integrates with `<linux/mnt_idmapping.h>`, user namespace ID maps, VFS permission helpers, inode ownership helpers, mount lifetime management, and seq-file mount stat reporting. Filesystems and VFS code pass `struct mnt_idmap *` into permission, create, setattr, and getattr paths.

## Risks
Incorrect map direction is security-sensitive: reporting and writing IDs use opposite transformations. `copy_mnt_idmap()` relies on memory barriers and the immutability of written user namespace maps; copying a partially initialized map would be dangerous. Dynamic extent allocation must free both forward and reverse arrays on all failure paths. Invalid or unmapped IDs must remain invalid to prevent inode ownership corruption.

## Test Signals
Exercise identity maps, invalid maps, single and multi-extent maps, mappings relative to non-initial filesystem namespaces, unmapped ID failures, refcount get/put lifetime, allocation failure during reverse extent copy, `vfsgid_in_group_p()` with and without `CONFIG_MULTIUSER`, and `statmount_mnt_idmap()` output/overflow behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/mnt_idmapping.c -->
