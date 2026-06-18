## sources/distributed-fs/openafs/src/libadmin/adminutil/afs_AdminInternal.h

Purpose: `afs_AdminInternal.h` defines private admin-library handle and iterator structures used by the OpenAFS admin APIs to manage tokens, cell connections, server-list cache state, and background RPC iteration.

Important types and APIs: `afs_token_handle_t` includes magic sentinels, validity flags, kernel/source flags, AFS and KAS token flags, security index, cell name, AFS/KAS tokens, arrays of rx security classes, client principal, and end magic. `afs_cell_handle_t` holds magic/valid/null flags, token handle, working cell, ubik clients for KAS/PTS/VOS, validity flags, VOS version flag, and cached server list with TTL. `afs_admin_iterator_t` contains magic/valid flags, mutex/condition variables, background worker thread, cache counters and queue indexes, termination/done flags, last status, RPC-specific data, and callback function pointers. It declares `IteratorInit`, `IteratorNext`, and `IteratorDone`.

Control flow and concurrency model: iterator comments require holding the iterator mutex while manipulating fields, except while making RPCs. The cache size is fixed at `CACHED_ITEMS` 5 and background workers coordinate producers/consumers through `add_item` and `remove_item` conditions.

State and persistence: all structures are in-memory runtime state. Magic constants `BEGIN_MAGIC` and `END_MAGIC` support handle validation and corruption detection.

Dependencies and integration points: includes cellconfig, auth/KTC token types, ubik clients, pthreads, and admin status types from public admin headers. It is the internal contract shared across admin util/client/KAS/PTS/VOS implementations.

Risks: structure fields expose raw pthread and ubik state, so lifecycle ordering is critical. Token handles own arrays of rx security class pointers that must be destroyed exactly once. Iterator callbacks must obey locking rules to avoid deadlocks or cache corruption.

Test signals: no direct tests in this subset. Signals come from admin API iterator tests and leak/race testing around `IteratorInit`/`IteratorNext`/`IteratorDone` under concurrent RPC workloads.
