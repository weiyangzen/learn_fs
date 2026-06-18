# Research: sources/distributed-fs/ipfs-kubo/config/experiments.go

Purpose: Holds experimental and legacy feature flags.

Important APIs/types/functions: `Experiments` includes filestore/urlstore/sharding/libp2p stream mounting/P2P HTTP proxy/optimistic provide/gateway-over-libp2p fields, plus removed-key sentinel fields `GraphsyncEnabled` and `AcceleratedDHTClient`.

Control flow, state, and persistence: No functions here, but custom sentinel types in `types.go` reject removed config keys during JSON decode while accepting limited empty/false values.

Dependencies and integration points: Consumed by daemon/node setup and config migration/validation. `AcceleratedDHTClient` moved to `Routing.AcceleratedDHTClient`.

Risks and test signals: Experimental flags can have unstable semantics. Deprecated fields remain for compatibility and may be ignored. Removed-key rejection is tested indirectly through `types.go` sentinel behavior but not by dedicated experiment tests in this subset.
