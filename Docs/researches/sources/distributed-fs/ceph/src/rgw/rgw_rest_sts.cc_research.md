# sources/distributed-fs/ceph/src/rgw/rgw_rest_sts.cc

## Purpose
`rgw_rest_sts.cc` implements Ceph RGW's STS REST API and web identity authentication engine. It handles OIDC/JWT validation for `AssumeRoleWithWebIdentity`, ordinary S3-authenticated STS actions, trust-policy evaluation, credential/session issuance, and STS XML responses.

## Important APIs, Types, and Functions
`rgw::auth::sts::WebTokenEngine` validates web identity tokens. It parses role ARN tenant/name, loads OIDC provider metadata, extracts token claims and principal tags, validates audience/client id, fetches OIDC discovery/JWKS data, verifies JWKS endpoint thumbprints, validates JWT signatures, loads the target role/account, and returns a `WebIdentityApplier`.

`get_cert_url()` retrieves `/.well-known/openid-configuration` and extracts `jwks_uri`. `verify_oidc_thumbprint()` optionally connects to the JWKS host, extracts the last TLS certificate in the chain, and compares its SHA1 thumbprint to registered provider thumbprints. `validate_signature()` supports RSA, ECDSA, and PSS algorithms with `x5c` certificates and bare RSA `n`/`e` JWKs; HMAC JWT algorithms are rejected.

`RGWREST_STS::verify_permission()` loads role info through `STS::STSService`, parses the role trust policy, optionally enforces `stsTagSession`, and evaluates either `stsAssumeRoleWithWebIdentity` or `stsAssumeRole` against the authenticated identity.

`RGWSTSGetSessionToken`, `RGWSTSAssumeRoleWithWebIdentity`, `RGWSTSAssumeRole`, and `RGWSTSGetCallerIdentity` parse STS action parameters, call `STS::STSService`, and write AWS-style XML response sections.

`RGW_Auth_STS::authorize()` applies the STS auth strategy. `RGWHandler_REST_STS` maps `Action` values to operation constructors and uses STS auth only for `AssumeRoleWithWebIdentity`; other actions use normal S3 auth. `RGWRESTMgr_STS` returns this handler.

## Control Flow
For `AssumeRoleWithWebIdentity`, the handler sees `Action=AssumeRoleWithWebIdentity` and authorizes with the STS strategy. `WebTokenEngine` extracts `WebIdentityToken`, decodes JWT claims, loads the OIDC provider based on issuer and role ARN tenant, validates client id/audience and signature, loads the role and optional account, then grants a web-identity applier. The op then validates parameters/trust policy and calls `sts.assumeRoleWithWebIdentity()`.

For `AssumeRole`, the handler authorizes with S3 credentials, builds an `STS::STSService`, validates role trust policy, parses duration/external id/policy/MFA fields, and calls `sts.assumeRole()`.

For `GetSessionToken`, permission is checked with `stsGetSessionToken` on an S3 ARN. The op validates optional duration bounds and calls `sts.getSessionToken()`.

For `GetCallerIdentity`, no permission is required. The op builds account, user id, and caller ARN from the authenticated identity and environment and returns them.

## State and Persistence Behavior
The file mostly reads persistent state and asks `STS::STSService` to create credentials. It reads OIDC provider records through `driver->load_oidc_provider()`, roles through `driver->get_role()->load_by_name()`, accounts through `driver->load_account_by_id()`, and role trust policies from role metadata.

Issued credentials and session token persistence are delegated to `STS::STSService` and related STS types. Request-local state includes extracted token claims, principal tags, `s->principal_tags`, role session name, policy strings, and XML formatter output.

Network-derived JWKS/OIDC data is not persisted here. It is fetched per validation path through `RGWHTTPTransceiver` and OpenSSL socket/TLS helpers.

## Dependencies and Integration Points
The implementation depends on OpenSSL, `jwt-cpp`, JSON parsing, RGW HTTP transceiver, OIDC provider storage, IAM policy parser/evaluator, STS service types, auth strategy registry, S3 auth for non-web-identity actions, SAL driver role/account/OIDC provider APIs, and RGW XML formatter helpers.

It integrates with IAM trust policies, role tags, principal tags, account-based role ARNs, web identity appliers, and frontend REST dispatch through `RGWRESTMgr_STS`.

## Risks
OIDC validation performs outbound HTTP and TLS connections in the request path and calls `maybe_warn_about_blocking()`. DNS, network latency, JWKS availability, and certificate-chain parsing can directly affect STS latency and reliability.

Thumbprint logic is configuration-sensitive. `rgw_enable_jwks_url_verification` changes whether JWKS endpoint certificate verification is enforced, and the local `skip_thumbprint_verification` variable naming in `validate_signature()` is easy to misread.

JWT claim recursion flattens nested objects and arrays into multimaps/sets. Collisions or unexpected claim types can affect IAM condition evaluation. HMAC JWT algorithms are explicitly unsupported.

Trust-policy evaluation is parsed at request time with a TODO noting that role creation could validate it earlier. Bad stored policies therefore fail at assumption time.

## Test Signals
Tests should cover missing/invalid tokens, issuer normalization, OIDC provider lookup by tenant/account role ARN, audience/client_id/azp matching, principal tags, expired JWTs, unsupported algorithms, x5c and bare RSA JWK validation, JWKS thumbprint enforcement toggles, broken discovery/JWKS JSON, missing roles/accounts, trust policy allow/deny, `stsTagSession`, malformed session policies, duration bounds, caller identity for account and tenant users, and unknown/missing `Action`.
