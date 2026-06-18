# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/acp_permisson.go

Purpose: defines S3 ACL permission string values.

Important APIs and values: `PermissionFullControl`, `PermissionRead`, `PermissionWrite`, `PermissionReadAcp`, and `PermissionWriteAcp`.

Control flow: no functions.

State and persistence: mutable package variables only.

Dependencies and integration: used by canned ACL grants and ACL parsing/serialization.

Risks: filename contains `permisson` typo, so discovery by expected spelling can be awkward. Variables are mutable and should be treated as constants by callers.

Test signals: no direct tests in this subset.
