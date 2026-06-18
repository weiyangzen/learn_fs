# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs.h

## Purpose

`nfs.h` is the shared contract for the Gluster NFS translator. It defines global constants, the protocol initializer callback type, central `struct nfs_state`, per-inode NFS context, user credential representation, and public helpers used by NFS protocol modules.

## Important APIs, types, and functions

- `GF_NFS`, memory/concurrency defaults, inode LRU multiplier, event-thread bounds, dynamic-volume constants, export-auth defaults, and auth cache defaults define core sizing and behavior.
- `nfs_version_initer_t` and `struct nfs_initer_list` describe protocol registration entries.
- `struct nfs_state` stores versions, gid cache, locks, RPC service, mount/NFSv3/NLM states, FOP mempool, subvolume/startup state, rmtab/statd paths, runtime options, auth settings, generation, and event-thread count.
- `struct nfs_inode_ctx` stores per-inode share state and generation.
- `nfs_user_t` stores uid, primary plus auxiliary gids, lock owner, and peer identifier.
- Public helpers initialize users, check subvolume startup, fix groups, and start the RPC poller.

## Control flow

The header defines macro-level access patterns rather than executing control flow. `gf_nfs_this_private` assumes `THIS` is the NFS xlator and exposes the private state; `gf_nfs_enable_ino32()` is used by NFSv3 attribute conversion to decide whether to hash GFIDs into 32-bit inode numbers.

## State and persistence behavior

`struct nfs_state` is process-local and authoritative for live NFS behavior. It includes references to persistent-path settings (`rmtab`, statd pid file), but actual persistence is performed by mount/statd/RPC code. `generation` lets dependent inode contexts detect topology changes; `gid_cache` caches server-side auxiliary group lookups.

## Dependencies and integration points

The header includes RPC service types, Gluster dict/gidcache/lkowner types, and is included by most NFS server modules. It is the shared ABI between `nfs.c`, NFSv3 code, mount, NLM, ACL, FOP wrappers, and helpers.

## Risks and edge cases

- Macros tied to global `THIS` are convenient but fragile in async callbacks if `THIS` is not the expected xlator.
- `NFS_NGROUPS` is fixed to protocol limits plus one primary gid, so callers must reject longer aux lists.
- `struct nfs_state` has many ownership-bearing pointers; lifecycle cleanup is spread across modules.

## Test signals

Build coverage detects ABI drift. Runtime tests should verify uid/gid extraction, auxiliary group truncation/rejection, `enable_ino32` behavior, generation changes on graph notifications, and correct defaults for auth/cache/event-thread options.
