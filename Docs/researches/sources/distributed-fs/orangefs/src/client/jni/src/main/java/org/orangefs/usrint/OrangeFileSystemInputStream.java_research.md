# sources/distributed-fs/orangefs/src/client/jni/src/main/java/org/orangefs/usrint/OrangeFileSystemInputStream.java
## sources/distributed-fs/orangefs/src/client/jni/src/main/java/org/orangefs/usrint/OrangeFileSystemInputStream.java

**Purpose:** Provides an `InputStream` facade over OrangeFS using `OrangeFileSystemInputChannel`, opening the file through JNI POSIX calls and exposing Java stream-style read, seek, skip, available, and close operations.

**APIs and control flow:** The constructor opens `path` with `O_RDONLY`, computes `fileSize` by seeking to end then back to start, and creates the input channel. `read()` delegates to the byte-array overload. `read(byte[], int, int)` wraps the supplied array in a `ByteBuffer` and delegates to channel read; nonpositive returns are normalized to EOF. `available()` subtracts channel `tell()` from stored `fileSize`. `seek(long)` rejects `pos >= fileSize` and forwards to channel seek. `skip(long)` clamps to available bytes, then calls `inChannel.seek(n)`.

**State and dependencies:** Stores the singleton `Orange`, POSIX flags, source path, immutable file size snapshot, and one input channel. Depends on `PVFS2POSIXJNI.open/lseek`, native descriptors, and Java `InputStream` semantics.

**Risks and tests:** `skip(n)` appears to seek to absolute offset `n`, not current position plus `n`, which diverges from `InputStream.skip`. `available()` casts a long to int and uses a stale file size snapshot. Seeking exactly to EOF is rejected. `mark` is unsupported. Test signals should include skip from nonzero offsets, zero-length reads, close idempotence, EOF behavior, and files whose size changes after open.
