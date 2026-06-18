# sources/distributed-fs/juicefs/pkg/object/restful_test.go

Purpose: tests the custom TCP dialing helpers used by the shared HTTP transport.

Important APIs and types: `startTCPListener` starts a background accept-and-close listener for test endpoints; `getPort` extracts the bound port. Test cases cover `dialParallel` and `splitIPsByVersion`.

Control flow and state: `TestDialParallel_OnlyPrimaries` confirms direct primary dialing succeeds. `TestDialParallel_OnlyFallbacks` documents and protects the case where primary IPs are empty but fallback IPs are available. `TestDialParallel_PrimaryFailsFast_FallbackSucceeds` verifies fallback starts when the primary path fails. `TestDialParallel_BothFail` expects an error. `TestSplitIPsByVersion` checks IPv4/IPv6 partitioning.

Persistence and integration: no object storage is used. The tests bind local TCP ports and exercise network behavior with short dialer timeouts.

Risks and test signals: tests are timing-sensitive but local. They focus on connection selection and panic prevention, not the full `httpClient` transport, DNS cache, TLS, REST request signing, or response cleanup behavior.
