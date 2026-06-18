<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/garbage.c -->
# sources/distributed-fs/ceph-client/net/unix/garbage.c

## Purpose
`garbage.c` implements garbage collection for AF_UNIX sockets passed through `SCM_RIGHTS`. It tracks in-flight Unix socket file descriptors as a directed graph and collects strongly connected components that are reachable only through their own queued file descriptors.

## Important APIs, Types, and Functions
- `struct unix_vertex` represents an in-flight Unix socket in the graph.
- `struct unix_edge` represents a passed Unix socket fd from predecessor to receiver.
- `unix_get_socket()` identifies AF_UNIX sockets from passed `struct file` objects.
- `unix_add_edges()`, `unix_del_edges()`, and `unix_update_edges()` maintain graph edges and per-user inflight counters as skbs are queued, removed, and accepted.
- `unix_prepare_fpl()`, `unix_destroy_fpl()`, and `unix_peek_fpl()` allocate graph metadata, tear it down, and invalidate GC decisions on `MSG_PEEK`.
- `unix_walk_scc()` and `__unix_walk_scc()` run iterative Tarjan SCC detection; `unix_walk_scc_fast()` rechecks known cyclic SCCs.
- `unix_gc()` collects dead SCC queues into a hitlist and purges them.
- `unix_schedule_gc()` decides when to queue or flush GC work.

## Control Flow
When AF_UNIX sends file descriptors, `unix_prepare_fpl()` allocates vertices/edges and schedules GC. When the skb is queued to a receiver, `unix_add_edges()` converts Unix socket files in the fd list into graph edges, updates receiver accounting, and increments `user->unix_inflight`. When the skb is consumed or destroyed, `unix_del_edges()` removes those edges and decrements counters. If graph state may be cyclic, `unix_gc()` walks SCCs under `unix_gc_lock`, decides whether each SCC is dead by checking outgoing edges and file reference counts, moves queued skbs from dead sockets/listener embryos to a hitlist, marks fd lists dead, and purges the hitlist outside the graph lock.

## State and Persistence
Global state includes `unix_gc_lock`, graph-state flags, unvisited/visited vertex lists, vertex index counters, cyclic SCC count, `gc_in_progress`, and a seqcount used to detect `MSG_PEEK` interference. Per fd-list state includes allocated vertices/edges, inflight/dead flags, owner user, and counts. Per socket state uses `unix_sock->vertex`, `listener`, and SCM stats.

## Dependencies and Integration Points
This file is tightly integrated with `af_unix.c` SCM accounting. It depends on `struct scm_fp_list`, socket files, skb queues, workqueues, TCP listen state values, and AF_UNIX listener embryo semantics. It also updates `user->unix_inflight`, which send-side limits read locklessly to enforce `RLIMIT_NOFILE`-based pressure.

## Risks and Edge Cases
Cycle collection is subtle. Embryo sockets are treated through their listener vertex because a listener indirectly holds embryo fd refs. `MSG_PEEK` can duplicate fd references while GC is in progress, so `unix_peek_seq` forces a later retry. Reference-count deadness requires `file_count == out_degree`; false positives would drop live sockets, and false negatives leak cycles. Locking must avoid holding the GC spinlock while freeing skbs because fd destruction can sleep or reenter socket logic.

## Test Signals
Stress tests should pass Unix sockets through each other to form self-cycles, multi-socket cycles, listener/embryo cycles, and non-cyclic chains; then close external references and verify GC frees only unreachable cycles. Include `MSG_PEEK` races, high inflight fd pressure, namespace teardown, accept after fd passing, and KASAN/refcount checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/garbage.c -->
