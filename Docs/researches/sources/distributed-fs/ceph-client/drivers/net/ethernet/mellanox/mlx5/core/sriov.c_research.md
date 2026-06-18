# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sriov.c

## Purpose

`sriov.c` manages mlx5 SR-IOV lifecycle. It enables/disables VFs at the mlx5 device and PCI layers, integrates VF vports with the eswitch, restores VF GUID/policy settings, configures dynamic VF MSI-X vector counts, waits for firmware pages to return, and exposes VF notifier registration for mlx5 submodules.

## Important APIs, Types, and Functions

Important public APIs are `mlx5_core_sriov_configure()`, `mlx5_sriov_disable()`, `mlx5_core_sriov_set_msix_vec_count()`, `mlx5_sriov_attach()`, `mlx5_sriov_detach()`, `mlx5_sriov_init()`, `mlx5_sriov_cleanup()`, `mlx5_sriov_blocking_notifier_register()`, and `mlx5_sriov_blocking_notifier_unregister()`. Local helpers are `mlx5_device_enable_sriov()`, `mlx5_device_disable_sriov()`, `mlx5_sriov_enable()`, `sriov_restore_guids()`, and `mlx5_get_max_vfs()`.

State lives in `dev->priv.sriov`: `max_vfs`, `num_vfs`, `max_ec_vfs`, and per-VF contexts with notifier heads, enabled bits, GUIDs, and policy.

## Control Flow

Enable takes the devlink lock around device-level setup, enables eswitch SR-IOV, computes default VF MSI-X vector count, and loops through requested VFs. For each VF it notifies registered listeners before enablement, calls `mlx5_core_enable_hca()`, sets MSI-X vector count if supported, marks the VF enabled, and restores InfiniBand GUID/policy settings for IB port-type devices. After device setup succeeds, `pci_enable_sriov()` creates PCI VFs; PCI failure triggers device-level disable rollback.

Disable first calls `pci_disable_sriov()`, then under devlink lock walks enabled VFs in reverse order, notifies listeners, disables each HCA, clears enabled bits, disables eswitch SR-IOV, and waits for VF and/or EC-VF firmware pages depending on whether this is a num-VF change or driver unload. ECPF devices skip host VF page wait until the ECPF itself is destroyed.

Attach/detach handle existing PCI VFs across driver bind/unbind. Initialization allocates per-VF contexts based on PCI total VFs, handles ECPF eswitch-manager max-VF query through eswitch functions, and initializes each notifier head.

## State and Persistence Behavior

Persistent driver state includes enabled flags, notifier heads, stored GUID/policy context, current and max VF counts, and EC VF capacity. Firmware state includes enabled VF HCAs, eswitch VF vports, vport GUID/policy context, and per-VF dynamic MSI-X table size. PCI state is created/destroyed by `pci_enable_sriov()` and `pci_disable_sriov()`.

## Dependencies and Integration Points

The file depends on PCI SR-IOV APIs, mlx5 HCA enable/disable commands, eswitch SR-IOV control, dynamic MSI-X helpers in `pci_irq.c`, vport context modification, page allocator wait counters, devlink locking, and blocking notifier chains used by VF-related modules.

## Risks and Edge Cases

`mlx5_device_enable_sriov()` continues after per-VF enable, MSI-X, or GUID restore failures and still returns 0 after eswitch enable; this can leave a partially enabled VF set, so callers and tests must inspect per-VF state. Page wait selection differs for EC SR-IOV and regular SR-IOV; incorrect counters can cause false timeouts or skipped waits. Notifier registration validates against `sriov->num_vfs`, not total allocated contexts, so notifiers for disabled but possible VFs are rejected.

## Test Signals

Test enabling/disabling varying VF counts, PCI enable rollback, driver attach with preexisting VFs, ECPF/EC-VF page wait behavior, IB GUID/policy restore, dynamic MSI-X sysfs updates including default count, eswitch enable failure, per-VF HCA failures, and notifier callbacks before VF enable/disable.
