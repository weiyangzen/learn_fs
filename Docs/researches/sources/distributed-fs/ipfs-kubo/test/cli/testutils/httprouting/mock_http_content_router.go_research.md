# sources/distributed-fs/ipfs-kubo/test/cli/testutils/httprouting/mock_http_content_router.go

Purpose: implements a thread-safe in-memory mock for the IPFS HTTP routing v1 server interfaces used by CLI routing tests.

Important APIs and types: `MockHTTPContentRouter` stores call counters, provider records, peer records, and a debug flag behind a mutex. It implements `FindProviders`, `ProvideBitswap`, `FindPeers`, `GetIPNS`, `PutIPNS`, `NumFindProvidersCalls`, `AddProvider`, and `GetClosestPeers`.

Control flow: lookup methods lock, initialize maps as needed, increment counters, return empty iterators when no records exist, and wrap stored records in `iter.Result` slices. `AddProvider` records provider entries by CID and, when the record is a `*types.PeerRecord`, also indexes it by peer ID for peer lookup. IPNS get/put return `routing.ErrNotSupported`. `GetClosestPeers` derives a peer ID from the CID key and returns matching peer records.

State and persistence: all state is in memory and protected by `sync.Mutex`. It is not persisted and is intended to be scoped to individual tests.

Dependencies and integration points: integrates with `boxo/routing/http/server`, `boxo/routing/http/types`, iterator utilities, `go-cid`, libp2p peer IDs, and routing interfaces. It can back an HTTP routing server in delegated routing tests.

Risks and test signals: the mock only implements the behavior needed by tests and does not model network errors, pagination, or full spec semantics. Call counters are useful for verifying cache/fallback behavior. Interface drift in boxo routing types would surface as compile failures.
