# sources/distributed-fs/ceph-client/net/ipv4/netfilter/nft_fib_ipv4.c

## Purpose
IPv4 nftables `fib` expression evaluation. It returns route output interface, output interface name, or address type for source/destination route lookups under nft flags.

## Important APIs, types, and functions
Exported evaluators are `nft_fib4_eval_type()` and `nft_fib4_eval()`. `get_saddr()` suppresses multicast, limited broadcast, and zeronet source addresses. `nft_fib4_select_ops()` chooses operation tables by `NFTA_FIB_RESULT`. Generic nft fib helpers provide init/dump/validate/result storage.

## Control flow
Type evaluation safely reads the IPv4 header, chooses source or destination, then queries interface-specific or device-table address type. Route evaluation builds `flowi4`, handles shortcut cases and l3mdev, reads header, handles zeronet broadcast/multicast cases, copies mark/DSCP when flagged, chooses lookup daddr/saddr, performs `fib_lookup()`, filters result type and requested oif usage, then stores the result.

## State and persistence
Per-rule state is generic `struct nft_fib`. Runtime evaluation is stateless except for nft register writes or `NFT_BREAK` on malformed headers.

## Dependencies and integration points
Depends on IPv4 FIB, route/flow APIs, nft metadata, l3mdev, inet address-type helpers, and generic nft fib infrastructure. Registers IPv4 `fib` expression and exports evaluators.

## Risks
Semantics are subtle around `OIF`/`IIF`, forward-hook source lookup, l3mdev, mark/DSCP, and special addresses. The deliberate choice not to set `flowi4_oif` prevents overly constrained results and should not regress.

## Test signals
Test daddr/saddr, iif/oif, mark-aware routes, VRF/l3mdev, local/multicast/broadcast/zeronet, forward-hook source lookup, malformed headers, `ADDRTYPE`, and rule dump/restore.
