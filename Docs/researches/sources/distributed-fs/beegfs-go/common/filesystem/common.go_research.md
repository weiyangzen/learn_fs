<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/common.go -->
# sources/distributed-fs/beegfs-go/common/filesystem/common.go

Purpose: shared helpers for ranged file reads/writes and checksums used by filesystem providers.

Important APIs/types/functions: `writeSeekCloser`, `limitedFileWriter`, `newLimitedFileWriter`, `Write`, `Close`, `readFilePart`, and `getFilePartChecksumSHA256`.

Control flow: the limited writer seeks to `offsetStart` on the first write, tracks bytes written, rejects writes that exceed inclusive `[offsetStart, offsetStop]`, delegates accepted writes, and closes exactly once. `readFilePart` seeks then reads a fixed-size buffer. The checksum helper returns base64-encoded SHA-256.

State and persistence: `limitedFileWriter` mutates an underlying file and tracks closed/written state in memory. Reads load the requested file part into memory.

Dependencies and integration points: used by `BeeGFS.ReadFilePart`, `BeeGFS.WriteFilePart`, and mock equivalents. Depends on standard `io`, `os`, `sha256`, and `base64`.

Risks: `readFilePart` uses `file.Read(buf)` once rather than `io.ReadFull`, so short reads can silently return partially filled buffers without an error. Offset validation is absent; negative or inverted ranges can cause seek/read/allocation errors. `ErrNoSpaceForWrite` message includes a trailing space from `errors.go`.

Test signals: `fs_test.go` validates writing multiple fixed ranges and reading/checksumming the full file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/common.go -->
