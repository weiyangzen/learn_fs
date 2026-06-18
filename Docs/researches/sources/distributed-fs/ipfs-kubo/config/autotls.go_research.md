# Research: sources/distributed-fs/ipfs-kubo/config/autotls.go

Purpose: Defines AutoTLS/p2p-forge configuration for obtaining domain names and TLS certificates for browser-friendly connectivity.

Important APIs/types/functions: `AutoTLS` fields include `Enabled`, `AutoWSS`, `SkipDNSLookup`, `DomainSuffix`, registration endpoint/token/delay, CA endpoint, and `ShortAddrs`. Defaults are sourced from `p2p-forge` plus Kubo constants.

Control flow, state, and persistence: No functions. Values are persisted in config and resolved by node/network setup. Flags use the ternary `Flag` type so unset can mean "default".

Dependencies and integration points: Depends on `github.com/ipshipyard/p2p-forge/client` constants. Profiles `test` and `default-networking` adjust AutoTLS enablement.

Risks and test signals: AutoWSS, ShortAddrs, and DNS behavior depend on multiple flags and downstream address generation. Misconfigured private endpoints or tokens can break certificate registration. No direct tests in this subset.
