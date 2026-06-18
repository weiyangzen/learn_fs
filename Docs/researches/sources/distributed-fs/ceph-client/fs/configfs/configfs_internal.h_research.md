# sources/distributed-fs/ceph-client/fs/configfs/configfs_internal.h

Purpose: defines configfs-private structures, flags, globals, helpers, and cross-file prototypes shared by the implementation.

Important APIs/types: `struct configfs_fragment` carries `frag_count`, `frag_sem`, and `frag_dead` to block file callbacks during teardown. `struct configfs_dirent` stores refcount, dependency/link counts, sibling/child lists, backing element, type flags, mode, dentry, persistent iattrs, optional lockdep depth, and fragment pointer. Flags distinguish root, directories, text/bin attributes, symlinks, user-created groups, default groups, dropping/creating states, and pinned versus lookup-created entries. Inline helpers convert dentries to items/attributes, get config items safely, and refcount dirents/fragments.

Control flow: not a runtime unit, but it encodes invariants used across files: pinned entries have dentries held in core; attributes are created lazily at lookup; fragments are shared by a group subtree and marked dead before detach.

State and persistence: state is held in dirents and fragments. `s_iattr` preserves chmod/chown/timestamps while dentries/inodes come and go in the RAM filesystem.

Dependencies/integration: declares `configfs_dirent_lock`, `configfs_symlink_mutex`, `configfs_dir_cachep`, inode/file/dir/symlink operations, mount pin/release functions, and creation helpers used among `dir.c`, `file.c`, `inode.c`, `mount.c`, and `symlink.c`.

Risks: flag semantics are subtle, especially `CONFIGFS_USET_CREATING`, `DROPPING`, and `IN_MKDIR`. Refcount mistakes on dirents/fragments can produce use-after-free or leaks. `configfs_get_config_item()` depends on dentry lock and unhashed checks.

Test signals: lockdep with default groups, refcount leak tests across subsystem unregister, attribute lookup/open during rmdir, symlink/rmdir races, and chmod persistence after dentry eviction/relookup.
