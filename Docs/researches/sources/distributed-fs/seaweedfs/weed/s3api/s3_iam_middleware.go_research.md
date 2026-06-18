# sources/distributed-fs/seaweedfs/weed/s3api/s3_iam_middleware.go

## Purpose
`s3_iam_middleware.go` connects the SeaweedFS S3 API to the newer IAM/STS/OIDC stack. It authenticates bearer JWTs, converts validated STS or external OIDC identities into S3 `IAMIdentity` values, extracts request context for policy conditions, and sends authorization checks to `integration.IAMManager`.

## Important APIs, Types, and Functions
Important types are `IAMIntegration`, `IAMManagerProvider`, `S3IAMIntegration`, `IAMIdentity`, and `OIDCIdentity`. `NewS3IAMIntegration` wires an `IAMManager` and its STS service. `AuthenticateJWT` validates bearer tokens, `AuthorizeAction` builds an `integration.ActionRequest`, `ValidateSessionToken` and `ValidateTrustPolicyForPrincipal` delegate to IAM services, and `DefaultAllow` exposes IAM's default behavior.

Key helpers are `buildS3ResourceArn`, `extractRequestContext`, `extractSourceIP`, `isPrivateIP`, `ParseUnverifiedJWTToken`, `validateExternalOIDCToken`, `selectPrimaryRole`, and `isSTSIssuer`. `SetIAMIntegration` attaches the integration to `S3ApiServer`.

## Control Flow
`AuthenticateJWT` rejects disabled IAM, missing bearer headers, empty tokens, and obvious invalid token strings. It parses the JWT without verifying it only to read `iss`; exact issuer matching via `isSTSIssuer` routes STS tokens to `stsService.ValidateSessionToken`, while other issuers are validated through `ValidateWebIdentityToken` with a timeout. STS identities are built from trusted `SessionInfo`; OIDC identities are built from validated provider output and copied attributes, with `sub`, `role`, email, display name, and groups populated for policy variable use.

`AuthorizeAction` rejects missing principals, extracts policy condition context, special-cases list operations by setting `s3:prefix` and bucket-level resource ARNs, adds identity claims and `jwt:` aliases without overwriting request-derived keys, resolves the concrete S3 action, and asks `IAMManager.IsActionAllowed`.

## State and Persistence Behavior
This file keeps only process memory state: the integration holds `iamManager`, `stsService`, filer address, and enabled flag. Private network CIDRs are initialized once in `privateNetworks`. No on-disk state is written here; identity claims and request context exist only for an authorization decision.

## Dependencies and Integration Points
The file depends on `github.com/golang-jwt/jwt/v5`, SeaweedFS IAM integration, OIDC provider identity types, STS session validation, S3 action/error constants, and HTTP request state. It integrates with `IdentityAccessManagement.authenticateJWTWithIAM` and `authorizeWithIAM`, with `ResolveS3Action`, and with IAM policy evaluation.

## Risks and Edge Cases
The unverified JWT parse is intentionally used only for routing, but any future use of those claims for authorization would be a security regression. `extractSourceIP` trusts forwarding headers only from private or local `RemoteAddr`; deployments using public CDN/proxy addresses need external controls because there is no configurable trusted proxy CIDR list here. OIDC role selection simply chooses the first role returned by the provider, so provider ordering becomes security-critical. `requestTime` may be nil unless upstream middleware sets it. `AuthorizeAction` compares `action == "List"` instead of using a typed constant, so action naming changes can break list-prefix semantics.

## Test Signals
Related tests cover exact STS issuer matching, first-role selection, JWT auth/authorization flows, invalid token handling, request context extraction, and IP-based policy enforcement. High-value additions would cover list-prefix IAM conditions, `jwt:` claim alias precedence, public-proxy header spoofing, and OIDC identities without roles.
