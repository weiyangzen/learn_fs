# sources/distributed-fs/ceph-client/drivers/hwmon/iio_hwmon.c

## Purpose

`iio_hwmon.c` is a bridge driver that exposes IIO consumer channels through the hwmon sysfs ABI. It dynamically creates `*_input` and optional `*_label` attributes for voltage, temperature, current, power, and relative-humidity IIO channels.

## Important APIs, Types, and Functions

`struct iio_hwmon_state` stores the acquired IIO channel array, channel count, hwmon attribute group, group pointer array, and attribute pointer array. `iio_hwmon_read_val()` obtains channel type and reads processed values, using `iio_read_channel_processed_scale(..., 1000)` for power so milliwatts become microwatts. `iio_hwmon_read_label()` delegates labels to `iio_read_channel_label()`. `iio_hwmon_probe()` acquires all channels, counts them, allocates dynamic sensor attributes, names them with hwmon prefixes, and registers a hwmon device.

## Control Flow

Probe calls `devm_iio_channel_get_all()`, deferring if no IIO provider is ready. It counts channels until the sentinel `indio_dev` is null, allocates room for input plus label attributes, and iterates each channel. Supported IIO types map to hwmon prefixes: voltage to `in`, temperature to `temp`, current to `curr`, power to `power`, and relative humidity to `humidity`. For each channel it creates a read-only input attribute and probes for a label using a temporary page buffer; if a label is available it adds a read-only label attribute. The hwmon name comes from the firmware node path with dashes replaced by underscores, or `iio_hwmon` without firmware metadata.

## State and Persistence Behavior

There is no sensor value cache or writable state. All attributes are devm-managed and values are read live from the IIO channel on each sysfs access. The temporary label buffer is explicitly freed before hwmon registration.

## Dependencies and Integration Points

The driver binds platform devices compatible with `iio-hwmon`, consumes IIO channels through the IIO consumer API, and exposes them using classic hwmon sysfs groups. It relies on unit compatibility between IIO processed values and hwmon units, with an explicit power conversion.

## Risks and Edge Cases

Unsupported IIO channel types abort probe entirely rather than skipping only that channel. The comment notes that IIO and hwmon base-unit assumptions need verification for new channel types. Label detection calls `iio_read_channel_label()` during probe and later again during sysfs reads; providers with transient label errors may expose no label. Attribute numbering is per type and order-dependent on the IIO channel list. A device with zero channels registers an empty hwmon group.

## Test Signals

Test probe deferral, supported type naming and numbering, unsupported type rejection, power scaling from milliwatts to microwatts, label presence and absence, firmware-node-derived hwmon name sanitization, and live propagation of IIO provider read errors through sysfs.
