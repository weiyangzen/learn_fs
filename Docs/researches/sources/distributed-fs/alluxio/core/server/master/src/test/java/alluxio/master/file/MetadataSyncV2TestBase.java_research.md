# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/MetadataSyncV2TestBase.java

## Purpose
Shared base class for Metadata Sync V2 tests that need S3-compatible UFS mounts. It configures S3Proxy or real S3 clients, exposes common bucket/mount constants, provides no-sync/list-sync contexts, and centralizes sync-stat and UFS-vs-Alluxio comparison helpers.

## Important APIs/types/functions
- Extends `FileSystemMasterTestBase`.
- Defines bucket constants, mount URI constants, test content strings, and `TIMEOUT_MS`.
- JUnit `@Rule` `S3ProxyRule` supplies transient S3-compatible object storage.
- `before()` configures S3 properties and creates two buckets; `after()` shuts clients and proxy down.
- Context helpers: `listSync`, `listNoSync`, `getNoSync`, static `existsNoSync`.
- S3 lifecycle helpers: `stopS3Server`, `startS3Server` use reflection into `S3ProxyRule`.
- Validation helpers: `checkUfsMatches`, `listUfsPath`, `assertSyncOperations` overloads, and `assertSyncFailureReason`.

## Control flow
- Setup branches on `mUseRealS3`: real AWS clients or local S3Proxy endpoint with path-style access and configured Alluxio S3 keys.
- `checkUfsMatches` does stack-based traversal: list Alluxio children without sync, list S3 children/prefixes with delimiter, compare normalized paths, and push directories for further checking.
- `listUfsPath` pages S3 `ListObjectsV2`, merges common prefixes and objects, filters descendants, sorts/distincts, and maps S3 keys to Alluxio paths.
- `assertSyncOperations(TaskGroup)` aggregates per-task atomic operation counters before comparing all enum counts, including zero-default operations.

## State and persistence behavior
- Manages external S3Proxy server resources and AWS SDK v1/v2 clients.
- Uses configuration global state for S3 endpoints, region, DNS bucket behavior, and listing length.
- Disables permission authorization to focus on metadata sync behavior.

## Dependencies and integration points
- Integrates Alluxio configuration, S3Proxy, AWS SDK v1 and v2, Alluxio file master contexts, path utilities, and mdsync stats types.
- Test subclasses depend on consistent bucket names and mount point constants.

## Risks and edge cases
- Reflection into S3Proxy internals is brittle across library upgrades.
- Global configuration mutation requires `super.after()` cleanup; leakage can affect unrelated tests.
- `checkUfsMatches` assumes sorted Alluxio list order is compatible with sorted S3 item order.
- Real S3 mode is disabled by default but would depend on external credentials/network.

## Test signals
- Provides high-value infrastructure for object-store sync tests and precise operation-count assertions.
- Failure in this base usually indicates environment/configuration breakage rather than a single sync scenario.
