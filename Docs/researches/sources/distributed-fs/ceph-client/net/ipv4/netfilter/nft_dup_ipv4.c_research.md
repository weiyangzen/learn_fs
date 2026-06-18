# sources/distributed-fs/ceph-client/net/ipv4/netfilter/nft_dup_ipv4.c

## Purpose
IPv4 nftables `dup` expression. It duplicates a packet to a configured IPv4 gateway and optional output interface while normal nft evaluation continues.

## Important APIs, types, and functions
`struct nft_dup_ipv4` stores source register numbers for gateway and optional device. `nft_dup_ipv4_init()` validates register loads. `nft_dup_ipv4_eval()` reads registers and calls `nf_dup_ipv4()`. `nft_dup_ipv4_dump()` serializes rule state. Module init/fini register the expression type.

## Control flow
At rule install, `NFTA_DUP_SREG_ADDR` is mandatory and `NFTA_DUP_SREG_DEV` optional. At evaluation, gateway and oif are read from nft registers, oif defaults to `-1`, and `nf_dup_ipv4()` receives the current net namespace, skb, hook, gateway, and oif.

## State and persistence
Per-rule state contains only register selectors. There is no mutable module runtime state; packet copy/routing behavior is delegated to `nf_dup_ipv4()`.

## Dependencies and integration points
Depends on nf_tables expression APIs, netlink policies, register load/dump helpers, and IPv4 packet duplication. Registered as family `NFPROTO_IPV4`, name `dup`.

## Risks
Register size validation protects runtime reads. Duplication failures do not set a verdict here, so callers must rely on `nf_dup_ipv4()` side effects. Optional device register zero means unset.

## Test signals
Install/dump rules with and without device register, duplicate packets at several hooks, test missing gateway attribute, invalid register size, and route failures in the duplication helper.
