# sources/distributed-fs/ceph-client/drivers/iio/dummy/iio_simple_dummy.c

Purpose: reference IIO software device showing direct-mode channels, sysfs attributes, optional events, and optional buffers without real hardware. It is both documentation and a userspace test target.

Important APIs/types/functions: `iio_dummy_channels[]` defines single-ended voltage, differential voltage, accel, timestamp, DAC output, steps, and activity channels. `struct iio_dummy_state` is declared in the header and initialized by `iio_dummy_init_device()`. `iio_dummy_read_raw()` and `iio_dummy_write_raw()` implement raw, processed, scale, offset, calibration, sampling-frequency, enable, and height attributes. `iio_dummy_probe()` and `iio_dummy_remove()` implement `iio_sw_device_ops`.

Control flow: software-device probe allocates `iio_sw_device` and `iio_dev`, initializes caches, duplicates the instance name, registers optional events and buffer support, then registers the IIO device. Direct raw/processed reads claim direct mode before reading cached state. Writes mutate cached state with mutex guards for most fields. Remove unregisters IIO, cleans buffer/events, frees name and device structures.

State/persistence: all sensor values are RAM caches with deterministic defaults: DAC 0, ADC 73/33/-34, accel 34, bias -7, default calibration scale, steps 47, running 98, walking 4. No hardware or persistent storage exists.

Dependencies/integration: integrates with `IIO_SW_DEVICE`, IIO core, sysfs, optional event callbacks, optional triggered buffers, and configfs-like software device group naming via `iio_swd_group_init_type_name()`.

Risks: the driver is intentionally permissive and illustrative, not strict hardware emulation. Some writes clamp activity to 0..100, but other fields accept arbitrary values. A few writes lack locking even though neighboring state uses locks. Test signals include software-device create/remove, all channel sysfs names, direct-mode busy behavior while buffers are active, optional event/buffer builds, and memory cleanup across probe failures.
