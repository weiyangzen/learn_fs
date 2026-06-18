# Research: sources/distributed-fs/seaweedfs/weed/s3api/filer_multipart_etag_test.go

## sources/distributed-fs/seaweedfs/weed/s3api/filer_multipart_etag_test.go

Purpose: regression tests for multipart ETag behavior when SeaweedFS has both an S3-stored ETag in `Entry.Extended[s3_constants.ExtETagKey]` and a filer-derived MD5 in `Entry.Attributes.Md5`. The tests pin the S3 compatibility rule that part validation and final multipart ETag calculation prefer the stored S3 part ETags, with MD5 fallback only when stored metadata is empty.

Important APIs and flow: `TestGetEtagFromEntryPrefersStoredExtendedETag` calls `getEtagFromEntry` and `validateCompletePartETag` against a synthetic `filer_pb.Entry`; `TestGetEtagFromEntryFallbacksToFilerETag` checks empty stored ETag fallback; `TestCalculateMultipartETagUsesStoredPartETags` verifies `calculateMultipartETag` uses stored part ETags. Helpers `newMultipartETagTestEntry`, `expectedMultipartETagForTest`, and `mustDecodeHexETagForTest` model AWS multipart ETag assembly by concatenating decoded part ETags and appending `-partCount`.

State and persistence: no durable writes occur, but the tests model persisted filer metadata fields. Dependencies are `filer_pb.Entry`, S3 constants, `crypto/md5`, and hex/string utilities. Integration point is the multipart complete path, especially ETag comparison from client CompleteMultipartUpload XML. Risk: changing ETag precedence can break clients that uploaded encrypted, copied, or otherwise non-MD5 parts. Test signal is focused and strong for precedence, fallback, and final multipart hash inputs.
