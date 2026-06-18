## sources/distributed-fs/ipfs-kubo/test/sharness/t0220-bitswap.sh

Purpose: tests Bitswap command output for stats and wantlists.

Important APIs and helpers: uses `ipfs bitswap stat`, `ipfs bitswap stat --human`, `ipfs bitswap wantlist -p`, `ipfs bitswap wantlist`, `ipfs config Identity.PeerID`, `test_check_peerid`, `test_cmp`, and daemon lifecycle helpers.

Control flow and state: starts a daemon, checks Bitswap stats output includes expected fields, validates local peer ID formatting, checks wantlist output with peer display, confirms the wantlist is empty after no outstanding requests, and repeats stat checks including human-readable output.

Dependencies and integration points: covers Bitswap session/accounting introspection, peer ID display, wantlist query endpoints, and human-size formatting.

Risks and test signals: catches renamed/missing stats fields, stale wantlist entries, and peer ID formatting regressions. Passing requires expected output fields and empty wantlist where appropriate.
