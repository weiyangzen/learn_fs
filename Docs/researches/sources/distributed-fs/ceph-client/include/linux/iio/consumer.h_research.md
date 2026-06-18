# `sources/distributed-fs/ceph-client/include/linux/iio/consumer.h`

Purpose: in-kernel IIO consumer interface for acquiring channels, callback buffers, reading/writing raw/processed/channel attributes, converting raw values, and querying extended info.

Important APIs/types/functions: `struct iio_channel`, channel get/release/devm/get-all/fwnode variants, callback buffer get/start/stop/watermark/release and underlying channel/device accessors, raw/average/processed reads, processed scaling, attribute read/write, raw write, min/max/available reads, channel type/offset/scale, `iio_multiply_value`, `iio_convert_raw_to_processed`, ext-info count/read/write, and label read.

Control flow and state: consumers acquire channel descriptors from mapping or firmware lookup, use direct read/write APIs or callback buffers, and release explicitly or through devm. Callback buffers register a callback that must be safe in any context and can stream channels from one provider device.

Dependencies/integration: depends on IIO types and provider channel specs, device/fwnode mapping, and IIO buffer infrastructure. Used by power, thermal, hwmon, regulator, and sensor consumers.

Risks: channel acquisition can return `ERR_PTR`; callback buffers cannot mux multiple provider devices; raw-to-processed conversions depend on offset/scale value types and can lose precision; callback context may not sleep; devm and manual release must not mix incorrectly.

Test signals: mapping-based and fwnode channel lookup, get-all sentinel termination, devm cleanup, raw/processed/scale/offset reads, write paths, available range/list returns, callback buffer streaming/watermark, ext-info and label reads, and absent provider errors.
