# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/hw/mmp_spi.c

## Purpose
Registers and implements an SPI master backed by the MMP LCD controller's smart-panel/SPI port so panel drivers can send initialization commands through the display controller.

## Important APIs, Types, and Functions
- `lcd_spi_write()` writes one 8/16/32-bit word to `LCD_SPU_SPI_TXDATA`, starts transfer via `LCD_SPU_SPI_CTRL`, polls SPI interrupt status, and clears the start bit/status.
- `lcd_spi_setup()` configures bit count, clock count, chip select, SPI enable, 3-wire/4-wire mode, and I/O pad mode.
- `lcd_spi_one_transfer()` iterates spi_message transfers and writes each word according to `spi->bits_per_word`.
- `lcd_spi_register()` allocates a `spi_controller`, stores the LCD register base in controller private data, sets bus number 5, and registers the controller.

## Control Flow
`mmp_ctrl.c` calls `lcd_spi_register()` after controller/path initialization. SPI core calls setup for devices, then transfer for messages. Each transfer word is synchronously written and polled until the SPI IRQ bit appears or a timeout expires; completion callback is invoked at the end of the message.

## State and Persistence
The SPI controller stores only a pointer to the LCD controller MMIO base in its private data. Hardware SPI control and I/O pad registers persist in the LCD controller. No unregister path is provided in this source.

## Dependencies and Integration Points
Depends on `mmp_ctrl.h`, Linux SPI core, I/O accessors, and the controller driver's `mmphw_ctrl`. Consumed by panel drivers such as `tpo_tj032md01bw.c`.

## Risks
The transfer implementation ignores `lcd_spi_write()` return values, always sets `m->status = 0`, and calls completion even after timeouts. It uses legacy `ctlr->transfer` rather than newer queued transfer hooks. The fixed bus number 5 can conflict in unusual systems. No cleanup/unregister path appears in the controller remove flow.

## Test Signals
Validate SPI controller registration, panel `spi_setup()` with 16-bit words, visible writes to `LCD_SPU_SPI_CTRL/TXDATA`, timeout logging when IRQ never arrives, and correct failure propagation once fixed. Panel init command traces are practical integration tests.
