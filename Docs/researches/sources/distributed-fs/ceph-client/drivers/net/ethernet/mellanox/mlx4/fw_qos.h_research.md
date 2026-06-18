# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/fw_qos.h

## Purpose
`fw_qos.h` defines the public mlx4 QoS firmware helper contract. It provides constants for user priorities and traffic classes, default VPP values, the per-vport QoS parameter type, and prototypes for port scheduler, VPP, and vport QoS commands.

## Important APIs, Types, and Functions
The header defines `MLX4_NUM_UP`, `MLX4_NUM_TC`, `MLX4_DEFAULT_QOS_PRIO`, and `MLX4_VPP_DEFAULT_VPORT`. `struct mlx4_vport_qos_param` carries `bw_share`, `max_avg_bw`, and `enable` for one user priority. Declared functions are `mlx4_SET_PORT_PRIO2TC()`, `mlx4_SET_PORT_SCHEDULER()`, `mlx4_ALLOCATE_VPP_get()`, `mlx4_ALLOCATE_VPP_set()`, `mlx4_SET_VPORT_QOS_get()`, and `mlx4_SET_VPORT_QOS_set()`.

## Control Flow
The header has no executable control flow. It documents expected sequencing: configure priority-to-TC and scheduler settings at the port level, query and allocate VPP resources per priority after port type is set and before QPs are open, and set vport QoS before associating QPs with that vport.

## State and Persistence
No state is stored in the header. State is represented by caller-owned arrays and `struct mlx4_vport_qos_param` values that `fw_qos.c` serializes into firmware mailboxes. Successful calls persist the configuration in firmware.

## Dependencies and Integration Points
The header includes mlx4 command and device public headers and is used by QoS/DCB implementation code plus `fw_qos.c`. It forms the interface between netdev QoS policy and firmware command encoding.

## Risks
Risks are mostly contract-related: all arrays are expected to have eight entries, VPP allocation must not exceed firmware-reported availability, scheduler bandwidth percentages must be valid per priority group, and callers must check firmware capability before invoking these helpers. Misordered VPP or QoS setup relative to QP creation can fail or produce undefined firmware behavior.

## Test Signals
Compile-time tests ensure consumers match the prototypes and constants. Runtime signals include successful DCB scheduler configuration, VPP allocation validation, vport QoS query/set round trips, and failure behavior on unsupported firmware or invalid port/vport identifiers.
