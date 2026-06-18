# sources/distributed-fs/ceph/src/rgw/rgw_client_io.h

## Purpose
`rgw_client_io.h` defines the RGW front-end IO abstraction used by request handlers to receive client bodies and emit REST responses without binding the core gateway code to a specific front end such as Beast, civetweb, FastCGI, or load generators. It separates a minimal `BasicClient` interface from the REST-specific `RestfulClient`, provides a decorator base for filter pipelines, and exposes the high-level `RGWRestfulIO` wrapper used from `req_state::cio`.

## Important APIs, Types, And Functions
`rgw::io::BasicClient` owns initialization through `init(CephContext*)`, delegates front-end-specific setup to `init_env()`, exposes `get_env()`, and finishes work through `complete_request()`. Its `init()` implementation lives in `rgw_client_io.cc` and logs sanitized environment variables at debug level 20.

`rgw::io::RestfulClient` extends `BasicClient` with the ordered HTTP response lifecycle: optional `send_100_continue()`, exactly one `send_status()`, headers and either content length or chunked transfer, `complete_header()`, body writes, flush, and request completion. Methods throw `rgw::io::Exception` on transport errors.

`DecoratedRestfulClient<DecorateeT>` is the static/dynamic decorator base. It can hold either a decoratee object or pointer, forwards all `RestfulClient` calls, and lets pointer-based decorators be rewired through `set_decoratee()`. `RGWRestfulIO` derives from `AccountingFilter<RestfulClient*>`, keeps `shared_ptr<DecoratedRestfulClient>` filters alive, and inserts filters by setting each new filter's decoratee to the current chain head.

`BuffererSink` and `StaticOutputBufferer<BufferSizeV>` provide stack-backed buffering for small output fragments such as HTTP headers. `RGWClientIOStreamBuf` adapts `RGWRestfulIO::recv_body()` into a C++ `std::streambuf` with putback support; `RGWClientIOStream` exposes it as `std::istream`.

## Control Flow
The request path constructs a front-end `RestfulClient`, wraps it in `RGWRestfulIO`, optionally adds filters, stores it in `req_state::cio`, and request handlers call through `RESTFUL_IO(s)` or `ACCOUNTING_IO(s)`. The response lifecycle is deliberately ordered, but the base classes do not enforce it; front ends and filters rely on callers to honor the contract.

`RGWClientIOStreamBuf::underflow()` preserves the putback window, reads a new window from `rio.recv_body()`, and returns EOF if the read returns zero or throws. This makes body parsing code consume client data through standard stream extraction while the real source remains the RGW client IO pipeline.

## State And Persistence Behavior
This file defines transient request IO state only. It does not persist data to RADOS. `RGWRestfulIO` owns filter objects for the lifetime of the wrapper, while the underlying front-end engine is supplied externally. `StaticOutputBufferer` stores a fixed char array inside the streambuf and flushes to its sink during `sync()` and `overflow()`.

## Dependencies And Integration Points
The header depends on `rgw_common.h` for `RGWEnv` and `req_state`, and includes `rgw_client_io_filters.h` mid-file because the filter templates derive from types declared earlier in this same header. It is included broadly by REST handlers, auth code, process code, logging, checksum pipes, and front-end client implementations. The helper casts assert that `req_state::cio` actually implements the expected IO interface.

## Risks And Edge Cases
The response ordering contract is documented but not enforced, so filter behavior can become incorrect if handlers send headers or body out of order. Pointer decorators can be rewired without synchronization, and the comments explicitly put atomicity/thread-safety on callers. `RGWClientIOStreamBuf::underflow()` catches all `rgw::io::Exception` and reports EOF, which can collapse transport errors into normal stream exhaustion for stream consumers. `StaticOutputBufferer::overflow()` writes to `*pptr()` before syncing, so the setp end pointer intentionally reserves one character of space.

## Test Signals
Useful tests exercise request initialization logging with sanitized env values, ordered response generation through decorator chains, `RGWRestfulIO::add_filter()` chaining order, accounting through `ACCOUNTING_IO()`, and body stream extraction across multiple `recv_body()` windows including zero-length EOF and thrown exceptions.
