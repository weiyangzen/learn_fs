# sources/distributed-fs/ipfs-kubo/core/node/p2pforge_resolver_test.go

Purpose: verifies deterministic p2p-forge DNS parsing and fallback behavior. Important helpers are `mockResolver`, `newTestResolver`, `assertLookupIP`, and tests for `LookupIPAddr` and `LookupTXT`.

Control flow: IP tests cover IPv4 ranges, trailing dot, uppercase suffix, full/compressed IPv6, loopback, and all-zero IPv6. Multiple suffix tests verify custom domains. Fallback tests ensure peerID-only, invalid peer ID, invalid IP encoding, leading hyphen, too many labels, and wrong suffix delegate to the fallback resolver. Error propagation is checked for fallback failure. TXT tests assert ACME challenge records are delegated and empty fallback records produce empty results.

State and persistence: pure in-memory mock resolver maps.

Dependencies/integration: Kubo config default domain suffix, Go net, testify. The tests protect AutoTLS DNS behavior and ACME compatibility.

Risks signaled: local parsing must not hijack unsupported names; otherwise future p2p-forge DNS formats or certificate validation could break.
