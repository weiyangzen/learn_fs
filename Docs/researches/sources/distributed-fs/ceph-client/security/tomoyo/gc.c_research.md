# sources/distributed-fs/ceph-client/security/tomoyo/gc.c

## Purpose

`gc.c` reclaims deleted TOMOYO policy objects and closed securityfs I/O buffers. It implements deferred cleanup for entries protected by SRCU readers, active securityfs cursors, shared reference counts, and task security blobs.

## Important APIs, types, and functions

`tomoyo_notify_gc()` is the exported registration/unregistration hook used by securityfs open/close paths. `tomoyo_del_condition()` releases all references held by a packed `struct tomoyo_condition`. Internal cleanup helpers release object-specific references for transition controls, aggregators, managers, ACLs, domains, names, groups, and group members. `tomoyo_try_to_gc()` is the central removal/reinject/free path. `tomoyo_collect_entry()` scans all domains, namespaces, conditions, groups, and interned names. `tomoyo_gc_thread()` runs collection from a kernel thread.

## Control flow

Policy deletion only marks entries as deleted. The collector later takes `tomoyo_policy_lock`, finds deleted or unreferenced objects, marks them `TOMOYO_GC_IN_PROGRESS`, unlinks them, drops the policy lock, waits for an SRCU grace period, checks whether securityfs readers/writers still hold list cursors or queued string pointers, releases object-specific references, then frees memory and subtracts from TOMOYO policy memory usage. If an entry is still visible to an I/O buffer or active task reference, it is reinserted at its previous list position.

`tomoyo_notify_gc()` adds open `tomoyo_io_buffer` objects to a protected list with a users count. On close it either frees the buffer immediately or, if writes occurred and cleanup may be needed, starts `tomoyo_gc_thread()`. The GC thread serializes itself with `tomoyo_gc_mutex`, collects policy entries, then frees any I/O buffers whose temporary users count reached zero.

## State and persistence behavior

The file maintains `tomoyo_io_buffer_list` under `tomoyo_io_buffer_list_lock`. It mutates global policy lists, shared reference counts, `is_deleted` markers, `TOMOYO_GC_IN_PROGRESS` states, and `tomoyo_memory_used[TOMOYO_MEMORY_POLICY]`. It intentionally delays freeing objects that remain reachable through securityfs read cursors, write-domain selections, queued read strings, condition/group/name references, or domain task references.

## Dependencies and integration points

GC relies on the object layouts declared in `common.h`, reference drop helpers from other files, `tomoyo_policy_lock`, `tomoyo_ss`, namespace/domain/name/group/condition lists, and Linux kthreads, spinlocks, mutexes, and SRCU. `common.c` calls `tomoyo_notify_gc()` when opening and closing control files. Update paths in `domain.c` and related parsers mark entries deleted rather than freeing directly.

## Risks

The main risk is use-after-free through partial securityfs reads, active write selections, or task domain pointers. `tomoyo_struct_used_by_io_buffer()` inspects `&head->w.domain->list`; if a writer buffer ever has a NULL domain while this expression is evaluated, that path must be protected by call context or it could fault. Reinjecting after failed reclamation depends on the saved list linkage remaining valid enough for `list_add_rcu(element, element->prev)`. Reference drops must match parser ownership exactly or GC can leak shared names/groups/conditions.

## Test signals

Useful tests include deleting policy while a reader is paused mid-read, deleting a selected domain while a writer is open, closing writers to trigger GC, deleting domains still referenced by tasks, removing group members and then groups, condition dedup/refcount release, repeated create/delete cycles with memory usage returning to baseline, and KASAN/RCU torture runs for concurrent readers and GC.
