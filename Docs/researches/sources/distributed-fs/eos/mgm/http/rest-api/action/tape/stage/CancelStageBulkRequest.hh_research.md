# sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/CancelStageBulkRequest.hh

## Purpose
`CancelStageBulkRequest.hh` declares the tape REST action used to cancel paths from an existing stage bulk request.

## Important APIs, Types, and Functions
`CancelStageBulkRequest` derives from `TapeAction`. Its constructor injects URL, method, tape business service, and `JsonModelBuilder<PathsModel>`. It stores the builder and overrides `run()`.

## Control Flow
At runtime, the implementation parses path JSON, extracts the request id from the registered URL pattern, and delegates cancellation to the business layer.

## State and Persistence Behavior
Only action dependencies are stored. Bulk-request cancellation state is persisted by the business/backend implementation, not by the action.

## Dependencies and Integration Points
The header depends on `TapeAction`, `JsonModelBuilder`, `PathsModel`, and `TapeRestApiBusiness`/`ITapeRestApiBusiness` types. It is registered by the tape REST handler for cancel-stage endpoints.

## Risks
The header includes the concrete `TapeRestApiBusiness.hh` even though the constructor takes the interface pointer, increasing compile coupling. Null dependency handling is absent. It must remain declaration-compatible with `TapeActions.hh`.

## Test Signals
Compile tests should include this header independently. Unit tests should validate constructor dependency wiring and `run()` behavior with mocked JSON parsing and business cancellation.
