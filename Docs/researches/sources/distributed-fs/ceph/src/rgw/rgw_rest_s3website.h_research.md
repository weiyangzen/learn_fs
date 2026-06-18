# sources/distributed-fs/ceph/src/rgw/rgw_rest_s3website.h

## Purpose
`rgw_rest_s3website.h` declares the S3 static website REST dialect. It specializes S3 handlers so website endpoints serve objects, index documents, redirects, and custom error documents while disallowing mutating bucket/object APIs.

## Important APIs, Types, and Functions
`RGWHandler_REST_S3Website` derives from `RGWHandler_REST_S3`. It stores the original object name before retargeting, overrides `retarget()`, `op_get()`, `op_head()`, and `error_handler()`, and makes PUT/DELETE/POST/COPY/OPTIONS unsupported. `serve_errordoc()` serves configured error objects.

`RGWHandler_REST_Service_S3Website`, `RGWHandler_REST_Obj_S3Website`, and `RGWHandler_REST_Bucket_S3Website` all provide website-specific `get_obj_op()` behavior. The bucket handler deliberately derives through the website base rather than normal bucket operation semantics because website endpoints do not support bucket operations.

`RGWRESTMgr_S3Website` returns website handlers and is friend-accessed by `RGWRESTMgr_S3` for nested resource routing.

`RGWGetObj_ObjStore_S3Website` extends S3 GET. It can mark an error-document request, override data/error response behavior, ignore range and conditional headers for error pages, and change the canonical op name to `WEBSITE.<method>.OBJECT`.

## Control Flow
Website requests are routed to the website manager and initialized as S3-derived handlers. Only GET and HEAD produce operations. The handler can retarget a bucket or object request to an index object, error document, or original object depending on website configuration and request path.

When serving a configured error page, `RGWGetObj_ObjStore_S3Website::get_params()` clears range and conditional request members so the error object is fetched as an unconditional body while the status line can represent the original error.

## State and Persistence Behavior
The header persists no state. It reads bucket website configuration and object data through normal RGW bucket/object state. Per-request mutable state includes `original_object_name`, retargeted `s->object`, and `is_errordoc_request`.

## Dependencies and Integration Points
It depends on `rgw_rest_s3.h`, normal S3 object GET behavior, website configuration stored on buckets, RGW handler retargeting, and formatter/error handling. It is integrated as an optional manager under the S3 REST manager.

## Risks
Retargeting mutates request object state. Incorrect restoration or object-name handling can serve the wrong key or create bad redirects. Error-document fetches intentionally bypass conditional headers, so that behavior must stay limited to error-document requests.

## Test Signals
Coverage should include website GET/HEAD only, PUT/DELETE/POST rejection, index document routing, slash redirect behavior, custom error document serving with original status, missing error page fallback, conditional/range headers on normal versus error-page requests, and bucket/object path edge cases.
