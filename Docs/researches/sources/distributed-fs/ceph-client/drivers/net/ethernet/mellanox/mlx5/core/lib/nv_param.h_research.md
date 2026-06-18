# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/nv_param.h

## Purpose
`nv_param.h` declares the mlx5 NV-parameter devlink registration interface. It is a narrow header used by devlink/core initialization code to add or remove permanent firmware-backed devlink parameters.

## Important APIs, types, and functions
The header exposes `mlx5_nv_param_register_dl_params(struct devlink *devlink)` and `mlx5_nv_param_unregister_dl_params(struct devlink *devlink)`. It includes the mlx5 driver definitions and local devlink declarations needed for those prototypes.

## Control flow
There is no runtime flow in this header. Callers register NV-backed parameters during device/devlink setup and unregister them during teardown. The implementation decides at runtime whether the device is a PF and no-ops for other function types.

## State and persistence behavior
The header stores no state. The declared implementation exposes persistent firmware settings through devlink permanent parameters, so callers must pair registration and unregistration with devlink lifetime.

## Dependencies and integration points
It depends on Linux mlx5 driver types and the local `devlink.h`. It integrates `nv_param.c` with the mlx5 devlink parameter registration path.

## Risks and edge cases
The main risk is lifecycle mismatch: registering parameters after devlink exposure or failing to unregister before devlink destruction can create stale devlink callbacks. Build coverage must keep prototypes consistent with implementation.

## Test signals
Build coverage and devlink parameter enumeration on mlx5 PFs are the direct signals. Non-PF devices should not expose these parameters, and unload/reload should not leave duplicate or stale devlink params.
