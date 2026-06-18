# sources/distributed-fs/orangefs/src/client/jni/src/main/java/org/orangefs/usrint/OrangeFileSystemOutputStream.java
## sources/distributed-fs/orangefs/src/client/jni/src/main/java/org/orangefs/usrint/OrangeFileSystemOutputStream.java

**Purpose:** Provides an `OutputStream` abstraction for writing OrangeFS files from Java, including optional append mode and OrangeFS creation hints for replication, block size, and layout.

**APIs and control flow:** The constructor initializes `Orange`, flags, and `path`, then calls `openWithHints(path, flags, mode, replication, blockSize, layout.getLayout())`. It wraps the returned descriptor in `OrangeFileSystemOutputChannel`. `write(byte[], int, int)` validates null and bounds, wraps the array in a `ByteBuffer`, and delegates to the channel. `write(int)` writes one byte. `flush()`, `tell()`, `getPath()`, and `close()` proxy to the channel.

**State and dependencies:** Holds the native descriptor indirectly through `outChannel`. Depends on JNI POSIX flags, the layout enum, and native OrangeFS hint handling.

**Risks and tests:** Append mode uses `O_APPEND | O_WRONLY` without `O_CREAT`; non-append uses `O_CREAT | O_WRONLY` without explicit truncation, so existing files may retain trailing data. The redundant `if (off < 0) return` is unreachable after bounds validation. Native open hints are not validated on the Java side. Test signals should cover create versus overwrite semantics, append, invalid bounds, layout constants, flush/close propagation, and native open failure paths.
