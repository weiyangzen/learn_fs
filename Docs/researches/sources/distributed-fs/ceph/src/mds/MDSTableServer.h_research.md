# sources/distributed-fs/ceph/src/mds/MDSTableServer.h

## Purpose
Declares abstract server-side MDS table protocol support on top of `MDSTable`, including prepare/commit/rollback/query handling and recovery APIs.

## Important APIs, Types, And Functions
Subclasses implement query handling, `_prepare`, `_get_reply_buffer`, `_commit`, `_rollback`, `encode_server_state`, and `decode_server_state`, with optional `_server_update` and `_notify_prep`. Public methods handle requests, server updates, replay notes, reset/encode/decode, finish recovery, and peer recovery/failure.

## Control Flow
Requests are journaled through private logged handlers before subclass hooks apply table changes. Recovery rebuilds pending operations and notifies active clients.

## State And Persistence Behavior
Stores table id, recovered flag, active clients, pending prepares by tid, committing tids, and pending notify gathers. Only subclass state and `pending_for_mds` are table-encoded.

## Dependencies And Integration Points
Depends on MDSTable, table type helpers, `mds_table_pending_t`, Ceph refs, and `MMDSTableRequest`. Driven by `MDSRank` table request routing.

## Risks
Subclasses must encode sufficient server state for replay. `_notify_prep` changes reply ordering. Copy operations exist for dencoder support and must remain safe with runtime members.

## Test Signals
Fake subclass tests for hooks, encode/decode wrapping, reset, replay note helpers, recovery APIs, and table-specific failover integration.
