# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/sense.c

## Purpose

`sense.c` implements mlx4 port-type sensing for devices that can dynamically detect whether a physical port should run InfiniBand or Ethernet. It periodically issues firmware `SENSE_PORT` commands for auto-configured ports and requests port-type changes when the sensed configuration is valid.

## Important APIs, Types, And Functions

- `mlx4_SENSE_PORT()` sends `MLX4_CMD_SENSE_PORT` and returns an `enum mlx4_port_type`.
- `mlx4_do_sense_ports()` iterates all device ports, senses only ports enabled by `sense->do_sense_port[]`, `sense->sense_allowed[]`, and `possible_type == MLX4_PORT_TYPE_AUTO`, and falls back to defaults on errors or zero results.
- `mlx4_sense_port()` is the delayed-work callback that locks `port_mutex`, senses ports, validates with `mlx4_check_port_params()`, and applies with `mlx4_change_port_types()`.
- `mlx4_start_sense()`, `mlx4_stop_sense()`, and `mlx4_sense_init()` manage the deferrable delayed work.

## Control Flow

Initialization stores the device pointer, enables sensing for all ports by default, and initializes `sense_poll` as deferrable work. Starting is conditional on `MLX4_DEV_CAP_FLAG_DPDP`; if the device lacks dynamic port detection, no polling is queued.

Each poll builds a sensed type array using current `dev->caps.port_type[1]` as defaults. Invalid firmware values greater than `2` are rejected. If no type is sensed for a port, the existing configuration remains. The worker then validates the full port set and calls the port-type change function. Regardless of success, it requeues itself after `MLX4_SENSE_RANGE`.

## State And Persistence Behavior

State is volatile and stored in `mlx4_priv(dev)->sense`: the delayed work object, device pointer, and per-port enable/allow arrays. Port type defaults come from `dev->caps.port_type`. There is no persistence beyond the running driver instance.

## Dependencies And Integration Points

This file depends on the mlx4 command interface, device capabilities, global mlx4 workqueue `mlx4_wq`, `priv->port_mutex`, and port-type validation/change helpers. It is tightly coupled to dynamic port detection support and should only actively poll when DPDP capability is present.

## Risks

- Firmware sense failures silently fall back to current defaults, which is safe but can hide persistent sensing failures except for logs.
- Reconfiguration happens under `port_mutex`; callers that also manipulate port state must preserve lock ordering.
- The worker always requeues after a validation failure, so repeated invalid configurations can produce recurring work.

## Test Signals

Test with DPDP-capable hardware or mocked command responses for Ethernet, InfiniBand, invalid values, and command failures. Verify `mlx4_stop_sense()` cancels the delayed work synchronously and that port type changes are not attempted when validation fails.
