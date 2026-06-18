# sources/distributed-fs/ceph/src/rgw/rgw_cr_rest.cc

## Purpose
Implements coroutine helpers for streaming REST resources between RGW components over HTTP, including read backpressure, write backpressure, request lifetime cleanup, and stream splicing.

## Important APIs, types, and functions
`RGWCRHTTPGetDataCB` buffers received body data and optional prepended metadata. `RGWStreamReadHTTPResourceCRF::init/read/decode_rest_obj()` drives async HTTP reads and extracts headers/extra data. `RGWStreamWriteHTTPResourceCRF::send/write/drain_writes()` sends headers and body chunks while honoring pending-write limits. `RGWStreamSpliceCR::operate()` connects a read resource to a write resource.

## Control flow
Read setup registers a receive callback, sends the request, then `read()` yields until data or completion events arrive. Write setup sends a request, `write()` yields when pending sends exceed the window, and `drain_writes()` finalizes the stream and handles response headers. Splice initializes the input, waits for attrs before sending output headers, copies chunks, then drains writes.

## State and persistence
State is transient coroutine state: request pointers, callback buffers, timers/IO ids, buffered data, flags for attrs/extra data, pending write state, and total bytes read. No durable storage is modified.

## Dependencies and integration points
Depends on RGW coroutine environment, HTTP manager/request classes, Boost.Asio stackless coroutine macros, and `bufferlist`.

## Risks and test signals
Risks include request cancellation ordering, callback locking, pause/unpause thresholds, extra-data framing, empty reads before EOF, and write drain races. Tests should simulate slow readers/writers, cancellation, HTTP errors, extra metadata decoding, and large stream splices.
