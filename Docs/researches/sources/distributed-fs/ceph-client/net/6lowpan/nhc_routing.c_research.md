<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_routing.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc_routing.c

This module registers RFC6282 routing-header next-header compression metadata. The descriptor `nhc_routing` maps `NEXTHDR_ROUTING` to id `0xe2` under mask `0xfe`.

No custom callbacks exist, so the file is a descriptor-only module. Compression is not available and uncompression returns unsupported after id recognition.

State is the descriptor plus registry membership. Dependencies include `nhc.h`, module lifecycle, and IPv6 routing header constants. It can conflict with the RFC7400 routing extension descriptor because both use `NEXTHDR_ROUTING`.

Risks include unsupported routed-extension packets and registry conflicts. Tests should cover masked id recognition, load conflict with `ghc_ext_route`, and clean unsupported receive behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_routing.c -->
