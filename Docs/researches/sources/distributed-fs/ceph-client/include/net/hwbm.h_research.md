# sources/distributed-fs/ceph-client/include/net/hwbm.h

Purpose: declares a hardware buffer manager pool abstraction for drivers that manage reusable receive buffers outside the normal skb allocation path.

Important APIs/types: `struct hwbm_pool` tracks capacity, fragment size, current buffer count, a construction callback, a mutex protecting the count, and private driver data. Under `CONFIG_HWBM`, functions free a buffer back to the pool, refill the pool, and add buffers. Without the option, stubs compile away and return success.

Control flow and state: drivers initialize a pool, call add/refill to allocate buffers, and call `hwbm_buf_free()` when a buffer returns. Persistent state is in the pool object and driver-private data; the mutex serializes buffer counter changes.

Dependencies and integration: depends on Linux mutexes, GFP allocation flags, and driver receive paths. It integrates with network drivers and page/fragment recycling logic.

Risks: config-disabled stubs can hide missing runtime behavior in builds without HWBM. Buffer constructors must match fragment size and hardware DMA requirements. Tests should include refill failure, concurrent free/refill, constructor errors, pool exhaustion, config-on/off builds, and driver teardown with outstanding buffers.
