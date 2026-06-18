# sources/distributed-fs/ceph/src/mds/QuiesceDbEncoding.h

Purpose: provides Ceph bufferlist `encode()` and `decode()` functions for all quiesce DB wire/persistence structures.

Important APIs and behavior: each structure uses `ENCODE_START(1, 1)` / `DECODE_START(1)` for versioned encoding. Encoded types include `QuiesceDbVersion`, `QuiesceState`, `QuiesceTimeInterval`, `RecordedQuiesceState`, `QuiesceSet::MemberInfo`, `QuiesceSet`, `QuiesceDbRequest`, `QuiesceDbListing`, `QuiesceDbPeerListing`, `QuiesceMap::RootInfo`, `QuiesceMap`, and `QuiesceDbPeerAck`. `QuiesceState` is stored as `uint8_t`, guarded by a static assertion; durations are stored as raw clock counts.

State and persistence: this header defines the wire compatibility surface for quiesce manager messages and any persisted bufferlists. Field order is the compatibility contract: changing it requires a new encoding version and compatibility decode path.

Dependencies and integration: depends on `QuiesceDb.h` and Ceph `include/encoding.h`. Message classes such as quiesce DB listing/ack wrappers depend on these overloads to serialize peer replication and acks.

Risks and test signals: the decode for `RecordedQuiesceState` calls `decode(rstate.at_age, p)` while encode writes `rstate.at_age.count()`, relying on the overload for `QuiesceTimeInterval`. Tests should round-trip all quiesce structures, include optional request fields, empty/non-empty maps, unknown state byte handling expectations, and cross-version compatibility if versions are raised.
