# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/port_buffer.h

Purpose: defines mlx5e port-buffer constants, support checks, change-bit flags, data structures, and public buffer configuration APIs.

Important APIs/types: `MLX5E_MAX_NETWORK_BUFFER`, `MLX5E_TOTAL_BUFFERS`, `MLX5E_DEFAULT_CABLE_LEN`, `MLX5_BUFFER_SUPPORTED`, change flags for cable/PFC/prio/size, `struct mlx5e_bufferx_reg`, `struct mlx5e_port_buffer`, `mlx5e_port_manual_buffer_config`, and `mlx5e_port_query_buffer`.

Control flow: callers query current port buffer state or request manual changes by passing a change bitmask plus optional PFC, buffer-size, and priority mapping data.

State and persistence: structures mirror firmware PBMC buffer entries in byte units. Implementation writes persistent port register state and updates DCB runtime fields.

Dependencies and integration: includes `en.h` and `port.h`; capability macro checks PBMC and PPTB PCAM support.

Risks: callers must provide arrays sized for eight priorities/buffers and valid change-specific pointers.

Test signals: DCB user configuration paths and capability-gated support reporting.
