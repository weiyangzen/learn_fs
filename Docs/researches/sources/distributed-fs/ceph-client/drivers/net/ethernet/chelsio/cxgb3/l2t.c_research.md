# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/l2t.c

## Purpose

`l2t.c` implements the Chelsio T3 Layer 2 Table used by offload connections to map next-hop IPv4 neighbours to hardware L2 table indices. It allocates and reuses L2T entries, tracks neighbour MAC/VLAN/SMT state, queues offload packets while ARP/neighbor resolution is pending, emits `CPL_L2T_WRITE_REQ` firmware work requests, and updates entries on kernel neighbour events.

## Important APIs, types, and functions

- `t3_init_l2t()` allocates a flexible `struct l2t_data` with `l2t_capacity` entries, initializes entry state, locks, queues, indices, free count, and rover.
- `t3_l2t_get()` looks up or allocates an L2T entry for a `dst_entry`/destination address/netdevice. It hashes by IPv4 neighbour primary key and ifindex, accounts for SMT port, takes a neighbour reference, inserts new entries into the hash chain, and sets initial `RESOLVING` state.
- `t3_l2t_send_slow()` handles non-VALID entries: revalidates STALE entries, queues packets for RESOLVING entries, triggers `neigh_event_send()`, and on successful resolution writes hardware state then drains the queued packets.
- `t3_l2t_update()` handles host neighbour changes: finds matching entries, replaces neighbour references, transitions state based on NUD flags, writes new L2T hardware entries when MAC changed or resolution completed, and handles failed resolution queues.
- `t3_l2e_free()` releases neighbour references when refcount reaches zero and increments free entry count.
- Helpers: `setup_l2e_send_pending()`, `alloc_l2e()`, `reuse_entry()`, `handle_failed_resolution()`, `neigh_replace()`, `arpq_enqueue()`, `arp_hash()`, and `vlan_prio()`.

## Control flow

A client obtains an entry with `t3_l2t_get()`, usually while preparing an offload connection or redirect. If the entry is already in the hash table for the same destination/ifindex/SMT port, `l2t_hold()` increments the refcount and `reuse_entry()` refreshes state on a 0-to-1 transition. If no entry exists, `alloc_l2e()` scans for a zero-ref entry, removes stale hash membership if necessary, and returns it for initialization.

When sending through `l2t_send()` from `l2t.h`, VALID entries go directly to `cxgb3_ofld_send()`. Other states enter `t3_l2t_send_slow()`: STALE entries kick neighbour revalidation and then optimistically become VALID, RESOLVING entries enqueue the skb and trigger ARP/neighbor resolution. Once resolution is available, `setup_l2e_send_pending()` builds a `CPL_L2T_WRITE_REQ`, copies the neighbour MAC into both software and firmware request state, sends the control request, drains `arpq`, and marks the entry VALID.

Neighbour notifications from `cxgb3_offload.c` call `t3_l2t_update()`. On NUD failure, queued packets are moved to a local queue and each skb's optional `arp_failure_handler` is invoked; if no failure handler exists, the packet is sent anyway. On connected/stale neighbour states, the hardware table is written and pending packets are sent.

## State and persistence behavior

All state is volatile and bound to an active `t3cdev` via the RCU `l2opt` pointer. `struct l2t_data` contains the table size, allocation rover, free count, table rwlock, RCU head, and flexible array of `struct l2t_entry`. Each entry stores software state (`VALID`, `STALE`, `RESOLVING`, `UNUSED`), hardware index, IPv4 address, ifindex, SMT index, VLAN TCI or `VLAN_NONE`, neighbour pointer with held reference, hash-chain pointers, pending skb queue, spinlock, refcount, and cached destination MAC. There is no disk persistence; hardware state is synchronized by firmware work requests.

The locking hierarchy is documented in the file: table rwlock nests outside entry locks. Lookups/allocations take the table lock; entry mutation takes the entry spinlock; updates can take the table lock as reader while multiple entries update in parallel. Refcounts and `nfree` are atomic, but correctness still depends on obeying the table/entry lock ordering.

## Dependencies and integration points

`l2t.c` depends on Linux `sk_buff`, `net_device`, VLAN helpers, Jenkins hash, `struct neighbour`, Chelsio `common.h`, `t3cdev.h`, `cxgb3_defs.h`, `l2t.h`, `t3_cpl.h`, and `firmware_exports.h`. It integrates with `cxgb3_offload.c` for neighbour events, `cxgb3_ofld_send()` for firmware work-request transmission, and offload clients that attach ARP failure handlers in skb control blocks.

## Risks and edge cases

- Hashing uses `d->nentries - 1` as a mask, so L2T capacity is expected to be a power of two. Non-power-of-two capacities would bias or truncate buckets.
- `addr = *(u32 *)neigh->primary_key` assumes IPv4-sized neighbour keys; this table is not a generic IPv6 neighbour map.
- If allocation of the CPL L2T write skb fails during resolution, queued packets remain pending until another packet retries or a neighbour update arrives.
- `handle_failed_resolution()` sends packets without a failure handler even after ARP failure; the comment questions whether this should be abandoned.
- `t3_l2e_free()` increments `nfree` after refcount reaches zero, while entries may remain in the hash table for reuse; allocation and hold paths must preserve the documented locking protocol.
- VLAN handling stores VLAN ID but `vlan_prio()` reads priority bits from `e->vlan`; current initialization from `vlan_dev_vlan_id()` does not include priority bits.

## Test signals

Tests should exercise entry allocation/reuse/free, hash collision chains, zero-ref stale hash removal, send path through VALID/STALE/RESOLVING states, ARP success and failure with and without skb failure handlers, neighbour MAC changes, VLAN and non-VLAN devices, redirect-driven L2T references, memory allocation failure for control skb, concurrent lookup/update/free under lockdep, and teardown through RCU after offload deactivation.
