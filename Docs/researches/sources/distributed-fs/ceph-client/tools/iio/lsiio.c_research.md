# sources/distributed-fs/ceph-client/tools/iio/lsiio.c

## Purpose

`lsiio.c` lists Industrial I/O devices and triggers available under IIO sysfs, optionally showing sensor channel attributes.

## Important APIs and Flow

The tool uses `iio_dir` and `read_sysfs_string` from `iio_utils`. Local helpers check prefixes and postfixes, dump input channels ending in `_raw` or `_input`, print one device by parsing its numeric suffix and reading its `name`, and print one trigger similarly. `dump_devices` scans the IIO sysfs directory twice: first for `iio:device*`, then for `trigger*`. `main` accepts repeated `-v`; default output resembles `lspci`, while verbosity level 1 lists sensor raw/input attributes below each device.

## State, Dependencies, and Integration

There is no persistent state. The tool depends on `/sys/bus/iio/devices/`, readable `name` files, and the shared sysfs helper implementation. It integrates with the other IIO examples as a discovery command for device and trigger names.

## Risks and Test Signals

The prefix check requires names to be longer than the prefix, so exact-prefix entries are ignored. Errors while dumping one entry abort the whole listing. Tests should run against fake and real IIO sysfs trees, covering no-device behavior, devices with missing names, trigger listings, and `-v` channel display.
