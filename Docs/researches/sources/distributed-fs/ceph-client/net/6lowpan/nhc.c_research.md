<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc.c

This file implements the registry and dispatch layer for 6LoWPAN next-header compression modules. It maps IPv6 `nexthdr` values to `struct lowpan_nhc` handlers and dispatches compression/uncompression callbacks during 6LoWPAN packet encode/decode.

The key state is `lowpan_nexthdr_nhcs[NEXTHDR_MAX + 1]`, protected by `lowpan_nhc_lock`. `lowpan_nhc_add()` and `lowpan_nhc_del()` are exported for NHC modules declared with `module_lowpan_nhc()`. `lowpan_nhc_check_compression()` tests whether a compressor exists for the IPv6 next header. `lowpan_nhc_do_compression()` calls the handler, fixes a missing transport header for raw sockets, and pulls the uncompressed transport header from the skb. `lowpan_nhc_do_uncompression()` reads the compressed id byte, finds a matching handler by `(id & idmask) == id`, calls its uncompressor if present, updates the IPv6 header's next-header field, and resets the transport header.

Control flow is synchronous and occurs while holding the spinlock. Deletion clears the registry slot and then calls `synchronize_net()` to reduce use-after-free exposure after module removal. The code still documents a race between check and compression if a module is removed between the two phases; it handles this by dropping the packet with `-EINVAL`.

Dependencies are `struct sk_buff`, IPv6 headers, lowpan helper APIs such as `lowpan_fetch_skb()` in handlers, and module lifetime rules. Risks include callback execution under a spinlock, module unload races, unknown id handling, and handlers with `NULL` callbacks that intentionally register ids but cannot actually compress/decompress. Tests should cover module add/delete conflicts, unknown ids, unsupported ids, raw-socket transport header setup, and successful UDP NHC round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc.c -->
