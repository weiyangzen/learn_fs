# sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine_test.go

Purpose: main policy-engine test suite covering policy lifecycle, condition operators, validation, wildcard matching, request context extraction, existing object tags, and multipart permission inheritance.

Important APIs and functions: tests exercise `NewPolicyEngine`, `SetBucketPolicy`, `GetBucketPolicy`, `DeleteBucketPolicy`, `EvaluatePolicy`, `ParsePolicy`, `CompilePolicy`, `BuildResourceArn`, `BuildActionName`, `EvaluatePolicyForRequest`, `GetConditionEvaluator`, `ExtractConditionValuesFromRequest`, and object tag helpers.

Control flow: the suite installs representative policies, evaluates explicit allow, explicit deny, and non-matching indeterminate cases, then checks helper behavior. Existing object tag tests build `entry.Extended`-style maps with `s3_constants.AmzObjectTaggingPrefix`. Multipart tests verify all multipart upload action constants inherit `s3:PutObject` matching on object ARNs while unrelated actions do not.

State and persistence: test state is per-engine in memory. The helper `tagsToEntry` mirrors object metadata rather than using a filer.

Dependencies and integration: validates integration among `engine.go`, `conditions.go`, `types.go`, `s3_constants`, and wildcard utilities.

Risks: source IP tests encode trust behavior for forwarded headers; deployment assumptions must match that behavior. Multipart inheritance deliberately expands `PutObject` semantics and must stay aligned with S3 IAM expectations.

Test signals: broad unit-level confidence for policy parsing/evaluation and several security regressions, including tag-based deny and action inheritance.
