# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/identity.go

Purpose: provides canonical hashing of an entry's `Extended` metadata for lifecycle identity compare-and-swap.

Important API: `HashExtended(ext map[string][]byte) []byte`. It returns nil for empty maps. For non-empty maps, it sorts keys and feeds SHA-256 with length-prefixed key and value bytes.

Control flow/state: pure deterministic function. Length prefixes prevent ambiguous concatenation collisions such as a forged single tag matching a multi-tag map. Sorting removes Go map iteration nondeterminism.

Dependencies/integration: used by both the lifecycle worker capturing schedule-time identity and the server refetching live entry identity. The bytes must match exactly across both sides for CAS validation.

Risks: any format change is a compatibility change for in-flight lifecycle delete witnesses. Returning nil for empty maps must remain consistent with server-side interpretation of no extended metadata. It hashes all `Extended` keys, not only object tags, so unrelated metadata changes can intentionally invalidate a scheduled delete.

Test signals: `final_cleanup_test.go` covers nil/empty, non-empty, and insertion-order stability; broader identity tests in s3api are referenced by comments.
