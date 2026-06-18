# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_hash_gen.h

## Purpose

`ip_set_hash_gen.h` is the generic hash set implementation template used by concrete hash set modules. Including modules define `HTYPE`, `MTYPE`, `HOST_MASK`, element structures, equality/listing helpers, and optional feature macros, and this header generates hash-table storage, add/delete/test/list/head, resize, garbage collection, and create logic.

## Important APIs And Types

The generic storage is `struct htable`, which contains RCU bucket pointers, hash-table size bits, per-region locks and counters, and resize reference counters. `struct hbucket` stores an array of fixed-size element records plus a bitmap of used slots. `struct htype` is token-pasted from `MTYPE` and stores the current RCU table, GC work, max elements, jhash seed, bucket size, optional netmask/bitmask/markmask, a resize add/delete backlog, a `next` cursor for range retries, and optional network prefix bookkeeping.

Generated variant callbacks include `mtype_add`, `mtype_del`, `mtype_test`, `mtype_resize`, `mtype_head`, `mtype_list`, `mtype_flush`, `mtype_destroy`, `mtype_uref`, `mtype_cancel_gc`, and `mtype_same_set`. When `IP_SET_EMIT_CREATE` is defined, the header also generates `HTYPE_create`.

## Control Flow

Add computes a jhash key over the element bytes, selects a region lock, checks region/global limits, optionally runs GC, reuses deleted or expired slots, supports force-add replacement, grows bucket arrays by `AHASH_INIT_SIZE`, and returns `-EAGAIN` to trigger resize when a bucket is full. It initializes counters, comments, skbinfo, and timeouts before marking a slot used. Delete clears the used bit, updates region counters, removes network prefix counts when enabled, destroys extensions, and shrinks or frees sparse buckets.

Resize allocates a table with one more hash bit, rehashes all live non-expired elements under RCU protection, publishes the new table, waits for readers, then replays kernel-side add/delete operations saved in `h->ad` during resize. Old tables are destroyed only when `uref` reaches zero. GC runs as delayed work over one region at a time, removing expired elements and shrinking buckets.

Test either hashes the exact element or, for network-aware types, iterates stored prefix lengths to match host addresses against network entries. Listing pins the table with `mtype_uref`, walks buckets from a netlink cursor, skips expired elements, emits type-specific data and extensions, and handles skb space limits. Head reports hashsize, maxelem, optional bitmask/netmask/markmask, bucket size/initval, references, memory size, element count, and set flags.

## State And Persistence

State is entirely in memory: RCU hash tables, per-region locks/counters, delayed work for timeout GC, element extension storage, prefix counters, and resize backlog entries. The create path accepts userspace `hashsize`, `maxelem`, timeout, bucket size, initval, netmask/bitmask, and flags. There is no persistent storage beyond userspace restore.

## Dependencies And Integration

The template depends on jhash, RCU, nfnetlink lock assertions, delayed work, ipset allocation and extension APIs, netmask helpers, and concrete type helpers. It is included twice by dual-family modules to generate IPv4 and IPv6 variants, with the second include usually defining `IP_SET_EMIT_CREATE`.

## Risks

This is a high-risk concurrency template. Region locking, RCU table replacement, `ref` and `uref` lifetimes, and resize backlog replay must remain consistent. Element size must be a multiple of `u32` for `jhash2`, enforced by `BUILD_BUG_ON`. Optional macros change data layout and matching semantics, so each concrete type must define equality, masking, and listing correctly. Force-add can evict existing elements under pressure. Net prefix bookkeeping must stay synchronized with add, delete, GC, and resize.

## Test Signals

Run hash-type tests with small bucket sizes and low maxelem to force bucket growth, resize, forceadd, GC, and full-set errors. Add concurrent packet-path add/delete/test while userspace triggers resize and dumps. Exercise timeout expiry, comments/counters/skbinfo, netmask/bitmask options, initval reproducibility, bucket-size create flags, net prefix matching, dump resumption after small skb limits, and KASAN/KCSAN/lockdep.
