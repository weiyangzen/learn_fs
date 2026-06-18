# Research: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/iceberg_pagination_test.go

## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/iceberg_pagination_test.go

Purpose: tests for Iceberg REST pagination query parsing.

Important tests: `TestParsePaginationDefaultValues` expects empty token and default page size. `TestParsePaginationUsesCamelCaseParameters` accepts `pageToken` and `pageSize`. `TestParsePaginationSupportsHyphenatedFallback` accepts `page-token` and `page-size`. `TestParsePaginationRejectsInvalidPageSize` rejects zero, negative, nonnumeric, and values above the maximum.

State and dependencies: tests use `httptest` requests only. Integration points are list namespaces and list tables handlers, which forward page token and page size to S3 Tables manager as continuation token/max results. Risks covered include client compatibility across camelCase and hyphenated Iceberg parameter spellings and preventing oversized list requests. Test signal is direct for helper boundaries.
