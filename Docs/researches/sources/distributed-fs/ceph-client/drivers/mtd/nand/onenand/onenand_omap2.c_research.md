# sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/onenand_omap2.c

## Purpose
`onenand_omap2.c` is the OMAP2/OMAP3 OneNAND platform glue. It maps the OneNAND memory window behind OMAP GPMC, optionally uses a GPIO interrupt for wait completion, optionally uses DMAengine for BufferRAM transfers, programs optimized GPMC/OneNAND timings, calls the generic `onenand_scan()`, and registers the MTD device.

## Important APIs, Types, and Functions
The central type is `struct omap2_onenand`, which embeds `struct mtd_info`, `struct onenand_chip`, GPMC chip-select state, physical base, optional interrupt GPIO, completions, and a DMA channel. Key functions are `omap2_onenand_probe()`, `omap2_onenand_remove()`, `omap2_onenand_shutdown()`, `omap2_onenand_wait()`, `omap2_onenand_set_cfg()`, `omap2_onenand_get_freq()`, and the DMA-backed `omap2_onenand_read_bufferram()` / `omap2_onenand_write_bufferram()`.

## Control Flow
Probe reads the DT `reg` property as the GPMC chip select, allocates state, maps the memory resource, obtains optional `int` GPIO, requests an IRQ when present, and installs `onenand.wait = omap2_onenand_wait`. It then requests a memcpy DMA channel; if available, it overrides BufferRAM read/write callbacks. After initializing `mtd.priv`, parent device, and OF node, it calls `onenand_scan()`. If the OneNAND version encodes a known frequency, it chooses latency, calls `gpmc_omap_onenand_set_timings()`, writes OneNAND sync/burst configuration, and finally calls `mtd_device_register()`.

`omap2_onenand_wait()` uses short polling for reset/preparing erase/verify erase, interrupt GPIO waits for non-read operations, and polling with interrupts disabled for reads. It checks ECC status on read completion, updates MTD ECC counters, and reports controller/timeout/write-protect errors. BufferRAM DMA paths use DMA only for aligned, DMA-addressable, sufficiently large transfers outside panic writes, with PIO fallback.

## State and Persistence
Persistent flash state is handled by the generic OneNAND core. This driver maintains volatile completions, optional DMA channel ownership, GPMC timing configuration, OneNAND SYS_CFG1 sync/burst mode, and a shutdown-time BufferRAM zeroing workaround to keep OMAP boot ROM detection stable after soft reset.

## Dependencies and Integration Points
It depends on OF platform matching `"ti,omap2-onenand"`, OMAP GPMC timing helpers, GPIO descriptors, DMAengine memcpy support, `linux/mtd/onenand.h`, and MTD registration. The generic core consumes the callbacks installed by this glue.

## Risks
Wait behavior mixes GPIO interrupts and polling and includes retry logic for long operations; false GPIO values or missed interrupts can cause timeouts. DMA fallback must preserve partial trailing bytes and avoid panic-write DMA. The write path calls `dma_unmap_page()` after `dma_map_single()`, which is suspicious in this source and should be checked against the kernel version's DMA API expectations. Incorrect GPMC timing or latency selection can produce intermittent data/ECC failures.

## Test Signals
Probe logs should show chip select, physical/virtual base, and DMA/PIO mode. Hardware tests should cover read/write/OOB/erase under DMA and PIO fallback, IRQ and no-IRQ configurations, panic write fallback, optimized timing logs, suspend/removal cleanup, and shutdown BufferRAM clearing behavior.
