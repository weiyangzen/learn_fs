# sources/distributed-fs/ipfs-kubo/test/cli/gateway_limits_test.go

Purpose: integration smoke tests for gateway retrieval timeout, maximum request duration, and concurrent request limiting.

Important APIs/functions: `TestGatewayLimits`, config fields `Gateway.RetrievalTimeout`, `Gateway.MaxRequestDuration`, `Gateway.MaxConcurrentRequests`, `harness.HTTPClient`, and `GatewayClient`.

Control flow: subtests configure short limits, start daemons, verify local content still returns 200, then request a known unavailable CID. Retrieval timeout and absolute request duration expect 504 responses; concurrent limiting starts one blocking request with a one-slot semaphore and expects the next request to return 429 with `Retry-After`, `Cache-Control: no-store`, and an error body.

State/persistence: daemon config, local gateway server, blocking goroutine, and local content blocks.

Dependencies/integration: gateway middleware for timeout/rate limiting, content routing stalls for nonexistent CIDs, HTTP response headers, and harness client behavior.

Risks/test signals: timing-sensitive but deterministic enough through low limits and blocking CID. It is basic integration coverage; boxo middleware unit tests cover deeper cases.
