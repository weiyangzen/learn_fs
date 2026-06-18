# sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine.go

Purpose: provides the runtime bucket policy engine: storing compiled policies per bucket, evaluating requests with AWS-style explicit-deny precedence, deriving request condition context, substituting policy variables, and building S3 ARNs/actions.

Important APIs and types: `PolicyEngine` owns bucket contexts behind an RW mutex. `SetBucketPolicy`, `GetBucketPolicy`, `DeleteBucketPolicy`, `HasPolicyForBucket`, `ClearAllPolicies`, and `GetAllBucketsWithPolicies` manage policy state. `EvaluatePolicy` and `EvaluatePolicyForRequest` are the primary evaluation APIs. `PolicyEvaluationResult` distinguishes deny, allow, and indeterminate. Helpers include `SubstituteVariables`, `ExtractPrincipalVariables`, `ExtractConditionValuesFromRequest`, `BuildResourceArn`, `BuildActionName`, `IsMultipartContinuationAction`, and `injectSSEForMultipart`.

Control flow: `SetBucketPolicy` parses and compiles JSON, then swaps the bucket context. `EvaluatePolicy` returns indeterminate if no bucket policy exists. `evaluateCompiledPolicy` scans statements, returning deny immediately on matching explicit deny, remembering any explicit allow, and otherwise returning indeterminate for IAM fallback. `evaluateStatement` checks action, resource or `NotResource`, principal, and conditions. Multipart actions can inherit `s3:PutObject` authorization, and UploadPart/UploadPartCopy can inherit SSE condition values from CreateMultipartUpload.

State and persistence: bucket policies are only in-memory compiled contexts here. Persistence is handled by higher S3 bucket policy plumbing outside this file.

Dependencies and integration: integrates with `types.go` compiled statements, `conditions.go`, SeaweedFS logging, HTTP requests, and S3 IAM/bucket-policy callers. `ExtractConditionValuesFromRequest` populates `aws:SourceIp`, transport, time, list prefix/delimiter/max-keys, auth type, method, and `x-amz-*` headers.

Risks: forwarded IP headers are trusted only when `RemoteAddr` is private/loopback, but deployments behind non-private proxies need care. `SubstituteVariables` inserts raw claim text, so policy safety depends on wildcard/ARN pattern semantics rather than sanitization. `PolicyEngine.evaluateStatement` is richer than `CompiledStatement.EvaluateStatement` in `types.go`; callers must use the engine path for conditions, dynamic variables, and `NotResource`.

Test signals: broad tests validate allow/deny/indeterminate behavior, request extraction, forwarded IP precedence, resource/action construction, variables, folder isolation, `NotResource`, existing object tags, and multipart SSE.
