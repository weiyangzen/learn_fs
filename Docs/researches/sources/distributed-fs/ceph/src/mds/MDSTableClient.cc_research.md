# sources/distributed-fs/ceph/src/mds/MDSTableClient.cc

## Purpose
Implements the client half of distributed MDS table mutation: prepare, agree, commit, ack, recovery reconstruction, and resend after table-server failover.

## Important APIs, Types, And Functions
`handle_request` processes query replies, notify prep, agree, ack, and server-ready. `_prepare` assigns or defers request ids and sends prepare. `commit` moves an agreed tid to pending commit and sends commit. Recovery helpers include `got_journaled_agree`, `got_journaled_ack`, `resend_commits`, `resend_prepares`, and `handle_mds_failure`.

## Control Flow
Messages before resolve may be deferred. Prepares wait until `SERVER_READY` supplies a base request id. `AGREE` completes the caller and records tid-to-reqid. `commit` marks the log segment pending, calls `notify_commit`, and sends commit if possible. `ACK` removes pending state and journals an `ETableClient` ACK before waking waiters.

## State And Persistence Behavior
Runtime maps track pending prepares, prepared updates, waiting prepares, pending commits, and ack waiters. Durable recovery state comes from MDLog table-client entries, not this class directly.

## Dependencies And Integration Points
Depends on MDSRank, MDSMap tableserver lookup, MMDSTableRequest, MDLog, LogSegment, ETableClient, retry contexts, and subclass hooks. SnapClient is the primary consumer here.

## Risks
Raw output pointers passed to `_prepare` must outlive async completion. Idempotent resend depends on reqid/tid mapping. Stray agree/ack paths are recovery-sensitive. Missing server-ready stalls deferred prepares.

## Test Signals
Prepare before/after ready, agree completion, duplicate/stray agree, rollback sends, commit resend, ACK journaling/waiter wake, journaled agree/ack replay, and tableserver failure readiness clearing.
