# sources/distributed-fs/ceph-client/net/netfilter/nft_fib.c

Purpose: provides shared generic helpers for nftables FIB/routing-table lookup expressions used by IPv4, IPv6, inet, and netdev frontends.

Important APIs/types/functions: exported `nft_fib_policy` validates `NFTA_FIB_DREG`, result, and flags. `nft_fib_validate()` enforces hook placement based on result and input/output interface flags. `nft_fib_init()` validates source/destination and iif/oif flag combinations and sets destination register width. `nft_fib_dump()` serializes expression configuration. `nft_fib_store_result()` stores output interface index/name or presence boolean.

Control flow: init requires nonzero flags, exactly one of source/destination, and not both iif/oif. Result `OIF` and `OIFNAME` reject OIF input flags and select register sizes of `int` or `IFNAMSIZ`; `ADDRTYPE` stores a u32. Validate maps result and flag direction to legal nf hook masks and calls `nft_chain_validate_hooks()`.

State/persistence: no dynamic state; expression state is `struct nft_fib` in private data. Dependencies are backend evaluators (`nft_fib4_eval`, `nft_fib6_eval`, type variants) declared in `nft_fib.h`, netdevice naming, and nf_tables register parsing. Risks include mismatched frontend/backend family assumptions, invalid flag combinations, stale device names if backend passes null dev, and hook validation regressions. Test signals: all result modes, present flag behavior, invalid flag combinations, hook placement by input/output path, dump round trips, IPv4/IPv6 backend parity, and no-route cases returning zero/empty output.
