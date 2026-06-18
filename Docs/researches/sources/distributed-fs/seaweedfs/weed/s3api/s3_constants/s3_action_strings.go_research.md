# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/s3_action_strings.go

Purpose: defines AWS-format S3 action strings used by bucket policy and IAM evaluation.

Important APIs and values: constants cover object operations, object ACL, object tagging, retention/legal hold, multipart upload operations, bucket create/delete/list/version listing, bucket ACL/policy/tagging/CORS/lifecycle/versioning/location/notification/object-lock, and `S3_ACTION_ALL`.

Control flow: no functions.

State and persistence: constants only; policies persist these strings in JSON and metadata.

Dependencies and integration: used by `s3_action_resolver.go`, policy engine multipart action sets, IAM policy definitions, tests, and S3 handlers.

Risks: action spelling must remain AWS-compatible. Resolver and policy tests depend on exact strings, especially case like `s3:GetObjectAcl` and lifecycle names.

Test signals: extensively referenced by action resolver tests, granular security tests, policy tests, and end-to-end IAM tests.
