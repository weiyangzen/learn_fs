# Research: sources/distributed-fs/ipfs-kubo/config/http_retrieval.go

Purpose: Defines configuration for HTTP-based block retrieval.

Important APIs/types/functions: `HTTPRetrieval` fields include `Enabled`, allowlist, denylist, worker count, max block size, and TLS insecure skip verify. Defaults set HTTP retrieval enabled, 16 workers, `2MiB` max block size, and TLS verification enabled.

Control flow, state, and persistence: No functions. Values are persisted and consumed by core node bitswap/retrieval setup.

Dependencies and integration points: Related to Bitswap config because HTTP retrieval can supplement or replace libp2p block retrieval in some modes.

Risks and test signals: Allow/deny lists and TLS skip verification have security implications. Max block size must stay aligned with Bitswap protocol limits. No direct tests in this subset.
