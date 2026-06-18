# sources/distributed-fs/ceph-client/drivers/staging/iio/Makefile

## Purpose
Adds staging IIO subdirectories to the build.

## Important Entries and Integration
`obj-y` descends unconditionally into `accel/`, `adc/`, `addac/`, `frequency/`, and `impedance-analyzer/`. Individual drivers are still controlled by each subdirectory Makefile and Kconfig symbol.

## Risks and Test Signals
Risk is directory omission or stale paths. Build tests should verify selected staging IIO drivers under these subdirectories are discovered and compiled.
