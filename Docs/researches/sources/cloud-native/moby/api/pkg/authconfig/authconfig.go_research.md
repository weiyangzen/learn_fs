# sources/cloud-native/moby/api/pkg/authconfig/authconfig.go

## Purpose
This Go package is a small API-boundary utility for serializing and parsing registry authentication data used in the Docker/Moby HTTP API. It converts `registry.AuthConfig` values to and from the base64url JSON representation carried in the `X-Registry-Auth` header, and it keeps compatibility behavior for older request-body based auth payloads.

## Important APIs, types, and functions
`Encode(authConfig registry.AuthConfig) (string, error)` marshals the struct to JSON and encodes it with `base64.URLEncoding`, which is the RFC4648 section 5 alphabet with padding. It wraps marshal failures as `errInvalidParameter`, although the current `registry.AuthConfig` field set is simple strings and unlikely to fail.

`Decode(authEncoded string) (*registry.AuthConfig, error)` accepts the header string. It returns an empty `AuthConfig` and no error for an empty header, returns empty config and no error for the literal decoded JSON object `{}`, validates that the input is padded base64url, and then delegates JSON parsing to `decode`.

`DecodeRequestBody(r io.ReadCloser) (*registry.AuthConfig, error)` preserves older API behavior where registry auth could be sent as a JSON request body. It delegates to the same JSON parser without first base64-decoding.

`decode(r io.Reader)` owns JSON decoding and rejects malformed JSON and extra JSON documents. `invalid` standardizes error text as `invalid X-Registry-Auth header: ...`. `errInvalidParameter` embeds an error and implements `InvalidParameter()`, `Cause()`, and `Unwrap()`, making the error usable both by older Docker error handling and modern `errors` unwrapping.

## Control flow
Encoding is linear: JSON marshal, wrap any error, base64url encode, return. Decoding first handles the empty string compatibility path, base64-decodes the header, converts base64 corruption into a stable user-facing validation error, special-cases decoded `{}`, then JSON-decodes into `registry.AuthConfig`. The JSON decoder reads the first document and uses `dec.More()` to reject a second top-level JSON value or trailing non-whitespace garbage.

## State and persistence behavior
The file is stateless. It allocates transient byte buffers and `registry.AuthConfig` values only. It does not persist credentials, cache decoded auth, or mutate global package state. The most important state effect is indirect: it shapes how registry credentials cross daemon/client HTTP boundaries.

## Dependencies
It depends on standard `bytes`, `encoding/base64`, `encoding/json`, `errors`, `fmt`, and `io`, plus `github.com/moby/moby/api/types/registry` for the public auth struct. It uses padded `base64.URLEncoding`, not `RawURLEncoding`, which is a compatibility-sensitive choice tested by `authconfig_test.go`.

## Integration points
Call sites include image, plugin, distribution, swarm, and system routes that read `registry.AuthHeader` or legacy bodies. The related `api/types/registry/authconfig.go` file defines `AuthHeader = "X-Registry-Auth"` and the `AuthConfig` fields. API swagger docs mention the header on push, pull, build, plugin, and swarm image paths. Error wrapping through `InvalidParameter()` integrates with daemon HTTP error classification.

## Risks and edge cases
The function always returns a non-nil `AuthConfig` pointer even on errors, so callers that ignore errors may silently continue with an empty auth configuration. Several daemon routes intentionally ignore decode errors, which is compatible but can make malformed auth indistinguishable from anonymous auth. The base64 decoder requires padding, so clients sending unpadded base64url will be rejected. The `dec.More()` extra-document check works for the tested top-level object cases, but future changes should be cautious because `More` is most commonly used inside arrays or objects; tests currently cover trailing invalid data and adjacent `{}` documents.

## Test signals
`authconfig_test.go` verifies empty input, `{}`, malformed JSON, a populated config, multiple JSON documents, unpadded base64 rejection, trailing whitespace acceptance, trailing garbage rejection, and encode output. The benchmark exercises empty, valid, invalid base64, and malformed JSON paths. No integration test is in this file, but repository call sites and swagger docs provide API-level coverage signals.
