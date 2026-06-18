# sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/GetStageBulkRequest.hh

## Purpose
`GetStageBulkRequest.hh` declares the tape REST action that returns status/details for a stage bulk request.

## Important APIs, Types, and Functions
`GetStageBulkRequest` derives from `TapeAction`. Its constructor injects URL, method, tape business service, and `TapeRestApiJsonifier<GetStageBulkRequestResponseModel>`. It stores the jsonifier and overrides `run()`.

## Control Flow
The handler dispatches matched GET requests to `run()`, which extracts a request id, fetches the response model, and serializes it.

## State and Persistence Behavior
Only dependency pointers are stored. Stage bulk request state is read from backend services through the business layer.

## Dependencies and Integration Points
The header depends on `TapeAction`, `TapeRestApiJsonifier`, and `GetStageBulkRequestResponseModel`. It is part of the tape REST action registration surface and mirrors a declaration in `TapeActions.hh`.

## Risks
The constructor parameter formatting is tight but valid; more importantly, duplicate declarations must stay synchronized. Null jsonifier/business dependencies are not guarded.

## Test Signals
Compile tests should include this header alone and with `TapeActions.hh`. Unit tests should mock the business response model and ensure `run()` sets the jsonifier before response creation.
