# sources/distributed-fs/ceph-client/include/net/xsk_buff_pool.h

## Purpose

`xsk_buff_pool.h` defines the AF_XDP buffer pool backing zero-copy UMEM access. It describes XDP buffer wrappers, DMA page maps, pool control/data-path fields, address translation, DMA sync, descriptor boundary checks, and handle reconstruction.

## Important APIs, types, and functions

Key types are `struct xdp_buff_xsk`, `struct xsk_dma_map`, `struct xsk_buff_pool`, and `struct xdp_desc_ctx`. Macros include `XSK_PRIV_MAX`, `XSK_CHECK_PRIV_TYPE()`, `XSK_TX_COMPL_FITS()`, and `XSK_NEXT_PG_CONTIG_MASK`. Core functions include `xp_create_and_assign_umem()`, `xp_assign_dev()`, `xp_assign_dev_shared()`, `xp_alloc_tx_descs()`, `xp_destroy()`, `xp_get_pool()`, `xp_put_pool()`, `xp_clear_dev()`, `xp_add_xsk()`, `xp_del_xsk()`, `xp_free()`, `xp_dma_map()`/`unmap()`, `xp_alloc()`/`alloc_batch()`/`can_alloc()`, `xp_raw_get_data()`, `xp_raw_get_dma()`, and `xp_raw_get_ctx()`. Inline helpers initialize buffer address/DMA, sync DMA, detect non-contiguous page crossing, parse multi-buffer descriptors, extract aligned/unaligned addresses, release heads, reconstruct UMEM handles, and test metadata enablement.

## Control flow

AF_XDP core creates a pool from UMEM, assigns it to a device queue, maps pages for DMA, and adds sockets. Drivers allocate `xdp_buff_xsk` heads, initialize data and DMA addresses from user descriptors, process RX/TX, and return heads to the pool. Address helpers convert descriptor handles to user virtual addresses and DMA addresses, while boundary checks prevent descriptors from spanning non-contiguous pages.

## State and persistence behavior

The pool persists across socket binding and holds device/netdev pointers, TX socket list, UMEM, work item, RX lock, free lists, fill/completion queues, DMA page array, buffer heads, TX descriptor cache, chunk geometry, metadata length, need-wakeup state, and free-head counters. DMA maps are refcounted and protected by RTNL list membership.

## Dependencies and integration points

It depends on AF_XDP UAPI, DMA mapping, BPF, public XDP types, netdevice/device/page declarations, and XSK queues. It integrates with AF_XDP core, zero-copy NIC drivers, XDP memory model registration, and TX metadata completion storage.

## Risks and test signals

Risks include incorrect unaligned address reconstruction, DMA page flag misuse, accepting descriptors crossing non-contiguous pages, free-head accounting imbalance, stale device pointers after teardown, and private callback storage overflow. Tests should cover pool create/assign/destroy, shared UMEM assignment, DMA map refcounts, aligned/unaligned descriptors, page-boundary validation, handle round trips, DMA sync, need-wakeup caching, TX descriptor allocation, and active socket removal.
