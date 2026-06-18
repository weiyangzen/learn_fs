# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/std_types.c

## Purpose
`std_types.c` defines mlx5-specific uverbs methods attached to standard RDMA objects. It lets userspace query mlx5 PD numbers, port eswitch/multiport metadata, and a data-direct sysfs path through the uverbs named-ioctl infrastructure.

## Important APIs, types, and functions
- `UVERBS_HANDLER(MLX5_IB_METHOD_PD_QUERY)` copies the mlx5 PD number (`pdn`) for a PD object.
- `fill_vport_icm_addr()` queries eswitch vport context or uplink capabilities and fills software steering ICM RX/TX addresses when supported.
- `fill_vport_vhca_id()` fills vport VHCA ID via `mlx5_vport_get_vhca_id()`.
- `fill_multiport_info()` returns native-port VHCA ID for multiport devices.
- `fill_switchdev_info()` returns representor vport number, vport VHCA ID, eswitch owner VHCA ID, vport steering ICM addresses, and optional register C0 match metadata.
- `UVERBS_HANDLER(MLX5_IB_METHOD_QUERY_PORT)` validates a port and dispatches to switchdev or multiport metadata fill paths.
- `UVERBS_HANDLER(MLX5_IB_METHOD_GET_DATA_DIRECT_SYSFS_PATH)` returns the sysfs path for the current data-direct device under `data_direct_lock`.
- `DECLARE_UVERBS_NAMED_METHOD()`, `ADD_UVERBS_METHODS()`, and `mlx5_ib_std_types_defs[]` publish the methods for `UVERBS_OBJECT_DEVICE` and `UVERBS_OBJECT_PD`.

## Control flow
For PD query, uverbs resolves the PD object and the handler copies `mpd->pdn` to the mandatory output attribute. For port query, userspace passes a port number; the handler obtains the ucontext and mlx5 device, validates the port, and fills output only when eswitch offloads or multiport mode are active. Switchdev mode derives metadata from the representor, eswitch core device, vport, VHCA ID, optional software steering ICM addresses, and optional metadata register C0. Multiport mode queries the native port core device and reports its VHCA ID.

The data-direct path handler obtains the ucontext, locks `dev->data_direct_lock`, verifies a data-direct device exists, gets its kobject path, checks the output buffer length, copies the path, and unlocks/free resources on all exits.

## State and persistence
This file registers static uverbs method definitions and reads live device state. It does not own persistent mutable state. Output reflects current eswitch mode, representor association, native-port mapping, data-direct device pointer, and mlx5 capabilities.

## Dependencies and integration points
It integrates with RDMA uverbs named ioctl APIs, mlx5 user ioctl ABI headers, eswitch representors, vport VHCA ID APIs, software steering capability fields, data-direct device state, kobject sysfs paths, and mlx5 ucontext/device conversion helpers.

## Risks
- Output ABI is capability- and mode-dependent; userspace must key off flags, and the driver must set flags only for valid fields.
- Switchdev queries require a representor for the requested port; missing representors return `-EOPNOTSUPP`.
- ICM address reporting depends on software steering owner capability and nonzero addresses; incorrect gating can expose invalid addresses.
- Data-direct sysfs path uses a caller-provided output length and must return `-ENOSPC` rather than overrun.
- The data-direct pointer is protected by `data_direct_lock`; future accesses must preserve that locking.

## Test signals
- Uverbs tests should query PDNs and verify exact output length/type handling.
- Port-query tests should cover switchdev representor ports, uplink and non-uplink vports, multiport mode, invalid ports, absent representors, and non-offload/non-multiport mode.
- Capability tests should verify flags for VHCA ID, vport, eswitch owner, ICM RX/TX, and reg C0 are set only when data is valid.
- Data-direct tests should cover no device (`-ENODEV`), too-small output (`-ENOSPC`), normal path copy, and concurrent device removal under the lock.
