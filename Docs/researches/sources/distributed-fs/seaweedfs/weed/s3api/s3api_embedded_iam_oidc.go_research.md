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
