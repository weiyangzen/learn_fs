# sources/distributed-fs/ceph-client/drivers/iio/dummy/iio_simple_dummy.h

Purpose: shared header that joins the simple dummy core, event support, and buffer support.

Important APIs/types/functions: `struct iio_dummy_state` is the central per-device state for cached DAC/ADC/accel/activity/steps values, mutex, fake registers, and optional event fields. Event declarations cover config/value read/write plus register/unregister hooks. Buffer declarations cover configure/unconfigure hooks. `enum iio_simple_dummy_scan_elements` gives stable scan indices for buffered data.

Control flow: compile-time `CONFIG_IIO_SIMPLE_DUMMY_EVENTS` and `CONFIG_IIO_SIMPLE_DUMMY_BUFFER` select real declarations or inline no-op stubs. This lets `iio_simple_dummy.c` call event and buffer hooks unconditionally while Kbuild controls linked objects.

State/persistence: the header describes state layout; actual initialization occurs in the C files. Optional event fields exist only in event-enabled builds, so structure size and available callbacks vary by configuration.

Dependencies/integration: includes kernel headers and forward-declares `struct iio_dev`, `struct iio_dummy_regs`, and calibration structs. It is the local contract between dummy core, event, and buffer modules.

Risks: because optional fields are compile-time gated, code touching event state must remain under the same config. Scan index changes must stay aligned with `iio_dummy_channels[]` and buffer `fakedata[]`. Test signals include builds with neither option, only events, only buffer, and both, plus buffer scan data matching the enum order.
