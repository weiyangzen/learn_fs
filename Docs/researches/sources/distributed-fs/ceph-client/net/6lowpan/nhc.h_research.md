<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc.h -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc.h

This header defines the internal 6LoWPAN next-header compression contract. It provides the `struct lowpan_nhc` descriptor, the `LOWPAN_NHC()` declaration macro, module init/exit glue through `module_lowpan_nhc()`, and function prototypes for registry and dispatch operations implemented in `nhc.c`.

The central type, `struct lowpan_nhc`, records a human-readable name, IPv6 next-header value, uncompressed header length to reserve or pull, compressed id and mask bytes, and optional `compress`/`uncompress` callbacks. The macro-generated descriptors are static const objects that individual NHC modules register at module load and deregister at exit. Public functions include `lowpan_nhc_check_compression()`, `lowpan_nhc_do_compression()`, `lowpan_nhc_do_uncompression()`, `lowpan_nhc_add()`, and `lowpan_nhc_del()`.

State is not held in the header itself, but the contract defines how modules participate in the global `lowpan_nexthdr_nhcs` table. Integration points include Linux module init/exit, `struct sk_buff` mutation, IPv6 next-header fields, and lowpan packet formatting.

Risks are mostly API-contract risks: descriptor ids and masks must not overlap ambiguously for the same decoded byte, `nexthdrlen` must match the actual header consumed/restored by handlers, and callbacks must tolerate skb linearity and bounds. Tests should compile NHC modules against this header, verify that each descriptor registers to the expected next-header number, and exercise unsupported descriptors with `NULL` callbacks so the core returns `-ENOTSUPP` rather than corrupting packet state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc.h -->
