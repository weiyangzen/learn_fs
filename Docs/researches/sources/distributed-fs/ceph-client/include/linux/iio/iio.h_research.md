<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/iio.h -->
# sources/distributed-fs/ceph-client/include/linux/iio/iio.h

Purpose: Main Industrial I/O kernel interface for declaring devices, channels, events, buffers, triggers, value formats, registration, and common helpers.

Important APIs/types/functions: Key types include `struct iio_chan_spec`, `iio_scan_type`, `iio_event_spec`, `iio_info`, `iio_buffer_setup_ops`, and `iio_dev`. Helpers cover enum/ext-info attributes, mount matrices, channel capability checks, timestamps, device registration/devm registration, event push, direct/buffer mode locking, driver data, private data, scan type lookup, active channel iteration, value formatting/parsing, ACPI mount data, and unit conversions.

Control flow: Drivers allocate an `iio_dev`, fill channel/spec/info callbacks, register it, then IIO core dispatches sysfs reads/writes, event config, buffer setup, trigger validation, scan updates, and debugfs access through the declared callbacks.

State/persistence: `struct iio_dev` persists for the device lifetime and stores modes, buffer, scan masks, trigger/poll functions, channels, label/name, callback tables, and private data. Mode guards protect direct reads versus active buffers.

Dependencies/integration: Integrates device model, cdev, cleanup guards, IIO UAPI types, buffers, triggers, ACPI, sysfs, debugfs, and DMA/timestamp alignment.

Risks: Incorrect scan formats, mask lengths, mode locking, or callback formats create ABI breakage, data corruption, or races between sysfs and buffered capture.

Test signals: Device registration/remove, sysfs raw/scale/available paths, event push/read, direct-mode lock failures while buffers run, buffer timestamp alignment, ext scan type validation, and ACPI orientation parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/iio/iio.h -->
