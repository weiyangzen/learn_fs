# sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/types.go

Purpose: defines the policy document model, parsing/validation, compiled statement representation, wildcard compilation, and simpler compiled-policy matching helpers for the S3 bucket policy engine.

Important APIs and types: `StringOrStringSlice` supports JSON string-or-array fields. `PolicyConditions`, `PolicyDocument`, `PolicyStatement`, `PolicyEffect`, and `PolicyEvaluationArgs` model policies and evaluation inputs. `CompiledPolicy` and `CompiledStatement` store compiled regex/wildcard matchers plus dynamic patterns for variables and `NotResource`. Public helpers include `ParsePolicy`, `ValidatePolicy`, `CompilePolicy`, `GetBucketFromResource`, `FastMatchesWildcard`, `NewStringOrStringSlice`, and `CloneStringOrStringSlice`.

Control flow: JSON unmarshalling accepts `Statement` as one object or an array. Validation enforces the 2012-10-17 version, at least one statement, valid effect, action presence, and at least one of `Resource`/`NotResource`. Compilation deep-copies statements and conditions, compiles static action/resource/principal/not-resource patterns, and stores variable-containing patterns for runtime substitution.

State and persistence: `PolicyCache` is defined but not used for persistence here. Compiled policies are in-memory immutable-ish objects after construction.

Dependencies and integration: uses `s3_constants` multipart action constants, `wildcard` matchers, `regexp`, `slices`, `encoding/json`, and `glog`. `engine.go` consumes the richer compiled fields.

Risks: `CompiledStatement.EvaluateStatement` and `CompiledPolicy.EvaluatePolicy` do not evaluate conditions, dynamic variables, or `NotResource`, so they are not equivalent to `PolicyEngine.EvaluatePolicy`. `StringOrStringSlice` stores unexported values, so external construction should use helpers or JSON unmarshalling.

Test signals: covered by parse/validation/compile tests, clone test, wildcard tests, dynamic variable tests, and multipart inheritance tests.
