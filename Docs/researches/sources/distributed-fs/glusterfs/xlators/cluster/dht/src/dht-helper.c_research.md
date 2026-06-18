# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-helper.c

## Purpose

`dht-helper.c` provides the shared runtime machinery behind DHT FOP implementations: fd-context tracking, migration info, fd reopening on migration targets, subvolume selection helpers, `dht_local_t` lifecycle, attribute merging, subvolume initialization, rebalance phase checks, inode context management, path healing, lock-subvolume routing, and directory xattr-heal helpers.

## Important APIs, Types, and Functions

FD state is handled by `dht_fd_ctx_set`, `dht_fd_open_on_dst`, and `dht_fd_ctx_destroy`; migration state by `dht_inode_ctx_set_mig_info`, `dht_inode_ctx_get_mig_info`, and `dht_mig_info_is_invalid`. `dht_check_and_open_fd_on_subvol` starts a synctask that opens an fd on the cached/destination child and then resumes the original FOP through `dht_check_and_open_fd_on_subvol_complete`. General helpers include `dht_frame_return`, `dht_filter_loc_subvol_key`, `dht_deitransform`, `dht_local_init`, `dht_local_wipe`, `dht_subvol_get_hashed`, `dht_subvol_get_cached`, `dht_iatt_merge`, and `dht_build_child_loc`. Rebalance checks are split between `dht_rebalance_complete_check` and `dht_rebalance_in_progress_check`. Inode context APIs include layout get/set wrappers, time cache updates, MDS/lock subvolume slots, and migration ctx cleanup.

## Control Flow

Most callers enter through a FOP callback after detecting migration phase bits, `EREMOTE`, `ENOENT`, `ESTALE`, `EBADF`, or similar stale-fd symptoms. For complete migration, the synctask reads the source linkto xattr, performs a DHT lookup to refresh cached layout, validates GFID, resets migration info, and opens every live fd on the new destination. For in-progress migration, it reads linkto, looks up the destination directly, validates GFID, opens all inode fds on the destination, and records source/destination migration info. The completion callback invokes the saved `local->rebalance.target_op_fn` so read/write callbacks can retry against the selected child.

## State and Persistence Behavior

The file manipulates runtime state across three scopes. FD context stores the child on which a specific fd is open. Inode context stores layout, timestamps, lock subvolume, MDS subvolume, and a second ctx slot for migration info. `dht_local_t` owns transient refs to locs, dicts, fd, inode, layout, rebalance vectors/iobrefs, call stubs, and lock arrays; `dht_local_wipe` is the authoritative cleanup. Persistent state is consulted through linkto xattrs, ancestry path xattrs, and DHT layout data but not normally written here except through child open/lookups and ctx updates.

## Dependencies and Integration Points

This file integrates with `dht-inode-read.c` and `dht-inode-write.c` retry paths, with layout/hash helpers for cached and hashed subvolumes, with lock code through `dht-lock.h`, with syncop APIs for migration and path heal, and with inode/fd tables. `dht_iatt_merge` is used by directory and multi-child operations to synthesize attributes. `dht_get_lock_subvolume` stabilizes directory locks across lock/unlock by storing `lock_subvol` in inode ctx.

## Risks and Test Signals

High-risk areas are lock ordering around inode/fd lists, refcount ownership during fd-list iteration, stale migration ctx after multiple migrations, root-credential syncops, and the `dht_check_and_open_fd_on_subvol_task` path where the code comments say ENOENT/ESTALE can be tolerated but the later assignment still sets failure. Tests should cover migration phase1 and phase2 with open fds, multiple fds on one inode, fd already open on destination, nested DHT layers returning `ENODATA`, GFID mismatch, concurrent lookup changing cached subvol, directory lock/unlock after inode cache pressure, path-heal from ancestry xattr, `dht_local_wipe` leak checks, and subvolume initialization for one-child pass-through volumes.
