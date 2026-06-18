# sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/examples.go

Purpose: build-ignored example and documentation file for policy-engine usage, legacy identity conversion, condition examples, and migration guidance.

Important APIs and values: exports example JSON strings such as `ExampleIdentityJSON`, `ExampleBucketPolicy`, `ExampleTimeBasedPolicy`, `ExampleIPRestrictedPolicy`, `ExamplePublicReadPolicy`, `ExampleCORSPolicy`, `ExampleUserAgentPolicy`, `ExamplePrefixBasedPolicy`, and `ExampleMultiStatementPolicy`. Helper functions include `GetAllExamples`, `ValidateExamplePolicies`, `GetExamplePolicy`, `CreateExamplePolicyDocument`, `PrintExamplePolicyPretty`, `PrintAllExamples`, and example demonstrations for usage, legacy integration, condition operators, and migration.

Control flow: example helpers gather static JSON strings, parse them with `ParsePolicy`, pretty-print with `encoding/json`, or demonstrate runtime calls to `NewPolicyEngine`, `SetBucketPolicy`, and `EvaluatePolicy`.

State and persistence: no production state. The file has `//go:build ignore`, so it is documentation/sample code rather than compiled package code.

Dependencies and integration: refers to policy-engine APIs and legacy migration helpers such as `ConvertIdentityToPolicy` and `NewPolicyBackedIAM`, showing intended integration with identity actions.

Risks: because it is build-ignored, examples can drift from compiled APIs unless explicitly validated by a separate process. The migration text says default deny, while the engine returns indeterminate for no matching bucket policy statement to allow IAM fallback.

Test signals: no direct tests for this file; `ValidateExamplePolicies` can be used manually to check example JSON against current parser rules.
