<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_sdio.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_sdio.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_sdio.h` declares SDIO HAL helpers for queue-to-pipe mapping and transmit page accounting. The source was reviewed as a complete 18-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `ffaddr2deviceId`, `rtw_hal_sdio_max_txoqt_free_space`, `rtw_hal_sdio_query_tx_freepage`, `rtw_hal_sdio_update_tx_freepage`, `rtw_hal_set_sdio_tx_max_length`, and `rtw_hal_get_sdio_tx_max_length`.

## Control Flow

Transmit code queries free pages and queue limits before building SDIO transfer buffers, then updates accounting after reserving pages for a queue.

## State and Persistence Behavior

Uses SDIO device-object queue maps and HAL free-page counters; the header owns no storage.

## Dependencies and Integration Points

Integrates with `sdio_hal.h`, `sdio_ops.h`, `rtl8723b_xmit.h`, and the adapter's `dvobj_priv`. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Stale free-page accounting causes queue starvation or firmware buffer overrun. Queue index mapping must match firmware queue IDs.

## Test Signals

Saturated traffic across VO/VI/BE/BK queues, low-page conditions, and SDIO TX aggregation boundary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_sdio.h -->
