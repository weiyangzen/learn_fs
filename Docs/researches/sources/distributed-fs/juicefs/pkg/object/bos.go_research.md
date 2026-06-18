# sources/distributed-fs/juicefs/pkg/object/bos.go

## Purpose
`bos.go` implements the Baidu BOS object storage backend with storage class/tag support and multipart upload/copy support.

## Important APIs, Types, and Functions
`bosclient` embeds `DefaultObjectStorage` and `tierStorage`, stores the bucket and BOS client, and implements object APIs plus multipart APIs: `Limits`, `CreateMultipartUpload`, `UploadPart`, `UploadPartCopy`, `AbortUpload`, `CompleteUpload`, and `ListUploads`. Helpers are `autoBOSEndpoint` and `newBOS`.

## Control Flow and State
`Create` creates the bucket and optionally sets default storage class, ignoring already-exists errors. `Head` maps BOS 404 to `os.ErrNotExist`. `Get` selects ranged or full reads; full reads verify checksum using user metadata or BOS CRC32. `Put` materializes the reader into bytes, applies tier storage class and encoded tags, and uploads. `Copy` applies storage class and optional tag replacement. `List` clamps limit to 1000, includes common prefixes for delimiter listings, and sorts mixed entries. Multipart methods map JuiceFS parts to BOS upload APIs.

## State and Persistence Behavior
Persistent state lives in BOS buckets, objects, object metadata/tags, and multipart upload state. Local state is the bucket name, BOS client, and tier config. `newBOS` can auto-discover bucket location from `bcebos.com`, uses environment credentials if explicit credentials are absent, disables SDK retries, and sets JuiceFS user agent.

## Dependencies and Integration Points
It depends on Baidu BCE/BOS SDK packages, JuiceFS checksum helpers, tier/tag utilities, object multipart abstractions, and storage registration via `Register("bos", newBOS)`.

## Risks and Test Signals
Risks include memory pressure from buffering entire `Put` readers, checksum compatibility, endpoint auto-location failures, no SDK retry policy, tag directive behavior during copy, delete string matching for `NoSuchKey`, and multipart part-size boundaries. Tests should cover create existing bucket, storage class/tag put/copy, checksum-verified get, delimiter list ordering, multipart upload/copy/abort/complete, and environment credential fallback.
