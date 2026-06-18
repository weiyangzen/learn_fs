# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/Makefile

## Purpose
This Makefile declares how the mlx5 InfiniBand/RDMA driver object is built and which feature-specific source files are conditionally included.

## Important APIs, types, and functions
The primary build target is `mlx5_ib.o`, selected by `obj-$(CONFIG_MLX5_INFINIBAND)`. The base object list includes address handles, command wrappers, congestion, counters, CQ, data-direct, device memory, DMAH, doorbell, flow steering, GSI, virtualization, MAD, main, memory, MR, QP/QPC, restrack, SRQ/SRQ commands, UMR, and WR logic. Conditional additions include `odp.o`, `ib_rep.o`, `devx.o`, `qos.o`, `std_types.o`, and `macsec.o`.

## Control flow
Kbuild assembles all `mlx5_ib-y` objects into one driver object when `CONFIG_MLX5_INFINIBAND` is enabled. Optional objects are appended when their feature symbols are enabled: on-demand paging, eswitch representors, user access/devx, and MACsec.

## State and persistence behavior
This file has no runtime state. Its only persistent effect is the compiled module or built-in object composition.

## Dependencies and integration points
It integrates with the Kconfig symbol and the Linux kernel kbuild system. It also documents feature boundaries in the mlx5 IB driver by mapping config symbols to compilation units.

## Risks
Build risks include missing an object for a feature registration path, stale conditional dependencies, and unintentionally compiling user-access or eswitch code without the required core support. Because many files register `ib_device_ops`, omitted objects can create link failures or missing runtime features.

## Test signals
Run build matrix coverage for baseline, ODP, eswitch, user access/devx, and MACsec configurations. Verify module link symbols and smoke-test load/unload for built-in and modular builds.
