# sources/cloud-native/moby/daemon/server/httputils/httputils_test.go

## Purpose
Tests content-type validation and JSON request decoding helpers.

## Important APIs, Types, And Functions
Tests directly call `matchesContentType` and `ReadJSON`.

## Control Flow
Content-type tests verify exact JSON, charset parameters, unsupported media type error text, and malformed header error text. JSON tests verify nil body, empty body, valid JSON, whitespace around JSON, extra content rejection, and invalid JSON error wrapping.

## State And Persistence
Each test constructs local `http.Request` objects with string readers. `ReadJSON` closes request bodies but no external state is affected.

## Dependencies And Integration Points
Uses Go HTTP and testing packages. It protects behavior used by all JSON-reading API handlers.

## Risks And Edge Cases
Tests assert exact error strings, so intentional wording changes require test updates. They do not cover multiple valid JSON top-level documents outside the object-plus-extra pattern.

## Test Signals
Failures indicate request content validation or JSON error classification changed.
