# sources/distributed-fs/ipfs-kubo/core/node/libp2p/addrs_test.go

Purpose: validates address filtering and diagnostic helper behavior from `addrs.go`. Important test helpers are `mustMultiaddrs`, `TestFindDeadListeners`, and `TestMakeAddrsFactoryDropsEmptyMultiaddrs`.

Control flow: table tests construct resolved listener addrs, raw `Addresses.Swarm`, filters, and NoAnnounce rules, then compare `findDeadListeners` output with `require.ElementsMatch`. Cases cover empty configs, explicit loopback reverse-proxy gotchas, wildcard expansions, IPv6 ULA filtering, Docker bridge addresses, DNS listeners, exact NoAnnounce entries, malformed rules, WebTransport certhashes, TCP/QUIC port sharing, WSS to `/tls/ws` rewrites, uppercase IPv6, and `/tcp/0` assigned ports. The factory test ensures nil/zero multiaddrs are removed while valid duplicates remain.

State and persistence: no external state; all tests are pure in-memory.

Dependencies/integration: uses multiaddr parsing and testify assertions. It directly protects the log-level routing semantics in `addrs.go` and guards signed peer records from receiving empty multiaddrs.

Risks signaled: explicit-vs-wildcard misclassification can produce noisy errors or hide unreachable listeners; full-string multiaddr comparisons are brittle across transport rewrites. This file is strong unit coverage for recent address edge cases.
