# sources/distributed-fs/lizardfs/src/master/itree.h

Purpose: declares the opaque C-style interval tree API.

Important APIs/types/functions: `itree_rebalance(void *)`, `itree_add_interval(void *, uint32_t, uint32_t, uint32_t)`, `itree_find(void *, uint32_t)`, and `itree_freeall(void *)`.

Control flow: callers keep the returned opaque pointer after add/rebalance calls and pass it back for lookups or freeing. Passing id zero to add deletes an interval.

State and persistence behavior: the tree is heap state hidden behind `void *`. No persistence.

Dependencies/integration: includes platform only; deliberately avoids exposing `itnode`.

Risks and test signals: type erasure means callers can pass invalid pointers without compile-time protection. Tests should include null roots and ensure callers always store returned roots after mutations.
