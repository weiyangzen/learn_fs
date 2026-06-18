# sources/distributed-fs/ceph/src/rgw/rgw_cr_rest.h

## Purpose
Declares coroutine wrappers for REST read, write, delete, and bidirectional streaming operations used by RGW cloud/remote resource flows.

## Important APIs, types, and functions
`rgw_rest_obj` carries object key, length, attrs, custom attrs, and ACLs. `RGWReadRawRESTResourceCR` and `RGWReadRESTResourceCR<T>` wrap async HTTP GET/read operations. `RGWSendRawRESTResourceCR<T,E>`, `RGWSendRESTResourceCR<S,T,E>`, `RGWPostRESTResourceCR`, `RGWPutRESTResourceCR`, `RGWPutRawRESTResourceCR`, `RGWPostRawRESTResourceCR`, and `RGWDeleteRESTResourceCR` wrap send verbs. `RGWStreamReadResourceCRF` and `RGWStreamWriteResourceCRF` define streaming interfaces, with HTTP implementations and `RGWStreamSpliceCR`.

## Control flow
Simple coroutine classes create an HTTP operation in `send_request()`, wait in `request_complete()`, and release intrusive references in cleanup/destructors. Streaming classes expose reentrant `read()`, `write()`, and drain methods for composed coroutines.

## State and persistence
All state is request-local: connection pointers, method/path/params, headers, attrs, input buffers, result pointers, request refs, range/multipart settings, and callback buffers.

## Dependencies and integration points
Integrates `RGWSimpleCoroutine`, `RGWCoroutine`, `RGWRESTConn`, `RGWREST*Resource`, `RGWHTTPManager`, `RGWHTTPStreamRWRequest`, Boost.Asio, and JSON formatting for typed sends.

## Risks and test signals
Manual `put()`/intrusive pointer ownership is a key risk. Tests should validate send failure cleanup, null result paths, error-result decoding, DELETE behavior, range setup, multipart writes, cancellation destructors, and streaming backpressure.
