<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/Makefile

## Purpose
`drivers/iio/proximity/Makefile` maps proximity-related Kconfig symbols to the object files built by kbuild.

## Important APIs, types, and functions
Each `obj-$(CONFIG_...) += ...o` line ties a configuration symbol to a driver object. Entries include `as3935.o`, `cros_ec_mkbp_proximity.o`, `d3323aa.o`, `hx9023s.o`, `irsd200.o`, `isl29501.o`, `pulsedlight-lidar-lite-v2.o`, `mb1232.o`, `ping.o`, `rfd77402.o`, `srf04.o`, `srf08.o`, Semtech SX objects, `vcnl3020.o`, VL53Lx objects, and `aw96103.o`.

## Control flow
kbuild evaluates each line according to the final `.config`. Enabled built-in symbols add objects to the built-in archive; module symbols build loadable modules.

## State and persistence behavior
The file has no runtime state. Build outputs depend on `.config` state.

## Dependencies and integration points
It integrates with Kconfig symbols in the same directory and with source filenames. The comment asks maintainers to keep entries alphabetically ordered, although `AW96103` appears at the end.

## Risks
Symbol/object mismatches cause missing modules or build failures. Ordering comments can drift from reality. Adding a Kconfig entry without a Makefile line silently prevents compilation.

## Test signals
Build each symbol as `m` and `y`, run `make drivers/iio/proximity/`, and compare Kconfig symbols against Makefile entries for one-to-one coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/Makefile -->
