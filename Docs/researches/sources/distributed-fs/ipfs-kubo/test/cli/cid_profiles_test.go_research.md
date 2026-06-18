# sources/distributed-fs/ipfs-kubo/test/cli/cid_profiles_test.go

Purpose: deterministic IPIP-499 UnixFS import profile test vectors for legacy `unixfs-v0-2015`, recommended `unixfs-v1-2025`, and the current default profile. It verifies CID version, hash, raw leaf behavior, chunk thresholds, max-link rebalancing, and HAMT directory sharding thresholds.

Important APIs/types/functions: `cidProfileExpectations`, profile fixtures `unixfsV02015`, `unixfsV12025`, `defaultProfile`, `TestCIDProfiles`, `runProfileTests`, helpers `verifyCIDVersion`, `verifyHashFunction`, `verifyRawLeaves`, `getBlockSize`, size/seed helpers, `TestDefaultMatchesExpectedProfile`, and `TestProtobufHelpers`.

Control flow: for each profile, subtests initialize nodes with profile args, add deterministic data at exact boundary sizes, inspect PB nodes and UnixFS data types, compare known CIDs, optionally export CARs via `CID_PROFILES_CAR_OUTPUT`, and build threshold-sized directories with testutils helpers.

State/persistence: creates large deterministic files, temporary directories with thousands of entries, daemon-backed blockstores, and optional CAR artifacts. Tests are parallel and isolated per repo.

Dependencies/integration: `harness`, `testutils`, UnixFS protobuf helpers, `boxo/ipld/unixfs`, `cid format`, `block stat`, `dag export`, and profile initialization.

Risks/test signals: high-value compatibility gate for future default/profile changes. It is expensive, including a 1 GiB synthetic v1 max-link case and thousands of file creations; expected CIDs must be updated intentionally when import semantics change.
