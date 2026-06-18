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
