# sources/distributed-fs/ceph-client/drivers/media/mmc/siano/smssdio.c

Purpose: SDIO transport driver for Siano SMS1xxx MDTV devices. It registers SDIO IDs, sends host requests to the device, receives interrupt-driven responses/data blocks, and connects the SDIO function to the shared Siano core.

Important APIs/types/functions: `struct smssdio_device` holds the `sdio_func`, Siano `coredev`, and partial split-message buffer. SDIO callbacks are `smssdio_probe()`, `smssdio_remove()`, and interrupt handler `smssdio_interrupt()`. Siano core callback `smssdio_sendrequest()` transmits buffers. The ID table maps Siano vendor/device IDs to board IDs.

Control flow: probe allocates transport state, fills `smsdevice_params_t`, rejects Stellar as unsupported, registers the common Siano device, sets board ID, claims the SDIO host, enables the function, sets 128-byte block size, claims IRQ, stores drvdata, releases host, and starts the core device. Interrupts acknowledge by reading `SMSSDIO_INT`, allocate or reuse a split buffer, read the first 128-byte block, determine remaining aligned length from the SMS header, read the rest either in one transfer or block-by-block fallback, endian-fix the message, and pass it to `smscore_onresponse()`. Remove unregisters the core, releases IRQ, disables function, and frees transport state.

State/persistence: runtime state is the SDIO function, common core device, and optional `split_cb`. Device buffers are transient and owned by the Siano core once delivered. No durable persistence.

Dependencies/integration: depends on Linux MMC/SDIO core, shared Siano `smscoreapi`, card database, endian helpers, firmware infrastructure through the core, and DMA-capable buffer allocation via core registration.

Risks/test signals: interrupt error path after failing the initial block read leaks `cb` because it returns without `smscore_putbuffer()`. Remove notes a racy split buffer cleanup. Pointer arithmetic is done on `void *`, relying on compiler extension. Tests should cover all matched board IDs, unsupported Stellar, enable/blocksize/IRQ/start unwind paths, split-message two-interrupt handling, fallback block reads after `-EINVAL`, endian conversion, send chunking by block size, and unplug during pending split message.
