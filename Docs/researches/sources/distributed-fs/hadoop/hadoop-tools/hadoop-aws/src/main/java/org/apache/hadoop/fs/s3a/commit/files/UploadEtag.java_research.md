# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/files/UploadEtag.java

## Purpose
Serializable storage for the ETag and optional checksum associated with one completed multipart-upload part.

## Important APIs, Types, And Functions
Fields are `etag`, `checksumAlgorithm`, and `checksum`. `fromCompletedPart()` extracts ETag plus the first matching checksum in CRC32, CRC32C, SHA1, SHA256 order of checks. `toCompletedPart()` rebuilds an AWS SDK `CompletedPart` for a supplied part number.

## Control Flow
`SinglePendingCommit.bindCommitData()` converts uploaded `CompletedPart` responses into `UploadEtag`s. Final commit converts them back through `CommitOperations.toPartEtags()` before `CompleteMultipartUpload`.

## State And Persistence
Each instance is Java-serializable and JSON-friendly. Only one checksum algorithm/value pair is stored even though `CompletedPart` can expose multiple checksum fields.

## Dependencies And Integration Points
Integrates with AWS SDK `CompletedPart` and `ChecksumAlgorithm`; used only through persistent commit metadata.

## Risks
If AWS returns multiple checksum fields, later checks overwrite earlier ones in `fromCompletedPart()`. Unknown checksum algorithm strings are ignored when rebuilding `CompletedPart`, retaining only the ETag.

## Test Signals
Round-trip each supported checksum type, null-checksum parts, invalid/unknown algorithm handling, and preservation of part numbering assigned by callers.
