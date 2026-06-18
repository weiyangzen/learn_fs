# sources/distributed-fs/ipfs-kubo/core/node/bitswap.go

## Purpose
Constructs Kubo Bitswap options, the Bitswap service, and the online exchange wrapper used by the node dependency graph.

## Important APIs, Types, and Functions
Defines Bitswap default constants, `bitswapOptionsOut`, `BitswapOptions`, `bitswapIn`, `Bitswap`, `OnlineExchange`, and `noopExchange`.

## Control Flow and State
`BitswapOptions` reads internal config defaults for workers, delays, outstanding bytes, and want-have replacement. `Bitswap` builds libp2p and/or HTTP retrieval networks, rejects configurations with both disabled, configures HTTP retrieval limits/allowlist/denylist, appends Kubo-specific provider query manager and broadcast-control options, decodes ignored providers, builds the provider query manager, enables/disables serving, creates Bitswap, and registers lifecycle close hooks. `OnlineExchange` returns either Bitswap or a no-op exchange that always reports not found.

## Dependencies and Integration Points
Depends on Boxo bitswap/client/network/httpnet, blockstore, exchange interface, provider query manager, Kubo config/version/helpers/shutdown, libp2p host/routing/peer, CIDs, and Uber Fx. It is part of node construction.

## Risks and Test Signals
Risks include config shadowing of the `libp2pEnabled` parameter, invalid ignored provider IDs aborting startup, HTTP retrieval security lists, broadcast-control default typo (`disabled` branch sets disposition to enabled), close hook ownership, and no-op exchange semantics when Bitswap inactive. Tests should cover network selection, config parsing, ignored providers, lifecycle close, and disabled exchange behavior.
