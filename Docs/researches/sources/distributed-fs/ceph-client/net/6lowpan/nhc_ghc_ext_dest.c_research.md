<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_ext_dest.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_ext_dest.c

This file registers the RFC7400 generic-header-compression id for IPv6 destination extension headers. `ghc_ext_dest` maps `NEXTHDR_DEST` to id `0xb6` with mask `0xfe`.

The descriptor has no compressor or uncompressor. It is a recognition stub that allows the framework to identify the id while still rejecting actual packet transformation as unsupported. It uses the same module registration macro as the RFC6282 NHC files.

State and persistence are limited to the module's static descriptor and the global NHC registry slot. A notable integration point is collision potential: it registers the same IPv6 next-header value as `nhc_dest`, so only one descriptor per `nexthdr` can be registered by the current registry. Loading both RFC6282 and RFC7400 destination modules can trigger `-EEXIST` depending on order.

Risks are id-space collisions, next-header slot conflicts, and user expectations of RFC7400 functionality despite missing callbacks. Tests should include module load ordering with `nhc_dest`, id matching for `0xb6/0xb7`, and unsupported uncompression paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_ext_dest.c -->
