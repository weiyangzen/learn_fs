# sources/distributed-fs/ceph-client/drivers/hid/hid-goodix-spi.c

Implements a Goodix GT7986U SPI transport that exposes touchscreen firmware as a HID device. It performs SPI register access, retrieves HID descriptors, implements raw HID get/set report commands, delivers IRQ-driven input reports, and handles suspend/resume power commands.

`struct goodix_ts_data` owns the SPI device, child HID device, HID descriptor, optional reset GPIO, report address, state flags, request mutex, event buffer, and aligned transfer buffer. `goodix_spi_read()`/`goodix_spi_write()` implement the Goodix prefixed register protocol. `goodix_dev_confirm()` verifies communication after reset. `goodix_hid_parse()`, `goodix_hid_start()`, `goodix_hid_open()`, `goodix_hid_close()`, and `goodix_hid_raw_request()` implement `goodix_hid_ll_driver`. `goodix_hid_irq()` reads event packages and calls `hid_input_report()`.

Probe configures SPI mode, allocates buffers, gets reset GPIO, confirms the device, waits for firmware boot, creates a `BUS_SPI` HID device, and registers a threaded IRQ. Raw GET/SET report operations build i2c-hid-like command packets and serialize with `hid_request_lock`. IRQ delivery is gated by `GOODIX_HID_STARTED`.

State is runtime-only: open/started flag, event buffer size, HID descriptor, and power state commands. Dependencies include SPI, HID low-level driver API, GPIO, IRQ, ACPI/OF/SPI matching, PM sleep ops, and unaligned helpers.

Risks include firmware-controlled package sizes, fixed temporary GET buffers, command/IRQ concurrency, and suspend/resume IRQ ordering. Test signals include descriptor parsing, hidraw GET/SET reports, IRQ coordinate and extra package delivery, buffer limit errors, suspend/resume, and removal with IRQ disabled.
