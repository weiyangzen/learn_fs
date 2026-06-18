# Research: sources/distributed-fs/seaweedfs/weed/s3api/iam_list_prefix_regression_test.go

## sources/distributed-fs/seaweedfs/weed/s3api/iam_list_prefix_regression_test.go

Purpose: regression tests for list-bucket IAM evaluation when S3 list requests carry `prefix` query parameters. The tests pin AWS semantics: list actions remain bucket-level resources, and prefix scoping belongs in the `s3:prefix` condition rather than in the resource ARN.

Important tests: `TestEvaluateIAMPolicies_ListBucketWithPrefix` ensures `s3:ListBucket` on `arn:aws:s3:::bucket` allows list requests with or without a promoted object prefix. `TestEvaluateIAMPolicies_ListBucketPrefixCondition` checks a `StringLike` `s3:prefix` condition accepts matching prefixes and rejects others. `TestEvaluateIAMPolicies_ListBucketVersionsWithPrefix` verifies version listing resolves to `s3:ListBucketVersions` even with a prefix.

State and dependencies: in-memory policies are installed via `PutPolicy`; synthetic identities and `httptest` requests mirror the post-auth promotion path. Dependencies are `s3_constants.ACTION_LIST`, IAM evaluator internals, and JSON policy construction. Integration points are `authRequestWithAuthType`, list-object/list-versions handlers, and policy engine condition context. Risk covered: using the prefix as the object part of the resource ARN breaks valid bucket list policies. Test signal is targeted at action/resource/condition mapping.
