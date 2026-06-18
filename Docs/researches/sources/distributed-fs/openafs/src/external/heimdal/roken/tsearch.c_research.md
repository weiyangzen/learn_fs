# sources/distributed-fs/openafs/src/external/heimdal/roken/tsearch.c

## Purpose
Provides public-domain binary tree search APIs compatible with `tsearch`, `tfind`, `tdelete`, and `twalk` when the platform lacks them.

## Important APIs, Types, And Functions
Internal `node_t` stores a key pointer and left/right links. Exported functions are `rk_tsearch`, `rk_twalk`, `rk_tdelete`, and `rk_tfind`; `trecurse` implements traversal. `VISIT` values come from `search.h`.

## Control Flow
`rk_tsearch` walks the tree using the caller comparison function, returning an existing node on equality or allocating/linking a new node at the leaf. `rk_tfind` performs the same search without insertion. `rk_twalk` recursively calls the action callback in leaf/preorder/postorder/endorder order. `rk_tdelete` finds the target, splices replacement children or successor nodes, frees the removed node, and returns the parent pointer tracked during search.

## State And Persistence
The tree root and nodes live in caller-managed storage reachable through `void **rootp`. Nodes are heap allocated; keys are not copied or freed.

## Dependencies And Integration Points
`roken.h.in` maps standard tree-search names to these functions when native APIs are missing.

## Risks And Test Signals
The tree is unbalanced and can degrade to linear behavior or deep recursion. Key lifetime is the caller's responsibility. Tests should cover insertion, duplicate lookup, ordered traversal events, deleting leaf/one-child/two-child/root nodes, missing deletes, and compare-function correctness.
