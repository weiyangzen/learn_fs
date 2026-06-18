## sources/distributed-fs/seaweedfs/weed/s3api/tags_test.go

Purpose: verifies URL-decoding behavior for tag headers.

Important test: `TestParseTagsHeader`.

Control flow: table cases parse simple tags, encoded timestamp with spaces/colons, encoded key and value, empty value, encoded slash/exclamation, invalid percent escape, and encoded plus/equals in values. The test checks either an expected error or exact map contents.

State and dependencies: no persistence. Exercises the package-private `parseTagsHeader` function.

Signals and risks: protects issue behavior where encoded timestamps and special values must decode before tag validation/storage. It does not test XML `FromTags` ordering or delegated tag validation limits, which are covered through S3 Tables utilities.
