# sources/distributed-fs/ceph-client/drivers/iio/afe/iio-rescale.c

## Purpose
This file implements a virtual IIO Analog Front End that wraps a source IIO channel and exposes a rescaled channel. It models common passive/active analog transformations such as current sense amplifiers, shunts, voltage dividers, RTDs, and temperature transducers.

## Important APIs, Types, And Functions
The driver uses `struct rescale` and `struct rescale_cfg` from `<linux/iio/afe/rescale.h>`. `rescale_process_scale()` and `rescale_process_offset()` are exported in the `IIO_RESCALE` namespace for reuse by other kernel users. Variant property parsers compute `numerator`, `denominator`, and optional `offset`: `rescale_current_sense_amplifier_props()`, `rescale_current_sense_shunt_props()`, `rescale_voltage_divider_props()`, `rescale_temp_sense_rtd_props()`, and `rescale_temp_transducer_props()`. `rescale_read_raw()`, `rescale_read_avail()`, ext-info proxy callbacks, `rescale_configure_channel()`, and `rescale_probe()` form the IIO device implementation.

## Control Flow
Probe obtains the unnamed source IIO channel, sizes private memory to include copied source ext-info callbacks, allocates an IIO device, selects variant config from firmware compatible data, computes scaling properties, validates nonzero numerator/denominator, sets a single channel with the target IIO type, proxies compatible ext-info entries, configures channel masks based on whether the source supports raw+scale/offset or processed data, and registers the device.

Raw reads either read raw source values or processed values if only processed data is available. Scale reads obtain source scale or use 1:1 for processed sources, then multiply by the rescaler ratio while preserving fractional representation where possible. Offset reads derive the equivalent userspace offset by combining source offset and rescaler offset divided by source scale. Available raw values are proxied only for raw sources.

## State And Persistence
Runtime state consists of the source channel pointer, computed ratio and offset, chosen variant config, copied channel spec, optional copied ext-info array, and a `chan_processed` flag. It does not maintain samples or persistent calibration. All behavior is recomputed from the source channel and static firmware properties at probe and read time.

## Dependencies And Integration Points
The driver depends on IIO consumer APIs, platform firmware matching, property APIs, gcd/overflow helpers, and the IIO core. It matches compatible strings `current-sense-amplifier`, `current-sense-shunt`, `voltage-divider`, `temperature-sense-rtd`, and `temperature-transducer`. It integrates with upstream producers by consuming their raw/processed/scale/offset/ext-info ABI and re-exposing a transformed channel.

## Risks And Test Signals
The most important risks are numeric overflow/rounding, sign handling for `IIO_VAL_INT_PLUS_MICRO/NANO`, invalid zero scaling factors, unsupported source channels, and misleading available values if source scale changes dynamically. Tests should cover all scale return types, negative numerator/denominator and source scales, offset composition with and without source offset, each compatible's property parsing and gcd reduction, processed-only sources, ext-info read/write proxying, raw available proxying, invalid missing properties, and exported helper use by another module.
