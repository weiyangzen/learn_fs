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
