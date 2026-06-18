# sources/distributed-fs/ceph-client/include/net/xdp_sock_drv.h

## Purpose

`xdp_sock_drv.h` is the driver-facing wrapper API for AF_XDP zero-copy support. It exposes pool sizing, DMA mapping, buffer allocation/free, multi-buffer fragment handling, raw descriptor address translation, metadata validation, and need-wakeup helpers.

## Important APIs, types, and functions

Important constants are `XDP_UMEM_MIN_CHUNK_SHIFT`, `XDP_UMEM_MIN_CHUNK_SIZE`, `NETDEV_XDP_ACT_XSK`, and `XDP_TXMD_FLAGS_VALID`. The driver-private callback descriptor is `struct xsk_cb_desc`. Wrappers include `xsk_tx_completed()`, `xsk_tx_peek_desc()`, `xsk_tx_peek_release_desc_batch()`, `xsk_tx_release()`, `xsk_get_pool_from_qid()`, wakeup setters/clearers, pool geometry helpers, `xsk_pool_dma_map()`/`unmap()`, DMA accessors, `xsk_buff_alloc()`/`alloc_batch()`/`can_alloc()`/`free()`, fragment helpers, raw data/DMA/context helpers, metadata helpers, and DMA sync helpers.

## Control flow

Drivers obtain an XSK pool for a queue, map UMEM pages for DMA, allocate XDP buffers from the fill ring, run RX/XDP, and free or redirect buffers. TX paths peek descriptors, translate user addresses to data/DMA plus optional metadata, prepare hardware descriptors, then report completions and release TX descriptors. Multi-buffer paths add fragments to the head buffer, maintain pool fragment lists, and free all fragments on packet completion.

## State and persistence behavior

Persistent state is in `struct xsk_buff_pool`: device/netdev pointers, queue ID, UMEM, fill/completion queues, free head arrays, DMA page array, chunk geometry, metadata length, need-wakeup cache, zero-copy limits, software checksum flag, and locks. Driver rings may persist completion metadata and DMA addresses until TX completion.

## Dependencies and integration points

It depends on `xdp_sock.h`, `xsk_buff_pool.h`, AF_XDP UAPI, DMA APIs, and `CONFIG_XDP_SOCKETS`. It integrates with NIC RX/TX queue setup, NAPI, DMA mapping, AF_XDP rings, XDP multi-buffer, and TX metadata offload.

## Risks and test signals

Risks include using zero helpers when AF_XDP is disabled, wrong frame size after reserving tailroom, DMA sync omissions, descriptor crossing non-contiguous pages, leaked fragment list entries, invalid metadata flags being silently ignored, and queue/pool lifetime races. Tests should cover pool lookup, DMA map/unmap, aligned and unaligned UMEM, multi-buffer RX/TX, descriptor boundary validation, need-wakeup behavior, metadata validation, and driver teardown with active sockets.
