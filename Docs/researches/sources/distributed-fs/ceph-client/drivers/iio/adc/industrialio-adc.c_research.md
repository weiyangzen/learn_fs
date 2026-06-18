# sources/distributed-fs/ceph-client/drivers/iio/adc/industrialio-adc.c

## Purpose
`industrialio-adc.c` provides a small exported helper for ADC drivers that describe channels in firmware child nodes. It allocates an array of single-ended `iio_chan_spec` entries from `channel` child nodes and their `reg` properties.

## Important APIs, types, and functions
- `devm_iio_adc_device_alloc_chaninfo_se()` is the sole exported function.
- It calls `iio_adc_device_num_channels(dev)` to count firmware-described channels.
- It uses `device_for_each_named_child_node_scoped(dev, child, "channel")` to iterate channel nodes.
- It copies a caller-provided template into each allocated channel spec and sets `chan->channel` from `reg`.
- It exports the symbol in namespace `IIO_DRIVER`.

## Control flow
The helper counts channels, returns `-ENOENT` when no channel nodes are present, devm-allocates the channel array, reads each child `reg`, optionally enforces `max_chan_id`, copies the template, stores the channel number, returns the allocated array through `cs`, and returns the number of channels.

## State and persistence
There is no persistent state. Allocated channel specs are devm-managed and freed at device detach.

## Dependencies and integration points
This helper integrates with firmware property APIs, IIO ADC helper APIs, devm allocation, and module namespace exports for ADC drivers that want common fwnode channel parsing.

## Risks
- The function assumes the count from `iio_adc_device_num_channels()` matches the later named-child iteration.
- It only sets `.channel`; drivers needing per-channel labels, differential pairs, or scan indices need additional processing.
- Returning `-ENOENT` for zero nodes is a contract callers must handle distinctly from empty-but-valid configurations.

## Test signals
Unit-test firmware nodes with no channels, missing `reg`, out-of-range `reg`, and valid sparse channel IDs. Check that template fields are preserved and devm cleanup occurs on probe failure.
