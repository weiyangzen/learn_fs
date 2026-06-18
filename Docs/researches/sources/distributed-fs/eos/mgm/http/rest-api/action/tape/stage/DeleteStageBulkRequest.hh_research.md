# sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/DeleteStageBulkRequest.hh

## Purpose
`DeleteStageBulkRequest.hh` declares the tape REST action for deleting a stage bulk request by id.

## Important APIs, Types, and Functions
`DeleteStageBulkRequest` derives from `TapeAction`. Its constructor injects access URL, method, and tape business service, then forwards them to the base. It overrides `run()` and stores no additional members.

## Control Flow
The concrete implementation extracts the request id from the URL and delegates deletion to the business layer. The header only provides the type contract for registration and dispatch.

## State and Persistence Behavior
No additional state is stored beyond the base `TapeAction` members. Backend persistence is handled by `deleteStageBulkRequest()`.

## Dependencies and Integration Points
It includes `TapeAction.hh` and MGM namespace macros. It is registered by the tape REST handler for delete-stage endpoints and overlaps with the declaration in `TapeActions.hh`.

## Risks
Duplicate declarations between this header and `TapeActions.hh` must stay identical. The class has no builder/jsonifier dependencies, so route setup mistakes may only appear at runtime through URL parsing.

## Test Signals
Compile tests should include both declaration paths. Unit tests should instantiate the action with a mock business service and verify deletion status mapping through `run()`.
