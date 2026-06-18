# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lag/lag.h

## Purpose
`lag/lag.h` defines mlx5 LAG core data structures, mode enums, flags, helper accessors, iteration macros, and internal function declarations shared by LAG implementation, debugfs, multipath, MPESW, and other mlx5 subsystems.

## Important APIs, Types, And Functions
- Mode constants cover none, RoCE, SR-IOV, multipath, and multiport eswitch.
- `struct lag_func` records each PF's core device, netdev, drop-rule state, xarray index, and port-change notifier.
- `struct lag_tracker` captures bond TX type, per-port lower state, bonded/inactive flags, hash type, and bond speed.
- `struct mlx5_lag` stores mode, flags, readiness, port count, bucket count, mapping, kref, PF xarray, tracker, workqueue, notifiers, net namespace, multipath/port-select/MPESW state, lock, and demux resources.
- Inline helpers resolve the LAG object, PF entries, device-index mappings, readiness, and support checks.
- Declarations cover activation, modification, demux, debugfs, device add/remove, shared FDB, vport speed, devcom, iteration, and counting helpers.

## Control Flow And State
The header models the shared LAG object as a refcounted cross-device container. Devices are stored in an xarray, with an xarray mark identifying the master PF. Iteration macros walk only present PF entries using helper functions. Capability gating in `mlx5_lag_is_supported` requires vport group manager, lag master, at least two supported ports, valid device index, and port count not exceeding `MLX5_MAX_PORTS`.

## Dependencies And Integration Points
It depends on debugfs, xarray, mlx5 flow steering, core device definitions, and LAG submodules `mp.h`, `port_sel.h`, and `mpesw.h`. It is included by `lag.c`, `debugfs.c`, and other mlx5 modules needing LAG state or exported internal helpers.

## Risks And Edge Cases
The iteration macros rely on assignment in loop conditions and helper return sentinels; misuse can be subtle. `mlx5_lag_pf` returns xarray entries without taking references, so callers need appropriate locking/lifetime protection. Support checks must stay aligned with firmware capabilities as multi-port devices evolve.

## Test Signals
Build coverage across eswitch and non-eswitch configs, multi-port capability detection, xarray master marking, helper mappings between xarray index/device index/sequence, and debugfs/LAG modules compiling against this shared contract.
