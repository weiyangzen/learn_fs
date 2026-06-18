# sources/distributed-fs/ceph-client/drivers/interconnect/core.c

Purpose: central Linux interconnect framework implementation. It registers providers, stores topology nodes, resolves OF/name paths, aggregates consumer bandwidth requests, applies provider constraints, exposes debugfs summaries/graphs, and handles sync-state initial bandwidth floors.

Important APIs/types/functions: exports OF translation/get helpers, `icc_get()`, `icc_set_tag()`, `icc_set_bw()`, enable/disable/put, node create/destroy/link/add/remove helpers, provider init/register/deregister, `icc_std_aggregate()`, and `icc_sync_state()`.

Control flow: providers create nodes/links and register xlate callbacks. Consumers obtain paths through OF phandle pairs or names. `path_find()` breadth-first traverses links and `path_init()` attaches one `icc_req` per hop to node request lists. `icc_set_bw()` updates requests, reaggregates nodes, calls provider `set()`, and rolls back on failure.

State and persistence: global state is `icc_idr`, `icc_providers`, provider count, `synced_state`, locks, and debugfs dentries. Per-path `icc_req` entries persist until `icc_put()`.

Dependencies/integration: OF parsing, device sync-state, debugfs, tracepoints, provider callbacks, `internal.h`.

Risks and test signals: test lock ordering, missing-link traversal cleanup, provider `set()` rollback, dynamic IDs, active users during deregistration, sync-state floors, and debugfs during add/remove.
