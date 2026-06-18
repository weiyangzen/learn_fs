# sources/distributed-fs/ceph/src/mds/events/ETableClient.h

Purpose: Declares journal records for client-side table operations.

Important APIs/types: `ETableClient` stores table id, operation, and tid. It prints table and operation names through `get_mdstable_name` and `get_mdstableserver_opname`, and implements encode/decode/dump/test/replay.

Control flow: Table clients journal prepare/commit/rollback progress so replay can resume table transactions.

State and persistence behavior: Persistent payload is table/op/tid. The table-specific mutation payload is handled elsewhere by table server or metablob records.

Dependencies and integration points: Depends on `mds_table_types`, `LogEvent`, and `MDSTableClient` replay logic.

Risks: Wrong table/op names are diagnostic only, but wrong tid breaks transaction recovery.

Test signals: Replay table client op sequences for snap/inotable/session-related tables and dencoder coverage.
