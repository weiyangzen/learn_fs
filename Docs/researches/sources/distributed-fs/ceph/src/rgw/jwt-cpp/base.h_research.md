# sources/distributed-fs/ceph/src/rgw/jwt-cpp/base.h

## Purpose
Provides a small header-only base64/base64url encoder and decoder used by the embedded `jwt-cpp` code. It defines alphabets and templated public encode/decode entry points over a common implementation.

## Important APIs, types, and functions
- `jwt::alphabet::base64` exposes the standard `A-Z a-z 0-9 + /` alphabet and `=` fill string.
- `jwt::alphabet::base64url` exposes the URL-safe `A-Z a-z 0-9 - _` alphabet and `%3d` fill string.
- `jwt::base::encode<T>()` encodes binary strings with alphabet `T`.
- `jwt::base::decode<T>()` decodes strings with alphabet `T` and validates padding.

## Control flow
Encoding processes complete 3-byte groups into four sextets, then handles 1- or 2-byte tails by emitting fill strings. Decoding strips up to two trailing fill strings, validates total group length, decodes complete 4-character groups with a linear alphabet lookup, and handles the final padded group according to fill count.

## State and persistence behavior
No persistent state exists. Alphabet arrays and fill strings are function-local statics shared for the process lifetime.

## Dependencies and integration points
Depends only on `<string>` and `<array>` in this file, but throws `std::runtime_error` without including `<stdexcept>` locally, so inclusion may rely on transitive headers. Used by JWT token encoding/decoding paths in RGW.

## Risks and edge cases
`base64url::fill()` uses the percent-encoded string `%3d` rather than raw `=`, so interoperability depends on callers expecting URL-encoded padding. Decoder rejects more than two fill strings and invalid lengths. Alphabet lookup is O(64) per character. Decode output size reserve does not include padded tail bytes, but string growth handles it. Missing `<stdexcept>` is a compile fragility if transitive includes change.

## Test signals
Tests should cover RFC base64 vectors, base64url vectors with `%3d` padding, invalid characters, invalid length, excessive fill, empty string, 1- and 2-byte tails, binary bytes with high bits set, and compile isolation of this header.
