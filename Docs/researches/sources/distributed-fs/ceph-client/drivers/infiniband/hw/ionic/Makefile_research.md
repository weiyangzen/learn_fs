# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/Makefile

## Purpose
`Makefile` builds the Ionic RDMA provider object and gives it access to shared Pensando Ionic Ethernet headers.

## Important APIs, Types, And Functions
The file sets `ccflags-y` to include `drivers/net/ethernet/pensando/ionic`, builds `ionic_rdma.o` when `CONFIG_INFINIBAND_IONIC` is enabled, and composes the module from `ionic_ibdev.o`, `ionic_lif_cfg.o`, `ionic_queue.o`, `ionic_pgtbl.o`, `ionic_admin.o`, `ionic_controlpath.o`, `ionic_datapath.o`, and `ionic_hw_stats.o`.

## Control Flow
Kbuild compiles each listed translation unit into the composite `ionic_rdma` module or built-in object. The include path makes shared `ionic_api.h` and firmware definitions visible to the RDMA files.

## State And Persistence
There is no runtime state. The file defines build composition and compile-time include search behavior.

## Dependencies And Integration Points
It is paired with `Kconfig` and integrates RDMA-specific files with shared Ionic net-driver headers. `ionic_admin.c` and `ionic_controlpath.c` rely on symbols and structures from the other objects listed here, especially lif config, queue helpers, page-table helpers, datapath completions, and hardware stats.

## Risks
The relative include path couples the RDMA driver to the net-driver source tree layout. Missing an object in `ionic_rdma-y` can produce link-time failures or incomplete `ib_device_ops`. Header name collisions are possible because the net-driver include directory is injected globally for this directory.

## Test Signals
Test module and built-in builds, clean rebuilds after touching shared Ionic headers, link coverage for all `ionic_*` symbols used by admin/controlpath/datapath files, and out-of-tree or alternate source-root builds where `$(srctree)` include paths matter.
