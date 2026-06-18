# sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/CreateStageBulkRequest.cc

## Purpose
`CreateStageBulkRequest.cc` implements creation of a tape stage bulk request from a JSON request body and returns a response containing the new request id and `Location` URL.

## Important APIs, Types, and Functions
`CreateStageBulkRequest::run()` builds a `CreateStageBulkRequestModel`, calls `mTapeRestApiBusiness->createStageBulkRequest(model.get(), vid)`, constructs `CreatedStageBulkRequestResponseModel` from `bulkRequest->getId()`, assigns `mOutputObjectJsonifier`, and returns a `201 Created` response with a `Location` header. `generateAccessURL()` uses `mTapeRestHandler->getAccessURLBuilder()->add(getAccessURLPattern())->add(bulkRequestId)->build()`.

## Control Flow
The action validates JSON, delegates creation, builds response metadata, and returns. JSON validation errors become `400`; tape business exceptions become `500`. Successful control flow depends on the business layer returning a non-null `bulk::BulkRequest`.

## State and Persistence Behavior
The action persists nothing directly. Stage bulk request creation and any MGM bulk-request records are performed by `ITapeRestApiBusiness`. The action exposes the persistent request id through the response body and `Location` header.

## Dependencies and Integration Points
It depends on `BulkRequest`, tape models/jsonifiers, `TapeRestHandler` URL building, REST exceptions, and the global MGM headers included for broader context. It is the REST entry point for staging files from tape back to disk.

## Risks
`mTapeRestHandler` and returned access URL builder are assumed non-null. The generated URL concatenates the action pattern and id; pattern semantics must match router expectations. All business failures map to `500`, and unexpected exceptions are not caught. The implementation includes several headers that appear unused, increasing compile coupling.

## Test Signals
Tests should cover invalid JSON, business failure, successful request id propagation, `201` status, `Location` header construction, jsonifier use, identity forwarding, and null/empty bulk request id handling.
