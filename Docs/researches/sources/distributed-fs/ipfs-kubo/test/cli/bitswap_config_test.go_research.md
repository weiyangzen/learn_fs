# sources/distributed-fs/ipfs-kubo/test/cli/bitswap_config_test.go

Purpose: integration tests for Bitswap configuration toggles, ensuring server/client behavior and daemon validation match `Bitswap.ServerEnabled`, `Bitswap.Libp2pEnabled`, and `HTTPRetrieval.Enabled`.

Important test: `TestBitswapConfig`. Subtests cover default server-enabled retrieval, server-disabled provider behavior, client retrieval while requester server is disabled, libp2p bitswap disabled with HTTP retrieval enabled, identify protocol suppression, and invalid configurations where both HTTP and libp2p retrieval are disabled.

Control flow creates provider/requester nodes, adds random test data, connects peers, and runs `ipfs cat`, `id`, `bitswap stat`, and `bitswap wantlist`. Some retrievals run in goroutines with timeout to avoid hanging on unavailable data. Identify protocol checks query remote peer protocols and ensure no bitswap protocol constants are advertised. State includes blockstore data, peer connections, config flags, and daemon startup failures. Dependencies include boxo bitswap protocol constants, harness networking, random bytes, and Kubo config. Risks include timing-based negative retrieval tests and changed error strings. Test signal verifies both data-plane behavior and configuration validation.
