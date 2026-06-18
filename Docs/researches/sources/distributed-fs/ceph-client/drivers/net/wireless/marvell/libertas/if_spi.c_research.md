# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/if_spi.c

## Purpose
Implements the SPI transport for Marvell Libertas WLAN cards. It initializes the SPI interface unit, loads helper and main firmware, handles firmware command/data/event movement through SPU registers, provides Libertas host-to-card callbacks, and registers a `spi_driver`.

## Important APIs And Functions
Low-level SPU helpers are `spu_write()`, `spu_read()`, `spu_read_u16()`, `spu_read_u32()`, `spu_wait_for_u16()`, `spu_wait_for_u32()`, `spu_set_interrupt_mode()`, `spu_get_chip_revision()`, and `spu_init()`. Firmware loading is split across `if_spi_prog_helper_firmware()`, `if_spi_prog_main_firmware_check_len()`, and `if_spi_prog_main_firmware()`. Runtime transfer handlers include `if_spi_c2h_cmd()`, `if_spi_c2h_data()`, `if_spi_h2c()`, `if_spi_e2h()`, `if_spi_host_to_card_worker()`, and `if_spi_host_to_card()`. Probe/remove and PM are handled by `if_spi_probe()`, `libertas_spi_remove()`, `if_spi_suspend()`, and `if_spi_resume_worker()`.

## Control Flow And State
All SPI bus access after firmware load is serialized through `card->workqueue`; IRQ context only queues work. Commands and data have separate packet lists protected by `buffer_lock`. `priv->dnld_sent` is updated when Libertas enqueues a command or data frame, while the worker calls `lbs_host_to_card_done()` when the card reports download readiness. Firmware load uses scratch registers, CRC retry handling, and a magic value in scratch 4 for success. Suspend disables IRQ, tears down platform resources, and resume re-runs platform setup and card init in worker context.

## Dependencies And Integration
Depends on Linux SPI, `linux/spi/libertas_spi.h` platform data, firmware loader, and full Libertas core callbacks. It uses `lbs_get_firmware()`, `lbs_add_card()`, `lbs_start_card()`, `lbs_process_rxed_packet()`, `lbs_queue_event()`, and command response notification.

## Risks And Test Signals
Risks include strict even-byte/word alignment, timing delays between SPU transactions, dummy-clock versus timed-delay platform behavior, command/data queue races, and firmware CRC retry exhaustion. Test signals include chip id/revision detection, helper/main firmware download, interrupt-driven command response and data RX, event delivery, TX wake after command/data ready bits, suspend/resume, and platform setup/teardown ordering.
