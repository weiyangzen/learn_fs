# sources/distributed-fs/ceph-client/drivers/iio/gyro/itg3200_buffer.c

## Purpose
Buffer and trigger support for the ITG3200 I2C gyroscope driver.

## Important APIs, Types, And Functions
Functions include `itg3200_read_all_channels`, `itg3200_trigger_handler`, `itg3200_buffer_configure`, `itg3200_buffer_unconfigure`, `itg3200_data_rdy_trigger_set_state`, `itg3200_probe_trigger`, and `itg3200_remove_trigger`.

## Control Flow
Core probe calls buffer configure and, when IRQ is present, trigger probe. Trigger setup allocates an IIO trigger, requests the data-ready IRQ, registers the trigger, and assigns it as default. Trigger handler bulk-reads temp and XYZ samples and pushes them with timestamp.

## State And Persistence
The trigger state toggles `ITG3200_IRQ_DATA_RDY_ENABLE` in the IRQ config register. Trigger allocation, IRQ registration, and default trigger reference are stored in `struct itg3200`.

## Dependencies And Integration Points
Depends on I2C transfer helpers from ITG3200 core/header, IIO triggered buffers, IIO triggers, and a hardware IRQ.

## Risks
Uses non-devm `iio_trigger_alloc`, `request_irq`, and cleanup, so error paths must stay exact. `itg3200_read_all_channels` returns raw `i2c_transfer` count, and the handler only treats negative as failure. No scan-mask selective reads; it always reads all channels.

## Test Signals
Probe with IRQ, enable/disable trigger, capture buffered samples, verify remove frees IRQ and trigger, and test buffer operation when no IRQ is configured.
