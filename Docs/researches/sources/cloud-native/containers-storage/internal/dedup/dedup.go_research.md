<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/dedup/dedup.go -->
# sources/cloud-native/containers-storage/internal/dedup/dedup.go

## Purpose
`dedup.go` implements platform-independent orchestration for file deduplication by grouping candidate files by checksum and asking platform-specific reflink/dedupe code to share storage.

## Important APIs, Types, And Functions
`DedupHashMethod` supports invalid, CRC64, file size, and SHA256 strategies. `DedupOptions` selects the hash method. `DedupResult` reports total deduped bytes. `getFileChecksum` hashes a file using `readAllFile`. `DedupDirs` walks directories, groups paths by checksum, skips zero-byte and already-visited inodes, and calls `dedupFiles.dedup`.

## Control Flow
`DedupDirs` initializes platform `dedupFiles`, then parallel-walks each directory using `pwalkdir.Walk`. For each regular non-empty file, it checks inode visitation, computes a checksum, locks the checksum bucket, tries deduping against known source paths, and appends as a future source if no dedupe succeeded. `errNotSupported` short-circuits as a non-fatal result.

## State And Persistence
In-memory maps track checksum groups and visited inodes. Persistent effects are filesystem reflink/dedupe operations that can cause duplicate file extents to share storage.

## Dependencies And Integration Points
Overlay and VFS drivers call `DedupDirs` for selected layer directories. The platform-specific files provide inode tracking, checksum reading, and Linux `FIDEDUPERANGE` ioctl behavior.

## Risks And Edge Cases
`DedupHashFileSize` is unsafe as a true content hash and should be used only when callers accept possible false positives guarded by kernel dedupe verification. Hash bucket locking and global result locking are concurrency-sensitive. Some filesystems can return unsupported per-file after walking has begun; this returns current savings with nil error.

## Test Signals
`dedup_linux_test.go` tests inode visit tracking. Full dedupe behavior depends on filesystem support and is not directly covered in the listed tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/dedup/dedup.go -->
