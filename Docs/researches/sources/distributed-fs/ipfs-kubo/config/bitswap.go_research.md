# Research: sources/distributed-fs/ipfs-kubo/config/bitswap.go

Purpose: Defines top-level Bitswap enablement configuration.

Important APIs/types/functions: `Bitswap` has `Libp2pEnabled` and `ServerEnabled` ternary flags. Defaults are `DefaultBitswapLibp2pEnabled` and `DefaultBitswapServerEnabled`, both true.

Control flow, state, and persistence: No functions. Flags are persisted in config and interpreted by node Bitswap setup.

Dependencies and integration points: Integrated with `HTTPRetrieval` and core node bitswap construction; `ServerEnabled` depends on libp2p bitswap being enabled.

Risks and test signals: Invalid combinations, such as server enabled while libp2p bitswap disabled, must be handled downstream. No direct tests in this subset.
