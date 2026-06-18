# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-adc0832.c

Purpose: SPI IIO driver for TI ADC0831/ADC0832/ADC0834/ADC0838 8-bit ADCs. It exposes single-ended and differential channel combinations and supports triggered buffers.

Important APIs/types/functions: `struct adc0832` stores SPI device, vref regulator, mutex, mux-bit count, aligned scan buffer, and small TX/RX buffers. Core routines are `adc0831_adc_conversion()`, `adc0832_adc_conversion()`, `adc0832_read_raw()`, `adc0832_trigger_handler()`, and probe.

Control flow: probe chooses channel table and mux-bit width from the SPI ID, enables vref, installs a regulator cleanup action, sets up a triggered buffer, and registers IIO. Direct reads lock, emit the device-specific start/single-ended/differential/channel command, run a two-byte SPI transfer, and return the received 8-bit result. ADC0831 uses a special read-only two-byte transfer and skips the tri-state/leading-zero bits. Triggered buffering iterates active scan channels under the same mutex and pushes collected bytes plus timestamp.

State and persistence: persistent state is model selection, vref regulator state, mux width, shared SPI buffers, and mutex. Hardware has no long-lived register configuration; every conversion command encodes the selected channel/mode.

Dependencies and integration: depends on SPI, regulator `vref`, IIO direct and triggered-buffer APIs, OF/SPI IDs, and scan metadata for differential channels.

Risks: command bit packing depends on mux width and channel numbering; differential entries must match the datasheet's odd/sign and select bits. The triggered handler pushes the full maximum data buffer size rather than only populated bytes, depending on IIO scan alignment behavior. The driver does not call `iio_device_claim_direct()` for raw reads but uses its mutex to serialize command buffers.

Test signals: all four chip variants, single-ended and differential channel reads, ADC0831 special path, vref scale, triggered buffer with mixed active channels, SPI transfer failure handling, and regulator cleanup.
