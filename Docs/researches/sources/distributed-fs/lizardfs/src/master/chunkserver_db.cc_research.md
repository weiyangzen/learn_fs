# sources/distributed-fs/lizardfs/src/master/chunkserver_db.cc

Purpose: maintains master-side identity records for known chunkservers keyed by IP and port.

Important APIs/functions: free-list helper `get_free_element_list`, `acquireFreeIndex`, `releaseIndex`, `csdb_new_connection`, `csdb_lost_connection`, `csdb_chunkserver_list`, `csdb_remove_server`, and `csdb_find`.

Control flow: new connections either attach to a disconnected existing record or allocate a new 13-bit ID from `gIdToCSEntry` free list. Lost connections null the live pointer but keep the record. Removal is allowed only while disconnected and releases the ID. Listing returns live server data from `matocsserv_getserverdata` or a disconnected placeholder entry.

State and persistence: static unordered map from `(ip,port)` to `csdbentry` and global ID-to-entry array/free list. State is in-memory and reconstructed from chunkserver connections.

Dependencies and integration: depends on `matocsserv` for labels/server data and `ChunkserverListEntry`; chunk copy records in `chunks.cc` store `csid` values limited by `csdbentry::kMaxIdCount`.

Risks: ID 0 is reserved/free-list head; exhaustion returns failure. The unordered-map stores entries by value, and `gIdToCSEntry` points to those values, relying on unordered_map reference stability for elements.

Test signals: no direct tests in this subset; exercised by chunkserver connection integration.
