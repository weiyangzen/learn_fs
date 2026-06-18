# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/Makefile

## Purpose
The Makefile defines the object composition for the MANA InfiniBand/RDMA driver.

## Important APIs, Types, And Functions
`obj-$(CONFIG_MANA_INFINIBAND) += mana_ib.o` links the driver when enabled. `mana_ib-y` aggregates `device.o`, `main.o`, `wq.o`, `qp.o`, `cq.o`, `mr.o`, `ah.o`, `wr.o`, and `counters.o`.

## Control Flow
There is no runtime control flow. Build flow collects the listed translation units into one `mana_ib` module or built-in object.

## State And Persistence
No runtime state exists. Build state is determined by `CONFIG_MANA_INFINIBAND`.

## Dependencies And Integration Points
The object list matches the `ib_device_ops` functions registered in `device.c` and prototypes in `mana_ib.h`; omitting any listed object would break verbs, memory, address-handle, work-request, or counter support.

## Risks
Adding new exported operations in `mana_ib.h` without updating `mana_ib-y` can create link failures. Removing objects may compile only if matching device ops are also removed.

## Test Signals
Kernel build with `CONFIG_MANA_INFINIBAND=y` and `m`; inspect `modinfo mana_ib` and link output for all expected objects.
