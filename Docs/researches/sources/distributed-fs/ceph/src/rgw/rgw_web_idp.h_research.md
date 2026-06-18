# sources/distributed-fs/ceph/src/rgw/rgw_web_idp.h

## Purpose
`rgw_web_idp.h` declares a small claim container for web identity provider tokens.

## Important APIs, Types, and Functions
`rgw::web_idp::WebTokenClaims` stores subject, audience, issuer, username, client id, and authorized party (`azp`).

## Control Flow
No functions are defined; callers populate the struct after decoding a web identity token and pass claims to STS/auth logic.

## State and Persistence Behavior
The struct is transient request state and has no encoding or persistence behavior in this file.

## Dependencies and Integration Points
Used by STS AssumeRoleWithWebIdentity and web identity token validation code. It intentionally has minimal dependencies.

## Risks
No validation is encoded in the type, so callers must validate required claims, audience matching, and issuer trust externally.

## Test Signals
Integration tests should verify decoded claims are correctly propagated into STS session token claims and trust-policy evaluation.
