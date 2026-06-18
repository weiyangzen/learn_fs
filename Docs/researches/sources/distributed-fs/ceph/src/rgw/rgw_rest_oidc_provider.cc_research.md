# sources/distributed-fs/ceph/src/rgw/rgw_rest_oidc_provider.cc

## Purpose

`rgw_rest_oidc_provider.cc` implements IAM OpenID Connect provider operations for RGW. It supports create, delete, get, list, add/remove client id, and replace thumbprint list, with IAM permission checks and optional forwarding to the metadata master zone.

## Important APIs and Functions

`forward_oidc_iam_request()` wraps shared IAM forwarding. `RGWRestOIDCProvider::verify_permission()`, `check_caps()`, and `send_response()` provide common base behavior. `format_creation_date()` formats AWS-style creation timestamps. `validate_provider_arn()` parses and validates OIDC provider ARNs while allowing provider URLs with ports.

Concrete operations are `RGWCreateOIDCProvider`, `RGWDeleteOIDCProvider`, `RGWGetOIDCProvider`, `RGWListOIDCProviders`, `RGWAddClientIdToOIDCProvider`, `RGWRemoveClientIdFromOIDCProvider`, and `RGWUpdateOIDCProviderThumbprint`.

## Control Flow

Create reads `Url`, `ClientIDList.member.*`, and `ThumbprintList.member.*`, enforces maximum lengths/counts, derives tenant/account, builds an ARN from `url_remove_prefix(provider_url)`, sets creation date, forwards if not metadata master, and stores the provider exclusively. Delete/get parse `OpenIDConnectProviderArn`, validate the account component against the authenticated account or tenant, and call the SAL driver's delete/load API. List fetches all providers for the account and emits their ARNs.

Add/remove client id and update thumbprints validate ARN and request fields, load the provider with a version tracker, optionally forward to master, mutate `client_ids` or `thumbprints`, and store non-exclusively with the version tracker. Add is idempotent for an existing client id. Remove is a no-op success if the client id is absent. Thumbprint update replaces the full list.

## State and Persistence Behavior

Persistent state is `RGWOIDCProviderInfo`: tenant/account, provider URL, ARN, creation date, client ids, and thumbprints. The SAL driver stores, loads, lists, and deletes provider records. Mutations use `RGWObjVersionTracker`, but this file does not use the shared retry helper for raced writes, so version conflicts may surface directly.

## Dependencies and Integration Points

The file depends on RGW IAM permission evaluation, shared IAM forwarding, OIDC provider metadata types, SAL OIDC APIs, request identity/account data, and formatter output. It is instantiated from `rgw_rest_iam.cc` action mappings.

## Risks and Edge Cases

ARN validation is custom and only accepts `arn:aws:iam::<tenant>:oidc-provider/...`, with account matching the caller. Create validates max thumbprints and max client ids, but thumbprint update validates non-empty and per-item length without enforcing the max count. Client-id add does not enforce the max total count after appending. Response section names for add/remove/update include duplicated or incorrect names in places, including thumbprint update using `AddClientIDToOpenIDConnectProviderResponse`.

Non-master operations load the provider before forwarding for add/remove/update. If the master changes state, local mutation uses the pre-forward loaded state and version tracker. Error mapping converts unexpected load/delete failures to `ERR_INTERNAL_ERROR` but leaves `-ENOENT` and `-EINVAL` as-is.

## Test Signals

Tests should cover URL/client/thumbprint length and count limits, ARN parser variants including localhost ports, account mismatch rejection, IAM permission fallback to caps, create exclusive conflict, list formatting, add idempotency, remove absent idempotency, thumbprint replacement, multisite forwarding, concurrent version conflicts, and exact XML response section names expected by IAM clients.
