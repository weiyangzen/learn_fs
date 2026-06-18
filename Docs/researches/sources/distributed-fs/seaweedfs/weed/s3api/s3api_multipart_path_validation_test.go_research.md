# sources/distributed-fs/seaweedfs/weed/s3api/s3api_multipart_path_validation_test.go

## Purpose
Tests multipart upload id validation for object-bound generated IDs and path traversal rejection.

## Important APIs, Types, And Functions
`TestCheckUploadIDRequiresGeneratedFormat` calls `S3ApiServer.generateUploadID(object)` and `S3ApiServer.checkUploadId(object, uploadID)`. It covers the legacy hash-only format and the newer `hash_randomhex` format.

## Control Flow
For object `dir/object`, the test accepts the generated hash and the current hash plus a 32-character lowercase hex suffix. It rejects wrong object hashes, arbitrary suffixes, uppercase suffixes, short/long suffixes, slash and backslash traversal, suffix traversal, and NUL-containing input.

## State And Persistence
No state is persisted. The test validates local string/path checks before any multipart upload directory access can happen.

## Dependencies And Integration Points
The file targets multipart upload handlers that derive paths below `.uploads` from user-supplied upload ids. It protects callers that later pass upload ids through path-cleaning helpers.

## Risks And Test Signals
The main signal is that upload id validation remains object-bound and traversal-safe. Additional coverage could include URL-escaped traversal, Unicode separators, and direct handler tests for abort/complete multipart requests.
