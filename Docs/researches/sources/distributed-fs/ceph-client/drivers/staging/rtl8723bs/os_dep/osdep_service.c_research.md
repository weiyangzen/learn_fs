# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/os_dep/osdep_service.c

Purpose: supplies small Linux service abstractions used by rtl8723bs for status conversion, skb receive submission, netdev private allocation, replaceable buffers, and a simple circular pointer buffer.

Important APIs/types/functions: `RTW_STATUS_CODE()` maps negative Linux errnos to `_FAIL` and nonnegative values to `_SUCCESS`. `_rtw_netif_rx()` sets `skb->dev` and submits to `netif_rx()`. `rtw_alloc_etherdev()` and `rtw_alloc_etherdev_with_old_priv()` allocate 4-queue Ethernet devices with a `rtw_netdev_priv_indicator`; `rtw_free_netdev()` frees the private adapter allocation and netdev. `rtw_buf_free()` and `rtw_buf_update()` manage owned byte buffers. Circular-buffer helpers are `rtw_cbuf_full()`, `rtw_cbuf_empty()`, `rtw_cbuf_push()`, `rtw_cbuf_pop()`, and `rtw_cbuf_alloc()`.

Control flow: allocation wraps `alloc_etherdev_mq()`, stores a private pointer and size in the indicator, and optionally `vzalloc()`s adapter private storage. Buffer update duplicates the new source first, then swaps the caller's pointer/length and frees the original. Circular push/pop only update read/write indexes modulo size and do no locking.

State and persistence: netdev private storage persists until `rtw_free_netdev()`. Replaceable buffers persist in caller-owned pointer/length pairs. `struct rtw_cbuf` stores size, read/write cursors, and a flexible array of pointers.

Dependencies and integration: used by netdev setup in `os_intfs.c`, receive path handoff to the kernel network stack, and any subsystem needing a tiny lock-free FIFO under externally controlled producer/consumer rules.

Risks: `rtw_cbuf_*` is explicitly lock-free and unsafe for arbitrary multi-producer/multi-consumer use. `rtw_buf_update()` drops the original even if `kmemdup()` fails for a non-empty source, replacing it with NULL/0. `rtw_free_netdev()` returns without freeing the `net_device` if `pnpi->priv` is NULL, so callers must understand ownership for old-priv netdevs.

Test signals: allocation/free tests should cover normal and old-private netdevs, failed adapter allocation, buffer update with NULL/empty/source allocation failure, circular-buffer wrap/full/empty edges, and receive path skb device assignment.
