# sources/distributed-fs/ceph-client/drivers/mmc/host/moxart-mmc.c Research

## sources/distributed-fs/ceph-client/drivers/mmc/host/moxart-mmc.c

### Purpose
`moxart-mmc.c` is a platform MMC host driver for MOXA ART/Faraday FTSdc010-style controllers. It implements a relatively synchronous request path around a memory-mapped command/data FIFO controller, optional DMA-engine channels, card-change interrupt handling, power/clock/bus-width programming, and basic write-protect reporting.

### Important APIs, Types, And Functions
The core state is `struct moxart_host`, which keeps the MMIO base, physical register address, DMA channels/descriptors, current MMC request, scatterlist cursor, completions for DMA/PIO, transfer length/remain counters, FIFO width, timeout/rate/sysclk, and removal/DMA flags. MMC callbacks are `moxart_request()`, `moxart_set_ios()`, and `moxart_get_ro()` through `moxart_ops`. Important helpers are `moxart_prepare_data()`, `moxart_send_command()`, `moxart_transfer_dma()`, `moxart_transfer_pio()`, `moxart_irq()`, `moxart_wait_for_status()`, and scatterlist cursor helpers.

### Control Flow
Probe allocates the MMC host, maps the resource, parses DT, reads the clock, discovers FIFO width from `REG_FEATURE`, tries to request `"tx"` and `"rx"` DMA channels, configures DMA slave addresses if available, sets MMC limits and 4-bit capability, resets the controller, requests the IRQ, and registers the host. A request initializes completions, stores `host->mrq`, checks the card-detect status bit, prepares data if present, sends the command by polling response status, then either performs DMA synchronously or waits for PIO completion driven by FIFO interrupts. After transfer, it checks removal, waits for data completion/error status, sets data errors, sends an explicit stop command if present, unlocks, and calls `mmc_request_done()`. The IRQ records card removal, terminates DMA if needed, signals detect change, and services FIFO under/overrun bits for PIO transfers.

### State, Persistence, And Dependencies
Persistent driver state includes current request, SG cursor, `data_len`, `data_remain`, `rate`, `fifo_width`, DMA availability, and `is_removed`. Hardware state is programmed through command, argument, response, data-control/timer/length, interrupt-mask, power-control, clock-control, and bus-width registers. The driver depends on platform DT resources, `mmc_of_parse()`, clock framework, DMA engine, DMA mapping, completions, spinlocks, and MMC core helpers.

### Integration Points
The OF match table binds `"moxa,moxart-mmc"` and `"faraday,ftsdc010"`. DMA channel names are `"tx"` and `"rx"`; when either is missing, the driver falls back to PIO unless probe deferral is required. The MMC core receives CMD/data completions through synchronous request completion. Card detection is controller-internal through `CARD_CHANGE`/`CARD_DETECT` rather than an MMC GPIO helper, while write protect is read from `WRITE_PROT`.

### Risks
The request path holds the host spinlock while polling command/data status, but drops it for DMA/PIO waits; races around card removal, `host->mrq`, and completions are therefore important. DMA completion timeout is not explicitly checked before setting `bytes_xfered = data_len`, so DMA hangs may be underreported until later data status. PIO assumes 32-bit word access and power-of-two block sizes enforced by `BUG_ON()`. Card-detect logic treats `CARD_DETECT` during request as timeout, so polarity assumptions must match hardware. Removal sets `host->mrq = NULL` in IRQ, which can race with in-flight PIO waiting. There is no runtime PM or regulator handling.

### Test Signals
Run probe with and without DMA channels, 1-bit and 4-bit bus modes, power off/on, write-protect readout, card insertion/removal during PIO and DMA, single/multi-block reads and writes, data CRC/timeout injection, stop-command paths, and transfer sizes below/above FIFO width. DMA timeout behavior should be checked carefully because completion timeout return value is ignored.
