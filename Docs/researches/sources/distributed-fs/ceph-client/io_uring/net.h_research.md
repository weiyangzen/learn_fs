<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/net.h -->
# sources/distributed-fs/ceph-client/io_uring/net.h

## Purpose
`net.h` declares io_uring networking request helpers and the async msghdr cache object. It conditionally exposes full networking APIs when `CONFIG_NET` is enabled and provides minimal no-op stubs for non-network builds.

## Important APIs, Types, and Functions
- `struct io_async_msghdr` stores cached vector state and the clearable msghdr-related fields: name length, fast iovec, control/payload lengths, user address, kernel `msghdr`, and sockaddr storage.
- Declared prep/issue/cleanup APIs cover shutdown, sendmsg/send, recvmsg/recv, send/recv failure, accept, socket, connect, zero-copy send, bind, listen, socket BPF population, and network message cache free.
- Non-CONFIG_NET stubs make `io_netmsg_cache_free()` and `io_socket_bpf_populate()` no-ops.

## Control Flow
The opcode table uses these declarations to wire network opcodes to prep and issue functions. Core request cleanup calls `io_sendmsg_recvmsg_cleanup()` or `io_send_zc_cleanup()` through `io_cold_defs`. Allocation caches call `io_netmsg_cache_free()` when freeing cached async msghdr objects.

## State and Persistence Behavior
`io_async_msghdr` is stored in `req->async_data` and may be recycled in the ring's `netmsg_cache`. The `struct_group(clear, ...)` layout allows the allocation cache to clear only per-use fields while retaining reusable vector allocations.

## Dependencies and Integration Points
It includes kernel net/uio/io_uring type headers and UAPI BPF filter context. It is consumed by `io_uring.c`, `opdef.c`, and network-related opcode handlers. Conditional compilation aligns with opdef's `CONFIG_NET` support decisions.

## Risks and Edge Cases
- The clear-group boundary must match cache initialization in `io_ring_ctx_alloc()`; otherwise stale msghdr state can leak across requests.
- Non-NET builds must not leave dangling references to unavailable issue functions.

## Test Signals
Build tests with `CONFIG_NET=y` and `CONFIG_NET=n` validate declarations/stubs. Runtime tests should verify async msghdr cache reuse does not preserve stale sockaddr/control/iovec state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/net.h -->
