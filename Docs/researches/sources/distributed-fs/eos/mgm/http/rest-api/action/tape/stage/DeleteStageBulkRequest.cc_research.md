# sources/distributed-fs/eos/mgm/http/rest-api/action/tape/stage/DeleteStageBulkRequest.cc

## Purpose
`DeleteStageBulkRequest.cc` implements deletion of an existing tape stage bulk request identified by the URL `{id}` parameter.

## Important APIs, Types, and Functions
`DeleteStageBulkRequest::run()` constructs a `URLParser` from the request URL, extracts `URLPARAM_ID` from `mAccessURLPattern`, and calls `mTapeRestApiBusiness->deleteStageBulkRequest(requestId, vid)`. `ObjectNotFoundException` maps to `404`; `TapeRestApiBusinessException` maps to `500`; success returns an empty `200 OK`.

## Control Flow
No request body is parsed. The URL id is extracted, the business layer deletes the request, and the response factory converts the result into HTTP status.

## State and Persistence Behavior
Persistent deletion happens in the tape bulk-request business/backend layer. This action stores no request state and does not directly modify files or namespace metadata.

## Dependencies and Integration Points
It depends on `URLParser`, `Constants.hh`, REST exceptions, and the tape business interface. It integrates the REST route for deleting or forgetting stage bulk requests with backend state cleanup.

## Risks
The action does not verify that URL parsing matched before indexing `requestParameters[URLPARAM_ID]`. It returns `200 OK` instead of `204 No Content`, which may be an intentional API contract but should be documented. Unexpected exceptions propagate.

## Test Signals
Tests should cover successful delete, not-found mapping, generic business failure, missing or malformed id routes, identity forwarding, and response status/body expectations.
