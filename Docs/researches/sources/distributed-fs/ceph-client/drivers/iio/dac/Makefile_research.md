
# sources/distributed-fs/ceph-client/drivers/iio/dac/Makefile

## Purpose
This Makefile maps DAC Kconfig symbols to object files for the IIO DAC subsystem.

## Important APIs, types, and functions
- Researched object mappings include `ad3530r.o`, `ad3552r-hs.o`, `ad3552r-common.o`, `ad3552r.o`, `ad5064.o`, `ad5360.o`, `ad5380.o`, `ad5421.o`, `ad5446.o`, `ad5446-spi.o`, `ad5446-i2c.o`, and `ad5449.o`.
- Common/library objects are built through symbols such as `CONFIG_AD3552R_LIB` and `CONFIG_AD5446`.

## Control flow
There is no runtime control flow; the kernel build system includes objects according to Kconfig.

## State and persistence behavior
Build artifact selection only.

## Dependencies and integration points
The file is the build bridge between the DAC Kconfig menu and module objects. It also ensures shared common objects are available for transport-specific modules that import their exported namespaces.

## Risks and edge cases
- If a transport driver selects a common library but the Makefile omits the common object, namespace imports and symbols fail.
- The comment asks new entries to remain alphabetical; ordering should be reviewed when adding drivers, since existing entries around `AD5064` and `AD5446` are not strictly lexicographic by filename.

## Test signals
Compile each researched DAC symbol as `m` and `y`; verify expected module names and that common modules load before namespace importers.
