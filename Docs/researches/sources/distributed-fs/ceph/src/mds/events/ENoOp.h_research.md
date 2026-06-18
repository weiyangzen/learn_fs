# sources/distributed-fs/ceph/src/mds/events/ENoOp.h

Purpose: Declares a no-op journal event with optional padding size.

Important APIs/types: `ENoOp` stores `pad_size`, implements encode/decode, empty dump, and replay.

Control flow: Used to insert journal records that do not change metadata, potentially for padding or protocol progress. Replay should consume the event without metadata side effects.

State and persistence behavior: Persistent payload is padding size and any encoded padding performed by implementation.

Dependencies and integration points: Inherits `LogEvent`.

Risks: Padding decode must stay bounded and compatible; no-op records should not affect segment accounting unexpectedly.

Test signals: Encode/decode with zero and nonzero padding, replay no side effects.
