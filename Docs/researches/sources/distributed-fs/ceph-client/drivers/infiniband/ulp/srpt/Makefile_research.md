# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srpt/Makefile

## Purpose

The SRPT Makefile connects the Kconfig symbol to the driver object.

## Important APIs, Types, and Functions

`obj-$(CONFIG_INFINIBAND_SRPT) += ib_srpt.o` tells Kbuild to compile and link `ib_srpt.c` when SRPT is enabled.

## Control Flow

There is no runtime flow. Kbuild evaluates `CONFIG_INFINIBAND_SRPT` and either omits the object, links it built-in, or emits it as a module.

## State and Persistence Behavior

The file affects build artifacts only. It creates no runtime state.

## Dependencies and Integration Points

It integrates with the surrounding RDMA ULP build tree and depends on `Kconfig` to ensure required subsystems are available before `ib_srpt.o` is selected.

## Risks and Edge Cases

Adding more translation units to SRPT without updating this file would omit code. Renaming `ib_srpt.c` without changing the object rule would break the build.

## Test Signals

`make M=drivers/infiniband/ulp/srpt` and full kernel builds with `CONFIG_INFINIBAND_SRPT=m` and `=y` should produce/link the expected object without unresolved RDMA or target-core symbols.
