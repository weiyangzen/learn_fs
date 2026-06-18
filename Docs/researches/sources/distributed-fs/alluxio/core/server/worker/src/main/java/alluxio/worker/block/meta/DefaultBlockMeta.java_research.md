# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/meta/DefaultBlockMeta.java

Purpose: Thread-safe metadata for a committed Alluxio worker block.

Important APIs: Static `commitPath`; constructors from explicit fields or `TempBlockMeta`; getters for block ID, location, size, path, and parent directory.

Control flow: The temp-block constructor reads the committed file length after the data file has moved, so metadata size reflects actual disk contents.

State and persistence: Immutable references and size. The committed block persists as a numeric file directly under the storage directory path.

Dependencies and integration: Uses `StorageDir`, `StorageTier`, `BlockStoreLocation`, `PathUtils`, and `File`. Stored in `DefaultStorageDir` committed block maps.

Risks and test signals: Size accuracy depends on file move ordering. Tests should cover commit path construction, medium-aware location, temp-to-committed conversion after file creation, and immutability.
