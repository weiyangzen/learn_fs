# sources/cloud-native/moby/api/pkg/authconfig/authconfig_test.go

## Purpose
This test file defines the behavioral contract for `api/pkg/authconfig`. It is especially important because registry authentication crosses a public HTTP header boundary and must maintain compatibility with old Docker clients and daemons.

## Important APIs, types, and functions
`TestDecodeAuthConfig` is a table-driven test around `Decode`. Each row includes a plain JSON fixture, a base64 fixture, the expected `registry.AuthConfig`, and optionally exact error text. The test first sanity-checks that the base64 fixture matches the plain JSON, trimming padding only for rows meant to simulate unpadded input.

`TestEncodeAuthConfig` verifies `Encode` for the empty config and a populated username/password/serveraddress config. It checks both the encoded string and the decoded JSON bytes, making field tags and `omitempty` behavior visible in the contract.

`BenchmarkDecodeAuthConfig` measures decode allocation/runtime for empty, `{}`, valid auth, invalid base64, and malformed JSON inputs.

## Control flow
The decode test loops through cases with `t.Run(tc.doc, ...)`. If a row expects an error, it asserts the concrete `errInvalidParameter` type and exact error string. Otherwise it asserts nil error and value equality. The encode test recalculates each expected base64 string from `outPlain`, invokes `Encode`, then decodes the returned header to prove the payload JSON is exactly the expected object.

## State and persistence behavior
The tests are stateless and deterministic. They do not use external registries, files, environment variables, or network access. The benchmark reports allocations but does not persist benchmark outputs.

## Dependencies
The file uses standard `encoding/base64`, `strings`, and `testing`; `github.com/moby/moby/api/types/registry` for the auth struct; and `gotest.tools/v3/assert` plus `gotest.tools/v3/assert/cmp` for assertions.

## Integration points
The tests lock down behavior consumed by daemon routes and clients that use `X-Registry-Auth`. Exact error text matters because client-facing daemon errors can include these strings. The cases also align with API docs that say the header contains base64url encoded JSON.

## Risks and edge cases covered
Covered edge cases include empty headers, empty JSON, malformed JSON, multiple adjacent JSON objects, unpadded base64url, trailing whitespace, trailing non-JSON data, and the special empty-config encode behavior. The test intentionally confirms the current padded-base64 requirement. It also confirms that invalid decode returns an `errInvalidParameter`, which preserves HTTP bad-parameter classification.

## Gaps and test signals
There is no direct test for `DecodeRequestBody`, even though it delegates to `decode`; request-body-specific resource closing is not relevant because the implementation accepts an `io.Reader` through the helper and does not close it. There is no fuzzing for unusual JSON token streams, large payloads, or non-object JSON values. The existing tests are strong for known compatibility cases and regression-sensitive error messages.
