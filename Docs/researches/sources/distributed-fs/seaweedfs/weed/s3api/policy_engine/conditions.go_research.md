# sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/conditions.go

Purpose: implements the condition-evaluation layer for the S3 bucket policy engine. It converts flexible policy values to string slices, dispatches AWS-style condition operators, resolves S3 existing-object-tag condition keys, and evaluates every condition attached to a policy statement.

Important APIs and types: `ConditionEvaluator` is the common interface. Concrete evaluators cover string equality and wildcard matching, numeric comparisons, RFC3339 date comparisons, bool checks, IP/CIDR checks, ARN equality/like checks, and `Null`. `GetConditionEvaluator` maps operator names to implementations. `EvaluateConditions` is the public condition entry point used by statement evaluation. `ExistingObjectTagPrefix` and `getConditionContextValue` connect `s3:ExistingObjectTag/<tag>` to object metadata under `s3_constants.AmzObjectTaggingPrefix`.

Control flow: `EvaluateConditions` treats an empty condition block as true, then iterates operator groups and condition keys. Unsupported operators are logged and skipped, not failed closed. For each key it pulls request/context values or object tag values, substitutes policy variables in expected values through `SubstituteVariables`, and requires every evaluated key to match.

State and persistence: `normalizedValueCache` is a process-global, mutex-protected LRU cache capped at 1000 normalized values. It is in-memory only and shared across evaluations.

Dependencies and integration: uses `glog`, `s3_constants`, and SeaweedFS wildcard helpers. It depends on `normalizeToStringSliceWithError`, `StringOrStringSlice.Strings`, and `SubstituteVariables` from the same package.

Risks: skipped unsupported operators can make a statement less restrictive than policy authors expect, especially for deny/allow conditions using unsupported AWS operators. Negative evaluators such as `StringNotEquals`, `NotIpAddress`, and date/numeric not-equals return true when no comparison succeeds, so missing context often satisfies negative conditions. Cache keys use type plus `fmt.Sprint`, which is pragmatic but can collide for complex values with equivalent string forms.

Test signals: covered by policy-engine tests for string/numeric/IP/bool operators, existing-object tags, variable substitution, `Null` SSE conditions, and multipart inherited SSE behavior.
