# Research: subset-b-008275

This grouped report covers RustFS policy evaluation, policy utility helpers, timestamp/JWT helpers, and the protocols crate S3 backend trait. Each section preserves its source path and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/string.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/function/string.rs

## Purpose

Implements IAM string condition functions for policy evaluation. This file backs operators such as string equality, string inequality through negation, case-insensitive equality, wildcard-like matching, and ForAllValues/ForAny-style behavior over request context values. It also defines the JSON value shape used by string functions.

## Important APIs, Types, and Functions

- `pub type StringFunc = InnerFunc<StringFuncValue>` is the concrete string condition function container.
- `StringFunc::evaluate_with_resolver(...)` evaluates all contained key/value clauses and combines them with logical AND. Flags select all-values semantics, case folding, wildcard matching, and negation.
- `FuncKeyValue<StringFuncValue>::eval(...)` performs exact string set matching. It resolves policy variables, substitutes common condition variables, optionally lowercases request and policy values, and compares request values against function values.
- `FuncKeyValue<StringFuncValue>::eval_like(...)` performs wildcard pattern matching using `policy::utils::wildcard::is_match`.
- `StringFuncValue(pub Set<String>)` stores non-empty condition values. Tests use `BTreeSet` for deterministic serialization, while production uses `HashSet`.
- Custom `Serialize` accepts/outputs a single string when there is exactly one value and a sequence for multiple values. Custom `Deserialize` accepts either a string or array and rejects empty arrays.

## Control Flow

Evaluation iterates over each `FuncKeyValue`. For non-like conditions, request values are read from `values` by `self.key.name()`, normalized for case if needed, and collected into a set. Policy-side values are asynchronously expanded through `resolve_aws_variables` when a resolver is present. Each expanded value also receives direct substitution for `KeyName::COMMON_KEYS` by replacing `${...}` variable forms with the first non-empty request condition value. The final result is an intersection check: `for_all` accepts empty request sets or requires all request values to be in the policy set; non-`for_all` requires at least one intersection.

For like conditions, each request value is tested against every resolved/substituted policy pattern using wildcard matching. With `for_all`, every request value must match at least one pattern; without it, any match succeeds. If the key is missing, `eval_like` returns `for_all`, matching the vacuous truth behavior also visible in tests.

`evaluate_with_resolver` XORs each clause result with `negate` and returns false on the first failed clause, so all clauses must pass after operator-specific negation.

## State and Persistence

This file is stateless. It allocates temporary sets/vectors during each evaluation and awaits policy-variable resolution. No persistent storage, global mutable state, or I/O is used.

## Dependencies and Integration Points

Depends on `FuncKeyValue`, `InnerFunc`, `KeyName`, `PolicyVariableResolver`, and `resolve_aws_variables` from the policy function/variable subsystem. It integrates with the broader `Functions` condition evaluator, with request condition maps supplied by statement and policy evaluation. Wildcard matching is delegated to `policy::utils::wildcard`.

## Risks and Edge Cases

- `for_all` returns true for missing request values, which is intentional in tests but sensitive for authorization semantics.
- Policy variable expansion can produce multiple candidate values; callers must understand this can widen matches.
- Common key substitution uses only the first non-empty request value, so multi-valued request keys do not generate combinations through this compatibility path.
- Production `HashSet` serialization order is not deterministic unless higher layers preserve or sort elsewhere; tests switch to `BTreeSet`.
- Lowercasing uses `to_lowercase`, which can expand Unicode characters; comparisons are string-based rather than locale-aware.

## Test Signals

Inline tests cover JSON deserialization/serialization, invalid keys and empty values, JWT role key matching, exact equality and negation, case-insensitive variants, wildcard like/not-like, `for_all` behavior, missing-key behavior, `s3:LocationConstraint` substitution, and tag-key specific condition matching.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/function/string.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/id.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/id.rs

## Purpose

Provides a lightweight wrapper around policy and statement ID strings. It supports serde, default construction, validation through the policy `Validator` trait, conversion from string-like inputs, and transparent string dereferencing.

## Important APIs, Types, and Functions

- `pub struct ID(pub String)` is a tuple newtype used for `Policy.ID`, bucket policy `Id`, and statement `Sid`.
- `ID::is_empty()` is used by serde `skip_serializing_if` attributes to omit empty IDs.
- `impl Validator for ID` accepts every UTF-8 Rust string as valid.
- `impl<T: ToString> From<T> for ID` allows literals and other stringable values to become IDs.
- `impl Deref<Target = String>` lets ID values be used like strings.

## Control Flow

There is no complex runtime flow. Validation always succeeds, and empty-state checks are direct string emptiness checks.

## State and Persistence

Stores only an owned `String`; no persistence or external state.

## Dependencies and Integration Points

Used by `Policy`, `BucketPolicy`, `Statement`, and `BPStatement` for optional identifiers. Depends on crate `Error`/`Result` only to satisfy the common `Validator` contract.

## Risks and Edge Cases

The permissive validator means length limits, reserved characters, or AWS-style SID restrictions are not enforced here. That may be deliberate compatibility behavior, but stricter validation must be added elsewhere if required.

## Test Signals

No local tests. Behavior is indirectly covered by policy and statement serialization tests that assert empty IDs/SIDs are omitted and non-empty SIDs are preserved.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/id.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/opa.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/opa.rs

## Purpose

Implements optional Open Policy Agent authorization integration. It discovers OPA plugin configuration from environment variables, validates connectivity, builds an HTTP client, converts RustFS policy request arguments to an OPA input document, and interprets supported OPA response shapes.

## Important APIs, Types, and Functions

- `Args { url, auth_token }` holds plugin configuration. `Args::enable()` returns true when a URL is configured.
- `check()` validates environment configuration. It requires `ENV_POLICY_PLUGIN_OPA_URL`, permits `ENV_POLICY_PLUGIN_AUTH_TOKEN`, and rejects unknown variables under the policy plugin prefix.
- `validate(config)` posts to the configured URL and requires HTTP 200 to consider OPA reachable.
- `lookup_config()` reads env vars, returns disabled default when the URL is absent, otherwise checks and validates the config.
- `AuthZPlugin::new(config)` builds a tuned `reqwest::Client` with short timeouts, keepalive, pooling, HTTP/2 keepalive, and TCP no-delay.
- `AuthZPlugin::is_allowed(args)` sends the OPA JSON payload, adds a bearer token when present, and fail-closes on transport, status, or JSON parse errors.
- `build_opa_input(args)` maps policy arguments into `input.identity`, `input.resource`, `input.action`, and `input.context`.
- `OpaResponseEnum` accepts either `{ "result": bool }` or `{ "result": { "allow": bool } }`.

## Control Flow

Startup config flow calls `lookup_config`: no URL means disabled; otherwise the environment is screened for unknown plugin settings and the endpoint is probed. Runtime authorization constructs payload from `PArgs`, posts JSON to `args.url`, optionally adds `Authorization: Bearer <token>`, checks for a successful HTTP status, then deserializes a supported OPA result form. Any failure logs an error and returns false.

## State and Persistence

The plugin retains only a `reqwest::Client` and cloned config. There is no persistence. Runtime payloads include the current UTC timestamp using `chrono::Utc::now().to_rfc3339()`.

## Dependencies and Integration Points

Depends on `rustfs_config::opa` constants for environment names, `reqwest` for HTTP, `serde_json` for payloads, `tracing` for logs, and `crate::policy::Args` for RustFS authorization context. It integrates as an external authorizer alongside or in front of local policy evaluation depending on caller wiring.

## Risks and Edge Cases

- Connectivity validation sends an empty POST to the policy URL; OPA policies that reject empty input may make startup fail.
- HTTP client construction uses `.unwrap()`, so invalid TLS/client configuration would panic, though the builder options are static.
- Authorization is fail-closed, which is appropriate for security but makes OPA availability a hard dependency once enabled.
- Only two response shapes are accepted; richer OPA documents must be adapted in policy or code.
- Environment screening rejects any unknown variable under the plugin prefix, which can catch typos but may surprise deployments with extra metadata env vars.

## Test Signals

Inline tests cover valid env config, missing URL, invalid env vars, disabled lookup behavior, and `Args::enable`. There are no HTTP mock tests for `validate` or `is_allowed`, so response parsing and fail-closed behavior are visible in code but not directly exercised here.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/opa.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/policy.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/policy.rs

## Purpose

Defines the top-level IAM and bucket policy data models, request argument structs, policy validation, policy merging, default built-in policies, claim-policy extraction helpers, and ExistingObjectTag prefetch analysis. It is the aggregation layer that applies statement-level authorization decisions into complete allow/deny policy semantics.

## Important APIs, Types, and Functions

- `DEFAULT_VERSION = "2012-10-17"` is the accepted IAM policy version.
- `Validator` is the shared validation trait used by policy model types.
- `Args<'a>` carries identity-policy request context: account, groups, action, bucket, object, conditions, claims, owner flag, and `deny_only`.
- `Args::get_role_arn()` and `Args::get_policies()` expose claim-derived role/policy values.
- `Policy { id, version, statements }` represents identity policy JSON.
- `Policy::is_allowed(args)` implements deny-first, deny-only, owner, and allow-statement evaluation.
- `Policy::match_resource(resource)` tests whether any statement resource matches a resource string.
- `Policy::merge_policies(inputs)` concatenates statements and removes duplicates.
- `Policy::parse_config(data)` deserializes JSON and validates it.
- `BucketPolicyArgs<'a>` is the bucket-policy request context without claims and deny-only.
- `BucketPolicy { id, version, statements }` represents bucket policy JSON.
- `BucketPolicy::is_allowed(args)` mirrors deny-first then owner then allow semantics for `BPStatement`.
- `get_policies_from_claims`, `iam_policy_claim_name_sa`, and internal `get_values_from_claims` parse policy names from string or array claims, splitting comma-delimited entries.
- `policy_uses_existing_object_tag_conditions`, `bucket_policy_uses_existing_object_tag_conditions`, and request-narrowing variants detect when object tags may be needed to evaluate conditions.
- `default::DEFAULT_POLICIES` defines `readwrite`, `readonly`, `writeonly`, `diagnostics`, and `consoleAdmin` built-in policies.

## Control Flow

`Policy::is_allowed` evaluates all explicit deny statements first. A matching deny is represented by `Statement::is_allowed` returning false after deny effect inversion, so the policy immediately rejects. If `deny_only` is set and no deny matched, the request is allowed without evaluating allow statements. Otherwise owners are allowed, then allow statements are scanned until one returns true. If none match, the default result is deny.

`BucketPolicy::is_allowed` follows the same deny-first pattern, then owner override, then allow scan. There is no deny-only path for bucket policies.

Validation enforces the default version when a version is present and delegates statement validation. Policy merging preserves the first non-empty version from inputs, appends all statements, then removes duplicates using statement equality that intentionally ignores SID.

Claim extraction first looks up claim names using exact-match preference and case-insensitive fallback from `get_claim_case_insensitive`. Ambiguous case-insensitive matches are treated as missing. String and array claims are split on commas and trimmed into a set.

ExistingObjectTag analysis first serializes `Functions` to JSON and searches keys recursively for `ExistingObjectTag`/`s3:ExistingObjectTag` forms. Request-specific helpers then use statement `request_reaches_condition_eval` to avoid fetching object tags when action, principal, or resource would skip the tag-dependent statement.

## State and Persistence

Policies and default policies are in-memory structures. `DEFAULT_POLICIES` uses `LazyLock` for process-local lazy initialization. No file or database persistence occurs in this file.

## Dependencies and Integration Points

Integrates with `Statement`, `BPStatement`, action/resource/function/effect/ID types, claim lookup utilities, `serde_json::Value`, and `rustfs_credentials::IAM_POLICY_CLAIM_NAME_SA`. Default policies depend on action enums for S3, STS, Admin, and KMS. Runtime callers supply `Args` or `BucketPolicyArgs` from S3/API authorization paths.

## Risks and Edge Cases

- `deny_only` intentionally allows requests if no explicit deny matches, even if no allow matches; callers must only use it for deny-only validation.
- Owner override occurs after denies, so explicit denies still block owner requests; this is security-sensitive and covered by tests.
- `Policy::merge_policies` de-duplicates based on statement equality that ignores SID and `not_resources`; equality includes effect, actions, not_actions, resources, and conditions only via `Statement::eq`, so duplicate semantics should be reviewed when NotResource is involved.
- Empty `{}` identity policy parses as an implied empty policy with no statements.
- ExistingObjectTag detection serializes conditions to JSON; serde shape changes in condition types can affect detection.
- Default policy definitions are authorization-critical and should stay aligned with action enum behavior.

## Test Signals

Inline tests cover parsing, single-string Action/Resource compatibility, default policy validity and STS allow, deny-only semantics, ListBucket prefix/resource behavior, bucket policy ListBucket behavior, policy variable substitution including nested and multi-value variables, NotAction/NotResource validation, admin/table resource scoping, STS/KMS/Admin resource exceptions, mixed action family rejection, serialization omission and deterministic order, ExistingObjectTag detection and request narrowing, claim lookup ambiguity, and JSON round trips.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/policy.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/principal.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/principal.rs

## Purpose

Models bucket-policy principals with AWS-compatible JSON handling. It supports wildcard string principals, object-form `AWS` principals, and object-form `Service` principals, and provides principal pattern matching for bucket policy statements.

## Important APIs, Types, and Functions

- `Principal { aws, service }` stores principal patterns as private `HashSet<String>` fields.
- Custom `Serialize` emits only non-empty `AWS`/`Service` fields and uses a single string for singleton sets, otherwise arrays.
- `PrincipalFormat` accepts either a wildcard string or object form.
- `PrincipalObject` uses `deny_unknown_fields` and supports optional `AWS` and `Service`.
- `PrincipalValues` accepts a single string or set of strings.
- `Principal::is_match(principal)` tests both AWS and Service patterns with `wildcard::is_simple_match`.
- `Validator for Principal` rejects empty principal sets.

## Control Flow

Deserialization treats only the literal string `"*"` as valid wildcard string form and maps it to an AWS wildcard. Object form converts provided values into sets and rejects objects that contain neither AWS nor Service. Matching scans AWS patterns first and then service patterns, returning true on the first simple wildcard match.

## State and Persistence

Pure in-memory value object. No persistence or global state.

## Dependencies and Integration Points

Used by `BPStatement` in bucket policy evaluation. Depends on `policy::utils::wildcard` for matching and the common `Validator` trait. Service principal support enables AWS-style bucket policies for service actors such as S3 logging.

## Risks and Edge Cases

- The raw string form accepts only `"*"`, not arbitrary AWS principal strings; non-wildcard principals must use object form.
- Sets mean duplicate principals are collapsed and output order is not stable for multi-element serialization.
- `is_simple_match` has different `?` semantics from strict wildcard matching; this is intentional but should be kept in mind for principal patterns.
- Private fields force tests and construction outside the module to use JSON deserialization or helper constructors.

## Test Signals

Inline tests cover accepted and rejected principal JSON forms, singleton and multi-element serialization, service principal round-trips, service matching, and combined AWS/Service matching.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/principal.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/resource.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/resource.rs

## Purpose

Defines policy resources and resource sets, including AWS S3 ARN parsing/serialization, validation, wildcard resource matching, condition-variable substitution, and policy-variable expansion. It is the resource authorization primitive used by statements.

## Important APIs, Types, and Functions

- `ResourceSet(pub Vec<Resource>)` preserves input order while providing duplicate suppression during deserialization.
- `ResourceSet::is_match(...)` and `is_match_with_resolver(...)` match any resource in the set against a request resource.
- `ResourceSet::match_resource(resource)` matches without conditions.
- `ResourceSet` custom serde accepts either a string or array and serializes as an array of resource strings.
- `Resource` has variants `S3(String)` and `Kms(String)`, although `TryFrom<&str>` currently accepts only S3 ARNs.
- `Resource::S3_PREFIX` is `arn:aws:s3:::`.
- `Resource::is_match_with_resolver(...)` expands variables, substitutes common condition keys, path-cleans the request resource, and checks exact or wildcard match.
- `Validator for Resource` rejects empty S3 resources, S3 resources starting with `/`, and KMS values containing path-like characters.

## Control Flow

Deserialization parses each resource string through `Resource::try_from`, strips the S3 ARN prefix, validates, and pushes only unique values. Matching expands the stored pattern through a `PolicyVariableResolver` when present. For each expanded pattern, it replaces common key variables with the first non-empty request condition value. It then normalizes the incoming request resource through `path::clean`; a non-dot exact equality succeeds, otherwise wildcard matching is attempted.

## State and Persistence

Resource objects hold only strings in memory. There is no persistence.

## Dependencies and Integration Points

Used by `Statement`, `BPStatement`, top-level policy matching, and default policies. Depends on `KeyName::COMMON_KEYS`, `policy::variables::resolve_aws_variables`, `policy::utils::path::clean`, and `policy::utils::wildcard`. It is part of the defense against path traversal-like resource matching bypasses.

## Risks and Edge Cases

- KMS resources exist as an enum variant but are not parsed from strings by `TryFrom<&str>`, so external JSON KMS resource support is incomplete or intentionally unused.
- Matching rejects cleaned `"."`, preventing empty/dot request resources from matching.
- Path cleaning can change request resource strings before wildcard matching; this is security-friendly for traversal but may differ from byte-exact S3 key semantics if callers pass keys containing dot segments.
- Serialization always emits ResourceSet as an array, even if source JSON was a single string.

## Test Signals

Inline tests cover broad S3 resource wildcard matching, bucket vs object resources, `?` matching, negative bucket/object cases, and path traversal defenses for `../` and nested safe/../../ patterns.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/resource.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/statement.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/statement.rs

## Purpose

Defines identity policy statements and bucket policy statements, including serde shape, validation rules, request applicability checks, condition evaluation entry points, resource construction, and effect application.

## Important APIs, Types, and Functions

- `Statement` represents IAM identity statements with `Sid`, `Effect`, `Action`, `NotAction`, `Resource`, `NotResource`, and `Condition`.
- `BPStatement` is the bucket-policy equivalent and adds required `Principal`.
- `variable_resolver_for_policy_args(args)` builds a `VariableResolver` from request claims, account, and conditions.
- `build_resource(action, bucket, object, bucket_resource_only)` creates the resource string used for matching.
- `ActionFamily` classifies actions into S3/Admin/STS/KMS/Mixed for validation.
- `Statement::request_reaches_condition_eval(args, resolver)` checks action and resource gates without evaluating conditions.
- `Statement::is_allowed(args)` checks request applicability, evaluates conditions with resolver, and applies `Effect`.
- `BPStatement::request_reaches_condition_eval(args)` additionally checks principal before action/resource gates.
- `BPStatement::is_allowed(args)` evaluates bucket-policy conditions and applies effect.

## Control Flow

For identity statements, authorization builds a variable resolver from claims and request context. It rejects requests when `Action` does not match, `NotAction` matches, required resource gates fail, or `NotResource` matches. KMS statements can shortcut resource matching when the built resource is `/` or resources are empty. Admin and STS statements can skip resource matching, except table-scoped admin actions that honor resources. If the request reaches conditions, condition functions are evaluated and `Effect::is_allowed` converts the condition boolean into allow/deny semantics.

Bucket policy flow first matches the principal, then action/not-action, then resources/not-resources, then conditions. It does not have the identity-policy admin/STS/KMS resource exceptions.

`build_resource` normally builds `bucket/object`, adding a slash after bucket when object is empty. For ListBucket/ListBucketVersions/ListBucketMultipartUploads with an `s3:prefix` condition reference, it uses the bucket-only resource so the prefix is evaluated by conditions rather than by object resource matching.

## State and Persistence

Statements are in-memory data models. Evaluation constructs transient resource strings and variable resolvers only; no persistence.

## Dependencies and Integration Points

Integrates directly with action sets, resource sets, functions/conditions, effects, principals, IDs, S3 key names, and variable resolution. Called by top-level `Policy` and `BucketPolicy`. The resource construction behavior is tightly coupled to ListBucket gateway behavior and condition key handling.

## Risks and Edge Cases

- Resource handling differs by action family and admin subtype. Changes to action enum classification can affect statement validation and evaluation.
- `ActionFamily::Mixed` rejects identity statements combining S3/Admin/STS/KMS actions; `NotAction` statements bypass this classification because their allowed family is not directly knowable.
- `Effect::Deny` means `Statement::is_allowed` returns false when a deny statement matches, which top-level policy code relies on for deny-first semantics.
- `build_resource` appends `/` to bucket-only resources; resource patterns must match this convention where relevant.
- Bucket-policy statements require `Principal` and do not allow empty resource sets.

## Test Signals

Direct tests are mostly in `policy.rs` and `tests/policy_is_allowed.rs`. They exercise ListBucket prefix behavior, NotAction/NotResource validation, admin table resource scoping, STS/Admin/KMS resource exceptions, mixed-family rejection, deny behavior, and bucket-policy principal/resource interactions.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/statement.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/utils.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/utils.rs

## Purpose

Provides shared policy utility modules and small helper functions for claim lookup and policy database path splitting.

## Important APIs, Types, and Functions

- Re-exports submodules `path` and `wildcard`.
- `ClaimLookup<'a>` distinguishes missing claims, a found claim value, and ambiguous case-insensitive matches.
- `get_claim_case_insensitive(claims, claim_name)` prefers exact key matches and otherwise finds a single Unicode-aware case-folded match.
- `_get_values_from_claims(claim, chaim_name)` parses exact-name string or array claims into comma-split values.
- `_split_path(path, second_index)` splits a path after the first slash or second slash depending on storage layout.

## Control Flow

Case-insensitive lookup first checks `HashMap::get` for exact match. If absent, it scans every claim key using `case_insensitive_eq`, which lowercases chars without allocating entire strings. The first folded match is retained; a second folded match returns `Ambiguous`. Path splitting finds either the first slash or, when `second_index` is true, the second slash, then returns the prefix including slash and the rest.

## State and Persistence

No state or persistence. Helpers operate on caller-supplied maps and strings.

## Dependencies and Integration Points

Used by policy claim extraction in `policy.rs` and any IAM storage code needing path splitting. `path` and `wildcard` submodules are used by resource and principal matching.

## Risks and Edge Cases

- `_get_values_from_claims` uses exact key lookup only and appears superseded by case-insensitive helpers for policy claims.
- `case_insensitive_eq` is Unicode-aware through `char::to_lowercase`, but not full locale-specific collation.
- Ambiguous folded claims are treated as missing by callers, reducing confused-deputy risk at the cost of ignoring potentially valid claims.
- `_split_path` returns the whole path and empty rest if the expected slash is absent.

## Test Signals

Inline tests cover path splitting for normal user/group/policydb layouts, slash-containing LDAP-like names, exact-match preference, ambiguity detection, and Unicode case matching.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/utils.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/utils/path.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/utils/path.rs

## Purpose

Implements a Rust version of Go's `path.Clean` for slash-separated policy resource matching. It normalizes dot segments, duplicate slashes, trailing slashes, and parent-directory segments.

## Important APIs, Types, and Functions

- `LazyBuf<'a>` delays allocation while building the cleaned path and only allocates when output diverges from input.
- `clean(path: &str) -> String` is the public normalizer.

## Control Flow

`clean` returns `"."` for empty input. It tracks whether the path is rooted, a read index, an output buffer/write index, and a `dotdot` boundary. It skips empty and `.` path elements, collapses `..` by rewinding the output buffer when possible, preserves leading `..` for relative paths, and emits normalized path components separated by single slashes. Empty output becomes `"."`.

## State and Persistence

No persistent state. `LazyBuf` owns temporary output storage for one call.

## Dependencies and Integration Points

Used by `Resource::is_match_with_resolver` before exact/wildcard resource checks. This is a security-sensitive integration because it prevents resource patterns such as `attacker-bucket/*` from matching request paths that normalize outside the bucket.

## Risks and Edge Cases

- Operates on bytes and returns `String::from_utf8_lossy`; if invalid UTF-8 were somehow supplied it would be lossy, though Rust `&str` inputs are valid UTF-8.
- Normalizing object keys may differ from raw S3 object key semantics for keys containing literal `.` or `..` path components. This is intentional for authorization safety but must align with request construction.
- Rooted paths are supported even though S3 resource validation rejects S3 patterns that start with `/`.

## Test Signals

Inline tests mirror many Go path-cleaning cases: empty paths, rooted paths, trailing slashes, duplicate slashes, `.` and `..`, over-parenting, and idempotency of already-clean output.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/utils/path.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/utils/wildcard.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/utils/wildcard.rs

## Purpose

Provides wildcard matching primitives for actions, resources, principals, and pattern-prefix checks. It supports `*` for arbitrary byte sequences and `?` for single-byte matching, with a special simple mode used by principal matching.

## Important APIs, Types, and Functions

- `is_simple_match(pattern, name)` calls `inner_match(..., simple = true)`.
- `is_match(pattern, name)` calls `inner_match(..., simple = false)`.
- `is_match_as_pattern_prefix(pattern, text)` tests whether text is compatible with the beginning of a wildcard pattern, stopping true at `*`.
- `inner_match` handles empty pattern and global `*` fast paths.
- `deep_match` recursively matches bytes for `?`, `*`, and literals.

## Control Flow

Strict matching requires `?` to consume an existing byte and final pattern exhaustion to coincide with name exhaustion. Simple matching differs when `?` sees an empty name: it returns true, allowing a trailing question mark to match an absent byte. `*` branches recursively over zero-character and one-or-more-character consumption. Prefix matching walks pattern/text pairs and accepts as soon as it reaches a `*`; `?` skips one text byte.

## State and Persistence

Pure stateless functions; no persistence.

## Dependencies and Integration Points

Used by `Resource` matching, string condition `StringLike`, action matching elsewhere in the policy module, and principal matching. Differences between strict and simple modes are important for principal behavior versus resource/action behavior.

## Risks and Edge Cases

- `deep_match` is recursive and can be exponential for adversarial patterns with many `*` branches and long names.
- Matching is byte-oriented, not Unicode scalar-aware. `?` matches one byte, not one Unicode character.
- `is_simple_match` permits `a?` to match `a`, unlike strict matching; use the correct API for the domain.

## Test Signals

Inline tests cover action-like patterns, bucket/object resource patterns, strict `?` behavior, simple-mode trailing `?` behavior, long wildcard path cases, and prefix-match semantics.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/utils/wildcard.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/variables.rs -->
# sources/object-store/rustfs/crates/policy/src/policy/variables.rs

## Purpose

Implements AWS-style policy variable resolution for resources and string conditions. It supports request-derived variables, claim-derived variables, custom variables, dynamic time variables, multi-value expansion, nested variable resolution, and optional caching for non-dynamic variables.

## Important APIs, Types, and Functions

- `VariableContext` carries HTTPS flag, source IP, account ID, region, username, claims, request conditions, and custom variables.
- `VariableResolverCache` wraps a `moka::future::Cache<String, String>`.
- `CachedAwsVariableResolver` delegates to `VariableResolver` and caches non-dynamic single-value resolutions for five minutes by default.
- `PolicyVariableResolver` is the async trait with `resolve`, `resolve_multiple`, and `is_dynamic`.
- `VariableResolver` resolves AWS variables from `VariableContext`.
- `resolve_aws_variables(pattern, resolver)` expands `${...}` placeholders into one or more strings, with up to ten iterative passes.
- `resolve_single_pass` finds variables, handles nested placeholders, expands multi-values by splicing multiple result strings, and leaves unknown variables unchanged.

## Control Flow

Variable resolution starts with the original pattern as a single result. Each pass calls `resolve_single_pass` on each current result. When a placeholder resolves to multiple values, the result list branches into one string per value. Duplicates are removed while preserving order. Resolution repeats until no changes occur or ten iterations are reached.

`VariableResolver` maps `aws:username` to context username, `aws:userid` to `sub` or `parent` claim values, `aws:PrincipalType` to `AssumedRole`, `ServiceAccount`, or `User`, `aws:SecureTransport` to a boolean string, current/epoch time to UTC time values, and account/region/source IP/custom variables from context. `resolve_multiple` supports multi-value `aws:userid` from array claims.

Nested variables such as `${${aws:PrincipalType}-${aws:userid}}` first resolve the inner expression to a variable name, then a later pass can resolve that generated variable if a resolver supplies it.

## State and Persistence

The base resolver holds an owned `VariableContext`. The cached resolver has an in-memory moka cache with capacity and TTL. Dynamic variables (`aws:CurrentTime`, `aws:EpochTime`) bypass the cache.

## Dependencies and Integration Points

Used by `Statement::variable_resolver_for_policy_args`, `Resource::is_match_with_resolver`, and string condition evaluation. Depends on `async_trait`, `moka`, `serde_json::Value`, `time::OffsetDateTime`, and async futures for recursive resolution.

## Risks and Edge Cases

- The ten-iteration cap prevents infinite recursion but may leave deeply nested or cyclic variables partially unresolved.
- Unknown variables remain as placeholders, so patterns can fail to match silently rather than error.
- `resolve_userid` uses `pop()` for single resolution, meaning arrays return the last element in single-value contexts; multi-value resolution returns all values.
- Cache keys are only variable names, so cached values are safe only because each cache instance is tied to one context.
- `conditions` exists in `VariableContext` but is not directly used by `VariableResolver` in this file; common condition substitution happens in string/resource matchers.

## Test Signals

Inline tests cover username, userid, multiple variables, no-variable pass-through, Unicode prefix preservation, and dynamic variables bypassing cache by comparing epoch-time resolutions across a delay. Policy-level tests cover nested and multi-value expansion.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/policy/variables.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/serde_datetime.rs -->
# sources/object-store/rustfs/crates/policy/src/serde_datetime.rs

## Purpose

Provides serde helpers for IAM timestamps. Serialization always emits RFC3339, while deserialization accepts RFC3339 and a legacy RustFS human-readable timestamp format.

## Important APIs, Types, and Functions

- `LEGACY_FORMAT` is a `OnceLock<OwnedFormatItem>` for the legacy parser.
- `legacy_format()` lazily parses the legacy `time` format description.
- `parse_rfc3339_or_legacy(s)` tries `Rfc3339` first and falls back to the legacy format.
- `serialize(dt, serializer)` delegates to `time::serde::rfc3339`.
- `deserialize(deserializer)` reads a string and parses it with the compatibility parser.
- `option::serialize` and `option::deserialize` provide the same behavior for `Option<OffsetDateTime>`.

## Control Flow

Deserialization reads borrowed string data from serde, attempts RFC3339 parsing, and on failure attempts the legacy format `YYYY-MM-DD HH:MM:SS.ffffff +00:00:00`. Errors are converted to serde custom errors. Option serialization emits `Some` as an RFC3339 string and `None` as null/none.

## State and Persistence

Only global state is the lazily initialized legacy format descriptor. No persistence or I/O.

## Dependencies and Integration Points

Used by policy data types that need stable timestamp wire formats. Depends on `serde` and `time` formatting/parsing. The comments call out MinIO compatibility.

## Risks and Edge Cases

- Legacy parser expects fractional seconds and an offset with seconds. Legacy timestamps that omit fractional or offset seconds will fail.
- Serialization normalizes all supported inputs to RFC3339, so legacy formatting is read-only compatibility.
- `legacy_format().expect` will panic only if the hard-coded format description is invalid.

## Test Signals

Inline tests verify legacy RustFS timestamp parsing and RFC3339 parsing through a transparent serde wrapper.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/serde_datetime.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/service_type.rs -->
# sources/object-store/rustfs/crates/policy/src/service_type.rs

## Purpose

Defines a small service discriminator for policy-related service names.

## Important APIs, Types, and Functions

- `ServiceType` enum has `S3` and `STS` variants.
- `impl TryFrom<&str> for ServiceType` accepts `"s3"` and `"sts"` and returns `Error::InvalidServiceType` for anything else.

## Control Flow

Conversion is a direct string match with lower-case accepted spellings only.

## State and Persistence

No state beyond the enum value.

## Dependencies and Integration Points

Depends on crate `Error`. Likely used by policy parsing or API code to route service-specific authorization.

## Risks and Edge Cases

- Matching is case-sensitive; `"S3"` or `"STS"` are rejected.
- Only S3 and STS are represented, despite the policy action model also containing Admin and KMS families.

## Test Signals

No local tests in this file. Coverage would come from callers that parse service strings.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/service_type.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/utils.rs -->
# sources/object-store/rustfs/crates/policy/src/utils.rs

## Purpose

Provides JWT helper functions for generating and extracting signed claim tokens using HMAC SHA-512.

## Important APIs, Types, and Functions

- `generate_jwt<T: Serialize>(claims, secret)` creates a JWT with `Algorithm::HS512`.
- `extract_claims<T: DeserializeOwned + Clone>(token, secret)` decodes and validates a JWT with the same HS512 algorithm.

## Control Flow

Token generation creates a new HS512 header and signs serialized claims with `EncodingKey::from_secret(secret.as_bytes())`. Extraction calls `jsonwebtoken::decode` with `DecodingKey::from_secret` and `Validation::new(Algorithm::HS512)`, returning `TokenData<T>` or a jsonwebtoken error.

## State and Persistence

No state or persistence. Secrets are caller-supplied strings used only during the call.

## Dependencies and Integration Points

Depends on `jsonwebtoken` and `serde`. Used by authentication or tests needing signed policy/IAM claims.

## Risks and Edge Cases

- Security rests entirely on caller-provided secret strength and lifecycle.
- `Validation::new` enforces standard jsonwebtoken defaults for the algorithm; callers should confirm issuer/audience/expiration requirements are configured elsewhere if needed.
- The round-trip extraction test is commented out, so decoding behavior is not locally exercised.

## Test Signals

Inline active test verifies that `generate_jwt` returns a non-empty token for a simple claims struct. A decode round-trip test exists but is commented out.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/src/utils.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/tests/policy_is_allowed.rs -->
# sources/object-store/rustfs/crates/policy/tests/policy_is_allowed.rs

## Purpose

Integration-style test matrix for `Policy::is_allowed`. It builds policies and request arguments directly and checks allow/deny outcomes across action matching, resource matching, conditions, deny statements, and NotResource behavior.

## Important APIs, Types, and Functions

- `ArgsBuilder` is a convenience struct with owned fields for account, groups, action string, bucket, conditions, owner flag, object, claims, and deny-only flag.
- `policy_is_allowed(policy, args) -> bool` converts `ArgsBuilder` into runtime `Args`, parses action strings, and blocks on async policy evaluation with `pollster`.
- The `#[test_case]` matrix supplies many concrete policies and expected booleans.

## Control Flow

Each test case constructs a `Policy` with one statement, creates request args, then calls `Policy::is_allowed`. Empty `groups` becomes `None`; non-empty groups are cloned into `Some(Vec<String>)`. Action strings are parsed through `try_into`, so invalid action strings would panic in test setup.

## State and Persistence

No state or persistence. Tests allocate temporary policy/request values only.

## Dependencies and Integration Points

Imports the public `rustfs_policy::policy` API, S3 actions, serde JSON values, `HashMap`, and `test_case`. It exercises the crate as an external consumer rather than through private module access.

## Risks and Edge Cases

- Cases are numbered and somewhat repetitive, so failures can require inspecting the embedded policy/request pair.
- Tests mostly use single-statement policies; complex multi-statement interactions are covered more in `policy.rs`.
- Because `pollster::block_on` is used, the test avoids tokio runtime assumptions for policy evaluation.

## Test Signals

The matrix verifies:

- Allowed S3 actions against wildcard resources.
- Denial when action does not match.
- Object resource pattern matching.
- IP address condition success and failure using `aws:SourceIp`/`SourceIp`.
- Deny effect precedence for matching deny statements.
- `NotResource` allow outside a blacklist and denial inside the blacklist.

These tests complement inline unit tests by confirming the public policy evaluation API behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/tests/policy_is_allowed.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/Cargo.toml -->
# sources/object-store/rustfs/crates/protocols/Cargo.toml

## Purpose

Defines the `rustfs-protocols` crate package metadata, feature flags, runtime dependencies, optional protocol dependencies, dev dependencies, docs.rs metadata, and Linux-specific Tokio io-uring feature.

## Important APIs, Types, and Functions

This is a manifest, not Rust code. Key configuration:

- Package name `rustfs-protocols`, description "Protocol implementations for RustFS (FTPS, SFTP, etc.)".
- Features: empty default, `ftps`, `swift`, `webdav`, and `sftp`.
- Core workspace dependencies include `rustfs-iam`, `rustfs-credentials`, `rustfs-policy`, `rustfs-utils`, `rustfs-config`, `rustfs-storage-api`, and optional `rustfs-tls-runtime`.
- Async/runtime dependencies include `tokio`, `tracing`, `futures-util`, `async-trait`, `time`, and `bytes`.
- S3 DTO dependency is `s3s`.
- Optional protocol stacks pull in libunftp/unftp/rustls, Swift HTTP/crypto/archive dependencies, WebDAV hyper/dav dependencies, and SFTP russh dependencies.
- Dev dependencies include `tempfile`, `proptest`, `tracing-subscriber`, and test-enabled `tokio`.

## Control Flow

Cargo resolves optional dependencies only when corresponding features are enabled. The Linux target section enables Tokio's `io-uring` feature only on Linux.

## State and Persistence

No runtime state. The manifest influences build graph, feature unification, docs.rs builds, and dependency availability.

## Dependencies and Integration Points

This crate bridges protocol implementations with IAM, credentials, policy, config, storage API, and TLS runtime crates. Feature choices determine which protocol modules can compile and what external crates enter the dependency graph.

## Risks and Edge Cases

- Default features are empty, so consumers must opt into protocol features explicitly.
- Feature dependency sets are broad, especially Swift and WebDAV, increasing compile and supply-chain surface when enabled.
- `tokio-util` is optional but configured with feature `rt`; feature interactions should be checked if multiple protocol features require different Tokio-util capabilities.
- docs.rs builds all features, so optional dependencies must remain mutually compatible.

## Test Signals

Manifest-level tests are indirect through crate builds. Dev dependencies indicate property tests and async tests exist elsewhere in the protocols crate. No specific tests are in this file.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/common/client/mod.rs -->
# sources/object-store/rustfs/crates/protocols/src/common/client/mod.rs

## Purpose

Defines the common client module boundary for protocol code and re-exports the S3 storage backend trait under a protocol-neutral alias.

## Important APIs, Types, and Functions

- `pub mod s3;` exposes the S3 client backend module.
- `pub use s3::StorageBackend as S3StorageBackend;` re-exports the trait for callers that want a clear S3-specific backend interface.

## Control Flow

No runtime control flow. This file is module wiring.

## State and Persistence

No state or persistence.

## Dependencies and Integration Points

Integrates `common::client::s3` with the rest of the protocols crate. Consumers can import `S3StorageBackend` from the common client module instead of the nested S3 module.

## Risks and Edge Cases

Any future backend traits added here should avoid name collisions and preserve the existing re-export path for downstream code.

## Test Signals

No local tests; compile tests and downstream use validate this module boundary.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/common/client/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/common/client/s3.rs -->
# sources/object-store/rustfs/crates/protocols/src/common/client/s3.rs

## Purpose

Defines the asynchronous `StorageBackend` trait used by protocol drivers to perform S3-compatible storage operations. It abstracts object, bucket, copy, and multipart upload operations behind a single backend interface.

## Important APIs, Types, and Functions

- `#[async_trait] pub trait StorageBackend: Send + Sync` is object-safe for async implementors via `async_trait`.
- Associated type `Error: std::error::Error + Send + Sync + 'static`.
- Object operations: `get_object`, `get_object_range`, `put_object`, `delete_object`, `head_object`.
- Bucket operations: `head_bucket`, `list_objects_v2`, `list_buckets`, `create_bucket`, `delete_bucket`.
- Copy operation: `copy_object`.
- Multipart operations: `create_multipart_upload`, `upload_part`, `complete_multipart_upload`, `abort_multipart_upload`, `upload_part_copy`.
- Method inputs and outputs are S3 DTOs from `s3s::dto::*` where full S3 request surfaces are needed.

## Control Flow

This file defines an interface only. Implementors decide how to authenticate using `access_key` and `secret_key`, map DTOs to storage APIs, stream bodies, enforce bucket/object semantics, and translate errors into `Self::Error`.

## State and Persistence

No state in the trait. Implementations are expected to interact with persistent object storage, multipart upload state, bucket metadata, and authorization systems.

## Dependencies and Integration Points

Depends on `async_trait` and `s3s::dto`. Protocol implementations such as SFTP, FTPS, WebDAV, or Swift bridges can call this trait to perform S3 operations without depending directly on one storage engine. It is also re-exported as `S3StorageBackend` from `mod.rs`.

## Risks and Edge Cases

- Credentials are passed as `&str` to every operation, so implementors must avoid logging them and should consider lifetime/sensitive-data handling.
- Trait comments document S3 constraints such as 10,000 multipart parts and sorted completion parts, but the trait does not enforce them; implementors must validate.
- `get_object` has both `start_pos: Option<u64>` and a separate `get_object_range(start_pos, length)`, so callers and implementors need clear semantics for partial reads.
- Copy and multipart methods accept full DTOs; implementors must correctly preserve metadata, SSE, object lock, conditional headers, cross-account fields, and abort idempotency.

## Test Signals

No local tests in this trait file. Compile-time implementation checks and protocol integration tests should validate conformance.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/common/client/s3.rs -->
