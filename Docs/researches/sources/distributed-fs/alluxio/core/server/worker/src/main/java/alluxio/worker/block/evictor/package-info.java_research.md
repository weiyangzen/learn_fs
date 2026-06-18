# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/package-info.java

Purpose: Package documentation for deprecated block evictor implementations.

Important APIs: No executable APIs. The package-level docs identify the eviction package role.

Control flow: None at runtime.

State and persistence: None.

Dependencies and integration: The package contains `Evictor`, `AbstractEvictor`, `LRUEvictor`, `EvictionPlan`, `BlockTransferInfo`, and helper classes that older block store paths or emulation paths may still reference.

Risks and test signals: Because the package is deprecated, tests should focus on compatibility coverage rather than new feature expansion. Build signals are package Javadoc and import correctness.
