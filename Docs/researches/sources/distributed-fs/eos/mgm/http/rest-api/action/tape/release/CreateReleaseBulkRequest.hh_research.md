# sources/distributed-fs/eos/mgm/http/rest-api/action/tape/release/CreateReleaseBulkRequest.hh

## Purpose
`CreateReleaseBulkRequest.hh` declares the tape REST action for release requests that operate on a JSON list of paths.

## Important APIs, Types, and Functions
`CreateReleaseBulkRequest` derives from `TapeAction`. Its constructor injects URL, method, tape business service, and a `JsonModelBuilder<PathsModel>`. The class stores the builder and overrides `run()`.

## Control Flow
The registered action parses request JSON and delegates to `releasePaths()` in its implementation. It does not use URL parameters or output model serialization.

## State and Persistence Behavior
Only shared dependency pointers are stored. Persistent release effects are delegated to the tape business implementation.

## Dependencies and Integration Points
It includes `TapeAction`, `JsonModelBuilder`, and tape JSON headers. The file includes `TapeAction.hh` twice, which is harmless because of include guards but unnecessary.

## Risks
The duplicated include is low risk but signals header churn. Like other per-action headers, it must stay in sync with `TapeActions.hh` if both declaration styles remain. Constructor dependencies are unchecked.

## Test Signals
Compile tests should include this header with and without `TapeActions.hh`. Unit tests should mock the builder and business layer to validate `run()` behavior for success and validation failure.
