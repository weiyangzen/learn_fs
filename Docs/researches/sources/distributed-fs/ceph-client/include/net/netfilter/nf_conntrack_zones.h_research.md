<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_zones.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_zones.h

## Purpose
`nf_conntrack_zones.h` defines inline helpers for conntrack zones, including default-zone fallback, template-derived zones, mark-derived zones, direction matching, and equality.

## Important APIs, types, and functions
It defines `nf_ct_zone`, `nf_ct_zone_init`, `nf_ct_zone_tmpl`, `nf_ct_zone_add`, `nf_ct_zone_matches_dir`, `nf_ct_zone_id`, `nf_ct_zone_equal`, and `nf_ct_zone_equal_any`.

## Control flow
Conntrack allocation copies a selected zone into the entry when zones are enabled. Templates can request dynamic zone IDs from `skb->mark`. Lookups compare zone IDs only for directions enabled by the zone's direction mask; otherwise they fall back to the default zone.

## State and persistence
State is the optional `ct->zone` field and temporary stack zone objects. Disabled builds use the global default zone and equality always succeeds.

## Dependencies and integration points
It depends on conntrack zones common UAPI and `struct nf_conn`. It integrates nft/iptables zone selection with conntrack lookup.

## Risks and test signals
Risks include mark-derived zone surprises, direction-mask mistakes, disabled-build behavior, and templates passed as NULL to `nf_ct_zone`. Tests should cover explicit zones, mark zones, original/reply direction masks, default fallback, and CONFIG_NF_CONNTRACK_ZONES off.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_zones.h` completely for this pass (89 lines, 2040 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_zones.h -->
