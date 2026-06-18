# sources/distributed-fs/ceph-client/security/selinux/ss/sidtab.c

## Purpose
`sidtab.c` implements SELinux SID-to-context and context-to-SID storage. It supports fast lock-free SID lookup, reverse context lookup, initial SID storage, dynamic SID allocation, optional SID-to-string caching, and live SID table conversion during policy reload.

## Important APIs, Types, and Functions
Main APIs are `sidtab_init()`, `sidtab_set_initial()`, `sidtab_search_entry()`, `sidtab_search_entry_force()`, `sidtab_context_to_sid()`, `sidtab_convert()`, `sidtab_cancel_convert()`, `sidtab_freeze_begin()`, `sidtab_freeze_end()`, `sidtab_destroy()`, `sidtab_hash_stats()`, and optional `sidtab_sid2str_get()/put()`. Internal helpers implement the tree allocator/lookup (`sidtab_do_lookup()`), reverse hash lookup (`context_to_sid()`), conversion traversal, and cache eviction.

## Control Flow
Initial SIDs are copied into fixed `isids[]` entries and optionally entered into the reverse hash. Dynamic SIDs are indexed after `SECINITSID_NUM`; lookup reads `count` with acquire semantics before walking the tree. `sidtab_context_to_sid()` first tries an RCU reverse-hash lookup, then locks, retries, rejects inserts if frozen, allocates the next tree entry, copies the context, mirrors it into a conversion target if a policy load is active, publishes `count` with release semantics, and inserts into the reverse hash. `sidtab_convert()` freezes the conversion snapshot count, enables live conversion for newly inserted entries, converts existing tree entries outside the lock, then builds the target reverse hash.

## State and Persistence
The sidtab is in-memory runtime state, not directly serialized. It persists across policy reloads by converting contexts from the old policy to the new policy. Invalid/unmapped contexts can be retained as strings in `struct context`, and force lookups can return them.

## Dependencies and Integration Points
It depends on `context` helpers for equality, copy, destroy, and hashing; `services_convert_context()` for policy reload conversion; SELinux initial SID constants; RCU hash/list APIs; and spinlocks for writers. `services.c` performs all high-level SID/context operations through this table.

## Risks
Key risks are publish-order races around `count`, stale inserts during policy switch, conversion target consistency, hash duplicates, and cache lifetime under RCU. `sidtab_convert()` assumes no concurrent policy loads and needs correct rollback through `sidtab_cancel_convert()` on failure.

## Test Signals
Stress tests should perform concurrent `security_context_to_sid()` while reloading policy, validate `-ESTALE` retry paths, check duplicate initial SID contexts, verify fallback to unlabeled for missing SIDs, run SID-to-context cache LRU tests when enabled, and monitor hash stats under large label sets.
