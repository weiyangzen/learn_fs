# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/rtl8723bs_xmit.c

Purpose: this file implements the RTL8723BS SDIO transmit scheduler, aggregation into xmit buffers, write-port draining, management-frame transmit handling, and transmit private initialization/free.

Important APIs and functions: `rtl8723bs_hal_xmit` enqueues data frames and wakes `SdioXmitStart`; `rtl8723bs_xmit_thread` runs `rtl8723bs_xmit_handler`; `xmit_xmitframes` aggregates queued frames into `xmit_buf` objects; `rtl8723bs_xmit_buf_handler` drains pending xmit buffers to SDIO write ports. `rtl8723bs_mgnt_xmit` prepares management/beacon frames. Init/free entry points are `rtl8723bs_init_xmit_priv` and `rtl8723bs_free_xmit_priv`.

Control flow: data transmit queues frames by WMM/hardware queue. The xmit thread wakes on `SdioXmitStart`, checks pending frames, selects queue order from WMM settings, allocates/extends an xmit buffer until SDIO max length or OQT space constraints, coalesces frames, fills TX descriptors with `rtl8723b_update_txdesc`, and enqueues the xmit buffer. The buffer handler waits on `xmit_comp`, checks free page counts and OQT space, writes to the mapped SDIO device ID, updates cached free pages, and frees the xmit buffer.

State and persistence: transient state lives in `xmit_priv` queues/completions, `xmit_buf` aggregation counters/page counts, `hal_com_data.SdioTxFIFOFreePage`, `SdioTxOQTFreeSpace`, and `SdioTxFIFOFreePageLock`. Link busy state can trigger ADDBA requests and low-power exit traffic notifications.

Dependencies and integration: depends on common xmit queues/coalescing, SDIO port writes from `sdio_ops.c`, queue/page mapping from `sdio_halinit.c`, TX descriptor construction in `rtl8723b_hal_init.c`, and MLME/power state.

Risks and test signals: resource accounting errors can deadlock TX or overrun FIFO pages. `pxmitbuf->priv_data` is special because the first aggregated frame is freed only after the final descriptor update; error paths must not double-free it. Tests should cover high/low/normal queues, busy traffic, AP sleeping stations, beacon direct write, management ack reports, OQT exhaustion, surprise removal/driver stop, and cleanup of pending buffers.
