# sources/distributed-fs/ceph-client/drivers/vdpa/mlx5/Makefile

Purpose: kbuild composition for mlx5 vDPA support.

Important APIs/types/functions: adds the core include path and builds `mlx5_vdpa.o` for `CONFIG_MLX5_VDPA_NET` from `net/mlx5_vnet.o`, `core/resources.o`, `core/mr.o`, and `net/debug.o`.

Control flow: a single module/object contains network vDPA logic, shared resource commands, memory registration, and debugfs support.

State and persistence: build-only file.

Dependencies and integration: depends on top-level vDPA Makefile and Kconfig selecting `MLX5_VDPA`/`MLX5_VDPA_NET`; shares core headers through `subdir-ccflags-y`.

Risks: feature additions split into new files must update the composite object list. Core code is compiled only through the net driver here.

Test signals: module build with `MLX5_VDPA_NET=m/y`, include path resolution for `mlx5_vdpa.h`, and link coverage for resource/MR/debug functions referenced by vnet.
