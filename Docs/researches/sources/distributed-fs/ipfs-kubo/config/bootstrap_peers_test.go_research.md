# Research: sources/distributed-fs/ipfs-kubo/config/bootstrap_peers_test.go

Purpose: Verifies bootstrap peer parse/format round-trip behavior.

Important APIs/types/functions: `TestBootstrapPeerStrings` parses `autoconf.FallbackBootstrapPeers`, formats the result, and checks element equality.

Control flow, state, and persistence: Pure in-memory test. It does not write config.

Dependencies and integration points: Uses Boxo autoconf fallback peer list and `testify` assertions. It protects compatibility between autoconf fallback peers and Kubo bootstrap serialization.

Risks and test signals: Uses `ElementsMatch`, so it does not enforce output ordering. It does not cover invalid multiaddrs or peers with multiple addresses beyond the fallback list shape.
