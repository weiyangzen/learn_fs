# sources/distributed-fs/coda/coda-src/venus/mariner.h

Purpose: declares the Mariner facility public functions and the `mariner` vproc class used for monitoring/control clients.

Important APIs and types: public functions initialize listeners, accept mux callbacks, broadcast fetch logs/path reports/volume state, and print active mariners. `qentry` stores queued output buffers. `mariner` inherits `vproc`, owns a writer LWP, fixed output queue, state flags for logging/reporting/volume-state subscriptions, uid filter, socket fd, command buffer, optional `plan9server`, and helpers for LWP-aware non-blocking reads/writes, request parsing, resignation, path/fid/rpc2 stats, and queued writing. `mariner_iterator` filters `vproc_iterator` to active Mariner vprocs.

State and persistence: all declared state is transient connection state; no RVM persistence is involved.

Dependencies and integration: depends on `vproc`, Venus fids, volume flags, Plan 9 server forward declaration, and C stdio. Friend declarations expose internals to accept callbacks, broadcast functions, kernel replace handling, and queue writer glue.

Risks and test signals: risks include private ownership/lifetime of queued buffers, friend-heavy access, fixed queue length, and vproc/thread lifecycle coupling. Tests should compile all friend users, iterate active clients, verify subscription flags, and confirm queue writer shutdown through EOF sentinel.
