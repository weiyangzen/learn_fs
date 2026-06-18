# sources/distributed-fs/ceph-client/drivers/staging/greybus/sdio.c

## Purpose
Implements a Greybus SD/MMC host bridge as a `gbphy_driver` for `GREYBUS_PROTOCOL_SDIO`. It presents a remote Greybus SDIO controller to the Linux MMC core by allocating an `mmc_host`, translating host capability, OCR, IOS, command, response, and data-transfer semantics into Greybus SDIO operations.

## Important APIs, Types, and Functions
`struct gb_sdio_host` owns the Greybus connection, gbphy device, `mmc_host`, current `mmc_request`, locks, workqueue, transfer cancellation state, and card state. `_gb_sdio_set_host_caps()` maps Greybus capability bits to `mmc->caps/caps2`; `_gb_sdio_get_host_ocr()` maps Greybus voltage bits to Linux OCR bits. `gb_sdio_get_caps()` fetches remote limits and programs `mmc` maximum block, segment, request, frequency, and OCR fields. `gb_mmc_request()`, `gb_mmc_set_ios()`, `gb_mmc_get_ro()`, `gb_mmc_get_cd()`, and `gb_mmc_switch_voltage()` implement `mmc_host_ops`. `gb_sdio_command()`, `_gb_sdio_send()`, `_gb_sdio_recv()`, and `gb_sdio_transfer()` encode command and data phases into `GB_SDIO_TYPE_COMMAND` and `GB_SDIO_TYPE_TRANSFER`.

## Control Flow and State
Probe allocates the MMC host, creates/enables the Greybus connection, reads capabilities, initializes locks and a single-lane workqueue, enables RX, registers the MMC host, then processes queued insert/remove events. Requests enter `gb_mmc_request()`, are rejected if removed or media absent, then run asynchronously in `gb_sdio_mrq_work()`: optional SBC, command, data chunks, optional stop, completion via `mmc_request_done()`. Transfer chunks are bounded by Greybus payload size and copied through scatterlists. STOP_TRANSMISSION marks `xfer_stop` so the active chunk loop aborts with `-EINTR`.

## Dependencies and Integration Points
Depends on Greybus core operations and `gbphy` runtime PM, Linux MMC core, scatterlist helpers, workqueues, mutexes, and spinlocks. It integrates with remote unsolicited `GB_SDIO_TYPE_EVENT` messages for card insert/remove/write-protect and calls `mmc_detect_change()`.

## Risks and Test Signals
Key risks are request lifetime races around remove, event queuing while `removed` is true, payload sizing for non-divisible block transfers, and the `single_op()` timeout check for multi-block single commands. Test signals include successful module probe/remove, card-detect changes, read/write scatterlist integrity across multi-payload transfers, STOP cancellation, runtime PM balance, and MMC core error propagation for `-ENOMEDIUM`, `-ESHUTDOWN`, and Greybus operation failures.
