# sources/distributed-fs/ceph-client/drivers/base/Kconfig

## Purpose
Defines generic driver-core configuration options for the kernel build: auxiliary bus availability, uevent helpers, devtmpfs, firmware/deferred-probe policy, device coredumps, driver/devres debug features, test hooks, NUMA/topology support, regmap inclusion, DMA buffer sharing, and fw_devlink sync-state behavior.

## Important APIs, Types, And Functions
This is Kconfig, not C. Key symbols include `AUXILIARY_BUS`, `UEVENT_HELPER`, `DEVTMPFS`, `DEVTMPFS_MOUNT`, `DEVTMPFS_SAFE`, `DRIVER_DEFERRED_PROBE_TIMEOUT`, `STANDALONE`, `PREVENT_FIRMWARE_BUILD`, `WANT_DEV_COREDUMP`, `ALLOW_DEV_COREDUMP`, `DEV_COREDUMP`, `DEBUG_DRIVER`, `DEBUG_DEVRES`, `DEBUG_TEST_DRIVER_REMOVE`, `GENERIC_ARCH_TOPOLOGY`, `GENERIC_ARCH_NUMA`, `DMA_SHARED_BUFFER`, and `FW_DEVLINK_SYNC_STATE_TIMEOUT`.

## Control Flow
The menu is evaluated at kernel configuration time. Boolean/tristate/int/string symbols gate compilation in `drivers/base/Makefile` and related subsystem Kconfigs. It sources firmware loader, base tests, and regmap Kconfigs.

## State And Persistence
Selections persist in the kernel `.config` and become preprocessor symbols such as `CONFIG_AUXILIARY_BUS`, `CONFIG_DEVTMPFS`, `CONFIG_GENERIC_ARCH_NUMA`, and `CONFIG_GENERIC_ARCH_TOPOLOGY`, influencing compiled objects and runtime defaults.

## Dependencies And Integration Points
Integrates with `drivers/base/Makefile`, firmware loader, devtmpfs, devcoredump, PM KUnit tests, NUMA memblocks, regmap, DMA fences, and fw_devlink driver-core behavior.

## Risks And Edge Cases
Enabling old `UEVENT_HELPER` can create heavy process load. `DEBUG_TEST_DRIVER_REMOVE` intentionally destabilizes systems by forcing probe/remove/probe. `DEVTMPFS_SAFE` can break users requiring executable mappings from device nodes. `FW_DEVLINK_SYNC_STATE_TIMEOUT` changes supplier/consumer synchronization semantics.

## Test Signals
Build matrix coverage for selected symbols, boot behavior for devtmpfs mount and uevent helper, KUnit tests for PM options, and object inclusion for auxiliary/topology/NUMA settings validate this file.
