
# sources/distributed-fs/ceph-client/net/sched/cls_route.c

## Purpose

`cls_route.c` implements the `route`/`route4` classifier, which maps route realm/classid metadata (`dst->tclassid`) and incoming interface to traffic-control classes and actions. It is legacy IPv4 routing-realm classification optimized around small tag values.

## Important APIs, Types, and Functions

`struct route4_head` owns 257 top-level buckets and a 16-entry fastmap cache. `struct route4_bucket` contains 33 filter chains: 16 `from` buckets, 16 incoming-interface buckets, and one wildcard bucket. `struct route4_filter` stores id, iif, result, extensions, handle, bucket pointer, proto pointer, and deferred work.

Hash helpers include `route4_hash_to()`, `route4_hash_from()`, `route4_hash_iif()`, `route4_hash_wild()`, `to_hash()`, and `from_hash()`. Core operations are `route4_classify()`, `route4_change()`, `route4_delete()`, `route4_destroy()`, `route4_get()`, `route4_walk()`, `route4_dump()`, and `route4_bind_class()`. `route4_set_parms()` builds canonical handles from `to`, `from`, and `iif`.

## Control Flow

Classification obtains `skb_dst()`, reads `dst->tclassid` and `inet_iif()`, then checks the fastmap under `fastmap_lock`. A cached success returns the class immediately; a cached failure returns no match. On cache miss it searches the `to` bucket, first exact `from`, then `iif`, then wildcard, then repeats with `to ANY` by clearing lower bits and using table index 256. A matching rule executes extensions if present; rules without actions may be cached in fastmap.

Creation requires a non-zero handle and options. `route4_set_parms()` validates actions, rejects simultaneous `from` and `iif`, constructs or verifies the canonical handle, allocates a bucket if needed, fills id/iif/class result, and binds classid. `route4_change()` allocates a new filter for both create and replace, inserts it ordered by handle, keeps destination metadata through `tcf_block_netif_keep_dst()`, removes any old filter, resets fastmap, and queues old destruction. Delete unlinks a filter, resets fastmap, queues destruction, frees an empty bucket, and reports whether the classifier is now empty. Destroy drains all buckets and RCU-frees buckets/head.

## State and Persistence Behavior

Persistent state is the bucket tree plus the fastmap cache. The fastmap is guarded by a global spinlock because the triple of id, iif, and filter pointer must change atomically. Filter memory and buckets are RCU-freed. Action net references can delay final filter free. Class binding persists in each filter result and is unbound during delete/destroy.

## Dependencies and Integration Points

The classifier depends on route metadata (`dst_entry::tclassid`), `inet_iif()`, `skb_dst()`, `tcf_exts`, qdisc class binding, netlink route4 attributes, RTNL-protected updates, and RCU-protected classification. It registers classifier kind `route`.

## Risks and Edge Cases

Fastmap cache invalidation is required on every topology change or stale filter pointers can be returned. The priority order (`to/from`, `to/iif`, wildcard, then `to ANY`) is user-visible. `from` and `iif` are mutually exclusive. Handle construction is subtle: top-level hash, from/iif encoding, and wildcard values must match dump/get/delete expectations. This local source has an apparent extra brace after `__route4_delete_filter()`, which is a compile risk in this snapshot.

## Test Signals

Use route realm classification tests with exact `to/from`, `to/fromif`, wildcard, and `to ANY` rules; replacement and deletion with fastmap invalidation; dump round trips for canonical handles; and action/class binding checks. Build tests should catch the local syntax issue.
