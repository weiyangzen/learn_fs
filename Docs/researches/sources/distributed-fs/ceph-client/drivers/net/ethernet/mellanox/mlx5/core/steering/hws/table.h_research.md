# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/table.h

Purpose: defines HWS table and default-miss relationship structures plus flow-table helper prototypes.

Important APIs/types: `struct mlx5hws_default_miss` records a table's miss target and reverse list of source tables. `struct mlx5hws_table` stores context, firmware FT id/type, logical type/level/uid, matcher list, context list node, and default-miss metadata. Inline helpers map HWS table types to firmware flow-table types.

Control flow/state: the header establishes the state consumed by `table.c` and matcher code. `mlx5hws_table_get_fw_ft_type()` currently accepts only FDB tables and returns `FS_FT_FDB`; resource FW type helper distinguishes FDB RX/TX mirror cases.

Dependencies/integration: included through HWS internal headers, depends on `mlx5hws_context`, table type enums, mlx5 flow-table constants, and Linux `list_head`.

Risks: only FDB is supported here; adding NIC table types requires updating the inline type mappers and table creation logic together. Default-miss list ownership is manual and must remain synchronized with firmware miss actions.

Test signals: compile/build coverage for all callers, FDB table creation, invalid table type rejection, and default-miss list membership after connect/destroy.
