# sources/distributed-fs/ceph-client/net/netlabel/netlabel_mgmt.c

## Purpose
Generic Netlink management interface for NetLabel domain mappings and protocol metadata. It lets privileged users add/remove/list domain mappings and defaults, query supported protocols, and retrieve the NetLabel protocol version.

## Important APIs, Types, And Functions
Defines global `atomic_t netlabel_mgmt_protocount`. Uses `netlbl_domhsh_walk_arg` for dumps. `netlbl_mgmt_add_common()` parses add/add-default payloads, while `netlbl_mgmt_listentry()` serializes mappings. Command handlers include add, remove, listall, adddef, removedef, listdef, protocols, and version. `netlbl_mgmt_genl_init()` registers the family.

## Control Flow
Add paths validate mutually exclusive IPv4/IPv6 selector attributes, copy optional domain strings, resolve CIPSO/CALIPSO DOI references, optionally build address-selector maps, and call `netlbl_domhsh_add()`. Remove deletes a named domain for all families; removedef deletes defaults. Listall walks the domain hash with bucket/chain cursors. Listdef looks up a family-specific default and serializes it. Protocol dumps emit unlabeled, CIPSOv4, and optionally CALIPSO.

## State And Persistence Behavior
The management counter tracks configured protocols and is incremented/decremented by DOI/static mapping layers as well as management-adjacent operations. Persistent mappings are transferred into the domain hash; on parse failures this file releases domain strings, selector allocations, and DOI references.

## Dependencies And Integration Points
Depends on Generic Netlink, CIPSO/CALIPSO DOI lookup, domain hash APIs, audit info from `netlabel_user.h`, and IPv4/IPv6 address helpers. It is registered by `netlbl_netlink_init()`.

## Risks And Test Signals
Risks include attribute validation gaps for binary address attrs in this policy, DOI reference leaks on complex add failure paths, counter drift, and dump truncation behavior when an skb fills. Test signals should include netlink add/list/remove for direct and selector mappings, default family behavior, protocol/version queries, DOI missing cases, and IPv6-disabled builds.
