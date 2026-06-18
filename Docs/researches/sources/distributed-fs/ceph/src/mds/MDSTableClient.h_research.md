# sources/distributed-fs/ceph/src/mds/MDSTableClient.h

## Purpose
Declares abstract client-side MDS table mutation protocol support. It supplies prepare/commit/recovery bookkeeping and delegates table-specific behavior to subclasses.

## Important APIs, Types, And Functions
Public methods include `handle_request`, `_prepare`, `commit`, resend helpers, journal recovery hooks, `has_committed`, `wait_for_ack`, `get_journaled_tids`, `handle_mds_failure`, and `is_server_ready`. Subclasses implement query resend/result, notify-prep, and commit notification. `_pending_prepare` stores context, tid pointer, optional buffer pointer, and mutation.

## Control Flow
Callers prepare a mutation, receive a tid, journal or use it, then commit with a log segment. Recovery replays agree/ack state and server-ready triggers resends.

## State And Persistence Behavior
Defines volatile maps/lists for pending prepares, prepared updates, waiting-for-reqid, pending commits, and ack waiters. Durable state is external MDLog entries.

## Dependencies And Integration Points
Depends on bufferlists, rank ids, Ceph refs, `LogSegmentRef`, `MMDSTableRequest`, and `MDSRank`. Used by table-specific clients.

## Risks
Async raw pointers and contexts require careful lifetime. Ack waiters depend on eventual ACK journaling. Subclasses must implement resend/query/notify paths or recovery can hang.

## Test Signals
Fake subclass lifecycle tests plus integration coverage for prepare/commit, ack waiters, journal replay, failover, and resend.
