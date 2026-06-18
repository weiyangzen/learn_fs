# sources/distributed-fs/ceph-client/drivers/block/rnbd/Makefile

## Purpose
Builds the RNBD client and server composite objects and supplies include flags needed for RTRS integration and server trace compilation.

## Important APIs, Types, And Functions
The file sets `ccflags-y := -I$(srctree)/drivers/infiniband/ulp/rtrs`, defines `rnbd-client-y` as `rnbd-clt.o` plus `rnbd-clt-sysfs.o`, defines `rnbd-server-y` as `rnbd-srv.o`, `rnbd-srv-sysfs.o`, and `rnbd-srv-trace.o`, adds a per-object include flag for `rnbd-srv-trace.o`, and wires final objects to `CONFIG_BLK_DEV_RNBD_CLIENT` and `CONFIG_BLK_DEV_RNBD_SERVER`.

## Control Flow
There is no runtime control flow. Kbuild uses the object lists to link client and server modules or built-ins depending on Kconfig. The parent block `Makefile` descends into `rnbd/` when `CONFIG_BLK_DEV_RNBD` is selected.

## State And Persistence Behavior
No runtime or persistent state is represented. The file controls build composition only.

## Dependencies And Integration Points
Integrates with Kbuild, the RNBD source files in the same directory, and RTRS headers under `drivers/infiniband/ulp/rtrs`. The trace object needs `-I$(src)` so generated or local trace headers can be found during compilation.

## Risks
Build breakage is the main risk. Object-list drift from source renames, missing RTRS include paths, or trace include path changes will fail compilation. Because client and server are separate composite objects, shared code additions must be explicitly added to the right object list or a common object strategy.

## Test Signals
Signals include compile tests for `CONFIG_BLK_DEV_RNBD_CLIENT=m/y`, `CONFIG_BLK_DEV_RNBD_SERVER=m/y`, and both enabled; clean builds after touching trace headers; and verifying final modules contain the expected sysfs and trace objects.
