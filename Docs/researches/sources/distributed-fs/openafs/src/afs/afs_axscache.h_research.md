# sources/distributed-fs/openafs/src/afs/afs_axscache.h

Purpose: Declares the access-cache entry type and fast macros used by cache-manager structures to cache access bits for recently checked users.

Important APIs and types: `struct axscache` contains `uid`, `axess`, and `next`. `afs_FindAxs(cachep,id)` checks the head entry inline and falls back to `afs_SlowFindAxs`. `axs_Front` moves a found node to the list front. `afs_AddAxs` allocates, fills, and prepends a new entry.

Control flow: The header has no standalone runtime path, but its macros mutate linked-list pointers and may evaluate arguments in ways callers must understand. `afs_FindAxs` explicitly requires a non-null list head and expects the caller to have checked that the cache pointer exists.

State and persistence: State lives in caller-owned linked lists plus the global allocator implemented in `afs_axscache.c`. There is no durable persistence.

Dependencies and integration points: Requires OpenAFS integer types and external implementations of `afs_SlowFindAxs` and `axs_Alloc`. It is integrated with vnode/access checks where parent structures serialize access-cache updates.

Risks: Macros hide allocation and pointer mutation, offer no null safety for `afs_FindAxs`, and rely on caller locks. The field name `axess` is historical and can obscure meaning. Because `afs_AddAxs` is a macro block without `do { } while (0)`, it is sensitive to use in conditional statements.

Test signals: Compile macro use in common conditional contexts, run null-head negative tests at call sites, verify cache-hit access bits are unchanged, and inspect list order after repeated `afs_FindAxs` and `afs_AddAxs` operations.
