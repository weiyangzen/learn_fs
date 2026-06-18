# sources/distributed-fs/ceph-client/net/core/hwbm.c

Purpose: Provides helper functions for hardware buffer manager pools, letting drivers allocate, construct, count, and free buffers sized either as page fragments or kmalloc objects.

Important APIs, types, and functions: `hwbm_buf_free()` frees buffers according to `bm_pool->frag_size`. `hwbm_pool_refill()` allocates one buffer with `netdev_alloc_frag()` for page-sized fragments or `kmalloc()` for larger buffers, then invokes an optional pool `construct` callback. `hwbm_pool_add()` fills a pool with a requested number of buffers under `buf_lock`.

Control flow: Pool add locks `buf_lock`, rejects already-full pools, rejects additions beyond configured size, checks unsigned overflow, then calls refill in a loop until either the requested count is reached or allocation/construct fails. It increments `buf_num` by the number actually added and returns that count. Refill frees the buffer and returns `-ENOMEM` if construction fails.

State and persistence: State is in the caller-owned `struct hwbm_pool`: configured size, current `buf_num`, `frag_size`, mutex, and optional construct callback. This file does not maintain global state or persistence.

Dependencies and integration points: Used by network drivers with hardware buffer managers, depends on skb fragment allocation, kmalloc, mutexes, and driver-specific construct callbacks that typically hand buffers to hardware rings.

Risks: The construct callback owns device-specific side effects; returning failure after partially handing a buffer to hardware would leak or corrupt ownership. `buf_num` is updated only after the loop, so callbacks must not depend on it during refill. Allocation context is `GFP_KERNEL` in pool add. Large `frag_size` changes allocation/free mode and must remain consistent.

Test signals: Add buffers to empty, partially full, and full pools; request too many buffers; simulate allocation and construct failures; verify free path for <= PAGE_SIZE and > PAGE_SIZE buffers; run with lockdep around concurrent add attempts.
