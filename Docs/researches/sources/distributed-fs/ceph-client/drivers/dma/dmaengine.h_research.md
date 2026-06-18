# sources/distributed-fs/ceph-client/drivers/dma/dmaengine.h

Purpose: Private helper header for DMAengine provider drivers. It is not a client API; it supplies cookie helpers, callback helpers, private slave-channel helpers, and debugfs root access.

Important APIs/types/functions: Cookie helpers are `dma_cookie_init`, `dma_cookie_assign`, `dma_cookie_complete`, `dma_cookie_status`, `dma_set_residue`, and `dma_set_in_flight_bytes`. Callback helpers include `struct dmaengine_desc_callback`, `dmaengine_desc_get_callback`, `dmaengine_desc_callback_invoke`, `dmaengine_desc_get_callback_invoke`, and `dmaengine_desc_callback_valid`. It declares `dma_get_slave_channel` and `dma_get_any_slave_channel`, and conditionally exposes `dmaengine_get_debugfs_root`.

Control flow: Providers initialize channel cookies to `DMA_MIN_COOKIE`, assign monotonically increasing nonzero cookies under their own lock, complete descriptors by moving the cookie to `completed_cookie` and clearing the descriptor cookie, and report status by comparing requested, completed, and used cookies. Callback helpers snapshot callback fields and invoke either result-aware or legacy callbacks with a default success result when needed.

State and persistence: The helpers mutate fields inside `struct dma_chan`, `struct dma_async_tx_descriptor`, and optional `struct dma_tx_state`. There is no independent state or persistence.

Dependencies/integration: Included by DMAengine provider drivers and `dmaengine.c`. Depends on public `<linux/dmaengine.h>` types and optional debugfs support.

Risks: Cookie assign/complete helpers require provider-side serialization; misuse can corrupt completion ordering. `dma_cookie_complete` BUGs on invalid cookies. Callback invocation locking is delegated to the driver. `dma_cookie_status` uses a barrier but no lock, so it reports the standard lockless snapshot semantics.

Test signals: provider unit/integration tests that submit and complete descriptors in order, wrap cookie values below `DMA_MIN_COOKIE`, status/residue reporting, callback and callback_result paths, and debugfs root behavior with and without `CONFIG_DEBUG_FS`.
