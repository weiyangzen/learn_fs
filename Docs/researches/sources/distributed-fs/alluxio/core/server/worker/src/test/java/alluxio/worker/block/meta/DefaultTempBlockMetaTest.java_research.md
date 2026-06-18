# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/meta/DefaultTempBlockMetaTest.java

Purpose: unit tests for `DefaultTempBlockMeta` path derivation, session ownership, and mutable size.

Important APIs and helpers: setup creates a temporary storage tier/directory and a `DefaultTempBlockMeta`. Tests cover `getPath`, `getCommitPath`, `getSessionId`, and `setBlockSize`.

Control flow and state: path tests assert temp block files live under a per-session temporary path while commit paths resolve to the final block path. The size test confirms the metadata starts at the configured size and can be set to smaller or larger values.

Dependencies and integration: depends on `DefaultStorageTier`, `StorageDir`, `PathUtils`, and JUnit temp directories.

Risks and test signals: narrow coverage documents file naming conventions needed by writers and commit flows. It does not validate storage-dir byte accounting; that is covered by `DefaultStorageDirTest`.
