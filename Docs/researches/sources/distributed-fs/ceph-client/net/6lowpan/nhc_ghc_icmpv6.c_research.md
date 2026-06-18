<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_icmpv6.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_icmpv6.c

This file registers the RFC7400 generic-header-compression id for ICMPv6. The descriptor `ghc_icmpv6` maps `NEXTHDR_ICMP` to exact id `0xdf` with mask `0xff`.

No compression or uncompression callbacks are implemented. The descriptor can be discovered by compressed id, but the core will return unsupported for receive and will not offer transmit compression.

State is limited to the descriptor and registry membership. Dependencies include `nhc.h`, IPv6/ICMP next-header constants, and module lifecycle. Unlike the extension stubs, it does not obviously conflict with another listed ICMP NHC descriptor in this work item.

Risks are operational confusion about RFC7400 support and exact-id matching mistakes. Tests should load/unload the module, inject a compressed id byte `0xdf`, and assert that the framework produces a warning and `-ENOTSUPP` without corrupting skb transport-header state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_icmpv6.c -->
