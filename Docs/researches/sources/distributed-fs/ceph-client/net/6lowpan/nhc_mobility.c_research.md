<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_mobility.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc_mobility.c

This file registers the RFC6282 mobility-header NHC id. `nhc_mobility` maps `NEXTHDR_MOBILITY` to id `0xe8` masked by `0xfe`.

It does not implement compression or uncompression. The framework can recognize the id but will reject actual packet handling as unsupported.

State is static descriptor registration. Dependencies are the NHC core and IPv6 mobility header constants. There is no persistence or runtime configuration.

Risks are primarily unsupported mobility traffic and possible incorrect assumptions by users or tests that descriptor registration means functional compression. Tests should validate load/unload, id matching, and `-ENOTSUPP` handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_mobility.c -->
