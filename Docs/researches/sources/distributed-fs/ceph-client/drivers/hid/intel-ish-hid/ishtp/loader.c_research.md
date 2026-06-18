# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp/loader.c

## Purpose
`loader.c` implements host-driven main firmware loading for ISH platforms that expose the firmware-loader fixed client. It locates a platform-specific firmware image, allocates DMA fragments, sends loader query/fragment/start commands over ISHTP fixed-client messaging, retries failures, and extracts manifest version information after a successful load.

## Important APIs, types, and functions
The public entry point is `ishtp_loader_work()`, scheduled by HBM when firmware advertises loader capability. Internal helpers are `loader_write_message()`, `loader_xfer_cmd()`, `prepare_dma_bufs()`, `release_dma_bufs()`, `_request_ish_firmware()`, `request_ish_firmware()`, `copy_manifest()`, and `copy_ish_version()`. Firmware naming uses DMI system vendor/product/product-family/SKU CRC32 values plus the generation string from `dev->driver_data->fw_generation`.

## Control flow and integration points
`ishtp_loader_work()` requests firmware using the most-specific DMI-derived filename first and the generation default last. It computes a page-aligned fragment size across `FRAGMENT_MAX_NUM` descriptors, allocates coherent DMA buffers, copies firmware chunks into them, flushes caches, and then retries up to `ISHTP_LOADER_RETRY_TIMES` through `XFER_QUERY`, `XFER_FRAGMENT`, and `START`. Loader responses arrive through `recv_fixed_cl_msg()` in `hbm.c`, which copies data into `dev->fw_loader_rx_buf` and wakes `wait_loader_recvd_msg`.

## State and persistence behavior
Runtime state lives in `struct ishtp_device`: loader wait flags/buffers, base firmware version, and project firmware version. DMA buffers are temporary and released before the work item exits. Firmware files are loaded from the kernel firmware search path but not modified. No driver state is persisted.

## Dependencies
The loader depends on firmware_class, DMI, CRC32, coherent DMA, cache flushing, ISHTP fixed-client writes, HBM loader capability detection, and manifest structures from `loader.h`. It requires `dev_get_drvdata(dev->devc)` to return the `ishtp_device`.

## Risks and edge cases
Missing firmware leaves firmware waiting for host load until drivers are reloaded. DMA allocation failure releases temporary state but cannot recover communication without retrying the driver load. Incorrect firmware may consume all retries and require a platform reset. `request_ish_firmware()` computes CRC variables only when the corresponding DMI string exists; filename branches must only use initialized CRCs. `loader_xfer_cmd()` relies on fixed 100 ms response timeout and a single shared receive buffer, so concurrent loader messages would be unsafe.

## Test signals
Test with default and DMI-specific firmware names, missing firmware, malformed loader responses, timeout/no-response, DMA allocation failure, fragment sizing across small and large firmware images, retry behavior after query/fragment/start failures, manifest present/absent cases, version-field decoding, and removal while loader work is pending.
