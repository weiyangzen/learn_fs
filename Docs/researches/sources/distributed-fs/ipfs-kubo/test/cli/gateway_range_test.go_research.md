# sources/distributed-fs/ipfs-kubo/test/cli/gateway_range_test.go

Purpose: verifies gateway range and directory responses for HAMT-sharded UnixFS fixtures with only minimal required blocks imported.

Important APIs/functions: `TestGatewayHAMTDirectory`, `TestGatewayHAMTRanges`, `IPFSDagImport`, `GatewayClient`, fixture CAR files, and HTTP `Range` headers.

Control flow: each test starts an empty offline test-profile node, imports a fixture CAR by expected root, then performs gateway reads. Directory listing of a 10k-item HAMT should succeed with minimal refs. Range subtests request two byte ranges from a large HAMT-sharded file and a multi-range request, expecting 206, exact `Content-Range`, and only the first range body for multi-range.

State/persistence: fixture CAR blocks imported into a temporary repo; daemon runs offline.

Dependencies/integration: trustless/offline gateway block traversal, HAMT directory/file resolution, byte-range serving, fixture integrity, and HTTP header processing.

Risks/test signals: strong regression for over-fetching and range traversal. Fixture CIDs and files are hard-coded and must stay aligned.
