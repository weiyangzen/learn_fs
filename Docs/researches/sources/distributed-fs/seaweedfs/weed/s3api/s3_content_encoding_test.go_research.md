# sources/distributed-fs/seaweedfs/weed/s3api/s3_content_encoding_test.go

Purpose: regression tests ensuring `Content-Encoding` and `Content-Language` metadata survive S3 PUT metadata parsing and GET response header emission.

Important APIs and functions: `TestContentEncodingPreservation` and `TestContentEncodingWithOtherHeaders` exercise `ParseS3Metadata` and `S3ApiServer.setResponseHeaders`.

Control flow: tests build PUT requests with content encoding/language and other standard headers, parse metadata, build mock filer entries with `Extended` metadata, then call `setResponseHeaders` and assert expected HTTP response headers.

State and persistence: simulates persistence by placing parsed metadata into a `filer_pb.Entry.Extended` map. No real filer is used.

Dependencies and integration: uses `S3ApiServer`, S3 metadata parsing, filer protobuf entries, and standard response header handling.

Risks: these tests guard standard headers only; any metadata filtering changes in `ParseS3Metadata` or `setResponseHeaders` can regress client-visible object behavior.

Test signals: direct coverage for issue-class regressions around compressed objects and language/cache/disposition metadata.
