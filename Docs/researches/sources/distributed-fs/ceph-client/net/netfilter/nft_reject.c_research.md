
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_reject.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_reject.c

## Purpose

`nft_reject.c` provides shared reject expression policy, initialization, dumping, hook validation, and ICMPX-to-family-code mapping used by family-specific reject implementations.

## Important APIs, Types, and Functions

Exported symbols include `nft_reject_policy`, `nft_reject_validate()`, `nft_reject_init()`, `nft_reject_dump()`, `nft_reject_icmp_code()`, and `nft_reject_icmpv6_code()`. The private data type is `struct nft_reject` from `nft_reject.h`, storing reject type and ICMP code.

## Control Flow

Initialization requires `NFTA_REJECT_TYPE`. ICMP and ICMPX unreachable modes require `NFTA_REJECT_ICMP_CODE`; ICMPX codes are range-checked against `NFT_REJECT_ICMPX_MAX`. TCP reset requires no code. Dump emits type and emits code only for unreachable modes. Shared validation allows local-in, forward, local-out, and prerouting hooks.

## State and Persistence Behavior

State is immutable expression configuration. ICMP mapping arrays are static module data. The file performs no packet mutation or verdict setting by itself; family modules call the helpers.

## Dependencies and Integration Points

This module exports helper symbols to IPv4, IPv6, inet, bridge, and netdev reject modules. It depends on nf_tables netlink policies and Linux ICMP/ICMPv6 constants.

## Risks and Test Signals

Risks include accepting invalid ICMPX codes, mismatched family mapping, or using reject in hooks where generated errors are invalid. Test reject rule creation for each type, invalid codes, dump round trips, and family modules' use of ICMPX mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_reject.c -->
