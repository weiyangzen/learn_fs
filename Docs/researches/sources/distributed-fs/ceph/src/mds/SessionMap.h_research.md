# sources/distributed-fs/ceph/src/mds/SessionMap.h

Purpose: Defines `Session`, `SessionFilter`, `SessionMapStore`, and `SessionMap`, the core in-memory and durable representation of client/MDS sessions.

Important APIs/types: `Session` exposes state transitions (`STATE_CLOSED`, `OPENING`, `OPEN`, `CLOSING`, `STALE`, `KILLING`), preallocated inode delegation, completed request/flush tracking, cap/lease LRU lists, recall counters, access checks, and connection metadata. `SessionMapStore` provides encode/decode/dump for session state outside a live MDS. `SessionMap` adds live indices, load/save, version projection/commit, replay helpers, perf counters, and dirty writeback.

Control flow: A session begins closed, moves through open/opening/stale/closing/killing, and can have an independent `importing_count`. `SessionMap::mark_projected()` advances a projected version and stores it on the session; `mark_dirty()` later advances committed sessionmap version and pops the expected projection. `SessionFilter` parses admin-socket style selectors by id, state, auth name, metadata, or reconnecting status.

State and persistence behavior: `session_info_t info` is the durable session payload, including inst, metadata, completed requests, flushes, and preallocated inos. Ephemeral fields include connection, request list, cap/lease LRU, decay counters, waiters, and `human_name`. `SessionMap` tracks `by_state`, `dirty_sessions`, `null_sessions`, `commit_waiters`, `waiting_for_load`, and average birth time.

Dependencies and integration points: Depends on Ceph entity/session types, `interval_set`, `MDSAuthCaps`, `DecayCounter`, `Message`, `Mutation`, and MDS context/gather helpers. It is consumed by `Server`, journal replay events (`ESession`, `ESessions`, `EMetaBlob` inode allocation fields), reconnect, cap recall, and admin session operations.

Risks: Refcount/list invariants are strict; the destructor asserts the session is off state lists. Preallocated inode intervals must remain consistent across `pending_prealloc_inos`, `free_prealloc_inos`, `delegated_inos`, and durable `info.prealloc_inos`. Completed request trimming controls idempotency; premature trimming can duplicate client operations.

Test signals: Unit/dencoder coverage should include session encode/decode, state names, dirty completed request flags, prealloc delegation/take paths, projected-version asserts, filter parsing, and `SessionMapStore::generate_test_instances`.
