# sources/distributed-fs/ceph/src/rgw/rgw_rest_zero.cc

## Purpose
`rgw_rest_zero.cc` implements a lightweight unauthenticated REST endpoint for benchmarking the RGW HTTP frontend without backend object IO. It models a single in-memory resource whose only durable-for-process property is a byte size; GET returns that many zero bytes, HEAD reports the size, PUT consumes and discards a request body while setting size, and DELETE resets size to zero.

## Important APIs, Types, and Functions
`ZeroResource` contains a mutex and `std::size_t size`. All paths handled by the manager share this one resource.

`ZeroOp` is the base operation. It permits all requests and sends headers using `response_content_type` and `response_content_length`.

`ZeroDeleteOp` locks the resource and sets size to zero. `ZeroHeadOp` locks and reports current size with `application/octet-stream`. `ZeroGetOp` locks to read size, sends headers, then writes zero-filled chunks up to `rgw_max_chunk_size`. `ZeroPutOp` requires `Content-Length`, parses it, reads and discards exactly that many bytes in chunks, and on success stores the new size.

`ZeroHandler` disables auth/permission checks and maps DELETE/GET/HEAD/PUT to the zero operations. `RESTMgr_Zero` owns the shared `ZeroResource` and returns a `ZeroHandler`.

## Control Flow
The manager returns a handler for any path under the endpoint. The handler creates an operation by HTTP method. PUT validates and drains the body before updating shared size. GET sends response headers first and then streams zero bytes until the recorded size is exhausted. HEAD does not send a body. DELETE is immediate.

## State and Persistence Behavior
State is process-local only. `ZeroResource::size` is protected by a mutex but is not stored in RADOS or any external backend. It resets when the RGW process restarts. PUT changes size only after the whole request body is read successfully.

## Dependencies and Integration Points
The file depends on RGW REST base classes, body IO helpers `recv_body()` and `dump_body()`, `rgw_max_chunk_size`, and Ceph `parse<size_t>()`. It lives in namespace `rgw` and integrates through `RESTMgr_Zero`.

## Risks
The GET and PUT loops subtract the return value from `dump_body()`/`recv_body()` without explicitly handling non-exception negative returns. If those helpers can return negative integers without throwing, the unsigned `remaining` counter could underflow. The endpoint is unauthenticated by design, so it should only be exposed intentionally.

Large `Content-Length` values can drive long drain/send loops and frontend bandwidth use even though there is no backend IO. This is expected for benchmarking but risky on public endpoints.

## Test Signals
Tests should cover PUT missing/invalid content length, PUT with zero and nonzero lengths, HEAD after PUT/DELETE, GET byte count and content type, concurrent PUT/GET/DELETE mutex behavior, request body read failures, response body write failures, and process-local reset semantics.
