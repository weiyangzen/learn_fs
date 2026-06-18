# sources/distributed-fs/ceph-client/drivers/spi/spi-davinci.c

## Purpose

`spi-davinci.c` is the TI DaVinci/DA8xx/Keystone SPI master driver. It uses `spi_bitbang` orchestration with controller-specific register programming, GPIO or native chip select, polled/interrupt/DMA transfer modes, per-device timing configuration, and OF or legacy platform data.

## Important APIs, Types, and Functions

`struct davinci_spi` stores the bitbang controller, clock, MMIO base/physical base, IRQ, completion, TX/RX pointers, word counts, DMA channels, platform data, byte-access callbacks, per-CS bytes-per-word cache, and prescaler limit. Important functions include `davinci_spi_setup_transfer()`, `davinci_spi_setup()`, `davinci_spi_chipselect()`, `davinci_spi_bufs()`, `davinci_spi_process_events()`, `davinci_spi_irq()`, DMA callbacks, `davinci_spi_request_dma()`, `spi_davinci_get_pdata()`, `davinci_spi_probe()`, and `davinci_spi_remove()`.

## Control Flow

Probe gets platform data or OF match data, allocates per-CS byte-size cache, maps registers, requests a threaded IRQ with a dummy thread function, enables the clock, configures SPI controller and bitbang callbacks, optionally requests DMA channels, resets the SPI module, programs pins, interrupt level, default CS, master/clock/powerdown bits, and starts `spi_bitbang`.

Setup configures native CS pin function, READY and loopback bits, and per-device OF config such as `ti,spi-wdelay`; if both DMA channels exist the device config defaults to DMA. Transfer setup selects 8- or 16-bit buffer callbacks, computes prescaler, programs SPIFMT and SPIDELAY. `davinci_spi_bufs()` initializes counts, enables the module, uses DMA when allowed or starts PIO/IRQ/polling by writing the first word, waits for completion or polls events, disables interrupts and module, checks error flags, and returns transferred length.

## State and Persistence Behavior

Per-device `struct davinci_spi_config` may be allocated from OF and stored in `spi->controller_data` until cleanup. Controller state persists in hardware registers, DMA channel handles, per-CS bytes-per-word cache, and bitbang workqueue state. There is no file-backed persistence; SPI transfers affect attached devices.

## Dependencies and Integration Points

The driver depends on platform/OF data, `spi_bitbang`, clocks, GPIO descriptors, IRQs, DMA engine slave channels, EDMA platform types, MMIO accessors, completions, and the SPI core. Compatible data selects IP version and prescaler limits.

## Risks and Edge Cases

`davinci_spi_get_prescale()` rejects prescalers below `prescaler_limit`, which is version-specific and easy to misconfigure. DMA eligibility rejects vmalloc buffers but assumes prepared SPI SG lists are valid. RX-only DMA aliases TX SG to RX SG to keep reloads synchronized, which is clever but fragile. Timeout calculation derives from speed and length and may underflow to too-short waits for small/fast transfers. Error handling clears interrupts after wait but DMA descriptors may need explicit termination on timeout. The threaded IRQ dummy exists solely to satisfy the API.

## Test Signals

Tests should cover OF and platform-data probe, all compatible versions, prescaler boundaries, CPOL/CPHA/LSB/loopback/READY/CS_WORD modes, GPIO and native CS, 8- and 16-bit buffers, polling, IRQ, and DMA modes, RX-only DMA with many SG entries, timeout/error flag handling, DMA request defer/failure, setup/cleanup of OF controller_data, and remove cleanup of bitbang and DMA channels.
