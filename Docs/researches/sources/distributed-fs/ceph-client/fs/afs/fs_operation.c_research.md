# sources/distributed-fs/ceph-client/fs/afs/fs_operation.c

Purpose: `fs_operation.c` provides the common lifecycle for fileserver-directed operations: allocate operation state, serialize vnode I/O, dispatch AFS/YFS RPCs, run result hooks, and release resources.

Important APIs and functions: exported functions are `afs_alloc_operation()`, `afs_begin_vnode_operation()`, `afs_end_vnode_operation()`, `afs_wait_for_operation()`, `afs_put_operation()`, and `afs_do_sync_operation()`. Internal I/O-lock helpers manage custom vnode serialization with `AFS_VNODE_IO_LOCK` and waiters.

Control flow: allocation obtains or references a key, pins the volume, records callback/volume snapshots, assigns a debug ID, and initializes an error. Begin optionally acquires one or two vnode I/O locks in address order, records FIDs, data versions, callback breaks, and modification flags. Wait loops through server selection, invokes AFS or YFS issue callbacks, waits for rxrpc completion, and dispatches success/aborted/failed hooks. It drops I/O locks before running `edit_dir`. Put runs cleanup hooks, clears modifying flags, releases vnodes, server state, volume, key, and memory.

State and persistence: operations are transient but capture durable expectations such as `dv_before`, `dv_delta`, callback breaks, selected server/address, and `AFS_VNODE_MODIFYING`. The custom I/O lock exists because acquisition and release can occur in different contexts.

Dependencies and integration points: used by directory, file, inode, flock, ACL, and YFS paths; depends on server selection, rxrpc call wrappers, key/volume/server refcounting, vnode flags, and operation callback tables.

Risks: missing begin calls lead to stale snapshots. Two-vnode locking must avoid deadlocks. Interruptible lock waiters must hand off correctly on signals. Edit hooks run after server serialization and must revalidate independently. `more_files` refs must be released correctly.

Test signals: one- and two-vnode operations, signal interruption during I/O lock wait, missing RPC issue functions, server rotation, hook dispatch paths, edit ordering, modifying flag cleanup, address preference update, and `more_files` release.
