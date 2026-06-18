# sources/distributed-fs/ceph/src/rgw/rgw_rest_client.h

## Purpose

`rgw_rest_client.h` declares the outbound RGW REST client abstraction. It exposes simple buffered requests, signed REST forwarding, streaming read/write requests, S3 object upload helpers, and header generation used by remote RGW connections.

## Important APIs and Types

`RGWHTTPSimpleRequest` extends `RGWHTTPClient` with HTTP status tracking, captured response headers, query parameters, optional request body iteration, bounded buffered response storage, and overrides for header/body callbacks. `RGWRESTSimpleRequest` adds an optional API name and `forward_request()` for forwarding an existing `req_info`.

`RGWRESTGenerateHTTPHeaders` is a `DoutPrefix` helper that initializes signing state and applies extra headers, RGW object attrs, HTTP attrs, ACL policy grants, and final S3 auth signatures. `RGWHTTPStreamRWRequest` adds receive callbacks, write-drain callbacks, streamed input/output buffers, pause flags, and `complete_request()` metadata extraction. `RGWRESTStreamRWRequest` wraps streaming HTTP requests with signed RGW REST URL preparation. The concrete read/head/send subclasses select HTTP methods. `RGWRESTStreamS3PutObj` specializes streaming PUT for S3 objects and object-iteration callbacks.

## Control Flow

Callers build one of the request classes, configure params and headers, and either call the simple `forward_request()` path or the streaming `send_prepare()` then `send()` path. Completion flows through `wait()` in the base HTTP layer and then file-specific extraction in `complete_request()`.

The streaming types separate URL/signing preparation from actual submission so callers can enqueue requests in an `RGWHTTPManager`, attach callbacks, and provide body chunks asynchronously through `add_send_data()` and `finish_write()`.

## State and Persistence Behavior

Objects declared here hold transient network state only: headers, buffers, offsets, callbacks, signing context, and host style. `RGWRESTStreamS3PutObj` owns and deletes its `RGWGetDataCB` callback. No class persists data locally; persistence occurs through the remote HTTP operation represented by the request.

## Dependencies and Integration Points

The declarations depend on `rgw_http_client.h`, Ceph `expected`, bufferlists, `req_info`, `RGWEnv`, ACL policy types, and `RGWHTTPManager`. They are integrated by `rgw_rest_conn.h/.cc`, multisite sync, admin forwarding, and S3 object transfer paths.

## Risks and Test Signals

The main API risks are lifecycle and ordering: streaming requests must be prepared before sending, callbacks must outlive request processing, and callers must not use deleted `RGWRESTStreamS3PutObj` pointers after `complete_request()`. Tests should compile all call sites, verify callback delivery, cover both `PathStyle` and `VirtualStyle`, and assert that `complete_request()` populates requested ETag, mtime, size, attrs, and headers.
