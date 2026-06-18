<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/Kconfig

## Purpose
Adds the `DM_PERSISTENT_DATA` kernel configuration symbol for the device-mapper persistent-data library. The library provides immutable on-disk metadata structures used by targets such as thin provisioning, cache metadata, and other dm components that need transactional btrees, space maps, arrays, and bitsets.

## Important APIs, Types, And Functions
This file defines one `tristate` config item. It depends on `BLK_DEV_DM`, selects `CRC32`, and selects `DM_BUFIO`. There are no C APIs here; the config symbol controls compilation of the object set listed by the companion Makefile.

## Control Flow
During Kconfig resolution, enabling a dependent dm target can select or require `DM_PERSISTENT_DATA`. When enabled built-in or as a module, the Makefile builds `dm-persistent-data.o` from the persistent-data source files. The selected dependencies ensure checksum helpers and dm-bufio cache infrastructure are present.

## State And Persistence
The Kconfig entry has no runtime state. Its persistence impact is indirect: enabling it compiles the code that reads and writes persistent metadata formats, and disabling it removes those helpers and any targets that depend on them.

## Dependencies And Integration Points
Integration points are the kernel configuration system, device-mapper block-device support, CRC helpers, and dm-bufio. Device-mapper targets that use these library APIs rely on this symbol being available in their build dependency chain.

## Risks
Incorrect dependency declarations would fail at link time or allow targets to build without required checksum/bufio support. Because the symbol is `tristate`, module/built-in ordering must be compatible with dm targets that consume exported symbols from the library.

## Test Signals
Build tests should cover `DM_PERSISTENT_DATA=y`, `m`, and disabled configurations where dependent targets are also disabled. Link checks should confirm all exported persistent-data symbols resolve for dm-thin/cache-style users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/Kconfig -->
