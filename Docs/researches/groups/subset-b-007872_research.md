# Research: subset-b-007872

Grouped research for SeaweedFS S3 policy engine, S3 action resolution, bucket encryption, S3 constants, and related tests. Each section is source-tree aligned and bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/conditions.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/conditions.go

Purpose: implements the condition-evaluation layer for the S3 bucket policy engine. It converts flexible policy values to string slices, dispatches AWS-style condition operators, resolves S3 existing-object-tag condition keys, and evaluates every condition attached to a policy statement.

Important APIs and types: `ConditionEvaluator` is the common interface. Concrete evaluators cover string equality and wildcard matching, numeric comparisons, RFC3339 date comparisons, bool checks, IP/CIDR checks, ARN equality/like checks, and `Null`. `GetConditionEvaluator` maps operator names to implementations. `EvaluateConditions` is the public condition entry point used by statement evaluation. `ExistingObjectTagPrefix` and `getConditionContextValue` connect `s3:ExistingObjectTag/<tag>` to object metadata under `s3_constants.AmzObjectTaggingPrefix`.

Control flow: `EvaluateConditions` treats an empty condition block as true, then iterates operator groups and condition keys. Unsupported operators are logged and skipped, not failed closed. For each key it pulls request/context values or object tag values, substitutes policy variables in expected values through `SubstituteVariables`, and requires every evaluated key to match.

State and persistence: `normalizedValueCache` is a process-global, mutex-protected LRU cache capped at 1000 normalized values. It is in-memory only and shared across evaluations.

Dependencies and integration: uses `glog`, `s3_constants`, and SeaweedFS wildcard helpers. It depends on `normalizeToStringSliceWithError`, `StringOrStringSlice.Strings`, and `SubstituteVariables` from the same package.

Risks: skipped unsupported operators can make a statement less restrictive than policy authors expect, especially for deny/allow conditions using unsupported AWS operators. Negative evaluators such as `StringNotEquals`, `NotIpAddress`, and date/numeric not-equals return true when no comparison succeeds, so missing context often satisfies negative conditions. Cache keys use type plus `fmt.Sprint`, which is pragmatic but can collide for complex values with equivalent string forms.

Test signals: covered by policy-engine tests for string/numeric/IP/bool operators, existing-object tags, variable substitution, `Null` SSE conditions, and multipart inherited SSE behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/conditions.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine.go

Purpose: provides the runtime bucket policy engine: storing compiled policies per bucket, evaluating requests with AWS-style explicit-deny precedence, deriving request condition context, substituting policy variables, and building S3 ARNs/actions.

Important APIs and types: `PolicyEngine` owns bucket contexts behind an RW mutex. `SetBucketPolicy`, `GetBucketPolicy`, `DeleteBucketPolicy`, `HasPolicyForBucket`, `ClearAllPolicies`, and `GetAllBucketsWithPolicies` manage policy state. `EvaluatePolicy` and `EvaluatePolicyForRequest` are the primary evaluation APIs. `PolicyEvaluationResult` distinguishes deny, allow, and indeterminate. Helpers include `SubstituteVariables`, `ExtractPrincipalVariables`, `ExtractConditionValuesFromRequest`, `BuildResourceArn`, `BuildActionName`, `IsMultipartContinuationAction`, and `injectSSEForMultipart`.

Control flow: `SetBucketPolicy` parses and compiles JSON, then swaps the bucket context. `EvaluatePolicy` returns indeterminate if no bucket policy exists. `evaluateCompiledPolicy` scans statements, returning deny immediately on matching explicit deny, remembering any explicit allow, and otherwise returning indeterminate for IAM fallback. `evaluateStatement` checks action, resource or `NotResource`, principal, and conditions. Multipart actions can inherit `s3:PutObject` authorization, and UploadPart/UploadPartCopy can inherit SSE condition values from CreateMultipartUpload.

State and persistence: bucket policies are only in-memory compiled contexts here. Persistence is handled by higher S3 bucket policy plumbing outside this file.

Dependencies and integration: integrates with `types.go` compiled statements, `conditions.go`, SeaweedFS logging, HTTP requests, and S3 IAM/bucket-policy callers. `ExtractConditionValuesFromRequest` populates `aws:SourceIp`, transport, time, list prefix/delimiter/max-keys, auth type, method, and `x-amz-*` headers.

Risks: forwarded IP headers are trusted only when `RemoteAddr` is private/loopback, but deployments behind non-private proxies need care. `SubstituteVariables` inserts raw claim text, so policy safety depends on wildcard/ARN pattern semantics rather than sanitization. `PolicyEngine.evaluateStatement` is richer than `CompiledStatement.EvaluateStatement` in `types.go`; callers must use the engine path for conditions, dynamic variables, and `NotResource`.

Test signals: broad tests validate allow/deny/indeterminate behavior, request extraction, forwarded IP precedence, resource/action construction, variables, folder isolation, `NotResource`, existing object tags, and multipart SSE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine_enhanced_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine_enhanced_test.go

Purpose: tests enhanced policy-variable behavior, especially principal-derived variables and JWT/LDAP claim substitution in resource patterns and conditions.

Important APIs and functions: `TestExtractPrincipalVariables` covers IAM user ARNs, IAM role ARNs, assumed-role ARNs, wildcard principals, and non-ARN principals. `TestSubstituteVariablesWithClaims` checks standard context variables plus `jwt:*` claims. `TestPolicyVariablesWithPrincipalType` verifies condition matching on `aws:principaltype`. `TestPolicyVariablesWithJWTClaims` drives JWT variables in resource ARNs through `PolicyEngine.EvaluatePolicy`. `TestExtractPrincipalVariablesWithAccount`, `TestSubstituteVariablesWithLDAP`, and `TestSubstituteVariablesSpecialChars` cover account extraction, LDAP prefixed/unprefixed fallback, and raw special-character substitution.

Control flow: tests build policies, install them with `SetBucketPolicy`, create `PolicyEvaluationArgs`, and assert allow or indeterminate results when variables match or mismatch. Substitution-only tests call `SubstituteVariables` directly.

State and persistence: all state is per-test in-memory policy engine state. No external persistence.

Dependencies and integration: exercises `engine.go` and `types.go` dynamic-pattern paths. It indirectly validates that policy variables are left intact when unresolved and that claims can be numeric/bool/string formatted.

Risks: the special-character test documents that substitution does not sanitize path traversal-like text. That is acceptable only if downstream policy/resource matching does not treat substituted values as filesystem paths.

Test signals: strong coverage for principal variable extraction and claims substitution, but these tests do not verify automatic population of claims from real authentication middleware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine_enhanced_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine_isolation_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine_isolation_test.go

Purpose: regression test for per-user folder isolation using dynamic resource variables and an explicit deny with `NotResource`.

Important APIs and functions: `TestIsolationPolicy` constructs a policy with `AllowOwnFolder`, `AllowListOwnPrefix`, and `DenyOtherFolders`. It evaluates `s3:GetObject` for Alice and Bob against their own and each other's prefixes.

Control flow: the test installs a bucket policy with `${aws:username}` in both `Resource` and `NotResource`. Matching own-folder requests hit the allow statement and do not hit the deny statement. Cross-folder requests fail the allow statement and match the deny statement because the requested resource is outside the substituted own-folder pattern.

State and persistence: uses an in-memory `PolicyEngine`; no persisted state.

Dependencies and integration: depends on dynamic pattern compilation in `types.go`, runtime substitution in `engine.go`, and `NotResource` evaluation.

Risks: this pattern is security-sensitive. If callers fail to populate `aws:username` consistently from the authenticated principal, the dynamic allow/deny boundary can become indeterminate or overly broad depending on policy shape.

Test signals: validates explicit deny precedence and dynamic `NotResource` for a common tenant-isolation policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine_isolation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine_notresource_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine_notresource_test.go

Purpose: focused regression test for `NotResource` statements that contain policy variables.

Important APIs and functions: `TestNotResourceWithVariables` installs a policy with `AllowOwnFolder` on `Resource` and `DenyOtherFolders` on `NotResource`, both using `${aws:username}`.

Control flow: first evaluation substitutes Alice into the allow and deny patterns. Alice's own object matches the allow and also matches the `NotResource` pattern, which means the deny statement does not apply. The second evaluation targets Bob's folder, so it does not match the allow and does satisfy the deny `NotResource` condition.

State and persistence: all policy state is in memory.

Dependencies and integration: directly validates `CompiledStatement.DynamicNotResourcePatterns`, `PolicyEngine.matchesDynamicPatterns`, and deny precedence in `engine.go`.

Risks: this test covers only one action and one variable. Unsupported conditions or missing variable context could still change real policy behavior.

Test signals: gives a narrow, high-value safety signal for dynamic `NotResource`, which is easy to regress when optimizing compiled statement matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine_notresource_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine_paths_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine_paths_test.go

Purpose: tests extraction of principal variables from IAM and STS ARNs that include path components.

Important APIs and functions: `TestExtractPrincipalVariablesWithPaths` verifies IAM user, IAM role, and assumed-role ARN parsing. Expected variables include `aws:PrincipalAccount`, `aws:principaltype`, `aws:username`, and `aws:userid` where applicable.

Control flow: the test calls `ExtractPrincipalVariables` and compares returned maps to expected values. User and role paths are reduced to the final role/user name. Assumed-role paths use the final session-name segment for username/userid.

State and persistence: no persisted state.

Dependencies and integration: protects the `strings.Split` parsing logic in `engine.go`, which feeds policy variables used by resource patterns and conditions.

Risks: ARN parsing is intentionally simple and assumes AWS-style colon and slash layout. Edge cases such as escaped characters or unusual partition/service forms are not covered.

Test signals: provides path-aware regression coverage for principal-derived variables used in multi-tenant policies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine_paths_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine_test.go

Purpose: main policy-engine test suite covering policy lifecycle, condition operators, validation, wildcard matching, request context extraction, existing object tags, and multipart permission inheritance.

Important APIs and functions: tests exercise `NewPolicyEngine`, `SetBucketPolicy`, `GetBucketPolicy`, `DeleteBucketPolicy`, `EvaluatePolicy`, `ParsePolicy`, `CompilePolicy`, `BuildResourceArn`, `BuildActionName`, `EvaluatePolicyForRequest`, `GetConditionEvaluator`, `ExtractConditionValuesFromRequest`, and object tag helpers.

Control flow: the suite installs representative policies, evaluates explicit allow, explicit deny, and non-matching indeterminate cases, then checks helper behavior. Existing object tag tests build `entry.Extended`-style maps with `s3_constants.AmzObjectTaggingPrefix`. Multipart tests verify all multipart upload action constants inherit `s3:PutObject` matching on object ARNs while unrelated actions do not.

State and persistence: test state is per-engine in memory. The helper `tagsToEntry` mirrors object metadata rather than using a filer.

Dependencies and integration: validates integration among `engine.go`, `conditions.go`, `types.go`, `s3_constants`, and wildcard utilities.

Risks: source IP tests encode trust behavior for forwarded headers; deployment assumptions must match that behavior. Multipart inheritance deliberately expands `PutObject` semantics and must stay aligned with S3 IAM expectations.

Test signals: broad unit-level confidence for policy parsing/evaluation and several security regressions, including tag-based deny and action inheritance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine_variables_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine_variables_test.go

Purpose: validates AWS policy variables in resource patterns and condition expected values, especially `${aws:username}`.

Important APIs and functions: `TestPolicyVariables` exercises resource variables for object access and condition variables for list prefixes. `TestEvaluatePolicyForRequestVariables` simulates the variable context that `EvaluatePolicyForRequest` should populate from the principal.

Control flow: the tests install policies with `${aws:username}` in object resource ARNs and `s3:prefix` conditions. Matching username/resource or prefix evaluates to allow; mismatches evaluate to indeterminate to allow IAM fallback.

State and persistence: all policy state is in-memory and scoped to each test.

Dependencies and integration: drives `CompilePolicy` dynamic pattern storage, `PolicyEngine.matchesDynamicPatterns`, `EvaluateConditions`, and `SubstituteVariables`.

Risks: the second test manually injects `aws:username` rather than constructing a full HTTP request path through `EvaluatePolicyForRequest`, so it confirms core evaluation more than complete request integration.

Test signals: good coverage for user-home directory policies and list-prefix constraints, which are common S3 isolation patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine_variables_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/examples.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/examples.go

Purpose: build-ignored example and documentation file for policy-engine usage, legacy identity conversion, condition examples, and migration guidance.

Important APIs and values: exports example JSON strings such as `ExampleIdentityJSON`, `ExampleBucketPolicy`, `ExampleTimeBasedPolicy`, `ExampleIPRestrictedPolicy`, `ExamplePublicReadPolicy`, `ExampleCORSPolicy`, `ExampleUserAgentPolicy`, `ExamplePrefixBasedPolicy`, and `ExampleMultiStatementPolicy`. Helper functions include `GetAllExamples`, `ValidateExamplePolicies`, `GetExamplePolicy`, `CreateExamplePolicyDocument`, `PrintExamplePolicyPretty`, `PrintAllExamples`, and example demonstrations for usage, legacy integration, condition operators, and migration.

Control flow: example helpers gather static JSON strings, parse them with `ParsePolicy`, pretty-print with `encoding/json`, or demonstrate runtime calls to `NewPolicyEngine`, `SetBucketPolicy`, and `EvaluatePolicy`.

State and persistence: no production state. The file has `//go:build ignore`, so it is documentation/sample code rather than compiled package code.

Dependencies and integration: refers to policy-engine APIs and legacy migration helpers such as `ConvertIdentityToPolicy` and `NewPolicyBackedIAM`, showing intended integration with identity actions.

Risks: because it is build-ignored, examples can drift from compiled APIs unless explicitly validated by a separate process. The migration text says default deny, while the engine returns indeterminate for no matching bucket policy statement to allow IAM fallback.

Test signals: no direct tests for this file; `ValidateExamplePolicies` can be used manually to check example JSON against current parser rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/examples.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/sse_condition_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/sse_condition_test.go

Purpose: tests server-side-encryption condition behavior in the bucket policy engine, including normal PutObject requests and multipart continuation actions.

Important APIs and functions: policy constants define deny-on-missing-SSE, allow-AES256-only, allow-KMS-only, and multipart deny policies. Helpers `newEngineWithPolicy`, `evalArgs`, and `evalArgsWithSSE` reduce setup. Tests cover `Null`, `StringEquals`, request-path normalization through `EvaluatePolicyForRequest`, and inherited SSE via `InheritedSSEAlgorithm`.

Control flow: tests install a policy, build evaluation args or HTTP requests, and assert allow/deny/non-deny. Multipart `UploadPart` and `UploadPartCopy` evaluations rely on `injectSSEForMultipart` to insert inherited algorithms only when CreateMultipartUpload used SSE.

State and persistence: in-memory policy engine only. The inherited SSE value simulates multipart upload metadata stored elsewhere.

Dependencies and integration: validates `ExtractConditionValuesFromRequest` canonicalization for `X-Amz-Server-Side-Encryption`, `IsMultipartContinuationAction`, `EvaluateConditions`, and the multipart `PutObject` inheritance path.

Risks: correctness depends on callers supplying canonical `InheritedSSEAlgorithm` for continuation requests. If multipart metadata lookup fails, `Null("true")` policies intentionally deny.

Test signals: strong regression coverage for SSE authorization, including case-insensitive AES256/aws:kms handling and the difference between regular PutObject and multipart part uploads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/sse_condition_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/types.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/types.go

Purpose: defines the policy document model, parsing/validation, compiled statement representation, wildcard compilation, and simpler compiled-policy matching helpers for the S3 bucket policy engine.

Important APIs and types: `StringOrStringSlice` supports JSON string-or-array fields. `PolicyConditions`, `PolicyDocument`, `PolicyStatement`, `PolicyEffect`, and `PolicyEvaluationArgs` model policies and evaluation inputs. `CompiledPolicy` and `CompiledStatement` store compiled regex/wildcard matchers plus dynamic patterns for variables and `NotResource`. Public helpers include `ParsePolicy`, `ValidatePolicy`, `CompilePolicy`, `GetBucketFromResource`, `FastMatchesWildcard`, `NewStringOrStringSlice`, and `CloneStringOrStringSlice`.

Control flow: JSON unmarshalling accepts `Statement` as one object or an array. Validation enforces the 2012-10-17 version, at least one statement, valid effect, action presence, and at least one of `Resource`/`NotResource`. Compilation deep-copies statements and conditions, compiles static action/resource/principal/not-resource patterns, and stores variable-containing patterns for runtime substitution.

State and persistence: `PolicyCache` is defined but not used for persistence here. Compiled policies are in-memory immutable-ish objects after construction.

Dependencies and integration: uses `s3_constants` multipart action constants, `wildcard` matchers, `regexp`, `slices`, `encoding/json`, and `glog`. `engine.go` consumes the richer compiled fields.

Risks: `CompiledStatement.EvaluateStatement` and `CompiledPolicy.EvaluatePolicy` do not evaluate conditions, dynamic variables, or `NotResource`, so they are not equivalent to `PolicyEngine.EvaluatePolicy`. `StringOrStringSlice` stores unexported values, so external construction should use helpers or JSON unmarshalling.

Test signals: covered by parse/validation/compile tests, clone test, wildcard tests, dynamic variable tests, and multipart inheritance tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/types_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/types_test.go

Purpose: focused regression test for deep copying `StringOrStringSlice` values.

Important APIs and functions: `TestCloneStringOrStringSliceCopiesBackingSlice` calls `NewStringOrStringSlice` and `CloneStringOrStringSlice`.

Control flow: creates an original two-action slice, clones it, mutates the clone's backing slice, then asserts the original remains unchanged while the clone reflects the mutation.

State and persistence: no external state.

Dependencies and integration: protects the clone behavior used when compiling policies and copying statement fields.

Risks: the test reaches the unexported `values` field because it is in the same package. External callers still cannot mutate internals directly, but package-local code can.

Test signals: narrow but important immutability signal for compiled policy safety.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/types_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_action_resolver.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_action_resolver.go

Purpose: resolves coarse handler actions plus HTTP request context into precise AWS S3 IAM action strings for bucket policy and IAM authorization.

Important APIs and functions: `ResolveS3Action` is the public entry point. Internals include `bucketQueryActions`, `resolveFromQueryParameters`, `resolveObjectLevelAction`, `resolveBucketLevelAction`, and `mapBaseActionToS3Format`.

Control flow: nil requests fall back to base-action mapping. Otherwise, query parameters have highest priority, distinguishing multipart upload, ACL, tagging, object attributes, version IDs, version listing, bucket policy/CORS/lifecycle/versioning/notification/object-lock, location, retention, legal hold, and batch delete. If no query-specific action matches, object-level or bucket-level method/resource logic maps methods such as GET, PUT, DELETE, and POST. Final fallback maps legacy actions like `Read`, `Write`, `List`, and `Admin` to S3 action strings.

State and persistence: stateless except for the package-level query action map.

Dependencies and integration: uses `net/http`, `net/url`, `strings`, and `s3_constants`. It is intended to unify bucket policy and IAM integration action resolution.

Risks: query parameter ordering matters; `attributes` intentionally precedes `versionId`. Empty object key and object value `"/"` are treated as bucket-level. Missing resolver coverage for a future S3 subresource will fall back to a coarse action, possibly weakening fine-grained policy behavior.

Test signals: resolver tests and granular security tests cover service-prefix passthrough, STS passthrough, attributes-before-versionId, DELETE mapping, ACL/tagging/multipart/bucket-policy precision, and coarse fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_action_resolver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_action_resolver_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_action_resolver_test.go

Purpose: targeted tests for action resolver passthrough and precedence rules.

Important APIs and functions: `TestMapBaseActionToS3Format_ServicePrefixPassthrough` validates `s3:`, `iam:`, and `sts:` actions are preserved and legacy `Read`/`Write` map to object actions. `TestResolveS3Action_STSActionsPassthrough` verifies STS actions survive through `ResolveS3Action` with and without HTTP context. `TestResolveS3Action_AttributesBeforeVersionId` checks that `?attributes&versionId=` resolves to `s3:GetObjectAttributes`, while plain versionId resolves to object-version actions.

Control flow: tests construct minimal requests and compare resolved action strings.

State and persistence: no state.

Dependencies and integration: directly validates `s3_action_resolver.go` and `s3_constants`.

Risks: the test file is focused and does not cover the full subresource table; broader coverage lives in `s3_granular_action_security_test.go`.

Test signals: strong signal for mixed IAM/STS integration and a subtle query precedence bug class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_action_resolver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_bucket_encryption.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_bucket_encryption.go

Purpose: implements S3 bucket default encryption configuration handlers and conversion between S3 XML and SeaweedFS protobuf metadata.

Important APIs and types: `ServerSideEncryptionConfiguration`, `ServerSideEncryptionRule`, and `ApplyServerSideEncryptionByDefault` model AWS XML. `ErrNoEncryptionConfig`, `EncryptionTypeAES256`, and `EncryptionTypeKMS` define error/algorithm constants. Public handlers are `GetBucketEncryptionHandler`, `PutBucketEncryptionHandler`, and `DeleteBucketEncryptionHandler`. Internal APIs include `GetBucketEncryptionConfig`, `getEncryptionConfiguration`, `updateEncryptionConfiguration`, `removeEncryptionConfiguration`, `IsDefaultEncryptionEnabled`, and `GetDefaultEncryptionHeaders`.

Control flow: PUT reads XML, validates at least one rule, validates algorithm, optionally validates KMS key IDs, converts to `s3_pb.EncryptionConfiguration`, and updates bucket metadata. GET loads metadata and returns XML or S3 no-config errors. DELETE checks existence and clears metadata. Header helper returns default SSE headers for upload paths.

State and persistence: persists encryption configuration through structured bucket metadata APIs: `GetBucketMetadata`, `UpdateBucketEncryption`, and `ClearBucketEncryption`. Cache invalidation is delegated to those metadata update calls.

Dependencies and integration: uses XML, HTTP, filer and S3 protobufs, S3 constants, S3 errors, and `isValidKMSKeyID` from surrounding S3 KMS code.

Risks: only the first rule is honored, matching AWS but discarding extra XML rules. `removeEncryptionConfiguration` treats metadata lookup failures as internal errors, while get treats missing bucket metadata as no-config in a recreation race. KMS validation depends on external helper correctness.

Test signals: no direct file-specific test in this subset, but SSE policy tests and broader S3 encryption code paths rely on default encryption headers and metadata behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_bucket_encryption.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/acp_canned_acl.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/acp_canned_acl.go

Purpose: defines S3 canned ACL names and prebuilt grant lists for common canned ACLs.

Important APIs and values: constants include `CannedAclPrivate`, `CannedAclPublicRead`, `CannedAclPublicReadWrite`, `CannedAclAuthenticatedRead`, `CannedAclLogDeliveryWrite`, `CannedAclBucketOwnerRead`, `CannedAclBucketOwnerFullControl`, and `CannedAclAwsExecRead`. Grant variables include `PublicRead`, `PublicReadWrite`, `AuthenticatedRead`, and `LogDeliveryWrite`.

Control flow: no functions. Grant slices are constructed from AWS SDK `s3.Grant` and `s3.Grantee` values using group URI/type/permission constants from sibling files.

State and persistence: package-level mutable slices of pointers; no persistence.

Dependencies and integration: used by ACL handling to translate canned ACL headers into grant sets. Depends on AWS SDK S3 structs and constants from ACP grantee/permission files.

Risks: grant slices are mutable globals; callers should not modify them in place. Some canned ACL constants have no prebuilt grant list here and must be handled elsewhere or treated as unsupported/default.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/acp_canned_acl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/acp_grantee_group.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/acp_grantee_group.go

Purpose: defines AWS S3 predefined grantee group URIs and validates group URIs.

Important APIs and values: `GranteeGroupAllUsers`, `GranteeGroupAuthenticatedUsers`, and `GranteeGroupLogDelivery` are package variables. `ValidateGroup` returns true for exactly those three group URIs.

Control flow: `ValidateGroup` uses a switch over known group constants and returns false by default.

State and persistence: package-level mutable string variables only; no persistence.

Dependencies and integration: used by ACL parsing/validation and canned ACL grant construction.

Risks: variables are mutable rather than constants, so package-local or external mutation could corrupt validation. Validation is exact string matching and does not normalize URI variants.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/acp_grantee_group.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/acp_grantee_type.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/acp_grantee_type.go

Purpose: centralizes S3 ACL grantee type strings.

Important APIs and values: package variables `GrantTypeCanonicalUser`, `GrantTypeAmazonCustomerByEmail`, and `GrantTypeGroup`.

Control flow: no functions.

State and persistence: mutable package variables only.

Dependencies and integration: consumed by canned ACL grants and ACL XML/parsing logic elsewhere.

Risks: because these are variables, accidental mutation can affect ACL serialization and validation globally.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/acp_grantee_type.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/acp_ownership.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/acp_ownership.go

Purpose: defines S3 object ownership modes and validates configured ownership strings.

Important APIs and values: `OwnershipBucketOwnerPreferred`, `OwnershipObjectWriter`, `OwnershipBucketOwnerEnforced`, `DefaultOwnershipForCreate`, `DefaultOwnershipForExists`, and `ValidateOwnership`.

Control flow: `ValidateOwnership` rejects empty strings and any value outside the three known ownership modes.

State and persistence: mutable package-level strings only. Actual ownership persistence is outside this file.

Dependencies and integration: used by bucket ACL/object ownership handling and metadata defaults.

Risks: defaults differ for newly created versus existing buckets, so migration paths must choose the correct default. Variables are mutable.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/acp_ownership.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/acp_permisson.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/acp_permisson.go

Purpose: defines S3 ACL permission string values.

Important APIs and values: `PermissionFullControl`, `PermissionRead`, `PermissionWrite`, `PermissionReadAcp`, and `PermissionWriteAcp`.

Control flow: no functions.

State and persistence: mutable package variables only.

Dependencies and integration: used by canned ACL grants and ACL parsing/serialization.

Risks: filename contains `permisson` typo, so discovery by expected spelling can be awkward. Variables are mutable and should be treated as constants by callers.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/acp_permisson.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/buckets.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/buckets.go

Purpose: defines the default filer path for S3 buckets.

Important APIs and values: `DefaultBucketsPath = "/buckets"`.

Control flow: no functions.

State and persistence: constant only. Actual bucket data persists under the configured buckets path in the filer.

Dependencies and integration: used by S3 server options and bucket path construction.

Risks: any code assuming this value without honoring configuration can diverge from deployments with custom bucket paths.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/buckets.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/crypto.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/crypto.go

Purpose: centralizes cryptographic and multipart constants for S3 server-side encryption and multipart upload handling.

Important APIs and values: defines AES sizes, `SSEAlgorithmAES256`, `SSEAlgorithmKMS`, SSE type labels, `S3MaxPartSize`, `PartOffsetMultiplier`, KMS encryption context/key limits, and `MaxS3MultipartParts`.

Control flow: no functions.

State and persistence: constants only.

Dependencies and integration: used by SSE-C, SSE-KMS, SSE-S3, multipart encryption, and KMS validation code. `PartOffsetMultiplier` is security-sensitive for CTR-mode IV offset separation.

Risks: changing `PartOffsetMultiplier`, AES sizes, or KMS limits can break encryption compatibility or security. The constants must stay aligned with AWS service limits and SeaweedFS encryption implementation.

Test signals: no direct tests in this subset, but SSE and multipart tests exercise consumers indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/crypto.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/extend_key.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/extend_key.go

Purpose: defines SeaweedFS extended metadata keys for S3 ownership, ACL, versioning, multipart, lifecycle, checksums, bucket policy, and object lock/retention/legal hold.

Important APIs and values: keys include owner/ACL/ownership/version IDs/delete markers/latest-version cache fields, multipart key, noncurrent lifecycle timestamp, lifecycle TTL fast-path flag, checksum metadata, `ExtBucketPolicyKey`, object lock retention/legal hold keys, and object-lock configuration component keys. It also defines retention modes, legal hold values, object lock enabled status, and bucket versioning statuses.

Control flow: no functions.

State and persistence: these constants are the persistence contract for entry extended attributes and bucket metadata fields.

Dependencies and integration: used throughout S3 metadata storage, versioning, lifecycle, checksum, bucket policy, multipart, and object lock code.

Risks: renaming or changing any key can orphan existing metadata or break backward compatibility. Several keys are optimized caches, so writers and readers must keep them consistent.

Test signals: no direct tests in this subset, but policy and existing-object-tag tests rely on extended metadata patterns in adjacent constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/extend_key.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/header.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/header.go

Purpose: defines S3 and SeaweedFS header constants plus request/path helper behavior for bucket/object extraction, object-key safety, response header pass-through, internal-header filtering, and authenticated identity context propagation.

Important APIs and values: large constant groups cover S3 namespace, object key length, metadata/tagging/ACL/object-lock/checksum/conditional/SSE headers, internal SSE metadata keys, internal filer headers, trusted principal/session headers, and non-standard identity constants. Functions include `GetBucketAndObject`, `IsValidObjectKey`, `IsValidBucketName`, `IsValidPathSegment`, `NormalizeObjectKey`, `GetPrefix`, `IsSeaweedFSInternalHeader`, `EnsureIdentityHolder`, `SetIdentityNameInContext`, `GetIdentityNameFromContext`, `SetIdentityInContext`, and `GetIdentityFromContext`.

Control flow: object keys are normalized by converting backslashes, collapsing duplicate slashes, and trimming leading slash. Validation rejects NUL and literal `.`/`..` path segments. Identity propagation installs a mutable holder pointer in request context so inner auth handlers can set identity visible to outer middleware holding earlier request copies.

State and persistence: header constants define HTTP and extended metadata contracts. Identity state is request-scoped, using `atomic.Pointer[string]` in the holder.

Dependencies and integration: uses Gorilla mux path vars, `net/http`, `context`, and `sync/atomic`. Used by S3 handlers, auth middleware, audit logging, metadata parsing, encryption, and policy tag handling.

Risks: `NormalizeObjectKey` alone does not reject traversal; callers must also call `IsValidObjectKey`. Internal principal/session headers are trusted only after auth layers scrub client-supplied values.

Test signals: header tests cover normalization, path validation, duplicate slash removal, and identity-holder propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/header.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/header_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/header_test.go

Purpose: validates object-key normalization/path-safety helpers and request-context identity propagation.

Important APIs and functions: tests cover `NormalizeObjectKey`, `IsValidObjectKey`, `IsValidBucketName`, `IsValidPathSegment`, `removeDuplicateSlashes`, `EnsureIdentityHolder`, `SetIdentityNameInContext`, and `GetIdentityNameFromContext`.

Control flow: table tests check slashes, backslashes, leading/trailing slash behavior, dot segments, NUL bytes, and bucket/path segment rejection. Identity tests simulate outer middleware installing a holder, inner authentication setting identity on a request copy, and outer middleware reading the identity through the shared holder.

State and persistence: only request-scoped context state; no persistence.

Dependencies and integration: protects `header.go` behavior used by mux-based S3 routes, filer path construction, and audit/auth middleware.

Risks: object keys like `.hidden` and `..hidden` remain valid by design, while exact dot segments are invalid. Tests encode that distinction.

Test signals: strong unit coverage for path traversal prevention primitives and identity propagation across request copies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/header_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/s3_acp.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/s3_acp.go

Purpose: defines canonical account IDs used by S3 ACP/ACL logic.

Important APIs and values: `AccountAnonymousId = "anonymous"` and `AccountAdminId = "admin"`.

Control flow: no functions.

State and persistence: constants only.

Dependencies and integration: consumed by ACL/account ownership code to represent anonymous and admin principals.

Risks: changing these constants changes identity semantics for ACLs and possibly persisted ownership data.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/s3_acp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/s3_action_strings.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/s3_action_strings.go

Purpose: defines AWS-format S3 action strings used by bucket policy and IAM evaluation.

Important APIs and values: constants cover object operations, object ACL, object tagging, retention/legal hold, multipart upload operations, bucket create/delete/list/version listing, bucket ACL/policy/tagging/CORS/lifecycle/versioning/location/notification/object-lock, and `S3_ACTION_ALL`.

Control flow: no functions.

State and persistence: constants only; policies persist these strings in JSON and metadata.

Dependencies and integration: used by `s3_action_resolver.go`, policy engine multipart action sets, IAM policy definitions, tests, and S3 handlers.

Risks: action spelling must remain AWS-compatible. Resolver and policy tests depend on exact strings, especially case like `s3:GetObjectAcl` and lifecycle names.

Test signals: extensively referenced by action resolver tests, granular security tests, policy tests, and end-to-end IAM tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/s3_action_strings.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/s3_actions.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/s3_actions.go

Purpose: defines legacy/coarse SeaweedFS action labels and common S3 internal folder/header constants.

Important APIs and values: coarse actions include `ACTION_READ`, `ACTION_READ_ACP`, `ACTION_WRITE`, `ACTION_WRITE_ACP`, `ACTION_ADMIN`, `ACTION_TAGGING`, `ACTION_LIST`, `ACTION_DELETE_BUCKET`, object-lock/retention/legal-hold actions, and object-lock config actions. Also defines `SeaweedStorageDestinationHeader`, `MultipartUploadsFolder`, `VersionsFolder`, and `FolderMimeType`.

Control flow: no functions.

State and persistence: constants are used in identity action lists and internal object layout names such as `.uploads` and `.versions`.

Dependencies and integration: `s3_action_resolver.go` maps these coarse actions to AWS S3 action strings. Multipart/versioning code uses folder constants.

Risks: coarse actions are less precise than AWS action strings; callers should use `ResolveS3Action` with HTTP context before authorization.

Test signals: resolver and granular security tests cover mappings from these coarse actions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/s3_actions.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/s3_config.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/s3_config.go

Purpose: holds S3 configuration defaults for circuit breaker files, allowed legacy actions, limit type labels, and action-string concatenation.

Important APIs and values: `CircuitBreakerConfigDir`, `CircuitBreakerConfigFile`, `AllowedActions`, `LimitTypeCount`, `LimitTypeBytes`, `Separator`, and `Concat`.

Control flow: `Concat` joins arbitrary strings with `Separator` (`:`), matching legacy action encodings such as `Read:bucket/path`.

State and persistence: mutable package variables hold defaults. Config files are external to this file.

Dependencies and integration: used by identity/action parsing, S3 configuration, and circuit breaker setup.

Risks: `AllowedActions` omits newer retention/object-lock constants defined in `s3_actions.go`, so validation paths using it may reject newer coarse actions unless updated elsewhere.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_constants/s3_config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_content_encoding_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_content_encoding_test.go

Purpose: regression tests ensuring `Content-Encoding` and `Content-Language` metadata survive S3 PUT metadata parsing and GET response header emission.

Important APIs and functions: `TestContentEncodingPreservation` and `TestContentEncodingWithOtherHeaders` exercise `ParseS3Metadata` and `S3ApiServer.setResponseHeaders`.

Control flow: tests build PUT requests with content encoding/language and other standard headers, parse metadata, build mock filer entries with `Extended` metadata, then call `setResponseHeaders` and assert expected HTTP response headers.

State and persistence: simulates persistence by placing parsed metadata into a `filer_pb.Entry.Extended` map. No real filer is used.

Dependencies and integration: uses `S3ApiServer`, S3 metadata parsing, filer protobuf entries, and standard response header handling.

Risks: these tests guard standard headers only; any metadata filtering changes in `ParseS3Metadata` or `setResponseHeaders` can regress client-visible object behavior.

Test signals: direct coverage for issue-class regressions around compressed objects and language/cache/disposition metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_content_encoding_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_end_to_end_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_end_to_end_test.go

Purpose: integration-style tests for S3 IAM/JWT behavior, role policies, prefix conditions, multipart authorization, CORS preflight, auth denial, and IAM-only anonymous rejection.

Important APIs and functions: helpers include `createTestJWTEndToEnd`, `setupCompleteS3IAMSystem`, `setupTestProviders`, role setup functions, `executeS3OperationWithJWT`, and `S3Operation`. Tests include `TestS3EndToEndWithJWT`, `TestS3MultipartUploadWithJWT`, `TestS3ListObjectsV2PrefixCondition`, `TestS3CORSWithJWT`, `TestS3PerformanceWithIAM`, `TestS3AuthenticationDenied`, and `TestS3IAMOnlyModeRejectsAnonymous`.

Control flow: tests initialize in-memory IAM manager, STS, policy, roles, OIDC/LDAP mock providers, assume roles with web identity JWTs, then authorize simplified S3 operations or direct IAM integration calls. Prefix-condition tests verify ListObjects requests use bucket ARNs and pass `s3:prefix`.

State and persistence: IAM stores are in memory. JWTs are generated per test. The S3 server is a mux test handler, not a full filer-backed S3 server.

Dependencies and integration: spans `iam/integration`, `oidc`, `ldap`, `policy`, `sts`, `S3IAMIntegration`, HTTP mux, and S3 error codes.

Risks: the simplified `/test-auth` endpoint maps methods to actions and treats some non-auth errors as allowed, so it is not a full S3 behavior test. Some setup paths skip on integration construction problems.

Test signals: useful high-level auth/authorization coverage, especially read/admin/IP-restricted roles, multipart write role, ListObjects prefix regression, and anonymous denial in IAM-only mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_end_to_end_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_error_utils.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_error_utils.go

Purpose: small helper file for consistent multipart operation error logging and return shape.

Important APIs and functions: `handleMultipartError` logs an operation-specific error and returns `(nil, errorCode)`. `handleMultipartInternalError` specializes it for `s3err.ErrInternalError`.

Control flow: callers pass an operation string, original error, and S3 error code. The helper logs through `glog.Errorf` and returns values compatible with multipart APIs that return an object plus `s3err.ErrorCode`.

State and persistence: no state.

Dependencies and integration: depends on SeaweedFS `glog` and `s3err`. Integrated by multipart handlers to reduce duplicated error handling.

Risks: logs include raw error text; callers should avoid passing sensitive details. The helper always returns nil payload, so it is only suitable for failure paths.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_error_utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_existing_object_tag_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_existing_object_tag_test.go

Purpose: tests S3 API integration for bucket policies that depend on `s3:ExistingObjectTag/<key>` using object metadata available after entry lookup.

Important APIs and functions: tests call `S3ApiServer.checkPolicyWithEntry`, `NewBucketPolicyEngine`, and `PolicyEngine.HasPolicyForBucket`. They use `s3_constants.AmzObjectTaggingPrefix` metadata keys and expect `s3err` outcomes.

Control flow: the allow-policy test checks public/missing/private tag cases and whether policy evaluation was decisive. No-policy and nil-engine tests assert graceful pass-through. Deny-policy tests verify explicit deny on confidential objects while allowing public/no-tag objects through an allow statement.

State and persistence: object tags are simulated as `map[string][]byte` entry metadata. Bucket policies are in-memory in the policy engine.

Dependencies and integration: validates the phase-two authorization path where an object entry is available, linking S3 handlers to `policy_engine.EvaluateConditions`.

Risks: existing-object-tag conditions cannot be fully evaluated before object metadata is loaded, so callers must ensure the second-phase `checkPolicyWithEntry` path is invoked for relevant operations.

Test signals: strong integration signal for tag-based allow/deny, no-policy fallback, nil policy-engine safety, and `HasPolicyForBucket`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_existing_object_tag_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_granular_action_security_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3_granular_action_security_test.go

Purpose: security-focused tests demonstrating that context-aware action resolution fixes coarse-action authorization gaps.

Important APIs and functions: helper `createTestRequestWithQueryParams` builds requests and extracts bucket/object. Tests include `TestGranularActionMappingSecurity`, `TestBackwardCompatibilityFallback`, `TestPolicyEnforcementScenarios`, `TestDeleteObjectPolicyEnforcement`, `TestFineGrainedPolicyExample`, and `TestCoarseActionResolution`.

Control flow: tests construct HTTP methods, paths, and query parameters, call `ResolveS3Action`, and assert precise AWS action strings. Cases cover DELETE object, ACL reads, tagging, multipart initiation, bucket policy updates, multipart upload listing, batch delete, and coarse `ACTION_WRITE` resolution.

State and persistence: no persisted state; tests are pure resolver checks.

Dependencies and integration: protects `s3_action_resolver.go` and `s3_constants` action strings. It documents intended security policy scenarios such as append-only buckets and metadata-only roles.

Risks: several tests log policy examples but do not run full policy evaluation. They prove action mapping, not end-to-end enforcement.

Test signals: high-value regression coverage for the critical bug class where `ACTION_WRITE` previously mapped DELETE operations to `s3:PutObject`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3_granular_action_security_test.go -->
