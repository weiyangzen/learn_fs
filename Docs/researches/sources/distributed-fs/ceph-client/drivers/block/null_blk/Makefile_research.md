# sources/distributed-fs/ceph-client/drivers/block/null_blk/Makefile

## Purpose
This Makefile describes how the null block driver is compiled from its component objects.

## Important APIs, Types, And Functions
`ccflags-y += -I$(src)` ensures trace-event includes can find local headers. `obj-$(CONFIG_BLK_DEV_NULL_BLK) += null_blk.o` builds the driver when selected. `null_blk-objs := main.o` makes `main.c` mandatory. `trace.o` is added only when both zoned block support and tracing are enabled. `zoned.o` is added when `CONFIG_BLK_DEV_ZONED` is enabled.

## Control Flow
There is no runtime flow. Build flow starts with `main.o`, then conditionally includes zoned support and zoned tracepoints. The trace object is guarded by zoned support because the local tracepoints describe zoned operations.

## State And Persistence Behavior
No runtime state or persistence exists in the Makefile.

## Dependencies And Integration Points
It integrates Kconfig symbols with Kbuild object composition. The include path supports `trace.h`'s `TRACE_INCLUDE_PATH .` pattern and local inclusion from generated trace code.

## Risks
Tracepoint compilation is sensitive to include paths and `CREATE_TRACE_POINTS`; removing `-I$(src)` can break generated trace includes. Building zoned functionality without matching source objects would leave the inline stubs in `null_blk.h` mismatched with runtime expectations.

## Test Signals
Build with `CONFIG_BLK_DEV_NULL_BLK=m/y`, with and without `CONFIG_BLK_DEV_ZONED`, and with and without `CONFIG_TRACING`, should include the expected objects and produce no trace include failures.
