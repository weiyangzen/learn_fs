# sources/distributed-fs/orangefs/src/client/jni/src/main/java/org/orangefs/usrint/PVFS2POSIXJNI.java
## sources/distributed-fs/orangefs/src/client/jni/src/main/java/org/orangefs/usrint/PVFS2POSIXJNI.java

**Purpose:** Java JNI declaration class for OrangeFS/PVFS POSIX-style operations. It loads native libraries and exposes file, directory, metadata, xattr, sync, and descriptor operations to higher Java wrappers.

**APIs and control flow:** A static initializer loads `libpvfs2.so`, `liborangefs.so`, and `libofs.so` from `JNI_LIBRARY_PATH`, exiting the JVM on failure. The constructor populates `f` via `fillPVFS2POSIXJNIFlags()`. Native methods cover access/chmod/chown, descriptor open/close/dup, lseek/read/write/pread/pwrite, stat/statfs, mkdir/mknod/link/symlink/rename/unlink/rmdir, xattr list/remove, timestamps, sync, umask, and OrangeFS-specific `openWithHints`. `toString()` reflectively dumps fields.

**State and dependencies:** State is the JNI-filled flags object. It depends on native library load order and on Java data carrier classes `Stat`, `Statfs`, and `PVFS2POSIXJNIFlags`; direct I/O uses `ByteBuffer`.

**Risks and tests:** `JNI_LIBRARY_PATH` null produces paths like `null/libpvfs2.so`; load failures call `System.exit(-1)`, which is hostile in libraries and tests. Native signatures must match generated JNI C exactly, including `ByteBuffer` directness and structure field names. Test signals include library-load isolation, flag population, native error mapping, direct and heap buffer behavior, and representative POSIX operations against an OrangeFS mount.
