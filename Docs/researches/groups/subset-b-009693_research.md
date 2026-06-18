# Research Group: subset-b-009693

This grouped report covers the requested NFS-Ganesha FSAL_PROXY_V4, FSAL_PSEUDO, and FSAL_RGW files. Each section preserves the source path and is bounded by the reconciliation markers required for splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/fsal_nfsv4_macros.h -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/fsal_nfsv4_macros.h

## Purpose
This header centralizes macros used by FSAL_PROXY_V4 to assemble NFSv4 and NFSv4.1 COMPOUND argument arrays. It keeps handle operations in `handle.c` concise by encapsulating repetitive `nfs_argop4` setup for session sequencing, filehandle selection, lookup, open, create, IO, setattr, link, remove, rename, readlink, commit, and legacy clientid/open-confirm forms.

## Important APIs, Types, and Functions
The exported surface is preprocessor macros rather than functions. Important macros include `COMPOUNDV4_ARG_ADD_OP_SEQUENCE`, `COMPOUNDV4_ARG_ADD_OP_CREATE_SESSION`, `COMPOUNDV4_ARG_ADD_OP_PUTROOTFH`, `COMPOUNDV4_ARG_ADD_OP_PUTFH`, `COMPOUNDV4_ARG_ADD_OP_LOOKUP`, `COMPOUNDV4_ARG_ADD_OP_GETFH`, `COMPOUNDV4_ARG_ADD_OP_GETATTR`, `COMPOUNDV4_ARGS_ADD_OP_OPEN_4_1`, `COMPOUNDV4_ARG_ADD_OP_MKDIR`, `COMPOUNDV4_ARG_ADD_OP_CREATE`, `COMPOUNDV4_ARG_ADD_OP_READ`, `COMPOUNDV4_ARG_ADD_OP_WRITE`, `COMPOUNDV4_ARG_ADD_OP_SETATTR`, and `COMPOUNDV4_ARG_ADD_OP_COMMIT`. `PRINT_HANDLE`, `TIMEOUTRPC`, and `ARRAY_SIZE` are small local utility definitions.

## Control Flow
Every macro assumes the caller owns an argument array and an operation counter. The macro writes the next `nfs_argop4` union arm, initializes selected fields, and increments the counter. Session sequencing is deliberately partial: slot id and sequence id are placeholders filled later by `proxyv4_compoundv4_execute` once a free RPC IO context is selected. Most name-taking macros store caller string pointers and lengths directly, so the referenced strings must remain valid through XDR encoding.

## State and Persistence Behavior
The header has no storage or persistence of its own. It mutates caller-provided stack arrays and embedded NFS union fields. For IO and setattr macros, stateids are copied into NFSv4 structures, with explicit all-zero stateless and all-ones bypass variants for selected operations.

## Dependencies and Integration Points
It depends on generated NFSv4 protocol types from `nfs4.h`, RPC/XDR definitions from `gsh_rpc.h`, and FSAL types from `fsal.h`. Its main consumer in this work item is `FSAL_PROXY_V4/handle.c`; the macros encode the wire-level operations that `proxyv4_nfsv4_call` sends over the proxy RPC connection.

## Risks
Because these are macros, arguments can be evaluated in-place without type checking, and many forms do not zero the whole operation union before writing selected fields. Several macros retain pointers to caller memory rather than copying payloads, making lifetime correctness the caller's responsibility. The write macro assigns `op->nfs_argop4_u.opread.stateid.seqid = 0` while constructing a write operation, which looks suspicious because the matching union member should be `opwrite`; this should be reviewed if write stateid sequencing is problematic.

## Test Signals
There are no direct unit tests for this header. Its signals are integration-level: proxy lookup, open, create, readdir, read/write, setattr, and session renewal succeeding against a remote NFSv4.1 server. Any XDR encode failure in `proxyv4_compoundv4_call` or unexpected NFS4ERR from backend operations would implicate these argument builders.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/fsal_nfsv4_macros.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle.c

## Purpose
This file implements the FSAL_PROXY_V4 object-handle and RPC bridge. It translates Ganesha FSAL object operations into NFSv4.1 COMPOUND calls against a remote NFS server, manages a shared TCP RPC connection, negotiates/renews NFSv4.1 client sessions, converts NFS attributes and errors to FSAL form, and constructs local proxy object handles from remote NFSv4 filehandles.

## Important APIs, Types, and Functions
Core private types are `struct proxyv4_rpc_io_context`, `struct proxyv4_handle_blob`, `struct proxyv4_obj_handle`, and `struct proxyv4_state`. Public/exported functions include `proxyv4_alloc_state`, `proxyv4_compoundv4_execute`, `proxyv4_init_rpc`, `proxyv4_close_thread`, `free_io_contexts`, `proxyv4_handle_ops_init`, `proxyv4_lookup_path`, `proxyv4_create_handle`, `proxyv4_get_dynamic_info`, and `proxyv4_wire_to_host`. Major FSAL object operations include lookup, mkdir, mknod, symlink, readlink, link, readdir, rename, getattrs, unlink, open2, read2, write2, close2, setattr2, commit2, handle-to-wire, and release.

## Control Flow
Initialization allocates `NB_RPC_SLOT` IO contexts and starts a receiver thread plus a clientid/session renewer. Callers build COMPOUND arrays using `fsal_nfsv4_macros.h`, then `proxyv4_compoundv4_execute` takes a free IO context, injects slot/sequence values into a leading `SEQUENCE`, sends the RPC through `proxyv4_compoundv4_call`, waits for `proxyv4_rpc_recv` to match the reply by XID, and returns the NFS status. Object methods follow a recurring pattern: get the active session id, add `SEQUENCE` and `PUTFH`, add the operation, optionally add `GETFH`/`GETATTR`, execute, convert errors through `nfsstat4_to_fsal`, and allocate or update an FSAL handle.

## State and Persistence Behavior
State is per export and per handle. The export owns RPC socket state, XID allocation, pending call list, free IO contexts, session id, client id, sequence id, and receiver/renewer threads protected by pthread mutexes and condition variables. Each proxy object stores the remote `nfs_fh4` copied into an inline `proxyv4_handle_blob`, plus optional NFSv3 digest mapping state when `PROXYV4_HANDLE_MAPPING` is enabled. Open state is held in `struct proxyv4_state` as a remote NFSv4 `stateid4`. Persistent state is limited to optional handle mapping through `HandleMap_SetFH`/`HandleMap_GetFH`; otherwise handles are reconstructed by asking the remote server for attributes.

## Dependencies and Integration Points
The file integrates with Ganesha FSAL core object/export ops, generated NFSv4 XDR routines, RPC auth-unix support, `op_ctx`, export manager state, conversion helpers such as `nfs4_Fattr_To_FSAL_attr` and `nfs4_FSALattr_To_Fattr`, and the optional handle mapping subsystem. `proxyv4_create_export` in `export.c` wires these functions into export ops and starts the RPC machinery, while `main.c` registers the module and initializes the handle ops vector.

## Risks
The receiver and sender share one TCP socket and rely on XID matching, condition variables, and reconnect signaling; races or missed wakeups would surface as timed-out or resent COMPOUND calls. Reply buffer sizes are bounded by configured send/receive sizes, and incorrect sizing can cause `E2BIG` or XDR decode failure. Several operations ignore parent pre/post attributes. `proxyv4_readdir` performs an extra lookup for every returned name, which is correct but expensive and may observe a changing directory. Open-state support is described in comments as incomplete; stateless close/status/reopen paths may not satisfy all upper-layer expectations. Path lookup rejects `..`, but intermediate symlinks fail by design rather than being followed.

## Test Signals
There are no direct tests in this subset. Useful signals are successful export startup, session negotiation through `EXCHANGE_ID`/`CREATE_SESSION`, lease renewal, remote lookup of `/`, correct maxread/maxwrite capping from backend attributes, NFSv3 handle round-trips when mapping is enabled, and FSAL operation success against a real NFSv4.1 server. Failures should be checked around RPC timeout/reconnect logs, NFS4ERR-to-FSAL translations, XDR encode/decode errors, and stale handle reconstruction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/CMakeLists.txt

## Purpose
This CMake file builds the optional PROXY_V4 handle mapping library and its two standalone test executables. The mapping library provides the persistent NFSv3 digest to NFSv4 proxy handle table used when `PROXYV4_HANDLE_MAPPING` is enabled.

## Important APIs, Types, and Functions
It defines `handlemapping_STAT_SRCS` as `handle_mapping.c`, `handle_mapping.h`, `handle_mapping_db.c`, `handle_mapping_db.h`, and `handle_mapping_internal.h`, then creates a static `handlemapping` library. It also defines `test_handle_mapping_db` from `test_handle_mapping_db.c` and `test_handle_mapping` from `test_handle_mapping.c`.

## Control Flow
The build flow is straightforward: compile the static library, apply sanitizer instrumentation, add LTTng generated-header dependencies when `USE_LTTNG` is set, then compile and link both test programs. Tests link against `handlemapping`, `hashtable`, `log`, `common_utils`, `rwlock`, and `sqlite3`.

## State and Persistence Behavior
The file does not persist runtime state. Its static library output is linked into consumers, and the test binaries operate on caller-supplied SQLite database directories when run.

## Dependencies and Integration Points
The build depends on the repository's hashtable/log/common utility libraries and SQLite. It is consumed by the higher-level FSAL_PROXY_V4 build only when handle mapping support is configured. The retained commented `Makefile.am` block documents older autotools linkage and helps validate the intended library/test membership.

## Risks
The CMake source list includes headers in the static library source variable, which is harmless but not necessary. The tests are built but there is no `add_test` registration here, so normal CTest execution may not run them automatically. The test source appears to use older function signatures than the current headers in places, which may indicate stale test coverage depending on surrounding compatibility macros.

## Test Signals
A successful build proves the handle mapping sources compile and link with SQLite and utility dependencies. Stronger signals require manually running `test_handle_mapping` or `test_handle_mapping_db` with a writable database directory and thread count.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/handle_mapping.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/handle_mapping.c

## Purpose
This file implements the in-memory front end for PROXY_V4's persistent handle map. It maps compact NFSv3-compatible digests, composed from object id and handle hash, to full proxy handle blobs that contain the underlying NFSv4 filehandle.

## Important APIs, Types, and Functions
The public API consists of `HandleMap_Init`, `HandleMap_GetFH`, `HandleMap_SetFH`, `HandleMap_DelFH`, and `HandleMap_Flush`. `handle_mapping_hash_add` is shared with the database loader through `handle_mapping_internal.h`. Private pool entries are `digest_pool_entry_t` for keys and `handle_pool_entry_t` for stored proxy handle data. The hash configuration supplies index, red-black-tree hash, compare, and display callbacks.

## Control Flow
`HandleMap_Init` validates the number of existing database files, initializes the database worker layer, creates memory pools, initializes the hashtable with the configured size, and reloads all persisted rows. `HandleMap_SetFH` first inserts into the hashtable without overwrite, then queues a database insert if the key was new. `HandleMap_GetFH` builds a temporary key, latches the hashtable entry, copies the stored handle into the caller buffer, and releases the latch. `HandleMap_DelFH` removes the hashtable entry, frees pooled key/value storage, and queues a database delete. `HandleMap_Flush` waits for database queues to drain.

## State and Persistence Behavior
The module owns global `handle_map_hash`, `digest_pool`, and `handle_pool` state. New mappings are immediately visible in memory and asynchronously persisted by `handle_mapping_db.c`. Deletes are removed from memory first and then queued to the database. Existing database rows are loaded into the hash during initialization, giving NFSv3 client handles continuity across server restarts.

## Dependencies and Integration Points
It depends on Ganesha's hashtable and pool APIs, FSAL logging, NFSv4 handle sizing, and the SQLite-backed database layer. `FSAL_PROXY_V4/handle.c` creates digests in `proxyv4_alloc_handle`, stores mappings through `HandleMap_SetFH`, and reconstructs NFSv4 handles in `proxyv4_wire_to_host` through `HandleMap_GetFH`.

## Risks
The code is global rather than per export, so multiple proxy exports with different handle-map configurations could collide or reinitialize shared state. `handle_mapping_hash_add` takes a `p_hash` parameter but inserts into the global `handle_map_hash`, so callers cannot truly target an alternate hash. Asynchronous DB persistence means a crash after in-memory insert but before flush can lose mappings and make issued NFSv3 handles stale. Digest uniqueness depends on object id plus a non-cryptographic handle hash; collisions return `HANDLEMAP_EXISTS` and may hide distinct handles.

## Test Signals
The companion `test_handle_mapping.c` is intended to initialize the map, insert 10,000 mappings, retrieve them, delete them, and flush. Runtime logs from reload counts, insert/retrieve/delete loops, stale returns for missing entries, and SQLite DB contents are the main validation signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/handle_mapping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/handle_mapping.h -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/handle_mapping.h

## Purpose
This public header defines the PROXY_V4 handle mapping API and wire digest format. It is the contract between the proxy object-handle code and the optional persistent mapping implementation.

## Important APIs, Types, and Functions
`handle_map_param_t` carries database directory, temp directory, database count, hashtable size, and synchronous-insert mode. `nfs23_map_handle_t` is the compact NFSv3-facing digest, with length, `PROXYV4_HANDLE_MAPPED` type marker, `handle_hash`, and `object_id`. The API functions are `HandleMap_Init`, `HandleMap_GetFH`, `HandleMap_SetFH`, `HandleMap_DelFH`, and `HandleMap_Flush`. Error constants range from `HANDLEMAP_SUCCESS` through stale, inconsistency, database, system, internal, invalid-parameter, hashtable, and exists outcomes.

## Control Flow
Consumers initialize the module with `HandleMap_Init`, call `HandleMap_SetFH` when a full proxy handle is created, use `HandleMap_GetFH` to expand an NFSv3 digest received from a client, call `HandleMap_DelFH` when a mapping should be removed, and call `HandleMap_Flush` before shutdown or durability-sensitive checkpoints.

## State and Persistence Behavior
The header describes persistent backing but does not implement it. The digest format is stable enough to be embedded in NFSv3 wire handles. `PROXYV4_HANDLE_MAXLEN` deliberately allows an NFSv4 filehandle plus the two-byte proxy handle blob prefix.

## Dependencies and Integration Points
It includes `fsal.h` for `struct gsh_buffdesc` and FSAL/NFS handle context. It is included by `proxyv4_fsal_methods.h` under `PROXYV4_HANDLE_MAPPING`, by `handle_mapping.c`, and by `handle_mapping_db.h`.

## Risks
The digest structure uses native integer fields, so cross-endian or ABI layout assumptions must be handled by the broader FSAL handle digest layer. The public parameter struct contains a `synchronous_insert` flag, but the database implementation currently only implements asynchronous insert behavior. Existing test code references older preallocation fields that are no longer present, indicating API drift risk.

## Test Signals
Compile-time inclusion under `PROXYV4_HANDLE_MAPPING`, successful proxy NFSv3 handle encoding/decoding, and the handle-mapping tests are the expected signals. Stale-handle behavior from `HandleMap_GetFH` is an important negative-path signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/handle_mapping.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/handle_mapping_db.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/handle_mapping_db.c

## Purpose
This file implements the SQLite persistence layer for PROXY_V4 handle mapping. It shards mappings across multiple SQLite database files, runs one worker thread per shard, reloads persisted handles into the in-memory hashtable, and asynchronously processes insert/delete requests.

## Important APIs, Types, and Functions
Public functions are `handlemap_db_count`, `handlemap_db_init`, `handlemap_db_reaload_all`, `handlemap_db_insert`, `handlemap_db_delete`, and `handlemap_db_flush`. `sscanmem` parses hex strings from SQLite back into binary handles and is exposed internally. Key private types include `db_op_item_t`, `flusher_queue_t`, and `db_thread_info_t`. Worker operations are `LOAD`, `INSERT`, and `DELETE`, with prepared statements for loading all rows, inserting one row, and deleting one row.

## Control Flow
`handlemap_db_init` records directories, validates `MAX_DB`, sets `sqlite3_temp_directory`, initializes per-thread queues and pools, and starts worker threads. Each worker opens `handlemap.sqlite.<index>`, creates the `HandleMap` table if absent, prepares SQL statements, then drains high-priority load/insert operations before lower-priority deletes. `handlemap_db_reaload_all` enqueues one load task per thread and waits for all queues to become idle. Inserts/deletes choose a queue via `select_db_queue`, allocate a task from that thread's pool, fill tuple data, and signal the worker. `handlemap_db_flush` waits for all queues and active work to finish.

## State and Persistence Behavior
Persistent rows live in SQLite files named with `DB_FILE_PREFIX` and a numeric suffix. The schema stores `ObjectId`, `HandleHash`, and a hex string `FSALHandle` with `(ObjectId, HandleHash)` as primary key. Queue state is in memory and protected by per-queue mutexes/conditions. Inserts are high-priority and asynchronous when `synchronous` is false; deletes are always asynchronous and lower priority. There is a `do_terminate` flag, but no public shutdown path in this file sets it or joins workers.

## Dependencies and Integration Points
The implementation depends on SQLite3, pthreads, directory scanning, `fnmatch`, Ganesha pool/logging utilities, and `handle_mapping_hash_add` from the in-memory layer. It is initialized by `HandleMap_Init` and receives persistence requests from `HandleMap_SetFH` and `HandleMap_DelFH`.

## Risks
Crash consistency is limited by async queues; callers must flush for stronger durability. The `synchronous_insert` parameter is stored but the synchronous branch is marked unsupported, so enabling it silently skips inserts. `handlemap_db_reaload_all(NULL)` in the DB-only test can pass a null hash to load operations, which is unsafe if rows exist. Worker errors inside operation processing are logged but not propagated to submitters after dequeue. There is no visible cleanup for prepared statements, SQLite handles, or worker threads in this subset.

## Test Signals
`test_handle_mapping_db.c` exercises count, init, reload, 10,000 insert requests, flush, 10,000 delete requests, and flush. Additional useful signals are database file count matching configured thread count, reload log counts, correct row creation/deletion in SQLite, and no queue stalls under concurrent workers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/handle_mapping_db.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/handle_mapping_db.h -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/handle_mapping_db.h

## Purpose
This internal header declares the SQLite-backed database layer for the PROXY_V4 handle map. It also defines the database filename prefix, table name, column names, and the maximum supported database shard count.

## Important APIs, Types, and Functions
Important constants are `DB_FILE_PREFIX`, `MAP_TABLE`, `OBJID_FIELD`, `HASH_FIELD`, `HANDLE_FIELD`, and `MAX_DB`. The API covers database counting, initialization, full reload into a hashtable, queued insert, queued delete, and flush.

## Control Flow
The intended sequence is count existing database files, initialize `db_count` worker threads and connections, reload all persisted mappings into a target hashtable, enqueue insert/delete mutations during runtime, and flush before shutdown or validation.

## State and Persistence Behavior
The header specifies how database state is named and sharded but does not own state. `MAX_DB` caps the number of SQLite worker/database instances at 32, while export configuration in `export.c` limits the common setting to a lower range.

## Dependencies and Integration Points
It includes `handle_mapping.h` for digest types and `hashtable.h` for reload targets. It is used by `handle_mapping.c`, `handle_mapping_db.c`, and both test programs.

## Risks
The function name `handlemap_db_reaload_all` contains a spelling error that is part of the ABI inside this subtree. Callers must pass a valid hashtable for reload in normal operation. Because this is an internal header, changes need synchronized updates across the mapping implementation and tests.

## Test Signals
Successful compilation of the mapping library and execution of the DB test are the main signals. Observing `handlemap.sqlite.<n>` files with the expected `HandleMap` schema validates the constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/handle_mapping_db.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/handle_mapping_internal.h -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/handle_mapping_internal.h

## Purpose
This small internal header shares helper declarations between the in-memory and database parts of handle mapping. It prevents the database loader from needing public access to private implementation details beyond the hash-add and hex-scan helpers.

## Important APIs, Types, and Functions
It declares `handle_mapping_hash_add`, which inserts a loaded mapping into a hash table, and `sscanmem`, which converts a hex string into binary memory.

## Control Flow
During database reload, `handle_mapping_db.c` reads each SQLite row, converts the stored hex handle with `sscanmem`, and calls `handle_mapping_hash_add` to repopulate the live map. Normal runtime inserts also use `handle_mapping_hash_add` through `HandleMap_SetFH`.

## State and Persistence Behavior
This header has no state. It exposes functions that mutate the global mapping hash and decode persistent row contents.

## Dependencies and Integration Points
It depends on `hashtable.h` and is included by both implementation files in `handle_mapping/`. It is intentionally narrower than the public `handle_mapping.h`.

## Risks
`handle_mapping_hash_add` accepts a `hash_table_t *` but the current implementation inserts into a global hash, so the declaration suggests more flexibility than actually exists. Any change to key/value pool layout must remain compatible with reload behavior.

## Test Signals
Reloading non-empty databases and seeing mappings become retrievable through `HandleMap_GetFH` validates both declarations indirectly. Bad hex rows exercise `sscanmem` error handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/handle_mapping_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/test_handle_mapping.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/test_handle_mapping.c

## Purpose
This standalone test/benchmark exercises the full handle mapping API: initialization, in-memory insertion, lookup, deletion, and database flush. It is intended to be run with a writable DB directory and a database thread count.

## Important APIs, Types, and Functions
The `main` function uses `HandleMap_Init`, `HandleMap_SetFH`, `HandleMap_GetFH`, `HandleMap_DelFH`, and `HandleMap_Flush`. It constructs `handle_map_param_t` and repeatedly populates `nfs23_map_handle_t` keys with synthetic object ids and hashes.

## Control Flow
The program initializes logging, validates `argc == 3`, parses the DB count, initializes the map, inserts 10,000 generated mappings, times the insertion loop, retrieves and deletes the same 10,000 mappings, flushes pending database work, logs timing, and exits nonzero on unexpected mapping errors.

## State and Persistence Behavior
The test writes mappings into the handle map and its SQLite backing store under the supplied directory, then deletes the same mappings and flushes. It uses `/tmp` as the SQLite temp directory. Key values vary with `time(NULL)`, so repeated runs generate different handle hashes and may interact with leftover rows.

## Dependencies and Integration Points
It depends on the handle mapping library, database layer header, Ganesha logging/memory helpers, and SQLite through the linked library. It is built by `handle_mapping/CMakeLists.txt`.

## Risks
The source appears stale relative to `handle_mapping.h`: it assigns removed fields such as `nb_handles_prealloc` and `nb_db_op_prealloc`, and calls `HandleMap_SetFH`/`HandleMap_GetFH` with fewer arguments than the current prototypes require. Unless compatibility macros exist outside this file, it may not compile. Even if corrected, it is a destructive benchmark against the supplied DB directory and should not be pointed at production handle-map storage.

## Test Signals
Useful signals are successful initialization, no unexpected errors during 10,000 set/get/delete operations, timing logs, and an empty or expected SQLite table after deletion and flush. Compile failures are themselves a signal of API drift in this subtree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/test_handle_mapping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/test_handle_mapping_db.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/test_handle_mapping_db.c

## Purpose
This standalone test/benchmark targets the lower-level SQLite database queue API directly. It measures sharded async insertion and deletion throughput without going through the public in-memory handle map.

## Important APIs, Types, and Functions
The `main` function calls `handlemap_db_count`, `handlemap_db_init`, `handlemap_db_reaload_all`, `handlemap_db_insert`, `handlemap_db_delete`, and `handlemap_db_flush`. It uses synthetic `nfs23_map_handle_t` keys and dummy `fsal_handle_t` payloads.

## Control Flow
The program validates DB directory and count arguments, initializes logging, counts existing DB shards, warns if the existing count differs, initializes DB workers, reloads all DB contents, submits 10,000 inserts, flushes, submits 10,000 deletes, flushes again, logs elapsed times, and exits on nonzero API returns.

## State and Persistence Behavior
It creates or updates `handlemap.sqlite.<n>` files in the supplied directory. Inserts and deletes are asynchronous until `handlemap_db_flush` waits for all queues to drain. The generated keys depend on current time, so stale rows from interrupted runs can remain unless explicitly deleted.

## Dependencies and Integration Points
It depends on `handle_mapping_db.h`, the DB implementation, logging helpers, pthreads, and SQLite. It is built by the local CMake file and is useful for validating DB queue behavior independently of hashtable lookup.

## Risks
The call `handlemap_db_init(dir, "/tmp", count, 1024, false)` does not match the current header signature, which takes four arguments after `tmp_dir`; unless hidden compatibility exists, this test is stale. `handlemap_db_reaload_all(NULL)` is unsafe if database rows exist because the loader attempts to insert rows into the provided hashtable. The test mutates persistent DB files and should use a scratch directory.

## Test Signals
Signals include successful DB shard counting, worker initialization, insert and delete timing logs, flush completion logs, and absence of SQLite errors. Compile-time signature mismatch is a strong maintenance signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/test_handle_mapping_db.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/main.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/main.c

## Purpose
This file is the module entry point and global configuration definition for FSAL_PROXY_V4. It declares the module object, default filesystem capabilities, module-level config items, registration/unregistration hooks, and handle-ops initialization.

## Important APIs, Types, and Functions
The global `PROXY_V4` is a `struct proxyv4_fsal_module` containing `fsal_module` and `handle_ops`. `proxyv4_params` defines module settings such as link/symlink support, `cansettime`, max read/write, umask, and export-path xdev authorization. `proxy_param_v4` is the config block. `proxyv4_init_config` loads and displays module config. `proxyv4_init` registers the FSAL and sets module ops. `proxyv4_unload` unregisters it.

## Control Flow
At module load, `proxyv4_init` calls `register_fsal`, installs `init_config` and `create_export`, then initializes the object-handle operation vector via `proxyv4_handle_ops_init`. Config loading later applies `proxy_param_v4` to the global module object and rejects non-harmless errors. On unload, `proxyv4_unload` unregisters the FSAL and logs failures to stderr.

## State and Persistence Behavior
State is the process-global `PROXY_V4` module object and its filesystem capability fields. No persistent storage is managed here. Export-specific runtime state, including RPC sessions and handle mapping, is created by `proxyv4_create_export` in `export.c`.

## Dependencies and Integration Points
It depends on FSAL registration APIs, config parsing, `proxyv4_fsal_methods.h`, and the handle implementation. It is the bridge that makes `handle.c` and export creation visible to Ganesha's FSAL loader.

## Risks
The config block is marked `CONFIG_UNIQUE`, reflecting that multiple module-level configurations are considered too risky. The default capability set advertises named attributes and ACL allow support even though `xattrs.c` returns not supported for extended-attribute operations; consumers need to rely on actual operation vectors as well as advertised info. Max read/write values are later validated against proxy RPC send/receive sizes in export config.

## Test Signals
Signals include successful FSAL registration under name `PROXY_V4`, valid config parsing, displayed fsinfo, initialized object ops, successful export creation, and clean unregister on module unload.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/proxyv4_fsal_methods.h -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/proxyv4_fsal_methods.h

## Purpose
This header defines the shared structures and function prototypes for FSAL_PROXY_V4. It is the internal contract between module registration, export creation, object-handle methods, RPC lifecycle management, xattr stubs, and optional handle mapping.

## Important APIs, Types, and Functions
Important types are `struct proxyv4_fsal_module`, `struct proxyv4_client_params`, `struct proxyv4_export_rpc`, and `struct proxyv4_export`. Constants define RPC header reserve and default IO size. Prototypes cover handle ops initialization, RPC lifecycle (`proxyv4_init_rpc`, `proxyv4_close_thread`, `free_io_contexts`), xattr operations, lookup/create-handle/dynamic-info/wire-to-host export methods, export creation, and state allocation.

## Control Flow
The module uses this header to share one type model: module init creates `PROXY_V4`, export creation fills `proxyv4_client_params` and `proxyv4_export_rpc`, handle operations use `op_ctx->fsal_export` to recover `struct proxyv4_export`, and xattr/export method vectors point to the declared functions.

## State and Persistence Behavior
The structures describe all major proxy export state. `proxyv4_client_params` stores remote server address, NFS program/port/sizes/timeouts, optional Kerberos fields, and optional handle-map parameters. `proxyv4_export_rpc` stores client/session ids, RPC socket/XID/pending calls, worker thread ids, and free IO contexts with locks/conditions. Persistence is only represented through `handle_map_param_t` when compiled with handle mapping.

## Dependencies and Integration Points
It depends on FSAL core types, pthreads, dirent, boolean support, and optionally `handle_mapping.h`. It is included by `main.c`, `export.c`, `handle.c`, and `xattrs.c`.

## Risks
The RPC state structure is concurrency-heavy and must remain consistent with initialization/destruction in `export.c` and `handle.c`. Optional Kerberos fields are compiled only under `_USE_GSSRPC` in export config but are always present in the struct. The `enable_handle_mapping` boolean is configured in export parsing, but `export.c` initializes `HandleMap_Init` unconditionally whenever `PROXYV4_HANDLE_MAPPING` is compiled, which may not honor the enable flag.

## Test Signals
Compile-time consistency across all proxy source files is the primary signal. Runtime export startup, thread creation, session establishment, and optional NFSv3 handle mapping validate that the structures are initialized and consumed coherently.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/proxyv4_fsal_methods.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/xattrs.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/xattrs.c

## Purpose
This file provides the FSAL_PROXY_V4 extended-attribute operation functions, all currently implemented as unsupported stubs. It satisfies expected symbols for the proxy FSAL without forwarding xattr operations to the remote NFSv4 server.

## Important APIs, Types, and Functions
Functions include `proxyv4_list_ext_attrs`, `proxyv4_getextattr_id_by_name`, `proxyv4_getextattr_value_by_name`, `proxyv4_getextattr_value_by_id`, `proxyv4_setextattr_value`, `proxyv4_setextattr_value_by_id`, `proxyv4_getextattr_attrs`, `proxyv4_remove_extattr_by_id`, and `proxyv4_remove_extattr_by_name`.

## Control Flow
Every function ignores its inputs and returns `fsalstat(ERR_FSAL_NOTSUPP, 0)`. There is no branching, allocation, or remote call path.

## State and Persistence Behavior
No state is read, mutated, cached, or persisted. No xattr changes can be made through this FSAL implementation.

## Dependencies and Integration Points
It includes FSAL core headers and `proxyv4_fsal_methods.h`, which declares these functions. Whether these stubs are installed into operation vectors depends on surrounding FSAL defaults and module capability wiring.

## Risks
`main.c` advertises `.named_attr = true`, while this file reports all xattr operations unsupported. That mismatch can confuse feature negotiation or clients expecting named attributes through proxy exports. Future real xattr support would need NFSv4 named-attribute or backend-specific behavior rather than simply toggling capability flags.

## Test Signals
Negative tests should observe `ERR_FSAL_NOTSUPP` for every xattr list/get/set/remove path. There are no positive xattr behavior signals in this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/xattrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PSEUDO/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PSEUDO/CMakeLists.txt

## Purpose
This CMake file builds the PSEUDO FSAL object library. PSEUDO provides an in-memory pseudo-filesystem used by Ganesha to represent namespace structure rather than a real backing filesystem.

## Important APIs, Types, and Functions
It adds `-D__USE_GNU`, sets `LIB_PREFIX`, defines `fsalpseudo_LIB_SRCS` as `handle.c`, `pseudofs_methods.h`, `main.c`, and `export.c`, and builds an OBJECT library named `fsalpseudo` with sanitizer support and `-fPIC`.

## Control Flow
The build compiles the PSEUDO handle, module, and export sources into object files for inclusion in the larger Ganesha build. When `USE_LTTNG` is enabled, it depends on generated trace headers and includes generated CMake file properties.

## State and Persistence Behavior
This file has no runtime state. It controls build artifacts only.

## Dependencies and Integration Points
It integrates the PSEUDO FSAL into the repository's CMake build and LTTng generation flow. The object library is expected to be consumed by the main server or FSAL aggregation target.

## Risks
The `LIB_PREFIX` variable is set but not used in this file. Because this is an OBJECT library, installation/export behavior is controlled elsewhere; missing higher-level linkage would make the FSAL unavailable despite local compilation.

## Test Signals
Successful compilation of `fsalpseudo` with sanitizers and optional LTTng dependencies is the main signal. Runtime behavior is validated through PSEUDO export and handle operations, not through this build file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PSEUDO/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PSEUDO/export.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PSEUDO/export.c

## Purpose
This file implements PSEUDO FSAL export operations. It creates and releases pseudo exports, provides static dynamic filesystem information, rejects quota operations, decodes pseudo wire handles for host endian, and wires export operation vectors to PSEUDO handle functions.

## Important APIs, Types, and Functions
Important functions are `release`, `get_dynamic_info`, `get_quota`, `set_quota`, `wire_to_host`, `pseudofs_export_ops_init`, and `pseudofs_create_export`. The export object type is `struct pseudofs_fsal_export` from `pseudofs_methods.h`.

## Control Flow
`pseudofs_create_export` allocates an export, initializes generic FSAL export state, installs PSEUDO export ops, attaches the export to the FSAL, records the current export path from `op_ctx`, and sets `op_ctx->fsal_export`. `release` frees the root handle if present, detaches the export, frees ops, path, and the export object. `wire_to_host` validates a minimal handle size and byte-swaps the hash key and length fields when client endian flags require it.

## State and Persistence Behavior
PSEUDO export state is in memory only: export path and root handle pointer. The root handle and all child pseudo handles are runtime objects; there is no disk persistence. Dynamic info always reports zero capacity/counts and a default time delta. Quotas are unsupported.

## Dependencies and Integration Points
It depends on FSAL common/config helpers, export manager context, `mdcache`, and PSEUDO handle functions. `pseudofs_create_export` is installed by `main.c`; `lookup_path`, `create_handle`, and handle serialization are implemented in `handle.c`.

## Risks
Release manually frees the root handle but child handle lifetime depends on handle release/unlink behavior, so leaks or stale live handles are possible if namespace teardown occurs with children still linked. `wire_to_host` only checks a one-byte minimum before reading a `uint64_t` and `ushort`, so malformed short buffers can be unsafe unless upper layers guarantee larger handle storage. Quota and capacity information are placeholders.

## Test Signals
Signals include successful pseudo export creation, root lookup, handle decode across endian flags, release without leaks, and expected `ERR_FSAL_NOTSUPP` for quota calls. Export update scenarios should see PSEUDO handle lookups return delay from `handle.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PSEUDO/export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PSEUDO/handle.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PSEUDO/handle.c

## Purpose
This file implements in-memory directory handles and object operations for FSAL_PSEUDO. It creates pseudo directory nodes, maintains parent/child AVL indexes, packages stable opaque handles from pseudo paths, supports lookup/readdir/mkdir/unlink/getattrs, and reconstructs handles by searching live FSAL handles.

## Important APIs, Types, and Functions
Important helpers include `package_pseudo_handle`, `create_fullpath`, `alloc_directory_handle`, AVL comparators, and `avltree_inline_name_lookup`. FSAL operations are `lookup`, `makedir`, `read_dirents`, `getattrs`, `file_unlink`, `handle_to_wire`, `handle_to_key`, `release`, `pseudofs_handle_ops_init`, `pseudofs_lookup_path`, and `pseudofs_create_handle`. Global `inode_number` generates pseudo file ids.

## Control Flow
Root lookup verifies the requested path equals the export path, lazily allocates the root handle, and returns it. `makedir` allocates a child directory, packages its handle from its full pseudo path, inserts it into the parent's name and index AVL trees under a write lock, assigns a cookie index, updates parent times, and increments parent link count. `lookup` searches the parent's name tree or returns the parent for `..`, with export-update delay handling. `read_dirents` walks the index AVL from the requested cookie and invokes the caller callback. `file_unlink` only removes empty directories, deletes AVL nodes, marks the child not in AVL, and updates parent metadata. `pseudofs_create_handle` scans the FSAL handle list for an identical opaque handle.

## State and Persistence Behavior
All namespace state is in memory. Each `pseudo_fsal_obj_handle` stores attributes, opaque handle bytes, parent pointer, child AVL trees, AVL nodes, directory index/cookie counters, link count, name, and `inavl` liveness flag. Handles are not persisted across restart; the opaque handle includes a CityHash64 of the full pseudo path, the path length, and as much path data as fits.

## Dependencies and Integration Points
It depends on FSAL common helpers, CityHash, NFS file handle sizing, display buffers, AVL trees, atomic counters, `op_ctx`, and export update state. It is wired into PSEUDO module/export ops by `pseudofs_handle_ops_init` and `pseudofs_export_ops_init`.

## Risks
Only directories are implemented; unsupported object types rely on default FSAL ops. `release` intentionally does not free live linked handles, so namespace lifetime is tied to unlink/export release behavior. `getattrs` copies attributes without broad locking beyond link count update. `pseudofs_create_handle` is O(number of live FSAL handles) and cannot reconstruct handles that are not currently resident, returning stale unless an export update is in progress. Handle uniqueness depends on hash plus truncated path content; collisions are unlikely but not impossible.

## Test Signals
Signals include correct root lookup, mkdir followed by lookup/readdir, stable cookies from index order, unlink returning `ERR_FSAL_NOTEMPTY` for non-empty directories, stale attributes after unlink, handle-to-wire/create-handle round trip for live handles, and delay responses during export updates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PSEUDO/handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PSEUDO/main.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PSEUDO/main.c

## Purpose
This file registers the PSEUDO FSAL module and defines its global filesystem capability defaults. PSEUDO is an in-memory directory-only namespace FSAL used to represent exported pseudo paths.

## Important APIs, Types, and Functions
The global `PSEUDOFS` contains the `fsal_module` and handle ops. `init_config` displays fsinfo and supported attributes. `unload_pseudo_fsal` unregisters the FSAL. `pseudo_fsal_init` registers the module as `PSEUDO`, installs export creation and unload ops, initializes handle ops, and displays config.

## Control Flow
At initialization, `pseudo_fsal_init` calls `register_fsal`, sets module operations, calls `pseudofs_handle_ops_init`, and logs fsinfo. On unload, `unload_pseudo_fsal` unregisters `PSEUDOFS.module`.

## State and Persistence Behavior
State is the process-global module object and capability flags such as no link/symlink/lock/named-attr support, POSIX attributes, max read/write sizes, and no pNFS. There is no persistent storage.

## Dependencies and Integration Points
It depends on FSAL init APIs, private FSAL declarations, and PSEUDO method declarations. `pseudofs_create_export` and `pseudofs_handle_ops_init` are provided by sibling files.

## Risks
There is no config parser here beyond displaying defaults, so all capability changes require code or higher-level defaults. Registration failures only print to stderr. The module advertises `cansettime = true`, but handle creation largely fixes metadata internally and only supports a narrow operation subset.

## Test Signals
Signals include successful registration as `PSEUDO`, initialized handle ops, displayed supported attributes, successful export creation, and clean unregister.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PSEUDO/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PSEUDO/pseudofs_methods.h -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PSEUDO/pseudofs_methods.h

## Purpose
This header defines PSEUDO FSAL shared types, supported attributes, object handle layout, and method prototypes. It is the internal contract between PSEUDO module, export, and handle implementations.

## Important APIs, Types, and Functions
It defines `PSEUDO_SUPPORTED_ATTRS`, `struct pseudo_fsal_module`, `struct pseudofs_fsal_export`, and `struct pseudo_fsal_obj_handle`. The object handle embeds FSAL public handle state, attributes, opaque handle pointer, parent pointer, name and index AVL trees/nodes, child index counters, link count, name, and liveness flag. It declares `pseudofs_lookup_path`, `pseudofs_create_handle`, `pseudofs_handle_ops_init`, and `pseudofs_create_export`. `pseudofs_unopenable_type` identifies socket, character, and block files as unopenable.

## Control Flow
The module creates a `pseudo_fsal_module`, exports allocate `pseudofs_fsal_export`, and handle operations allocate/manipulate `pseudo_fsal_obj_handle` instances. The inline unopenable helper is available to code that needs type-based open filtering, although this subset primarily implements directories.

## State and Persistence Behavior
The header describes in-memory state only. `root_handle` and child handles are process-local; no pseudo namespace persistence is defined.

## Dependencies and Integration Points
It includes AVL and list helpers, and depends on FSAL core types included by its consumers. It is included by all PSEUDO C files in this work item.

## Risks
The handle struct exposes many mutable fields directly across files, so synchronization discipline must be maintained by implementation code. Because the opaque handle is a pointer into memory allocated after the struct, allocation size assumptions in `handle.c` are part of the ABI. The root name is documented as a full path, unlike normal child names.

## Test Signals
Compile-time consistency across PSEUDO sources is the main header signal. Runtime mkdir/lookup/readdir/unlink and handle round-trips validate the struct layout and method contracts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PSEUDO/pseudofs_methods.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_RGW/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_RGW/CMakeLists.txt

## Purpose
This CMake file builds and installs the RGW FSAL module. RGW integrates Ganesha with Ceph RADOS Gateway through librgw/rgw_file.

## Important APIs, Types, and Functions
It defines `fsalrgw_LIB_SRCS` as `up.c`, `main.c`, `export.c`, `handle.c`, `internal.c`, and `internal.h`, adds RGW include directories, builds `fsalrgw` as a MODULE library, links it against `ganesha_nfsd`, `${RGW_LIBRARIES}`, `${SYSTEM_LIBRARIES}`, and `${LDFLAG_DISALLOW_UNDEF}`, sets module version `4.2.0`, and installs it to `${FSAL_DESTINATION}`.

## Control Flow
The build adds `_FILE_OFFSET_BITS=64`, compiles all RGW sources, applies sanitizer instrumentation, links with Ceph RGW and system libraries, then installs the loadable FSAL module.

## State and Persistence Behavior
This file has no runtime state. It controls build and installation artifacts.

## Dependencies and Integration Points
It depends on discovered `RGW_INCLUDE_DIR` and `RGW_LIBRARIES`, the main Ganesha daemon target, and FSAL installation settings. The message output helps diagnose include path selection during configuration.

## Risks
RGW library/API version mismatches will surface at compile or link time, with additional version checks in `internal.h`. Because undefined symbols are disallowed through linker flags, missing Ceph or Ganesha symbols should fail the build. Module build/install behavior assumes RGW support is enabled and dependencies are available.

## Test Signals
Successful CMake configure showing the RGW include dir, successful module link with no undefined symbols, and installed `fsalrgw` module are build-level signals. Runtime validation requires creating an RGW export.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_RGW/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_RGW/export.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_RGW/export.c

## Purpose
This file implements RGW FSAL export operations: export release, path lookup, wire-handle normalization, handle reconstruction, dynamic filesystem information, and export-op vector initialization. It adapts Ganesha FSAL calls to librgw/rgw_file handles.

## Important APIs, Types, and Functions
Important functions are `release`, `lookup_path`, `wire_to_host`, `create_handle`, `get_fs_dynamic_info`, and `export_ops_init`. It works with `struct rgw_export`, `struct rgw_handle`, `struct rgw_file_handle`, `struct rgw_fh_hk`, `struct rgw_statvfs`, and POSIX `struct stat`.

## Control Flow
`lookup_path` parses export paths into root, bucket, or bucket/global-directory forms, rejects trailing slash patterns, performs `rgw_lookup` for bucket and optional directory handles, verifies global-directory handles are not files, fetches attributes with `rgw_getattr`, normalizes fsid in the non-mount2 path, constructs an FSAL handle, and optionally returns POSIX-converted attributes. `wire_to_host` reduces accepted NFSv3/NFSv4 digest buffers to the RGW hash-key size. `create_handle` validates handle length, copies the hash key, calls `rgw_lookup_handle`, gets attributes, and constructs a handle. `get_fs_dynamic_info` calls `rgw_statfs` and maps RGW statvfs counters to FSAL dynamic info. `release` unmounts RGW, deconstructs the root handle, detaches the export, frees ops, and frees the export object.

## State and Persistence Behavior
Export state lives in `struct rgw_export`: mounted `rgw_fs`, root handle, RGW user/access/secret strings, and FSAL export state. Persistent object state is owned by the RGW backend; this file only creates runtime handle wrappers. Wire handles are compact `rgw_fh_hk` keys that can be looked up later through librgw.

## Dependencies and Integration Points
It depends on librgw/rgw_file APIs, FSAL common helpers, POSIX stat conversion, `internal.h`, and `rgw2fsal_error`/`construct_handle`/`deconstruct_handle` from sibling RGW implementation files. `main.c` creates exports and installs `export_ops_init`.

## Risks
`lookup_path` uses `strdup`/`strsep` for bucket splitting but does not free the duplicated path, which is a small leak on the global-directory branch. Some path parsing is ad hoc and rejects trailing slashes. In non-`USE_FSAL_RGW_MOUNT2`, lookup of a path returns root attributes for `global_dir == NULL`, which may be surprising for bucket paths. `release` asserts `rgw_umount` success, which can abort on unmount failure. Secrets are held in memory as plain strings configured by export creation.

## Test Signals
Signals include successful RGW mount followed by root/bucket/directory `lookup_path`, handle-to-wire/create-handle round trips via `rgw_lookup_handle`, accurate `rgw_statfs` mapping, correct stale/error conversion when lookup fails, and clean release/unmount.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_RGW/export.c -->
