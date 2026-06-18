<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_udp.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_udp.c

This module registers the RFC7400 generic UDP compression id range. It maps `NEXTHDR_UDP` to id `0xd0` with mask `0xf8`.

It has no compressor or uncompressor and therefore differs from `nhc_udp.c`, which implements RFC6282 UDP compression. Because the NHC registry is keyed by next-header number, this GHC UDP descriptor can conflict with the implemented RFC6282 UDP descriptor if both are loaded.

State is the static descriptor and global registry slot. Integration points are module load ordering, the NHC id scanner, and UDP next-header dispatch. There is no persistence.

Risks are high because UDP is the one fully implemented NHC in this group; loading the GHC stub instead of the RFC6282 UDP module could make UDP compression unavailable. Tests should cover conflict behavior with `nhc_udp`, exact range matching for ids `0xd0` through `0xd7`, compression check failure due to `NULL` callback, and receive `-ENOTSUPP` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_udp.c -->
