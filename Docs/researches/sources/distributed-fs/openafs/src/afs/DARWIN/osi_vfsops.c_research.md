# sources/distributed-fs/openafs/src/afs/DARWIN/osi_vfsops.c

## Purpose
Implements Darwin VFS operations for mounting, unmounting, rooting, statfs/getattr, sysctl, and operation-vector initialization for the OpenAFS filesystem.

## Important APIs, Types, And Functions
Key functions are `afs_mount`, `afs_unmount`, `afs_root`, older `afs_vget`/`afs_vfs_vget`, `afs_statfs`, modern `afs_vfs_getattr`, `afs_sysctl_int`, `afs_sysctl`, `afs_init`, and the exported `afs_vfsops` table. Globals include `afs_globalVp`, `afs_globalVFS`, `afs_vfs_typenum`, `afs_darwin_realmodes`, and `afs_darwin_fsevents`.

## Control Flow
Mount rejects updates/remount conflicts, records `afs_globalVFS`, sets I/O sizing and fsid, fills mount names, optionally resolves a named volume into a root fid stored in mount private data, and marks the VFS auth-opaque on modern Darwin. Root either reuses a cached global root vcache or initializes a request, checks AFS initialization, gets the desired root fid, finalizes the vnode, handles global root replacement races, and returns a vnode reference. Unmount frees mount-private root fids or, for the main mount, requires force to drop the global root, flush vnodes, clear `afs_globalVFS`, and warm-shutdown AFS. Statfs and getattr advertise fake capacity and capabilities. Sysctl exposes Darwin feature toggles.

## State And Persistence
Persistent state is the global mount pointer, cached root vcache, mount-private alternate root fid, VFS typenum, and sysctl feature variables. `afs_globalVp` intentionally holds the root around until unmount.

## Dependencies And Integration Points
Depends on Darwin VFS APIs, OpenAFS volume lookup, cell lookup, root fid handling, vcache acquisition, `afs_darwin_finalizevnode`, sysctl constants, and the vnode operation table from `osi_vnodeops.c`.

## Risks
Only one main AFS mount is supported; remounts return busy. Root vnode races are explicitly retried and can leak refs if mishandled. Named-volume mount private data stores allocated root fids and uses `(qaddr_t)-1` as a sentinel during unmount. Fake capacity/capability reporting must remain compatible with userland expectations.

## Test Signals
Mount `/afs`, mount named volumes, root lookup, statfs/getattr capability queries, sysctl reads/writes for Darwin toggles, forced and non-forced unmount behavior, and vnode flush during shutdown.
