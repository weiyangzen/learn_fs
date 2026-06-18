# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/iser/Makefile

## Purpose
`iser/Makefile` defines how the iSER initiator driver is built when `CONFIG_INFINIBAND_ISER` is enabled.

## Important APIs, Types, And Functions
The key rule is `obj-$(CONFIG_INFINIBAND_ISER) += ib_iser.o`, which emits the driver as built-in or module according to the Kconfig value. `ib_iser-y` lists the component objects linked into `ib_iser.o`: `iser_verbs.o`, `iser_initiator.o`, `iser_memory.o`, and `iscsi_iser.o`.

## Control Flow And State
There is no runtime control flow. Build state flows from Kconfig into kbuild: enabled configurations compile the listed source objects and link them into one driver object; disabled configurations compile none of them.

## Dependencies And Integration Points
The file integrates with Linux kbuild and the `INFINIBAND_ISER` Kconfig option. The object list indicates the driver is split into RDMA verbs handling, initiator/session logic, memory registration, and the iSCSI transport binding.

## Risks And Test Signals
Risks are limited to build composition: omitted objects would produce missing symbols or incomplete protocol behavior, and stale object names would break builds. Test signals include `CONFIG_INFINIBAND_ISER=y` and `m` builds, clean module link of `ib_iser.o`, and dependency builds that compile all four listed implementation objects.
