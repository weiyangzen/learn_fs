<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/union_find.c -->
# sources/distributed-fs/ceph-client/lib/union_find.c

## Purpose
Disjoint-set union-find helpers implementing path compression and union by rank.

## APIs, Types, and Functions
Exports in-source functions `uf_find(struct uf_node *node)` and `uf_union(struct uf_node *node1, struct uf_node *node2)` as declared by `linux/union_find.h`.

## Control Flow, State, and Persistence
`uf_find()` follows parent pointers until a root whose parent is itself, compressing the path by making each visited node point to its grandparent. `uf_union()` finds both roots, returns if already equal, otherwise attaches the lower-rank root under the higher-rank root or increments rank when ranks are equal. Persistent state lives in caller-owned `struct uf_node` parent and rank fields.

## Dependencies and Integration
Depends on `linux/union_find.h`. It integrates with callers that initialize each node's parent to itself and maintain any required locking.

## Risks and Test Signals
Risks include no NULL checks, no internal synchronization, incorrect behavior if nodes are not initialized as singleton sets, and rank overflow only in extreme constructed cases. Test signals include singleton find, repeated union idempotence, rank tie behavior, path compression effects, and concurrent caller locking tests where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/union_find.c -->
