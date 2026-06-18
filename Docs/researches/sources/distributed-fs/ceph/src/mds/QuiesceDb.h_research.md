# sources/distributed-fs/ceph/src/mds/QuiesceDb.h

Purpose: defines the core quiesce database model: lifecycle states, relative-time versioning, client requests, replicated listings, root maps, peer acks, and callback interfaces used by the manager and agents.

Important APIs and types: `QuiesceState` is ordered intentionally so min/max aggregation reflects lifecycle. `QuiesceDbVersion` pairs membership epoch and set version. `QuiesceSet` holds members, state, timeout, expiration, and methods for requested/effective member state and next set state. `QuiesceDbRequest` encodes include/query, exclude/cancel, reset/release, optional conditional version, timeout/expiration changes, await, flags, and roots. `QuiesceDbListing` is the replicated set-centric DB update. `QuiesceMap` is the root-centric request/ack map used by agents. `QuiesceInterface` defines transport/control callbacks.

State and persistence: no manager storage is implemented here, but all persistent/replicated fields are defined here. Times are represented as database ages rather than absolute timestamps because MDS clocks are not synchronized. `RecordedQuiesceState` records both state and relative age of state transition.

Dependencies and integration: uses Ceph coarse real clock, CephFS types, `mdstypes.h`, STL containers, and generic callback types. `QuiesceDbManager`, `QuiesceAgent`, and MDS message wrappers include these types.

Risks and test signals: enum ordering is a semantic dependency; inserting states in the wrong place would break min/max aggregation. Request validity has subtle wildcard rules, and `Control` uses a union with `raw` for encoding. Tests should cover request validity, root include/exclude/reset semantics, state aggregation under release/quiesced rollback, TTL saturation, and database-age calculations across replicated listings.
