# sources/distributed-fs/ceph/src/rgw/rgw_rest_conn.h

## Purpose

`rgw_rest_conn.h` declares the high-level RGW REST connection facade used to talk to remote RGW endpoints. It also defines JSON decode helpers, param-list helpers, streaming receive-to-buffer callbacks, and refcounted resource wrappers for remote resource reads and writes.

## Important APIs and Types

`parse_decode_json()` parses a `bufferlist` into a `JSONParser` and decodes it into a caller-provided object. `rgw_http_param_pair`, `append_param_list()`, and `make_param_list()` convert C-style null-terminated param arrays or maps into `param_vec_t`.

`RGWRESTConn` owns endpoint configuration, credentials, zone identity, API name, host style, and endpoint health. Public methods cover request forwarding, IAM forwarding, S3 object PUT/GET, generic resource send/get, and JSON resource fetches. `get_obj_params` centralizes optional object-transfer flags. `S3RESTConn` is a base-connection variant that suppresses RGW sys-param injection.

`RGWRESTReadResource` and `RGWRESTSendResource` are `RefCountedObject`/`RGWIOProvider` wrappers around stream requests. `RGWRESTPostResource`, `RGWRESTPutResource`, and `RGWRESTDeleteResource` select write methods.

## Control Flow

Callers create a connection from zone endpoints and credentials, then either use one-shot helpers or instantiate resource wrappers. Template helpers fetch raw data, call `parse_decode_json()`, and return typed results. Asynchronous flows call `aio_read()` or `aio_send()` and later `wait()`.

## State and Persistence Behavior

The header exposes in-memory connection state only. Endpoint status is an unordered map of atomics recording when endpoints became unconnectable. Resource wrappers hold one request, one receive callback, request params/headers, and accumulated response buffer. Persistent effects are remote and depend on the HTTP operation.

## Dependencies and Integration Points

This header depends on `rgw_rest_client.h`, Ceph JSON utilities, refcounting, SAL forward declarations, and `RGWHTTPManager`. It is included by multisite and admin code that needs remote RGW communication. The `RGWIOProvider` methods allow these requests to participate in RGW I/O accounting.

## Risks and Test Signals

Template JSON decode errors collapse to `-EINVAL`, so callers lose detailed parse diagnostics. The C-style `rgw_http_param_pair` lists require null termination. Resource wrappers contain request objects initialized from `conn->get_url()`, so construction with no valid endpoint can produce weak diagnostics. Compile-time tests should instantiate all templates used by callers; runtime tests should cover raw and typed waits, async send/read, IO provider ids, and endpoint error handling.
