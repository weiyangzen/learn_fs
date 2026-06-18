# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/StorageDirAllocatorView.java

Purpose: Limited storage-directory view for allocators.

Important APIs: Constructor and override `getAvailableBytes`.

Control flow: If the parent tier view is using reserved space, available bytes are computed as capacity minus committed bytes; otherwise it returns the directory's available bytes. This lets internal moves use reserved capacity while normal allocations do not.

State and persistence: View over live `StorageDir`; no independent persistence.

Dependencies and integration: Created by `StorageTierAllocatorView` and consumed by allocators such as `RoundRobinAllocator`.

Risks and test signals: The local `reservedBytes` variable is unused, and available-byte semantics differ sharply based on `mUseReservedSpace`. Tests should cover both reserved and normal modes.
