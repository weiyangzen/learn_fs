# sources/distributed-fs/ceph-client/net/netfilter/xt_CHECKSUM.c

Purpose: `CHECKSUM` target fills partial packet checksums, primarily for mangle OUTPUT UDP cases.

Important APIs/types/functions: `checksum_tg()` and `checksum_tg_check()` with `XT_CHECKSUM_OP_FILL`.

Control flow: check rejects unsupported or empty operation masks and warns for broad/non-UDP usage. Runtime calls `skb_checksum_help()` only for non-GSO `CHECKSUM_PARTIAL` skbs, then continues traversal.

State and persistence: no persistent state; checksum data in skb may be completed. Dependencies include x_tables, IPv4/IPv6 rule metadata, and skb checksum helpers. Risks: helper return is ignored, non-UDP use is warned not rejected, and GSO packets are intentionally skipped. Test signals: operation validation, UDP-constrained rule, partial checksum conversion, GSO no-op, IPv4/IPv6 registration, and warning path.
