# sources/distributed-fs/ceph/src/mds/MDSTableServer.cc

## Purpose
Implements server-side distributed MDS table mutation. It journals prepare/commit/rollback/server-update operations, applies subclass table changes after logging, handles notification gathers, and recovers pending prepares.

## Important APIs, Types, And Functions
`handle_request` routes table requests. `_note_prepare`, `_note_commit`, `_note_rollback`, and `_note_server_update` mutate version/pending state. `handle_prepare` and `_prepare_logged` journal and apply prepare, then send or delay `AGREE`. `handle_commit` and `_commit_logged` journal/apply commit and send `ACK`. Recovery uses `finish_recovery`, `_do_server_recovery`, `handle_mds_recovery`, and `handle_mds_failure_or_stop`.

## Control Flow
Prepare logs before applying `_prepare`. Optional `_notify_prep` holds the agree reply until active clients send notify ACKs. Commit is guarded by `committing_tids`; already committed tids get immediate ACK. Recovery resends agrees for pending tids and sends `SERVER_READY` with next reqids.

## State And Persistence Behavior
Encoded state is subclass server state plus `pending_for_mds`. Runtime state includes `active_clients`, `recovered`, `committing_tids`, and `pending_notifies`. Every mutation advances `version`; replay also updates `projected_version`.

## Dependencies And Integration Points
Depends on MDSRank, MDLog, ETableServer, MMDSTableRequest, and subclass hooks. SnapServer is the main table-server user in this subset.

## Risks
Journal-before-reply ordering is essential. Notify gathers can delay clients until failure handling prunes peers. Rollback and impossible commit states assert. Recovery reqid calculation must prevent reuse hazards.

## Test Signals
Prepare/agree, notify gather, commit/ack, duplicate commit, already committed ACK, rollback, server update, encode/decode pending state, recovery resend/server-ready, peer recovery, and failure-stop notify cleanup.
