# sources/distributed-fs/ceph-client/include/linux/kernfs.h

## Purpose
Declares kernfs, the pseudo-filesystem framework used by sysfs-like hierarchies while decoupling node lifetime and locking from VFS details.

## Important APIs, Types, And Functions
Core types include `struct kernfs_global_locks`, `enum kernfs_node_type`, node/root flags, `struct kernfs_elem_dir`, symlink and attr unions, `struct kernfs_node`, `struct kernfs_syscall_ops`, `struct kernfs_open_file`, `struct kernfs_ops`, and `struct kernfs_fs_context`. Public APIs cover root creation/destruction, node lookup/path/name/refcounting, directory/file/link creation, activation/show/remove/rename/setattr, open-file poll/notify, xattrs, mount context handling, namespace filtering, ID lookup, and convenience wrappers without namespace arguments.

## Control Flow
Callers create a root, build nodes, optionally keep them deactivated for atomic visibility, then activate. VFS opens populate `kernfs_open_file` and route reads through seq_file or raw read callbacks, writes through bounced buffers, and optional mmap/poll/llseek hooks. Namespace-enabled directories filter children by superblock namespace tags.

## State And Persistence
Each `kernfs_node` carries reference and active counts, parent/name RCU pointers, rbtree membership, namespace tag, hash, flags, mode, type-specific data, stable ID/generation, private pointer, optional iattrs, and RCU reclamation. Open-file state tracks per-open private data, event counters, buffers, mmap state, and release status. State is in-memory pseudo-filesystem state.

## Dependencies And Integration Points
Depends on lists, mutexes, IDR, lockdep, rbtree, atomics, uid/gid, wait queues, rwsems, RCU, VFS types, fs_context, seq_file, and vm operations. Integrates with sysfs, cgroups, config-like filesystems, namespace-aware mounts, exportfs handles, and user xattrs.

## Risks
Reference count and active protection rules are central: holding `count` only keeps the node memory accessible, while dereferencing outer entities requires an active reference. Hashed open-file locks reduce contention but do not provide global exclusion. `KERNFS_ROOT_EXTRA_OPEN_PERM_CHECK` deliberately changes permission semantics.

## Test Signals
Signals include sysfs/kernfs selftests, concurrent create/remove/rename/open/read/write, namespace filtering, deactivated activation atomicity, poll/notify behavior, mmap files, xattrs, exportfs ID lookup, RCU/refcount debugging, and disabled `CONFIG_KERNFS` stub builds.
