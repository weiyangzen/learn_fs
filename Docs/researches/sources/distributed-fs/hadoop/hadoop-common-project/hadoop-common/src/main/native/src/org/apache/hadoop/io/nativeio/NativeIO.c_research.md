<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/NativeIO.c -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/NativeIO.c

## Purpose
`NativeIO.c` is Hadoop common's broad JNI bridge for native filesystem, file descriptor, permission, memory, and optional persistent-memory operations. It exposes POSIX and Windows operations through Java `NativeIO` inner classes and normalizes native errors into `NativeIOException`.

## Important APIs, Types, and Functions
Initialization APIs include `initNative()`, `initNativePosix()`, and `initNativeWindows()`. POSIX methods include `fstat`, `stat`, `posix_fadvise`, `sync_file_range`, `mlock_native`, `open`, `chmodImpl`, `getUserName`, `getGroupName`, `mmap`, `munmap`, rename/link, memlock-limit, and PMDK methods. Windows methods include file/directory creation with mode, owner lookup, file pointer movement, access checks, working-set extension, unbuffered copy, rename/link wrappers, and security/stat helpers. Internal helpers initialize Java stat classes, NativeIOException classes, errno enum mapping, file descriptor helpers, and optional password/group lookup locking.

## Control Flow
Initialization caches global class references, constructors, file-descriptor fields, errno enum mapping, constants, and optional PMDK state. POSIX wrappers convert Java strings or file descriptors to native values, call one system API, then map failures through `throw_ioe()`. User/group lookup optionally enters `pw_lock_object`, allocates reentrant lookup buffers, retries on `ERANGE`, validates returned pointers, and converts names to Java strings. PMDK methods load libpmem, map/create/unmap/copy/sync persistent memory regions, and construct Java `PmemMappedRegion` objects.

## State and Persistence
Static global references cache Java classes/constructors and `pw_lock_object`. File descriptors and mmap/PMDK addresses persist outside this file after being returned to Java. PMDK loader state persists process-wide. There is no filesystem persistence except operations intentionally performed on caller-specified paths.

## Dependencies and Integration Points
It depends on POSIX syscalls, Windows winutils wrappers, `file_descriptor`, `errno_enum`, `exception`, and optional `pmdk_load`. It is a central integration point for Hadoop Java NativeIO, HDFS short-circuit/persistent memory paths, and platform-specific file permission behavior.

## Risks and Edge Cases
The file has many platform branches, so behavior differs substantially across Unix, FreeBSD, macOS, and Windows. Several PMDK format strings print 64-bit addresses/lengths with `%x`. `pmem_region_deinit()` attempts to delete a method ID as a global reference, which is not a valid JNI reference. `mmap()` does not check pending exceptions from `fd_get()`. User/group lookup depends on correct optional locking for platforms with non-threadsafe NSS behavior.

## Test Signals
Tests should cover init/deinit idempotence, POSIX constants, stat/fstat permission fields, errno enum mapping, file open/chmod/rename/link, fadvise and sync-file-range availability, mlock and memlock limits, mmap/munmap, Windows create/access/owner operations, PMDK supported/unsupported states, and concurrent user/group lookups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/nativeio/NativeIO.c -->
