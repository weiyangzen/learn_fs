# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/os_dep/sdio_ops_linux.c

Purpose: implements rtl8723bs Linux SDIO CMD52/CMD53 read/write primitives and host-claim handling for register and memory access.

Important APIs/types/functions: `rtw_sdio_claim_host_needed()` suppresses nested `sdio_claim_host()` while running in the driver's SDIO IRQ thread. `rtw_sdio_set_irq_thd()` records that IRQ thread. Byte/register operations include `_sd_cmd52_read()`, `sd_cmd52_read()`, `_sd_cmd52_write()`, `sd_cmd52_write()`, `sd_read8()`, `sd_read32()`, `sd_write8()`, and `sd_write32()`. Bulk operations are `_sd_read()`, `sd_read()`, `_sd_write()`, and `sd_write()`.

Control flow: public wrappers resolve adapter/dvobj/sdio_func, skip work on surprise removal, conditionally claim the SDIO host, call the underscore variant, then release the host. CMD52 helpers loop byte-by-byte. CMD53 helpers use byte access for 1-2 byte transfers and `sdio_memcpy_fromio()`/`sdio_memcpy_toio()` for larger transfers. 32-bit read/write retries up to `SD_IO_TRY_CNT`, reset continual I/O error state on success, and mark `bSurpriseRemoved` on shutdown/device errors or excessive continual errors.

State and persistence: uses `sdio_data->sys_sdio_irq_thd` to track IRQ context and adapter `bSurpriseRemoved` to short-circuit future I/O. Continual I/O error counters live in `dvobj_priv` and are updated through helper calls.

Dependencies and integration: called by Realtek IO/HAL layers after `rtw_init_io_priv()` installs SDIO ops. Depends on Linux SDIO core and driver error accounting helpers.

Risks: many helpers return zero or no-op when `bSurpriseRemoved` is set, which can look like success to callers. 8-bit and bulk paths do not retry like 32-bit paths. Caller-provided buffers must be DMA-safe for CMD53 as documented. Incorrect IRQ-thread tagging could deadlock through recursive host claims.

Test signals: test byte and bulk reads/writes, 1/2-byte CMD53 fallbacks, host-claim suppression inside IRQ handler, retry behavior for transient `sdio_readl/writel` failures, continual I/O error threshold, and surprise removal errors `-ESHUTDOWN`/`-ENODEV`.
