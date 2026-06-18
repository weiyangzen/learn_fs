# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etm4x-cfg.h

## Purpose

This header declares ETMv4-specific CoreSight system configuration resource IDs and the registration entry point used by the ETM4x core driver.

## Important APIs and Constants

Resource IDs classify counters, comparators, comparator pairs, resource selectors, selector pairs, sequencer, and timestamp. `ETM4_CFG_RES_MASK` masks the low nibble of resource IDs. `etm4_cscfg_register(struct coresight_device *csdev)` registers an ETM4 CoreSight source with the syscfg framework and loads matching features.

## Control Flow and Integration

`coresight-etm4x-core.c` calls `etm4_cscfg_register()` after CoreSight source registration and perf symlink creation. The implementation in `coresight-etm4x-cfg.c` uses this header's declaration and ETM4 resource identifiers to connect generic syscfg feature descriptors to ETM4 driver config storage.

## State, Dependencies, Risks, and Test Signals

The header defines constants only. Runtime state is maintained by `coresight-etm4x-cfg.c`, generic syscfg objects, and `struct etmv4_config`. It depends on `coresight-config.h` and `coresight-etm4x.h`. The main risk is changing resource ID values in a way that breaks existing syscfg feature descriptors. Test signals include successful ETM4 syscfg registration and feature descriptors that refer to each resource class.
