# sources/distributed-fs/eos/mgm/http/rest-api/action/tape/release/CreateReleaseBulkRequest.cc

## Purpose
`CreateReleaseBulkRequest.cc` implements the tape REST action that asks the tape business layer to release disk replicas for a JSON list of paths.

## Important APIs, Types, and Functions
`CreateReleaseBulkRequest::run()` parses the request body into `PathsModel`, calls `mTapeRestApiBusiness->releasePaths(paths.get(), vid)`, and returns an empty `200 OK` response on success. JSON validation errors produce `400 Bad Request`; tape business exceptions produce `500 Internal Error`.

## Control Flow
The action is a direct validate-call-respond adapter. No URL parameters are read and no response model is built because success is represented by an empty OK response.

## State and Persistence Behavior
The action itself has no persistence. Releasing paths may mutate file residency or tape-related state in the business/backend layer, but that is outside this HTTP adapter.

## Dependencies and Integration Points
It depends on `CreateReleaseBulkRequest.hh`, REST exceptions, `PathsModel`, `JsonModelBuilder`, `ITapeRestApiBusiness`, and `RestResponseFactory`. It maps the REST release endpoint to `releasePaths()`.

## Risks
All domain failures are collapsed to `500` except JSON validation. There is no explicit not-found or per-path partial-failure response at this layer. Null dependencies would fail at runtime.

## Test Signals
Tests should cover invalid JSON, successful release with identity forwarding, empty success response, business exception mapping, empty/missing path-list validation, and ensuring no output jsonifier is required.
