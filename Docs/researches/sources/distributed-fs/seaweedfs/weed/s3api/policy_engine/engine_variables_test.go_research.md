# sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine_variables_test.go

Purpose: validates AWS policy variables in resource patterns and condition expected values, especially `${aws:username}`.

Important APIs and functions: `TestPolicyVariables` exercises resource variables for object access and condition variables for list prefixes. `TestEvaluatePolicyForRequestVariables` simulates the variable context that `EvaluatePolicyForRequest` should populate from the principal.

Control flow: the tests install policies with `${aws:username}` in object resource ARNs and `s3:prefix` conditions. Matching username/resource or prefix evaluates to allow; mismatches evaluate to indeterminate to allow IAM fallback.

State and persistence: all policy state is in-memory and scoped to each test.

Dependencies and integration: drives `CompilePolicy` dynamic pattern storage, `PolicyEngine.matchesDynamicPatterns`, `EvaluateConditions`, and `SubstituteVariables`.

Risks: the second test manually injects `aws:username` rather than constructing a full HTTP request path through `EvaluatePolicyForRequest`, so it confirms core evaluation more than complete request integration.

Test signals: good coverage for user-home directory policies and list-prefix constraints, which are common S3 isolation patterns.
