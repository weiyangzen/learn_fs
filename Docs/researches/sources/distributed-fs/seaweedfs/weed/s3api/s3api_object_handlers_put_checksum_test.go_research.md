# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_put_checksum_test.go

Purpose: this focused test file validates S3 additional checksum algorithm detection for PUT-style requests, including presigned URL behavior where AWS SDKs hoist checksum headers into query parameters.

Important APIs/types/functions: tests call `detectRequestedChecksumAlgorithm`, `parseRequestQuery`, and `lookupHeaderOrQuery`. They assert `ChecksumAlgorithm` enum values and canonical header names from `s3_constants`, plus `s3err.ErrInvalidRequest` for unsupported algorithms.

Control flow: `TestDetectRequestedChecksumAlgorithm` builds `httptest` PUT requests and mutates either headers or query parameters. Cases cover `x-amz-sdk-checksum-algorithm`, `x-amz-checksum-algorithm`, presigned query variants with mixed/lowercase keys, individual checksum value presence, unsupported `MD5`, and no checksum. `TestLookupHeaderOrQueryCaseInsensitive` verifies fallback query matching uses case-insensitive key comparison.

State and persistence behavior: no persistence is performed. The tests protect the pre-write detection phase that controls whether `putToFiler` wraps the data reader in a checksum hash and later stores `ExtChecksumAlgorithm` and `ExtChecksumValue` in filer entry metadata.

Dependencies and integration points: depends on `net/http/httptest`, S3 checksum constants, and S3 error codes. It integrates directly with `putToFiler` because that function parses the request query once, calls `detectRequestedChecksumAlgorithmQ`, verifies expected checksums, stores checksum metadata, and returns checksum response headers through `SSEResponseMetadata`.

Risks: the tests cover detection but not the full body checksum verification path or storage of checksum metadata. They also do not cover `x-amz-trailer` comma-separated values, CRC64NVME, CRC32C, or precedence when multiple checksum hints are present. Detection order is deterministic in production; tests should be expanded if API compatibility requires detailed precedence guarantees.

Test signals: strong regression signal for issue-style presigned URL checksum support and for case-insensitive query lookup. It ensures unsupported requested algorithms fail before upload rather than silently falling back to no checksum.
