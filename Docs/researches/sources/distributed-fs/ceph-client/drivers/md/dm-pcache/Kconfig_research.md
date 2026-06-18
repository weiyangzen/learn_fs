
# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/Kconfig

## Purpose
Adds the `DM_PCACHE` kernel configuration option for an experimental persistent-cache device-mapper target that uses persistent memory or DAX-capable devices as a low-latency cache in front of block devices.

## Important APIs, Types, And Functions
Defines `config DM_PCACHE` as a tristate named "Persistent cache for Block Device (Experimental)". It depends on `BLK_DEV_DM` and `DEV_DAX`. The help text identifies persistent memory/CXL/DAX devices as cache media and warns that the feature is experimental.

## Control Flow
Kconfig participates in build-time selection only. When enabled as built-in or module, the `Makefile` builds `dm-pcache.o` from the persistent-cache source set. When disabled, none of the pcache target code is compiled.

## State And Persistence
No runtime state is defined here. The option controls whether pcache's runtime and on-media metadata code can exist in the kernel build.

## Dependencies And Integration Points
Integrates with the Linux Kconfig system under device-mapper drivers. `BLK_DEV_DM` supplies the target framework and `DEV_DAX` supplies direct-access persistent-memory support required by `cache_dev.c`.

## Risks
The feature is marked experimental and depends on DAX; enabling it without suitable hardware or test coverage risks exposing unfinished target behavior. Missing dependency declarations would cause build failures because the source uses DAX and dm APIs directly.

## Test Signals
Run Kconfig builds with `DM_PCACHE=n/m/y`, verify dependencies select or hide the option correctly, build with `DEV_DAX` disabled to ensure exclusion, and load the module only on systems with appropriate DAX-capable cache devices.
