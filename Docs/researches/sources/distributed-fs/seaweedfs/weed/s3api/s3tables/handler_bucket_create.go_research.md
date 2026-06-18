# sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler_bucket_create.go

## Purpose
This file implements `CreateTableBucket`, including request validation, authorization, collision checks with existing S3 buckets, metadata persistence, optional tag persistence, and ARN response generation.

## Important APIs and functions
`handleCreateTableBucket` reads `CreateTableBucketRequest`, validates bucket name, derives the principal, chooses IAM or legacy authorization, checks table/object bucket conflicts, creates directory state, writes `ExtendedKeyTableBucket`, `ExtendedKeyMetadata`, and optional `ExtendedKeyTags`, and returns `CreateTableBucketResponse`.

## Control flow and state behavior
The handler validates JSON and name before authorization. IAM mode uses `shouldUseIAM`, identity policy names, and `authorizeIAMAction`; if IAM denies but zero-config default allow applies without explicit identity actions/policies, it falls back to legacy checks. Legacy permission checks use `CheckPermissionWithContext` against the handler/account owner. The existence check first asks the filer for configured bucket root and then looks up the requested name, distinguishing table bucket entries from ordinary S3 bucket entries. Creation ensures the root path exists, creates the bucket directory, marks it as a table bucket, stores JSON metadata with owner principal and creation time, and stores request tags if present.

## Dependencies and integration points
The file integrates with validation/path helpers (`validateBucketName`, `GetTableBucketPath`), filer ops, S3 constants for bucket root, IAM and legacy permission code, and metadata types from `utils.go`.

## Risks and edge cases
The check-then-create sequence is not atomic; concurrent creates can race between lookup and `CreateEntry`. Metadata and marker attributes are written as separate updates, so partial creation can leave a directory without all attributes if later writes fail. Owner selection under legacy default allow may differ from request principal. Collision checks depend on `IsTableBucketEntry` marker correctness.

## Test signals
No test file in this subset targets creation directly. Adjacent S3 Tables tests and permission tests should cover validation/authorization, but this path would benefit from race/partial-failure tests.
