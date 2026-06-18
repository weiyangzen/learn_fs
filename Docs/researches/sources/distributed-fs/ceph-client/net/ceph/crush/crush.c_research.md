# sources/distributed-fs/ceph-client/net/ceph/crush/crush.c

## Purpose
Provides common CRUSH map helpers for bucket algorithm naming, bucket item weight lookup, and memory destruction for CRUSH maps, buckets, and rules.

## Important APIs, Types, and Functions
Functions include `crush_bucket_alg_name()`, `crush_get_bucket_item_weight()`, `crush_destroy_bucket_uniform()`, `crush_destroy_bucket_list()`, `crush_destroy_bucket_tree()`, `crush_destroy_bucket_straw()`, `crush_destroy_bucket_straw2()`, `crush_destroy_bucket()`, `crush_destroy()`, and `crush_destroy_rule()`. It handles `struct crush_bucket` and algorithm-specific bucket structs.

## Control Flow
Weight lookup checks index bounds and switches by bucket algorithm to return the correct weight source. Destroy helpers free each algorithm's auxiliary arrays, then the common item array and bucket object. `crush_destroy()` iterates bucket and rule arrays, destroys populated entries, frees arrays, clears kernel-only name/choose-arg tables, and frees the map.

## State and Persistence
No global state. The functions tear down heap state created by CRUSH map decoding. CRUSH maps are in-memory representations of cluster placement data.

## Dependencies and Integration Points
Depends on kernel CRUSH structs and kernel-only cleanup helpers such as `clear_crush_names()` and `clear_choose_args()`. Used by OSD map lifecycle code.

## Risks
Destruction assumes algorithm tags match allocation layout. New bucket algorithms require updates to both weight lookup and cleanup. `crush_get_bucket_item_weight()` returns 0 for unknown algorithms or out-of-range indexes, which can mask invalid maps if callers do not validate earlier.

## Test Signals
Decode and destroy maps containing every bucket algorithm, run KASAN/KMEMLEAK on failure paths, verify weight lookup for each algorithm and out-of-range positions, and test unknown/invalid algorithm handling during map validation.
