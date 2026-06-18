# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/l2t.h

## Purpose

`l2t.h` declares the Chelsio T3 offload Layer 2 Table data structures and helper API. It defines entry states, table/entry layout, skb ARP-failure callback storage, RCU accessor, TCB bitfield macros for the L2T index, function prototypes implemented in `l2t.c`, and fast inline send/hold/release helpers used by offload clients and redirect logic.

## Important APIs, types, and functions

- Entry states: `L2T_STATE_VALID`, `L2T_STATE_STALE`, `L2T_STATE_RESOLVING`, and `L2T_STATE_UNUSED`.
- `struct l2t_entry`: state, hardware index, IPv4 address, ifindex, SMT index, VLAN, neighbour pointer, hash bucket/chain links, pending ARP queue, entry lock, refcount, and destination MAC.
- `struct l2t_data`: number of entries, allocation rover, free count, table rwlock, RCU head, and flexible `l2tab[]`.
- `struct l2t_skb_cb` and `set_arp_failure_handler()` store an optional ARP failure callback in `skb->cb`.
- `L2DATA(cdev)` dereferences `t3cdev.l2opt` under RCU.
- TCB L2T index macros: `W_TCB_L2T_IX`, `S_TCB_L2T_IX`, `M_TCB_L2T_IX`, and `V_TCB_L2T_IX()`.
- Main functions: `t3_l2e_free()`, `t3_l2t_update()`, `t3_l2t_get()`, `t3_l2t_send_slow()`, `t3_init_l2t()`, and `cxgb3_ofld_send()`.
- Inline helpers: `l2t_send()`, `l2t_release()`, and `l2t_hold()`.

## Control flow

The header establishes the intended fast path: callers use `l2t_send()`, which sends immediately through `cxgb3_ofld_send()` when `e->state` is VALID and otherwise delegates to `t3_l2t_send_slow()`. References are managed with `l2t_hold()` on acquisition/reuse and `l2t_release()` on completion. `l2t_release()` enters an RCU read section, fetches current L2 data, decrements the entry refcount, and calls `t3_l2e_free()` when the refcount reaches zero and table data still exists.

## State and persistence behavior

The header defines volatile in-memory state only. L2T entries mirror hardware table entries but are not persistent. Lifetime is managed by atomic refcounts and RCU around the table pointer. The pending ARP queue is stored per entry as an skb queue and can hold offload packets until neighbour resolution completes or fails.

## Dependencies and integration points

It includes Linux spinlock and atomic definitions plus `t3cdev.h`. It forward-declares `struct neighbour` and `struct sk_buff`, and it is included by `cxgb3_offload.h`, `cxgb3_offload.c`, and `l2t.c`. Offload protocol clients use these declarations to bind connections to L2 entries and to release them safely.

## Risks and edge cases

- `l2t_send()` reads `e->state` without taking the entry lock for speed; state transitions must tolerate racing into the slow path.
- `l2t_release()` can call into free logic while only under RCU plus atomic refcount transition; table teardown must keep `l2t_data` alive through `call_rcu()`.
- `L2T_SKB_CB()` overlays `skb->cb`; callers must not conflict with other control-block users for the same skb.
- `l2t_hold()` decrements `nfree` only on a 0-to-1 transition; incorrect external refcount manipulation would corrupt free accounting.
- The flexible array uses `__counted_by(nentries)`, so compiler and allocation helpers must agree on the table length.

## Test signals

Build coverage should ensure all users agree on inline prototypes and that skb control block size is sufficient. Runtime tests should verify fast-path `l2t_send()`, slow-path delegation, hold/release free accounting, RCU teardown, ARP failure callback invocation, and lockdep-clean concurrent neighbour updates with active sends.
