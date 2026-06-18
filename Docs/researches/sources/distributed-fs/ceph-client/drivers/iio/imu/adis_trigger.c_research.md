# Research: sources/distributed-fs/ceph-client/drivers/iio/imu/adis_trigger.c

Purpose: shared trigger setup for ADIS16xxx IIO devices. It translates IIO trigger enable/disable calls into ADIS IRQ enable operations and validates/request IRQs for data-ready or FIFO-watermark lines.

Important APIs, types, and functions: `adis_data_rdy_trigger_set_state()` calls `adis_enable_irq()`. `adis_trigger_ops` exposes that callback to IIO. `adis_validate_irq_flag()` normalizes and validates IRQ trigger flags, including FIFO versus non-FIFO polarity requirements and `IRQF_NO_AUTOEN` for unmasked data-ready lines. `devm_adis_probe_trigger()` allocates, configures, requests, and registers the trigger.

Control flow: setup allocates a named trigger using the IIO device ID, stores `struct adis` as trigger private data, validates IRQ flags, requests either threaded IRQ for FIFO devices or normal IRQ for data-ready devices, then registers the trigger with devm cleanup. Runtime trigger state changes call back into the driver or generic ADIS IRQ enable path.

State and persistence: sets `adis->trig` and may mutate `adis->irq_flag` by adding default rising-edge behavior or `IRQF_NO_AUTOEN`. No hardware state persists here except what `adis_enable_irq()` toggles through the underlying ADIS ops.

Dependencies and integration: consumed by `adis_buffer.c` and ADIS drivers; depends on SPI IRQ presence, IIO trigger core, `iio_trigger_generic_data_rdy_poll`, and ADIS metadata flags `unmasked_drdy` and `has_fifo`.

Risks: wrong IRQ polarity is rejected differently for FIFO level-triggered devices versus edge-triggered non-FIFO devices. Missing IRQ defaults to no trigger setup at the caller layer. Unmasked DRDY lines require `IRQF_NO_AUTOEN` to prevent interrupts before the buffer path is ready.

Test signals: validate default IRQ flags, invalid edge/level combinations, FIFO threaded request path, non-FIFO request path, trigger enable/disable calling `adis_enable_irq()`, and probe behavior when IRQ request or trigger registration fails.
