# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/hal_sdio.c

## Purpose

`hal_sdio.c` provides small SDIO transmit-resource helpers for RTL8723BS. It tracks free TX FIFO pages, public-page borrowing, output-queue-token free space, and maximum transmit buffer length per queue. The source was read as a complete 105-line file.

## Important APIs, Types, and Functions

The exported functions are `rtw_hal_sdio_max_txoqt_free_space`, `rtw_hal_sdio_query_tx_freepage`, `rtw_hal_sdio_update_tx_freepage`, `rtw_hal_set_sdio_tx_max_length`, and `rtw_hal_get_sdio_tx_max_length`. They use `struct hal_com_data`, `struct dvobj_priv`, queue indices such as `HI_QUEUE_IDX`, `MID_QUEUE_IDX`, `LOW_QUEUE_IDX`, `PUBLIC_QUEUE_IDX`, and SDIO device IDs from `ffaddr2deviceId`.

## Control Flow

The query path checks whether dedicated free pages plus public free pages can satisfy a transmit request. The update path consumes dedicated pages first and falls back to the public queue. Maximum queue lengths are computed from queue-page counts plus half of the public queue, capped at `MAX_XMITBUF_SZ`, then selected by the output FIFO/device ID.

## State and Persistence Behavior

The state is entirely in `hal_com_data`: `SdioTxOQTMaxFreeSpace`, `SdioTxFIFOFreePage[]`, and `sdio_tx_max_len[]`. It persists only for the active adapter session and is updated as TX resources are consumed/refreshed.

## Dependencies and Integration Points

The file depends on the HAL default variable `HAL_DEF_TX_PAGE_SIZE`, SDIO queue indices, `ffaddr2deviceId`, and xmit scheduling code that queries and decrements pages before queuing frames. It is part of the SDIO HAL transmit path.

## Risks and Edge Cases

The free-page update lock is commented out, so concurrent TX scheduling could underflow or race if callers do not serialize access. `PageIdx` is not bounds-checked. Public page subtraction can underflow if query and update are not paired atomically. `rtw_hal_sdio_max_txoqt_free_space` imposes a minimum of 8, which can hide a lower hardware value.

## Test Signals

Unit tests should cover dedicated-only, public-borrowing, insufficient-page, queue-index mapping, and max-length capping. Concurrency tests or lockdep-style review should focus on page accounting under parallel transmit.
