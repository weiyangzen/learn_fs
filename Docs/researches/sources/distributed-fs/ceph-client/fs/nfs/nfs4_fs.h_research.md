# sources/distributed-fs/ceph-client/fs/nfs/nfs4_fs.h

## Purpose

`nfs4_fs.h` is the central NFSv4 client-private header. It defines version bounds, client state flags, sequence/owner/state structures, minor-version operation tables, recovery hooks, stateid helpers, and cross-file function declarations used by NFSv4 procedure, state, namespace, client, file, idmap, xattr, and callback code.

## Important APIs, Types, and Functions

Key types include `enum nfs4_client_state`, `struct nfs4_minor_version_ops`, `struct nfs_seqid_counter`, `struct nfs_seqid`, `struct nfs4_state_owner`, `struct nfs4_lock_state`, `struct nfs4_state`, `struct nfs4_exception`, `struct nfs4_state_recovery_ops`, `struct nfs4_sequence_slot_ops`, `struct nfs4_state_maintenance_ops`, and `struct nfs4_mig_recovery_ops`.

The header exposes procedure-layer APIs such as `nfs4_handle_exception`, `nfs4_call_sync`, `nfs4_init_sequence`, `nfs4_proc_get_rootfh`, `nfs4_proc_exchange_id`, `nfs4_proc_create_session`, `nfs4_proc_fs_locations`, `nfs4_proc_secinfo`, `nfs4_set_rw_stateid`, `nfs4_bitmask_set`, and state/recovery helpers. It also declares `nfs4_xattr_cache_*` functions under `CONFIG_NFS_V4_2`.

## Control Flow

As a header, it does not own a runtime control loop. It defines contracts used across the NFSv4 client: procedure code fills `nfs4_exception` and calls `nfs4_handle_exception`; state code maintains `nfs4_state` and `nfs4_state_owner`; client code invokes minor-version ops; and RPC code uses sequence slots and state protection wrappers before calls.

## State and Persistence Behavior

The header describes in-memory state that persists for the life of mounts, opens, locks, delegations, sessions, and recovery episodes. `nfs4_state` tracks open/lock stateids, open mode reference counts, delegation/open flags, and wait queues. `nfs4_state_owner` and `nfs_seqid_counter` enforce ordered once-only open/lock owner semantics.

## Dependencies and Integration Points

The header is included by many NFSv4 implementation files and connects `nfs4client.c`, `nfs4proc.c`, `nfs4state.c`, `nfs4renewd.c`, `nfs4namespace.c`, `nfs42proc.c`, `nfs42xattr.c`, and XDR/procedure code.

## Risks and Edge Cases

Because this header defines shared contracts, risks are broad: state flag misuse, stale stateid comparison errors, incorrect machine-credential protection, or minor-version dispatch mismatches can break recovery and data consistency. Stateid helpers must respect sequence wrap rules and special zero/current/invalid stateids.

## Test Signals

Test signals are indirect: NFSv4.0 and v4.1/v4.2 mount/open/lock/recovery tests, session reset, delegation return, pNFS migration, stateid wrap behavior, machine credential cleanup/write paths, and xattr cache build coverage under `CONFIG_NFS_V4_2`.
