# sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine_enhanced_test.go

Purpose: tests enhanced policy-variable behavior, especially principal-derived variables and JWT/LDAP claim substitution in resource patterns and conditions.

Important APIs and functions: `TestExtractPrincipalVariables` covers IAM user ARNs, IAM role ARNs, assumed-role ARNs, wildcard principals, and non-ARN principals. `TestSubstituteVariablesWithClaims` checks standard context variables plus `jwt:*` claims. `TestPolicyVariablesWithPrincipalType` verifies condition matching on `aws:principaltype`. `TestPolicyVariablesWithJWTClaims` drives JWT variables in resource ARNs through `PolicyEngine.EvaluatePolicy`. `TestExtractPrincipalVariablesWithAccount`, `TestSubstituteVariablesWithLDAP`, and `TestSubstituteVariablesSpecialChars` cover account extraction, LDAP prefixed/unprefixed fallback, and raw special-character substitution.

Control flow: tests build policies, install them with `SetBucketPolicy`, create `PolicyEvaluationArgs`, and assert allow or indeterminate results when variables match or mismatch. Substitution-only tests call `SubstituteVariables` directly.

State and persistence: all state is per-test in-memory policy engine state. No external persistence.

Dependencies and integration: exercises `engine.go` and `types.go` dynamic-pattern paths. It indirectly validates that policy variables are left intact when unresolved and that claims can be numeric/bool/string formatted.

Risks: the special-character test documents that substitution does not sanitize path traversal-like text. That is acceptable only if downstream policy/resource matching does not treat substituted values as filesystem paths.

Test signals: strong coverage for principal variable extraction and claims substitution, but these tests do not verify automatic population of claims from real authentication middleware.
