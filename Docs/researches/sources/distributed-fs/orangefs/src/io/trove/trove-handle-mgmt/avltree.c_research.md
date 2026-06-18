# sources/distributed-fs/orangefs/src/io/trove/trove-handle-mgmt/avltree.c

## Purpose
Implements a generic AVL tree used by OrangeFS handle-management code, with insert, remove, lookup, highest-key lookup, and traversal operations parameterized by macros from the including type definitions.

## Important APIs, Types, And Functions
Public functions are `avlinsert`, `avlremove`, `avlaccess`, optional `avlaltaccess`, `avlgethighest`, `avldepthfirst`, and `avlpostorder`. Internal helpers perform left/right rotations, insertion rebalance (`avlleftgrown`, `avlrightgrown`), deletion rebalance (`avlleftshrunk`, `avlrightshrunk`), and replacement by highest/lowest subtree node.

## Control Flow
Insertion recursively descends by `AVLKEY(d)`, allocates a new node on an empty subtree, and propagates `BALANCE` upward to trigger rotations and skew updates. Removal recursively descends by key, replaces two-child nodes with predecessor or successor data, frees removed node data through `free`, and rebalances as subtrees shrink. Accessors recursively search by primary or alternate key. Traversals call worker callbacks in sorted depth-first or post-order order.

## State And Persistence
State is an in-memory tree of `struct avlnode` instances. The implementation owns node allocations and frees `AVLDATUM` payloads during replacement/removal, so callers must provide heap-owned compatible payloads. No disk persistence occurs.

## Dependencies And Integration Points
Includes `trove-extentlist.h` before `avltree.h`, which supplies `AVLDATUM`, `AVLKEY_TYPE`, `AVLKEY`, and possibly `AVLALTKEY`. It is compiled with handle-management sources and likely backs extent/free-handle ledgers.

## Risks And Test Signals
Risks include recursive depth under corrupted trees, payload ownership assumptions (`free(d)`), duplicate-key insert returning `ERROR` without freeing caller payload, alternate-key search only valid if tree ordering matches the alternate key, and balancing correctness after complex deletes. Tests should insert ascending/descending/random ranges, reject duplicates, remove leaves/one-child/two-child/root nodes, verify sorted traversal and height bounds, validate highest lookup, and run leak checks around failed inserts/removals.
