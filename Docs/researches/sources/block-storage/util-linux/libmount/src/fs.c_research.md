# File Research: sources/block-storage/util-linux/libmount/src/fs.c

This file implements `struct libmnt_fs`, the core representation for one fstab, mtab, mountinfo, swap, or statmount-derived filesystem entry. It owns string fields, mount IDs, propagation, source tags, options split by class, swap metadata, and conversion/matching helpers.

Key entry points:

- Lifecycle: `mnt_new_fs()`, `mnt_free_fs()`, `mnt_reset_fs()`, `mnt_ref_fs()`, `mnt_unref_fs()`.
- Copying: `mnt_copy_fs()` copies unset fields into a destination; `mnt_copy_mtab_fs()` creates an mtab-safe copy with options filtered by `MNT_NOMTAB`.
- Source/target/type: `mnt_fs_get_source()`, `mnt_fs_set_source()`, `mnt_fs_get_srcpath()`, `mnt_fs_get_tag()`, `mnt_fs_get_target()`, `mnt_fs_set_target()`, `mnt_fs_get_fstype()`, `mnt_fs_set_fstype()`.
- Options: `mnt_fs_set_options()`, append/prepend variants, `mnt_fs_get_options()`, `mnt_fs_strdup_options()`, `mnt_fs_get_fs_options()`, `mnt_fs_get_vfs_options()`, `mnt_fs_get_user_options()`, and attribute/comment helpers.
- Identity and metadata: mount ID, unique ID, parent IDs, namespace ID, device number, TID, root, bind source, propagation, swap size/priority.
- Matching: `mnt_fs_match_target()`, `mnt_fs_match_source()`, `mnt_fs_match_fstype()`, `mnt_fs_match_options()`.
- Diagnostics and interop: `mnt_fs_print_debug()`, `mnt_fs_to_mntent()`, `mnt_free_mntent()`.

Important behavior:

- Source parsing uses `blkid_parse_tag_string()` to recognize valid `LABEL=`, `UUID=`, and similar tags. When a source is a tag, `mnt_fs_get_srcpath()` deliberately returns `NULL`.
- Filesystem type setting updates cached flags for pseudo filesystems, network filesystems, and swap entries.
- Option strings can be backed by a `libmnt_optlist`. When `mnt_fs_follow_optlist()` is used, getters synchronize cached strings from the optlist age; reads are therefore not purely const-like operations.
- Option merging preserves read-only semantics: `merge_optstr()` removes duplicate `ro`/`rw` entries and gives `ro` precedence unless both sides explicitly specify `rw`.
- `mnt_fs_get_vfs_options_all()` emits all VFS options, including default inverted options from the option map.
- With `HAVE_STATMOUNT_API`, many getters lazily call `mnt_fs_try_statmount()` to fetch missing kernel data on demand.
- Target matching compares raw paths, then target canonicalization, and finally canonicalizes both sides for non-kernel/non-swap entries.
- Source matching first compares native source paths/tags, then cache-resolved paths, then compares tags read through libblkid/cache. It skips canonical source matching for network and pseudo filesystems.

Dependencies and interactions:

- Depends on optstring parsing, optlist age/versioning, libblkid tag parsing, mount type classifiers, cache/path resolution, and statmount support.
- `context_umount.c`, table lookup code, hooks, and update writers rely on this file's source/target/type and option semantics.
- `fs_statmount.c` fills fields that this file lazily exposes.

Risk notes:

- `mnt_copy_fs()` intentionally does not overwrite already-set destination strings. Callers that expect a complete replacement must clear fields first, as `context_umount.c` does for source and target.
- Returning cached internal string pointers makes lifetime depend on the `libmnt_fs`; callers must not free them.
- Statmount-on-demand can make getters perform syscalls unless fetching is disabled.
