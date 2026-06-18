# sources/distributed-fs/ceph-client/io_uring/zcrx.h

## Purpose

`sources/distributed-fs/ceph-client/io_uring/zcrx.h` declares the in-kernel state and public io_uring entry points for zero-copy receive. It is the local contract shared by io_uring receive code, registration code, and the ZCRX implementation. The source was read as a complete 121-line file.

## Important APIs, Types, and Functions

`struct io_zcrx_mem` tracks imported memory: size, dma-buf vs pinned-pages mode, page arrays, sg tables, accounted pages, dma-buf attachment, and dma-buf object. `struct io_zcrx_area` owns the `net_iov_area`, back-pointer to `io_zcrx_ifq`, per-buffer user refs, freelist, area id, mapping state, and imported memory. `struct zcrx_rq` describes the userspace refill ring and cached head. `struct io_zcrx_ifq` is the registered interface queue with area pointer, user/mm accounting, refill ring, RX queue id, device/netdev references, refcounts, provider lock, and mapped region.

When `CONFIG_IO_URING_ZCRX` is enabled, the header declares `io_zcrx_ctrl()`, `io_register_zcrx()`, `io_unregister_zcrx()`, `io_terminate_zcrx()`, `io_zcrx_recv()`, and `io_zcrx_get_region()`. When disabled, those helpers return `-EOPNOTSUPP` or `NULL` and unregister/terminate become no-ops. `io_recvzc()` and `io_recvzc_prep()` are always declared for the higher-level receive operation.

## Control Flow

The header has no executable control flow beyond disabled-feature inline stubs. It establishes that enabled builds use the real registration/control/receive implementation, while disabled builds compile callers without special-case preprocessor logic.

## State and Persistence Behavior

The structures describe runtime state only. Lifetimes are reference-counted through `io_zcrx_ifq.refs` and `user_refs`, and are tied to io_uring context lifetime, exported fd lifetime, netdev page-pool ownership, and user-visible buffer ownership. No persistent storage is declared here.

## Dependencies and Integration Points

Includes show the integration surface: `linux/io_uring_types.h`, `linux/dma-buf.h`, sockets, page-pool types, and net-device tracker support. The constants `ZCRX_SUPPORTED_REG_FLAGS` and `ZCRX_FEATURES` bind this implementation to UAPI flags such as import, nodev registration, and RX page-size feature reporting.

## Risks and Edge Cases

The header is a state-layout contract inside io_uring. Field changes can break assumptions in the implementation about cacheline placement, page-pool callbacks, mmap region lookup, and lifetime cleanup. The disabled stubs must stay behaviorally aligned with callers so unsupported kernels return clean errors instead of partially enabling recvzc paths.

## Test Signals

Build tests should cover both `CONFIG_IO_URING_ZCRX=y` and disabled configurations. Static checks should verify all declared enabled symbols are implemented and that disabled stubs satisfy callers. Runtime tests should confirm unsupported builds return `-EOPNOTSUPP` for registration, control, and receive.
