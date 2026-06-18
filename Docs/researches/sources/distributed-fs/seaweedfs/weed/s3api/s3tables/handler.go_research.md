# sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler.go

## Purpose
This file defines the S3 Tables API handler core: constants, handler configuration, operation dispatch, principal extraction, request/response helpers, ARN generation, and tag-reading utility.

## Important APIs and types
Constants define table storage root, default account/region, extended-attribute keys, and a 10 MB request body limit. `S3TablesHandler` stores region, account ID, default-allow flag, trusted flag, and optional IAM authorizer. Setters configure region/account/default allow/trusted mode. `FilerClient` abstracts access to a Seaweed filer client. `HandleRequest` dispatches by `X-Amz-Target` operation suffix to bucket, namespace, table, policy, and tag handlers. Principal helpers include `getAccountID`, `normalizePrincipalID`, and `getIdentityActions`. HTTP helpers include `readRequestBody`, `writeJSON`, and `writeError`. ARN helpers generate bucket/table ARNs. `isAuthError`, `readTags`, and `mapKeys` support downstream handlers.

## Control flow and state behavior
`HandleRequest` requires `X-Amz-Target`, strips any namespace prefix before the last dot, switches to the correct handler, and logs returned errors. `getAccountID` uses reflection to avoid import cycles: it prefers OIDC `sub`, then `preferred_username`, then non-admin account IDs, identity-name context, `x-amz-account-id`, and finally handler default. Admin account IDs are kept only if identity actions include admin permission. Request bodies are bounded with `io.LimitReader` before JSON decode. Responses use AWS JSON content type.

## Dependencies and integration points
This file depends on `s3_constants` context helpers, `filer_pb`, HTTP, JSON, reflection, and permission/IAM helpers in the same package. It is the entry point called by the S3 API server for S3 Tables control-plane operations.

## Risks and edge cases
Principal extraction uses reflection over identity shapes, so field renames or type changes can silently break ownership. `normalizePrincipalID` collapses ARNs to suffixes and warns this is unsafe for future multi-account support. `defaultAllowFor` and IAM/legacy permission interplay live outside this file but are invoked by handlers dispatched here. `HandleRequest` logs errors after handlers may already have written responses.

## Test signals
`handler_identity_test.go` covers the most fragile identity-principal extraction and default-allow decisions. Other S3 Tables tests cover operation-specific flows.
