# sources/distributed-fs/ceph-client/fs/nfs/nfs4session.h

## Purpose
`nfs4session.h` declares the NFSv4.1 session and slot-table data structures shared by the NFSv4 client. It is the contract between session management, state recovery, XDR/SEQUENCE call setup, and callback handling.

## Important APIs and Types
- Constants: `NFS4_DEF_SLOT_TABLE_SIZE`, `NFS4_DEF_CB_SLOT_TABLE_SIZE`, `NFS4_MAX_SLOT_TABLE`, `NFS4_MAX_SLOTID`, `NFS4_NO_SLOT`.
- `struct nfs4_slot`: per-slot sequence state, slot number, table pointer, generation, and flags for privilege and sequence completion.
- `struct nfs4_slot_table`: parent session, slot list, used bitmap, locking, RPC wait queue, completion wait state, slot bounds, generation, and dynamic resizing derivatives.
- `struct nfs4_session`: session ID, session flags/state, channel attributes, fore/back slot tables, and owning `nfs_client`.
- Inline helpers: `nfs4_slot_tbl_draining()`, `nfs4_test_locked_slot()`, `nfs4_get_session()`, `nfs4_has_session()`, `nfs4_has_persistent_session()`, `nfs4_copy_sessionid()`, `nfs_session_id_hash()`.

## Control Flow
The header does not implement protocol control flow, but it defines the fields consumed by `nfs4session.c` and `nfs4state.c`. Slot users take `slot_tbl_lock`, reserve a bitmap bit, attach a slot to SEQUENCE args, and later free it. Recovery code tests `NFS4_SLOT_TBL_DRAINING` and waits on `complete`. Session users test `NFS4_SESSION_INITING` and `NFS4_SESSION_ESTABLISHED` through `session_state`.

## State and Persistence
The structures are transient client memory. The most important mutable state is the slot sequence counters and session ID because they mirror server-side session state. `generation` is used to avoid applying stale target-slot updates after target changes.

## Dependencies and Integration Points
The header is compiled only when `CONFIG_NFS_V4` is enabled. It depends on kernel bitmap sizing, CRC32 hashing, NFSv4 protocol structures, and SUNRPC wait queue types through includers. The exported declarations are used by session setup, client state recovery, callback SEQUENCE handling, and pNFS data-server session setup.

## Risks
Because the header fixes maximum slot table size and bitmap layout, changing constants can affect memory use and concurrency limits globally. Callers must honor the locking annotations in the C file; the header exposes raw structures, so misuse can bypass invariants such as `highest_used_slotid` consistency or drain semantics.

## Test Signals
Compile coverage under `CONFIG_NFS_V4`, `CONFIG_NFS_V4_1`, and pNFS configurations is the first signal. Runtime tests should validate that session ID hashes in trace output remain stable, persistent-session detection follows `SESSION4_PERSIST`, and slot table size bounds prevent out-of-range slot IDs.
