<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_ext_route.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_ext_route.c

This module registers RFC7400 generic compression metadata for IPv6 routing extension headers. The descriptor maps `NEXTHDR_ROUTING` to id `0xb2` under mask `0xfe`.

The file contains no transform callbacks, so it is a registration stub. Compression is not offered, and uncompression of matching bytes is rejected as unsupported by the core after descriptor lookup.

State is the static `ghc_ext_route` descriptor and the global NHC registry entry while the module is loaded. Dependencies are `nhc.h` and IPv6 routing next-header definitions. It can conflict with `nhc_routing` because the registry allows only one descriptor per next-header value.

Risks include unexpected `-EEXIST` during module load, unsupported RFC7400 packet reception, and ambiguity between RFC6282/RFC7400 ids in deployments. Tests should check module conflict paths, id matching, and graceful unsupported uncompression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_ext_route.c -->
