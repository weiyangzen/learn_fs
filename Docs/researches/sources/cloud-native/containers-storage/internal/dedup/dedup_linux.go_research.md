<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/dedup/dedup_linux.go -->
# sources/cloud-native/containers-storage/internal/dedup/dedup_linux.go

## Purpose
This Linux implementation provides inode tracking, file reading, and `FIDEDUPERANGE` ioctl support for deduplication.

## Important APIs, Types, And Functions
`deviceInodePair` keys visited files by device and inode. `dedupFiles` stores a mutex-protected visited set. `newDedupFiles`, `recordInode`, `isFirstVisitOf`, `dedup`, and `readAllFile` implement platform operations.

## Control Flow
`isFirstVisitOf` extracts `syscall.Stat_t` and records the inode. `dedup` opens source read-only and destination write-only, rejects hardlinks by comparing device/inode, builds `unix.FileDedupeRange`, and calls `unix.IoctlFileDedupeRange`; `ENOTSUP` is normalized to `errNotSupported`. `readAllFile` reads small files into memory and mmaps larger files with sequential madvise before hashing.

## State And Persistence
Visited inode state is in-memory. Successful ioctl calls modify filesystem extent sharing for destination files.

## Dependencies And Integration Points
`dedup.go` calls these methods while walking driver layer directories. The code depends on Linux file dedupe ioctl support and `golang.org/x/sys/unix`.

## Risks And Edge Cases
Mmap of large files can fail; small-file reads assume stable file size from `fs.FileInfo`. Destination files are opened write-only because the ioctl targets their fd. The function reports unsupported reflinks as benign to the caller, but other ioctl errors abort dedup.

## Test Signals
`dedup_linux_test.go` verifies inode recording and repeat detection, including separate device/inode pairs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/dedup/dedup_linux.go -->
