# sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_zones_common.h

Purpose: Defines common conntrack zone identifiers, direction masks, and zone metadata used to partition conntrack state.

Important APIs, types, and functions: Exports default zone constants, direction bit masks, `NF_CT_FLAG_MARK`, `struct nf_conntrack_zone`, and `nf_ct_zone_dflt`. Detected source surface: 24 lines; includes `uapi/linux/netfilter/nf_conntrack_tuple_common.h`; macros `NF_CT_DEFAULT_ZONE_DIR`, `NF_CT_DEFAULT_ZONE_ID`, `NF_CT_FLAG_MARK`, `NF_CT_ZONE_DIR_ORIG`, `NF_CT_ZONE_DIR_REPL`, `_NF_CONNTRACK_ZONES_COMMON_H`; structs `nf_conntrack_zone`; enums none; typedefs none; function-like declarations/helpers none.

Control flow: Conntrack code combines zone id, direction mask, and mark flag when hashing or matching tuples so otherwise identical flows can be isolated by namespace, ruleset, or mark.

State and persistence behavior: A zone is immutable metadata attached to a lookup or connection. The default zone is a shared constant.

Dependencies and integration points: Depends on conntrack tuple direction UAPI. Used by core conntrack, nftables/iptables ct zone targets, and net namespace rules.

Risks and test signals: Risks are default-zone leakage, direction mask mismatch, and mark-based zone confusion. Test same tuple in separate zones and original/reply direction restrictions.
