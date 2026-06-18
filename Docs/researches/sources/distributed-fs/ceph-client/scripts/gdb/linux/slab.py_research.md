# sources/distributed-fs/ceph-client/scripts/gdb/linux/slab.py

## Purpose
`slab.py` provides SLUB debugging commands: `lx-slabinfo` for cache summaries and `lx-slabtrace` for allocation/free site aggregation.

## Important APIs, Types, and Functions
Helpers decode slab folios, object addresses, object indexes, freelist hardening, original allocation size, and `struct track` metadata. `slabtrace()` aggregates locations by call site, stack handle, and wasted bytes. `slabinfo()` prints active objects, total objects, object size, objects per slab, and pages per slab.

## Control Flow
Both commands require `CONFIG_SLUB_DEBUG`. `slabtrace()` finds the named cache, walks node partial/full lists, builds a free-object bitmap from the freelist, skips free objects, reads alloc/free tracks, aggregates locations, and optionally prints stack depot traces. `slabinfo()` walks all caches and per-node partial lists to derive counts.

## State and Persistence Behavior
Read-only. Local aggregation state exists only for the command invocation.

## Dependencies and Integration Points
It depends on list traversal, stack depot, constants, and `mm.page_ops()` for slab address conversion and KASAN tag reset.

## Risks and Test Signals
Freelist decoding must match `CONFIG_SLAB_FREELIST_HARDENED`; corrupted freelists can index outside the bitmap. Full scans are expensive on large caches. Test with SLUB debug enabled, cache names with and without `SLAB_STORE_USER`, and compare `lx-slabinfo` with `/proc/slabinfo`.
