# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/meta/DefaultBlockMetaTest.java

Purpose: unit tests for `DefaultBlockMeta` path and committed-size behavior.

Important APIs and helpers: setup creates a temporary storage tier and directory through `DefaultStorageTier.newStorageTier`, then constructs a `DefaultTempBlockMeta` and its committed `DefaultBlockMeta`. Tests cover `BlockMeta.getBlockSize()` and `BlockMeta.getPath()`.

Control flow and state: `getBlockSize()` observes the block size through the file at the commit path. With no file content it reports zero; with a short file it reports the actual short length; with a full file it reports the configured target block size. `getPath()` verifies path construction from the block directory and block ID.

Dependencies and integration: depends on `BufferUtils`, `PathUtils`, `TemporaryFolder`, storage-tier/directory metadata, and local filesystem writes.

Risks and test signals: it exercises filesystem-backed size discovery rather than pure metadata only. Coverage is narrow but important for commit-path compatibility and partial-file size reporting.
