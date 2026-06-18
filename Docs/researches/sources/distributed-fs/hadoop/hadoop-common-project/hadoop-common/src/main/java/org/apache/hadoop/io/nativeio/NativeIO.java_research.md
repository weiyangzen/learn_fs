<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/nativeio/NativeIO.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/nativeio/NativeIO.java

## Purpose
`NativeIO` centralizes JNI-backed filesystem, memory, cache, and platform-specific I/O operations that Java did not historically expose directly. It provides POSIX wrappers, Windows wrappers, persistent-memory helpers, owner/stat lookup, secure file creation, rename/link/copy helpers, and fallbacks when native code is unavailable.

## Important APIs and Types
`NativeIO.POSIX` exposes open/stat/chmod/fadvise/sync_file_range/mlock/mmap/munmap, PMDK support state, `Pmem`, `PmemMappedRegion`, `CacheManipulator`, and `Stat`. `NativeIO.Windows` exposes CreateFile-style constants, file/directory creation with mode, share-delete descriptors, access checks, and working-set extension. Top-level methods include `isAvailable`, `getOwner`, `getShareDeleteFileDescriptor`, `getCreateForWriteFileOutputStream`, `renameTo`, `link`, and `copyFileUnbuffered`.

## Control Flow
Three static initialization paths attempt JNI initialization: POSIX nested initialization, Windows nested initialization, and top-level initialization. They check `NativeCodeLoader.isNativeCodeLoaded`, call native init methods, set `nativeLoaded`, and log advisory diagnostics on failure. POSIX operations generally check native support, translate Windows-specific errors where needed, and cache capability fallbacks when native symbols are missing. File creation chooses POSIX `open(O_CREAT|O_EXCL)` or Windows `CreateFile(CREATE_NEW)`. `copyFileUnbuffered` uses a native Windows path when possible and otherwise loops `FileChannel.transferTo` until all bytes are copied.

## State and Persistence
Static state includes native-loaded flags, fadvise/sync-file-range capability booleans, PMDK support state, configurable UID/group name cache timeouts, concurrent ID/name caches, and a lazily initialized top-level UID cache. Persistent effects include chmod, file creation, directory creation, hard links, rename, mmap/pmem mapping, unbuffered copy, cache hints, and memory locking.

## Dependencies and Integration Points
The class integrates with Hadoop `NativeCodeLoader`, `Shell`, `CommonConfigurationKeys`, `HardLink`, `PathIOException`, `SecureIOUtils.AlreadyExistsException`, `CleanerUtil`, and `PerformanceAdvisory`, plus JDK `FileDescriptor`, channels, direct buffers, `Unsafe`, and platform JNI implementations in libhadoop.

## Risks and Edge Cases
Native and nested `nativeLoaded` flags are separate; callers must use the right availability check for the operation. Some fallbacks silently no-op after `UnsatisfiedLinkError` or `UnsupportedOperationException`, which avoids crashes but can hide missing OS optimizations. `getShareDeleteFileDescriptor` on non-Windows creates a `RandomAccessFile` and returns only its descriptor, making lifecycle ownership subtle. `copyFileUnbuffered` can spin if `transferTo` returns zero while bytes remain. UID cache configuration is read lazily and separately from POSIX cache configuration. `sun.misc.Unsafe` and manual unmap remain portability risks.

## Test Signals
Tests should run with native code available and unavailable, POSIX and Windows-specific mappings, secure create existing-file translation, chmod/stat owner lookup, fadvise/sync fallback disablement, direct and non-direct mlock, unmap unsupported paths, hard-link fallback, `transferTo` partial-copy loops, and PMDK support-state messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/nativeio/NativeIO.java -->
