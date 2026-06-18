<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_ext_frag.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_ext_frag.c

This module declares the RFC7400 generic header compression descriptor for IPv6 fragmentation extension headers. It maps `NEXTHDR_FRAGMENT` to id `0xb4` masked by `0xfe`.

There are no custom callbacks, so the file participates only in descriptor registration. Compression checks for fragment headers will not select it as usable, and uncompression of a matching id returns unsupported from the core.

State is the static descriptor plus global registration. Dependencies are `nhc.h`, module init/exit, and IPv6 fragment constants. Like the destination GHC module, it can conflict with the RFC6282 fragment descriptor because the registry is keyed only by IPv6 next-header number.

Risk areas include module load conflicts, silently unavailable compression, and correctness of the id/mask pair. Tests should verify `lowpan_nhc_add()` conflict behavior with `nhc_fragment`, unload synchronization, and expected `-ENOTSUPP` on receive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_ext_frag.c -->
