# sources/distributed-fs/eos/mgm/http/rest-api/action/tape/TapeAction.hh

## Purpose
`TapeAction.hh` declares the abstract base for tape-specific REST actions. It adds access to the tape business interface and common REST response factory on top of the generic `Action` contract.

## Important APIs, Types, and Functions
`TapeAction` derives from `Action`. Its constructor accepts an access URL pattern, HTTP method, and `shared_ptr<ITapeRestApiBusiness>`. It keeps `mTapeRestApiBusiness` and a `RestResponseFactory` member for concrete actions. `run()` remains pure virtual.

## Control Flow
Concrete tape actions receive parsed HTTP requests from the tape REST handler. They validate JSON or URL parameters, invoke `mTapeRestApiBusiness`, and use `mResponseFactory` to create protocol responses.

## State and Persistence Behavior
`TapeAction` itself stores shared business-service ownership and response-factory state. Persistent tape request state is created, queried, canceled, or deleted by the business layer, not this base class.

## Dependencies and Integration Points
The header depends on `Action`, `ITapeRestApiBusiness`, `RestResponseFactory`, and tape REST configuration. It is the common parent for stage, release, and archive-info action classes.

## Risks
The business pointer is not checked for null in the constructor. All concrete actions assume it and their JSON builders/jsonifiers are valid. Shared ownership can hide lifecycle cycles if handlers/business objects retain actions.

## Test Signals
Tests should instantiate simple derived actions with mock `ITapeRestApiBusiness`, verify method/pattern inheritance, and validate consistent error response construction through `RestResponseFactory`.
