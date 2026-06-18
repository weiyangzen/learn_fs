# sources/distributed-fs/lizardfs/src/master/chunkserver_db.h

Purpose: declares chunkserver database structures and lookup/connection APIs.

Important APIs/types/functions: `csdbentry` with `kMaxIdCount = 8192`, live `matocsserventry *eptr`, `csid`, and `MediaLabel`; global `gIdToCSEntry`; `csdb_new_connection`, `csdb_lost_connection`, `csdb_chunkserver_list`, `csdb_remove_server`, `csdb_find(ip,port)`, and inline `csdb_find(id)`.

Control flow: consumers register, mark disconnected, list, remove, or find chunkserver records.

State and persistence: state owned by `chunkserver_db.cc`; no on-disk persistence.

Dependencies and integration: includes media labels and protocol chunkserver list entries; used heavily by `chunks.cc` and `matocsserv`.

Risks: `csdb_find(id)` asserts bounds but can return null for free IDs; callers must handle disconnected entries where `eptr` is null.

Test signals: no direct tests in this subset.
