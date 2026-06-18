# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/reviewer/MockReviewer.java

Purpose: test-only `Reviewer` implementation that deterministically rejects allocation into directories with selected available-byte values.

Important APIs and helpers: `resetBytesToReject(Set<Long>)` replaces the static rejection set. `acceptAllocation(StorageDirView)` reads `dirView.getAvailableBytes()` and returns false when that value is present in the set.

Control flow and state: all instances share the static `BYTES_TO_REJECT` set. Tests can reconfigure rejection criteria before exercising allocation decisions without needing random probability or real disk pressure.

Dependencies and integration: implements `Reviewer`, consumes `StorageDirView`, and uses Guava `Sets` for the mutable static set.

Risks and test signals: static mutable state must be reset between tests to avoid leakage. It is useful for deterministic allocator/reviewer integration tests, but it is not a production reviewer and has no persistence.
