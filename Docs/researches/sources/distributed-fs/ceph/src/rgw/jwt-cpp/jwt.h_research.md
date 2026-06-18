# sources/distributed-fs/ceph/src/rgw/jwt-cpp/jwt.h

## Purpose
This header is Ceph RGW's vendored, header-only JWT implementation. It decodes, builds, signs, and verifies JSON Web Tokens using picojson for JSON, a local base64url helper, and OpenSSL for HMAC, RSA, ECDSA, and RSA-PSS algorithms. It is a security-sensitive dependency for RGW code paths that accept or issue JWT-like credentials.

## Important APIs, types, and functions
- Exception types: `signature_verification_exception`, `signature_generation_exception`, `rsa_exception`, `ecdsa_exception`, and `token_verification_exception` distinguish crypto setup, signing, and verification failures.
- `helper::extract_pubkey_from_cert()`, `load_public_key_from_string()`, and `load_private_key_from_string()` wrap PEM/certificate BIO handling and produce OpenSSL key objects.
- `jwt::algorithm` provides `none`, `hmacsha` with `hs256/hs384/hs512`, `rsa` with `rs256/rs384/rs512`, `ecdsa` with `es256/es384/es512`, and `pss` with `ps256/ps384/ps512`.
- `jwt::claim` wraps `picojson::value` and exposes typed conversion to string, int64 date, bool, double, array, object, and string set.
- `jwt::payload`, `jwt::header`, and `jwt::decoded_jwt` expose standard JWT claims and raw base64/decoded token parts.
- `jwt::builder` builds JSON header/payload maps and signs compact JWT strings.
- `jwt::verifier<Clock>` verifies the declared algorithm, signature, registered claims, audience membership, and time claims.

## Control flow
`decoded_jwt` splits the token on two dots, pads each base64url segment, decodes header/payload/signature, parses header and payload as JSON objects, and stores claims in unordered maps. `builder::sign()` constructs JSON objects, injects `alg`, serializes via picojson, base64url encodes without padding, signs `header.payload`, and appends the encoded signature. `verifier::verify()` reconstructs the signed data, selects an explicitly allowed algorithm by header `alg`, verifies the signature, checks exp/iat/nbf against the injected clock and leeway, then checks required claims and audience.

## State and persistence behavior
The header has no durable persistence. Runtime state is held in token strings, claim maps, OpenSSL key handles, and verifier allowed-algorithm maps. Crypto key material is copied into strings and OpenSSL objects for the lifetime of algorithm instances.

## Dependencies and integration points
The file depends on Ceph's vendored `picojson/picojson.h`, `base.h`, `rgw/rgw_b64.h`, STL containers/chrono, and OpenSSL EVP/HMAC/PEM/EC/RSA/BIGNUM APIs. It includes compatibility branches for OpenSSL 1.0 style context and ECDSA accessors. RGW integrations should construct a verifier with only expected algorithms; algorithm confusion protection depends on the caller configuring `allow_algorithm()`.

## Risks and edge cases
- `algorithm::none` is available; accepting it is safe only if callers never allow it for untrusted tokens.
- RSA JWK modulus/exponent support builds an `EVP_PKEY` from base64url strings; padding and malformed input need targeted tests.
- HMAC comparison avoids early exit but is not a dedicated constant-time primitive.
- ECDSA verification assumes the compact `r || s` signature format and does not explicitly reject odd or unexpected signature lengths before splitting.
- Leeway setters encode seconds as dates in `claims`; the verify path converts those dates back to seconds. This works by convention but is easy to misuse if claims are inspected as real expected time claims.
- `parse_claims()` assumes parsed JSON is an object before iterating `val.get<picojson::object>()`.

## Test signals
Useful tests should cover valid and invalid HS/RS/ES/PS tokens, wrong algorithm rejection, tampered signature rejection, PEM and certificate key loading, JWK modulus/exponent RSA verification, exp/iat/nbf leeway boundaries with a fake clock, string and array audience forms, malformed compact-token structure, invalid base64url, non-object JSON, and explicit rejection of `none` unless intentionally allowed.
