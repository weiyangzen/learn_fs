# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-stm32.c

Purpose: supplies shared DMA helper routines for STM32 I2C controller drivers. It requests TX/RX DMA channels, configures slave addresses for the controller data registers, prepares a single DMA transfer, and releases DMA resources.

Important APIs/types/functions: exported helpers are `stm32_i2c_dma_request()`, `stm32_i2c_dma_free()`, and `stm32_i2c_prep_dma_xfer()`. They operate on `struct stm32_i2c_dma` from `i2c-stm32.h`, including TX/RX channels, active channel, mapped DMA address/length, transfer direction, data direction, and completion. The request function accepts physical controller address plus TXDR/RXDR offsets so controller-specific drivers can share the same helper.

Control flow: `stm32_i2c_dma_request()` allocates managed state, requests `"tx"` then `"rx"` DMA channels, configures TX as memory-to-device with one-byte width and RX as device-to-memory with one-byte width, initializes a completion, and returns the helper state. On any failure it releases already acquired channels and frees the managed allocation. `stm32_i2c_prep_dma_xfer()` selects RX or TX channel from the `rd_wr` flag, maps the caller buffer, prepares a slave descriptor with interrupt completion, stores callback metadata, submits it, and issues pending DMA. Errors unmap the buffer before returning.

State and persistence: DMA state persists for the lifetime of the parent controller driver after request. Per-transfer state is `chan_using`, `dma_buf`, `dma_len`, and direction fields. The helper maps buffers for each transfer but leaves unmapping to callback/error handling by the controller driver after successful submission.

Dependencies and integration: depends on Linux DMA engine, DMA mapping, device-managed allocation, and named DMA channels. It is consumed by STM32F7-style controller code and parameterized by that controller's TX/RX register offsets.

Risks: successful transfer preparation requires callers to unmap `dma_buf`; leaks or stale mappings happen if the controller callback path is skipped. `-ENODEV` for absent channels is intentionally quiet to allow PIO fallback, while other failures are logged. TX and RX channels must both exist or the helper fails completely.

Test signals: no-DMA fallback with `-ENODEV`, TX-only request failure cleanup, RX config failure cleanup, DMA mapping failure, descriptor preparation failure, and successful callback/unmap paths from a controller transfer.
