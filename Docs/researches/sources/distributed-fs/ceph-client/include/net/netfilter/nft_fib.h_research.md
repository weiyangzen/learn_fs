# sources/distributed-fs/ceph-client/include/net/netfilter/nft_fib.h

Purpose: Defines common nftables FIB expression state and helpers for route/interface lookup based matching.

Important APIs/types/functions: `struct nft_fib` stores destination register, result selector, and flags. APIs include `nft_fib_dump`, `nft_fib_init`, `nft_fib_validate`, IPv4/IPv6 type/eval functions, `nft_fib_store_result`, and helpers `nft_fib_is_loopback`, `nft_fib_can_skip`, and `nft_fib_l3mdev_master_ifindex_rcu`.

Control flow: Init validates netlink attributes; eval functions perform family-specific FIB lookups and store requested result into nft registers. `nft_fib_can_skip` short-circuits lookup in inbound hooks when socket cached route/loopback proves the input device.

State and persistence: Expression-private state is embedded in nft rules. Runtime lookup reads route/device/socket state but stores no persistent data.

Dependencies/integration: Depends on `nf_tables.h`, l3mdev master lookup, netdevice flags, socket fullsock state, and IPv4/IPv6 route lookup implementations.

Risks/test signals: Test loopback skips, socket route cache correctness, VRF/l3mdev master indexes, result register length, invalid hook use, IPv4/IPv6 parity, and route changes during evaluation.
