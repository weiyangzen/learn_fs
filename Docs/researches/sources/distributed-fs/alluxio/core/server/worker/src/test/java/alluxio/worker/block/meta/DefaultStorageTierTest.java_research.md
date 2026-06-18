# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/meta/DefaultStorageTierTest.java

Purpose: tests `DefaultStorageTier` aggregation of storage directories and tolerance of directory setup failures or misconfiguration.

Important APIs and helpers: setup creates a tier with two temp directories and capacities. Tests cover `getTierAlias`, `getTierOrdinal`, `getCapacityBytes`, `getAvailableBytes`, `getDir`, `getStorageDirs`, tolerant failed directory initialization, tolerant capacity/path misconfiguration, and `removeStorageDir`.

Control flow and state: the tests add block metadata to one directory to observe tier-level available-capacity aggregation. Failure-tolerance cases manipulate config or directory state and verify the tier keeps only usable directories where appropriate. `removeDir` mutates the tier directory list and rejects removing a directory from another tier.

Dependencies and integration: uses `ConfigurationRule`, `TemporaryFolder`, `DefaultStorageTier`, `StorageDir`, and ImmutableList expectations.

Risks and test signals: `getDir(2)` expects `null` despite comments mentioning an exception, which documents current behavior. These tests are useful for startup robustness and tier summary metrics, not for block-store allocation policy.
