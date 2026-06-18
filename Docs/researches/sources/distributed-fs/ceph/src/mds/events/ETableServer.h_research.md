# sources/distributed-fs/ceph/src/mds/events/ETableServer.h

Purpose: Declares journal records for authoritative table-server operations and mutations.

Important APIs/types: `ETableServer` stores table id, operation, request id, source MDS, mutation buffer, tid, and table version. It implements encode/decode/dump/test/update_segment/replay.

Control flow: Table-server prepare/commit/rollback/update events persist distributed table mutations. Replay applies table operation, request id, source rank, tid, and version to the appropriate `MDSTableServer`.

State and persistence behavior: Persistent payload includes both transaction metadata and opaque table mutation buffer. `update_segment()` accounts table transactions for log trimming.

Dependencies and integration points: Depends on `mds_table_types`, `LogEvent`, `MDSTableServer`, and specific tables such as snapshot server.

Risks: Mutation buffer schema is table-specific; mismatched table/op decoding can corrupt table state. Version must remain monotonic.

Test signals: Snap table server prepare/commit/rollback replay, server update replay, request deduplication by reqid/bymds, and dencoder tests.
