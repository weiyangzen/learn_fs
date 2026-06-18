# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/fw_qos.c

## Purpose
`fw_qos.c` implements firmware command helpers for mlx4 Enhanced QoS. It configures port priority-to-traffic-class mapping, traffic-class scheduler bandwidth/rate limits, virtual port priority allocation (VPP), and per-vport QoS bandwidth parameters.

## Important APIs, Types, and Functions
Exported APIs are `mlx4_SET_PORT_PRIO2TC()`, `mlx4_SET_PORT_SCHEDULER()`, `mlx4_ALLOCATE_VPP_get()`, `mlx4_ALLOCATE_VPP_set()`, `mlx4_SET_VPORT_QOS_get()`, and `mlx4_SET_VPORT_QOS_set()`. Internal mailbox structures are `struct mlx4_set_port_prio2tc_context`, `struct mlx4_port_scheduler_tc_cfg_be`, `struct mlx4_set_port_scheduler_context`, `struct mlx4_alloc_vpp_param`, `struct mlx4_prio_qos_param`, and `struct mlx4_set_vport_context`.

## Control Flow
Each API allocates a command mailbox, fills or reads a firmware-defined context, invokes `mlx4_cmd()` or `mlx4_cmd_box()` with the relevant opcode and modifier, then frees the mailbox. `mlx4_SET_PORT_PRIO2TC()` packs two user priorities per byte. `mlx4_SET_PORT_SCHEDULER()` iterates all traffic classes, sets priority group, ETS bandwidth percentage, and either a default or explicit rate limit using 100 Mbps or 1 Gbps units. VPP query/set commands read or write available/distributed VPP counts per user priority. Vport QoS query/set commands transfer `bw_share`, `max_avg_bw`, and an enable bit per user priority.

## State and Persistence
The file does not retain local state. Successful commands persist configuration in device firmware for the selected physical port or vport. Mailbox data is temporary, and the caller owns arrays passed for priority, traffic class, rate limit, VPP allocation, and vport QoS.

## Dependencies and Integration Points
The file depends on the mlx4 command mailbox layer, command opcodes from `linux/mlx4/cmd.h`, device types from `linux/mlx4/device.h`, and declarations/constants from `fw_qos.h` and `fw.h`. It is used by Ethernet DCB/netlink and SR-IOV QoS management paths after firmware capability checks in `fw.c` and HCA initialization enablement.

## Risks
Risks include invalid caller-provided arrays, bandwidth percentages that do not sum correctly within priority groups, rate-limit unit conversion truncation for values above the 100 Mbps range, endian conversion mistakes in firmware contexts, and issuing commands when the device or port lacks QoS/VPP support. The enable bit in vport QoS is shifted to bit 31 on set and decoded from low bits on get, so firmware format assumptions should be validated.

## Test Signals
Useful tests cover priority-to-TC packing, scheduler programming with null and non-null rate-limit arrays, boundary rate limits around `MLX4_MAX_100M_UNITS_VAL`, VPP query before and after allocation, per-vport QoS set/get round trips for all eight priorities, unsupported firmware failures, mailbox allocation failure, and integration through DCB configuration tools.
