# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/Makefile

Purpose: minimal Kbuild fragment for the mlx5 eswitch subdirectory. It applies `subdir-ccflags-y += -I$(src)/..`, making parent `core` headers available to sources below `core/esw`.

Important behavior: there are no object lists or conditional targets in this file; compilation units are selected by parent Kbuild files. Its only API-like effect is the include-path contract for files such as `esw/acl/*.c`, which include headers like `mlx5_core.h`, `eswitch.h`, and local ACL headers.

State and dependencies: no runtime state. The dependency is build-system state: `$(src)` must resolve to `drivers/net/ethernet/mellanox/mlx5/core/esw`, and the parent directory must contain the headers consumed by eswitch submodules.

Risks and test signals: changes here can break all eswitch subdirectory compilation by removing parent include visibility or adding overbroad flags. Test signals are allmodconfig or mlx5 eswitch builds, especially ACL files that rely on `-I$(src)/..`.
