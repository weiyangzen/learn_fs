# sources/distributed-fs/ceph/src/rgw/rgw_os_lib.cc

## Purpose
`rgw_os_lib.cc` implements lib-rgw request target parsing for `RGWHandler_Lib`. It maps a library frontend request URI into `req_state` bucket and object fields without the normal HTTP frontend assumptions.

## Important APIs, Types, And Functions
The only function is `rgw::RGWHandler_Lib::init_from_header(rgw::sal::Driver* driver, req_state* s)`. It parses `s->relative_uri`, initializes `s->info.args`, assigns `s->bucket_name`, `s->object_key.name`, `s->object_key.instance`, and creates `s->object` through `driver->get_object()`.

## Control Flow
The function treats leading `?` as a request-parameter-only URI, otherwise uses `s->info.request_params`; it parses args, strips a leading slash, derives the first path segment as bucket when no bucket is already set, and treats the remainder or full path as the object key. It also reads the `versionId` query arg into the object key instance.

## State And Persistence
It mutates only request-local `req_state`. No persistent bucket or object metadata is written. The object pointer is a SAL handle, not a read of object data.

## Dependencies And Integration Points
It depends on `rgw_rest*`, `rgw_file_int.h`, `rgw_lib_frontend.h`, and SAL driver object creation. It is specific to the RGW library/file frontend, where requests may not arrive as normal HTTP path-style or virtual-hosted S3 requests.

## Risks And Test Signals
Risks include ambiguous parsing for empty paths, paths without a leading slash, request params embedded in `relative_uri`, and version-id propagation. Tests should cover bucket-only, bucket/object, preselected bucket plus object path, query-only paths, versioned object access, and paths with nested object keys.
