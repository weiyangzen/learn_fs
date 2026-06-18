# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_list_set.c

## Purpose

`ip_set_list_set.c` implements `list:set`, an ipset type whose elements are references to other ipsets. Packet operations walk the member sets in order and delegate add/delete/test to them. Userspace operations manage ordered membership, optional before/after placement, timeouts, and per-element extensions.

## Important APIs, types, and functions

`struct set_elem` is the RCU-protected list node storing the referenced set pointer, referenced set id, list head, and RCU head. `struct set_adt_elem` carries userspace add/delete/test input: target id, reference id, and before/after mode. `struct list_set` stores configured size, timeout GC timer, owning set, net namespace, and `members` list. Packet functions `list_set_ktest()`, `list_set_kadd()`, and `list_set_kdel()` iterate member sets and call `ip_set_test/add/del`. Userspace helpers `list_set_uadd()`, `list_set_udel()`, and `list_set_utest()` implement ordered membership semantics. `list_set_del()`, `list_set_replace()`, and `__list_set_del_rcu()` manage RCU deletion and reference release. `list_set_gc()` periodically removes expired elements.

## Control flow

Packet `kadt` takes an RCU read lock, builds kernel extensions, and dispatches by ADT. Test clears sub-counter matching flags to avoid unwanted nested counter lookup, then returns success only if a member set matches and the list element's own extensions match. Add/delete walk members until a sub-operation succeeds. Userspace `uadt` resolves `IPSET_ATTR_NAME` and optional `NAMEREF` to set ids, rejects loops by refusing member sets whose type has `IPSET_TYPE_NAME`, performs timeout cleanup before mutating timed lists, calls the variant ADT function, then drops references on error or non-add paths. Create initializes the list object, sets lockdep class, computes element size with extensions, and starts GC when timeout is configured.

## State and persistence behavior

Persistent state is the ordered RCU list of referenced set ids, per-element extensions, references held on member sets, optional timeout values, and the GC timer. Deletion and replacement release referenced set ids and free nodes after an RCU grace period. `flush` removes all members and extension size accounting. `cancel_gc` stops the timer and flushes references before destroy.

## Dependencies and integration points

The file depends on ipset core reference management, list extension helpers, RCU lists, net namespace lookup, timers, and netlink policies. It integrates deeply with other ipset types because every member operation delegates to `ip_set_test/add/del` by id. The registered type advertises `IPSET_TYPE_NAME | IPSET_DUMP_LAST`.

## Risks

Ordered before/after semantics are subtle, especially with expired entries skipped during lookup and possible replacement of timed-out slots. Reference management must pair every `ip_set_get_byname()` with `ip_set_put_byindex()` on all error paths. Packet add/delete semantics stop after the first successful member operation, which may hide later member failures. Loop detection prevents nested `list:set`, but only by checking `IPSET_TYPE_NAME`.

## Test signals

Tests should cover append, before, after, delete with reference constraints, duplicate add with and without `-exist`, timeout expiration and GC, flush/destroy reference release, packet test/add/delete delegation order, loop rejection, list dump pagination, counter/comment/skbinfo extensions on list elements, and namespace cleanup.
