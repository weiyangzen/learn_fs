# sources/distributed-fs/seaweedfs/weed/s3api/s3api_bucket_policy_arn_test.go

Purpose: Tests AWS-compatible ARN construction for bucket resources and principals.

Important APIs/types/functions: `TestBuildResourceARN` and `TestBuildPrincipalARN`.

Control flow: resource tests cover bucket-only, slash-only object, normal object, and leading-slash object cases. principal tests cover nil/anonymous principals, explicit `PrincipalArn`, anonymous identity/account IDs, normal account/name, missing account defaulting, and missing name defaulting to `unknown`.

State and persistence: no persistent state; only pure helper behavior.

Dependencies and integration: depends on `Identity`, `Account`, `s3_constants.AccountAnonymousId`, `defaultAccountID`, `buildResourceARN`, and `buildPrincipalARN`. These helpers feed bucket policy evaluation and IAM-compatible principal/resource matching.

Risks: does not test URL-escaped object names, wildcard resource construction beyond object strings, STS/JWT-derived principals, or account aliases.

Test signals: good regression protection for policy engine interoperability with AWS-style `arn:aws:s3:::` and `arn:aws:iam::` values.
