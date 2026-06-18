# sources/distributed-fs/eos/mgm/http/rest-api/action/tape/archiveinfo/GetArchiveInfo.cc

## Purpose
`GetArchiveInfo.cc` implements the tape REST action that returns archive/tape information for a submitted list of paths.

## Important APIs, Types, and Functions
`GetArchiveInfo::run()` parses the request body into `PathsModel` using `mInputJsonModelBuilder`, calls `mTapeRestApiBusiness->getFileInfo(paths.get(), vid)`, wraps the resulting `bulk::QueryPrepareResponse` in `GetArchiveInfoResponseModel`, assigns `mOutputObjectJsonifier`, and returns an `OK` JSON response.

## Control Flow
The action first validates JSON. `JsonValidationException` becomes `400 Bad Request`. Business exceptions from `getFileInfo()` become `500 Internal Error`. On success, response-model creation and jsonification are delegated to the response factory.

## State and Persistence Behavior
The action does not persist state. It queries archive information through the tape business interface. Any backend reads or cache effects happen below `ITapeRestApiBusiness`.

## Dependencies and Integration Points
It depends on `GetArchiveInfo.hh`, REST exceptions, `GetArchiveInfoResponseModel`, `PathsModel`, `bulk::QueryPrepareResponse`, and `RestResponseFactory`. It integrates the HTTP REST layer with the tape prepare/query business path.

## Risks
Only `TapeRestApiBusinessException` is caught from the business call; other exceptions propagate through the REST handler. A null builder, business pointer, or jsonifier would fail at runtime. The action returns `500` for all business-layer failures, so client-visible error specificity is limited.

## Test Signals
Tests should cover malformed JSON, valid path lists, business success json output, business exception to `500`, empty path-list validation, virtual identity forwarding, and jsonifier invocation.
