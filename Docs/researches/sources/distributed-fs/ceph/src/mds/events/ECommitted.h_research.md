# sources/distributed-fs/ceph/src/mds/events/ECommitted.h

Purpose: Declares a journal event recording that a metadata request identified by `metareqid_t` has committed.

Important APIs/types: `ECommitted` stores `reqid`, implements print/encode/decode/dump/test-instance generation, and replays against `MDSRank`. `update_segment()` is intentionally empty.

Control flow: The event is emitted after a peer or client metadata request reaches committed state; replay can mark the request committed/idempotent without replaying metadata changes from this event itself.

State and persistence behavior: Persistent payload is only the request id. Segment accounting is not updated here, making it a marker/control event rather than metadata payload.

Dependencies and integration points: Inherits `LogEvent`, includes `EMetaBlob` for related metadata event context, and integrates with mdlog replay.

Risks: Request id correctness matters for duplicate suppression. If replay semantics diverge from request tracking, unsafe requests may be retried incorrectly.

Test signals: Encode/decode and replay idempotency around duplicate client/peer requests.
