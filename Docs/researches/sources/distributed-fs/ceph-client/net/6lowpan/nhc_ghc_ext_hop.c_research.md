<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_ext_hop.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_ext_hop.c

This file registers the RFC7400 generic compression id for hop-by-hop IPv6 extension headers. `ghc_ext_hop` uses `NEXTHDR_HOP`, id `0xb0`, and mask `0xfe`.

No actual compression or uncompression implementation is provided. The descriptor can be loaded into the NHC registry, but any matching received packet will be reported as an implemented id with no uncompressor and rejected by the core.

State is not persistent beyond module load. It depends on the 6LoWPAN NHC framework and module registration. It also shares the `NEXTHDR_HOP` registry key with the RFC6282 hop-by-hop descriptor, so load ordering can matter.

Risks are registry conflicts and unsupported packet paths. Tests should cover load/unload, conflict with `nhc_hop`, id-mask matching, and receive behavior that warns and returns `-ENOTSUPP` without advancing skb state incorrectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_ext_hop.c -->
