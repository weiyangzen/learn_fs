# sources/cloud-native/moby/integration/system/api_test.go

## Purpose
Checks that the daemon returns a JSON API error response for an unmatched route when the client requests JSON.

## Important APIs, Types, And Functions
- `TestAPIErrorNotFoundJSON` performs `GET /notfound` with `request.JSON`, reads into `common.ErrorResponse`, and checks the error text.

## Control Flow
The test gets a setup context, sends a raw request, asserts HTTP 404, then decodes the response through `request.ReadJSONResponse`.

## State And Persistence
No daemon state changes are made.

## Dependencies And Integration Points
Touches the API router's 404 path, JSON error encoding, `common.ErrorResponse`, and request test helpers.

## Risks And Edge Cases
404 uses a different error path from normal handler errors, so this test is deliberately narrow. It depends on exact `page not found` error text.

## Test Signals
Passing means the not-found path emits status 404 and a JSON error object whose error string is `page not found`.
