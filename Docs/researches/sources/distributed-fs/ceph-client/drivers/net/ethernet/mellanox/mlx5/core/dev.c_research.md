# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/dev.c

## Purpose

`dev.c` owns mlx5 auxiliary-device orchestration. It decides which protocol subdrivers are supported and enabled for a core device, allocates the `priv->adev[]` array, creates/removes auxiliary devices for Ethernet, representors, RDMA, multiport RDMA, vDPA-net, DPLL, and fwctl, and handles attach/detach/rescan flows after device configuration changes.

## Important APIs, Types, and Functions

- `mlx5_eth_supported()`, `mlx5_vnet_supported()`, and `mlx5_rdma_supported()` check build options, devlink params, device role, and firmware capabilities.
- Local predicates `is_eth_rep_supported()`, `is_ib_rep_supported()`, `is_mp_supported()`, `is_dpll_supported()`, and `is_fwctl_supported()` gate auxiliary protocols.
- `mlx5_adev_init()` / `mlx5_adev_cleanup()` allocate and free the array of auxiliary-device pointers.
- `mlx5_adev_idx_alloc()` / `mlx5_adev_idx_free()` allocate stable auxiliary IDs from `mlx5_adev_ida`.
- `mlx5_attach_device()` resumes existing auxiliary drivers or creates missing supported devices.
- `mlx5_detach_device()` suspends or deletes auxiliary devices in reverse order and marks the core as detached.
- `mlx5_register_device()`, `mlx5_unregister_device()`, and `mlx5_rescan_drivers_locked()` are the main rescan controls.
- `mlx5_same_hw_devs()` compares NIC software system image GUIDs.
- `mlx5_core_reps_aux_devs_remove()` forcibly removes representor aux devices under ETH device lock.

## Control Flow

The static `mlx5_adev_devices[]` table maps protocol indexes to auxiliary suffixes and support/enable predicates. Add/rescan flows iterate forward. For a missing supported entry, `add_adev()` allocates `struct mlx5_adev`, initializes an `auxiliary_device`, sets parent/release/name/id fields, and calls `auxiliary_device_add()`. For an existing bound device, attach may call the auxiliary driver's `resume()`.

Detach iterates in reverse so dependent representor-style devices are removed before base devices. If `suspend` is requested and the aux driver implements `suspend`, the device is kept but suspended. Otherwise it is deleted and uninitialized. `delete_drivers()` removes devices whose enable predicate is now false, whose support predicate is now false, or when `MLX5_PRIV_FLAGS_DISABLE_ALL_ADEV` is set.

## State and Persistence Behavior

Persistent state includes `dev->priv.adev[]`, per-auxiliary `struct mlx5_adev`, `dev->priv.flags` bits for detach/lightweight/disable-all behavior, and the global IDA. Auxiliary devices are Linux device-model objects with release callbacks; `adev_release()` frees the `mlx5_adev` and clears `priv->adev[idx]`.

The file assumes callers hold the devlink instance lock for public attach/detach/register/unregister paths and uses `mlx5_devcom_comp_lock()` to serialize with devcom component changes.

## Dependencies and Integration Points

Dependencies include auxiliary bus APIs, mlx5 capability macros, eswitch/switchdev state, devlink driver-init params for RDMA/vDPA/Ethernet enablement, lag/multiport helpers, vDPA capability definitions, and fwctl/DPLL build options. It is central to binding `mlx5_core` to independent protocol drivers.

## Risks and Edge Cases

- Attach can partially create aux devices then fail; the caller decides whether to unwind by unregistering.
- Enable predicates use devlink driver-init values; changes generally require reload/rescan, so runtime expectations must match devlink semantics.
- `mlx5_detach_device()` skips deleting a suspended aux device; subsequent attach relies on that aux driver's resume path.
- `mlx5_core_reps_aux_devs_remove()` assumes the ETH auxiliary device lock is already held and logs if ETH is gone.
- Support checks are feature-sensitive; missing firmware caps lead to silent absence for some protocols and warnings for Ethernet-required caps.

## Test Signals

Test with combinations of `CONFIG_MLX5_CORE_EN`, `CONFIG_MLX5_INFINIBAND`, `CONFIG_MLX5_ESWITCH`, `CONFIG_MLX5_VDPA_NET`, and `CONFIG_MLX5_DPLL`. Exercise devlink driver-init toggles followed by reload/rescan. Validate attach/detach under switchdev, multiport slave, lightweight, SF, PF, and VF roles. Use sysfs unbind/rebind of aux drivers and confirm resume/suspend handling.
