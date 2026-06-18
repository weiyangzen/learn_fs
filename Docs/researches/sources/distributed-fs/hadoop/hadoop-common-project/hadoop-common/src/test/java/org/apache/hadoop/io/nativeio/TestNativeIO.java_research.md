# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/nativeio/TestNativeIO.java

## Purpose
`TestNativeIO` exercises Hadoop native I/O wrappers across POSIX, Windows, memory mapping, file-copy, and persistent-memory paths. It verifies JNI/native method availability, error translation, platform-specific semantics, and concurrency safety.

## Important APIs, Types, and Functions
The tests use `NativeIO.POSIX.getFstat()`, `getStat()`, `open()`, `chmod()`, `posix_fadvise()`, `sync_file_range()`, `getUserName()`, `getGroupName()`, `mlock()`, `munmap()`, POSIX constants, and `NativeIO.POSIX.Pmem` mapping/copy/sync APIs. Windows paths use `NativeIO.Windows.createFile()`, `setFilePointer()`, and `access()`. Cross-platform helpers include `NativeIO.renameTo()`, `NativeIO.copyFileUnbuffered()`, and `NativeIO.getMemlockLimit()`. `doStatTest()` centralizes stat validation against `StatUtils.getPermissionFromProcess()`.

## Control Flow
Two `@BeforeEach` hooks skip tests unless native code is loaded and reset `TEST_DIR`. The suite then branches by platform assumptions: POSIX-only tests cover open/chmod/fadvise/user lookup/constants; Windows-only tests cover file pointer, share-delete create, long-path access checks; common tests cover stat, rename, sync range, memory lock, unbuffered copy, and PMDK-gated persistent memory. Multi-threaded stat and fstat tests repeatedly issue native calls from thread pools or `SubjectInheritingThread`s and propagate any observed exception.

## State and Persistence
State is temporary filesystem state under `testnativeio`, `renameTest`, `/dev/zero`, and PMDK paths such as `/mnt/pmem0/...` when PMDK is available. Native file descriptors are opened and closed through Java streams. Persistent-memory tests create mapped files and explicitly delete some error-path files.

## Dependencies and Integration Points
The file integrates with Hadoop `NativeCodeLoader`, `NativeIOException`/`Errno`, local `FileSystem`, `FsPermission`, `PathIOException`, `StatUtils`, Apache Commons IO cleanup, and platform assumption helpers. It directly tests Hadoop's bridge to OS syscalls and native libraries.

## Risks and Edge Cases
Many tests are platform and environment sensitive. PMDK tests assume a configured `/mnt/pmem0` device and 16 GB volume model when `isPmdkAvailable()` is true. `testCopyFileUnbuffered()` allocates and maps a 128 MB file. Error assertions differ for Windows messages versus POSIX `Errno`. Concurrency tests may reveal native library thread-safety problems in user/group lookup.

## Test Signals
Signals include matching stat owner/group/mode with OS commands, expected `Errno` for closed or missing descriptors, no descriptor leaks over 10,000 opens, correct Windows access behavior including long paths, successful mlock/copy/PMDK byte round trips, and all native constants being initialized.
