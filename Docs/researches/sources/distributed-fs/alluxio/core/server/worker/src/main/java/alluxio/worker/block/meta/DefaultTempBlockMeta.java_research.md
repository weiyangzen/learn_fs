# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/DefaultTempBlockMeta.java

Purpose: Metadata for an uncommitted worker block file owned by a session.

Important APIs: Static `tempPath`; getters for size, path, ID, location, parent dir, commit path, session ID; `setBlockSize`.

Control flow: Temp paths are built from storage dir, configured temp folder, `sessionId % SUB_DIR_MAX`, and a file name containing hex session ID plus block ID. Commit path points to the final numeric committed block file.

State and persistence: Keeps mutable temp block size in memory. The temp file persists on disk until commit, abort, or cleanup.

Dependencies and integration: Used by `DefaultStorageDir`, `StoreBlockWriter`, and block store write paths. Reads temp folder configuration statically.

Risks and test signals: Static config values are captured when the class loads. Tests should cover path format, subdirectory distribution, size growth, location medium, and commit path consistency with `DefaultBlockMeta`.
