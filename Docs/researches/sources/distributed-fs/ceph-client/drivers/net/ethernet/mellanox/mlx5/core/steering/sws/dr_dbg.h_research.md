# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_dbg.h

Purpose: declares debug dump constants, transient buffer structures, domain debugfs state, and public debug list/lifecycle hooks for SWS steering.

Important APIs/types: `MLX5DR_DEBUG_DUMP_BUFF_SIZE`, `MLX5DR_DEBUG_DUMP_BUFF_LENGTH`, dump state enum, `mlx5dr_dbg_dump_buff`, `mlx5dr_dbg_dump_data`, `mlx5dr_dbg_dump_info`, and function prototypes for init/uninit and table/rule add/delete.

Control flow/state: `mlx5dr_dbg_dump_info` is embedded in the domain and stores mutex-protected debug lists, debugfs dentries, current dump buffer data, and atomic dump state. The .c file allocates/frees buffers and populates list nodes.

Dependencies/integration: requires `struct mlx5dr_domain`, `struct mlx5dr_table`, `struct mlx5dr_rule`, Linux list/dentry/mutex/atomic definitions through DR includes.

Risks: buffer size is large by design; increasing it affects memory pressure. The header exposes list-management functions but not lifetime constraints, so callers must pair add/del with object lifecycle.

Test signals: compile coverage, FDB debugfs lifecycle, add/del calls during table/rule create/destroy, and repeated read/free cycles.
