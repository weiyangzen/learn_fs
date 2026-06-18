# sources/distributed-fs/ceph-client/drivers/iio/imu/adis.c

Purpose: Shared SPI helper library for Analog Devices ADIS16xxx IIO devices. It implements paged register access, bit updates, debugfs access, IRQ control, status checking, reset/startup/self-test, single conversions, and `struct adis` initialization.

Important APIs/types/functions: `__adis_write_reg()` and `__adis_read_reg()` perform unlocked multi-byte SPI register transactions with optional page switching and configured delays. `__adis_update_bits_base()` read-modify-writes fields. `__adis_enable_irq()` toggles data-ready interrupt via device-specific callback, unmasked IRQ handling, or MSC control register. `__adis_check_status()` reads diagnostic status and logs per-bit messages. `__adis_reset()`, `adis_self_test()`, and `__adis_initial_startup()` establish known device state, including optional reset GPIO and product-id warning. `adis_single_conversion()` reads a channel and sign-extends/masks it. `adis_init()` validates config, initializes locks, SPI delay defaults, ops, current page, and IIO drvdata.

Control flow: Device drivers call `adis_init()` first, then startup and buffer setup helpers. Register read/write helpers select page if needed, build SPI message sequences, and update `current_page` after success. Startup prefers hardware reset GPIO if present; otherwise software reset, then self-test, optional IRQ disable, and optional product-id check.

State and persistence: `struct adis` stores SPI device, config, ops, current page, buffers, and `state_lock`. Hardware state includes selected page, diagnostic status, IRQ enable, reset/self-test side effects, and device registers.

Dependencies and integration points: Uses SPI core, GPIOD reset, IIO device drvdata, debugfs, and public ADIS headers. Exports symbols in `IIO_ADISLIB` / one reset symbol appears exported under `IIO_ADIS_LIB`.

Risks: Register helpers are explicitly unlocked; callers must use `state_lock` or `adis_dev_auto_scoped_lock`. Page cache correctness depends on all register access going through helpers. Namespace spelling inconsistency for `__adis_reset` export (`IIO_ADIS_LIB` vs `IIO_ADISLIB`) is notable. Product-id mismatch only warns. Self-test cleanup ignores errors when clearing non-autoclear self-test bits.

Test signals: Unit-style SPI mock tests for read/write sizes and paging, startup with/without reset GPIO, diagnostic bit logging, IRQ enable paths, single conversion sign extension, and build/module namespace checks for all ADIS consumers.
