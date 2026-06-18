
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_redir.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_redir.c

## Purpose

`nft_redir.c` implements nftables NAT redirect expressions for IPv4, IPv6, and inet families. Redirect rewrites packet destination to a local address, optionally using protocol port ranges loaded from registers.

## Important APIs, Types, and Functions

`struct nft_redir` stores source registers for min/max protocol ports and NAT range flags. `nft_redir_validate()` requires NAT chain type and restricts hooks to prerouting and local output. `nft_redir_init()` parses port registers and flags and obtains conntrack/NAT namespace support with `nf_ct_netns_get()`. `nft_redir_eval()` builds `struct nf_nat_range2` and dispatches to `nf_nat_redirect_ipv4()` or `nf_nat_redirect_ipv6()`.

## Control Flow

On rule creation, optional min/max protocol registers imply `NF_NAT_RANGE_PROTO_SPECIFIED`; missing max defaults to min. Evaluation zeroes a NAT range, fills flags and optional port range, switches on packet family, and stores the NAT helper verdict. Module init registers IPv4, optionally IPv6, and optionally inet expression types, unwinding prior registrations on failure.

## State and Persistence Behavior

The expression keeps only register and flag configuration. NAT connection persistence is owned by conntrack/NAT subsystems, not this file. Namespace references acquired at init are released by family-specific destroy callbacks.

## Dependencies and Integration Points

Dependencies include nf_tables, `nf_nat.h`, `nf_nat_redirect.h`, conntrack namespace reference management, and family-specific NAT redirect helpers. The expression is only valid in NAT chains, so it integrates with nft chain dependency validation.

## Risks and Test Signals

Risks include losing `NF_NAT_RANGE_PROTO_SPECIFIED` when flags are overwritten by `NFTA_REDIR_FLAGS`, invalid hook use, family dispatch surprises in inet chains, and namespace reference leaks on registration or destroy errors. Test IPv4/IPv6/inet redirect, port min-only and min/max registers, NAT chain validation, local-output vs prerouting behavior, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_redir.c -->
