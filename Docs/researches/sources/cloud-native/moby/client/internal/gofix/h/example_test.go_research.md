# sources/cloud-native/moby/client/internal/gofix/h/example_test.go

## Purpose
`example_test.go` tests the Moby client behavior for example. These files are compile-only examples for Go fix directives rather than runtime daemon tests.

## Important APIs, Types, And Functions
Test functions: none exported; package documentation/example file. Referenced routes or paths: none.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
