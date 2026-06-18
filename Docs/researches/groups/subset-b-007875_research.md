# subset-b-007875 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_embedded_iam.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_embedded_iam.go

## Purpose

This file implements SeaweedFS's embedded IAM query API inside the S3 server. It exposes AWS IAM-like operations for users, access keys, inline policies, managed policies, groups, service accounts, user tags, request authentication, error serialization, persistence, and post-mutation reloads. The central type is `EmbeddedIamApi`, which binds a `credential.CredentialManager`, the runtime `IdentityAccessManagement` cache, a mutation lock, testing hooks, and a `readOnly` guard.

The implementation deliberately mixes two persistence surfaces. User/group/service-account shape still flows through `iam_pb.S3ApiConfiguration` and `PutS3ApiConfiguration`, while managed policies and inline policy documents use `credentialManager` APIs so policy JSON can round-trip losslessly and store-specific behavior such as transactional rename can be honored. `ExecuteAction` is the main dispatcher that coordinates these surfaces.

## Important APIs, types, and helpers

`NewEmbeddedIamApi`, `GetS3ApiConfiguration`, `PutS3ApiConfiguration`, `ReloadConfiguration`, and `refreshIAMConfiguration` are the lifecycle APIs. Test hooks can replace the configuration and reload functions, while production loads and saves through the credential manager.

Constants define access key prefixes, random key lengths, service-account IDs, and limits such as `MaxManagedPoliciesPerUser`, `MaxServiceAccountsPerUser`, and user tag limits. Type aliases map the local names used by older S3 code to shared `weed/iam` response types, keeping XML response structs centralized.

Utility functions wrap shared IAM helpers for hashing, random strings, slice comparison, and S3 action mapping. `iamValidateStatus` accepts only `Active` and `Inactive`. `newIamErrorResponse` and `writeIamErrorResponse` translate embedded IAM errors to XML and HTTP status codes, including 404 for `NoSuchEntity`, 409 for conflicts, 400 for malformed or validation errors, 403 for access denied and limit exceeded, and 501 for `NotImplemented`.

User APIs include `ListUsers`, `CreateUser`, `GetUser`, `UpdateUser`, `DeleteUser`, `SetUserStatus`, and helpers such as `findIdentityByName`. Access key APIs include `ListAccessKeys`, `CreateAccessKey`, `DeleteAccessKey`, and `UpdateAccessKey`. Policy APIs include `CreatePolicy`, `DeletePolicy`, `ListPolicies`, `GetPolicy`, `ListPolicyVersions`, `GetPolicyVersion`, `CreatePolicyVersion`, `DeletePolicyVersion`, `iamPolicyNameFromArn`, `iamPolicyArn`, `GetPolicyDocument`, `getActions`, and `recomputeActions`.

Inline user policy APIs are `PutUserPolicy`, `GetUserPolicy`, `DeleteUserPolicy`, and `ListUserPolicies`. Tag APIs are `parseTagListParams`, `parseTagKeysParams`, `mergeUserTags`, `TagUser`, `UntagUser`, and `ListUserTags`. Managed-policy attachment APIs are `AttachUserPolicy`, `DetachUserPolicy`, and `ListAttachedUserPolicies`.

Service account APIs are `CreateServiceAccount`, `DeleteServiceAccount`, `ListServiceAccounts`, `GetServiceAccount`, and `UpdateServiceAccount`. Group APIs cover create/delete/update/get/list, membership, managed policy attachment, `ListGroupsForUser`, and group inline policies. HTTP/auth entry points are `handleImplicitUsername`, `AuthIam`, `ExecuteAction`, and `DoActions`.

## Control flow

HTTP requests enter `DoActions`. It ensures a request ID, parses form data, fills implicit usernames for selected self-service actions, injects `CreatedBy` for service accounts, calls `ExecuteAction`, then writes either IAM XML errors or a successful XML response.

`AuthIam` is a middleware for IAM endpoints. It first allows all requests when IAM is disabled. Otherwise it authenticates the SigV4 request before parsing the form body, because IAM signature verification needs the original body hash. After successful auth, it parses form fields, stores the authenticated identity in context, allows self-service access-key operations against the caller's own user, and otherwise requires admin or explicit `iam:<Action>` permission against `arn:aws:iam:::*`.

`ExecuteAction` serializes all IAM operations with `policyLock`, enforces `readOnly`, dispatches OIDC provider actions before loading S3 configuration, loads `iam_pb.S3ApiConfiguration`, switches on `Action`, sets `changed`, persists if needed, reloads runtime IAM maps, sets the request ID on the response, and returns. Some operations persist internally through `credentialManager` and set `changed=false`; the tail still reloads for policy and targeted-create actions that change the runtime cache.

User and key flows mutate `s3cfg.Identities`. `CreateUser` validates uniqueness and appends a disabled-false identity; in `ExecuteAction` it uses `credentialManager.CreateUser` for a targeted persistent write when `skipPersist` is false, avoiding a full rewrite of existing users. `UpdateUser` performs a store-level rename first where supported, migrates inline policies as fallback, then renames identity, group memberships, and service-account parent references. `DeleteUser` refuses to remove users with service accounts and removes the user from groups.

Policy flows either parse AWS IAM JSON to SeaweedFS `policy_engine.PolicyDocument` or reconstruct legacy documents from `ident.Actions`. `getActions` accepts `Allow` statements only, maps S3 actions such as `s3:Get*` to internal actions, handles bare `"*"` resources, parses S3 ARNs, and emits internal action strings such as `Read:bucket/path`. `PutUserPolicy` persists the original inline policy document before recomputing aggregate `ident.Actions`; `GetUserPolicy` prefers the stored document for lossless round-trip and falls back to reconstruction from actions. Managed policies are single-version: `CreatePolicyVersion` replaces the document only when `SetAsDefault=true`, and `DeletePolicyVersion` refuses to delete `v1` because it is always the default.

Service accounts are children of IAM users. `CreateServiceAccount` validates parent user, description length, per-user limit, generated ID syntax, future expiration, independent action-copy semantics, and random access/secret key generation before appending both the service-account record and parent ID reference. Updates allow status, description, and expiration changes; deletion removes both the service-account object and parent reference.

Groups are held in `s3cfg.Groups`. Deletion refuses non-empty membership or attached managed policies. Group inline policies are persisted through `credentialManager` and rehydrated on reload rather than materialized in the protobuf group. Managed policy attachment validates the policy exists through `credentialManager` but stores the policy name on the group config.

## State and persistence behavior

The major state objects are `iam_pb.S3ApiConfiguration.Identities`, `Groups`, `ServiceAccounts`, credential-manager policy stores, and the runtime `IdentityAccessManagement` cache. `policyLock` protects the whole read-modify-write operation. Persistent writes are intentionally action-specific: ordinary config mutations call `PutS3ApiConfiguration`; managed policy and inline policy operations call credential-manager APIs; targeted `CreateUser` bypasses full configuration saves; OIDC is dispatched elsewhere.

Reload behavior is critical. When `changed=true`, `ExecuteAction` saves the config unless `skipPersist` is set, then reloads runtime IAM state so new access keys and status changes are visible. When `changed=false` but the credential manager changed policy/user state, a special reload clause refreshes the cache. Some helper methods like `AttachUserPolicy` also perform best-effort refresh, then `ExecuteAction` may reload again.

`skipPersist` suppresses persistent writes for configuration-mutating actions. The targeted `CreateUser` optimization explicitly honors this, leaving only the in-memory response path. User policy document persistence happens before `ident.Actions` changes so the config and policy document store do not diverge after a failed write.

## Dependencies and integration points

The file depends on AWS SDK IAM structs for response compatibility, `weed/iam` for XML response types and IAM helper functions, `credential.CredentialManager` for persistence, `iam_pb` protobuf state, `filer_pb.ErrNotFound` for missing config bootstrap, `policy_engine` for IAM JSON policy parsing, `s3_constants` action names and context helpers, `s3err` XML/error writing, and request IDs.

It integrates with the wider S3 server through `IdentityAccessManagement` for authentication, access-key lookup, runtime permission checks, and reloads; through S3 route handlers via `DoActions` and `AuthIam`; through the credential-store implementations for memory, filer, and database-backed persistence; and with Terraform/AWS IAM clients via AWS-shaped action names and XML response structures.

## Risks and edge cases

There is a high risk of cache/store divergence if a mutation persists through the credential manager but misses a reload path. `ExecuteAction` has explicit special cases, but any new action must choose `changed` carefully. Another risk is split persistence: users/groups/service accounts are protobuf config state, while policy documents and attachments can be store-specific; inconsistent store implementations could expose behavior differences.

`getActions` accepts only `Allow` effects and known S3 action mappings; deny policies, conditions, principals, and many AWS IAM features are outside this reduced model. Policy versioning is intentionally single-version, which is compatible with some clients but not all AWS semantics. `GetUserPolicy` fallback is lossy and exists mainly for older `ident.Actions` state.

Random ID generation and caller-supplied access keys are validated, but collision checking only covers supplied access key IDs; random-key collisions are statistically unlikely but not retried in this function. `handleImplicitUsername` parses SigV4 headers manually and depends on the runtime IAM cache being current. User tag parsing iterates sparse AWS member keys by map sort, while OIDC's related helper uses contiguous indexes; behavior differs across files.

The authorization model allows a small self-service set without admin if the target user is the caller or omitted. New IAM actions need explicit consideration in `iamSelfServiceActions`, `readOnly`, `DoActions` implicit username handling, and permission verification. Group managed policies have no per-group limit in this file, unlike user managed policies.

## Test signals

The companion tests exercise user create/list/get/update/delete, targeted create persistence, `skipPersist`, valid ARN responses, implicit username resolution, managed policy CRUD and single-version updates, inline policy exact round trips, fallback reconstruction, wildcard resource parsing, access-key supplied credential validation, duplicate/collision handling, user/access-key status, disabled identity lookup, authentication-before-parse ordering, direct `ExecuteAction`, and read-only mode.

Separate tag tests cover `TagUser`, `UntagUser`, `ListUserTags`, duplicate keys, replacement, validation limits, no-op missing untag keys, and not-found responses. Governance and encrypted-copy tests are not direct IAM handler tests but pin adjacent S3 permission/action and metadata contracts that rely on the same constants and identity system.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_embedded_iam.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_embedded_iam_oidc.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_embedded_iam_oidc.go

## Purpose

This file extends the embedded IAM API with OpenID Connect provider actions. These operations are not stored in `iam_pb.S3ApiConfiguration`; instead they are short-circuited from `ExecuteAction` and routed to the IAM integration manager. The result is an AWS IAM-compatible query API surface for creating, listing, fetching, deleting, tagging, and updating OIDC provider records used by STS/web-identity integrations.

## Important APIs, types, and helpers

Action constants cover `GetOpenIDConnectProvider`, `ListOpenIDConnectProviders`, `CreateOpenIDConnectProvider`, `DeleteOpenIDConnectProvider`, `AddClientIDToOpenIDConnectProvider`, `RemoveClientIDFromOpenIDConnectProvider`, `UpdateOpenIDConnectProviderThumbprint`, `TagOpenIDConnectProvider`, and `UntagOpenIDConnectProvider`.

`isOIDCProviderAction` classifies the action family. `dispatchOIDCProviderAction` obtains an `integration.IAMManager` from `EmbeddedIamApi.oidcIAMManager` and calls the specific handler. Handler methods map query parameters onto integration records and shared `iamlib` response structs. `extractMemberList` reads AWS-style `Prefix.member.N` arrays. `extractTags` reads `Tags.member.N.Key` and `Tags.member.N.Value` pairs into a map. `requireProviderArn` validates the common ARN parameter.

`oidcIAMManager` is the integration bridge: it requires `e.iam`, `e.iam.iamIntegration`, and an implementation of `IAMManagerProvider`, then returns `GetIAMManager()`.

## Control flow

`ExecuteAction` calls `dispatchOIDCProviderAction` before loading or saving S3 API configuration. If the action is not OIDC-related, dispatch returns `(nil, nil, false)` and normal IAM handling continues. If it is OIDC-related but no manager is configured, dispatch returns an IAM service-failure error.

Create flow trims `Url`, requires at least one `ClientIDList` member, collects optional thumbprints and tags, derives the provider ARN from the STS account ID and URL, builds `integration.OIDCProviderRecord`, and calls `mgr.CreateOIDCProvider`. Duplicate providers map to `EntityAlreadyExists`; other validation/store errors map to `InvalidInput`. The response includes the provider ARN and any tags.

Fetch/list flows call `ListOIDCProviders` and `GetOIDCProvider`. List returns only ARN entries. Get returns URL, client IDs, thumbprints, optional UTC create date, and tags. Delete requires `OpenIDConnectProviderArn` and calls `DeleteOIDCProvider`; unlike some other operations, any delete error maps to service failure.

Mutation flows for client IDs, thumbprints, tags, and untagging validate required ARN and list/member inputs, call the matching manager method, map `ErrOIDCProviderNotFound` to `NoSuchEntity`, and otherwise map validation-like operations to `InvalidInput` or store failures to `ServiceFailure`.

## State and persistence behavior

This file owns no direct in-memory state and does not save `S3ApiConfiguration`. All durable state belongs to `integration.IAMManager` and its backing store. The account ID used for ARN derivation comes from `mgr.GetSTSService().Config.AccountId`. Response tag order is map iteration order, so it is not stable.

Because OIDC actions bypass the normal `changed` and reload path, they depend on the integration manager to make state immediately visible to STS/OIDC consumers. They also participate in `readOnly`: the main file explicitly allows only list/get OIDC actions when `EmbeddedIamApi.readOnly` is true, so create/delete/update/tag actions are blocked before dispatch.

## Dependencies and integration points

The file depends on AWS IAM error constants, shared `weed/iam` response structs, and `weed/iam/integration` for OIDC records and manager operations. It integrates with the main embedded IAM dispatcher, with `IdentityAccessManagement.iamIntegration`, and with STS configuration for account IDs. The derived ARN contract must match the integration package's OIDC provider store and any STS AssumeRoleWithWebIdentity implementation.

## Risks and edge cases

`extractMemberList` stops at the first missing index, so sparse AWS query arrays such as member 1 and member 3 only return member 1. `extractTags` similarly stops at the first missing key and silently overwrites duplicate keys in the map. There is no tag-count or tag-length validation in this file; validation may exist in the integration layer, but the embedded API does not enforce the user-tag limits used elsewhere.

Error mapping is not fully symmetric. Create maps non-duplicate manager errors to `InvalidInput`; delete maps all errors to service failure; get maps all errors to `NoSuchEntity`. This may be acceptable for current manager errors but could hide infrastructure failures or validation details.

OIDC dispatch assumes the integration object implements `IAMManagerProvider`. A deployment with IAM enabled but without that provider receives service failure for all OIDC provider actions. Because these actions bypass S3 configuration reloads, any future runtime cache around OIDC providers would need explicit refresh handling.

## Test signals

No OIDC-specific test file is included in this work item. The main embedded IAM tests indirectly cover dispatch constraints only through read-only allow-list behavior and generic `ExecuteAction`/error response paths. Stronger test coverage should include create/list/get/update/delete/tag/untag against a fake `IAMManager`, duplicate and not-found errors, read-only blocking for write actions, sparse member handling, and ARN derivation from STS account ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_embedded_iam_oidc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_embedded_iam_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_embedded_iam_test.go

## Purpose

This file is the main regression suite for the embedded IAM API. It builds a memory-backed `EmbeddedIamApiForTest`, drives the API through both AWS SDK-generated IAM requests and direct form posts, and asserts XML responses, persistent state, runtime reload behavior, error codes, and IAM authentication details. The tests document compatibility requirements for Terraform/AWS IAM clients and protect several prior SeaweedFS issues.

## Important APIs, types, and helpers

`EmbeddedIamApiForTest` embeds `EmbeddedIamApi` and tracks `mockConfig`. `NewEmbeddedIamApiForTest` creates a memory credential store, a credential manager, an IAM runtime object, and hook implementations for `GetS3ApiConfiguration`, `PutS3ApiConfiguration`, and reload. The fixture syncs direct `mockConfig` test setup into the memory store, then loads cloned protobuf state back out.

`executeEmbeddedIamRequest` routes a request through a `mux.Router` bound to `/` and optionally XML-unmarshals the response. `embeddedIamErrorResponseForTest`, `extractEmbeddedIamErrorCodeAndMessage`, and `extractEmbeddedIamRequestID` parse response details across the XML forms emitted by IAM and S3 error writers. `mustMarshalJSON` supports direct runtime IAM loading.

The tests call many public methods indirectly through `DoActions`, and some lower-level methods directly (`PutGroupPolicy`, `GetUserPolicy`, `getActions`, `ExecuteAction`) when that is the narrowest way to assert behavior.

## Control flow and coverage

User lifecycle coverage includes create, list, get, update, delete, not-found errors, valid ARN generation, implicit username lookup from a SigV4 authorization header, and a full workflow. `TestEmbeddedIamCreateUserDoesNotSaveAllUsers` verifies the optimized `CreateUser` path does not call full `PutS3ApiConfiguration`. `TestEmbeddedIamCreateUserSkipPersist` verifies `skipPersist=true` avoids any store write.

Policy coverage includes managed policy creation, delete-conflict when attached, attach/detach/list user policies, idempotent attach, detach-not-attached errors, policy limit enforcement, malformed JSON, single-version `CreatePolicyVersion`, missing policy on policy-version create, and rejection of `SetAsDefault=false`/omitted. Tests also verify policy version retrieval reflects updates.

Inline policy coverage includes `PutUserPolicy`, `GetUserPolicy`, `DeleteUserPolicy`, `ListUserPolicies`, missing user errors, exact document round-trip for issue #9008, lossy fallback reconstruction from `ident.Actions`, wildcard resource acceptance for issue #9209, and group inline policy CRUD. This is the suite's strongest signal that policy documents must be persisted separately from simplified action strings.

Access key coverage includes generated credentials, caller-supplied keys, missing user failure without mutation, weak key validation, duplicate access-key rejection without owner-name leakage, partial supplied key rejection, boundary lengths, deletion, status updates, list status defaults, disabled user lookup, and inactive access key lookup.

Auth coverage includes `TestAuthIamAuthenticatesBeforeParseForm`, which signs a real IAM request and asserts middleware authenticates before form parsing, and `TestOldCodeOrderWouldFail`, which demonstrates why parsing first causes `SignatureDoesNotMatch`. `TestEmbeddedIamReadOnly` asserts write operations are forbidden while read operations still work. `TestEmbeddedIamNotImplementedAction` verifies 501 XML error shape and request ID propagation.

## State and persistence behavior

The fixture's memory store is intentionally used as the source of truth after first sync. Several tests seed both `mockConfig` and the credential manager to distinguish full-config saves from targeted writes. Clone behavior avoids protobuf slice aliasing between store-loaded config and the caller's `s3cfg`.

Persistence assertions are direct: users are read back with `credentialManager.GetUser`, inline policies with `GetUserInlinePolicy`, managed policies through subsequent IAM API calls, and runtime identity cache through `api.iam.lookupByIdentityName` or `LookupByAccessKey`. Tests also inspect `api.mockConfig` after mutations to make sure identity slices, credentials, actions, policy names, disabled flags, and service-related fields move as expected.

The suite repeatedly constructs direct requests with `PostForm` and `Form` already populated as well as AWS SDK requests that require `Build()`. This exercises both pre-parsed test shortcuts and actual form parsing in `DoActions`.

## Dependencies and integration points

The tests depend on AWS SDK IAM request builders, AWS ARN validation, Gorilla mux routing, memory credential store, credential manager, IAM protobufs, policy engine types, S3 constants, S3 error codes, request IDs, protobuf cloning, and testify assertions. They also use S3 SigV4 helper functions available in the package to build a valid IAM-service signature.

These tests are the main integration signal between embedded IAM, credential persistence, runtime IAM lookup, XML response types from `weed/iam`, and client compatibility expectations from Terraform and the AWS SDK.

## Risks and gaps

The fixture uses the memory store, so it cannot fully reproduce database foreign-key behavior, filer store write amplification, or distributed reload timing. Some tests call methods directly and may bypass `ExecuteAction` persistence/reload behavior. OIDC provider behavior is not covered here despite read-only allow-list entries. Service-account and group management coverage is lighter than user/policy/access-key coverage.

The test fixture's one-time sync from `mockConfig` to store can be subtle: tests that mutate `mockConfig` after first load may need to reset or save explicitly. Because the memory store may reorder identities after save/load, tests already avoid relying on identity order in some cases, but future tests must keep that in mind.

## Test signals

This file provides high-value regression signals for issue-driven behavior: Terraform-compatible user ARNs and policy updates, no full user rewrite on create, no persistent write under `skipPersist`, exact inline-policy round trips, wildcard `"Resource":"*"` handling, safe supplied access keys, request ID propagation, body-preserving auth, disabled/inactive credential enforcement, managed policy attachment limits, and read-only mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_embedded_iam_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_embedded_iam_user_tags_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_embedded_iam_user_tags_test.go

## Purpose

This file provides focused coverage for embedded IAM user tag operations: `TagUser`, `ListUserTags`, and `UntagUser`. It verifies AWS query-encoded tag inputs mutate `iam_pb.Identity.Tags` correctly, response XML can be unmarshaled into shared IAM response types, validation errors map to expected IAM codes, and tag limits are enforced.

## Important APIs, types, and helpers

`postTagAction` sends a form-encoded POST through a test mux router bound to `EmbeddedIamApiForTest.DoActions`. It sets `PostForm`, `Form`, and `Content-Type`, making it suitable for hand-built tag edge cases that are awkward to express with the AWS SDK. `findIdentity` searches an `iam_pb.S3ApiConfiguration` by name so tests do not assume identity ordering.

The tests reuse the fixture and error parsers from `s3api_embedded_iam_test.go`. AWS SDK request builders are used for normal `TagUser`, `ListUserTags`, `UntagUser`, and not-found request shape; hand-built `url.Values` are used for duplicate, empty, limit, and malformed member parameters.

## Control flow and coverage

`TestEmbeddedIamTagUser` creates an `alice` identity, sends two tags through the AWS SDK, and asserts both tags are persisted in order with expected key/value pairs. `TestEmbeddedIamListUserTags` seeds `bob` with tags and confirms the response contains both tags and `IsTruncated=false`. `TestEmbeddedIamUntagUser` removes one existing tag and one missing tag, asserting the missing key is ignored and only the requested existing key is removed.

Validation tests cover a too-long tag key returning `ValidationError`, replacement of an existing tag value without duplicating the tag, exceeding `MaxUserTags` returning `LimitExceeded`/HTTP 403, no-op untag for a missing key, duplicate tag keys in a single request returning `InvalidInput`, invalid untag key cases, and `TagUser` against a missing user returning `NoSuchEntity`.

## State and persistence behavior

All tested state is on `iam_pb.Identity.Tags` within `api.mockConfig`, persisted through the normal `DoActions` and `ExecuteAction` changed-config path. `TagUser` merges new tags into existing tags, preserving prior order and replacing duplicate existing keys. `UntagUser` filters the tag slice and leaves unknown keys untouched. `ListUserTags` is read-only and does not mutate the config.

The tests assert in-memory fixture state after API calls, which confirms that the configuration save/load hook preserves tag fields. Since the fixture uses memory-backed persistence, it validates protobuf state behavior rather than a specific external store.

## Dependencies and integration points

This file depends on the main embedded IAM test fixture, AWS SDK IAM tag request builders, Gorilla mux, `iam_pb.UserTag`, shared IAM response aliases, `MaxUserTags`, `MaxUserTagKeyLength`, and IAM error constants. It integrates with the tag parsing helpers and dispatcher cases in `s3api_embedded_iam.go`.

## Risks and gaps

The tests do not cover maximum tag value length directly, empty tag value acceptance, sparse `Tags.member.N` numbering, `ListUserTags` for missing users, `UntagUser` missing users, or persistence behavior in non-memory stores. They also do not exercise auth/permission checks around tag APIs; the requests are routed straight to `DoActions` without `AuthIam` middleware.

Because `postTagAction` sets both `PostForm` and `Form`, it can bypass some parsing failure modes that would occur with malformed HTTP bodies. AWS SDK tests cover standard encoding, while hand-built tests mainly cover parser logic after form values exist.

## Test signals

The file strongly signals that user tags are bounded to 50 entries, tag keys are bounded to 128 characters, duplicate keys inside a request are rejected, existing keys are replaced rather than duplicated, unknown untag keys are ignored, and tag list pagination is intentionally not implemented because the bounded tag set fits in one response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_embedded_iam_user_tags_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_encrypted_volume_copy_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_encrypted_volume_copy_test.go

## Purpose

This file is a focused regression test for S3 CopyObject behavior on encrypted and/or compressed SeaweedFS volume chunks. It protects `S3ApiServer.createDestinationChunk`, ensuring copied chunk metadata preserves encryption keys, compression flags, offsets, sizes, and ETags. The motivating issue is that failing to preserve `IsCompressed` could lead to double-compression and unreadable copied objects on encrypted volumes.

## Important APIs, types, and helpers

The tested API is `(*S3ApiServer).createDestinationChunk`, called with a source `*filer_pb.FileChunk`, destination offset, and destination size. Test data uses `filer_pb.FileChunk` fields `Offset`, `Size`, `CipherKey`, `IsCompressed`, and `ETag`; the scenario test uses `util.GenCipherKey()` to simulate encrypted volume chunks.

There are no custom helper functions. The suite uses table-driven subtests and `bytes.Equal` for cipher-key comparison.

## Control flow and coverage

`TestCreateDestinationChunkPreservesEncryption` runs four cases: encrypted and compressed, encrypted only, compressed only, and neither encrypted nor compressed. For each, it calls `createDestinationChunk` and asserts the destination chunk has the requested offset and size while preserving or omitting `CipherKey` and `IsCompressed` according to the source. It also asserts `ETag` preservation.

`TestEncryptedVolumeCopyScenario` documents issue #7530 with a multi-chunk encrypted-volume copy scenario. It builds two chunks with generated cipher keys and `IsCompressed=true`, calls `createDestinationChunk` for each, and asserts compression, cipher key, offset, size, and ETag are preserved. This is closer to the real copy path, where multiple filer chunks make up one S3 object.

## State and persistence behavior

These tests do not touch durable state or the filer. They validate pure chunk transformation behavior. The state of interest is metadata copied from the source chunk to the destination chunk. Because cipher keys are byte slices, the tests check value equality, not whether the slice is deep-copied.

## Dependencies and integration points

The file depends on `filer_pb.FileChunk`, `S3ApiServer`, and `util.GenCipherKey`. It integrates with the S3 CopyObject/chunk-copy implementation where `createDestinationChunk` is used to build destination metadata for copied or renamed objects. Correct behavior is especially important when volume encryption and compression are enabled in the filer/volume layer.

## Risks and gaps

The tests do not execute a full S3 CopyObject request, do not read back copied object data, and do not verify filer persistence. They also do not assert all `FileChunk` fields, such as file ID, modified timestamp, source file ID semantics, or whether metadata slices are aliased. If future copy code mutates `CipherKey`, a value-equality-only test may miss aliasing side effects.

The scenario test documents expected behavior but remains a unit-level check around `createDestinationChunk`; it does not prove encrypted-volume copy works end to end with real compression/encryption codecs.

## Test signals

The key signal is that chunk copy must be metadata-preserving for encryption and compression. `CipherKey`, `IsCompressed`, and `ETag` are part of the object's readability contract, not incidental metadata. Any refactor of copy/rename chunk creation should keep these assertions intact or add stronger end-to-end coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_encrypted_volume_copy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_governance_permissions_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_governance_permissions_test.go

## Purpose

This file documents and partially tests S3 Object Lock governance-retention bypass permission behavior. It focuses on action/resource string generation, bypass header parsing, expected retention-mode decision logic, and the `ErrGovernanceBypassNotPermitted` contract. Several tests are intentionally skipped because full validation requires an integrated S3 API server and IAM setup.

## Important APIs, types, and helpers

The file references `s3_constants.ACTION_BYPASS_GOVERNANCE_RETENTION`, `s3_constants.ACTION_ADMIN`, `RetentionModeCompliance`, `RetentionModeGovernance`, and `GetBucketAndObject`. It also checks package errors `ErrGovernanceBypassNotPermitted` and `ErrGovernanceModeActive`. The implementation under test is described as `checkGovernanceBypassPermission` and `checkObjectLockPermissions`, though most active tests simulate their internal string/branch logic instead of invoking them directly.

## Control flow and coverage

Resource generation tests trim a leading slash from object names and combine bucket/object into paths such as `bucket/object`, `bucket/folder/object`, or `bucket/` for empty/root objects. Action generation tests combine those paths with `BypassGovernanceRetention:` and `Admin:` prefixes, matching the internal permission strings expected by IAM identity checks.

Header tests assert that only an exact `x-amz-bypass-governance-retention: true` enables bypass; false, missing, empty, or invalid values do not. Method-call pattern tests document how DELETE and PUT handlers extract bucket, object, version ID, versioning status, and bypass header before calling object-lock permission checks.

Retention-mode tests simulate the expected decision tree: compliance mode cannot be bypassed; governance mode without bypass returns governance-active error; governance mode with bypass but without permission returns bypass-not-permitted; governance mode with bypass and permission succeeds. `TestGovernanceBypassNotPermittedError` asserts the error constant message and simulates the branch where bypass is requested but permission is absent.

Skipped tests document intended integration behavior: `checkGovernanceBypassPermission` should authenticate the request, test `BypassGovernanceRetention` permission, fall back to admin permission, and deny anonymous or unauthorized users. End-to-end object-lock tests are skipped because they need full S3 server setup.

## State and persistence behavior

The active tests are stateless. They construct requests and strings locally without mutating IAM, bucket metadata, object retention records, or persistence layers. The skipped tests describe stateful integration with IAM identities and object-lock retention metadata, but no durable state is exercised here.

## Dependencies and integration points

The tests integrate conceptually with S3 object-lock handlers: `DeleteObjectHandler`, `DeleteMultipleObjectsHandler`, `PutObjectHandler`, and `PutObjectRetentionHandler`. They depend on IAM permission evaluation through the action names generated here and on object-lock retention modes from S3 constants. The intended production path must bridge HTTP headers, bucket/object parsing, versioning checks, object retention metadata, and IAM authorization.

## Risks and gaps

Most tests validate duplicated logic rather than invoking production methods. That means a production implementation could drift while these tests still pass if the copied string logic remains unchanged. Several high-value tests are skipped, including actual IAM permission success/failure, admin fallback, anonymous denial, and handler-level object-lock enforcement.

There is a subtle inconsistency in action/path generation across tests: some resource tests build `bucket + "/" + strings.TrimPrefix(object, "/")`, producing `bucket/` for empty objects, while one action-generation test expects bucket-only action `BypassGovernanceRetention:test-bucket` from `bucket + object`. Production code must have one canonical resource format, or IAM policies may not match for bucket-level operations.

Unicode and special-character paths are only checked for string construction/no panic, not URL escaping, canonical request behavior, or IAM policy matching. Header parsing is case-sensitive for the value `"true"`, which may or may not be intended relative to AWS behavior.

## Test signals

The file's strongest signal is the security posture change: governance bypass must not trust a client-provided admin header; it must use IAM authentication and permission checks. It also pins the expected permission action name `BypassGovernanceRetention`, admin fallback action, exact bypass header condition, and distinct errors for active governance mode versus requested bypass without permission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_governance_permissions_test.go -->
