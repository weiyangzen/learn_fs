# sources/distributed-fs/ipfs-kubo/core/node/libp2p/cgnat_test.go

Purpose: unit-tests NAT classification, notice latching, and warning text. Important tests are `TestClassifyNAT`, `TestLatchNotice`, and `TestCGNATNoticeOutput`.

Control flow: `TestClassifyNAT` feeds synthetic multiaddrs, local interface IP sets, and libp2p reachability values into `classifyNAT`. It asserts CGNAT wins over double NAT, local Tailscale-style 100.64/10 addresses are ignored, public reachability suppresses warnings, IPv6 is ignored, and own private interface addrs are not flagged. `TestLatchNotice` proves double-NAT can upgrade to CGNAT but cannot downgrade or repeat. Output tests replace `cgnatNoticeOut` with a buffer and assert key strings.

State and persistence: pure in-memory; `captureNotice` restores the global writer with `t.Cleanup`.

Dependencies/integration: uses multiaddr, libp2p network reachability, testing, and bytes/string checks. The tests directly encode expected operational semantics for user-facing NAT warnings.

Risks signaled: false positives for overlay networks and repeated notices would be user-visible; this suite specifically guards both.
