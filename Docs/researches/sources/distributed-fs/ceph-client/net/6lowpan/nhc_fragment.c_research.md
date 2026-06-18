<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_fragment.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc_fragment.c

This module registers the RFC6282 fragment-header next-header compression id. The descriptor `nhc_fragment` maps `NEXTHDR_FRAGMENT` to id `0xe4` with mask `0xfe` and no transform callbacks.

Control flow is entirely module registration through `module_lowpan_nhc()`. Once loaded, the descriptor can be discovered by id during uncompression, but because `uncompress` is `NULL`, the core warns and returns `-ENOTSUPP`. Compression is similarly unavailable because `compress` is `NULL`.

There is no persistent state except the static descriptor and registry membership. Dependencies are the 6LoWPAN NHC framework and IPv6 fragment next-header constants.

Risks are misinterpreting this file as full fragment support; actual fragmentation behavior must be handled elsewhere in the 6LoWPAN stack. Test signals are descriptor registration, duplicate-registration rejection if another fragment NHC is loaded, masked id matching, and graceful unsupported receive behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_fragment.c -->
