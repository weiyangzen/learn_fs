# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54spi.c

## Purpose
This file implements the Prism54 SPI frontend for stlc45xx-class devices. It handles SPI register access, GPIO power/IRQ control, firmware and EEPROM loading, firmware upload through SPI DMA registers, interrupt/workqueue processing, RX/TX transfers, and SPI driver probe/remove.

## Important APIs, Types, and Functions
- SPI primitives are `p54spi_spi_read()`, `p54spi_spi_write()`, `p54spi_read32()`, `p54spi_write16()`, and `p54spi_write32()`.
- Firmware/EEPROM setup is handled by `p54spi_request_firmware()`, `p54spi_request_eeprom()`, and `p54spi_upload_firmware()`.
- Power/interrupt helpers include `p54spi_power_on()`, `p54spi_power_off()`, `p54spi_wakeup()`, `p54spi_sleep()`, `p54spi_int_ack()`, and `p54spi_int_ready()`.
- Runtime data paths are `p54spi_rx()`, `p54spi_tx_frame()`, `p54spi_wq_tx()`, `p54spi_op_tx()`, and `p54spi_work()`.
- p54 common callbacks are `p54spi_op_start()` and `p54spi_op_stop()`.
- `p54spi_probe()` and `p54spi_remove()` manage SPI device lifecycle.

## Control Flow
Probe allocates common p54 hardware, sets 16-bit SPI mode at 24 MHz, requests power and IRQ GPIOs from module parameters, installs an edge IRQ initially disabled, initializes work/completion/list/mutex/spinlock state, sets bus callbacks, requests firmware, parses EEPROM from user firmware or optional built-in fallback, and registers common mac80211 hardware.

Start locks the bus mutex, marks firmware booting, powers on the chip, uploads firmware in chunks via SPI DMA write registers, enables host interrupts, releases the mutex, waits up to two seconds for READY completion from the workqueue, and verifies `FW_STATE_READY`. The IRQ handler only queues work. Work reads host interrupt bits, handles READY state transitions, receives update/SW-update frames, and drains queued TX packets. TX queues SKBs into a list embedded in `rate_driver_data`, then work wakes the chip, writes DMA payload to firmware memory at the p54 request ID, waits for WR_READY, acknowledges, frees control SKBs when appropriate, and sleeps the chip. Stop powers off, clears pending TX list, marks firmware off, and cancels work.

## State and Persistence Behavior
Persistent SPI state includes GPIO numbers, firmware pointer, `fw_state`, work item, mutex, completion, TX list, and TX spinlock. The device is power-cycled across start/stop. Queued TX entries are stored in SKB control metadata and `tx_pending`; stop drops the list without walking/freeing entries, relying on higher-level queue stoppage and existing ownership assumptions.

## Dependencies and Integration Points
It depends on SPI core, firmware loader, GPIO/IRQ APIs, p54 common APIs, LMAC macros, and optional `p54spi_eeprom.h`. It registers as `p54spi` and aliases several SPI device names.

## Risks and Edge Cases
GPIOs are module parameters rather than platform data, which is fragile. SPI helpers ignore `spi_sync()` return values, so bus errors may be hidden. Firmware upload uses `BUG_ON(fw_len != 0)` after loop accounting. RX reserves four extra bytes for firmware alignment bugs. TX failure frees the SKB and aborts workqueue drain. Work serialization relies on the mutex; TX list ownership relies on spinlock and SKB lifetime. Optional fallback EEPROM may be generic and unsuitable for all boards.

## Test Signals
Signals include SPI probe, firmware parse/upload, READY interrupt completion, EEPROM parse, mac80211 registration, RX/TX through SPI DMA, clean power cycling, IRQ work scheduling, and fallback EEPROM behavior when configured.
