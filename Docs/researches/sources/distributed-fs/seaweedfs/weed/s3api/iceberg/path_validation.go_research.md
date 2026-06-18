# Research: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/path_validation.go

## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/path_validation.go

Purpose: middleware and helpers that prevent path traversal through Iceberg REST route variables before they are joined into filer paths.

Important APIs: `validateRequestPath` inspects mux vars `prefix`, `namespace`, and `table`. It requires captured values to be non-empty, validates `prefix` with S3 bucket-name rules, validates table and each unit-separator-delimited namespace segment with `isValidNameSegment`, and rejects bad requests before handlers run. `isValidTablePath` checks slash-separated table locations for unsafe segments. `isValidNameSegment` rejects `.`, `..`, embedded `/`, backslash, and NUL, while allowing empty for helper-level use.

State and dependencies: stateless HTTP middleware depending on mux vars and S3 bucket-name validation. Integration points are `Server.RegisterRoutes`, stage-create marker paths, table location builders, and stale-location cleanup. Risks: route cleaning is disabled with `SkipClean(true)`, so this middleware is the front-line defense for `..` in captured vars; helper-level empty segment allowance is safe only when callers separately reject empty captures. Tests cover traversal, unit separator edge cases, empty captures, and helper rules.
