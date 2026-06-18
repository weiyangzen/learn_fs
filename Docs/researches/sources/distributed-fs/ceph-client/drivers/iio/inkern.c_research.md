# sources/distributed-fs/ceph-client/drivers/iio/inkern.c

## Purpose

`inkern.c` is the in-kernel IIO consumer API implementation. It lets non-IIO kernel drivers discover producer channels by firmware references or board mapping tables, hold references to the backing `iio_dev`, and perform raw, processed, scale, min/max, write, ext-info, and label operations without going through userspace sysfs.

## Important APIs, Types, and Functions

- `struct iio_map_internal`, `iio_map_list`, and `iio_map_list_lock` store legacy `struct iio_map` consumer-to-provider mappings.
- `iio_map_array_register()`, `iio_map_array_unregister()`, and `devm_iio_map_array_register()` manage board maps.
- `fwnode_iio_channel_get_by_name()`, `iio_channel_get()`, `devm_iio_channel_get()`, `iio_channel_get_all()`, and their release/devm variants resolve single or all channels.
- `iio_read_channel_raw()`, `iio_read_channel_processed_scale()`, `iio_read_channel_attribute()`, `iio_read_avail_channel_attribute()`, min/max helpers, and write helpers dispatch into provider `iio_info` callbacks.
- `iio_multiply_value()` normalizes IIO value encodings for processed conversions and is exported to the IIO unit-test namespace.
- `iio_read_channel_ext_info()`, `iio_write_channel_ext_info()`, and `iio_read_channel_label()` expose channel extension metadata.

## Control Flow

Channel lookup prefers firmware: `iio_channel_get()` calls `fwnode_iio_channel_get_by_name()` for the consumer device, which matches `io-channel-names`, resolves `io-channels`, finds the producer on `iio_bus_type`, and translates the specifier via provider `fwnode_xlate` or the simple index translator. If direct node lookup returns `-ENODEV`, the code walks parents that advertise `io-channel-ranges`. Legacy fallback scans the global map list under `iio_map_list_lock`, grabs an IIO device reference, and optionally resolves the provider channel by datasheet name.

Reads and writes lock `to_iio_dev_opaque(...)->info_exist_lock` around provider callback access so unregister cannot race with consumers dereferencing `indio_dev->info`. Processed reads first prefer provider `IIO_CHAN_INFO_PROCESSED`, otherwise read raw, optionally add offset, multiply by scale, and apply the consumer scale argument.

## State and Persistence Behavior

Persistent state is the global mapping list, each `iio_channel`'s `indio_dev` reference, optional `consumer_data`, and selected `iio_chan_spec`. Devm helpers register cleanup actions so maps and acquired channels are released with the owner device. No readings are cached here; values are delegated to producer drivers.

## Dependencies and Integration Points

The file integrates with the IIO bus/core, firmware property APIs, `struct iio_info` provider callbacks, `iio_device_get()/put()`, device-managed cleanup, and legacy machine mapping via `<linux/iio/machine.h>`. It is the contract used by regulator, hwmon, thermal, power, and other kernel subsystems that consume IIO channels.

## Risks and Edge Cases

Firmware lookup distinguishes `-ENODEV`, `-ENOENT`, `-EINVAL`, and `-EPROBE_DEFER`; a wrong return path can accidentally suppress fallback or retry. `iio_channel_get_all()` must unwind partially acquired references on errors. The conversion path truncates some offset encodings before scaling. This source snapshot also shows suspicious duplicated statements/braces in `__fwnode_iio_channel_get_by_name()`, `iio_channel_release_all()`, and `iio_channel_read_max()`, which are compile or review signals rather than intended behavior.

## Test Signals

Use firmware and legacy-map tests for named, unnamed, parent-ranged, missing, and deferred channels. Exercise `read_raw`, `read_raw_multi`, processed conversion with offset/scale formats, available list/range min/max, devm cleanup, release-all unwind, ext-info buffer validation, and provider unregister racing with consumer reads.
