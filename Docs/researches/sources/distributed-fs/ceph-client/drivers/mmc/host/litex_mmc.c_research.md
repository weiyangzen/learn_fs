# sources/distributed-fs/ceph-client/drivers/mmc/host/litex_mmc.c

## Purpose

`litex_mmc.c` implements an MMC host driver for LiteX LiteSDCard gateware. It exposes LiteX PHY/core/reader/writer/IRQ CSR regions as an MMC host, using LiteX CSR accessors and DMA-capable memory addresses for block transfers. The driver is tailored to SD cards, forcing 4-bit mode and disabling SDIO/MMC card types through capabilities.

## Important APIs, Types, And Functions

- Register macros describe LiteX PHY, core command/data event, reader DMA, writer DMA, and interrupt CSR offsets.
- Protocol constants encode LiteSDCard command transfer direction, response length, event bits, polling timeouts, and IRQ bits.
- `struct litex_mmc_host` stores mapped CSR regions, coherent bounce buffer and DMA address, command completion, IRQ, reference and SD clock values, raw response words, relative card address, and state flags for bus-width injection and APP_CMD tracking.
- `litex_mmc_sdcard_wait_done()` polls event registers and maps done, write error, timeout, and CRC bits to Linux errors.
- `litex_mmc_send_cmd()` writes command argument/configuration, optionally waits for IRQ completion, validates command and data event registers, copies response words, tracks RCA and APP_CMD state, and waits for reader/writer DMA done.
- `litex_mmc_set_bus_width()` injects `APP_CMD` and `SD_APP_SET_BUS_WIDTH` before first data transfer because the hardware only supports 4-bit transfers and needs that programming earlier than the generic core may do it.
- `litex_mmc_do_dma()` maps the request scatterlist. If a single DMA segment is available it programs hardware directly; otherwise it uses a coherent bounce buffer and copies write/read data.
- `litex_mmc_request()` sequences optional SBC, early bus-width setup, DMA programming, command retry, response translation, optional stop command, DMA unmap, data copy-back, and request completion.
- `litex_mmc_irq_init()` optionally enables card-detect and command-done IRQs; otherwise it marks the host as polling.
- `litex_mmc_probe()` allocates the host, maps named resources, configures DMA mask/bounce buffer, initializes capabilities and limits, parses DT, and adds the host.

## Control Flow And State

The request path is synchronous from the MMC core perspective. `litex_mmc_request()` first verifies card presence, sends SBC if present, performs one-time 4-bit bus setup before data, programs DMA reader/writer, sends the command with retries, translates LiteX response layout to MMC response layout, sends a stop if needed, unmaps DMA, copies bounce reads back, and calls `mmc_request_done()`.

For commands with data or DAT0 busy and a valid IRQ, `litex_mmc_send_cmd()` enables `CMD_DONE` and waits on `host->cmd_done`; otherwise it polls event registers. Card-detect IRQs call `mmc_detect_change()`. Persistent state includes `rca`, `app_cmd`, and `is_bus_width_set`, which allow command injection to preserve SD application-command ordering and reset bus-width setup after card removal or command errors.

## Dependencies And Integration Points

The driver depends on LiteX CSR helpers (`litex_read8/16/32`, `litex_write*`), Linux platform resources by name (`phy`, `core`, `reader`, `writer`, optional `irq`), DMA mapping/coherent allocation, clocks, MMC/SD constants, OF match `"litex,mmc"`, and the MMC core. It uses standard regulator parsing but defaults to 3.3 V if no OCR is available.

## Risks And Edge Cases

- The hardware only supports 4-bit SD-card operation. The driver forcibly sets `MMC_CAP_4_BIT_DATA`, clears 8-bit, and sets `MMC_CAP2_NO_SDIO | MMC_CAP2_NO_MMC`; integration expecting SDIO/MMC will not work.
- `litex_mmc_do_dma()` maps the SG list before deciding direct versus bounce. It relies on later unconditional `dma_unmap_sg()` whenever data exists.
- Bounce buffer size is `mmc->max_req_size * 2` based on defaults; request limit comments warn that changing block count requires recalculating size.
- `wait_for_completion()` has no explicit timeout; command event register polling after wake still catches device-side errors, but lost IRQs could block if IRQ mode is used.
- `is_bus_width_set` is reset on command errors and card removal, which is required but can add hidden command traffic before data transfers.

## Test Signals

Tests should cover polling and IRQ mode, card insertion/removal, first data transfer bus-width injection, APP_CMD ordering around ACMD6, direct single-SG DMA and bounce-buffer multi-SG paths, read copy-back, command retry behavior, optional SBC/stop handling, response layouts for short and long responses, and DT resource naming errors.
