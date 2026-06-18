# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/BlockPageIdTest.java

Purpose: tests identity, hashing, parsing, and downcast behavior for `BlockPageId`.

Important APIs and helpers: tests cover constructors from numeric and string file IDs, equality with parent `PageId`, set-key behavior, inequality with another subclass, hash-code consistency, `getBlockId`, `getBlockSize`, `downcast`, and malformed file IDs. `MoreFieldsPageId` models a conflicting subclass.

Control flow and state: valid file IDs use the `paged_block_<hex>_size_<hex>` encoding, including a negative block ID represented as all hex f's. Invalid cases cover bad prefix, insufficient digits, empty ID, extra suffix, and negative block size.

Dependencies and integration: depends on Alluxio cache `PageId`, Guava collection helpers, and JUnit exception assertions.

Risks and test signals: strong compatibility signal for file ID encoding used by paged block store metadata. It intentionally verifies cross-class equality with raw `PageId`, which is important for map/set lookups.
