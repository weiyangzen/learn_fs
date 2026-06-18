# sources/distributed-fs/ceph/src/rgw/rgw_asio_client.h

## Purpose
Declares the Beast/ASIO RGW client IO adapter used by the RGW beast frontend.

## Important APIs, Types, and Functions
- `ClientIO` derives from `io::RestfulClient` and `io::BuffererSink`.
- Holds a Beast request parser reference, SSL flag, endpoint addresses, environment, static output buffer, and keepalive/continue state.
- Overrides environment initialization, request completion, flushing, status/header/body output, and environment access.

## Control Flow
The header exposes direct `send_body()` forwarding to `write_data()` and `keep_alive()` inspection. Implementation handles the detailed HTTP/env translation.

## State and Persistence
Only per-request runtime state is held. The parser is referenced, so its lifetime must exceed `ClientIO`.

## Dependencies and Integration Points
Includes Boost.Asio TCP, Boost.Beast HTTP/core, Ceph asserts, and RGW client IO abstractions. It is coupled to `request_parser<buffer_body>`.

## Risks and Edge Cases
The parser reference and endpoint snapshots must remain valid during the request. `keep_alive()` returns adapter state, which can be changed by response handling after construction.

## Test Signals
Construction/lifetime tests, send-body forwarding, environment access, and keepalive state transitions should accompany implementation tests.
