# sources/distributed-fs/eos/mgm/http/rest-api/action/tape/archiveinfo/GetArchiveInfo.hh

## Purpose
`GetArchiveInfo.hh` declares the tape REST action for archive information queries over a JSON path list.

## Important APIs, Types, and Functions
`GetArchiveInfo` derives from `TapeAction`. Its constructor injects access URL, method, tape business service, `JsonModelBuilder<PathsModel>`, and `TapeRestApiJsonifier<GetArchiveInfoResponseModel>`. `run()` is overridden in the `.cc` file. The class stores the input builder and output jsonifier as shared pointers.

## Control Flow
The tape REST handler registers this action for its route. At runtime, `run()` builds `PathsModel`, queries business state, and serializes a response model.

## State and Persistence Behavior
The header defines dependency state only. It does not own request or archive metadata. Persistent archive state is queried through the business dependency.

## Dependencies and Integration Points
It includes `TapeAction`, `JsonModelBuilder`, `TapeRestApiJsonifier`, and `GetArchiveInfoResponseModel`. `PathsModel` is referenced as the expected input model through included tape action/model headers.

## Risks
Dependency pointers are assumed valid. This per-action declaration overlaps with the consolidated `TapeActions.hh` declaration, so duplicate declarations must remain structurally identical.

## Test Signals
Compile tests should include this header alone and alongside `TapeActions.hh`. Unit tests should inject mock builders/jsonifiers/business services and verify constructor wiring through `run()`.
