
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_bitmap.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_set_bitmap.c

## Purpose

`nft_set_bitmap.c` implements a compact O(1) nftables set backend for small integer keys of one or two bytes. A two-bit bitmap records element active state across current and next nftables generations while a list holds full element extensions for API operations.

## Important APIs, Types, and Functions

`struct nft_bitmap` contains the element list and bitmap bytes. `struct nft_bitmap_elem` contains `nft_elem_priv`, list node, and extension block. `nft_bitmap_lookup()` tests the bitmap only and returns a static found extension for set membership. `nft_bitmap_insert()`, `nft_bitmap_deactivate()`, `nft_bitmap_activate()`, `nft_bitmap_flush()`, and `nft_bitmap_remove()` update generation bits and list membership. `nft_bitmap_estimate()` accepts only key lengths up to two bytes and no element expressions.

## Control Flow

Key bytes map to a two-bit location by shifting the numeric key left by one. Insert checks for an active duplicate in the next generation, sets the next-generation active bit, and appends the element to the RCU list. Deactivate clears the next-generation bit and toggles element active metadata. Abort/commit behavior is driven by nf_tables generation handling via backend callbacks.

## State and Persistence Behavior

Persistent state is the bitmap plus RCU list of element extensions. The two-bit encoding distinguishes stable active, stable inactive, pending insert, and pending delete states across transactions. Lookups intentionally do not return per-element extensions; maps, objects, timeouts, and expressions are not supported by the estimate path.

## Dependencies and Integration Points

The backend integrates with nf_tables set type registration through exported `nft_set_bitmap_type`, nft generation masks, RCU list walking, and element destroy helpers.

## Risks and Test Signals

Risks include endian-sensitive key interpretation, bitmap bounds for two-byte keys, generation-bit mistakes during abort/commit, and stale list entries after remove. Test one-byte and two-byte sets, duplicate insert, delete/abort, flush, walk/get, and backend selection avoiding maps or expression-bearing sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_set_bitmap.c -->
