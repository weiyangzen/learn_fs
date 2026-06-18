<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/mount.h -->
# sources/distributed-fs/ceph-client/fs/mount.h

## Purpose
`fs/mount.h` is an internal VFS mount namespace header. It defines the private `struct mount` that embeds public `struct vfsmount`, the mount namespace container, mountpoint records, per-CPU mount reference counters, propagation flags, and helper routines/macros used by path lookup and namespace management.

## Important APIs, Types, and Functions
`struct mnt_namespace` tracks namespace identity, root mount, an rb-tree of mounts, user namespace ownership, poll/event state, fsnotify marks, mount counts, passive references, and anonymous namespace state. `struct mount` contains parent/child topology, mountpoint dentry, namespace membership, per-superblock linkage, propagation lists, expiry/pin state, fsnotify state, IDs, peer group ID, and overmount pointer. Important helpers include `real_mount()`, `mnt_has_parent()`, `is_mounted()`, `__path_is_mountpoint()`, `detach_mounts()`, `get_mnt_ns()`, `is_local_mountpoint()`, `anon_ns_root()`, `mnt_ns_attached()`, `move_from_ns()`, `mnt_notify_add()`, `topmost_overmount()`, and write-hold bit helpers.

## Control Flow
Path lookup uses `real_mount()` to move from public `vfsmount` to private topology and `__lookup_mnt()`/`__path_is_mountpoint()` to detect covered dentries. Namespace mutation code uses `move_from_ns()` to remove a mount from the namespace rb-tree while maintaining cached first/last nodes. `detach_mounts()` avoids work unless the dentry has mountpoints. Lock guard macros wrap `mount_lock` seqlock operations for writers and exclusive readers. Fsnotify-aware builds queue mount namespace notifications only when the current or previous namespace has marks.

## State and Persistence Behavior
The header describes in-memory namespace and mount graph state only. Mount IDs, propagation topology, namespace rb-tree links, writer holds, and fsnotify connector pointers are runtime state. The `WRITE_HOLD` bit is stored in the low bit of `mnt_pprev_for_sb`, so pointer alignment is part of the representation.

## Dependencies and Integration Points
This header is included by core VFS namespace and namei code. `fs/namei.c` uses `real_mount()`, mount parent relationships, `mount_lock`, and `__lookup_mnt()` to implement `..`, mount crossing, `LOOKUP_NO_XDEV`, and managed dentry traversal. It also integrates with fsnotify, namespace common infrastructure, poll wait queues, rb-trees, mount propagation, and mount pinning.

## Risks
Mount topology is highly concurrent and protected by seqlocks, namespace locks, rb-tree invariants, and reference counts. Misusing `real_mount()` on invalid/internal mounts, failing to update first/last rb-tree caches in `move_from_ns()`, or mishandling the low-bit `WRITE_HOLD` encoding can corrupt namespace state. Helper callers must account for detached and internal mounts represented by null or error namespace pointers.

## Test Signals
Signals include mount/umount/move/bind propagation tests, path lookup across stacked mounts, `LOOKUP_NO_XDEV` behavior, namespace cloning and anonymous namespace handling, fsnotify mount namespace events, rb-tree order after mount removal, and stress tests around concurrent mount traversal with `mount_lock` sequence retries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/mount.h -->
