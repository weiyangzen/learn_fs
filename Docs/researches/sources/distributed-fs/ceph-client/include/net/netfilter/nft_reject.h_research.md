# sources/distributed-fs/ceph-client/include/net/netfilter/nft_reject.h

Purpose: Provides common nftables reject expression state, validation, init, dump, and ICMP code validation helpers.

Important APIs/types/functions: `struct nft_reject` stores reject type and ICMP code. APIs are `nft_reject_validate`, `nft_reject_init`, `nft_reject_dump`, `nft_reject_icmp_code`, and `nft_reject_icmpv6_code`; `nft_reject_policy` defines netlink attribute validation.

Control flow: Init parses reject type/code from netlink, validate enforces hook/family constraints, family-specific eval code later generates TCP reset or ICMP/ICMPv6 rejects using this state.

State and persistence: Expression-private immutable state embedded in nft rules.

Dependencies/integration: Depends on netlink policies, nftables expression lifecycle, uapi reject types, and family-specific reject implementations.

Risks/test signals: Test invalid ICMP/ICMPv6 codes, TCP reset in unsupported contexts, bridge/inet family interactions, dump round-trip, and malformed netlink attributes.
