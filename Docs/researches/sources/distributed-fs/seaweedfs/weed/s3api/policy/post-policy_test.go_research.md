# Research: sources/distributed-fs/seaweedfs/weed/s3api/policy/post-policy_test.go

## sources/distributed-fs/seaweedfs/weed/s3api/policy/post-policy_test.go

Purpose: tests for S3 POST policy parsing/validation, especially stricter X-Amz field handling and prefix-stem policy conditions.

Important helpers: `EncodePath` percent-encodes non-reserved UTF-8 path characters for tests; `buildParsedPolicy` creates expiring policy JSON and calls `ParsePostPolicyForm`. Tests verify unknown condition keys are rejected with useful context, stray `X-Amz-*` fields are rejected except reserved auth fields, exact X-Amz conditions allow matching fields, prefix-stem conditions like `$x-amz-meta-` authorize matching form-field names, value prefixes are enforced, overlapping exact and prefix conditions both apply, multiple prefix stems all apply, and unknown-key errors include policy value.

State and dependencies: tests use `http.Header` as submitted form fields, time-based future expiration, regex/UTF-8 helpers, and string assertions. Integration points are browser-based S3 POST object uploads and SigV4 form auth fields. Risks covered are both over-permissive acceptance of unexpected fields and over-strict rejection of AWS-valid prefix-stem metadata conditions. Test signal is strong for policy edge cases around X-Amz forms.
