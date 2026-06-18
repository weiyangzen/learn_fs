# sources/distributed-fs/ceph/src/rgw/rgw_swift_auth.cc

## Purpose
`rgw_swift_auth.cc` implements Swift authentication engines and the legacy Swift auth endpoint. It supports TempURL HMAC authentication, external Swift auth URL validation, locally signed `AUTH_rgwtk` tokens, and token issuance from `X-Auth-User`/`X-Auth-Key`.

## Important APIs, Types, and Functions
`TempURLApplier` mutates content-disposition and marks log entries as temp-url. `TempURLEngine` loads bucket-owner temp URL keys, converts ISO8601 expirations, rejects expired URLs/disallowed headers, selects HMAC helper by signature form, supports prefixed temp URLs, and grants a temp-url applier on match. `ExternalTokenEngine` validates tokens by querying configured `rgw_swift_auth_url`. `build_token()` and `encode_token()` serialize swift user, nonce, expiration, and HMAC-SHA1. `SignedTokenEngine` decodes, verifies expiration and HMAC, loads the mapped user, and grants a local applier. `RGW_SWIFT_Auth_Get::execute()` issues Swift storage URL and auth tokens.

## Control Flow
The strategy invokes engines in order. TempURL requires query args, loads owner info from URL bucket/account context, checks each configured temp URL key against allowed methods and path variants, and returns grant/reject. Signed token strips `AUTH_rgwtk`, hex-decodes the payload, decodes fields, loads the Swift user, rebuilds the token with the user's Swift key, and compares bytes. External auth calls a remote token endpoint and maps the first returned auth group to a Swift user. The auth endpoint validates the supplied Swift key and emits headers.

## State and Persistence Behavior
No durable state is written except request logs. Issued signed tokens contain user, nonce, expiration, and HMAC in a hex payload. Authentication loads user/account/policy state through SAL and configures request-local appliers.

## Dependencies and Integration Points
The file depends on RGW auth strategy/applier classes, Keystone/external auth, SAL user lookup, account policy loading, RGW HTTP client header collection, HMAC-SHA implementations, base64 helpers, request env/args, and Swift URL config.

## Risks
TempURL path compatibility tries two path variants and special HEAD method fallbacks, so regressions are easy. Signature comparison length logic includes `dest_size + 1`, which relies on generated strings being null terminated. External auth throws on validator errors, so strategy behavior depends on caller exception handling. Legacy signed tokens use HMAC-SHA1. The auth endpoint uses `goto` cleanup and may expose misconfiguration through headers/logs.

## Test Signals
Cover TempURL SHA1/SHA256/SHA512 bare and named-base64 signatures, ISO8601 expires, expired and malformed expires, prefixed temp URLs, HEAD fallbacks, disallowed manifest header, tenant/account URL cases, external token header parsing, signed token tampering/expiration, missing Swift keys, and auth endpoint URL construction.
