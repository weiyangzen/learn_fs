# sources/distributed-fs/ceph/src/rgw/rgw_rest_sts.h

## Purpose
`rgw_rest_sts.h` declares the STS REST handler, STS operation classes, and web-identity authentication strategy used by RGW STS endpoints.

## Important APIs, Types, and Functions
`rgw::auth::sts::WebTokenEngine` derives from `rgw::auth::Engine` and declares helpers for OIDC provider loading, JWT claim extraction, signature validation, certificate/thumbprint validation, role parsing, and web identity applier creation.

`rgw::auth::sts::DefaultStrategy` combines a `TokenExtractor`, `WebIdentityApplier::Factory`, and `WebTokenEngine`. Its extractor reads `WebIdentityToken` from request args, and its applier factory wraps `WebIdentityApplier` with `add_sysreq()`.

`RGWREST_STS` is the common base for STS ops and owns an `STS::STSService` member. Derived ops are `RGWSTSAssumeRoleWithWebIdentity`, `RGWSTSAssumeRole`, `RGWSTSGetSessionToken`, and `RGWSTSGetCallerIdentity`.

`RGW_Auth_STS`, `RGWHandler_REST_STS`, and `RGWRESTMgr_STS` declare authorization, action routing, handler initialization, and manager integration.

## Control Flow
The manager always returns `RGWHandler_REST_STS`. The handler parses POST actions, checks whether the action exists, selects one of the operation classes, and chooses STS web-token auth only for `AssumeRoleWithWebIdentity`. All other actions reuse S3 authorization.

Operation classes use `get_params()`, `verify_permission()`, `execute()`, and `send_response()` from the RGW op lifecycle. `RGWREST_STS::verify_permission()` centralizes role trust-policy checks for assume-role variants.

## State and Persistence Behavior
The header declares request-local parameter storage for duration, role ARN/session name, provider id, web identity claims, external id, MFA fields, and inline session policy. Persistent state is accessed in the implementation through roles, OIDC providers, account info, and STS-issued credentials.

## Dependencies and Integration Points
It depends on RGW auth, auth filters, REST base classes, STS service definitions, web identity provider support, OIDC provider types, and `jwt-cpp`. The declared classes integrate STS into the RGW REST manager tree and auth strategy registry.

## Risks
The auth split between web identity and S3 credentials is action-name dependent. If new STS actions are added without updating routing and authorization selection, they may get the wrong auth mechanism or no operation.

The header exposes many private web-token helper declarations, indicating a large security-sensitive implementation surface. Changes must preserve token validation, provider lookup, and applier semantics together.

## Test Signals
Header-level compatibility is exercised by STS action dispatch tests, auth strategy registry construction, web identity applier creation, and build coverage for JWT/OpenSSL dependencies. Behavior tests belong with the `.cc` implementation.
