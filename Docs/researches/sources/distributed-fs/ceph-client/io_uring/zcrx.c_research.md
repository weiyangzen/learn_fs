# sources/distributed-fs/ceph-client/io_uring/zcrx.c

## Purpose

`sources/distributed-fs/ceph-client/io_uring/zcrx.c` implements io_uring zero-copy receive support. It lets privileged users register a receive queue backed by user memory or a dma-buf, bind that queue to a network RX queue through the page-pool memory-provider API, deliver received buffer slices through extended CQEs, and reclaim buffers through a userspace refill ring. The source was read as a complete 1615-line file.

## Important APIs, Types, and Functions

The exported entry points are `io_register_zcrx()`, `io_unregister_zcrx()`, `io_terminate_zcrx()`, `io_zcrx_ctrl()`, `io_zcrx_get_region()`, and `io_zcrx_recv()`. Internal lifecycle helpers include `io_import_umem()`, `io_import_dmabuf()`, `io_import_area()`, `io_zcrx_create_area()`, `zcrx_register_netdev()`, `io_allocate_rbuf_ring()`, `io_zcrx_ifq_free()`, and `zcrx_unregister()`.

The page-pool integration is the `memory_provider_ops io_uring_pp_zc_ops` table: `io_pp_zc_alloc_netmems()` refills the driver page pool from returned userspace buffers or the area freelist, `io_pp_zc_release_netmem()` returns provider buffers to the freelist, `io_pp_zc_init()` validates page-pool parameters, `io_pp_uninstall()` detaches the provider, and `io_pp_nl_fill()` reports netlink attributes.

Receive-side helpers are `io_zcrx_queue_cqe()`, `io_zcrx_recv_frag()`, `io_zcrx_copy_chunk()`, `io_zcrx_recv_skb()`, and `io_zcrx_tcp_recvmsg()`. Control operations include `zcrx_flush_rq()` for force-returning userspace-held buffers and `zcrx_export()`/`import_zcrx()` for sharing a ZCRX queue through an anonymous inode fd.

## Control Flow

Registration requires `CAP_NET_ADMIN`, `IORING_SETUP_DEFER_TASKRUN`, and either `IORING_SETUP_CQE32` or `IORING_SETUP_CQE_MIXED`. `io_register_zcrx()` copies the userspace registration, preallocates an xarray id, creates the mapped refill region, imports the memory area, optionally opens a netdev RX queue with this file's page-pool provider, publishes the `io_zcrx_ifq`, and copies negotiated offsets, ids, and buffer sizes back to userspace.

Memory import validates reserved fields, page alignment, size ranges, and flags. Anonymous user memory is pinned with `io_pin_pages()`, converted to an sg table, optionally DMA-mapped, and charged against io_uring memory accounting. Dma-buf import attaches to the RX device, maps for `DMA_FROM_DEVICE`, and verifies the mapped DMA length matches the requested length. Area creation slices imported memory into power-of-two `net_iov` entries, initializes per-buffer user reference counters, and seeds the freelist.

The network datapath asks the page pool for provider memory. The fast refill path parses userspace RQEs, decrements the userspace reference for the named `net_iov`, tests the page-pool refcount, and returns only buffers owned by the requesting page pool. The slow path allocates unused `net_iov`s from the freelist. Receive CQEs contain the original request user data, result length, `IORING_CQE_F_MORE`, optional `IORING_CQE_F_32`, and a ZCRX offset encoding area id plus buffer offset. TCP is the only supported protocol path, via `tcp_read_sock()`.

## State and Persistence Behavior

State is in `io_zcrx_ifq`, `io_zcrx_area`, `io_zcrx_mem`, and the mapped `zcrx_rq`. It is per-io_uring-context and held in `ctx->zcrx_ctxs`. The state persists until explicit unregister, io_uring termination, imported-fd close, or page-pool/netdev uninstall. No file-backed data is persisted; pinned pages, dma-buf attachments, DMA mappings, xarray ids, region mappings, netdev references, device references, uid/mm accounting, and page-pool references are all runtime resources.

User references (`area->user_refs`) and page-pool refs jointly protect buffers exposed to userspace. `io_zcrx_scrub()` reclaims buffers still counted as userspace-held during unregister. `io_terminate_zcrx()` first marks and unregisters userspace-facing queue ownership; `io_unregister_zcrx()` later erases xarray entries and drops final references.

## Dependencies and Integration Points

This file integrates io_uring resource registration, mapped regions, deferred CQE allocation, network `page_pool`, netdev RX queue memory-provider installation, DMA mapping APIs, dma-buf, TCP receive internals, RPS flow recording, and netlink queue diagnostics. It depends on UAPI structures from `linux/io_uring.h`, local io_uring helpers from `io_uring.h`, `memmap.h`, `kbuf.h`, and `rsrc.h`, and the data contracts declared in `zcrx.h`.

## Risks and Edge Cases

The main risks are lifetime and ownership races across io_uring, userspace, page pools, and netdev teardown. Incorrect user-ref or page-pool-ref transitions can lead to buffer reuse while userspace still reads it, leaked buffers, or stale DMA ownership. The code also has sharp validation requirements around power-of-two buffer sizes, page alignment, dma-buf lengths, xarray publication, RQE offset parsing, and mixed/CQE32 CQE layout. Dma-buf areas are not kernel-readable, so skb head data and non-provider fragments can only be copied when the area came from pinned pages.

## Test Signals

Useful tests include registration failure coverage for missing capabilities, wrong io_uring setup flags, bad reserved fields, invalid RX queue ids, bad region sizes, non-power-of-two buffer sizes, and unsupported dma-buf configurations. Datapath tests should cover TCP receive with provider frags, copied skb head data, fallback copies, RQE refill, RQ flush, multishot CQE behavior, queue export/import, netdev uninstall, unregister while buffers are held by userspace, dma-sync-required devices, and memory-accounting cleanup after all failure paths.
