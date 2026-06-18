# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/macsec.h

## Purpose
`macsec.h` exposes the internal mlx5 RoCE MACsec hooks to the RDMA driver while providing compile-time no-op stubs when `CONFIG_MLX5_MACSEC` is disabled.

## Important APIs, Types, And Functions
The header forward-declares `struct mlx5_reserved_gids` and declares GID add/delete hooks, GID/device-list initialization and deallocation, and MACsec event notifier register/unregister helpers. In non-MACsec builds, the add/init functions return success and delete/dealloc/register/unregister functions are empty.

## Control Flow
There is no runtime control flow in the header. Conditional compilation selects real implementations from `macsec.c` or stubs. The real hooks are called from `main.c` in GID cache operations and device lifecycle stages.

## State And Persistence Behavior
The header owns no state directly. Its conditional declaration controls whether `struct mlx5_ib_port` includes per-port `reserved_gids` in `mlx5_ib.h`, and whether MACsec operations manipulate `dev->macsec` state.

## Dependencies And Integration Points
It includes `<net/macsec.h>`, RDMA cache/address headers, and `mlx5_ib.h`. Because `mlx5_ib.h` also includes `macsec.h`, changes here can influence most mlx5 RDMA compilation units.

## Risks
The no-op stubs mean callers must not rely on MACsec side effects when the feature is disabled. Header include cycles are managed by include guards, but adding definitions that require complete mlx5 types could create ordering problems.

## Test Signals
Build tests with `CONFIG_MLX5_MACSEC=y` and disabled, plus runtime tests confirming GID add/delete works without MACsec support and invokes steering only when support is compiled and advertised.
