# sources/distributed-fs/ceph-client/drivers/block/null_blk/Kconfig

## Purpose
This Kconfig fragment declares build options for the null block test driver and its optional fault-injection support.

## Important APIs, Types, And Functions
`config BLK_DEV_NULL_BLK` is a tristate option named "Null test block driver" and selects `CONFIGFS_FS`, because runtime device creation/configuration is exposed through configfs. `config BLK_DEV_NULL_BLK_FAULT_INJECTION` is a bool depending on `BLK_DEV_NULL_BLK` and `FAULT_INJECTION_CONFIGFS`, enabling per-device fault injection groups used by `main.c`.

## Control Flow
There is no runtime control flow. Build selection of `BLK_DEV_NULL_BLK` controls whether `null_blk.o` is built. Enabling fault injection compiles extra fault attributes, configfs groups, and failure decisions for request timeout, request requeue, and hardware-context initialization.

## State And Persistence Behavior
The file stores compile-time configuration only. Runtime state is in `main.c` and optional fault-injection configfs state.

## Dependencies And Integration Points
The Kconfig integrates null_blk with configfs and the generic fault-injection framework. It also indirectly coordinates with the Makefile, which adds `main.o`, `zoned.o`, and optional tracing objects based on configuration.

## Risks
Because `BLK_DEV_NULL_BLK` selects configfs, disabling configfs independently is not possible when the driver is enabled. Fault injection depends on `FAULT_INJECTION_CONFIGFS`; tests expecting fault knobs must ensure this option is enabled.

## Test Signals
Build-menu visibility, successful module or built-in build for `BLK_DEV_NULL_BLK`, and presence/absence of configfs fault groups under created nullb devices validate the configuration.
