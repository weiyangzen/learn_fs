# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/ecpf.h

## Purpose

`ecpf.h` declares ECPF helpers and provides no-op stubs when eswitch support is disabled.

## Important APIs, Types, and Functions

- `MLX5_ECPU_BIT_NUM` identifies the embedded CPU bit in the initialization segment.
- Declarations cover embedded CPU read, ECPF init/cleanup, and host-PF enable/disable HCA commands.
- Without `CONFIG_MLX5_ESWITCH`, inline stubs return false or success and do nothing.

## Control Flow

Core initialization can include this header unconditionally. Build-time stubs remove ECPF side effects when eswitch support is absent.

## State and Persistence Behavior

No state in the header. Implementations mutate firmware HCA state and wait on page counters.

## Dependencies and Integration Points

Depends on Linux mlx5 driver headers and `mlx5_core.h`. It is used by core device lifecycle and eswitch/ECPF handling.

## Risks and Edge Cases

Consumers must not assume ECPF behavior exists when `CONFIG_MLX5_ESWITCH` is disabled. Stubbed `mlx5_ec_init()` returning success can hide missing eswitch functionality in builds that do not support it.

## Test Signals

Compile with and without `CONFIG_MLX5_ESWITCH`. Verify callers do not require symbols unavailable in the stub configuration.
