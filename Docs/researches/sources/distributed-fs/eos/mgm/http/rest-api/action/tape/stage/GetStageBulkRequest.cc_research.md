# sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/GetStageBulkRequest.cc

## Purpose
`GetStageBulkRequest.cc` implements retrieval of a tape stage bulk request status/model by id.

## Important APIs, Types, and Functions
`GetStageBulkRequest::run()` extracts `{id}` from the URL with `URLParser`, calls `mTapeRestApiBusiness->getStageBulkRequest(requestId, vid)`, sets `mOutputObjectJsonifier` on the returned `GetStageBulkRequestResponseModel`, and returns an `OK` response. It maps `ObjectNotFoundException` to `404` and `TapeRestApiBusinessException` to `500`.

## Control Flow
The action has no request body. It resolves the route id, asks the business layer for a response model, attaches serialization behavior, and delegates HTTP response construction to `RestResponseFactory`.

## State and Persistence Behavior
The action is read-only at this layer. Persistent bulk-request state is read through the business implementation; no local cache is maintained.

## Dependencies and Integration Points
It depends on `GetStageBulkRequestResponseModel`, `URLParser`, `Constants.hh`, REST exceptions, `TapeRestApiJsonifier`, and `ITapeRestApiBusiness`. It connects the REST status endpoint to bulk-request state.

## Risks
Missing id extraction is not checked before map indexing. A null response model from the business layer would be dereferenced. The response model is responsible for serialization after `setJsonifier()`, so jsonifier misconfiguration breaks output late.

## Test Signals
Tests should cover successful retrieval, output JSON shape, not-found and generic failure mapping, missing id behavior, null response-model protection, identity forwarding, and jsonifier assignment.
