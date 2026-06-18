# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/ListMultipartUploadsResult.java

## Purpose
`ListMultipartUploadsResult` is the XML response model for S3 multipart upload listing. It converts multipart metadata file statuses into upload entries for a specific bucket.

## Important APIs, Types, and Functions
`buildFromStatuses(String bucket, List<URIStatus> children)` is the main factory. It filters statuses by xAttrs `UPLOADS_BUCKET_XATTR_KEY` and `UPLOADS_OBJECT_XATTR_KEY`, maps matching entries to nested `Upload` objects, and returns a result. Accessors expose XML `Bucket` and repeated unwrapped `Upload` entries. `Upload` exposes `Key`, `UploadId`, and `Initiated`.

## Control Flow, State, and Persistence
The factory streams over metadata statuses, skips entries missing required xAttrs with a warning, filters to the requested bucket by xAttr value, uses status name as upload ID, formats last modification time as initiation time, and stores the resulting list. No persistent state is changed.

## Dependencies and Integration Points
It integrates Alluxio metadata xAttrs used by S3 multipart upload bookkeeping with Jackson XML serialization and S3 date formatting.

## Risks
The TODO notes unsupported fields such as `MaxUploads`, upload markers, and next markers, so pagination is incomplete. Entries with malformed or missing metadata are silently skipped except for logs. Character-set assumptions depend on `S3Constants.XATTR_STR_CHARSET`.

## Test Signals
Signals should cover filtering by bucket xAttr, skipping missing metadata, upload ID from status name, initiation date formatting, empty result behavior, and future pagination when implemented.
