# sources/distributed-fs/ipfs-kubo/core/commands/swarm_addrs_autonat.go

Purpose: implements `ipfs swarm addrs autonat`, reporting AutoNAT V2 overall and per-address reachability.

Important APIs/types/functions: `reachabilityHost` and `confirmedAddrsHost` are small capability interfaces checked against `nd.PeerHost`. `autoNATResult` is the JSON/text output. Helpers convert multiaddrs to strings and render address sections.

Control flow: command requires an online node. It defaults reachability to unknown, then conditionally reads `ConfirmedAddrs` for reachable/unreachable/unknown address lists and `Reachability` for overall state. It adds best-effort NAT classification through `libp2p.DetectNAT`, emits the result, and text-encodes a human-readable report.

State and persistence behavior: read-only. It reports live AutoNAT/libp2p host state and does not mutate repo, peerstore, or network.

Dependencies and integration points: depends on the libp2p host implementation exposing optional methods from embedded BasicHost/AutoNAT V2 support, Kubo libp2p NAT detection, and shared `ErrNotOnline`.

Risks: when host capabilities are absent, it returns unknown/empty data rather than an error. NAT classification is best-effort and may be empty. Text output can show no per-address data even when overall reachability is known.

Test signals: no direct tests in this file.
